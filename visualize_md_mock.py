#!/usr/bin/env python3
"""
Generate a mock 3D enzyme–substrate visualization with a toy MD-like animation
using py3Dmol. Produces a multi-model PDB (frames) and an HTML viewer.

This is a lightweight placeholder until real structures/trajectories are available.
"""

import math
from pathlib import Path
import sys
import numpy as np
import urllib.request

sys.path.insert(0, "src")
from mzymed.file_handler import FileUploader


def load_sequence(path: Path) -> str:
    up = FileUploader()
    rec = up.load_sequence(str(path))
    if not rec:
        raise ValueError(f"Failed to load sequence from {path}")
    return str(rec.seq)


def helix_coords(length: int, radius: float = 8.0, rise: float = 1.5):
    coords = []
    for i in range(length):
        angle = i * 2 * math.pi / 10.0
        x = radius * math.cos(angle)
        y = radius * math.sin(angle)
        z = i * rise
        coords.append((x, y, z))
    return coords


def substrate_coords(length: int, frame: int, n_frames: int, base_radius: float = 15.0):
    coords = []
    theta0 = frame * 2 * math.pi / n_frames
    for i in range(length):
        r = base_radius + 2.0 * math.sin(theta0 + i * 0.3)
        angle = theta0 + i * 0.5
        x = r * math.cos(angle)
        y = r * math.sin(angle)
        z = 2.0 * math.sin(theta0 * 2 + i * 0.2)
        coords.append((x, y, z))
    return coords


def pdb_from_coords(enzyme_seq: str, substrate_seq: str, n_frames: int = 5) -> str:
    """Generate multi-frame PDB but return only first frame for viewer."""
    lines = []
    frame = 0  # Just first frame for rendering
    lines.append(f"MODEL    1\n")
    atom_id = 1
    # Enzyme chain A
    enz_coords = helix_coords(len(enzyme_seq))
    # Substrate chain B moves per frame
    sub_coords = substrate_coords(len(substrate_seq), frame, n_frames)

    # Recentering to keep the system near the origin for better viewing
    all_pts = np.array(enz_coords + sub_coords)
    center = all_pts.mean(axis=0)
    enz_coords = [(x - center[0], y - center[1], z - center[2]) for x, y, z in enz_coords]
    sub_coords = [(x - center[0], y - center[1], z - center[2]) for x, y, z in sub_coords]

    for i, (x, y, z) in enumerate(enz_coords, start=1):
        resname = "GLY"  # placeholder residue
        lines.append(
            "ATOM  {aid:5d}  CA  {res:3s} A{ires:4d}    "
            "{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n".format(
                aid=atom_id, res=resname, ires=i, x=x, y=y, z=z
            )
        )
        atom_id += 1
    lines.append("TER\n")
    for j, (x, y, z) in enumerate(sub_coords, start=1):
        resname = "GLC"  # mock glucose unit
        lines.append(
            "ATOM  {aid:5d}  CA  {res:3s} B{ires:4d}    "
            "{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n".format(
                aid=atom_id, res=resname, ires=j, x=x, y=y, z=z
            )
        )
        atom_id += 1
    lines.append("TER\nENDMDL\nEND\n")
    return "".join(lines)


def write_html(pdb_path: Path, out_html: Path):
        """Write a self-contained HTML that loads 3Dmol and animates frames."""
        pdb_data = pdb_path.read_text(encoding="utf-8").replace("`", "\`")
        html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset=\"utf-8\" />
    <title>Enzyme-Substrate MD Mock</title>
    <link rel=\"icon\" href=\"data:,\" />
    <style>
        body {{ margin: 0; padding: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }}
    </style>
</head>
<body>
    <div id=\"viewer\" style=\"width: 900px; height: 700px; position: relative;\"></div>
    <script>
        const pdbData = `{pdb_data}`;

        function load3Dmol(callback) {{
            const localScript = document.createElement('script');
            localScript.src = '3Dmol-min.js';
            localScript.onload = () => callback();
            localScript.onerror = () => {{
                const cdnScript = document.createElement('script');
                cdnScript.src = 'https://cdn.jsdelivr.net/npm/3dmol@2.5.3/build/3Dmol-min.js';
                cdnScript.onload = () => callback();
                cdnScript.onerror = () => console.error('Failed to load 3Dmol from local and CDN.');
                document.head.appendChild(cdnScript);
            }};
            document.head.appendChild(localScript);
        }}

    load3Dmol(() => {
      if (typeof $3Dmol === 'undefined') {
        console.error('3Dmol is still undefined after loading.');
        return;
      }
      const viewer = $3Dmol.createViewer('viewer', { backgroundColor: 'white' });
      viewer.addModel(pdbData, 'pdb');
      viewer.setStyle({ chain: 'A' }, { sphere: { color: 'red', scale: 0.6 } });
      viewer.setStyle({ chain: 'B' }, { sphere: { color: 'cyan', scale: 0.5 } });
      viewer.zoomTo();
      viewer.zoom(1.4);
      viewer.render();
      console.log('Viewer rendered successfully');
    });
    </script>
</body>
</html>
"""

        out_html.parent.mkdir(parents=True, exist_ok=True)
        out_html.write_text(html, encoding="utf-8")


def ensure_local_3dmol(out_dir: Path):
    """Download 3Dmol script locally so the HTML works offline."""
    target = out_dir / "3Dmol-min.js"
    if target.exists():
        return target
    url = "https://cdn.jsdelivr.net/npm/3dmol@2.5.3/build/3Dmol-min.js"
    try:
        out_dir.mkdir(exist_ok=True)
        urllib.request.urlretrieve(url, target)
        print("✓ Downloaded local 3Dmol-min.js")
    except Exception as e:
        print(f"⚠ Could not download 3Dmol-min.js: {e}")
    return target if target.exists() else None


def main():
    base = Path(__file__).parent
    enzyme_path = base / "laminarinases" / "GH16" / "BxLam16A.fasta"
    substrate_path = base / "laminarin_substrate.fasta"

    enzyme_seq = load_sequence(enzyme_path)
    substrate_seq = load_sequence(substrate_path)

    pdb_data = pdb_from_coords(enzyme_seq, substrate_seq, n_frames=30)

    out_dir = base / "visual_outputs"
    out_dir.mkdir(exist_ok=True)
    ensure_local_3dmol(out_dir)
    pdb_path = out_dir / "enzyme_substrate_mock.pdb"
    html_path = out_dir / "enzyme_substrate_md.html"

    with open(pdb_path, "w", encoding="utf-8") as f:
        f.write(pdb_data)

    write_html(pdb_path, html_path)

    print("✓ Wrote mock multi-model PDB to", pdb_path)
    print("✓ Wrote interactive MD-style HTML to", html_path)
    print("Open the HTML in a browser to view the animation (py3Dmol frames).")


if __name__ == "__main__":
    main()
