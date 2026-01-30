#!/usr/bin/env python3
"""
Sequential batch MD runner for all 85 laminarinase structures (4 known + 81 predicted).
Runs GPU-accelerated 100 ps MD with comprehensive tracking.
"""

import os
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import time

# Base paths
BASE_DIR = Path(__file__).parent
REAL_STRUCTURES = BASE_DIR / "real_structures"
PREDICTED_STRUCTURES = BASE_DIR / "predicted_structures"
ANALYSIS_DIR = BASE_DIR / "analysis_results"
OUTPUT_DIR = BASE_DIR / "batch_md_results"

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)

def extract_pdb_id(filename):
    """Extract PDB ID from filename."""
    name = Path(filename).stem
    if "_predicted" in name:
        return name.replace("_predicted", "")
    return name

def run_md_simulation(pdb_id, is_predicted=False, steps=50000):
    """Run MD simulation for a single structure."""
    try:
        cmd = [
            sys.executable,
            str(BASE_DIR / "run_glucan_complex_md.py"),
            "--pdb", pdb_id,
            "--steps", str(steps),
            "--report-interval", "1000"
        ]
        
        start_time = time.time()
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
        elapsed = time.time() - start_time
        
        success = result.returncode == 0
        
        return {
            "success": success,
            "elapsed_seconds": elapsed,
            "returncode": result.returncode,
            "stdout": result.stdout[-500:] if result.stdout else "",  # Last 500 chars
            "stderr": result.stderr[-500:] if result.stderr else ""
        }
    except subprocess.TimeoutExpired:
        return {
            "success": False,
            "elapsed_seconds": 3600,
            "returncode": -1,
            "stdout": "",
            "stderr": "Timeout after 1 hour"
        }
    except Exception as e:
        return {
            "success": False,
            "elapsed_seconds": 0,
            "returncode": -1,
            "stdout": "",
            "stderr": str(e)
        }

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

def main():
    """Main batch runner."""
    
    # Collect all structures
    known_pdb_ids = sorted([f.stem for f in REAL_STRUCTURES.glob("*.pdb")])
    predicted_ids = sorted([extract_pdb_id(f) for f in PREDICTED_STRUCTURES.glob("*.pdb")])
    
    all_structures = []
    for pdb_id in known_pdb_ids:
        all_structures.append({"id": pdb_id, "type": "known"})
    for pred_id in predicted_ids:
        all_structures.append({"id": pred_id, "type": "predicted"})
    
    print(f"\n{'='*80}")
    print(f"BATCH MD SIMULATION FOR ALL LAMINARINASE STRUCTURES")
    print(f"{'='*80}")
    print(f"Known structures:      {len(known_pdb_ids)}")
    print(f"Predicted structures:  {len(predicted_ids)}")
    print(f"Total:                 {len(all_structures)}")
    print(f"Steps per structure:   50,000 (100 ps)")
    print(f"GPU platform:          CUDA (with OpenCL/CPU fallback)")
    print(f"Estimated time:        {len(all_structures) * 8 // 60} - {len(all_structures) * 15 // 60} hours")
    print(f"{'='*80}\n")
    
    # Results tracking
    results = {
        "metadata": {
            "start_time": datetime.now().isoformat(),
            "total_structures": len(all_structures),
            "known_structures": len(known_pdb_ids),
            "predicted_structures": len(predicted_ids)
        },
        "structures": {}
    }
    
    success_count = 0
    fail_count = 0
    total_time = 0
    
    # Run simulations
    for i, struct in enumerate(all_structures, 1):
        pdb_id = struct["id"]
        struct_type = struct["type"]
        
        # Print progress
        print(f"\n[{i:3d}/{len(all_structures)}] {pdb_id:20s} ({struct_type:10s})", end=" ... ", flush=True)
        
        # Run MD
        md_result = run_md_simulation(pdb_id, is_predicted=(struct_type=="predicted"), steps=50000)
        
        # Load RMSD if successful
        rmsd_data = load_rmsd_data(pdb_id) if md_result["success"] else None
        
        # Store result
        results["structures"][pdb_id] = {
            "type": struct_type,
            "md_result": md_result,
            "rmsd_data": rmsd_data,
            "index": i
        }
        
        # Update counters
        elapsed = md_result["elapsed_seconds"]
        total_time += elapsed
        
        if md_result["success"]:
            success_count += 1
            rmsd_str = f"RMSD: {rmsd_data['mean_rmsd_nm']:.4f} nm" if rmsd_data else ""
            print(f"[OK] SUCCESS ({elapsed:.1f}s) {rmsd_str}")
        else:
            fail_count += 1
            print(f"[FAIL] FAILED ({elapsed:.1f}s)")
            if md_result["stderr"]:
                print(f"   Error: {md_result['stderr'][:100]}")
    
    # Final summary
    results["metadata"]["end_time"] = datetime.now().isoformat()
    results["metadata"]["total_elapsed_seconds"] = total_time
    results["metadata"]["successful_simulations"] = success_count
    results["metadata"]["failed_simulations"] = fail_count
    results["metadata"]["success_rate"] = f"{100*success_count/len(all_structures):.1f}%"
    
    # Save results
    results_file = OUTPUT_DIR / "batch_md_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    # Print final summary
    print(f"\n{'='*80}")
    print("BATCH SIMULATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total structures:      {len(all_structures)}")
    print(f"Successful:            {success_count}")
    print(f"Failed:                {fail_count}")
    print(f"Success rate:          {100*success_count/len(all_structures):.1f}%")
    print(f"Total elapsed time:    {total_time/3600:.1f} hours")
    print(f"Avg time per struct:   {total_time/len(all_structures):.1f} seconds")
    print(f"\nResults saved to:      {results_file}")
    print(f"{'='*80}\n")
    
    return results

if __name__ == "__main__":
    main()
