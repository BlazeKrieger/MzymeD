#!/usr/bin/env python3
"""
MD validation with proper hydrogen addition.
This version adds hydrogens to all structures before MD simulation.
"""

import os
import json
import numpy as np
from pathlib import Path
from openmm.app import PDBFile, ForceField, Simulation, DCDReporter, HBonds, Modeller
from openmm import LangevinIntegrator
from openmm.unit import *
import mdtraj as md
from datetime import datetime

# Paths
STRUCTURES_DIR = Path("all_laminarinase_structures")
RANKING_FILE = Path("comprehensive_laminarinase_ranking.json")
OUTPUT_DIR = Path("md_validation_results")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# MD Parameters - SHORTER duration for fast validation across 20 structures
MD_DURATION = 200  # picoseconds (reduced from 500 to speed up)
TEMPERATURE = 300  # Kelvin
TIME_STEP = 2.0    # femtoseconds
REPORT_INTERVAL = 50  # frames per trajectory

def load_ranking():
    """Load the static analysis ranking."""
    with open(RANKING_FILE) as f:
        data = json.load(f)
        if isinstance(data, dict) and 'ranking' in data:
            return data['ranking']
        return data

def run_md_on_structure(pdb_file, pdb_id, duration_ps=200):
    """
    Run MD simulation on a PDB structure with hydrogen addition.
    Returns dict with binding site RMSD and stability metrics.
    """
    print(f"\n{'='*70}")
    print(f"Running MD on {pdb_id} ({pdb_file.name})")
    print(f"{'='*70}")
    
    try:
        # Load structure
        pdb = PDBFile(str(pdb_file))
        
        # Create modeller and add hydrogens
        print(f"  Adding hydrogens...", end="", flush=True)
        modeller = Modeller(pdb.topology, pdb.positions)
        forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
        modeller.addHydrogens(forcefield, pH=7.0)
        print(" done")
        
        # Create system
        print(f"  Creating system...", end="", flush=True)
        system = forcefield.createSystem(
            modeller.topology,
            nonbondedMethod=0,  # NoCutoff for implicit solvent
            constraints=HBonds,
            implicitSolvent='GBn2'
        )
        print(" done")
        
        # Create integrator and simulation
        integrator = LangevinIntegrator(TEMPERATURE*kelvin, 1.0/picosecond, TIME_STEP*femtoseconds)
        simulation = Simulation(modeller.topology, system, integrator)
        simulation.context.setPositions(modeller.positions)
        
        # Minimize energy briefly
        print(f"  Energy minimization...", end="", flush=True)
        simulation.minimizeEnergy(maxIterations=100)
        print(" done")
        
        # Run MD
        print(f"  Running {duration_ps} ps MD...", end="", flush=True)
        n_steps = int(duration_ps * 1000 / TIME_STEP)
        report_interval = max(1, int(n_steps / 10))  # 10 snapshots
        
        dcd_file = OUTPUT_DIR / f"{pdb_id}_trajectory.dcd"
        simulation.reporters.append(DCDReporter(str(dcd_file), report_interval))
        
        simulation.step(n_steps)
        print(" done")
        
        # Analyze trajectory
        print(f"  Analyzing trajectory...", end="", flush=True)
        
        # Load trajectory with mdtraj
        traj = md.load(str(dcd_file), top=str(pdb_file))
        
        # Calculate RMSD from initial structure (CA atoms only)
        topology = traj.topology
        ca_indices = topology.select('name CA')
        
        if len(ca_indices) > 0:
            distances = md.rmsd(traj, traj[0], atom_indices=ca_indices)
        else:
            distances = np.zeros(len(traj))
        
        # Metrics
        rmsd_mean = np.mean(distances)
        rmsd_max = np.max(distances)
        rmsd_std = np.std(distances)
        
        # Count residues
        n_residues = topology.n_residues
        n_atoms = topology.n_atoms
        
        # Calculate radius of gyration
        rg = md.compute_rg(traj)
        rg_mean = np.mean(rg)
        rg_std = np.std(rg)
        
        print(" done")
        
        results = {
            'pdb_id': pdb_id,
            'rmsd_mean': float(rmsd_mean),
            'rmsd_max': float(rmsd_max),
            'rmsd_std': float(rmsd_std),
            'rg_mean': float(rg_mean),
            'rg_std': float(rg_std),
            'n_residues': int(n_residues),
            'n_atoms': int(n_atoms),
            'md_duration_ps': duration_ps,
            'status': 'SUCCESS'
        }
        
        return results
        
    except Exception as e:
        print(f" FAILED: {str(e)[:80]}")
        return {
            'pdb_id': pdb_id,
            'rmsd_mean': None,
            'rmsd_max': None,
            'rmsd_std': None,
            'rg_mean': None,
            'rg_std': None,
            'n_residues': None,
            'n_atoms': None,
            'md_duration_ps': duration_ps,
            'status': f'FAILED'
        }

def calculate_stability_score(md_metrics):
    """
    Calculate a stability score from MD metrics.
    Lower RMSD = higher stability.
    """
    if md_metrics['status'] != 'SUCCESS' or md_metrics['rmsd_mean'] is None:
        return None
    
    rmsd_mean = md_metrics['rmsd_mean']
    rmsd_std = md_metrics['rmsd_std']
    
    # Score: 100 for <0.5Å RMSD, decreasing exponentially
    rmsd_score = 100 * np.exp(-rmsd_mean / 0.5)
    variance_penalty = 10 * (rmsd_std / (rmsd_mean + 0.01))
    
    stability_score = max(0, rmsd_score - variance_penalty)
    return min(100, stability_score)

def main():
    print("\n" + "="*70)
    print("MD VALIDATION: Running MD on all 20 laminarinase structures")
    print(f"Duration: {MD_DURATION} ps per structure")
    print(f"Start time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Load static ranking
    ranking = load_ranking()
    
    # Get PDB files
    pdb_files = sorted(STRUCTURES_DIR.glob("*.pdb"))
    print(f"\nFound {len(pdb_files)} PDB files")
    
    # Run MD on each structure
    md_results = {}
    for i, pdb_file in enumerate(pdb_files, 1):
        pdb_id = pdb_file.stem
        print(f"\n[{i}/{len(pdb_files)}] Processing {pdb_id}")
        
        result = run_md_on_structure(pdb_file, pdb_id, duration_ps=MD_DURATION)
        md_results[pdb_id] = result
    
    # Save raw MD results
    md_results_file = OUTPUT_DIR / "md_results_raw.json"
    with open(md_results_file, 'w') as f:
        serializable_results = {}
        for pdb_id, result in md_results.items():
            serializable_results[pdb_id] = {k: (float(v) if isinstance(v, (np.floating, float)) else v) 
                                             for k, v in result.items()}
        json.dump(serializable_results, f, indent=2)
    
    print(f"\n\nRaw MD results saved to {md_results_file}")
    
    # Combine static and dynamic results
    comparison_results = []
    
    for entry in ranking:
        pdb_id = entry['pdb_id']
        static_score = entry['affinity_score']
        
        if pdb_id in md_results:
            md_data = md_results[pdb_id]
            stability_score = calculate_stability_score(md_data)
            
            comparison = {
                'pdb_id': pdb_id,
                'enzyme_name': entry.get('enzyme_name', 'Unknown'),
                'static_affinity_score': static_score,
                'md_stability_score': stability_score,
                'rmsd_mean': md_data.get('rmsd_mean'),
                'rmsd_max': md_data.get('rmsd_max'),
                'rmsd_std': md_data.get('rmsd_std'),
                'rg_mean': md_data.get('rg_mean'),
                'rg_std': md_data.get('rg_std'),
                'md_status': md_data.get('status', 'UNKNOWN'),
                'agreement': 'MATCHING' if (stability_score is not None and static_score > 50 and stability_score > 50) or 
                            (stability_score is not None and static_score <= 50 and stability_score <= 50) else 'DIVERGING'
            }
            comparison_results.append(comparison)
    
    # Sort by static score
    comparison_results.sort(key=lambda x: x['static_affinity_score'], reverse=True)
    
    # Save comparison results
    comparison_file = OUTPUT_DIR / "md_vs_static_comparison.json"
    with open(comparison_file, 'w') as f:
        json.dump(comparison_results, f, indent=2)
    
    # Print summary
    print("\n" + "="*70)
    print("COMPARISON: Static Affinity vs MD Stability")
    print("="*70)
    print(f"{'Rank':<5} {'PDB':<6} {'Static':<8} {'Stability':<10} {'RMSD_Å':<8} {'Agreement':<10}")
    print("-"*70)
    
    for rank, result in enumerate(comparison_results, 1):
        pdb_id = result['pdb_id']
        static = result['static_affinity_score']
        stability = result['md_stability_score']
        rmsd = result['rmsd_mean']
        agreement = result['agreement']
        
        if stability is not None:
            print(f"{rank:<5} {pdb_id:<6} {static:>7.1f} {stability:>9.1f}    {rmsd:>7.2f}    {agreement:<10}")
        else:
            print(f"{rank:<5} {pdb_id:<6} {static:>7.1f} {'FAILED':<9}    {'N/A':<7}    {agreement:<10}")
    
    # Calculate agreement
    successful_md = sum(1 for r in comparison_results if r['md_status'] == 'SUCCESS')
    matching = sum(1 for r in comparison_results if r['agreement'] == 'MATCHING' and r['md_status'] == 'SUCCESS')
    
    if successful_md > 0:
        agreement_pct = 100 * matching / successful_md
        print(f"\nMD Successful: {successful_md}/{len(comparison_results)}")
        print(f"Ranking Agreement: {matching}/{successful_md} ({agreement_pct:.0f}%)")
        
        if agreement_pct >= 80:
            print("✓ CONCLUSION: Static ranking is STRONGLY VALIDATED by MD")
        elif agreement_pct >= 60:
            print("✓ CONCLUSION: Static ranking is MODERATELY VALIDATED by MD")
        else:
            print("⚠ CONCLUSION: Some discrepancies between static and MD")
    
    print("="*70)
    print(f"\n✓ Comparison results saved to {comparison_file}")
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == "__main__":
    main()
