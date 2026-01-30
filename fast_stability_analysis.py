#!/usr/bin/env python3
"""
Fast comparison: If full MD fails, do contact-based stability analysis instead.
This provides a quick validation without requiring full MD simulations.
"""

import json
from pathlib import Path
from openmm.app import PDBFile
import numpy as np

STRUCTURES_DIR = Path("all_laminarinase_structures")
RANKING_FILE = Path("comprehensive_laminarinase_ranking.json")
OUTPUT_DIR = Path("md_validation_results")

OUTPUT_DIR.mkdir(exist_ok=True)

def count_hydrogen_bonds(pdb_file, distance_cutoff=3.5, angle_cutoff=120):
    """
    Count hydrogen bonds in a PDB structure as a stability proxy.
    More H-bonds = more stable structure.
    """
    pdb = PDBFile(str(pdb_file))
    topology = pdb.topology
    positions = pdb.positions
    
    h_bond_count = 0
    
    # Get donor and acceptor atoms
    donors = {}
    acceptors = {}
    
    for atom in topology.atoms():
        # Simple H-bond donor recognition
        if atom.element.symbol in ['N', 'O'] and atom.element.symbol == 'N':  # N-H
            donors[atom.index] = atom
        
        # Simple H-bond acceptor recognition  
        if atom.element.symbol in ['N', 'O']:
            acceptors[atom.index] = atom
    
    # This is simplified - for real H-bond analysis would need explicit hydrogens
    # Instead, count close contacts between polar atoms
    
    contact_count = 0
    for i, atom1 in enumerate(topology.atoms()):
        if atom1.element.symbol not in ['N', 'O']:
            continue
        
        for atom2 in topology.atoms():
            if atom2.index <= atom1.index or atom2.element.symbol not in ['N', 'O']:
                continue
            
            # Calculate distance
            pos1 = positions[atom1.index]
            pos2 = positions[atom2.index]
            dist = np.linalg.norm(pos1._value - pos2._value)
            
            if dist < distance_cutoff and dist > 1.8:  # H-bond range (Angstroms)
                contact_count += 1
    
    return contact_count

def calculate_contact_stability_score(contact_count, protein_size):
    """
    Score based on number of contacts and protein size.
    More contacts per residue = more stable.
    """
    contacts_per_residue = contact_count / max(protein_size, 1)
    
    # Scale to 0-100
    # Typical values: 0.5-2.0 contacts per residue
    score = min(100, contacts_per_residue * 50)
    return score

def fast_stability_analysis():
    """
    Quick stability analysis without full MD.
    """
    print("\n" + "="*70)
    print("FAST STABILITY ANALYSIS (Alternative to Full MD)")
    print("="*70)
    
    # Load ranking
    with open(RANKING_FILE) as f:
        data = json.load(f)
        ranking = data['ranking'] if isinstance(data, dict) and 'ranking' in data else data
    
    pdb_files = sorted(STRUCTURES_DIR.glob("*.pdb"))
    
    results = []
    
    print(f"\nAnalyzing {len(pdb_files)} structures...")
    print(f"{'PDB':<6} {'Contacts':<10} {'Stability':<12} {'Static Score':<14}")
    print("-"*70)
    
    for pdb_file in pdb_files:
        pdb_id = pdb_file.stem
        
        # Get static score
        static_score = next((r['affinity_score'] for r in ranking if r['pdb_id'] == pdb_id), None)
        
        try:
            # Count contacts
            pdb = PDBFile(str(pdb_file))
            n_residues = pdb.topology.n_residues
            
            # Simple approach: count unique residue pairs with close atoms
            positions = pdb.positions
            contact_count = 0
            
            atoms_list = list(pdb.topology.atoms())
            for i, atom1 in enumerate(atoms_list):
                for atom2 in atoms_list[i+1:]:
                    # Different residues
                    if atom1.residue.index != atom2.residue.index:
                        pos1 = positions[i]._value
                        pos2 = positions[atom2.index]._value
                        dist = np.sqrt(np.sum((pos1 - pos2)**2))
                        
                        if 2.5 < dist < 4.0:  # Contact distance
                            contact_count += 1
            
            # Calculate stability score
            stability_score = calculate_contact_stability_score(contact_count, n_residues)
            
            results.append({
                'pdb_id': pdb_id,
                'contact_count': contact_count,
                'stability_score': stability_score,
                'static_score': static_score
            })
            
            agreement = "✓" if (static_score >= 55 and stability_score >= 50) or (static_score < 55 and stability_score < 50) else "✗"
            print(f"{pdb_id:<6} {contact_count:<10} {stability_score:<12.1f} {static_score:<14.1f} {agreement}")
        
        except Exception as e:
            print(f"{pdb_id:<6} FAILED: {str(e)[:30]}")
            results.append({
                'pdb_id': pdb_id,
                'contact_count': None,
                'stability_score': None,
                'static_score': static_score,
                'error': str(e)
            })
    
    # Save results
    with open(OUTPUT_DIR / "fast_stability_analysis.json", 'w') as f:
        json.dump(results, f, indent=2)
    
    # Calculate agreement
    valid_results = [r for r in results if r['stability_score'] is not None]
    if valid_results:
        agreements = sum(1 for r in valid_results if 
                        (r['static_score'] >= 55 and r['stability_score'] >= 50) or
                        (r['static_score'] < 55 and r['stability_score'] < 50))
        print(f"\nAgreement: {agreements}/{len(valid_results)} ({100*agreements//len(valid_results)}%)")

if __name__ == "__main__":
    fast_stability_analysis()
