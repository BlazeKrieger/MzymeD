#!/usr/bin/env python3
"""
Comprehensive test of MzymeD with laminarinase files
"""

import sys
import os
from pathlib import Path

sys.path.insert(0, 'src')

def test_full_workflow():
    """Test the full MzymeD workflow with laminarinase files"""
    from mzymed.app import MzymeDApp
    from mzymed.file_handler import FileUploader
    
    # Create app instance
    app = MzymeDApp(output_dir="test_outputs")

    # Ensure substrate exists (laminarin mock)
    substrate_path = Path("laminarin_substrate.fasta")
    if not substrate_path.exists():
        uploader = FileUploader(upload_dir="uploads")
        uploader.create_fasta_from_sequence("GGGGTGGGGGGGGGGGGGGGGGGGGGGGGGG", "laminarin_mock", "Laminarin fragment")
        substrate_path = Path(uploader.upload_dir) / "laminarin_mock.fasta"
    
    if app.process_substrate(str(substrate_path)):
        print("✓ Substrate loaded: laminarin mock")
    else:
        print("⚠ Substrate failed to load; continuing without substrate")
    
    # Get first few laminarinase files
    lam_dir = Path("laminarinases")
    fasta_files = sorted(list(lam_dir.rglob("*.fasta")))[:3]
    
    print(f"\n{'='*60}")
    print(f"TESTING FULL WORKFLOW")
    print(f"{'='*60}")
    print(f"Testing with {len(fasta_files)} laminarinase files\n")
    
    results = []
    
    for i, fasta_file in enumerate(fasta_files, 1):
        print(f"\n{'─'*60}")
        print(f"Test {i}: {fasta_file.name}")
        print(f"{'─'*60}")
        
        try:
            # Process enzyme
            if app.process_enzyme(str(fasta_file)):
                print(f"✓ Enzyme processing successful")
                
                # Analyze interactions (includes binding energy if substrate loaded)
                analysis = app.analyze_interactions()
                if analysis:
                    binding = analysis.get('binding_energy')
                    if binding is not None:
                        print(f"✓ Interaction analysis successful (binding energy: {binding:.2f} kcal/mol)")
                    else:
                        print(f"✓ Interaction analysis successful")
                    results.append({
                        'file': fasta_file.name,
                        'status': 'PASSED',
                        'analysis': analysis
                    })
                else:
                    print(f"⚠ Interaction analysis returned None")
                    results.append({
                        'file': fasta_file.name,
                        'status': 'PARTIAL',
                        'analysis': None
                    })
            else:
                print(f"✗ Enzyme processing failed")
                results.append({
                    'file': fasta_file.name,
                    'status': 'FAILED',
                    'analysis': None
                })
                
        except Exception as e:
            print(f"✗ Error: {e}")
            import traceback
            traceback.print_exc()
            results.append({
                'file': fasta_file.name,
                'status': 'ERROR',
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print(f"WORKFLOW TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r['status'] == 'PASSED')
    partial = sum(1 for r in results if r['status'] == 'PARTIAL')
    failed = sum(1 for r in results if r['status'] in ['FAILED', 'ERROR'])
    
    for result in results:
        status_symbol = '✓' if result['status'] == 'PASSED' else ('⚠' if result['status'] == 'PARTIAL' else '✗')
        print(f"{status_symbol} {result['file']}: {result['status']}")
    
    print(f"\nTotal: {passed} passed, {partial} partial, {failed} failed")
    print(f"{'='*60}\n")
    
    return passed > 0

if __name__ == "__main__":
    print("\n" + "="*60)
    print("MzymeD - Full Workflow Test with Laminarinases")
    print("="*60)
    
    try:
        if test_full_workflow():
            print("✓ Workflow test PASSED")
        else:
            print("✗ Workflow test FAILED")
    except Exception as e:
        print(f"✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
