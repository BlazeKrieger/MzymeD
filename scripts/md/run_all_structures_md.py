#!/usr/bin/env python3
"""
Batch MD simulation runner for all laminarinase structures (known + predicted).
Runs GPU-accelerated 100 ps MD for all 85 structures and generates ranking report.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from collections import defaultdict
import glob

# Base paths
BASE_DIR = Path(__file__).parent
REAL_STRUCTURES = BASE_DIR / "real_structures"
PREDICTED_STRUCTURES = BASE_DIR / "predicted_structures"
ANALYSIS_DIR = BASE_DIR / "analysis_results"
OUTPUT_DIR = BASE_DIR / "batch_md_results"

# Create output directory
OUTPUT_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

def extract_pdb_id(filename):
    """Extract PDB ID from filename (first 4 chars if known structure, otherwise accession ID)."""
    name = Path(filename).stem
    filename_str = str(filename)
    if "_predicted" in name:
        return name.replace("_predicted", "")
    return name

def run_md_simulation(pdb_file, pdb_id, steps=50000):
    """Run MD simulation for a single structure."""
    try:
        cmd = [
            sys.executable,
            str(BASE_DIR / "run_glucan_complex_md.py"),
            "--pdb", pdb_id,
            "--steps", str(steps),
            "--report-interval", "1000"
        ]
        
        print(f"\n{'='*70}")
        print(f"Running MD: {pdb_id}")
        print(f"Steps: {steps} (100 ps)")
        print(f"{'='*70}")
        
        result = subprocess.run(cmd, capture_output=False, text=True)
        
        if result.returncode == 0:
            print(f"✓ SUCCESS: {pdb_id}")
            return True
        else:
            print(f"✗ FAILED: {pdb_id}")
            return False
    except Exception as e:
        print(f"✗ ERROR ({pdb_id}): {str(e)}")
        return False

def load_rmsd_data(pdb_id):
    """Load RMSD data from analysis results."""
    rmsd_file = ANALYSIS_DIR / f"glucan_complex_{pdb_id}_rmsd.json"
    if rmsd_file.exists():
        try:
            with open(rmsd_file) as f:
                return json.load(f)
        except:
            return None
    return None

def is_known_structure(pdb_id):
    """Check if this is a known structure (PDB ID)."""
    return len(pdb_id) == 4 and pdb_id[0].isdigit()

def main():
    """Main batch runner."""
    
    # Collect all structures
    known_pdb_ids = [f.stem for f in REAL_STRUCTURES.glob("*.pdb")]
    predicted_ids = [extract_pdb_id(f) for f in PREDICTED_STRUCTURES.glob("*.pdb")]
    
    all_ids = sorted(known_pdb_ids) + sorted(predicted_ids)
    
    print(f"\n{'='*70}")
    print(f"BATCH MD SIMULATION FOR ALL LAMINARINASE STRUCTURES")
    print(f"{'='*70}")
    print(f"Known structures:    {len(known_pdb_ids)}")
    print(f"Predicted structures: {len(predicted_ids)}")
    print(f"Total:              {len(all_ids)}")
    print(f"GPU platform:       CUDA (with OpenCL/CPU fallback)")
    print(f"Per-structure time: ~100 ps (50,000 steps × 2 fs)")
    print(f"Estimated total:    {len(all_ids) * 10 // 60} - {len(all_ids) * 20 // 60} hours")
    print(f"{'='*70}\n")
    
    # Run simulations
    results = {
        "known": {},
        "predicted": {},
        "summary": {}
    }
    
    success_count = 0
    fail_count = 0
    
    for i, pdb_id in enumerate(all_ids, 1):
        print(f"\n[{i}/{len(all_ids)}]", end=" ")
        
        success = run_md_simulation(None, pdb_id, steps=50000)
        
        # Load results
        rmsd_data = load_rmsd_data(pdb_id)
        
        if is_known_structure(pdb_id):
            results["known"][pdb_id] = {
                "success": success,
                "rmsd_data": rmsd_data
            }
        else:
            results["predicted"][pdb_id] = {
                "success": success,
                "rmsd_data": rmsd_data
            }
        
        if success:
            success_count += 1
        else:
            fail_count += 1
    
    # Summary
    results["summary"] = {
        "total_structures": len(all_ids),
        "known_structures": len(known_pdb_ids),
        "predicted_structures": len(predicted_ids),
        "successful_simulations": success_count,
        "failed_simulations": fail_count,
        "success_rate": f"{100*success_count/len(all_ids):.1f}%"
    }
    
    # Save results
    results_file = OUTPUT_DIR / "batch_md_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print("BATCH SIMULATION COMPLETE")
    print(f"{'='*70}")
    print(f"Results saved to: {results_file}")
    print(f"Successful: {success_count}/{len(all_ids)}")
    print(f"Success rate: {100*success_count/len(all_ids):.1f}%")
    print(f"{'='*70}\n")
    
    return results

if __name__ == "__main__":
    main()
