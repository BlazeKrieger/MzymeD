#!/usr/bin/env python3
"""
Enzyme affinity assessment via coarse-grained MD.
Uses only heavy atoms (C-alpha/backbone) to avoid missing hydrogen issues.
"""

import glob
import json
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

try:
    from openmm import *
    from openmm.app import *
    import openmm.unit as u
    from openmm.unit import Quantity
    import mdtraj as md
    import numpy as np
except ImportError as e:
    print(f"ERROR: Required packages missing: {e}")
    exit(1)

BASE_DIR = Path(__file__).parent
CLEAN_DIR = BASE_DIR / "predicted_structures_cleaned"
OUTPUT_DIR = BASE_DIR / "alphafold_enzyme_affinity"
LOG_DIR = OUTPUT_DIR / "logs"

OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"Enzyme Affinity Assessment (Coarse-Grained C-Alpha MD)")
print(f"{'='*70}\n")

# Find cleaned PDB files
pdb_files = sorted(glob.glob(str(CLEAN_DIR / "*_clean.pdb")))
print(f"Found: {len(pdb_files)} cleaned PDB files\n")

# MD parameters (coarse-grained, so longer timestep)
TEMP = 300 * u.kelvin
TIME_STEP = 5.0 * u.femtoseconds  # Larger for C-alpha only
PRODUCTION_TIME = 50.0 * u.picoseconds  # Shorter since coarse-grained
STEPS = int(PRODUCTION_TIME / TIME_STEP)
FRICTION_COEFF = 0.5 / u.picosecond

affinity_results = {}

for idx, pdb_file in enumerate(pdb_files, 1):
    pdb_name = Path(pdb_file).stem.replace('_clean', '')
    enzyme_name = pdb_name.split('_')[0]
    
    log_file = LOG_DIR / f"{pdb_name}_md.log"
    traj_file = OUTPUT_DIR / f"{pdb_name}_trajectory.dcd"
    
    try:
        with open(log_file, 'w') as log:
            log.write(f"[{idx}/{len(pdb_files)}] Running C-alpha MD for {enzyme_name}\n\n")
            log.flush()
            
            # Load PDB
            pdb = PDBFile(str(pdb_file))
            topology = pdb.topology
            positions = pdb.positions
            
            # Create coarse-grained system: select only C-alpha atoms
            ca_atoms = []
            ca_topology = Topology()
            ca_positions = []
            
            chain_map = {}
            atom_indices = {}
            
            for chain in topology.chains():
                new_chain = ca_topology.addChain()
                for residue in chain.residues():
                    new_residue = ca_topology.addResidue(residue.name, new_chain)
                    for atom in residue.atoms():
                        if atom.name == 'CA':
                            ca_atoms.append(atom)
                            ca_topology.addAtom(atom.name, atom.element, new_residue)
                            ca_positions.append(positions[atom.index])
                            atom_indices[atom.index] = len(ca_atoms) - 1
            
            if len(ca_atoms) == 0:
                log.write("ERROR: No CA atoms found in structure\n")
                continue
            
            ca_positions = Quantity(ca_positions, u.angstroms)
            
            # Create a simple harmonic spring network
            system = System()
            for i in range(len(ca_atoms)):
                system.addParticle(12.0 * u.amu)  # Approximate mass for C-alpha
            
            # Add bonds (springs between consecutive C-alphas)
            nb_cutoff = 5.0 * u.angstroms
            bonds_force = HarmonicBondForce()
            nonbonded_force = NonbondedForce()
            
            for i in range(len(ca_atoms) - 1):
                # Bond between consecutive residues
                r0 = np.linalg.norm(ca_positions[i+1] - ca_positions[i])
                bonds_force.addBond(i, i+1, r0, 230.0 * u.kilocalories_per_mole / u.angstrom**2)
            
            # Add non-bonded interactions (Lennard-Jones approximation)
            for i in range(len(ca_atoms)):
                nonbonded_force.addParticle(0.0, 4.0 * u.angstroms, 0.1 * u.kilocalories_per_mole)
            
            nonbonded_force.setNonbondedMethod(CutoffNonbonded)
            nonbonded_force.setCutoffDistance(nb_cutoff)
            
            system.addForce(bonds_force)
            system.addForce(nonbonded_force)
            
            # Create simulation
            integrator = LangevinMiddleIntegrator(TEMP, FRICTION_COEFF, TIME_STEP)
            simulation = Simulation(ca_topology, system, integrator)
            simulation.context.setPositions(ca_positions)
            
            # Minimize
            log.write(f"Energy minimization ({len(ca_atoms)} C-alpha atoms)...\n")
            log.flush()
            simulation.minimizeEnergy(maxIterations=500)
            
            # Run MD
            log.write(f"Running {PRODUCTION_TIME} MD ({STEPS} steps)...\n")
            log.flush()
            simulation.reporters.append(DCDReporter(str(traj_file), 10))
            simulation.step(STEPS)
            
            # Get final state
            state = simulation.context.getState(getPositions=True, getEnergy=True)
            final_energy = state.getPotentialEnergy().in_units(u.kilocalories_per_mole)
            
            # Calculate RMSD
            traj = md.load(str(traj_file), top=md.Topology.from_openmm(ca_topology))
            initial_coords = traj.xyz[0]
            rmsd_nm = np.array([np.sqrt(np.mean(np.sum((frame - initial_coords)**2, axis=1))) 
                                 for frame in traj.xyz])
            rmsd = np.mean(rmsd_nm[5:]) * 10  # Angstroms, skip first frames
            rmsd_std = np.std(rmsd_nm[5:]) * 10
            
            # Stability score
            stability = 1.0 / (1.0 + rmsd)
            
            # Simple affinity proxy: lower energy + stable = better binder
            affinity_score = stability * (1.0 / (1.0 + final_energy / 100.0))
            
            affinity_results[enzyme_name] = {
                'pdb': pdb_name,
                'n_residues': len(ca_atoms),
                'final_energy_kcal': float(final_energy),
                'rmsd_angstrom': float(rmsd),
                'rmsd_std': float(rmsd_std),
                'stability_score': float(stability),
                'affinity_proxy_score': float(affinity_score)
            }
            
            log.write(f"\n✓ COMPLETE\n")
            log.write(f"  Final Energy: {final_energy:.2f} kcal/mol\n")
            log.write(f"  RMSD: {rmsd:.3f} ± {rmsd_std:.3f} Å\n")
            log.write(f"  Stability: {stability:.4f}\n")
            log.write(f"  Affinity Score: {affinity_score:.4f}\n")
            
            print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> Affinity: {affinity_score:.4f}")
            
    except Exception as e:
        print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> ERROR: {str(e)[:60]}")
        with open(log_file, 'w') as log:
            log.write(f"ERROR: {str(e)}\n")

# Rank by affinity
ranked = sorted(affinity_results.items(), key=lambda x: x[1]['affinity_proxy_score'], reverse=True)

# Save results
output_json = OUTPUT_DIR / "affinity_scores.json"
with open(output_json, 'w') as f:
    json.dump(dict(ranked), f, indent=2)

print(f"\n{'='*70}")
print(f"Top 5 Enzymes by Predicted Affinity:")
print(f"{'='*70}")
for i, (name, scores) in enumerate(ranked[:5], 1):
    print(f"{i}. {name:30s} Score: {scores['affinity_proxy_score']:.4f}")

print(f"\n✓ Results saved to: {output_json}")
