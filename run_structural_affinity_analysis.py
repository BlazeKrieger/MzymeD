#!/usr/bin/env python3
"""
Enzyme affinity prediction based on structural analysis.
Avoids force field issues by analyzing raw AlphaFold predictions.
"""

import glob
import json
from pathlib import Path
import numpy as np
from collections import defaultdict
import warnings

warnings.filterwarnings('ignore')

try:
    from Bio.PDB import PDBParser
    import pandas as pd
except ImportError:
    print("ERROR: BioPython required")
    exit(1)

BASE_DIR = Path(__file__).parent
CLEAN_DIR = BASE_DIR / "predicted_structures_cleaned"
PRED_DIR = BASE_DIR / "predicted_structures_alphafold"
ANALYSIS_DIR = BASE_DIR / "alphafold_enzyme_affinity"

ANALYSIS_DIR.mkdir(exist_ok=True)

print(f"\n{'='*70}")
print(f"Structural Stability Analysis for Affinity Prediction")
print(f"{'='*70}\n")

def calculate_pairwise_distances(ca_coords):
    """Calculate CA-CA distances for stability analysis."""
    distances = []
    for i in range(len(ca_coords) - 1):
        d = np.linalg.norm(ca_coords[i+1] - ca_coords[i])
        distances.append(d)
    return np.array(distances)

def extract_confidence_from_json(pdb_name):
    """Extract confidence metrics from AlphaFold JSON output if available."""
    search_name = pdb_name.split('_unrelaxed')[0]  # Get base name
    
    for json_file in glob.glob(str(PRED_DIR / f"*{search_name}*_scores_*.json")):
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
                if 'plddt' in data:
                    plddt = np.mean(data['plddt'])
                    return float(plddt)
        except:
            pass
    return 80.0  # Default if not found

def calculate_active_site_flexibility(ca_coords, n_residues):
    """Estimate active site flexibility from backbone geometry."""
    # Active site typically in middle ~40% of structure
    start = max(0, n_residues // 4)
    end = min(n_residues, n_residues * 3 // 4)
    
    if start >= end:
        return 0.0
    
    # Use variance in CA-CA distances in this region as flexibility proxy
    active_site_coords = ca_coords[start:end]
    distances = calculate_pairwise_distances(active_site_coords)
    
    if len(distances) > 0:
        # Low std = rigid backbone, high std = flexible
        flexibility = float(np.std(distances))
    else:
        flexibility = 0.0
    
    return flexibility

# Load cleaned PDB files
pdb_files = sorted(glob.glob(str(CLEAN_DIR / "*_clean.pdb")))
print(f"Found: {len(pdb_files)} cleaned PDB files\n")

parser = PDBParser(QUIET=True)
affinity_results = {}

for idx, pdb_file in enumerate(pdb_files, 1):
    pdb_name = Path(pdb_file).stem.replace('_clean', '')
    enzyme_name = pdb_name.split('_')[0]
    
    try:
        # Parse PDB
        structure = parser.get_structure('enzyme', str(pdb_file))
        model = structure[0]
        
        # Extract CA coordinates
        ca_coords = []
        n_residues = 0
        for chain in model:
            for residue in chain:
                n_residues += 1
                if 'CA' in residue:
                    ca_coords.append(residue['CA'].get_coord())
        
        ca_coords = np.array(ca_coords)
        
        if len(ca_coords) < 10:
            print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> ERROR: Too few residues ({len(ca_coords)})")
            continue
        
        # Calculate structural metrics
        ca_distances = calculate_pairwise_distances(ca_coords)
        dist_mean = np.mean(ca_distances)
        dist_std = np.std(ca_distances)
        
        # Backbone regularity: lower std = more regular/stable
        regularity = 1.0 / (1.0 + dist_std / 3.8)  # Expected CA-CA ~3.8 Å
        
        # Active site flexibility
        active_site_flex = calculate_active_site_flexibility(ca_coords, n_residues)
        
        # Get confidence score from original AlphaFold predictions
        plddt = extract_confidence_from_json(pdb_name)
        
        # Affinity scoring:
        # - Higher pLDDT = more reliable structure
        # - Higher regularity = more stable protein
        # - Moderate flexibility = better binding (too rigid might not accommodate substrate)
        
        confidence_score = plddt / 100.0  # 0-1
        
        # Optimal flexibility: not too rigid, not too flexible
        # Peak around 0.1-0.15 Å std in active site
        flexibility_score = 1.0 - abs((active_site_flex - 0.12) / 0.12) if active_site_flex > 0 else 0.5
        flexibility_score = max(0, min(1, flexibility_score))
        
        # Combined affinity proxy: confidence + stability + reasonable flexibility
        affinity_score = (confidence_score * 0.5 + regularity * 0.3 + flexibility_score * 0.2)
        
        affinity_results[enzyme_name] = {
            'pdb': pdb_name,
            'n_residues': int(n_residues),
            'plddt_confidence': float(plddt),
            'backbone_regularity': float(regularity),
            'active_site_flexibility_angstrom': float(active_site_flex),
            'flexibility_score': float(flexibility_score),
            'affinity_proxy_score': float(affinity_score)
        }
        
        print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> Affinity: {affinity_score:.4f}")
        
    except Exception as e:
        print(f"[{idx}/{len(pdb_files)}] {enzyme_name:25s} -> ERROR: {str(e)[:40]}")

# Rank by affinity
ranked = sorted(affinity_results.items(), key=lambda x: x[1]['affinity_proxy_score'], reverse=True)

# Save results
output_json = ANALYSIS_DIR / "affinity_scores.json"
with open(output_json, 'w') as f:
    json.dump(dict(ranked), f, indent=2)

print(f"\n{'='*70}")
print(f"Top 5 Enzymes by Predicted Affinity:")
print(f"{'='*70}")
for i, (name, scores) in enumerate(ranked[:5], 1):
    print(f"{i}. {name:30s} Score: {scores['affinity_proxy_score']:.4f}")
    print(f"   - pLDDT Confidence: {scores['plddt_confidence']:.1f}")
    print(f"   - Backbone Regularity: {scores['backbone_regularity']:.4f}")
    print(f"   - Flexibility Score: {scores['flexibility_score']:.4f}\n")

print(f"✓ Results saved to: {output_json}")
