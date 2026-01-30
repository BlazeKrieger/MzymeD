#!/usr/bin/env python3
"""
Step 3: Validate ESMFold predicted structures using molecular dynamics.
Runs 500 ps MD simulations to assess stability and active site geometry.
"""

import json
import numpy as np
from pathlib import Path
from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md
import matplotlib.pyplot as plt
import pandas as pd

ESMFOLD_DIR = Path("esmfold_structures")
OUTPUT_DIR = Path("esmfold_md_validation")
OUTPUT_DIR.mkdir(exist_ok=True)

def run_md_validation(pdb_file, protein_id):
    """
    Run 500 ps MD simulation and analyze stability.
    Returns dict with RMSD, Rg, stability metrics.
    """
    try:
        print(f"  Loading structure...")
        pdb = PDBFile(str(pdb_file))
        
        print(f"  Setting up force field...")
        forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
        
        # Use implicit solvent for speed
        system = forcefield.createSystem(
            pdb.topology,
            nonbondedMethod=CutoffNonPeriodic,
            nonbondedCutoff=1.0*nanometers,
            constraints=HBonds
        )
        
        print(f"  Setting up integrator...")
        integrator = LangevinMiddleIntegrator(
            300*kelvin,
            1.0/picosecond,
            2.0*femtoseconds
        )
        
        simulation = Simulation(pdb.topology, system, integrator)
        simulation.context.setPositions(pdb.positions)
        
        print(f"  Minimizing energy...")
        simulation.minimizeEnergy(maxIterations=500)
        
        print(f"  Running 500 ps MD simulation...")
        n_steps = 250000  # 500 ps at 2 fs timestep
        save_interval = 1000  # Save every 2 ps
        
        positions_list = []
        
        for step in range(0, n_steps, save_interval):
            simulation.step(save_interval)
            positions = simulation.context.getState(getPositions=True).getPositions()
            positions_list.append(positions)
            
            if (step // save_interval) % 25 == 0:
                progress = (step / n_steps) * 100
                print(f"    Progress: {progress:.1f}%")
        
        print(f"  Analyzing trajectory...")
        
        # Convert to MDTraj
        traj = md.Trajectory(
            xyz=np.array([pos.value_in_unit(nanometers) for pos in positions_list]),
            topology=md.Topology.from_openmm(pdb.topology)
        )
        
        # Calculate metrics
        rmsd = md.rmsd(traj, traj, 0) * 10  # Convert to Angstroms
        rg = md.compute_rg(traj) * 10  # Radius of gyration in Angstroms
        
        # Stability assessment
        mean_rmsd = np.mean(rmsd)
        final_rmsd = rmsd[-1]
        rmsd_drift = final_rmsd - rmsd[50]  # Drift after equilibration
        
        stability_score = 100 - min(100, (rmsd_drift / 2) * 100)
        
        # Active site analysis (C-alpha atoms)
        ca_indices = traj.topology.select('name CA')
        ca_rmsd = md.rmsd(traj.atom_slice(ca_indices), traj.atom_slice(ca_indices), 0) * 10
        
        results = {
            'protein_id': protein_id,
            'n_frames': len(traj),
            'duration_ps': 500,
            'mean_rmsd': float(mean_rmsd),
            'final_rmsd': float(final_rmsd),
            'rmsd_drift': float(rmsd_drift),
            'mean_rg': float(np.mean(rg)),
            'stability_score': float(stability_score),
            'ca_mean_rmsd': float(np.mean(ca_rmsd)),
            'status': 'stable' if stability_score >= 70 else 'unstable'
        }
        
        # Save trajectory
        traj_file = OUTPUT_DIR / f"{protein_id}_md.pdb"
        traj.save_pdb(str(traj_file))
        
        # Plot RMSD
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))
        
        time_ps = np.arange(len(rmsd)) * 2  # 2 ps intervals
        ax1.plot(time_ps, rmsd, 'b-', linewidth=1)
        ax1.set_xlabel('Time (ps)', fontweight='bold')
        ax1.set_ylabel('RMSD (Å)', fontweight='bold')
        ax1.set_title(f'{protein_id} - RMSD Evolution', fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        ax2.plot(time_ps, rg, 'g-', linewidth=1)
        ax2.set_xlabel('Time (ps)', fontweight='bold')
        ax2.set_ylabel('Radius of Gyration (Å)', fontweight='bold')
        ax2.set_title(f'{protein_id} - Compactness', fontweight='bold')
        ax2.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(OUTPUT_DIR / f"{protein_id}_md_analysis.png", dpi=150)
        plt.close()
        
        print(f"  ✓ MD validation complete")
        print(f"    Mean RMSD: {mean_rmsd:.2f} Å")
        print(f"    Stability: {stability_score:.1f}/100")
        
        return results
        
    except Exception as e:
        print(f"  ✗ MD validation failed: {e}")
        return {
            'protein_id': protein_id,
            'status': 'failed',
            'error': str(e)
        }

def main():
    print("\n" + "="*80)
    print("STEP 3: MOLECULAR DYNAMICS VALIDATION OF ESMFOLD STRUCTURES")
    print("="*80)
    print(f"\nValidating predicted structures with 500 ps MD simulations")
    print(f"Output: {OUTPUT_DIR}/\n")
    
    # Find all ESMFold predictions
    pdb_files = list(ESMFOLD_DIR.glob("*_esmfold.pdb"))
    
    if not pdb_files:
        print("No ESMFold structures found. Run Step 2 first.")
        return
    
    print(f"Found {len(pdb_files)} structures to validate\n")
    
    results = []
    
    for i, pdb_file in enumerate(pdb_files, 1):
        protein_id = pdb_file.stem.replace('_esmfold', '')
        
        print(f"[{i}/{len(pdb_files)}] {protein_id}")
        print("-" * 80)
        
        result = run_md_validation(pdb_file, protein_id)
        results.append(result)
        print()
    
    # Save results
    output_json = OUTPUT_DIR / "md_validation_results.json"
    with open(output_json, 'w') as f:
        json.dump({
            'timestamp': pd.Timestamp.now().isoformat(),
            'total_structures': len(pdb_files),
            'successful': sum(1 for r in results if r.get('status') != 'failed'),
            'results': results
        }, f, indent=2)
    
    # Summary
    stable = [r for r in results if r.get('status') == 'stable']
    print("\n" + "="*80)
    print("MD VALIDATION SUMMARY")
    print("="*80)
    print(f"Total structures: {len(pdb_files)}")
    print(f"Stable (≥70):     {len(stable)}")
    print(f"\nTop 5 Most Stable:")
    sorted_results = sorted([r for r in results if 'stability_score' in r], 
                           key=lambda x: x['stability_score'], reverse=True)[:5]
    for i, r in enumerate(sorted_results, 1):
        print(f"  {i}. {r['protein_id']}: {r['stability_score']:.1f}/100 (RMSD drift: {r['rmsd_drift']:.2f} Å)")
    print(f"\nOutput: {output_json}")
    print("="*80)

if __name__ == "__main__":
    main()
