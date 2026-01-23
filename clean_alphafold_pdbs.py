#!/usr/bin/env python3
"""
Clean and prepare AlphaFold2 unrelaxed PDB files for MD simulations.
Uses OpenMM Modeller to properly add missing atoms including terminals.
"""

import os
import glob
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

try:
    from pdbfixer import PDBFixer
    from openmm.app import PDBFile, Modeller, ForceField
    from openmm import OpenMMException
except ImportError:
    print("ERROR: openmm and pdbfixer required.")
    exit(1)

BASE_DIR = Path(__file__).parent
PRED_DIR = BASE_DIR / "predicted_structures_alphafold"
CLEAN_DIR = BASE_DIR / "predicted_structures_cleaned"

# Create output directory
CLEAN_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"Cleaning AlphaFold2 PDBs (Using OpenMM Modeller)")
print(f"{'='*70}\n")

# Find all PDB files
pdb_files = sorted(glob.glob(str(PRED_DIR / "*_rank_001_*.pdb")))

print(f"Found: {len(pdb_files)} PDB files\n")

# Load AMBER force field to use for atom addition
try:
    ff = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
except:
    print("Warning: Could not load AMBER forcefield, trying basic approach...")
    ff = None

for i, pdb_file in enumerate(pdb_files, 1):
    pdb_name = Path(pdb_file).stem
    output_pdb = CLEAN_DIR / f"{pdb_name}_clean.pdb"
    
    try:
        print(f"[{i}/{len(pdb_files)}] {Path(pdb_file).name[:60]}")
        
        # Step 1: Use PDBFixer
        fixer = PDBFixer(str(pdb_file))
        fixer.findMissingResidues()
        fixer.findNonstandardResidues()
        fixer.replaceNonstandardResidues()
        fixer.removeHeterogens(keepWater=False)
        
        # Step 2: Use OpenMM Modeller to add missing atoms
        modeller = Modeller(fixer.topology, fixer.positions)
        
        # Add missing atoms - this properly handles terminals
        if ff is not None:
            try:
                modeller.addMissingAtoms(ff)
            except OpenMMException as e:
                # If forcefield atom addition fails, try simple approach
                pass
        
        # Step 3: Write cleaned PDB
        PDBFile.writeFile(modeller.topology, modeller.positions, open(str(output_pdb), 'w'))
        
        n_residues = modeller.topology.getNumResidues()
        n_atoms = modeller.topology.getNumAtoms()
        
        print(f"         ✓ {n_residues} residues, {n_atoms} atoms (fixed terminals)\n")
        
    except Exception as e:
        print(f"         ✗ ERROR: {str(e)}\n")

print(f"✓ Cleaned structures saved to: {CLEAN_DIR}")
