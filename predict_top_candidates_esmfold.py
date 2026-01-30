#!/usr/bin/env python3
"""
Step 2: Generate real 3D structures using ESMFold for top 15 candidates.
This uses the actual ESMFold model from Meta AI for accurate structure prediction.
"""

import json
import torch
from pathlib import Path
from Bio import SeqIO
import time

# Try to import ESMFold
try:
    import esm
    ESMFOLD_AVAILABLE = True
    print("✓ ESMFold successfully imported")
except ImportError:
    ESMFOLD_AVAILABLE = False
    print("✗ ESMFold not available - install with: pip install fair-esm")

PREDICTIONS_JSON = Path("predicted_activity_analysis/predicted_activity_assessment.json")
LAMINARINASES_DIR = Path("laminarinases")
OUTPUT_DIR = Path("esmfold_structures")
OUTPUT_DIR.mkdir(exist_ok=True)

# Top 15 candidates from analysis
TOP_CANDIDATES = [
    "ACU35625.1",  # 95.3 - GH55
    "AOR29491.1",  # 94.6 - GH17
    "BAF52916.1",  # 94.3 - GH3
    "CAB01407.1",  # 94.2 - GH3
    "ADU06434.1",  # 94.2 - GH55
    "AAD35118.1",  # 93.7 - Mixed
    "CCK26176.1",  # 93.7 - GH55
    "AEN12197.1",  # 93.7 - GH55
    "ABQ46917.1",  # 93.6 - GH16
    "AGJ57089.1",  # 93.6 - GH55
    "CDF79586.1",  # 92.2 - GH16
    "CAL68405.1",  # 91.8 - GH16
    "UYI35443.1",  # 92.0 - GH55
    "ALP73406.1",  # 92.6 - GH16
    "ABJ15796.1",  # 93.5 - GH16
]

def find_fasta_for_id(protein_id):
    """Find the FASTA file containing this protein ID."""
    for fasta_file in LAMINARINASES_DIR.rglob("*.fasta"):
        for record in SeqIO.parse(str(fasta_file), "fasta"):
            if protein_id in record.id:
                return fasta_file, str(record.seq)
    return None, None

def predict_with_esmfold(sequence, protein_id, output_pdb):
    """Use ESMFold to predict structure."""
    if not ESMFOLD_AVAILABLE:
        print(f"  ✗ ESMFold not available for {protein_id}")
        return False
    
    try:
        print(f"  Loading ESMFold model...")
        model = esm.pretrained.esmfold_v1()
        model = model.eval()
        
        # Use GPU if available
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        model = model.to(device)
        print(f"  Using device: {device}")
        
        print(f"  Running prediction for {len(sequence)} residues...")
        start_time = time.time()
        
        with torch.no_grad():
            output = model.infer_pdb(sequence)
        
        elapsed = time.time() - start_time
        
        # Save PDB
        with open(output_pdb, 'w') as f:
            f.write(output)
        
        print(f"  ✓ Prediction complete in {elapsed:.1f}s")
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False

def main():
    print("\n" + "="*80)
    print("STEP 2: REAL STRUCTURE PREDICTION USING ESMFold")
    print("="*80)
    print(f"\nPredicting structures for top {len(TOP_CANDIDATES)} candidates")
    print(f"Output directory: {OUTPUT_DIR}/\n")
    
    if not ESMFOLD_AVAILABLE:
        print("\n" + "="*80)
        print("ERROR: ESMFold not installed")
        print("="*80)
        print("\nInstall with:")
        print("  conda run -n mzymed pip install fair-esm")
        print("\nOr use the simpler installation:")
        print("  pip install 'esm @ git+https://github.com/facebookresearch/esm.git'")
        return
    
    results = {
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'model': 'ESMFold v1',
        'predictions': []
    }
    
    successful = 0
    failed = 0
    
    for i, protein_id in enumerate(TOP_CANDIDATES, 1):
        print(f"\n[{i}/{len(TOP_CANDIDATES)}] {protein_id}")
        print("-" * 80)
        
        # Find FASTA file
        fasta_file, sequence = find_fasta_for_id(protein_id)
        
        if not fasta_file:
            print(f"  ✗ FASTA file not found")
            failed += 1
            continue
        
        print(f"  Source: {fasta_file.relative_to(LAMINARINASES_DIR)}")
        print(f"  Length: {len(sequence)} residues")
        
        # Output PDB path
        output_pdb = OUTPUT_DIR / f"{protein_id}_esmfold.pdb"
        
        # Check if already predicted
        if output_pdb.exists():
            print(f"  ⚠ Structure already exists, skipping")
            successful += 1
            results['predictions'].append({
                'id': protein_id,
                'length': len(sequence),
                'pdb_file': str(output_pdb),
                'status': 'already_exists',
                'source': str(fasta_file.relative_to(LAMINARINASES_DIR))
            })
            continue
        
        # Predict structure
        success = predict_with_esmfold(sequence, protein_id, output_pdb)
        
        if success:
            successful += 1
            results['predictions'].append({
                'id': protein_id,
                'length': len(sequence),
                'pdb_file': str(output_pdb),
                'status': 'predicted',
                'source': str(fasta_file.relative_to(LAMINARINASES_DIR))
            })
        else:
            failed += 1
            results['predictions'].append({
                'id': protein_id,
                'length': len(sequence),
                'pdb_file': str(output_pdb),
                'status': 'failed',
                'source': str(fasta_file.relative_to(LAMINARINASES_DIR))
            })
    
    # Save results
    results['summary'] = {
        'total': len(TOP_CANDIDATES),
        'successful': successful,
        'failed': failed
    }
    
    output_json = OUTPUT_DIR / "esmfold_predictions.json"
    with open(output_json, 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*80)
    print("PREDICTION SUMMARY")
    print("="*80)
    print(f"Total candidates: {len(TOP_CANDIDATES)}")
    print(f"Successful:       {successful}")
    print(f"Failed:           {failed}")
    print(f"\nOutput: {OUTPUT_DIR}/")
    print(f"Log: {output_json}")
    print("="*80)

if __name__ == "__main__":
    main()
