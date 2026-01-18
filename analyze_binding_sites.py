#!/usr/bin/env python3
"""
Option A: Analyze binding sites in 2W52.pdb
Identifies all close contacts between enzyme (chain A) and substrates (chains B, C, D)
"""

from Bio.PDB import PDBParser, PDBIO, Select
from scipy.spatial.distance import euclidean
import numpy as np
from collections import defaultdict
import json
from pathlib import Path

class BindingSiteAnalyzer:
    def __init__(self, pdb_file):
        self.parser = PDBParser(QUIET=True)
        self.structure = self.parser.get_structure('enzyme', pdb_file)
        self.enzyme_chain = 'A'
        self.substrate_chains = ['B', 'C', 'D']
    
    def get_chain_atoms(self, chain_id):
        """Extract all atoms from a chain with their coordinates"""
        atoms = []
        for chain in self.structure.get_chains():
            if chain.id == chain_id:
                for residue in chain.get_residues():
                    # Include both standard residues and HETATM records (like NAG sugars)
                    for atom in residue.get_atoms():
                        atoms.append({
                            'name': atom.name,
                            'coord': atom.coord,
                            'resname': residue.resname,
                            'resnum': residue.id[1],
                            'element': atom.element
                        })
        return atoms
    
    def find_close_contacts(self, enzyme_atoms, substrate_atoms, distance_cutoff=3.5):
        """Find all atom pairs within distance cutoff"""
        contacts = []
        for enz in enzyme_atoms:
            for sub in substrate_atoms:
                dist = euclidean(enz['coord'], sub['coord'])
                if dist < distance_cutoff:
                    contacts.append({
                        'distance': dist,
                        'enzyme_res': f"{enz['resname']}{enz['resnum']}",
                        'enzyme_atom': enz['name'],
                        'substrate_atom': sub['name'],
                        'substrate_res': f"{sub['resname']}{sub['resnum']}",
                        'enzyme_resnum': enz['resnum']
                    })
        return contacts
    
    def analyze_all_sites(self):
        """Analyze contacts for all substrate chains"""
        enzyme_atoms = self.get_chain_atoms(self.enzyme_chain)
        results = {}
        
        print("\n" + "="*80)
        print("BINDING SITE ANALYSIS FOR 2W52.PDB")
        print("="*80)
        print(f"\nEnzyme: Chain {self.enzyme_chain} ({len(enzyme_atoms)} atoms)")
        
        for chain_id in self.substrate_chains:
            substrate_atoms = self.get_chain_atoms(chain_id)
            
            if not substrate_atoms:
                print(f"\nChain {chain_id}: NOT FOUND")
                continue
            
            print(f"\n{'-'*80}")
            print(f"SUBSTRATE CHAIN {chain_id}")
            print(f"{'-'*80}")
            print(f"Substrate atoms: {len(substrate_atoms)}")
            
            # Find contacts
            contacts = self.find_close_contacts(enzyme_atoms, substrate_atoms, distance_cutoff=3.5)
            
            if not contacts:
                print("No close contacts found")
                continue
            
            # Sort by distance
            contacts.sort(key=lambda x: x['distance'])
            
            # Group by enzyme residue
            residue_contacts = defaultdict(list)
            for contact in contacts:
                residue_contacts[contact['enzyme_resnum']].append(contact)
            
            print(f"\nTotal close contacts (< 3.5 Å): {len(contacts)}")
            print(f"Unique enzyme residues involved: {len(residue_contacts)}")
            
            # Show top contacts
            print(f"\nTop 15 closest contacts:")
            print(f"{'Dist (Å)':<10} {'Enzyme Residue':<20} {'Enzyme Atom':<10} {'Substrate Atom':<10}")
            print("-" * 50)
            for contact in contacts[:15]:
                print(f"{contact['distance']:<10.2f} {contact['enzyme_res']:<20} {contact['enzyme_atom']:<10} {contact['substrate_atom']:<10}")
            
            # Show enzyme residues by frequency
            print(f"\nEnzyme residues by contact frequency:")
            print(f"{'Residue':<15} {'# Contacts':<12} {'Avg Distance (Å)':<15}")
            print("-" * 42)
            
            residue_stats = []
            for resnum, res_contacts in sorted(residue_contacts.items()):
                avg_dist = np.mean([c['distance'] for c in res_contacts])
                residue_stats.append((resnum, len(res_contacts), avg_dist, res_contacts[0]['enzyme_res']))
            
            residue_stats.sort(key=lambda x: -x[1])  # Sort by contact count
            for resnum, count, avg_dist, resname in residue_stats[:20]:
                print(f"{resname:<15} {count:<12} {avg_dist:<15.2f}")
            
            results[chain_id] = {
                'total_contacts': len(contacts),
                'unique_residues': len(residue_contacts),
                'top_residues': residue_stats[:10],
                'all_contacts': contacts
            }
        
        return results
    
    def compare_binding_sites(self, results):
        """Compare substrate binding sites"""
        print("\n" + "="*80)
        print("BINDING SITE COMPARISON")
        print("="*80)
        
        if len(results) < 2:
            print("Only one substrate found - comparison not possible")
            return
        
        chains_found = sorted(results.keys())
        print(f"\nSubstrates found: {', '.join(chains_found)}")
        
        # Get top residues for each chain
        for chain_id in chains_found:
            top_res = [r[3] for r in results[chain_id]['top_residues'][:5]]
            print(f"\nChain {chain_id} - Top 5 contacting residues:")
            for i, res in enumerate(top_res, 1):
                print(f"  {i}. {res}")
        
        # Identify shared residues
        if len(chains_found) > 1:
            chain1_residues = set(r[3] for r in results[chains_found[0]]['top_residues'])
            chain2_residues = set(r[3] for r in results[chains_found[1]]['top_residues'])
            shared = chain1_residues & chain2_residues
            
            print(f"\nShared binding residues (Chain {chains_found[0]} & {chains_found[1]}):")
            if shared:
                for res in sorted(shared):
                    print(f"  • {res}")
            else:
                print("  No shared residues in top 10")
        
        print("\nINTERPRETATION:")
        print("  • Shared residues = Part of extended binding cleft")
        print("  • Different residues = Distinct binding subsites")
        print("  • More contacts = Higher affinity binding")


def main():
    pdb_file = 'real_structures/2W52.pdb'
    
    if not Path(pdb_file).exists():
        print(f"Error: {pdb_file} not found")
        return
    
    analyzer = BindingSiteAnalyzer(pdb_file)
    results = analyzer.analyze_all_sites()
    analyzer.compare_binding_sites(results)
    
    # Save results
    output_file = 'analysis_results/binding_site_analysis.json'
    Path('analysis_results').mkdir(exist_ok=True)
    
    # Convert for JSON serialization
    json_results = {}
    for chain, data in results.items():
        json_results[chain] = {
            'total_contacts': data['total_contacts'],
            'unique_residues': data['unique_residues'],
            'top_residues': [(r[3], int(r[1]), float(r[2])) for r in data['top_residues']],
        }
    
    with open(output_file, 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print(f"\n✓ Results saved to: {output_file}")


if __name__ == '__main__':
    main()
