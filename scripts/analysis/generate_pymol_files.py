#!/usr/bin/env python3
"""
Generate PDB files for enzyme-substrate complex and create PyMOL script.
Can be opened directly in PyMOL for elegant 3D visualization.
"""

from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, "src")
from mzymed.file_handler import FileUploader


def helix_coords(length: int, radius: float = 8.0, rise: float = 1.5):
    coords = []
    for i in range(length):
        angle = i * 2 * np.pi / 10.0
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = i * rise
        coords.append((x, y, z))
    return np.array(coords)


def substrate_coords(length: int, radius: float = 15.0):
    coords = []
    for i in range(length):
        angle = i * 0.5
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 2.0 * np.sin(angle * 2)
        coords.append((x, y, z))
    return np.array(coords)


def write_pdb(coords, chain, resname, output_path: Path):
    """Write PDB file from coordinates."""
    lines = ["HEADER    ENZYME-SUBSTRATE COMPLEX", "TITLE     LAMINARINASE + LAMINARIN\n"]
    
    # Center structure
    center = coords.mean(axis=0)
    coords = coords - center
    
    atom_id = 1
    for i, (x, y, z) in enumerate(coords, start=1):
        line = (
            f"ATOM  {atom_id:5d}  CA  {resname:3s} {chain}{i:4d}    "
            f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n"
        )
        lines.append(line)
        atom_id += 1
    
    lines.append("END\n")
    output_path.write_text("".join(lines))
    print(f"✓ Wrote PDB: {output_path.name}")


def create_pymol_script(enzyme_pdb: Path, substrate_pdb: Path, output_script: Path):
    """Create PyMOL script for visualization."""
    script = f"""# PyMOL script for enzyme-substrate visualization
# Load structures
load "{enzyme_pdb.name}", enzyme
load "{substrate_pdb.name}", substrate

# Set styles
show cartoon, enzyme
color red, enzyme
cartoon helix, enzyme

show sticks, substrate
color cyan, substrate

# Set representation
as spheres, enzyme
as spheres, substrate
set sphere_scale, 0.6, enzyme
set sphere_scale, 0.5, substrate

# Coloring
color red, enzyme
color cyan, substrate

# Center and zoom
center
zoom

# Fancy rendering (optional - comment out if slow)
set ray_trace_mode, 1
set antialias, 2

# Set background
bg_color white

# Save image
# ray 1200, 900
# png enzyme_substrate_md.png, dpi=300

print "Enzyme-substrate complex loaded!"
print "Enzyme (red): BxLam16A laminarinase"
print "Substrate (cyan): Laminarin mock"
"""
    output_script.write_text(script)
    print(f"✓ Wrote PyMOL script: {output_script.name}")


def main():
    base = Path(__file__).parent
    enzyme_path = base / "laminarinases" / "GH16" / "BxLam16A.fasta"
    substrate_path = base / "laminarin_substrate.fasta"
    out_dir = base / "visual_outputs"
    out_dir.mkdir(exist_ok=True)
    
    # Load sequences
    uploader = FileUploader()
    enzyme_rec = uploader.load_sequence(str(enzyme_path))
    substrate_rec = uploader.load_sequence(str(substrate_path))
    
    if not enzyme_rec or not substrate_rec:
        raise ValueError("Failed to load sequences")
    
    enzyme_seq = str(enzyme_rec.seq)
    substrate_seq = str(substrate_rec.seq)
    
    # Generate coordinates
    enz_coords = helix_coords(len(enzyme_seq))
    sub_coords = substrate_coords(len(substrate_seq))
    
    # Write PDB files
    enzyme_pdb = out_dir / "enzyme.pdb"
    substrate_pdb = out_dir / "substrate.pdb"
    write_pdb(enz_coords, "A", "GLY", enzyme_pdb)
    write_pdb(sub_coords, "B", "GLC", substrate_pdb)
    
    # Create PyMOL script
    pymol_script = out_dir / "view_complex.pml"
    create_pymol_script(enzyme_pdb, substrate_pdb, pymol_script)
    
    print(f"\n✓ Generated PyMOL files")
    print(f"  Enzyme PDB: {enzyme_pdb}")
    print(f"  Substrate PDB: {substrate_pdb}")
    print(f"  PyMOL script: {pymol_script}")
    print(f"\n📌 To visualize:")
    print(f"   1. Open PyMOL")
    print(f"   2. File → Open → {enzyme_pdb}")
    print(f"   3. File → Open → {substrate_pdb}")
    print(f"   OR")
    print(f"   pymol {pymol_script}")


if __name__ == "__main__":
    main()
