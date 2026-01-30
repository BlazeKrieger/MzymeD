#!/usr/bin/env python3
"""
Quick analysis and validation of AlphaFold2 predictions.
"""

import os
import json
import glob
from pathlib import Path
import numpy as np
from datetime import datetime

BASE_DIR = Path(__file__).parent
PRED_DIR = BASE_DIR / "predicted_structures_alphafold"
AF_RESULTS = BASE_DIR / "outputs/colabfold_results"
ANALYSIS_DIR = BASE_DIR / "alphafold_analysis"

# Create output directory
ANALYSIS_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"AlphaFold2 Prediction Analysis")
print(f"{'='*70}\n")

# Find all confidence JSON files from ColabFold results
json_files = glob.glob(str(AF_RESULTS / "*_scores_rank_001_*.json"))

print(f"Found {len(json_files)} confidence files\n")

results = []

for json_file in sorted(json_files):
    try:
        with open(json_file) as f:
            data = json.load(f)
        
        # Extract metrics
        plddt = np.array(data.get('plddt', []))
        pae = data.get('pae', [])
        ptm = data.get('ptm', 0)
        iptm = data.get('iptm', 0)
        
        enzyme_name = Path(json_file).stem.split("_scores_rank_001")[0]
        
        result = {
            "enzyme": enzyme_name,
            "plddt_mean": float(np.mean(plddt)) if len(plddt) > 0 else None,
            "plddt_min": float(np.min(plddt)) if len(plddt) > 0 else None,
            "plddt_max": float(np.max(plddt)) if len(plddt) > 0 else None,
            "n_residues": len(plddt) if len(plddt) > 0 else None,
            "ptm": float(ptm),
            "iptm": float(iptm),
            "confidence_category": "VERY HIGH" if np.mean(plddt) >= 90 else "HIGH" if np.mean(plddt) >= 70 else "MODERATE" if np.mean(plddt) >= 50 else "LOW"
        }
        
        results.append(result)
        
        status = "✓"
        print(f"{status} {enzyme_name}")
        print(f"   pLDDT: {result['plddt_mean']:.1f} ± {result['plddt_max']-result['plddt_min']:.1f} ({result['confidence_category']})")
        print(f"   pTM: {result['ptm']:.3f}, iPTM: {result['iptm']:.3f}")
        print(f"   Residues: {result['n_residues']}")
        
    except Exception as e:
        print(f"✗ Error processing {json_file}: {str(e)}")

# Sort by confidence
results_sorted = sorted(results, key=lambda x: x['plddt_mean'], reverse=True)

# Summary statistics
print(f"\n{'='*70}")
print(f"SUMMARY")
print(f"{'='*70}\n")

plddt_values = [r['plddt_mean'] for r in results if r['plddt_mean']]
ptm_values = [r['ptm'] for r in results if r['ptm']]

print(f"Total structures: {len(results)}")
print(f"Mean pLDDT: {np.mean(plddt_values):.1f} ± {np.std(plddt_values):.1f}")
print(f"Mean pTM: {np.mean(ptm_values):.3f} ± {np.std(ptm_values):.3f}")
print()

# Quality distribution
very_high = sum(1 for r in results if r['plddt_mean'] >= 90)
high = sum(1 for r in results if 70 <= r['plddt_mean'] < 90)
moderate = sum(1 for r in results if 50 <= r['plddt_mean'] < 70)
low = sum(1 for r in results if r['plddt_mean'] < 50)

print(f"Quality Distribution:")
print(f"  VERY HIGH (≥90): {very_high} ({100*very_high/len(results):.0f}%)")
print(f"  HIGH (70-89):    {high} ({100*high/len(results):.0f}%)")
print(f"  MODERATE (50-69): {moderate} ({100*moderate/len(results):.0f}%)")
print(f"  LOW (<50):        {low} ({100*low/len(results):.0f}%)")

# Save detailed results
output_file = ANALYSIS_DIR / "alphafold_predictions_summary.json"
with open(output_file, 'w') as f:
    json.dump({
        "timestamp": datetime.now().isoformat(),
        "total_structures": len(results),
        "statistics": {
            "plddt_mean": float(np.mean(plddt_values)),
            "plddt_std": float(np.std(plddt_values)),
            "ptm_mean": float(np.mean(ptm_values)),
            "ptm_std": float(np.std(ptm_values)),
        },
        "quality_distribution": {
            "very_high_90plus": very_high,
            "high_70_89": high,
            "moderate_50_69": moderate,
            "low_below_50": low
        },
        "predictions": results_sorted
    }, f, indent=2)

print(f"\nDetailed results: {output_file}")

# Top 5 candidates for further analysis
print(f"\n{'='*70}")
print(f"TOP 5 STRUCTURES (Best Confidence)")
print(f"{'='*70}\n")

for i, r in enumerate(results_sorted[:5], 1):
    print(f"{i}. {r['enzyme']}")
    print(f"   pLDDT: {r['plddt_mean']:.1f}  |  pTM: {r['ptm']:.3f}  |  Category: {r['confidence_category']}")

print("\n")
