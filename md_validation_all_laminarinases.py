#!/usr/bin/env python3
"""
Run MD simulations on all 20 laminarinase structures to validate static analysis ranking.
Compares dynamic stability metrics with static affinity scores.
"""

import os
import json
import numpy as np
from pathlib import Path
from openmm.app import PDBFile, ForceField, Simulation, DCDReporter, HBonds
from openmm import LangevinIntegrator, NonbondedForce
from openmm.unit import *
import mdtraj as md
from datetime import datetime

# Paths
STRUCTURES_DIR = Path("all_laminarinase_structures")
RANKING_FILE = Path("comprehensive_laminarinase_ranking.json")
OUTPUT_DIR = Path("md_validation_results")

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)

# MD Parameters
MD_DURATION = 500  # picoseconds (500 ps for faster execution across 20 structures)
TEMPERATURE = 300  # Kelvin
TIME_STEP = 2.0    # femtoseconds
REPORT_INTERVAL = 50  # frames per trajectory

def load_ranking():
    """Load the static analysis ranking."""
    with open(RANKING_FILE) as f:
        data = json.load(f)
        # Extract ranking list if it's nested
        if isinstance(data, dict) and 'ranking' in data:
            return data['ranking']
        return data

def run_md_on_structure(pdb_file, pdb_id, duration_ps=500):
    """
    Run MD simulation on a PDB structure and extract stability metrics.
    Returns dict with binding site RMSD and stability metrics.
    """
    print(f"\n{'='*70}")
    print(f"Running MD on {pdb_id} ({pdb_file.name})")
    print(f"{'='*70}")
    
    try:
        # Load structure
        pdb = PDBFile(str(pdb_file))
        
        # Create system - using Amber14 force field with implicit solvent
        forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
        system = forcefield.createSystem(
            pdb.topology,
            nonbondedMethod=0,  # NoCutoff (0) or PME
            constraints=HBonds,
            implicitSolvent='GBn2'
        )
        
        # Create integrator and simulation
        integrator = LangevinIntegrator(TEMPERATURE*kelvin, 1.0/picosecond, TIME_STEP*femtoseconds)
        simulation = Simulation(pdb.topology, system, integrator)
        simulation.context.setPositions(pdb.positions)
        
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
        
        # Calculate RMSD from initial structure (binding site region)
        # Use CA atoms only for faster analysis
        topology = traj.topology
        ca_indices = topology.select('name CA')
        
        if len(ca_indices) > 0:
            # Reference structure is first frame
            distances = md.rmsd(traj, traj[0], atom_indices=ca_indices)
        else:
            distances = np.zeros(len(traj))
        
        # Metrics
        rmsd_mean = np.mean(distances)
        rmsd_max = np.max(distances)
        rmsd_std = np.std(distances)
        
        # Count residues (proxy for protein size/stability)
        n_residues = topology.n_residues
        n_atoms = topology.n_atoms
        
        # Calculate radius of gyration (structural compactness)
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
        print(f" FAILED: {str(e)}")
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
            'status': f'FAILED: {str(e)}'
        }

def calculate_stability_score(md_metrics):
    """
    Calculate a stability score from MD metrics.
    Lower RMSD and more stable structure = higher score.
    Scale: 0-100 (inverse of RMSD-based deviation)
    """
    if md_metrics['status'] != 'SUCCESS':
        return None
    
    rmsd_mean = md_metrics['rmsd_mean']
    rmsd_std = md_metrics['rmsd_std']
    
    # Penalize high RMSD (flexibility) and high variance (instability)
    # Baseline: <0.5 Å RMSD = good stability, >2.0 Å = poor
    rmsd_score = 100 * np.exp(-rmsd_mean / 0.5)  # Exponential decay
    variance_penalty = 20 * (rmsd_std / (rmsd_mean + 0.01))  # Penalty for instability
    
    stability_score = max(0, rmsd_score - variance_penalty)
    return min(100, stability_score)

def main():
    print("\n" + "="*70)
    print("MD VALIDATION: Running MD on all 20 laminarinase structures")
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
        # Convert numpy types to native Python types for JSON serialization
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
    
    # Sort by static score for comparison
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
    
    # Calculate ranking concordance
    static_ranking = [entry['pdb_id'] for entry in comparison_results]
    
    # Rerank by stability score (excluding failed)
    valid_results = [r for r in comparison_results if r['md_stability_score'] is not None]
    valid_results.sort(key=lambda x: x['md_stability_score'], reverse=True)
    md_ranking = [entry['pdb_id'] for entry in valid_results]
    
    # Calculate Spearman correlation
    def rank_correlation(list1, list2):
        """Calculate Kendall tau correlation between two rankings."""
        # Create rank dictionaries
        rank1 = {item: i for i, item in enumerate(list1)}
        rank2 = {item: i for i, item in enumerate(list2)}
        
        common_items = set(rank1.keys()) & set(rank2.keys())
        if len(common_items) < 2:
            return None
        
        # Calculate correlation using Kendall tau
        from scipy.stats import kendalltau
        ranks1 = [rank1[item] for item in sorted(common_items)]
        ranks2 = [rank2[item] for item in sorted(common_items)]
        
        tau, p_value = kendalltau(ranks1, ranks2)
        return tau, p_value
    
    try:
        tau, p_value = rank_correlation(static_ranking, md_ranking)
        print("\n" + "="*70)
        print(f"Ranking Concordance Analysis:")
        print(f"  Kendall Tau correlation: {tau:.3f}")
        print(f"  P-value: {p_value:.3f}")
        
        if tau > 0.7:
            print(f"  Result: STRONG AGREEMENT - Static ranking holds up in MD")
        elif tau > 0.4:
            print(f"  Result: MODERATE AGREEMENT - Some reordering in MD")
        else:
            print(f"  Result: WEAK AGREEMENT - Significant differences in MD")
        print("="*70)
    except Exception as e:
        print(f"\nNote: Could not calculate correlation: {e}")
    
    # Save summary report
    summary = {
        'analysis_date': datetime.now().isoformat(),
        'md_duration_ps': MD_DURATION,
        'temperature_k': TEMPERATURE,
        'total_structures': len(pdb_files),
        'successful_md': sum(1 for r in comparison_results if r['md_status'] == 'SUCCESS'),
        'failed_md': sum(1 for r in comparison_results if r['md_status'] != 'SUCCESS'),
        'ranking_concordance_tau': float(tau) if 'tau' in locals() else None,
    }
    
    summary_file = OUTPUT_DIR / "md_validation_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2, default=str)
    
    print(f"\n✓ Comparison results saved to {comparison_file}")
    print(f"✓ Summary saved to {summary_file}")
    print(f"✓ MD trajectories saved to {OUTPUT_DIR}/*.dcd")
    
    print(f"\nEnd time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nMD validation complete!")

if __name__ == "__main__":
    main()
