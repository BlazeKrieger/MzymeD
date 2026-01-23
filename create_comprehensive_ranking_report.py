#!/usr/bin/env python3
"""
Comprehensive ranking report for all laminarinase structures.
Combines activity scores, MD stability, binding sites, and creates multi-figure visualization.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pathlib import Path
from datetime import datetime
import pandas as pd

# Base paths
BASE_DIR = Path(__file__).parent
ANALYSIS_DIR = BASE_DIR / "analysis_results"
PREDICTED_ANALYSIS_DIR = BASE_DIR / "predicted_activity_analysis"
EXPERIMENTAL_PLAN_DIR = BASE_DIR / "experimental_validation_plan"
OUTPUT_DIR = BASE_DIR / "comprehensive_ranking"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

def load_activity_scores():
    """Load predicted activity scores."""
    activity_file = PREDICTED_ANALYSIS_DIR / "predicted_activity_assessment.json"
    if activity_file.exists():
        with open(activity_file) as f:
            return json.load(f)
    return {}

def load_top5_candidates():
    """Load top 5 experimental candidates."""
    top5_file = EXPERIMENTAL_PLAN_DIR / "top5_experimental_validation_plan.json"
    if top5_file.exists():
        with open(top5_file) as f:
            return json.load(f)
    return {}

def load_binding_site_analysis():
    """Load binding site analysis for known structures."""
    binding_file = ANALYSIS_DIR / "binding_site_analysis.json"
    if binding_file.exists():
        with open(binding_file) as f:
            return json.load(f)
    return {}

def load_all_md_results():
    """Load all MD results from batch run."""
    results = {}
    for rmsd_file in ANALYSIS_DIR.glob("glucan_complex_*_rmsd.json"):
        pdb_id = rmsd_file.stem.replace("glucan_complex_", "").replace("_rmsd", "")
        try:
            with open(rmsd_file) as f:
                results[pdb_id] = json.load(f)
        except:
            pass
    return results

def create_comprehensive_report():
    """Create comprehensive ranking report with all data."""
    
    print("Loading data...")
    activity_scores = load_activity_scores()
    top5_candidates = load_top5_candidates()
    binding_sites = load_binding_site_analysis()
    md_results = load_all_md_results()
    
    # Create multi-panel figure
    fig = plt.figure(figsize=(20, 24))
    fig.suptitle('Comprehensive Laminarinase Structure Ranking Report', 
                 fontsize=24, fontweight='bold', y=0.995)
    
    # Panel 1: Activity Score Distribution (All 81 predicted + Top 5)
    print("Creating Panel 1: Activity Score Distribution...")
    ax1 = plt.subplot(4, 2, 1)
    
    if activity_scores.get("sequences"):
        scores = [s.get("activity_score", 0) for s in activity_scores["sequences"]]
        ax1.hist(scores, bins=20, alpha=0.7, color='steelblue', edgecolor='black')
        
        # Mark top 5
        if top5_candidates.get("top_5"):
            top5_scores = [c.get("activity_score", 0) for c in top5_candidates["top_5"]]
            for score in top5_scores:
                ax1.axvline(score, color='red', linestyle='--', linewidth=2, alpha=0.7)
        
        ax1.set_xlabel('Activity Score', fontsize=12, fontweight='bold')
        ax1.set_ylabel('Count', fontsize=12, fontweight='bold')
        ax1.set_title('Panel 1: Activity Score Distribution (81 Predicted)', fontsize=13, fontweight='bold')
        ax1.grid(True, alpha=0.3)
    
    # Panel 2: Top 15 Activity Ranking
    print("Creating Panel 2: Top 15 Candidates...")
    ax2 = plt.subplot(4, 2, 2)
    
    if activity_scores.get("sequences"):
        top_15 = sorted(activity_scores["sequences"], 
                       key=lambda x: x.get("activity_score", 0), 
                       reverse=True)[:15]
        names = [s.get("sequence_id", "Unknown")[:20] for s in top_15]
        scores = [s.get("activity_score", 0) for s in top_15]
        colors = ['red' if any(c.get("sequence_id") == s.get("sequence_id") 
                              for c in top5_candidates.get("top_5", [])) 
                 else 'steelblue' for s in top_15]
        
        y_pos = np.arange(len(names))
        ax2.barh(y_pos, scores, color=colors, edgecolor='black')
        ax2.set_yticks(y_pos)
        ax2.set_yticklabels(names, fontsize=9)
        ax2.set_xlabel('Activity Score', fontsize=12, fontweight='bold')
        ax2.set_title('Panel 2: Top 15 Activity Ranking', fontsize=13, fontweight='bold')
        ax2.invert_yaxis()
        ax2.grid(True, alpha=0.3, axis='x')
    
    # Panel 3: MD Stability Comparison (Known Structures)
    print("Creating Panel 3: MD Stability...")
    ax3 = plt.subplot(4, 2, 3)
    
    if md_results:
        pdb_ids = sorted(md_results.keys())
        mean_rmsd = [md_results[p].get("mean_rmsd_nm", 0) for p in pdb_ids]
        max_rmsd = [md_results[p].get("max_rmsd_nm", 0) for p in pdb_ids]
        
        x = np.arange(len(pdb_ids))
        width = 0.35
        ax3.bar(x - width/2, mean_rmsd, width, label='Mean RMSD', 
               color='steelblue', edgecolor='black')
        ax3.bar(x + width/2, max_rmsd, width, label='Max RMSD', 
               color='orange', edgecolor='black')
        
        ax3.set_ylabel('RMSD (nm)', fontsize=12, fontweight='bold')
        ax3.set_title('Panel 3: MD Stability (100 ps)', fontsize=13, fontweight='bold')
        ax3.set_xticks(x)
        ax3.set_xticklabels(pdb_ids)
        ax3.legend()
        ax3.grid(True, alpha=0.3, axis='y')
    
    # Panel 4: Stability Classification
    print("Creating Panel 4: Stability Classification...")
    ax4 = plt.subplot(4, 2, 4)
    
    if md_results:
        stability_categories = {"Very Stable": 0, "Stable": 0, "Moderate": 0, "Unstable": 0}
        for pdb_id, data in md_results.items():
            mean_rmsd = data.get("mean_rmsd_nm", 0)
            if mean_rmsd < 0.10:
                stability_categories["Very Stable"] += 1
            elif mean_rmsd < 0.15:
                stability_categories["Stable"] += 1
            elif mean_rmsd < 0.25:
                stability_categories["Moderate"] += 1
            else:
                stability_categories["Unstable"] += 1
        
        categories = list(stability_categories.keys())
        counts = list(stability_categories.values())
        colors_stability = ['darkgreen', 'green', 'orange', 'red']
        
        wedges, texts, autotexts = ax4.pie(counts, labels=categories, autopct='%1.0f%%',
                                           colors=colors_stability, startangle=90)
        ax4.set_title('Panel 4: Stability Classification', fontsize=13, fontweight='bold')
        
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
    
    # Panel 5: Binding Site Analysis
    print("Creating Panel 5: Binding Site Analysis...")
    ax5 = plt.subplot(4, 2, 5)
    
    if binding_sites.get("structures"):
        struct_ids = list(binding_sites["structures"].keys())[:6]  # Top 6
        residue_counts = [len(binding_sites["structures"][s].get("binding_residues", [])) 
                         for s in struct_ids]
        
        bars = ax5.bar(struct_ids, residue_counts, color='teal', edgecolor='black')
        ax5.set_ylabel('Number of Binding Residues', fontsize=12, fontweight='bold')
        ax5.set_title('Panel 5: Binding Site Size Comparison', fontsize=13, fontweight='bold')
        ax5.grid(True, alpha=0.3, axis='y')
        
        # Add values on bars
        for bar in bars:
            height = bar.get_height()
            ax5.text(bar.get_x() + bar.get_width()/2., height,
                    f'{int(height)}', ha='center', va='bottom', fontweight='bold')
    
    # Panel 6: Top 5 Recommendation Cards
    print("Creating Panel 6: Top 5 Recommendations...")
    ax6 = plt.subplot(4, 2, 6)
    ax6.axis('off')
    
    if top5_candidates.get("top_5"):
        text_str = "TOP 5 CANDIDATES FOR EXPERIMENTAL VALIDATION\n" + "="*50 + "\n\n"
        for i, candidate in enumerate(top5_candidates["top_5"], 1):
            seq_id = candidate.get("sequence_id", "Unknown")[:30]
            activity = candidate.get("activity_score", 0)
            family = candidate.get("family", "Unknown")
            length = candidate.get("sequence_length", "Unknown")
            
            text_str += f"{i}. {seq_id}\n"
            text_str += f"   Activity: {activity:.1f} | Family: {family} | Length: {length}\n\n"
        
        ax6.text(0.05, 0.95, text_str, transform=ax6.transAxes,
                fontsize=10, verticalalignment='top', family='monospace',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
    
    # Panel 7: Overall Composite Ranking
    print("Creating Panel 7: Composite Ranking...")
    ax7 = plt.subplot(4, 2, 7)
    
    # Combine known and top predicted
    composite_ranking = []
    
    if top5_candidates.get("top_5"):
        for i, cand in enumerate(top5_candidates["top_5"], 1):
            composite_ranking.append({
                "rank": i,
                "name": cand.get("sequence_id", "Unknown")[:15],
                "score": (cand.get("activity_score", 0) + 80) / 2  # Normalized
            })
    
    if md_results:
        for i, (pdb_id, data) in enumerate(sorted(md_results.items(), 
                                                   key=lambda x: x[1].get("mean_rmsd_nm", 1)), 1):
            # Stability score (lower RMSD = higher score)
            rmsd = data.get("mean_rmsd_nm", 1)
            stability_score = max(0, 100 - rmsd * 1000)
            composite_ranking.append({
                "rank": len(top5_candidates.get("top_5", [])) + i,
                "name": pdb_id,
                "score": stability_score
            })
    
    if composite_ranking:
        composite_ranking = sorted(composite_ranking, key=lambda x: x["score"], reverse=True)[:10]
        names = [r["name"] for r in composite_ranking]
        scores = [r["score"] for r in composite_ranking]
        ranks = [r["rank"] for r in composite_ranking]
        
        y_pos = np.arange(len(names))
        colors_ranking = plt.cm.RdYlGn(np.linspace(1, 0, len(names)))
        
        ax7.barh(y_pos, scores, color=colors_ranking, edgecolor='black')
        ax7.set_yticks(y_pos)
        ax7.set_yticklabels(names, fontsize=10)
        ax7.set_xlabel('Composite Score', fontsize=12, fontweight='bold')
        ax7.set_title('Panel 7: Top 10 Composite Ranking', fontsize=13, fontweight='bold')
        ax7.invert_yaxis()
        ax7.grid(True, alpha=0.3, axis='x')
    
    # Panel 8: Summary Statistics
    print("Creating Panel 8: Summary Statistics...")
    ax8 = plt.subplot(4, 2, 8)
    ax8.axis('off')
    
    summary_text = f"""
COMPREHENSIVE ANALYSIS SUMMARY
{'='*50}

STRUCTURES ANALYZED:
  • Known PDB structures: 4 (2W52, 2W39, 4BPZ, 4BOW)
  • Predicted structures: 81
  • Total: 85

ACTIVITY ASSESSMENT:
  • Mean activity score: {np.mean([s.get('activity_score', 0) for s in activity_scores.get('sequences', [])]):.1f}
  • Max activity score: {max([s.get('activity_score', 0) for s in activity_scores.get('sequences', [])]) if activity_scores.get('sequences') else 0:.1f}
  • Top 5 average: {np.mean([c.get('activity_score', 0) for c in top5_candidates.get('top_5', [])]):.1f}

MD STABILITY:
  • Structures simulated: {len(md_results)}
  • Mean RMSD: {np.mean([d.get('mean_rmsd_nm', 0) for d in md_results.values()]):.3f} nm
  • Max RMSD: {max([d.get('max_rmsd_nm', 0) for d in md_results.values()]) if md_results else 0:.3f} nm

BINDING ANALYSIS:
  • Structures with binding data: {len(binding_sites.get('structures', {}))}
  • Avg residues per binding site: {np.mean([len(b.get('binding_residues', [])) for b in binding_sites.get('structures', {}).values()]) if binding_sites.get('structures') else 0:.1f}

Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    """
    
    ax8.text(0.05, 0.95, summary_text, transform=ax8.transAxes,
            fontsize=9, verticalalignment='top', family='monospace',
            bbox=dict(boxstyle='round', facecolor='lightblue', alpha=0.5))
    
    # Save figure
    plt.tight_layout()
    report_file = OUTPUT_DIR / "comprehensive_ranking_report.png"
    plt.savefig(report_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Report figure saved: {report_file}")
    
    # Create markdown report
    create_markdown_report(activity_scores, top5_candidates, binding_sites, md_results)
    
    return OUTPUT_DIR

def create_markdown_report(activity_scores, top5_candidates, binding_sites, md_results):
    """Create detailed markdown report."""
    
    report_file = OUTPUT_DIR / "COMPREHENSIVE_RANKING_REPORT.md"
    
    with open(report_file, 'w') as f:
        f.write("# Comprehensive Laminarinase Structure Ranking Report\n\n")
        f.write(f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Executive Summary
        f.write("## Executive Summary\n\n")
        f.write("This report consolidates a comprehensive analysis of laminarinase structures, combining:\n")
        f.write("- **Predicted activity scores** for 81 novel sequences\n")
        f.write("- **Molecular dynamics stability** for known PDB structures\n")
        f.write("- **Binding site characterization** for enzyme-substrate complexes\n")
        f.write("- **Top 5 candidates** selected for experimental validation\n\n")
        
        # Activity Assessment
        f.write("## 1. Activity Assessment (81 Predicted Sequences)\n\n")
        if activity_scores.get("sequences"):
            scores = [s.get("activity_score", 0) for s in activity_scores["sequences"]]
            f.write(f"- **Mean activity score**: {np.mean(scores):.2f}\n")
            f.write(f"- **Median activity score**: {np.median(scores):.2f}\n")
            f.write(f"- **Max activity score**: {max(scores):.2f}\n")
            f.write(f"- **Min activity score**: {min(scores):.2f}\n")
            f.write(f"- **Standard deviation**: {np.std(scores):.2f}\n\n")
            
            # Top 15 ranking
            top_15 = sorted(activity_scores["sequences"], 
                           key=lambda x: x.get("activity_score", 0), 
                           reverse=True)[:15]
            f.write("### Top 15 Predicted Sequences\n\n")
            f.write("| Rank | Sequence ID | Activity Score | Family | Length |\n")
            f.write("|------|-------------|----------------|--------|--------|\n")
            for i, seq in enumerate(top_15, 1):
                f.write(f"| {i} | {seq.get('sequence_id', 'Unknown')} | {seq.get('activity_score', 0):.1f} | "
                       f"{seq.get('family', 'Unknown')} | {seq.get('sequence_length', '?')} |\n")
            f.write("\n")
        
        # MD Stability
        f.write("## 2. MD Stability Analysis (Known Structures)\n\n")
        if md_results:
            f.write("### RMSD Metrics (100 ps MD simulation)\n\n")
            f.write("| PDB ID | Mean RMSD (nm) | Max RMSD (nm) | Frames | Status |\n")
            f.write("|--------|----------------|----------------|--------|--------|\n")
            for pdb_id in sorted(md_results.keys()):
                data = md_results[pdb_id]
                mean_rmsd = data.get("mean_rmsd_nm", 0)
                max_rmsd = data.get("max_rmsd_nm", 0)
                frames = data.get("frames", 0)
                status = "✓ Stable" if mean_rmsd < 0.15 else "⚠ Moderate" if mean_rmsd < 0.25 else "✗ Unstable"
                f.write(f"| {pdb_id} | {mean_rmsd:.4f} | {max_rmsd:.4f} | {frames} | {status} |\n")
            f.write("\n")
        
        # Binding Site Analysis
        f.write("## 3. Binding Site Analysis\n\n")
        if binding_sites.get("structures"):
            for struct_id, struct_data in binding_sites["structures"].items():
                f.write(f"### {struct_id}\n")
                residues = struct_data.get("binding_residues", [])
                f.write(f"- **Binding residues**: {len(residues)}\n")
                f.write(f"- **Residues**: {', '.join(residues[:10])}")
                if len(residues) > 10:
                    f.write(f", ... and {len(residues)-10} more")
                f.write("\n\n")
        
        # Top 5 Candidates
        f.write("## 4. Top 5 Candidates for Experimental Validation\n\n")
        if top5_candidates.get("top_5"):
            for i, cand in enumerate(top5_candidates["top_5"], 1):
                f.write(f"### Candidate {i}: {cand.get('sequence_id', 'Unknown')}\n\n")
                f.write(f"- **Activity Score**: {cand.get('activity_score', 0):.2f}\n")
                f.write(f"- **Family**: {cand.get('family', 'Unknown')}\n")
                f.write(f"- **Length**: {cand.get('sequence_length', '?')} amino acids\n")
                f.write(f"- **Priority**: Rank {i}\n\n")
        
        f.write("## 5. Recommendations\n\n")
        f.write("1. Prioritize experimental validation of top 5 candidates based on activity scores\n")
        f.write("2. Focus on stable structures (mean RMSD < 0.15 nm) for initial studies\n")
        f.write("3. Investigate binding site residues for mutation studies\n")
        f.write("4. Consider family-based clustering for targeted screening\n\n")
        
        f.write("---\n")
        f.write(f"*Report generated: {datetime.now().isoformat()}*\n")
    
    print(f"✓ Markdown report saved: {report_file}")

if __name__ == "__main__":
    create_comprehensive_report()
    print("\n✓ All reports generated successfully!")
