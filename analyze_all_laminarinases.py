#!/usr/bin/env python3
"""
Comprehensive Affinity Analysis of All Downloaded Laminarinases
================================================================
Analyzes all 20+ downloaded laminarinase structures and ranks them
"""

import os
import json
import numpy as np
from Bio import PDB
from scipy.spatial.distance import cdist, euclidean
from scipy.spatial import ConvexHull
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

class ComprehensiveLaminarinaseAnalyzer:
    """Analyzes all laminarinase structures from PDB."""
    
    def __init__(self, structures_dir='all_laminarinase_structures'):
        self.structures_dir = structures_dir
        self.parser = PDB.PDBParser(QUIET=True)
        self.results = {}
        
        self.catalytic_residues = {
            'GLU': [107, 115, 119, 135, 144, 154],
            'ASP': [214, 256],
            'TRP': [133, 257],
            'ASN': [43, 84],
            'HIS': [133],
            'GLN': [260]
        }
    
    def get_binding_site_atoms(self, structure, chain_id='A'):
        """Extract atoms in the binding site."""
        model = structure[0]
        
        # Find catalytic center
        try:
            chain = None
            for c in model:
                if c.id == chain_id:
                    chain = c
                    break
            
            if not chain:
                return [], np.array([0, 0, 0])
            
            coords_list = []
            for residue in chain:
                if residue.id[0] == ' ':
                    for atom in residue:
                        coords_list.append(atom.coord)
            
            if coords_list:
                catalytic_center = np.mean(coords_list, axis=0)
            else:
                return [], np.array([0, 0, 0])
        except:
            return [], np.array([0, 0, 0])
        
        # Extract binding site atoms
        binding_site_atoms = []
        for residue in chain:
            if residue.id[0] != ' ':
                continue
            for atom in residue:
                dist = euclidean(atom.coord, catalytic_center)
                if dist < 20:
                    binding_site_atoms.append({
                        'coord': atom.coord,
                        'name': atom.name,
                        'residue': residue.resname,
                        'residue_id': residue.id[1],
                        'element': atom.element
                    })
        
        return binding_site_atoms, catalytic_center
    
    def calculate_binding_site_volume(self, binding_site_atoms):
        """Calculate binding site volume."""
        if len(binding_site_atoms) < 4:
            return 0
        
        coords = np.array([atom['coord'] for atom in binding_site_atoms])
        try:
            hull = ConvexHull(coords)
            return hull.volume
        except:
            return 0
    
    def calculate_catalytic_conservation(self, structure, chain_id='A'):
        """Score catalytic residue presence."""
        model = structure[0]
        
        try:
            chain = None
            for c in model:
                if c.id == chain_id:
                    chain = c
                    break
            
            if not chain:
                return {'score': 0, 'normalized': 0, 'details': {}}
        except:
            return {'score': 0, 'normalized': 0, 'details': {}}
        
        score = 0
        found_residues = {}
        
        for res_type, positions in self.catalytic_residues.items():
            found_residues[res_type] = 0
            for residue in chain:
                if residue.resname == res_type and residue.id[1] in positions:
                    found_residues[res_type] += 1
                    score += 1
        
        return {
            'score': score,
            'normalized': min(score / 8.0, 1.0),
            'details': found_residues
        }
    
    def count_substrate_contacts(self, structure):
        """Count enzyme-substrate contacts."""
        model = structure[0]
        
        enzyme_atoms = []
        contact_count = 0
        substrate_chains = []
        
        try:
            # Get enzyme atoms (chain A)
            for chain in model:
                if chain.id == 'A':
                    for residue in chain:
                        if residue.id[0] == ' ':
                            for atom in residue:
                                enzyme_atoms.append(atom.coord)
                    break
            
            # Count contacts with other chains
            for chain in model:
                if chain.id == 'A':
                    continue
                
                substrate_chains.append(chain.id)
                for residue in chain:
                    for atom in residue:
                        if enzyme_atoms:
                            distances = cdist([atom.coord], enzyme_atoms)[0]
                            if np.min(distances) < 3.5:
                                contact_count += 1
        except:
            pass
        
        return {
            'total_contacts': contact_count,
            'substrate_chains': substrate_chains,
            'num_substrate_chains': len(substrate_chains),
            'contacts_per_chain': contact_count / len(substrate_chains) if substrate_chains else 0
        }
    
    def analyze_all_structures(self):
        """Analyze all downloaded structures."""
        
        pdb_files = list(Path(self.structures_dir).glob('*.pdb'))
        
        print("\n" + "="*80)
        print(f"ANALYZING {len(pdb_files)} LAMINARINASE STRUCTURES")
        print("="*80)
        
        for pdb_file in sorted(pdb_files):
            pdb_id = pdb_file.stem.upper()
            print(f"\n→ {pdb_id}...", end=' ', flush=True)
            
            try:
                structure = self.parser.get_structure(pdb_id, str(pdb_file))
                
                # Get basic info
                binding_site_atoms, _ = self.get_binding_site_atoms(structure, 'A')
                volume = self.calculate_binding_site_volume(binding_site_atoms)
                catalytic = self.calculate_catalytic_conservation(structure, 'A')
                contacts = self.count_substrate_contacts(structure)
                
                # Count residues
                residue_count = 0
                model = structure[0]
                for chain in model:
                    if chain.id == 'A':
                        for residue in chain:
                            if residue.id[0] == ' ':
                                residue_count += 1
                        break
                
                self.results[pdb_id] = {
                    'pdb_id': pdb_id,
                    'binding_site_volume': volume,
                    'catalytic_score': catalytic['score'],
                    'catalytic_normalized': catalytic['normalized'],
                    'substrate_contacts': contacts['total_contacts'],
                    'substrate_chains': contacts['num_substrate_chains'],
                    'residue_count': residue_count,
                    'binding_site_atoms': len(binding_site_atoms)
                }
                
                print("✓")
                
            except Exception as e:
                print(f"✗ ({str(e)[:30]})")
        
        return self.results
    
    def calculate_affinity_scores(self):
        """Calculate affinity scores for all structures."""
        
        print("\n" + "="*80)
        print("CALCULATING AFFINITY SCORES")
        print("="*80)
        
        for pdb_id, data in self.results.items():
            score = 0
            
            # Catalytic (30%)
            catalytic_norm = min(data['catalytic_normalized'] * 30, 30)
            score += catalytic_norm
            
            # Contacts (35%)
            max_contacts = 60
            contact_norm = min((data['substrate_contacts'] / max_contacts) * 35, 35)
            score += contact_norm
            
            # Volume (20%)
            volume = data['binding_site_volume']
            if 50 < volume < 500:
                volume_norm = 20
            elif volume < 50 or volume > 800:
                volume_norm = 10
            else:
                volume_norm = 15
            score += volume_norm
            
            # Size (15%)
            size_norm = min((data['residue_count'] / 400) * 15, 15)
            score += size_norm
            
            data['affinity_score'] = min(score, 100)
    
    def rank_and_report(self):
        """Rank enzymes and generate report."""
        
        self.calculate_affinity_scores()
        
        # Rank by affinity score
        ranked = sorted(
            self.results.items(),
            key=lambda x: x[1]['affinity_score'],
            reverse=True
        )
        
        print("\n" + "="*80)
        print("COMPLETE LAMINARINASE RANKING (ALL PDB STRUCTURES)")
        print("="*80)
        
        for rank, (pdb_id, data) in enumerate(ranked, 1):
            print(f"\n{rank:2d}. {pdb_id:6s} - Score: {data['affinity_score']:5.1f}/100")
            print(f"    Catalytic: {data['catalytic_score']}/8 | Contacts: {data['substrate_contacts']:2d} | Volume: {data['binding_site_volume']:7.0f} Ų")
        
        # Save detailed results
        json_results = {
            'total_analyzed': len(self.results),
            'ranking': []
        }
        
        for rank, (pdb_id, data) in enumerate(ranked, 1):
            json_results['ranking'].append({
                'rank': rank,
                'pdb_id': pdb_id,
                'affinity_score': data['affinity_score'],
                'catalytic_residues': data['catalytic_score'],
                'substrate_contacts': data['substrate_contacts'],
                'binding_site_volume': data['binding_site_volume'],
                'protein_length': data['residue_count']
            })
        
        with open('comprehensive_laminarinase_ranking.json', 'w') as f:
            json.dump(json_results, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"✓ Detailed results saved to comprehensive_laminarinase_ranking.json")
        print(f"✓ Analyzed {len(self.results)} structures from all_laminarinase_structures/")
        
        return ranked


def main():
    """Run comprehensive analysis."""
    analyzer = ComprehensiveLaminarinaseAnalyzer()
    
    # Analyze all structures
    results = analyzer.analyze_all_structures()
    
    if results:
        # Rank and report
        ranked = analyzer.rank_and_report()
        
        # Summary
        print(f"\n{'='*80}")
        print("ANALYSIS COMPLETE")
        print(f"{'='*80}")
        print(f"Total structures analyzed: {len(results)}")
        print(f"Top candidate: {ranked[0][0]} (Score: {ranked[0][1]['affinity_score']:.1f}/100)")
    else:
        print("No structures analyzed. Check download folder.")


if __name__ == '__main__':
    main()
