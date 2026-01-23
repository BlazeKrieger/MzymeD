#!/usr/bin/env python3
"""
Quick test of C-alpha MD setup
"""

from pathlib import Path
from openmm.app import PDBFile
from openmm import *
import openmm.unit as u

pdb_file = Path("predicted_structures_cleaned/2VY0_1_Chains___264_aa___Activity__78.1___laminarinases_GH16_Lam16_rcsb_pdb_2VY0.fasta_unrelaxed_rank_001_alphafold2_ptm_model_5_seed_000_clean.pdb")

print(f"Loading {pdb_file.name}...")

try:
    pdb = PDBFile(str(pdb_file))
    print(f"✓ PDB loaded: {pdb.topology.getNumResidues()} residues, {pdb.topology.getNumAtoms()} atoms")
    
    # Test creating C-alpha list
    ca_atoms = []
    ca_positions = []
    for chain in pdb.topology.chains():
        for residue in chain.residues():
            for atom in residue.atoms():
                if atom.name == 'CA':
                    ca_atoms.append(atom)
                    ca_positions.append(pdb.positions[atom.index])
    
    print(f"✓ Found {len(ca_atoms)} C-alpha atoms")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
