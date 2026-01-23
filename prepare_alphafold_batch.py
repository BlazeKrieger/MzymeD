#!/usr/bin/env python3
"""
Prepare batch FASTA file for AlphaFold Server submission
Extracts all 80 predicted sequences and creates a single combined FASTA file
"""

import json
import os
from pathlib import Path
from Bio import SeqIO

def load_sequences_from_json():
    """Load sequence metadata from JSON"""
    json_file = "predicted_activity_analysis/predicted_activity_assessment.json"
    with open(json_file) as f:
        data = json.load(f)
    return data['activity_analysis']

def load_fasta_sequence(fasta_path):
    """Load sequence from FASTA file"""
    if not os.path.exists(fasta_path):
        print(f"  [WARNING] FASTA not found: {fasta_path}")
        return None
    
    records = list(SeqIO.parse(fasta_path, "fasta"))
    if not records:
        print(f"  [WARNING] No sequences in: {fasta_path}")
        return None
    
    # Return first record
    return str(records[0].seq)

def create_combined_fasta():
    """Create combined FASTA file with all 80 predicted sequences"""
    
    print("=" * 80)
    print("PREPARING ALPHAFOLD SERVER BATCH SUBMISSION FILE")
    print("=" * 80)
    
    # Load metadata
    sequences_data = load_sequences_from_json()
    print(f"\nLoaded {len(sequences_data)} sequences from JSON")
    
    # Output file
    output_fasta = "laminarinases_all_80_sequences.fasta"
    output_medium_large = "laminarinases_medium_large_61.fasta"
    
    # Track statistics
    small_count = 0
    medium_count = 0
    large_count = 0
    total_written = 0
    medium_large_written = 0
    
    # Create combined FASTA
    with open(output_fasta, 'w') as f_all, open(output_medium_large, 'w') as f_ml:
        for i, seq_data in enumerate(sequences_data, 1):
            accession = seq_data['id']
            length = seq_data['sequence_length']
            activity = seq_data['activity_score']
            source = seq_data['source']
            
            # Load sequence from FASTA file
            sequence = load_fasta_sequence(source)
            if sequence is None:
                print(f"[{i}/{len(sequences_data)}] {accession} - SKIPPED (no sequence)")
                continue
            
            # Write to combined file
            header = f">{accession} | {length} aa | Activity: {activity:.1f} | {source}"
            f_all.write(f"{header}\n")
            f_all.write(f"{sequence}\n\n")
            total_written += 1
            
            # Classify by size
            if length < 400:
                small_count += 1
                status = "SMALL (ESMFold already exists)"
            elif length < 1200:
                medium_count += 1
                status = "MEDIUM (AlphaFold recommended)"
                # Write to medium/large file
                f_ml.write(f"{header}\n")
                f_ml.write(f"{sequence}\n\n")
                medium_large_written += 1
            else:
                large_count += 1
                status = "LARGE (AlphaFold recommended)"
                # Write to medium/large file
                f_ml.write(f"{header}\n")
                f_ml.write(f"{sequence}\n\n")
                medium_large_written += 1
            
            print(f"[{i}/{len(sequences_data)}] {accession:20s} {length:4d} aa - {status}")
    
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total sequences processed:     {total_written}")
    print(f"  Small (< 400 aa):            {small_count} - Use existing ESMFold")
    print(f"  Medium (400-1200 aa):        {medium_count} - Submit to AlphaFold")
    print(f"  Large (> 1200 aa):           {large_count} - Submit to AlphaFold")
    print(f"\nFiles created:")
    print(f"  {output_fasta} - All {total_written} sequences")
    print(f"  {output_medium_large} - {medium_large_written} medium/large sequences")
    
    print("\n" + "=" * 80)
    print("NEXT STEPS")
    print("=" * 80)
    print("1. Go to: https://alphafoldserver.com")
    print("2. Sign in (free account)")
    print("3. Click 'Create new job'")
    print("4. Upload one of these files:")
    print(f"   - {output_fasta} (all 80 sequences)")
    print(f"   - {output_medium_large} (only 61 medium/large sequences)")
    print("5. Select 'Monomer' prediction mode")
    print("6. Click 'Predict'")
    print("7. Wait 15-60 minutes for results")
    print("8. Download ZIP with all PDB files")
    print("\nAlternative: Use ColabFold notebook (free Google Colab GPU)")
    print("   https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/AlphaFold2.ipynb")
    print("=" * 80)

if __name__ == "__main__":
    create_combined_fasta()
