#!/usr/bin/env python3
"""
Create comparison table: Static Affinity vs Glucanase Activity
"""

import json
import matplotlib.pyplot as plt
import numpy as np

# Load both rankings
with open("comprehensive_laminarinase_ranking.json") as f:
    data = json.load(f)
    static_ranking = data['ranking']

with open("glucanase_activity_analysis/glucanase_activity_assessment.json") as f:
    activity_ranking = json.load(f)

# Sort activity by score
activity_ranking.sort(key=lambda x: x['kcat_km_score'], reverse=True)

# Create comparison table
print("\n" + "="*100)
print("COMPREHENSIVE COMPARISON: Static Affinity vs Glucanase Activity")
print("="*100)
print(f"{'Activity':<8} {'PDB':<6} {'Activity':<9} {'Static':<8} {'GLU':<4} {'Geom':<6} {'Status':<20}")
print(f"{'Rank':<8} {'ID':<6} {'Score':<9} {'Rank':<8} {'#':<4} {'Score':<6} {'& Recommendation':<20}")
print("-"*100)

for i, enzyme in enumerate(activity_ranking, 1):
    pdb_id = enzyme['pdb_id']
    activity_score = enzyme['kcat_km_score']
    static_rank = enzyme['rank']
    n_glu = enzyme['n_glutamates']
    geom = enzyme['geometry_score']
    
    # Find if it's in top tier for both
    in_top_static = static_rank <= 5
    in_top_activity = i <= 5
    
    if in_top_static and in_top_activity:
        status = "⭐ TOP in both"
    elif in_top_activity:
        status = "✓ HIGH activity"
    elif in_top_static:
        status = "✓ HIGH affinity"
    else:
        status = "Good candidate"
    
    print(f"{i:<8} {pdb_id:<6} {activity_score:<9.1f} {static_rank:<8} {n_glu:<4} {geom:<6.0f} {status:<20}")

print("="*100)

# Find top 3 by activity and their static ranking
print("\n" + "="*100)
print("TOP 3 BY GLUCANASE ACTIVITY:")
print("="*100)

for i in range(3):
    enzyme = activity_ranking[i]
    print(f"\n{i+1}. {enzyme['pdb_id']} - Activity Score: {enzyme['kcat_km_score']:.1f}/100")
    print(f"   Static Affinity Rank: #{enzyme['rank']} (Score: {[r for r in static_ranking if r['pdb_id'] == enzyme['pdb_id']][0]['affinity_score']:.1f})")
    print(f"   Glutamates: {enzyme['n_glutamates']} | Geometry: {enzyme['geometry_score']:.0f}/100")
    print(f"   ✓ Optimal for: {'Industrial β-1,3-glucan degradation' if enzyme['kcat_km_score'] >= 90 else 'High-activity biotechnology applications'}")

print("\n" + "="*100)
print("TOP 3 BY STATIC AFFINITY (for comparison):")
print("="*100)

for i in range(3):
    enzyme = static_ranking[i]
    pdb_id = enzyme['pdb_id']
    activity_data = next(a for a in activity_ranking if a['pdb_id'] == pdb_id)
    activity_rank = activity_ranking.index(activity_data) + 1
    
    print(f"\n{i+1}. {pdb_id} - Static Score: {enzyme['affinity_score']:.1f}/100")
    print(f"   Activity Rank: #{activity_rank} (Score: {activity_data['kcat_km_score']:.1f})")
    print(f"   Catalytic residues: {enzyme['catalytic_residues']}/8 | Contacts: {enzyme['substrate_contacts']}")
    print(f"   ✓ Optimal for: Strong substrate binding and multi-site interactions")

# Create comparison scatter plot
fig, ax = plt.subplots(1, 1, figsize=(10, 8))

static_scores = [next(r['affinity_score'] for r in static_ranking if r['pdb_id'] == a['pdb_id']) 
                 for a in activity_ranking]
activity_scores = [a['kcat_km_score'] for a in activity_ranking]
pdb_ids = [a['pdb_id'] for a in activity_ranking]

# Color code by being in top 5 of both
colors = []
for i, pdb in enumerate(pdb_ids):
    static_rank = next(r['rank'] for r in static_ranking if r['pdb_id'] == pdb)
    activity_rank = i + 1
    
    if static_rank <= 5 and activity_rank <= 5:
        colors.append('#FFD700')  # Gold - top in both
    elif activity_rank <= 5:
        colors.append('#1B5E20')  # Green - top activity
    elif static_rank <= 5:
        colors.append('#1565C0')  # Blue - top static
    else:
        colors.append('#757575')  # Gray - other

scatter = ax.scatter(static_scores, activity_scores, s=200, alpha=0.7, 
                    c=colors, edgecolors='black', linewidth=2)

# Add labels for top candidates
for i, pdb in enumerate(pdb_ids):
    static_rank = next(r['rank'] for r in static_ranking if r['pdb_id'] == pdb)
    activity_rank = i + 1
    
    if static_rank <= 5 or activity_rank <= 5:
        ax.annotate(pdb, (static_scores[i], activity_scores[i]), 
                   xytext=(5, 5), textcoords='offset points',
                   fontsize=9, fontweight='bold',
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.7))

ax.set_xlabel('Static Affinity Score', fontsize=13, fontweight='bold')
ax.set_ylabel('Glucanase Activity Score (kcat/Km)', fontsize=13, fontweight='bold')
ax.set_title('Comparison: Static Affinity vs Catalytic Activity\nAll 20 Laminarinase Structures', 
            fontsize=15, fontweight='bold')
ax.grid(alpha=0.3)
ax.set_xlim(0, 70)
ax.set_ylim(65, 95)

# Add legend
from matplotlib.patches import Patch
legend_elements = [
    Patch(facecolor='#FFD700', edgecolor='black', label='⭐ Top 5 in Both'),
    Patch(facecolor='#1B5E20', edgecolor='black', label='Top 5 Activity'),
    Patch(facecolor='#1565C0', edgecolor='black', label='Top 5 Static'),
    Patch(facecolor='#757575', edgecolor='black', label='Other')
]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11)

plt.tight_layout()
plt.savefig("static_vs_activity_comparison.png", dpi=150, bbox_inches='tight')
print("\n✓ Comparison visualization saved: static_vs_activity_comparison.png")

# Final summary
print("\n" + "="*100)
print("KEY FINDINGS:")
print("="*100)
print(f"1. ALL 20 enzymes show HIGH glucanase activity (scores 70-91/100)")
print(f"2. Activity ranking differs from static affinity ranking")
print(f"3. Top activity: 8XPH (91.1) ranked #10 in static affinity")
print(f"4. Top static: 2W52 (62.6) ranked #9 in activity (82.4)")
print(f"5. Both metrics are important for different applications:")
print(f"   - High ACTIVITY → Fast catalytic turnover (industrial)")
print(f"   - High AFFINITY → Strong substrate binding (processivity)")
print(f"\n⭐ BEST OVERALL: Enzymes in top 5 of both rankings")
print(f"   - 2W39: Static #4, Activity #3 (87.3/100)")
print(f"   - Other top candidates show complementary strengths")
print("="*100)
