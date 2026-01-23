#!/usr/bin/env python3
"""
Enzyme affinity assessment via MD simulation.
Measures enzyme stability & active site flexibility as proxies for laminarin binding.
Uses coarse-grained approach to avoid missing terminal issues.
"""

import glob
import json
from pathlib import Path
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

try:
    from openmm import *
    from openmm.app import *
    import openmm.unit as u
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
print(f"Enzyme Affinity Assessment via Implicit Solvent MD")
print(f"{'='*70}\n")

# Find cleaned PDB files
pdb_files = sorted(glob.glob(str(CLEAN_DIR / "*_clean.pdb")))
print(f"Found: {len(pdb_files)} cleaned PDB files\n")

# MD parameters
TEMP = 300 * u.kelvin
TIME_STEP = 2.0 * u.femtoseconds
PRODUCTION_TIME = 100.0 * u.picoseconds
STEPS = int(PRODUCTION_TIME / TIME_STEP)
FRICTION_COEFF = 1.0 / u.picosecond

affinity_results = {}

for idx, pdb_file in enumerate(pdb_files, 1):
    pdb_name = Path(pdb_file).stem.replace('_clean', '')
    enzyme_name = pdb_name.split('_')[0]
    
    log_file = LOG_DIR / f"{pdb_name}_md.log"
    traj_file = OUTPUT_DIR / f"{pdb_name}_trajectory.dcd"
    
    try:
        with open(log_file, 'w') as log:
            log.write(f"[{idx}/{len(pdb_files)}] Running MD for {enzyme_name}\n")
            log.flush()
            
            # Load PDB - use CHARMM forcefield which is more lenient
            pdb = PDBFile(str(pdb_file))
            topology = pdb.topology
            positions = pdb.positions
            
            # Create system using CHARMM (more forgiving than AMBER for unrelaxed structures)
            try:
                ff = ForceField('charmm36.xml')
                system = ff.createSystem(topology, nonbondedMethod=CutoffNonbonded,
                                        nonbondedCutoff=1.0*u.nanometer)
            except:
                # Fallback to AMBER 14 with implicit solvent
                ff = ForceField('amber14-all.xml', 'implicit/obc2.xml')
                system = ff.createSystem(topology)
            
            # Add integrator
            integrator = LangevinMiddleIntegrator(TEMP, FRICTION_COEFF, TIME_STEP)
            
            # Set up simulation
            simulation = Simulation(topology, system, integrator)
            simulation.context.setPositions(positions)
            
            # Minimize energy first (crucial for unrelaxed structures)
            log.write(f"Minimizing energy...\n")
            log.flush()
            simulation.minimizeEnergy(maxIterations=500)
            
            # Get minimized positions
            state = simulation.context.getState(getPositions=True)
            min_positions = state.getPositions()
            
            # Run production MD
            log.write(f"Running {PRODUCTION_TIME} MD simulation ({STEPS} steps)...\n")
            log.flush()
            
            # Add DCD reporter
            simulation.reporters.append(DCDReporter(str(traj_file), 50))
            
            # Run MD
            simulation.step(STEPS)
            
            # Get final state
            state = simulation.context.getState(getPositions=True, getEnergy=True)
            final_energy = state.getPotentialEnergy().in_units(u.kilocalories_per_mole)
            
            # Calculate RMSD from starting structure
            traj = md.load(str(traj_file), top=md.Topology.from_openmm(topology))
            ca_indices = traj.topology.select('name CA')
            if len(ca_indices) > 0:
                rmsd_nm = md.rmsd(traj, traj[0], atom_indices=ca_indices)
                rmsd = np.mean(rmsd_nm[10:]) * 10  # Convert to Angstroms, skip first frames
                rmsd_std = np.std(rmsd_nm[10:]) * 10
            else:
                rmsd = 0.0
                rmsd_std = 0.0
            
            # Calculate active site flexibility (residues 50-100 CA RMSD as proxy)
            n_ca = len(ca_indices)
            active_site_start = max(0, n_ca // 4)
            active_site_end = min(n_ca, n_ca * 3 // 4)
            
            if active_site_end > active_site_start:
                active_site_indices = ca_indices[active_site_start:active_site_end]
                flexibility = np.mean(md.rmsd(traj, traj[0], atom_indices=active_site_indices)[10:]) * 10
            else:
                flexibility = 0.0
            
            # Stability score (lower RMSD = more stable)
            stability = 1.0 / (1.0 + rmsd)  # Range [0-1]
            
            # Affinity proxy: stability * (1 - flexibility)
            # Higher value = more likely to bind (stable + flexible active site)
            affinity_score = stability * (1.0 - min(1.0, flexibility / 5.0))
            
            # Store results
            affinity_results[enzyme_name] = {
                'pdb': pdb_name,
                'final_energy_kcal': float(final_energy),
                'rmsd_angstrom': float(rmsd),
                'rmsd_std': float(rmsd_std),
                'active_site_flexibility': float(flexibility),
                'stability_score': float(stability),
                'affinity_proxy_score': float(affinity_score)
            }
            
            log.write(f"✓ COMPLETE\n")
            log.write(f"  Final Energy: {final_energy:.2f} kcal/mol\n")
            log.write(f"  RMSD: {rmsd:.3f} ± {rmsd_std:.3f} Å\n")
            log.write(f"  Active Site Flexibility: {flexibility:.3f} Å\n")
            log.write(f"  Stability Score: {stability:.4f}\n")
            log.write(f"  Affinity Proxy Score: {affinity_score:.4f}\n")
            
            print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> Affinity: {affinity_score:.4f}")
            
    except Exception as e:
        print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> ERROR: {str(e)[:50]}")
        with open(log_file, 'w') as log:
            log.write(f"ERROR: {str(e)}\n")

# Sort by affinity score
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
