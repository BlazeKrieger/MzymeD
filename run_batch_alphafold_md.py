#!/usr/bin/env python3
"""
Run MD simulations on all AlphaFold2 predicted laminarinase structures.
"""

import os
import json
import glob
import subprocess
import sys
from pathlib import Path

os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md
import numpy as np
from datetime import datetime

BASE_DIR = Path(__file__).parent
PRED_DIR = BASE_DIR / "predicted_structures_alphafold"
OUTPUT_DIR = BASE_DIR / "alphafold_md_results"
LOG_DIR = OUTPUT_DIR / "logs"

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

def get_enzyme_name(pdb_file):
    """Extract enzyme name from filename."""
    stem = Path(pdb_file).stem
    parts = stem.split("_unrelaxed_rank_001")
    if parts:
        return parts[0]
    return stem

def run_md_single(pdb_file, max_steps=50000, timeout=600):
    """
    Run MD on single structure using OpenMM.
    
    Args:
        pdb_file: Path to PDB file
        max_steps: MD steps (default 50000 = 100 ps)
        timeout: Max seconds per simulation
    """
    
    enzyme_name = get_enzyme_name(pdb_file)
    output_traj = OUTPUT_DIR / f"{enzyme_name}_md_trajectory.pdb"
    output_log = LOG_DIR / f"{enzyme_name}_md.log"
    output_rmsd = OUTPUT_DIR / f"{enzyme_name}_rmsd.json"
    
    print(f"\n{'='*70}")
    print(f"MD: {enzyme_name}")
    print(f"PDB: {Path(pdb_file).name}")
    print(f"{'='*70}")
    
    try:
        # Load PDB
        pdb = PDBFile(str(pdb_file))
        n_residues = len(list(pdb.topology.residues()))
        print(f"✓ Loaded: {n_residues} residues, {pdb.topology.getNumAtoms()} atoms")
        
        # Force field: AMBER14 + implicit solvent (fast, no box needed)
        print("• Loading AMBER14 force field...")
        forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
        
        # Add hydrogens
        print("• Adding hydrogens...")
        modeller = Modeller(pdb.topology, pdb.positions)
        modeller.addHydrogens(forcefield)
        n_atoms = modeller.topology.getNumAtoms()
        print(f"✓ Added H: {n_atoms} total atoms")
        
        # Create system
        print("• Creating system...")
        system = forcefield.createSystem(
            modeller.topology,
            nonbondedMethod=CutoffNonPeriodic,
            nonbondedCutoff=1.0*nanometers,
            constraints=HBonds,
            rigidWater=True
        )
        
        # Integrator
        temperature = 300*kelvin
        timestep = 2.0*femtoseconds
        integrator = LangevinIntegrator(temperature, 1.0/picosecond, timestep)
        
        # Simulation
        print("• Creating simulation...")
        try:
            platform = Platform.getPlatformByName('CUDA')
            properties = {'CudaPrecision': 'mixed', 'DeviceIndex': '0'}
            simulation = Simulation(modeller.topology, system, integrator, platform, properties)
            platform_name = "CUDA"
        except:
            platform = Platform.getPlatformByName('CPU')
            simulation = Simulation(modeller.topology, system, integrator, platform)
            platform_name = "CPU"
        
        print(f"✓ Using {platform_name}")
        
        simulation.context.setPositions(modeller.positions)
        
        # Energy minimization
        print("• Minimizing energy...")
        initial_energy = simulation.context.getState(getEnergy=True).getPotentialEnergy()
        print(f"  Initial PE: {initial_energy}")
        
        simulation.minimizeEnergy(maxIterations=500, tolerance=1*kilojoule/mole)
        
        final_energy = simulation.context.getState(getEnergy=True).getPotentialEnergy()
        print(f"  Final PE: {final_energy}")
        
        # Equilibration
        print("• Equilibrating (2 ps)...")
        simulation.context.setVelocitiesToTemperature(temperature)
        simulation.step(1000)
        
        # MD reporting
        simulation.reporters.append(
            PDBReporter(str(output_traj), 500)  # Every 1 ps
        )
        simulation.reporters.append(
            StateDataReporter(
                str(output_log),
                100,
                step=True,
                time=True,
                potentialEnergy=True,
                kineticEnergy=True,
                temperature=True,
                progress=True,
                remainingTime=True,
                speed=True,
                totalSteps=max_steps,
                separator='\t'
            )
        )
        
        # Production MD
        print(f"• Running MD: {max_steps} steps ({max_steps*2/1000:.1f} ps)...")
        print(f"  Output: {output_traj.name}")
        print(f"  Logging to: {output_log.name}\n")
        
        simulation.step(max_steps)
        
        # Get final state
        state = simulation.context.getState(getEnergy=True, getPositions=True, getVelocities=True)
        final_pe = state.getPotentialEnergy()
        
        # Calculate RMSD
        print("\n• Calculating RMSD...")
        traj = md.load(str(output_traj))
        ca_indices = traj.topology.select("name CA")
        rmsd_values = md.rmsd(traj, traj, frame=0, atom_indices=ca_indices) * 10  # Convert to Angstroms
        
        rmsd_data = {
            "enzyme": enzyme_name,
            "n_residues": n_residues,
            "n_atoms": n_atoms,
            "n_frames": len(traj),
            "duration_ps": len(traj) * 1.0,
            "rmsd_initial_nm": float(rmsd_values[0]),
            "rmsd_final_nm": float(rmsd_values[-1]),
            "rmsd_mean_nm": float(np.mean(rmsd_values)),
            "rmsd_max_nm": float(np.max(rmsd_values)),
            "final_pe_kj_mol": float(final_pe.value_in_unit(kilojoule_per_mole)),
            "timestamp": datetime.now().isoformat(),
            "platform": platform_name
        }
        
        with open(output_rmsd, 'w') as f:
            json.dump(rmsd_data, f, indent=2)
        
        print(f"✓ RMSD (initial→final): {rmsd_values[0]:.3f} → {rmsd_values[-1]:.3f} Å")
        print(f"✓ SUCCESS: {enzyme_name}")
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        with open(output_log, 'w') as f:
            f.write(f"ERROR: {str(e)}\n")
        return False

def main():
    """Batch MD runner."""
    
    pdb_files = sorted(glob.glob(str(PRED_DIR / "*_rank_001_*.pdb")))
    
    print(f"\n{'='*70}")
    print(f"AlphaFold2 Predicted Structures - MD Batch Run")
    print(f"{'='*70}")
    print(f"\nFound: {len(pdb_files)} structures")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*70}\n")
    
    if not pdb_files:
        print("ERROR: No PDB files found!")
        return 1
    
    results = {}
    for i, pdb_file in enumerate(pdb_files, 1):
        enzyme_name = get_enzyme_name(pdb_file)
        print(f"\n[{i}/{len(pdb_files)}] {enzyme_name}")
        
        success = run_md_single(pdb_file)
        results[enzyme_name] = "SUCCESS" if success else "FAILED"
    
    # Summary
    print(f"\n\n{'='*70}")
    print(f"BATCH RUN SUMMARY")
    print(f"{'='*70}\n")
    
    success_count = sum(1 for v in results.values() if v == "SUCCESS")
    print(f"Completed: {success_count}/{len(pdb_files)}")
    print(f"Success rate: {100*success_count/len(pdb_files):.1f}%\n")
    
    # Save summary
    summary_file = OUTPUT_DIR / "batch_summary.json"
    with open(summary_file, 'w') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "total_structures": len(pdb_files),
            "successful": success_count,
            "success_rate": success_count / len(pdb_files),
            "results": results
        }, f, indent=2)
    
    print(f"Summary: {summary_file}")
    print(f"\nRMSD results in: {OUTPUT_DIR}")
    
    return 0 if success_count == len(pdb_files) else 1

if __name__ == "__main__":
    sys.exit(main())
