#!/usr/bin/env python3
"""
Option B Part 1: Multi-structure comparison
Downloads PDB structures and compares binding sites across laminarinase variants
"""

from Bio.PDB import PDBList, PDBParser
from pathlib import Path
import json
import subprocess

class StructureDownloader:
    def __init__(self):
        self.pdbl = PDBList()
        self.pdb_dir = Path('real_structures')
        self.pdb_dir.mkdir(exist_ok=True)
    
    def download_structure(self, pdb_id):
        """Download PDB structure if not already present"""
        pdb_file = self.pdb_dir / f"{pdb_id.lower()}.pdb"
        
        if pdb_file.exists():
            print(f"✓ {pdb_id}.pdb already downloaded")
            return str(pdb_file)
        
        try:
            print(f"↓ Downloading {pdb_id}...")
            filepath = self.pdbl.retrieve_pdb_file(
                pdb_id, 
                pdir=str(self.pdb_dir), 
                file_format='pdb'
            )
            # Rename from .ent to .pdb
            new_filepath = self.pdb_dir / f"{pdb_id.lower()}.pdb"
            Path(filepath).rename(new_filepath) if Path(filepath).exists() else None
            print(f"✓ Downloaded: {pdb_id}")
            return str(new_filepath)
        except Exception as e:
            print(f"✗ Failed to download {pdb_id}: {e}")
            return None
    
    def get_pdb_info(self, pdb_id):
        """Get info about a PDB structure"""
        try:
            # Query RCSB API for structure info
            import urllib.request
            url = f"https://data.rcsb.org/rest/v1/core/entry/{pdb_id}"
            response = urllib.request.urlopen(url, timeout=5)
            data = json.loads(response.read())
            
            title = data.get('struct', {}).get('title', 'Unknown')
            resolution = data.get('rcsb_entry_info', {}).get('resolution_combined', [None])[0]
            
            return {'title': title, 'resolution': resolution}
        except:
            return {'title': 'Unknown', 'resolution': None}


def main():
    print("\n" + "="*80)
    print("OPTION B PART 1: MULTI-STRUCTURE COMPARISON")
    print("="*80)
    
    # Known laminarinase structures from your repo and PDB
    structures_to_analyze = {
        '2W52': 'Laminarinase 16A + NAG (your current structure)',
        '2W39': 'Laminarinase 16A + disaccharide',
        '4BOW': 'Different laminarinase variant',
        '4BPZ': 'Different laminarinase variant',
    }
    
    downloader = StructureDownloader()
    
    print("\nTarget structures:")
    for pdb_id, description in structures_to_analyze.items():
        print(f"  • {pdb_id}: {description}")
    
    # Download structures
    print("\nDownloading structures...")
    downloaded = {}
    for pdb_id in structures_to_analyze.keys():
        filepath = downloader.download_structure(pdb_id)
        if filepath:
            downloaded[pdb_id] = filepath
    
    # Analyze each structure
    print("\n" + "-"*80)
    print("ANALYZING DOWNLOADED STRUCTURES")
    print("-"*80)
    
    for pdb_id, filepath in downloaded.items():
        print(f"\n{pdb_id}:")
        info = downloader.get_pdb_info(pdb_id)
        print(f"  Title: {info['title']}")
        if info['resolution']:
            print(f"  Resolution: {info['resolution']:.2f} Å")
        
        # Quick check of chains
        try:
            parser = PDBParser(QUIET=True)
            structure = parser.get_structure(pdb_id, filepath)
            chains = [chain.id for chain in structure.get_chains()]
            print(f"  Chains: {', '.join(chains)}")
        except:
            print(f"  Could not parse structure")
    
    # Create analysis script for all structures
    print("\n" + "="*80)
    print("NEXT STEPS")
    print("="*80)
    print("""
For comprehensive analysis across all structures:

1. Compare substrate binding modes:
   python analyze_binding_sites.py --compare-all
   
2. Identify conserved binding residues:
   python align_binding_residues.py
   
3. Visualize all structures in PyMOL:
   pymol real_structures/*.pdb
   """)
    
    print("✓ Multi-structure download complete")


if __name__ == '__main__':
    main()
