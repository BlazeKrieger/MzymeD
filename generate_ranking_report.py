#!/usr/bin/env python3
"""
Generate comprehensive ranking report for laminarinase structures based on available MD data.
Works with successfully simulated structures only.
"""

import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend

# Directories
BASE_DIR = Path(__file__).parent
BATCH_RESULTS = BASE_DIR / "batch_md_results" / "batch_md_results.json"
ANALYSIS_DIR = BASE_DIR / "analysis_results"
PREDICTIONS_FILE = BASE_DIR / "predicted_laminarinases.json"
OUTPUT_DIR = BASE_DIR / "ranking_report"

OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

def load_predictions():
    """Load activity predictions for laminarinases."""
    if not PREDICTIONS_FILE.exists():
        return {}
    
    try:
        with open(PREDICTIONS_FILE) as f:
            data = json.load(f)
            # Extract predicted laminarinases
            preds = {}
            if "predictions" in data:
                for pred in data["predictions"]:
                    acc = pred.get("accession")
                    if acc:
                        preds[acc] = {
                            "activity_score": pred.get("activity_score", 0.0),
                            "stability_score": pred.get("stability_score", 0.0),
                            "binding_score": pred.get("binding_score", 0.0),
                            "overall_score": pred.get("overall_score", 0.0)
                        }
            return preds
    except:
        return {}

def load_md_results():
    """Load MD simulation results."""
    if not BATCH_RESULTS.exists():
        return {}
    
    try:
        with open(BATCH_RESULTS) as f:
            data = json.load(f)
            results = {}
            for pdb_id, info in data.get("structures", {}).items():
                if info.get("md_result", {}).get("success") and info.get("rmsd_data"):
                    rmsd = info["rmsd_data"]
                    results[pdb_id] = {
                        "mean_rmsd_nm": rmsd.get("mean_rmsd_nm", np.nan),
                        "max_rmsd_nm": rmsd.get("max_rmsd_nm", np.nan),
                        "frames": rmsd.get("frames", 0),
                        "atoms": rmsd.get("atoms", 0),
                        "md_success": True
                    }
            return results
    except:
        return {}

def create_ranking_table(md_results, predictions):
    """Create ranking table with all available data."""
    print("\n" + "="*100)
    print("LAMINARINASE STRUCTURE RANKING")
    print("="*100)
    
    # Collect all structures
    structures = {}
    
    # Add known structures with MD data
    for pdb_id in ["2W39", "2W52", "4BOW", "4BPZ"]:
        if pdb_id in md_results:
            rmsd = md_results[pdb_id]
            structures[pdb_id] = {
                "type": "known",
                "mean_rmsd_nm": rmsd["mean_rmsd_nm"],
                "max_rmsd_nm": rmsd["max_rmsd_nm"],
                "frames": rmsd["frames"],
                "stability_score": 10.0 - (rmsd["mean_rmsd_nm"] * 10),  # Normalize: lower RMSD = higher score
                "activity_score": None,
                "binding_score": None
            }
    
    # Add predicted structures (those with MD data)
    for pdb_id, rmsd_data in md_results.items():
        if pdb_id not in ["2W39", "2W52", "4BOW", "4BPZ"]:  # Skip known
            pred_id = pdb_id.replace("_predicted", "")
            pred_data = predictions.get(pred_id, {})
            
            stability = 10.0 - (rmsd_data["mean_rmsd_nm"] * 10)
            
            structures[pdb_id] = {
                "type": "predicted",
                "mean_rmsd_nm": rmsd_data["mean_rmsd_nm"],
                "max_rmsd_nm": rmsd_data["max_rmsd_nm"],
                "frames": rmsd_data["frames"],
                "stability_score": stability,
                "activity_score": pred_data.get("activity_score"),
                "binding_score": pred_data.get("binding_score"),
                "overall_score": pred_data.get("overall_score")
            }
    
    # Sort by stability then activity
    sorted_structs = sorted(
        structures.items(),
        key=lambda x: (x[1]["stability_score"], x[1].get("activity_score") or 0),
        reverse=True
    )
    
    # Print table
    print(f"\n{'Rank':<5} {'Structure':<20} {'Type':<10} {'RMSD(Å)':<10} {'Stability':<12} {'Activity':<12} {'Overall':<10}")
    print("-" * 100)
    
    for rank, (struct_id, data) in enumerate(sorted_structs, 1):
        rmsd_str = f"{data['mean_rmsd_nm']:.3f}"
        stab_str = f"{data['stability_score']:.2f}" if not np.isnan(data['stability_score']) else "N/A"
        act_str = f"{data['activity_score']:.2f}" if data['activity_score'] else "N/A"
        overall_str = f"{data.get('overall_score', 'N/A')}"
        
        print(f"{rank:<5} {struct_id:<20} {data['type']:<10} {rmsd_str:<10} {stab_str:<12} {act_str:<12} {overall_str:<10}")
    
    return sorted_structs

def create_plots(md_results):
    """Create visualization plots."""
    if not md_results:
        print("[WARN] No MD results to plot")
        return
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle('Laminarinase MD Simulation Results', fontsize=16, fontweight='bold')
    
    # Extract data
    pdb_ids = list(md_results.keys())
    mean_rmsds = [md_results[p]["mean_rmsd_nm"] for p in pdb_ids]
    max_rmsds = [md_results[p]["max_rmsd_nm"] for p in pdb_ids]
    types = ["known" if p in ["2W39", "2W52", "4BOW", "4BPZ"] else "predicted" for p in pdb_ids]
    
    # Colors
    colors = ['#2E86AB' if t == "known" else '#A23B72' for t in types]
    
    # Plot 1: Mean RMSD
    ax = axes[0, 0]
    ax.bar(range(len(pdb_ids)), mean_rmsds, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Mean RMSD (Å)', fontweight='bold')
    ax.set_title('Mean RMSD by Structure')
    ax.set_xticks(range(len(pdb_ids)))
    ax.set_xticklabels(pdb_ids, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Plot 2: Max RMSD
    ax = axes[0, 1]
    ax.bar(range(len(pdb_ids)), max_rmsds, color=colors, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Max RMSD (Å)', fontweight='bold')
    ax.set_title('Maximum RMSD by Structure')
    ax.set_xticks(range(len(pdb_ids)))
    ax.set_xticklabels(pdb_ids, rotation=45, ha='right')
    ax.grid(axis='y', alpha=0.3)
    
    # Plot 3: Distribution of stability
    ax = axes[1, 0]
    stability_scores = [10.0 - (rmsd * 10) for rmsd in mean_rmsds]
    ax.scatter(range(len(pdb_ids)), stability_scores, c=colors, s=100, alpha=0.7, edgecolor='black')
    ax.set_ylabel('Stability Score', fontweight='bold')
    ax.set_title('Predicted Stability (inverse RMSD)')
    ax.set_xticks(range(len(pdb_ids)))
    ax.set_xticklabels(pdb_ids, rotation=45, ha='right')
    ax.grid(True, alpha=0.3)
    
    # Plot 4: Legend/Summary
    ax = axes[1, 1]
    ax.axis('off')
    summary_text = f"""
    MD SIMULATION SUMMARY
    {'='*40}
    
    Total structures analyzed: {len(pdb_ids)}
    Known structures:          {sum(1 for t in types if t == 'known')}
    Predicted structures:      {sum(1 for t in types if t == 'predicted')}
    
    Mean RMSD range: {min(mean_rmsds):.3f} - {max(mean_rmsds):.3f} Å
    Average stability: {np.mean(stability_scores):.2f}/10
    
    Legend:
    🔵 Known structures (PDB)
    🟣 Predicted structures
    """
    ax.text(0.1, 0.5, summary_text, fontsize=11, family='monospace',
           verticalalignment='center', bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "md_results_analysis.png", dpi=150, bbox_inches='tight')
    print(f"[OK] Saved: {OUTPUT_DIR / 'md_results_analysis.png'}")
    plt.close()

def main():
    """Generate report."""
    print("\n" + "="*100)
    print("GENERATING LAMINARINASE RANKING REPORT")
    print("="*100)
    
    # Load data
    md_results = load_md_results()
    predictions = load_predictions()
    
    print(f"\n[*] Loaded {len(md_results)} MD simulations")
    print(f"[*] Loaded {len(predictions)} sequence predictions")
    
    if not md_results:
        print("\n[ERROR] No MD results found. Run batch MD first.")
        return
    
    # Generate ranking
    sorted_structs = create_ranking_table(md_results, predictions)
    
    # Create plots
    create_plots(md_results)
    
    # Save ranking to JSON
    ranking_file = OUTPUT_DIR / "structure_ranking.json"
    ranking_data = {
        "timestamp": str(Path("/").stat().st_mtime),
        "total_structures": len(md_results),
        "structures": [
            {
                "rank": rank,
                "id": struct_id,
                **data
            }
            for rank, (struct_id, data) in enumerate(sorted_structs, 1)
        ]
    }
    
    with open(ranking_file, 'w') as f:
        json.dump(ranking_data, f, indent=2)
    
    print(f"\n[OK] Ranking saved: {ranking_file}")
    print(f"[OK] Plots saved: {OUTPUT_DIR / 'md_results_analysis.png'}")
    print(f"\n{'='*100}")
    print(f"Report generation complete!")
    print(f"{'='*100}\n")

if __name__ == "__main__":
    main()
