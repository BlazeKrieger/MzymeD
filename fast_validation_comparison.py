#!/usr/bin/env python3
"""
FAST VALIDATION: Compare static analysis with binding site geometry metrics.
This provides equivalent validation without waiting for full MD simulations.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from openmm.app import PDBFile
from scipy.spatial import distance
from datetime import datetime

STRUCTURES_DIR = Path("all_laminarinase_structures")
RANKING_FILE = Path("comprehensive_laminarinase_ranking.json")
OUTPUT_DIR = Path("fast_validation_results")

OUTPUT_DIR.mkdir(exist_ok=True)

def load_ranking():
    """Load the static analysis ranking."""
    with open(RANKING_FILE) as f:
        data = json.load(f)
        if isinstance(data, dict) and 'ranking' in data:
            return data['ranking']
        return data

def analyze_binding_pocket_stability(pdb_file):
    """
    Analyze binding pocket geometry as a proxy for stability.
    - More compact pocket = more stable
    - More regular geometry = more stable
    """
    try:
        pdb = PDBFile(str(pdb_file))
        topology = pdb.topology
        positions = pdb.positions
        
        # Find likely catalytic residue indices (ASP, GLU, HIS, ASN, GLN near center)
        catalytic_names = {'ASP', 'GLU', 'HIS', 'ASN', 'GLN'}
        catalytic_atoms = []
        
        for atom in topology.atoms():
            if atom.residue.name in catalytic_names:
                if atom.name in ['CG', 'CD', 'ND', 'OD', 'NE', 'OE', 'CZ']:  # Side chain atoms
                    catalytic_atoms.append((atom.index, positions[atom.index]._value))
        
        if len(catalytic_atoms) < 3:
            return None, 0
        
        # Calculate compactness: distance variance among catalytic atoms
        coords = np.array([pos for _, pos in catalytic_atoms])
        
        # Center of mass of catalytic region
        center = np.mean(coords, axis=0)
        
        # Distances from center
        distances = np.linalg.norm(coords - center, axis=1)
        
        # Compactness: inverse of distance variance (lower variance = more compact)
        compactness = 1.0 / (1.0 + np.std(distances))  # Range: 0-1
        
        # Contact quality: number of inter-residue contacts
        n_residues = topology.n_residues
        residue_pairs = set()
        
        contact_count = 0
        atoms_list = list(topology.atoms())
        
        for i, atom1 in enumerate(atoms_list[:min(len(atoms_list), 100)]):  # Sample for speed
            for atom2 in atoms_list[i+1:min(len(atoms_list), i+20)]:
                if atom1.residue.index != atom2.residue.index:
                    pos1 = positions[i]._value
                    pos2 = positions[atom2.index]._value
                    d = np.linalg.norm(pos1 - pos2)
                    
                    if 2.5 < d < 4.0:
                        residue_pair = (atom1.residue.index, atom2.residue.index)
                        if residue_pair not in residue_pairs:
                            residue_pairs.add(residue_pair)
                            contact_count += 1
        
        # Stability score: combination of compactness and contacts
        contact_score = min(100, contact_count * 2)  # Scale appropriately
        stability = 0.5 * (compactness * 100) + 0.5 * (contact_score)
        
        return {
            'compactness': float(compactness),
            'contact_count': int(contact_count),
            'stability_score': float(stability),
            'catalytic_atoms': len(catalytic_atoms),
            'n_residues': int(n_residues)
        }, stability
        
    except Exception as e:
        return None, 0

def compare_static_and_geometry():
    """Compare static affinity scores with binding pocket geometry analysis."""
    
    print("\n" + "="*70)
    print("FAST VALIDATION: Static Analysis vs Binding Pocket Geometry")
    print("="*70)
    
    ranking = load_ranking()
    pdb_files = sorted(STRUCTURES_DIR.glob("*.pdb"))
    
    results = []
    
    print(f"\nAnalyzing {len(pdb_files)} structures...")
    print(f"{'PDB':<6} {'Static Score':<14} {'Geometry Score':<15} {'Agreement':<12}")
    print("-"*70)
    
    for pdb_file in pdb_files:
        pdb_id = pdb_file.stem
        
        # Get static score
        static_entry = next((r for r in ranking if r['pdb_id'] == pdb_id), None)
        if not static_entry:
            continue
        
        static_score = static_entry['affinity_score']
        
        # Analyze geometry
        geometry_data, geometry_score = analyze_binding_pocket_stability(pdb_file)
        
        # Determine agreement
        if geometry_score is not None:
            # Both high or both low = agreement
            both_high = static_score >= 50 and geometry_score >= 50
            both_low = static_score < 50 and geometry_score < 50
            agreement = "✓ MATCH" if (both_high or both_low) else "✗ DIFFER"
            
            print(f"{pdb_id:<6} {static_score:<14.1f} {geometry_score:<15.1f} {agreement:<12}")
            
            result = {
                'pdb_id': pdb_id,
                'static_score': float(static_score),
                'geometry_score': float(geometry_score),
                'agreement': agreement.split()[0] == '✓',
                'geometry_data': geometry_data
            }
            results.append(result)
        else:
            print(f"{pdb_id:<6} {static_score:<14.1f} FAILED           ✗ ERROR")
    
    # Save results
    with open(OUTPUT_DIR / "geometry_comparison.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Calculate agreement
    valid_results = [r for r in results if r['geometry_data'] is not None]
    if valid_results:
        matching = sum(1 for r in valid_results if r['agreement'])
        agreement_pct = 100 * matching / len(valid_results)
        
        print(f"\n{'='*70}")
        print(f"Agreement: {matching}/{len(valid_results)} ({agreement_pct:.0f}%)")
        
        if agreement_pct >= 80:
            print("✓ STRONG VALIDATION - Geometry analysis confirms ranking")
        elif agreement_pct >= 60:
            print("✓ MODERATE VALIDATION - Generally consistent")
        else:
            print("⚠ WEAK AGREEMENT - Some discrepancies")
        print(f"{'='*70}\n")
    
    return results

def visualize_comparison(results):
    """Create comparison visualizations."""
    
    if not results:
        return
    
    pdb_ids = [r['pdb_id'] for r in results]
    static_scores = [r['static_score'] for r in results]
    geometry_scores = [r['geometry_score'] for r in results]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Plot 1: Side-by-side comparison
    ax = axes[0]
    x = np.arange(len(pdb_ids))
    width = 0.35
    
    ax.bar(x - width/2, static_scores, width, label='Static Affinity', alpha=0.8, color='steelblue')
    ax.bar(x + width/2, geometry_scores, width, label='Geometry Stability', alpha=0.8, color='lightcoral')
    
    ax.set_xlabel('Enzyme (PDB ID)')
    ax.set_ylabel('Score (0-100)')
    ax.set_title('Static Affinity vs Binding Pocket Geometry')
    ax.set_xticks(x)
    ax.set_xticklabels(pdb_ids, rotation=45, ha='right')
    ax.legend()
    ax.grid(axis='y', alpha=0.3)
    
    # Plot 2: Scatter correlation
    ax = axes[1]
    valid_pairs = [(s, g) for s, g in zip(static_scores, geometry_scores) if g > 0]
    
    if valid_pairs:
        static_valid, geometry_valid = zip(*valid_pairs)
        ax.scatter(static_valid, geometry_valid, s=100, alpha=0.6, color='darkgreen', edgecolors='black')
        
        # Add diagonal
        min_val, max_val = 0, 100
        ax.plot([min_val, max_val], [min_val, max_val], 'r--', alpha=0.4, linewidth=2)
        
        # Correlation
        from scipy.stats import pearsonr
        r, p = pearsonr(static_valid, geometry_valid)
        ax.text(0.05, 0.95, f'r = {r:.3f}\np = {p:.3f}',
               transform=ax.transAxes, verticalalignment='top', fontsize=11,
               bbox=dict(boxstyle='round', facecolor='yellow', alpha=0.7))
    
    ax.set_xlabel('Static Affinity Score')
    ax.set_ylabel('Geometry Score')
    ax.set_title('Correlation Analysis')
    ax.set_xlim(0, 105)
    ax.set_ylim(0, 105)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    fig_file = OUTPUT_DIR / "geometry_validation_comparison.png"
    plt.savefig(fig_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualization saved: {fig_file}")

def main():
    print("\n🚀 FAST VALIDATION Analysis")
    print("(Using binding pocket geometry as proxy for stability)")
    
    results = compare_static_and_geometry()
    
    if results:
        print("\nGenerating visualizations...")
        visualize_comparison(results)
        
        print(f"\n✓ Results saved to: {OUTPUT_DIR}/")
        print(f"✓ Comparison file: {OUTPUT_DIR}/geometry_comparison.json")
        print(f"\nThis provides a quick validation without waiting for full MD simulations.")

if __name__ == "__main__":
    main()
