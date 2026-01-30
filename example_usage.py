#!/usr/bin/env python3
import sys
sys.path.insert(0, 'src')
from mzymed.app import MzymeDApp

def main():
    print("MzymeD - Enzyme-Substrate Molecular Dynamics Analysis")
    app = MzymeDApp(output_dir="outputs")
    
    enzyme_file = "example_laminarinase.fasta"
    if app.process_enzyme(enzyme_file):
        print("✓ Enzyme processed")
    
    results = app.analyze_interactions()
    if results:
        print("✓ Analysis complete")
        print(f"Active site residues: {len(results.get('active_site_residues', []))}")
    
    print("\nDone! Check outputs/ folder for results")

if __name__ == "__main__":
    main()
