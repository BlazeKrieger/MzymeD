#!/usr/bin/env python3
"""
Generate mock MD trajectory showing enzyme-substrate binding dynamics for PyMOL.
Creates multi-frame PDB with smooth interpolation between states.
"""

from pathlib import Path
import sys
import numpy as np

sys.path.insert(0, "src")
from mzymed.file_handler import FileUploader


def helix_coords(length: int, radius: float = 8.0, rise: float = 1.5):
    """Generate helical coordinates for enzyme."""
    coords = []
    for i in range(length):
        angle = i * 2 * np.pi / 10.0
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = i * rise
        coords.append((x, y, z))
    return np.array(coords)


def substrate_coords(length: int, radius: float = 15.0, phase: float = 0):
    """Generate substrate coordinates that move toward enzyme."""
    coords = []
    for i in range(length):
        angle = i * 0.5 + phase
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        z = 2.0 * np.sin(angle * 2) + phase * 5  # Vertical movement
        coords.append((x, y, z))
    return np.array(coords)


def write_trajectory_pdb(enzyme_coords, substrate_frames, output_path: Path):
    """Write multi-frame PDB trajectory file."""
    lines = [
        "HEADER    MD TRAJECTORY - ENZYME-SUBSTRATE COMPLEX",
        "TITLE     LAMINARINASE + LAMINARIN BINDING DYNAMICS",
        "REMARK    Generated mock trajectory with 20 frames",
        "REMARK    Shows substrate approaching enzyme active site\n"
    ]
    
    # Center enzyme
    enz_center = enzyme_coords.mean(axis=0)
    enzyme_coords = enzyme_coords - enz_center
    
    for frame_num, substrate_coords_frame in enumerate(substrate_frames, start=1):
        lines.append(f"MODEL     {frame_num:4d}\n")
        
        # Write enzyme atoms (chain A)
        atom_id = 1
        for i, (x, y, z) in enumerate(enzyme_coords, start=1):
            line = (
                f"ATOM  {atom_id:5d}  CA  GLY A{i:4d}    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n"
            )
            lines.append(line)
            atom_id += 1
        
        # Write substrate atoms (chain B)
        substrate_coords_centered = substrate_coords_frame - enz_center
        for i, (x, y, z) in enumerate(substrate_coords_centered, start=1):
            line = (
                f"ATOM  {atom_id:5d}  CA  GLC B{i:4d}    "
                f"{x:8.3f}{y:8.3f}{z:8.3f}  1.00  0.00           C\n"
            )
            lines.append(line)
            atom_id += 1
        
        lines.append("ENDMDL\n")
    
    lines.append("END\n")
    output_path.write_text("".join(lines))
    print(f"✓ Wrote trajectory: {output_path.name} ({len(substrate_frames)} frames)")


def create_pymol_trajectory_script(trajectory_pdb: Path, output_script: Path):
    """Create PyMOL script for trajectory visualization."""
    script = f"""# PyMOL script for MD trajectory visualization
# Load trajectory
load "{trajectory_pdb.name}", traj

# Split chains
select enzyme, chain A
select substrate, chain B

# Set enzyme representation
show cartoon, enzyme
color red, enzyme
cartoon helix, enzyme
set cartoon_transparency, 0.3, enzyme

# Set substrate representation
show spheres, substrate
color cyan, substrate
set sphere_scale, 0.8, substrate

# Center and zoom
center
zoom

# Animation settings
set movie_loop, 1
set movie_fps, 10
mplay

# Optional: High-quality rendering
set ray_trace_mode, 1
set antialias, 2
bg_color white

# Optional: Save animation frames (uncomment to use)
# mset 1 x20
# frame 1
# mpng trajectory_frames/frame_, width=1200, height=900

print "MD Trajectory loaded!"
print "Use: mplay to play animation"
print "Use: mstop to stop"
print "Frames: 20"
print "Enzyme (red): BxLam16A laminarinase"
print "Substrate (cyan): Laminarin approaching active site"
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
    
    print(f"Generating MD trajectory...")
    print(f"  Enzyme: {len(enzyme_seq)} residues")
    print(f"  Substrate: {len(substrate_seq)} residues")
    
    # Generate enzyme coordinates (static)
    enz_coords = helix_coords(len(enzyme_seq))
    
    # Generate substrate trajectory (20 frames approaching enzyme)
    num_frames = 20
    substrate_frames = []
    
    for frame in range(num_frames):
        # Interpolate from far away to binding site
        progress = frame / (num_frames - 1)  # 0 to 1
        
        # Start radius: 15, end radius: 9 (closer to enzyme)
        radius = 15.0 - progress * 6.0
        
        # Phase shift causes rotation
        phase = progress * np.pi * 2
        
        coords = substrate_coords(len(substrate_seq), radius=radius, phase=phase)
        substrate_frames.append(coords)
    
    # Write trajectory PDB
    trajectory_pdb = out_dir / "md_trajectory.pdb"
    write_trajectory_pdb(enz_coords, substrate_frames, trajectory_pdb)
    
    # Create PyMOL script
    pymol_script = out_dir / "view_trajectory.pml"
    create_pymol_trajectory_script(trajectory_pdb, pymol_script)
    
    print(f"\n✓ Generated MD trajectory files")
    print(f"  Trajectory PDB: {trajectory_pdb}")
    print(f"  PyMOL script: {pymol_script}")
    print(f"  Frames: {num_frames}")
    print(f"\n📌 To visualize in PyMOL:")
    print(f"   pymol {pymol_script}")
    print(f"   OR")
    print(f"   1. Open PyMOL")
    print(f"   2. File → Open → {trajectory_pdb}")
    print(f"   3. Type: mplay (to play animation)")


if __name__ == "__main__":
    main()
