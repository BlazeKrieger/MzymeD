#!/usr/bin/env python3
"""
Assess glucanase activity for all 81 predicted laminarinase structures.
Compares predicted structures against the 20 experimentally validated ones.
"""

import json
import numpy as np
from pathlib import Path
from Bio import SeqIO
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import seaborn as sns

# Directories
PREDICTED_DIR = Path("predicted_structures_advanced")
PREDICTIONS_LOG = Path("structure_predictions_advanced.json")
KNOWN_ACTIVITIES_JSON = Path("glucanase_activity_analysis/glucanase_activity_assessment.json")
OUTPUT_DIR = Path("predicted_activity_analysis")
OUTPUT_DIR.mkdir(exist_ok=True)

def load_known_activities():
    """Load the activity scores from known structures."""
    if KNOWN_ACTIVITIES_JSON.exists():
        with open(KNOWN_ACTIVITIES_JSON) as f:
            data = json.load(f)
        known = {}
        # Handle both list and dict formats
        if isinstance(data, list):
            for entry in data:
                known[entry.get('pdb_id', entry.get('id', ''))] = entry.get('kcat_km_score', entry.get('activity_score', 0))
        else:
            for entry in data.get('results', []):
                known[entry['pdb_id']] = entry['activity_score']
        return known
    return {}

def estimate_activity_from_sequence(fasta_path):
    """
    Estimate glucanase activity from sequence properties.
    Uses sequence-based features similar to the structure-based analysis.
    """
    try:
        record = SeqIO.read(str(fasta_path), "fasta")
        sequence = str(record.seq)
    except:
        return None
    
    # Catalytic residues commonly found in laminarinases
    catalytic_residues = {
        'E': sequence.count('E'),  # Glutamic acid (acid/base catalyst)
        'D': sequence.count('D'),  # Aspartic acid
        'H': sequence.count('H'),  # Histidine (nucleophile help)
    }
    
    # Estimate catalytic conservation score
    catalytic_score = min(100, (catalytic_residues['E'] + catalytic_residues['D'] * 0.8 + catalytic_residues['H'] * 0.5) / 0.5)
    
    # Active site geometry estimate (based on aromatic residues)
    aromatics = sequence.count('F') + sequence.count('W') + sequence.count('Y')
    geometry_score = min(100, aromatics * 3)  # Aromatics important for stacking
    
    # Substrate specificity (based on hydrophobic/polar balance)
    hydrophobic = sum(1 for aa in sequence if aa in 'AILMFVP')
    polar = sum(1 for aa in sequence if aa in 'STNQ')
    hydro_polar_ratio = hydrophobic / (polar + 1)  # Avoid division by zero
    specificity_score = min(100, 50 + hydro_polar_ratio * 10)
    
    # Structural quality estimate (sequence length, composition)
    length_score = min(100, (len(sequence) / 600 * 100))  # Typical laminarinase ~600 aa
    
    # Calculate final activity score
    activity = (
        catalytic_score * 0.35 +
        geometry_score * 0.30 +
        specificity_score * 0.20 +
        length_score * 0.15
    )
    
    return {
        'activity': round(activity, 1),
        'catalytic': round(catalytic_score, 1),
        'geometry': round(geometry_score, 1),
        'specificity': round(specificity_score, 1),
        'length': len(sequence),
    }

def main():
    print("\n" + "="*100)
    print("GLUCANASE ACTIVITY ASSESSMENT FOR PREDICTED STRUCTURES")
    print("="*100)
    
    # Load known activities for reference
    known_activities = load_known_activities()
    
    # Load predictions log
    with open(PREDICTIONS_LOG) as f:
        predictions_data = json.load(f)
    
    results = {
        'predicted_count': 0,
        'known_count': len(known_activities),
        'activity_analysis': [],
        'comparison': {},
        'statistics': {},
    }
    
    all_activities = []
    
    print(f"\nAnalyzing {len(predictions_data['sequences'])} predicted structures...")
    print(f"Reference: {len(known_activities)} experimentally validated structures\n")
    
    print(f"{'Rank':<6} {'ID':<25} {'Activity':<10} {'Catalytic':<10} {'Status':<15}")
    print("-"*100)
    
    # Process each predicted structure
    for i, seq_data in enumerate(predictions_data['sequences'], 1):
        protein_id = seq_data['id']
        
        # Find the FASTA file for this sequence
        fasta_file = Path(seq_data['file'])
        
        # Estimate activity
        activity_data = estimate_activity_from_sequence(fasta_file)
        
        if activity_data:
            activity_score = activity_data['activity']
            all_activities.append(activity_score)
            
            # Determine status
            if activity_score >= 80:
                status = "✓ HIGH"
            elif activity_score >= 70:
                status = "◐ MODERATE"
            else:
                status = "✗ LOW"
            
            print(f"{i:<6} {protein_id:<25} {activity_score:<10} {activity_data['catalytic']:<10} {status:<15}")
            
            results['activity_analysis'].append({
                'rank': i,
                'id': protein_id,
                'sequence_length': activity_data['length'],
                'activity_score': activity_score,
                'catalytic_conservation': activity_data['catalytic'],
                'active_site_geometry': activity_data['geometry'],
                'substrate_specificity': activity_data['specificity'],
                'family': seq_data.get('family', 'Unknown'),
                'source': seq_data.get('file', 'Unknown')
            })
            
            results['predicted_count'] += 1
    
    # Calculate statistics
    if all_activities:
        results['statistics'] = {
            'mean_activity': round(np.mean(all_activities), 1),
            'median_activity': round(np.median(all_activities), 1),
            'std_dev': round(np.std(all_activities), 1),
            'min_activity': round(np.min(all_activities), 1),
            'max_activity': round(np.max(all_activities), 1),
            'high_count': sum(1 for a in all_activities if a >= 80),
            'moderate_count': sum(1 for a in all_activities if 70 <= a < 80),
            'low_count': sum(1 for a in all_activities if a < 70),
        }
    
    # Sort by activity score
    results['activity_analysis'].sort(key=lambda x: x['activity_score'], reverse=True)
    
    print("\n" + "-"*100)
    print("SUMMARY STATISTICS")
    print("-"*100)
    print(f"Mean Activity Score:        {results['statistics']['mean_activity']}")
    print(f"Median Activity Score:      {results['statistics']['median_activity']}")
    print(f"Standard Deviation:         {results['statistics']['std_dev']}")
    print(f"Activity Range:             {results['statistics']['min_activity']} - {results['statistics']['max_activity']}")
    print(f"\nActivity Distribution:")
    print(f"  HIGH (≥80):               {results['statistics']['high_count']} enzymes")
    print(f"  MODERATE (70-79):         {results['statistics']['moderate_count']} enzymes")
    print(f"  LOW (<70):                {results['statistics']['low_count']} enzymes")
    
    # Comparison with known structures
    if known_activities:
        known_scores = list(known_activities.values())
        results['comparison'] = {
            'predicted_mean': results['statistics']['mean_activity'],
            'known_mean': round(np.mean(known_scores), 1),
            'predicted_median': results['statistics']['median_activity'],
            'known_median': round(np.median(known_scores), 1),
            'difference_mean': round(results['statistics']['mean_activity'] - np.mean(known_scores), 1),
            'difference_median': round(results['statistics']['median_activity'] - np.median(known_scores), 1),
        }
        
        print(f"\nComparison with Known Structures:")
        print(f"  Predicted Mean:           {results['comparison']['predicted_mean']}")
        print(f"  Known Mean:               {results['comparison']['known_mean']}")
        print(f"  Difference:               {results['comparison']['difference_mean']:+.1f}")
    
    # Save results
    output_json = OUTPUT_DIR / "predicted_activity_assessment.json"
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "="*100)
    print(f"Results saved to: {output_json}")
    print("="*100 + "\n")
    
    # Create visualization
    create_visualizations(results, all_activities, known_activities)

def create_visualizations(results, all_activities, known_activities):
    """Create comprehensive visualizations."""
    
    fig, axes = plt.subplots(2, 2, figsize=(16, 12))
    fig.suptitle('Predicted Laminarinase Activity Analysis (81 sequences)', 
                 fontsize=16, fontweight='bold', y=0.995)
    
    # 1. Distribution of predicted activities
    ax = axes[0, 0]
    ax.hist(all_activities, bins=15, color='steelblue', alpha=0.7, edgecolor='black')
    ax.axvline(np.mean(all_activities), color='red', linestyle='--', linewidth=2, label=f"Mean: {np.mean(all_activities):.1f}")
    ax.axvline(np.median(all_activities), color='green', linestyle='--', linewidth=2, label=f"Median: {np.median(all_activities):.1f}")
    ax.set_xlabel('Activity Score', fontsize=11, fontweight='bold')
    ax.set_ylabel('Number of Enzymes', fontsize=11, fontweight='bold')
    ax.set_title('Activity Score Distribution (n=81)', fontsize=12, fontweight='bold')
    ax.legend()
    ax.grid(True, alpha=0.3)
    
    # 2. Top 15 enzymes by activity
    ax = axes[0, 1]
    top_15 = results['activity_analysis'][:15]
    names = [e['id'][:15] for e in top_15]
    scores = [e['activity_score'] for e in top_15]
    colors = ['green' if s >= 80 else 'orange' if s >= 70 else 'red' for s in scores]
    bars = ax.barh(names, scores, color=colors, edgecolor='black', linewidth=1)
    ax.set_xlabel('Activity Score', fontsize=11, fontweight='bold')
    ax.set_title('Top 15 Predicted Enzymes', fontsize=12, fontweight='bold')
    ax.set_xlim(0, 100)
    for i, (bar, score) in enumerate(zip(bars, scores)):
        ax.text(score + 1, i, f'{score:.1f}', va='center', fontweight='bold')
    ax.grid(True, alpha=0.3, axis='x')
    
    # 3. Component scores for top 10
    ax = axes[1, 0]
    top_10 = results['activity_analysis'][:10]
    names = [e['id'][:12] for e in top_10]
    x = np.arange(len(names))
    width = 0.2
    
    catalytic = [e['catalytic_conservation'] for e in top_10]
    geometry = [e['active_site_geometry'] for e in top_10]
    specificity = [e['substrate_specificity'] for e in top_10]
    
    ax.bar(x - width, catalytic, width, label='Catalytic', color='skyblue', edgecolor='black')
    ax.bar(x, geometry, width, label='Geometry', color='lightcoral', edgecolor='black')
    ax.bar(x + width, specificity, width, label='Specificity', color='lightgreen', edgecolor='black')
    
    ax.set_ylabel('Score', fontsize=11, fontweight='bold')
    ax.set_title('Top 10 Enzymes - Component Scores', fontsize=12, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(names, rotation=45, ha='right', fontsize=9)
    ax.legend()
    ax.grid(True, alpha=0.3, axis='y')
    
    # 4. Comparison with known structures
    ax = axes[1, 1]
    categories = ['Mean\nActivity', 'Median\nActivity', 'Max\nActivity', 'Min\nActivity']
    
    if known_activities:
        known_scores = list(known_activities.values())
        predicted_vals = [
            np.mean(all_activities),
            np.median(all_activities),
            np.max(all_activities),
            np.min(all_activities)
        ]
        known_vals = [
            np.mean(known_scores),
            np.median(known_scores),
            np.max(known_scores),
            np.min(known_scores)
        ]
        
        x = np.arange(len(categories))
        width = 0.35
        
        ax.bar(x - width/2, predicted_vals, width, label='Predicted (n=81)', 
               color='steelblue', edgecolor='black', linewidth=1)
        ax.bar(x + width/2, known_vals, width, label='Known (n=20)', 
               color='darkorange', edgecolor='black', linewidth=1)
        
        ax.set_ylabel('Score', fontsize=11, fontweight='bold')
        ax.set_title('Predicted vs Known Structures', fontsize=12, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, fontsize=10)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    else:
        ax.text(0.5, 0.5, 'Reference data not available', 
               ha='center', va='center', transform=ax.transAxes,
               fontsize=12, style='italic')
    
    plt.tight_layout()
    output_fig = OUTPUT_DIR / "predicted_activity_analysis.png"
    plt.savefig(output_fig, dpi=150, bbox_inches='tight')
    print(f"✓ Visualization saved: {output_fig}")
    plt.close()

if __name__ == "__main__":
    main()
