#!/usr/bin/env python3
"""
Test script to test MzymeD with laminarinase FASTA files
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

def list_laminarinase_files():
    """List available laminarinase files"""
    lam_dir = Path("laminarinases")
    fasta_files = []
    
    for fasta_file in lam_dir.rglob("*.fasta"):
        fasta_files.append(fasta_file)
    
    return sorted(fasta_files)

def test_file_loading():
    """Test if files can be loaded"""
    from mzymed.file_handler import FileUploader
    
    uploader = FileUploader()
    fasta_files = list_laminarinase_files()
    
    print(f"\n{'='*60}")
    print(f"TESTING FILE LOADING")
    print(f"{'='*60}")
    print(f"Found {len(fasta_files)} FASTA files\n")
    
    success_count = 0
    error_count = 0
    
    # Test first 5 files
    for fasta_file in fasta_files[:5]:
        print(f"Testing: {fasta_file.relative_to('.')}")
        try:
            is_valid, message = uploader.validate_sequence_file(str(fasta_file))
            if is_valid:
                seq_record = uploader.load_sequence(str(fasta_file))
                if seq_record:
                    seq_len = len(seq_record.seq)
                    print(f"  ✓ Loaded successfully ({seq_len} aa)")
                    success_count += 1
                else:
                    print(f"  ✗ Failed to load sequence")
                    error_count += 1
            else:
                print(f"  ✗ Validation failed: {message}")
                error_count += 1
        except Exception as e:
            print(f"  ✗ Error: {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Results: {success_count} successful, {error_count} failed")
    print(f"{'='*60}\n")
    
    return success_count > 0

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MzymeD - Laminarinase Test Suite")
    print("="*60)
    
    try:
        if test_file_loading():
            print("✓ File loading test PASSED")
        else:
            print("✗ File loading test FAILED")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
