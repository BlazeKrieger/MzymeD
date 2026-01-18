#!/usr/bin/env python3
"""
Enzyme-Substrate Visualization:
Show MD trajectory of enzyme with substrate frozen in place from crystal structure
"""

import os
from Bio.PDB import PDBParser, PDBIO, Select
import mdtraj as md

print("="*70)
print("ENZYME-SUBSTRATE VISUALIZATION")
print("="*70)

# Step 1: Load enzyme MD trajectory (50 frames)
print("\n1. Loading enzyme MD trajectory...")
traj = md.load('md_simulation/real_md_trajectory.pdb')
print(f"   Trajectory: {traj.n_frames} frames, {traj.n_atoms} atoms")

# Step 2: Extract substrate chains from original crystal structure
print("\n2. Extracting substrate chains from 2W52.pdb...")
parser = PDBParser(QUIET=True)
struct = parser.get_structure('2W52', 'real_structures/2W52.pdb')

class SelectSubstrate(Select):
    def accept_chain(self, chain):
        return chain.id in ['B', 'C', 'D']

io = PDBIO()
io.set_structure(struct)
io.save('md_simulation/substrate_frozen.pdb', select=SelectSubstrate())
print("   ✓ Substrate saved (will stay fixed)")

# Step 3: Create combined visualization file
print("\n3. Creating combined trajectory (enzyme moving + substrate fixed)...")

# Read enzyme trajectory
with open('md_simulation/real_md_trajectory.pdb', 'r') as f:
    traj_lines = f.readlines()

# Read substrate
with open('md_simulation/substrate_frozen.pdb', 'r') as f:
    substrate_lines = f.readlines()

# Extract atoms
substrate_atoms = [l for l in substrate_lines if l.startswith(('ATOM  ', 'HETATM'))]
print(f"   Substrate atoms: {len(substrate_atoms)}")

# Split trajectory into frames
frames = []
current_frame = []
model_count = 0

for line in traj_lines:
    if line.startswith('MODEL'):
        model_count += 1
    elif line.startswith('ENDMDL'):
        if current_frame:
            frames.append(current_frame)
        current_frame = []
    elif line.startswith(('ATOM  ', 'HETATM')):
        current_frame.append(line)
    elif line.startswith('END'):
        if current_frame:
            frames.append(current_frame)

if not frames:
    # No MODEL records, treat whole file as one frame
    frames = [traj_lines]

print(f"   Enzyme frames: {len(frames)}")

# Renumber substrate atoms
next_atom_num = 4293  # After enzyme atoms
renumbered_substrate = []
for i, line in enumerate(substrate_atoms):
    atom_num = next_atom_num + i
    new_line = line[:6] + f'{atom_num:5d}' + line[11:]
    renumbered_substrate.append(new_line)

# Write combined file with all frames (enzyme moving, substrate fixed each frame)
with open('md_simulation/enzyme_substrate_combined.pdb', 'w') as f:
    f.write("REMARK Enzyme-Substrate Complex Visualization\n")
    f.write("REMARK Enzyme moving from MD / Substrate fixed from crystal\n")
    
    for frame_idx, enzyme_atoms in enumerate(frames):
        f.write(f"MODEL {frame_idx+1}\n")
        # Write enzyme atoms for this frame
        f.writelines(enzyme_atoms)
        # Write substrate atoms (fixed)
        f.writelines(renumbered_substrate)
        f.write("ENDMDL\n")
    
    f.write("END\n")

print(f"   ✓ Combined file created: 50 frames with enzyme+substrate")

# Step 4: Statistics
print("\n4. Simulation Statistics:")
print(f"   Enzyme atoms: 4292 (moving)")
print(f"   Substrate atoms: {len(substrate_atoms)} (fixed)")
print(f"   Total atoms per frame: {4292 + len(substrate_atoms)}")
print(f"   Frames: {len(frames)}")
print(f"   Duration: {(len(frames)-1)*2} ps (100 ps total)")

# Step 5: Identify key residues
print("\n5. Catalytic Residues in Laminarinase (GH16):")
print("   GLU107 - Nucleophile (general base)")
print("   ASP256 - General acid catalyst")  
print("   TRP257 - Substrate binding")
print("   GLY49  - Loop motion")

# Step 6: RMSD analysis
print("\n6. Enzyme Motion Analysis:")
ca_idx = traj.topology.select('name CA')
rmsd = md.rmsd(traj, traj[0], atom_indices=ca_idx)
print(f"   Cα RMSD: min={rmsd.min():.3f} Å, max={rmsd.max():.3f} Å, mean={rmsd.mean():.3f} Å")

print("\n" + "="*70)
print("✓ COMPLETE: enzyme_substrate_combined.pdb")
print("="*70)

print("\nVisualization Commands (PyMOL):")
print("  pymol md_simulation/enzyme_substrate_combined.pdb")
print("\nPyMOL Commands:")
print("  # Hide everything first")
print("  hide all")
print("  ")
print("  # Show enzyme as cartoon")
print("  show cartoon, chain A")
print("  color spectrum, chain A")
print("  ")
print("  # Show substrate as sticks")
print("  show sticks, chain B+C+D")
print("  color cyan, chain B+C+D")
print("  ")
print("  # Highlight catalytic residues")
print("  show spheres, resi 107 or resi 256 or resi 257 or resi 49")
print("  color red, resi 107")
print("  color orange, resi 256")
print("  color yellow, resi 257")
print("  color purple, resi 49")
print("  ")
print("  # Play animation")
print("  mplay")
print("  ")
print("  # Set background")
print("  bg_color white")
print("  set ray_opaque_background, 1")
