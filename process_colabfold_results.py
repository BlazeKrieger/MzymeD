#!/usr/bin/env python3
"""
Process ColabFold results after downloading from Google Colab
Organizes PDB files and generates summary report
"""

import os
import json
import shutil
import glob
from pathlib import Path

def process_colabfold_results():
    """Process downloaded ColabFold predictions"""
    
    print("=" * 80)
    print("PROCESSING COLABFOLD RESULTS")
    print("=" * 80)
    
    # Check for results
    result_dirs = [
        "laminarinases_batch",  # Default name
        "laminarinases_batch_results",
        "colabfold_results"
    ]
    
    results_dir = None
    for d in result_dirs:
        if os.path.exists(d):
            results_dir = d
            break
    
    if not results_dir:
        print("\n❌ No ColabFold results directory found!")
        print("Expected directories:")
        for d in result_dirs:
            print(f"  - {d}/")
        print("\nPlease extract the downloaded ZIP file first.")
        return
    
    print(f"✅ Found results in: {results_dir}/")
    
    # Create output directory
    output_dir = "predicted_structures_alphafold"
    os.makedirs(output_dir, exist_ok=True)
    print(f"✅ Output directory: {output_dir}/")
    
    # Find all PDB files (rank 1 only - best model)
    pdb_pattern = os.path.join(results_dir, "*_rank_001_*.pdb")
    pdb_files = glob.glob(pdb_pattern)
    
    if not pdb_files:
        # Try alternative pattern
        pdb_pattern = os.path.join(results_dir, "*.pdb")
        pdb_files = glob.glob(pdb_pattern)
    
    print(f"\n📁 Found {len(pdb_files)} PDB files")
    
    # Find JSON confidence files
    json_pattern = os.path.join(results_dir, "*.json")
    json_files = glob.glob(json_pattern)
    print(f"📁 Found {len(json_files)} confidence files")
    
    # Process each PDB file
    print("\n" + "=" * 80)
    print("COPYING STRUCTURES")
    print("=" * 80)
    
    predictions = []
    
    for pdb_file in sorted(pdb_files):
        basename = os.path.basename(pdb_file)
        
        # Extract accession (remove model/rank suffixes)
        accession = basename.split('_')[0]
        
        # New filename: accession_alphafold.pdb
        new_name = f"{accession}_alphafold.pdb"
        dest_path = os.path.join(output_dir, new_name)
        
        # Copy file
        shutil.copy2(pdb_file, dest_path)
        
        # Load confidence if available
        json_file = pdb_file.replace('.pdb', '.json')
        plddt = None
        if os.path.exists(json_file):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                    plddt = data.get('plddt', data.get('mean_plddt'))
            except:
                pass
        
        # Get sequence length from PDB
        length = 0
        with open(pdb_file) as f:
            for line in f:
                if line.startswith('ATOM') and line[12:16].strip() == 'CA':
                    length += 1
        
        predictions.append({
            'accession': accession,
            'filename': new_name,
            'length': length,
            'plddt': plddt,
            'source': basename
        })
        
        status = f"pLDDT: {plddt:.2f}" if plddt else "no confidence"
        print(f"  {accession:20s} → {new_name:35s} ({length:4d} aa, {status})")
    
    # Generate summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total structures:    {len(predictions)}")
    print(f"Output directory:    {output_dir}/")
    
    if predictions:
        lengths = [p['length'] for p in predictions]
        print(f"Size range:          {min(lengths)} - {max(lengths)} aa")
        
        plddt_scores = [p['plddt'] for p in predictions if p['plddt'] is not None]
        if plddt_scores:
            print(f"pLDDT range:         {min(plddt_scores):.2f} - {max(plddt_scores):.2f}")
            print(f"Mean pLDDT:          {sum(plddt_scores)/len(plddt_scores):.2f}")
            
            # Quality assessment
            high_quality = sum(1 for s in plddt_scores if s > 90)
            good_quality = sum(1 for s in plddt_scores if 70 <= s <= 90)
            low_quality = sum(1 for s in plddt_scores if s < 70)
            
            print(f"\nQuality distribution:")
            print(f"  High (>90):        {high_quality} structures")
            print(f"  Good (70-90):      {good_quality} structures")
            print(f"  Low (<70):         {low_quality} structures")
    
    # Save summary JSON
    summary_file = "alphafold_predictions_summary.json"
    summary = {
        'total': len(predictions),
        'output_directory': output_dir,
        'predictions': predictions
    }
    
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"\n✅ Summary saved: {summary_file}")
    
    # Show top 10 by confidence
    if plddt_scores:
        print("\n" + "=" * 80)
        print("TOP 10 PREDICTIONS BY CONFIDENCE")
        print("=" * 80)
        
        sorted_predictions = sorted(predictions, 
                                   key=lambda x: x['plddt'] if x['plddt'] else 0, 
                                   reverse=True)
        
        for i, pred in enumerate(sorted_predictions[:10], 1):
            plddt_str = f"{pred['plddt']:.2f}" if pred['plddt'] else "N/A"
            print(f"{i:2d}. {pred['accession']:20s} {pred['length']:4d} aa  pLDDT: {plddt_str}")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Check structures in predicted_structures_alphafold/")
    print("2. Combine with existing ESMFold predictions (19 structures)")
    print("3. Run batch MD on all 84 structures (4 known + 80 predicted)")
    print("   Command: python run_batch_md_sequential.py")
    print("=" * 80)

if __name__ == "__main__":
    process_colabfold_results()
