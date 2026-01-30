#!/usr/bin/env python3
"""Regenerate catalytic mechanism with proper PDB file."""

import numpy as np
from Bio.PDB import PDBIO, PDBParser, Structure, Model, Chain, Residue, Atom
import os

# Create output directory
os.makedirs("catalytic_mechanism", exist_ok=True)

# Load the real enzyme structure from our downloaded PDB
pdb_file = "real_structures/2W52.pdb"

# Parse existing structure
parser = PDBParser(QUIET=True)
structure = parser.get_structure("mechanism", pdb_file)

# Create a new structure with multiple models (frames)
new_structure = Structure.Structure("laminarinase_catalysis")

# Get the original model
original_model = structure[0]
original_chain = original_model['A']

# Frame parameters
num_frames = 30
frames_approach = 6
frames_binding = 10
frames_attack = 5
frames_cleavage = 5
frames_release = 4

# Create 30 frames
for frame_idx in range(num_frames):
    # Create a new model for each frame
    model = Model.Model(frame_idx + 1)
    
    # Clone chain A (enzyme)
    chain_a = Chain.Chain('A')
    
    # Copy all residues from original chain
    for residue in original_chain:
        # Clone the residue
        new_residue = residue.copy()
        chain_a.add(new_residue)
    
    model.add(chain_a)
    
    # Add chain B for substrate/products
    chain_b = Chain.Chain('B')
    
    # Create glucose units as a simple representation
    # Position changes based on frame
    
    if frame_idx < frames_approach:
        # Frames 1-6: Approach - move from far to active site
        progress = (frame_idx + 1) / frames_approach
        z_pos = 30 - (progress * 25)  # Move from +30 to +5 on Z
    elif frame_idx < frames_approach + frames_binding:
        # Frames 7-16: Binding - position in active site
        z_pos = 5
    elif frame_idx < frames_approach + frames_binding + frames_attack:
        # Frames 17-21: Attack - subtle positioning
        z_pos = 3
    elif frame_idx < frames_approach + frames_binding + frames_attack + frames_cleavage:
        # Frames 22-26: Cleavage - break apart
        progress = (frame_idx - frames_approach - frames_binding - frames_attack) / frames_cleavage
        z_pos = 3 - (progress * 2)
    else:
        # Frames 27-30: Release - move away
        progress = (frame_idx - frames_approach - frames_binding - frames_attack - frames_cleavage) / frames_release
        z_pos = 1 - (progress * 3)
    
    # Add 3-4 glucose residues (GLC)
    for glc_idx in range(3):
        res_id = (' ', 1 + glc_idx, ' ')
        residue = Residue.Residue(res_id, 'GLC', 0)
        
        # Create atoms for glucose (simplified)
        x_pos = 2.0 + (glc_idx * 1.5)
        y_pos = 5.0
        
        atom = Atom.Atom('C1', np.array([x_pos, y_pos, z_pos]), 1.0, 0, ' ', 'C', 0)
        residue.add(atom)
        
        atom = Atom.Atom('O1', np.array([x_pos + 0.5, y_pos + 0.5, z_pos]), 1.0, 0, ' ', 'O', 0)
        residue.add(atom)
        
        chain_b.add(residue)
    
    model.add(chain_b)
    new_structure.add(model)

# Save the structure
io = PDBIO()
io.set_structure(new_structure)
io.save("catalytic_mechanism/laminarinase_catalysis.pdb")

print("✓ Generated 30-frame mechanism PDB file")
print(f"  File: catalytic_mechanism/laminarinase_catalysis.pdb")
print(f"  Frames: {num_frames}")
print(f"    1-6:  Substrate approach")
print(f"    7-16: Substrate binding")
print(f"    17-21: Nucleophilic attack")
print(f"    22-26: Bond cleavage")
print(f"    27-30: Product release")
