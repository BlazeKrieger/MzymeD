#!/usr/bin/env python3
"""
Comparative Enzyme Affinity Analysis for Laminarinases
========================================================
Compares binding affinity of multiple laminarinase structures against laminarin substrate.
Uses structural features, binding site geometry, and contact analysis to rank enzymes.
"""

import os
import json
import numpy as np
from Bio import PDB
from scipy.spatial.distance import cdist, euclidean
from scipy.spatial import ConvexHull
import warnings

warnings.filterwarnings('ignore')


class EnzymeAffinityAnalyzer:
    """Analyzes enzyme affinity for laminarin substrate."""
    
    def __init__(self, structures_dir):
        self.structures_dir = structures_dir
        self.parser = PDB.PDBParser(QUIET=True)
        self.results = {}
        
        # Catalytic residues for GH16/GH17 laminarinases
        self.catalytic_residues = {
            'GLU': [107, 115, 119],  # Catalytic glutamates
            'ASP': [214, 256],        # Catalytic aspartates
            'TRP': [133, 257],        # Tryptophan (substrate binding)
            'ASN': [43, 84],          # Asparagine (substrate binding)
            'HIS': [133],             # Histidine (substrate binding)
            'GLN': [260]              # Glutamine (substrate binding)
        }
        
        self.enzyme_info = {
            '2W52': {'name': 'BxLam16A', 'organism': 'Phanerochaete chrysosporium', 'family': 'GH16', 'pdb': '2W52'},
            '2W39': {'name': 'BxLam16A', 'organism': 'Phanerochaete chrysosporium', 'family': 'GH16', 'pdb': '2W39'},
            '4BOW': {'name': 'NtLam16', 'organism': 'Nectria haematococca', 'family': 'GH16', 'pdb': '4BOW'},
            '4BPZ': {'name': 'CaLam', 'organism': 'Chrysosporium ascoides', 'family': 'GH16', 'pdb': '4BPZ'}
        }
    
    def get_binding_site_atoms(self, structure, chain_id='A'):
        """Extract atoms in and around the binding site."""
        ppb = PDB.PPBuilder()
        model = structure[0]
        chain = model[chain_id]
        
        # Get catalytic center coordinates
        try:
            glu107 = chain['A'][107]['CA']
            catalytic_center = np.array(glu107.coord)
        except:
            # Fallback: use chain center
            coords = []
            for residue in chain:
                for atom in residue:
                    coords.append(atom.coord)
            catalytic_center = np.mean(coords, axis=0)
        
        # Extract atoms within 20 Å of catalytic center
        binding_site_atoms = []
        for residue in chain:
            if residue.id[0] != ' ':  # Skip heteroatoms in enzyme
                continue
            for atom in residue:
                dist = euclidean(atom.coord, catalytic_center)
                if dist < 20:  # Binding site radius
                    binding_site_atoms.append({
                        'coord': atom.coord,
                        'name': atom.name,
                        'residue': residue.resname,
                        'residue_id': residue.id[1],
                        'element': atom.element
                    })
        
        return binding_site_atoms, catalytic_center
    
    def calculate_binding_site_volume(self, binding_site_atoms):
        """Estimate binding site volume using ConvexHull."""
        if len(binding_site_atoms) < 4:
            return 0
        
        coords = np.array([atom['coord'] for atom in binding_site_atoms])
        try:
            hull = ConvexHull(coords)
            return hull.volume
        except:
            return 0
    
    def calculate_catalytic_residue_conservation(self, structure, chain_id='A'):
        """Score presence of canonical catalytic residues."""
        model = structure[0]
        chain = model[chain_id]
        
        score = 0
        found_residues = {}
        
        for res_type, positions in self.catalytic_residues.items():
            found_residues[res_type] = 0
            for residue in chain:
                if residue.resname == res_type and residue.id[1] in positions:
                    found_residues[res_type] += 1
                    score += 1
        
        # Normalize (max 8 canonical residues for GH16)
        return {'score': score, 'details': found_residues, 'normalized': score / 8.0}
    
    def count_substrate_contacts_all_chains(self, structure):
        """Count contacts between enzyme (chain A) and all substrate chains."""
        model = structure[0]
        
        enzyme_atoms = []
        substrate_atoms = []
        
        # Get enzyme atoms (chain A)
        for chain in model:
            if chain.id == 'A':
                for residue in chain:
                    if residue.id[0] == ' ':  # Only standard residues
                        for atom in residue:
                            enzyme_atoms.append(atom.coord)
                break
        
        # Get all substrate atoms (other chains)
        contact_count = 0
        substrate_chains = []
        
        for chain in model:
            if chain.id == 'A':
                continue
            substrate_chains.append(chain.id)
            for residue in chain:
                for atom in residue:
                    substrate_atoms.append(atom.coord)
                    
                    # Check contact with enzyme
                    if enzyme_atoms:
                        distances = cdist([atom.coord], enzyme_atoms)[0]
                        if np.min(distances) < 3.5:  # Hydrogen bond distance
                            contact_count += 1
        
        return {
            'total_contacts': contact_count,
            'substrate_chains': substrate_chains,
            'num_substrate_chains': len(substrate_chains),
            'contacts_per_chain': contact_count / len(substrate_chains) if substrate_chains else 0
        }
    
    def analyze_structure(self, pdb_id, pdb_file):
        """Comprehensive analysis of single enzyme structure."""
        print(f"\n{'='*70}")
        print(f"Analyzing {pdb_id}: {self.enzyme_info[pdb_id]['name']}")
        print(f"{'='*70}")
        
        try:
            structure = self.parser.get_structure(pdb_id, pdb_file)
        except Exception as e:
            print(f"Error loading {pdb_file}: {e}")
            return None
        
        results = {
            'pdb_id': pdb_id,
            'file': pdb_file,
            **self.enzyme_info[pdb_id]
        }
        
        # 1. Binding site geometry
        binding_site_atoms, catalytic_center = self.get_binding_site_atoms(structure, 'A')
        volume = self.calculate_binding_site_volume(binding_site_atoms)
        results['binding_site_volume'] = volume
        results['binding_site_atom_count'] = len(binding_site_atoms)
        
        print(f"Binding site volume: {volume:.2f} Ų")
        print(f"Binding site atoms: {len(binding_site_atoms)}")
        
        # 2. Catalytic residue conservation
        catalytic_score = self.calculate_catalytic_residue_conservation(structure, 'A')
        results['catalytic_score'] = catalytic_score
        
        print(f"Catalytic residue conservation: {catalytic_score['score']}/8")
        for res_type, count in catalytic_score['details'].items():
            if count > 0:
                print(f"  {res_type}: {count} residues")
        
        # 3. Substrate contact analysis
        contact_info = self.count_substrate_contacts_all_chains(structure)
        results['substrate_contacts'] = contact_info
        
        print(f"Total substrate-enzyme contacts: {contact_info['total_contacts']}")
        print(f"Substrate chains in structure: {contact_info['substrate_chains']}")
        print(f"Contacts per substrate chain: {contact_info['contacts_per_chain']:.1f}")
        
        # 4. Structure quality metrics
        model = structure[0]
        residue_count = 0
        for residue in model['A']:
            if residue.id[0] == ' ':
                residue_count += 1
        results['residue_count'] = residue_count
        
        print(f"Protein chain length: {residue_count} residues")
        
        return results
    
    def calculate_affinity_score(self, analysis_results):
        """Calculate composite affinity score (0-100)."""
        score = 0
        weights = {
            'catalytic': 0.30,
            'contacts': 0.35,
            'volume': 0.20,
            'size': 0.15
        }
        
        # Catalytic residue presence (0-30)
        catalytic_norm = min(analysis_results['catalytic_score']['normalized'] * 30, 30)
        score += catalytic_norm
        
        # Substrate contacts (0-35) - more contacts = stronger binding prediction
        max_contacts = 60  # Normalize to this
        contact_norm = min((analysis_results['substrate_contacts']['total_contacts'] / max_contacts) * 35, 35)
        score += contact_norm
        
        # Binding site volume (0-20) - optimal volume for substrate accommodation
        # Smaller sites may have better specificity, but too small is bad
        volume = analysis_results['binding_site_volume']
        if 50 < volume < 500:  # Optimal range
            volume_norm = 20
        elif volume < 50 or volume > 800:
            volume_norm = 10
        else:
            volume_norm = 15
        score += volume_norm
        
        # Protein size (0-15) - larger proteins often more stable
        size_norm = min((analysis_results['residue_count'] / 400) * 15, 15)
        score += size_norm
        
        return min(score, 100)
    
    def run_analysis(self):
        """Run complete comparative analysis."""
        print("\n" + "="*70)
        print("LAMINARINASE AFFINITY COMPARISON ANALYSIS")
        print("="*70)
        
        # Analyze all structures
        for pdb_id, info in self.enzyme_info.items():
            pdb_file = os.path.join(self.structures_dir, f"{pdb_id}.pdb")
            
            if os.path.exists(pdb_file):
                result = self.analyze_structure(pdb_id, pdb_file)
                if result:
                    self.results[pdb_id] = result
            else:
                print(f"Warning: {pdb_file} not found")
        
        # Calculate affinity scores
        print("\n" + "="*70)
        print("AFFINITY SCORING")
        print("="*70)
        
        for pdb_id, result in self.results.items():
            affinity_score = self.calculate_affinity_score(result)
            result['affinity_score'] = affinity_score
            print(f"{pdb_id} ({result['name']}): {affinity_score:.1f}/100")
        
        # Rank enzymes
        ranked = sorted(
            self.results.items(),
            key=lambda x: x[1]['affinity_score'],
            reverse=True
        )
        
        print("\n" + "="*70)
        print("ENZYME RANKING BY PREDICTED LAMINARIN AFFINITY")
        print("="*70)
        
        for rank, (pdb_id, result) in enumerate(ranked, 1):
            print(f"\n{rank}. {result['name']} ({result['pdb']}) - SCORE: {result['affinity_score']:.1f}/100")
            print(f"   Organism: {result['organism']}")
            print(f"   Family: {result['family']}")
            print(f"   Catalytic score: {result['catalytic_score']['score']}/8")
            print(f"   Substrate contacts: {result['substrate_contacts']['total_contacts']}")
            print(f"   Binding site volume: {result['binding_site_volume']:.1f} Ų")
            print(f"   Protein size: {result['residue_count']} residues")
        
        # Save results
        self.save_results(ranked)
        
        return ranked
    
    def save_results(self, ranked_data):
        """Save analysis results to JSON."""
        output_file = 'enzyme_affinity_comparison.json'
        
        # Prepare JSON-serializable data
        json_data = {
            'analysis_type': 'Laminarinase Affinity Comparison',
            'ranking': []
        }
        
        for rank, (pdb_id, result) in enumerate(ranked_data, 1):
            json_data['ranking'].append({
                'rank': rank,
                'pdb_id': pdb_id,
                'name': result['name'],
                'organism': result['organism'],
                'affinity_score': result['affinity_score'],
                'catalytic_residue_score': result['catalytic_score']['score'],
                'substrate_contacts': result['substrate_contacts']['total_contacts'],
                'binding_site_volume': result['binding_site_volume'],
                'protein_length': result['residue_count']
            })
        
        with open(output_file, 'w') as f:
            json.dump(json_data, f, indent=2)
        
        print(f"\n✓ Results saved to {output_file}")


def main():
    """Run the affinity analysis."""
    structures_dir = 'real_structures'
    
    analyzer = EnzymeAffinityAnalyzer(structures_dir)
    ranked_enzymes = analyzer.run_analysis()
    
    # Print summary
    print("\n" + "="*70)
    print("SUMMARY")
    print("="*70)
    print(f"Analyzed {len(ranked_enzymes)} laminarinase structures")
    print(f"Ranking metric: Predicted laminarin binding affinity")
    print(f"Top enzyme: {ranked_enzymes[0][1]['name']} ({ranked_enzymes[0][1]['affinity_score']:.1f}/100)")


if __name__ == '__main__':
    main()
