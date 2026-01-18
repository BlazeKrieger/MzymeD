#!/usr/bin/env python3
"""Check what's in the 2W52.pdb file"""

from Bio.PDB import PDBParser

parser = PDBParser(QUIET=True)
struct = parser.get_structure('test', 'real_structures/2W52.pdb')
model = struct[0]

print('Chains in 2W52.pdb:')
for chain in model:
    residues = list(chain)
    print(f'\nChain {chain.id}: {len(residues)} residues')
    
    # Group residues by type
    residue_types = {}
    for res in residues:
        res_name = res.resname
        if res_name not in residue_types:
            residue_types[res_name] = []
        residue_types[res_name].append(res)
    
    for res_name in sorted(residue_types.keys()):
        res_list = residue_types[res_name]
        print(f'  {res_name}: {len(res_list)} residues (e.g., {res_list[0].id})')
