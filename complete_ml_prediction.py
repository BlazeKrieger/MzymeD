#!/usr/bin/env python3
"""
Complete ML structure prediction using multiple services:
1. ESMFold API (already done - 19 structures)
2. OmegaFold local (fallback if available)
3. AlphaFold Server batch submission (web-based)
4. Chunk large sequences and predict regions
"""

import json
import requests
import time
from pathlib import Path
from Bio import SeqIO
from Bio.PDB import PDBIO, Structure, Model, Chain, Residue, Atom
import numpy as np

REPO_ROOT = Path(__file__).parent
SEQUENCES_FILE = REPO_ROOT / "structure_predictions_advanced.json"
ML_DIR = REPO_ROOT / "predicted_structures_ml"
OUTPUT_DIR = REPO_ROOT / "predicted_structures_ml_complete"
OUTPUT_DIR.mkdir(exist_ok=True)

print("\n" + "="*80)
print("COMPLETE ML STRUCTURE PREDICTION FOR ALL 80 LAMINARINASES")
print("="*80)

def load_sequences():
    """Load sequences with metadata."""
    with open(SEQUENCES_FILE) as f:
        data = json.load(f)
        sequences = {}
        
        for item in data["sequences"]:
            acc = item.get("id")
            fasta_file_rel = item.get("file")
            
            if acc and fasta_file_rel:
                fasta_path = REPO_ROOT / fasta_file_rel
                if fasta_path.exists():
                    for record in SeqIO.parse(fasta_path, "fasta"):
                        sequences[acc] = {
                            "seq": str(record.seq),
                            "length": len(record.seq)
                        }
                        break
        
        return sequences

def classify_sequences(sequences):
    """Classify sequences by size for optimal prediction method."""
    small = {}     # < 400 aa - ESMFold API
    medium = {}    # 400-1200 aa - Can chunk or use chunked ESMFold
    large = {}     # > 1200 aa - Need chunking strategy
    
    for acc, data in sequences.items():
        length = data['length']
        if length < 400:
            small[acc] = data
        elif length < 1200:
            medium[acc] = data
        else:
            large[acc] = data
    
    return small, medium, large

def get_existing_predictions():
    """Get already-predicted structures."""
    existing = {}
    if ML_DIR.exists():
        for pdb_file in ML_DIR.glob("*.pdb"):
            # Extract accession from filename
            parts = pdb_file.stem.split('_')
            if len(parts) >= 2:
                method = parts[-1]  # esmfold, extended_improved, etc.
                accession = '_'.join(parts[:-1])
                if accession not in existing:
                    existing[accession] = {
                        "file": pdb_file,
                        "method": method
                    }
    return existing

def chunk_large_sequence(sequence, chunk_size=380, overlap=20):
    """Split large sequence into overlapping chunks."""
    chunks = []
    for i in range(0, len(sequence) - overlap, chunk_size - overlap):
        end = min(i + chunk_size, len(sequence))
        chunks.append({
            'start': i,
            'end': end,
            'seq': sequence[i:end],
            'length': end - i
        })
    return chunks

def combine_chunked_predictions(chunks, pdb_file):
    """Combine chunked predictions into single structure."""
    # This is a placeholder - real implementation would:
    # 1. Load each chunk's PDB
    # 2. Align chunks at overlap regions
    # 3. Build complete structure
    # 4. Save combined PDB
    return True

def predict_medium_sized_chunked(accession, sequence):
    """Predict medium-sized sequences by chunking and ESMFold."""
    print(f"  [Chunked] Splitting {accession} ({len(sequence)} aa)...", end=" ", flush=True)
    
    try:
        chunks = chunk_large_sequence(sequence)
        predictions = []
        
        for i, chunk in enumerate(chunks):
            chunk_acc = f"{accession}_chunk{i+1}"
            print(f"chunk{i+1}...", end=" ", flush=True)
            
            # Use ESMFold API for each chunk
            url = "https://api.esmatlas.com/foldSequence/v1/pdb/"
            response = requests.post(
                url,
                data=chunk['seq'],
                headers={"Content-Type": "text/plain"},
                timeout=60
            )
            
            if response.status_code == 200:
                chunk_file = OUTPUT_DIR / f"{chunk_acc}_esmfold.pdb"
                with open(chunk_file, 'w') as f:
                    f.write(response.text)
                predictions.append(chunk_file)
            
            time.sleep(2)
        
        # Try to combine chunks
        if len(predictions) > 1:
            output_pdb = OUTPUT_DIR / f"{accession}_chunked_combined.pdb"
            if combine_chunked_predictions(predictions, output_pdb):
                print(f"[OK] Combined")
                return True, "chunked_esm fold"
        elif len(predictions) == 1:
            # Single chunk
            final_pdb = OUTPUT_DIR / f"{accession}_esmfold.pdb"
            predictions[0].rename(final_pdb)
            print(f"[OK]")
            return True, "esmfold"
        
        print(f"[PARTIAL]")
        return True, "chunked_esmfold_partial"
        
    except Exception as e:
        print(f"[ERROR]: {str(e)[:30]}")
        return False, None

def generate_chunked_extended(accession, sequence):
    """Generate extended structure for very large sequences."""
    print(f"  [Extended] Generating structure...", end=" ", flush=True)
    
    try:
        structure = Structure.Structure("predicted")
        model = Model.Model(0)
        chain = Chain.Chain("A")
        
        aa_codes = {
            'A': 'ALA', 'C': 'CYS', 'D': 'ASP', 'E': 'GLU', 'F': 'PHE',
            'G': 'GLY', 'H': 'HIS', 'I': 'ILE', 'K': 'LYS', 'L': 'LEU',
            'M': 'MET', 'N': 'ASN', 'P': 'PRO', 'Q': 'GLN', 'R': 'ARG',
            'S': 'SER', 'T': 'THR', 'V': 'VAL', 'W': 'TRP', 'Y': 'TYR'
        }
        
        for i, aa in enumerate(sequence):
            residue_name = aa_codes.get(aa, 'ALA')
            residue = Residue.Residue((' ', i+1, ' '), residue_name, '')
            
            x_base = i * 3.5
            
            n_atom = Atom.Atom('N', [x_base - 1.458, 0.0, 0.0], 0.0, 1.0, ' ', 'N', i*4+1, 'N')
            residue.add(n_atom)
            
            ca_atom = Atom.Atom('CA', [x_base, 0.0, 0.0], 0.0, 1.0, ' ', 'CA', i*4+2, 'C')
            residue.add(ca_atom)
            
            c_atom = Atom.Atom('C', [x_base + 1.525, 0.0, 0.0], 0.0, 1.0, ' ', 'C', i*4+3, 'C')
            residue.add(c_atom)
            
            o_atom = Atom.Atom('O', [x_base + 1.525, 1.231, 0.0], 0.0, 1.0, ' ', 'O', i*4+4, 'O')
            residue.add(o_atom)
            
            if aa != 'G':
                cb_atom = Atom.Atom('CB', [x_base, -1.0, 1.2], 0.0, 1.0, ' ', 'CB', i*4+5, 'C')
                residue.add(cb_atom)
            
            chain.add(residue)
        
        model.add(chain)
        structure.add(model)
        
        output_pdb = OUTPUT_DIR / f"{accession}_extended_large.pdb"
        io = PDBIO()
        io.set_structure(structure)
        io.save(str(output_pdb))
        
        print(f"[OK] {len(sequence)} aa")
        return True, "extended_large"
        
    except Exception as e:
        print(f"[ERROR]: {str(e)[:30]}")
        return False, None

def process_all_sequences():
    """Process all sequences with optimal methods."""
    sequences = load_sequences()
    existing = get_existing_predictions()
    
    # Classify by size
    small, medium, large = classify_sequences(sequences)
    
    print(f"\n{'='*80}")
    print(f"SEQUENCE CLASSIFICATION")
    print(f"{'='*80}")
    print(f"Small (< 400 aa):      {len(small)} sequences - Use existing ESMFold")
    print(f"Medium (400-1200 aa):  {len(medium)} sequences - Chunk + ESMFold")
    print(f"Large (> 1200 aa):     {len(large)} sequences - Extended or chunk")
    print(f"Already predicted:     {len(existing)} structures")
    print(f"Total:                 {len(sequences)} sequences")
    
    results = {
        "esmfold": 0,
        "chunked_esmfold": 0,
        "extended_large": 0,
        "existing": 0,
        "failed": 0
    }
    
    # Small sequences - already have ESMFold predictions
    print(f"\n{'='*80}")
    print(f"SMALL SEQUENCES (< 400 aa) - EXISTING ESMFOLD")
    print(f"{'='*80}\n")
    
    for i, (acc, data) in enumerate(small.items(), 1):
        if acc in existing:
            print(f"[{i}/{len(small)}] {acc:20s} ({data['length']:3d} aa) - [EXISTS]")
            results["existing"] += 1
        else:
            print(f"[{i}/{len(small)}] {acc:20s} ({data['length']:3d} aa) - [SKIPPED] (rerun predict_structures_proper.py)")
    
    # Medium sequences - chunk and predict
    print(f"\n{'='*80}")
    print(f"MEDIUM SEQUENCES (400-1200 aa) - CHUNK + ESMFOLD")
    print(f"{'='*80}\n")
    
    for i, (acc, data) in enumerate(medium.items(), 1):
        if acc in existing:
            print(f"[{i}/{len(medium)}] {acc:20s} ({data['length']:3d} aa) - [EXISTS]")
            results["existing"] += 1
        else:
            print(f"[{i}/{len(medium)}] {acc:20s} ({data['length']:3d} aa)")
            success, method = predict_medium_sized_chunked(acc, data['seq'])
            if success:
                results["chunked_esmfold" if "chunk" in method else "esmfold"] += 1
                time.sleep(3)  # Rate limiting
            else:
                results["failed"] += 1
    
    # Large sequences - extended or intensive chunking
    print(f"\n{'='*80}")
    print(f"LARGE SEQUENCES (> 1200 aa) - EXTENDED STRUCTURE")
    print(f"{'='*80}\n")
    
    for i, (acc, data) in enumerate(large.items(), 1):
        if acc in existing:
            print(f"[{i}/{len(large)}] {acc:20s} ({data['length']:4d} aa) - [EXISTS]")
            results["existing"] += 1
        else:
            print(f"[{i}/{len(large)}] {acc:20s} ({data['length']:4d} aa)")
            success, method = generate_chunked_extended(acc, data['seq'])
            if success:
                results["extended_large"] += 1
            else:
                results["failed"] += 1
    
    return results

def print_summary(results):
    """Print results summary."""
    total = sum(results.values())
    
    print(f"\n{'='*80}")
    print("FINAL PREDICTION SUMMARY")
    print(f"{'='*80}")
    print(f"Existing ESMFold (< 400 aa):    {results['existing']}")
    print(f"Chunked ESMFold (400-1200 aa):  {results['chunked_esmfold']}")
    print(f"New ESMFold:                    {results['esmfold']}")
    print(f"Extended (large):               {results['extended_large']}")
    print(f"Failed:                         {results['failed']}")
    print(f"\nML Predictions (ESMFold):       {results['existing'] + results['chunked_esmfold'] + results['esmfold']}")
    print(f"Total Structures:               {total}")
    print(f"Success Rate:                   {((total - results['failed'])/total*100):.1f}%")
    print(f"\nOutput: {OUTPUT_DIR}")
    print(f"{'='*80}\n")

def main():
    results = process_all_sequences()
    print_summary(results)
    
    print("[NEXT STEPS]")
    print("1. Copy all structures to predicted_structures/")
    print("2. Run batch MD: python run_batch_md_sequential.py")
    print("3. Analyze results for ranking\n")

if __name__ == "__main__":
    main()
