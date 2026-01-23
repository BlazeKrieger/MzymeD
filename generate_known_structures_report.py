#!/usr/bin/env python3
"""
Generate comprehensive ranking report for the 4 known laminarinase structures
that successfully completed MD simulations.
"""

import json
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

REPO_ROOT = Path(__file__).parent
BATCH_RESULTS = REPO_ROOT / "batch_md_results" / "batch_md_results.json"
OUTPUT_DIR = REPO_ROOT / "known_structures_report"
OUTPUT_DIR.mkdir(exist_ok=True)

# Known structure metadata
KNOWN_STRUCTURES = {
    "2W39": {
        "name": "Laminarinase from Thermotoga maritima",
        "gh_family": "GH16",
        "organism": "Thermotoga maritima",
        "resolution": "2.0 Å",
        "ligand": "β-1,3-glucan (laminarin)"
    },
    "2W52": {
        "name": "Laminarinase-substrate complex",
        "gh_family": "GH16", 
        "organism": "Thermotoga maritima",
        "resolution": "2.2 Å",
        "ligand": "β-1,3-glucan oligosaccharide"
    },
    "4BOW": {
        "name": "Endo-β-1,3-glucanase",
        "gh_family": "GH16",
        "organism": "Streptomyces sioyaensis",
        "resolution": "1.8 Å",
        "ligand": "Laminarin hexasaccharide"
    },
    "4BPZ": {
        "name": "Endo-β-1,3-glucanase complex",
        "gh_family": "GH16",
        "organism": "Streptomyces sioyaensis", 
        "resolution": "2.0 Å",
        "ligand": "Laminarin tetrasaccharide"
    }
}

def load_batch_results():
    """Load MD results from batch simulation."""
    print(f"[LOAD] Reading batch results from {BATCH_RESULTS.name}...")
    
    with open(BATCH_RESULTS) as f:
        data = json.load(f)
    
    # Filter only known structures with RMSD data
    working_results = []
    for structure_id, structure_data in data["structures"].items():
        if structure_id in KNOWN_STRUCTURES and structure_data.get("rmsd_data"):
            rmsd_data = structure_data["rmsd_data"]
            md_result = structure_data["md_result"]
            
            working_results.append({
                "structure_id": structure_id,
                "mean_rmsd_nm": rmsd_data["mean_rmsd_nm"],
                "max_rmsd_nm": rmsd_data["max_rmsd_nm"],
                "runtime_sec": md_result["elapsed_seconds"]
            })
    
    print(f"[SUCCESS] Found {len(working_results)} structures with valid MD data")
    return working_results

def calculate_stability_score(result):
    """Calculate stability score (0-100) based on RMSD."""
    mean_rmsd = result["mean_rmsd_nm"]
    max_rmsd = result["max_rmsd_nm"]
    
    # Lower RMSD = higher stability
    # RMSD < 0.15 nm = excellent (90-100)
    # RMSD 0.15-0.20 = good (70-90)
    # RMSD 0.20-0.30 = moderate (50-70)
    # RMSD > 0.30 = poor (0-50)
    
    if mean_rmsd < 0.15:
        base_score = 100 - (mean_rmsd / 0.15) * 10
    elif mean_rmsd < 0.20:
        base_score = 90 - ((mean_rmsd - 0.15) / 0.05) * 20
    elif mean_rmsd < 0.30:
        base_score = 70 - ((mean_rmsd - 0.20) / 0.10) * 20
    else:
        base_score = max(0, 50 - (mean_rmsd - 0.30) * 50)
    
    # Penalize high max RMSD (indicates instability spikes)
    if max_rmsd > mean_rmsd * 1.5:
        base_score *= 0.9
    
    return round(base_score, 1)

def generate_ranking():
    """Generate structure ranking."""
    results = load_batch_results()
    
    # Add metadata and scores
    ranked = []
    for result in results:
        structure_id = result["structure_id"]
        metadata = KNOWN_STRUCTURES[structure_id]
        
        stability_score = calculate_stability_score(result)
        
        ranked.append({
            "structure_id": structure_id,
            "name": metadata["name"],
            "organism": metadata["organism"],
            "gh_family": metadata["gh_family"],
            "resolution": metadata["resolution"],
            "ligand": metadata["ligand"],
            "mean_rmsd_nm": result["mean_rmsd_nm"],
            "max_rmsd_nm": result["max_rmsd_nm"],
            "runtime_sec": result["runtime_sec"],
            "stability_score": stability_score
        })
    
    # Sort by stability score (descending)
    ranked.sort(key=lambda x: x["stability_score"], reverse=True)
    
    return ranked

def create_visualization(ranked):
    """Create comprehensive visualization."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Known Laminarinase Structures - MD Stability Analysis', 
                 fontsize=16, fontweight='bold')
    
    structure_ids = [r["structure_id"] for r in ranked]
    stability_scores = [r["stability_score"] for r in ranked]
    mean_rmsds = [r["mean_rmsd_nm"] * 10 for r in ranked]  # Convert to Å
    max_rmsds = [r["max_rmsd_nm"] * 10 for r in ranked]
    
    colors = ['#2ecc71', '#3498db', '#f39c12', '#e74c3c']
    
    # 1. Stability Scores
    ax1 = axes[0, 0]
    bars1 = ax1.barh(structure_ids, stability_scores, color=colors)
    ax1.set_xlabel('Stability Score (0-100)', fontweight='bold')
    ax1.set_title('Overall Stability Ranking')
    ax1.set_xlim(0, 100)
    for i, (bar, score) in enumerate(zip(bars1, stability_scores)):
        ax1.text(score + 2, i, f'{score:.1f}', va='center', fontweight='bold')
    ax1.grid(axis='x', alpha=0.3)
    
    # 2. RMSD Comparison
    ax2 = axes[0, 1]
    x = np.arange(len(structure_ids))
    width = 0.35
    ax2.bar(x - width/2, mean_rmsds, width, label='Mean RMSD', color='#3498db', alpha=0.8)
    ax2.bar(x + width/2, max_rmsds, width, label='Max RMSD', color='#e74c3c', alpha=0.8)
    ax2.set_ylabel('RMSD (Å)', fontweight='bold')
    ax2.set_title('RMSD Analysis')
    ax2.set_xticks(x)
    ax2.set_xticklabels(structure_ids)
    ax2.legend()
    ax2.grid(axis='y', alpha=0.3)
    
    # 3. RMSD Stability Matrix
    ax3 = axes[1, 0]
    rmsd_data = np.array([[mean_rmsds[i], max_rmsds[i]] for i in range(len(structure_ids))])
    im = ax3.imshow(rmsd_data.T, cmap='RdYlGn_r', aspect='auto')
    ax3.set_xticks(np.arange(len(structure_ids)))
    ax3.set_yticks([0, 1])
    ax3.set_xticklabels(structure_ids)
    ax3.set_yticklabels(['Mean RMSD', 'Max RMSD'])
    ax3.set_title('RMSD Heatmap (Å)')
    
    # Add text annotations
    for i in range(len(structure_ids)):
        for j in range(2):
            text = ax3.text(i, j, f'{rmsd_data[i, j]:.2f}',
                          ha="center", va="center", color="white", fontweight='bold')
    
    plt.colorbar(im, ax=ax3, label='RMSD (Å)')
    
    # 4. Summary Table
    ax4 = axes[1, 1]
    ax4.axis('tight')
    ax4.axis('off')
    
    table_data = []
    headers = ['PDB', 'Organism', 'Score', 'Mean RMSD']
    for r in ranked:
        organism_short = r["organism"].split()[0][:15]
        table_data.append([
            r["structure_id"],
            organism_short,
            f'{r["stability_score"]:.1f}',
            f'{r["mean_rmsd_nm"]*10:.2f} Å'
        ])
    
    table = ax4.table(cellText=table_data, colLabels=headers,
                     cellLoc='center', loc='center',
                     colWidths=[0.15, 0.35, 0.2, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2)
    
    # Color cells by score
    for i in range(1, len(ranked) + 1):
        score = ranked[i-1]["stability_score"]
        if score >= 90:
            color = '#d5f4e6'
        elif score >= 70:
            color = '#fff3cd'
        else:
            color = '#f8d7da'
        table[(i, 2)].set_facecolor(color)
    
    plt.tight_layout()
    
    output_file = OUTPUT_DIR / "stability_analysis.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"[SAVE] Visualization saved to {output_file}")
    plt.close()

def save_report(ranked):
    """Save comprehensive JSON report."""
    report = {
        "analysis_type": "Known Laminarinase Structures - MD Stability",
        "total_structures": len(ranked),
        "simulation_parameters": {
            "duration_ps": 100,
            "steps": 50000,
            "platform": "OpenCL/CPU",
            "force_field": "AMBER14 + GLYCAM06j-1",
            "solvent": "Implicit (GBn2)"
        },
        "ranking": ranked,
        "notes": [
            "Only known PDB structures with ligands successfully ran MD",
            "Predicted structures failed due to crude extended conformation geometry",
            "RMSD measured relative to initial minimized structure",
            "Lower RMSD indicates better structural stability"
        ]
    }
    
    output_file = OUTPUT_DIR / "stability_ranking.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"[SAVE] Ranking report saved to {output_file}")

def print_summary(ranked):
    """Print summary to console."""
    print("\n" + "="*80)
    print("KNOWN LAMINARINASE STRUCTURES - STABILITY RANKING")
    print("="*80)
    print(f"{'Rank':<6} {'PDB':<8} {'Organism':<25} {'Score':<8} {'Mean RMSD'}")
    print("-"*80)
    
    for i, r in enumerate(ranked, 1):
        organism_short = r["organism"].split()[0][:24]
        print(f"{i:<6} {r['structure_id']:<8} {organism_short:<25} {r['stability_score']:<8.1f} {r['mean_rmsd_nm']*10:.2f} Å")
    
    print("="*80)
    print(f"\n[BEST] {ranked[0]['structure_id']}: {ranked[0]['name']}")
    print(f"       Stability Score: {ranked[0]['stability_score']}/100")
    print(f"       Mean RMSD: {ranked[0]['mean_rmsd_nm']*10:.2f} Å")
    print(f"       {ranked[0]['organism']}")
    print(f"\n[OUTPUT] Report directory: {OUTPUT_DIR}")
    print("="*80 + "\n")

def main():
    print("\n" + "="*80)
    print("KNOWN STRUCTURES STABILITY ANALYSIS")
    print("="*80)
    
    ranked = generate_ranking()
    create_visualization(ranked)
    save_report(ranked)
    print_summary(ranked)
    
    print("\n[NOTE] Predicted structures require ML-based prediction")
    print("       (ESMFold/AlphaFold) for proper MD simulation.")
    print("       Extended conformations are too crude for OpenMM.\n")

if __name__ == "__main__":
    main()
