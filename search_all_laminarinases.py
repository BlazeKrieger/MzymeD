#!/usr/bin/env python3
"""
Fast Search for Laminarinase Structures - Direct API Query
===========================================================
"""

import requests
import json
import os
from pathlib import Path
import time
import urllib3

# Suppress SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def search_pdb_simple(keywords):
    """Simple PDB search using RCSB query API."""
    
    print("\n" + "="*80)
    print("SEARCHING RCSB PDB FOR LAMINARINASE STRUCTURES")
    print("="*80)
    
    all_pdb_ids = set()
    
    for keyword in keywords:
        print(f"\nSearching: '{keyword}'")
        try:
            # Use basic text search
            url = f"https://search.rcsb.org/rcsbsearch/v2/query"
            
            query_json = {
                "query": {
                    "type": "text",
                    "parameters": {
                        "q": keyword,
                        "eDismax": True
                    }
                },
                "request_options": {
                    "paginate": {
                        "start": 0,
                        "rows": 200
                    }
                },
                "return_type": "entry"
            }
            
            response = requests.post(
                url, 
                json=query_json, 
                timeout=15,
                verify=False
            )
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('result_set', [])
                
                for result in results:
                    pdb_id = result.get('identifier', '').upper()
                    if pdb_id:
                        all_pdb_ids.add(pdb_id)
                
                print(f"  Found {len(results)} results, cumulative: {len(all_pdb_ids)}")
            else:
                print(f"  Query failed: {response.status_code}")
            
            time.sleep(1)
            
        except requests.exceptions.Timeout:
            print(f"  Timeout on {keyword}")
        except Exception as e:
            print(f"  Error: {str(e)[:100]}")
    
    return sorted(list(all_pdb_ids))

def download_pdb_file(pdb_id, output_dir):
    """Download a PDB file from RCSB."""
    try:
        url = f"https://files.rcsb.org/download/{pdb_id.upper()}.pdb"
        response = requests.get(url, timeout=10, verify=False)
        
        if response.status_code == 200:
            output_file = os.path.join(output_dir, f"{pdb_id.upper()}.pdb")
            with open(output_file, 'w') as f:
                f.write(response.text)
            return True
        return False
    except:
        return False

def main():
    """Run the search and download."""
    
    output_dir = 'all_laminarinase_structures'
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Search terms
    keywords = [
        'laminarinase',
        'beta-glucanase',
        '1,3-glucanase',
        'laminarin',
        'GH16',
    ]
    
    # Search
    pdb_ids = search_pdb_simple(keywords)
    
    print(f"\n{'='*80}")
    print(f"TOTAL STRUCTURES FOUND: {len(pdb_ids)}")
    print(f"{'='*80}\n")
    
    if pdb_ids:
        print("PDB IDs found:")
        for i, pdb_id in enumerate(pdb_ids, 1):
            print(f"  {i:3d}. {pdb_id}")
        
        # Save list
        with open('found_laminarinases.json', 'w') as f:
            json.dump({'count': len(pdb_ids), 'pdb_ids': pdb_ids}, f, indent=2)
        print(f"\n✓ Found PDB IDs saved to found_laminarinases.json")
        
        # Download first 30
        print(f"\n{'='*80}")
        print(f"DOWNLOADING STRUCTURES (limiting to first 30)")
        print(f"{'='*80}\n")
        
        downloaded = []
        failed = []
        
        for i, pdb_id in enumerate(pdb_ids[:30], 1):
            print(f"[{i}/30] {pdb_id}...", end=' ', flush=True)
            if download_pdb_file(pdb_id, output_dir):
                print("✓")
                downloaded.append(pdb_id)
            else:
                print("✗")
                failed.append(pdb_id)
            time.sleep(0.3)
        
        print(f"\n{'='*80}")
        print(f"Downloaded: {len(downloaded)}")
        print(f"Failed: {len(failed)}")
        print(f"{'='*80}\n")
        
        # Save download results
        with open('download_results.json', 'w') as f:
            json.dump({
                'downloaded': downloaded,
                'failed': failed,
                'total_downloaded': len(downloaded)
            }, f, indent=2)
        
        print(f"✓ Results saved to download_results.json")
        print(f"✓ Structures saved in {output_dir}/")

if __name__ == '__main__':
    main()
