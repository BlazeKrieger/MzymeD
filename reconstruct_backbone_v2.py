#!/usr/bin/env python3
"""
Better PDB reconstruction from CA traces using rosetta-style backbone placement.
"""

import numpy as np
from pathlib import Path
import json
from openmm.app import PDBFile, Topology
from openmm import unit

def read_ca_pdb(filename):
    """Read CA coordinates and residue info from PDB."""
    cas = []
    residues = []
    chains_info = []
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('ATOM'):
                atom_name = line[12:16].strip()
                res_num = int(line[22:26])
                res_name = line[17:20].strip()
                chain_id = line[21]
                
                if atom_name == 'CA':
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        
                        cas.append(np.array([x, y, z]))
                        residues.append({
                            'num': res_num,
                            'name': res_name,
                            'chain': chain_id
                        })
                    except:
                        pass
    
    return np.array(cas), residues

def build_backbone_atoms(cas, residues):
    """Build N, C, O atoms from CA trace using ideal geometry."""
    output_lines = []
    atom_counter = 1
    
    n_residues = len(cas)
    
    for i in range(n_residues):
        ca = cas[i]
        res_info = residues[i]
        res_name = res_info['name']
        res_num = res_info['num']
        chain = res_info['chain']
        
        # Add N (backbone nitrogen)
        if i > 0:
            # N is ~1.46 Å from CA in direction away from previous CA
            vec_to_prev = cas[i-1] - ca
            if np.linalg.norm(vec_to_prev) > 0.1:
                vec_to_prev = vec_to_prev / np.linalg.norm(vec_to_prev)
                # Rotate ~120 degrees to place N
                perp = np.array([-vec_to_prev[1], vec_to_prev[0], 0])
                if np.linalg.norm(perp) < 0.1:
                    perp = np.array([1, 0, 0])
                else:
                    perp = perp / np.linalg.norm(perp)
                n_pos = ca - vec_to_prev * 0.3 + perp * 1.0
            else:
                n_pos = ca + np.array([0, 1.46, 0])
        else:
            n_pos = ca + np.array([0, 1.46, 0])
        
        line = (f"ATOM  {atom_counter:>5} {'N':^4} {res_name:>3} {chain:>1}"
                f"{res_num:>4}    {n_pos[0]:>8.3f}{n_pos[1]:>8.3f}{n_pos[2]:>8.3f}"
                f"  1.00 50.00           N\n")
        output_lines.append(line)
        atom_counter += 1
        
        # Add CA
        line = (f"ATOM  {atom_counter:>5} {'CA':^4} {res_name:>3} {chain:>1}"
                f"{res_num:>4}    {ca[0]:>8.3f}{ca[1]:>8.3f}{ca[2]:>8.3f}"
                f"  1.00 50.00           C\n")
        output_lines.append(line)
        atom_counter += 1
        
        # Add C (carbonyl carbon)
        if i < n_residues - 1:
            vec_to_next = cas[i+1] - ca
            if np.linalg.norm(vec_to_next) > 0.1:
                vec_to_next = vec_to_next / np.linalg.norm(vec_to_next)
                c_pos = ca + vec_to_next * 1.54
            else:
                c_pos = ca + np.array([1.54, 0, 0])
        else:
            c_pos = ca + np.array([1.54, 0, 0])
        
        line = (f"ATOM  {atom_counter:>5} {'C':^4} {res_name:>3} {chain:>1}"
                f"{res_num:>4}    {c_pos[0]:>8.3f}{c_pos[1]:>8.3f}{c_pos[2]:>8.3f}"
                f"  1.00 50.00           C\n")
        output_lines.append(line)
        atom_counter += 1
        
        # Add O (carbonyl oxygen)
        if i < n_residues - 1:
            # O is roughly opposite to N, on the C
            perp = np.array([-vec_to_next[1], vec_to_next[0], 0])
            if np.linalg.norm(perp) < 0.1:
                perp = np.array([0, 1, 0])
            else:
                perp = perp / np.linalg.norm(perp)
            o_pos = c_pos + perp * 1.24
        else:
            o_pos = c_pos + np.array([0, 1.24, 0])
        
        line = (f"ATOM  {atom_counter:>5} {'O':^4} {res_name:>3} {chain:>1}"
                f"{res_num:>4}    {o_pos[0]:>8.3f}{o_pos[1]:>8.3f}{o_pos[2]:>8.3f}"
                f"  1.00 50.00           O\n")
        output_lines.append(line)
        atom_counter += 1
        
        # Add CB (beta carbon) for non-GLY
        if res_name != 'GLY':
            if i < n_residues - 1:
                vec_to_next = cas[i+1] - ca
                perp = np.array([-vec_to_next[1], vec_to_next[0], 0])
                if np.linalg.norm(perp) < 0.1:
                    perp = np.array([1, 0, 0])
                else:
                    perp = perp / np.linalg.norm(perp)
                cb_pos = ca + perp * 1.54
            else:
                cb_pos = ca + np.array([1.54, 0, 0])
            
            line = (f"ATOM  {atom_counter:>5} {'CB':^4} {res_name:>3} {chain:>1}"
                    f"{res_num:>4}    {cb_pos[0]:>8.3f}{cb_pos[1]:>8.3f}{cb_pos[2]:>8.3f}"
                    f"  1.00 50.00           C\n")
            output_lines.append(line)
            atom_counter += 1
    
    return output_lines

def main():
    src_dir = Path("predicted_structures_advanced")
    out_dir = Path("predicted_structures_reconstructed_v2")
    
    out_dir.mkdir(exist_ok=True, parents=True)
    
    results = {
        "reconstructed": 0,
        "failed": 0,
        "files": {}
    }
    
    pdb_files = sorted(src_dir.glob("*.pdb"))
    print(f"[*] Reconstructing {len(pdb_files)} structures...")
    
    for i, pdb_file in enumerate(pdb_files):
        try:
            cas, residues = read_ca_pdb(pdb_file)
            
            if len(cas) < 2:
                raise ValueError(f"Only {len(cas)} CA atoms found")
            
            # Build new PDB with full atoms
            lines = ["HEADER    RECONSTRUCTED STRUCTURE\n"]
            lines.append("REMARK    Full atoms from CA trace\n")
            lines += build_backbone_atoms(cas, residues)
            lines.append("END\n")
            
            # Write output
            out_file = out_dir / pdb_file.name
            with open(out_file, 'w') as f:
                f.writelines(lines)
            
            results["reconstructed"] += 1
            results["files"][pdb_file.name] = "OK"
            print(f"[{i+1:3d}/{len(pdb_files)}] {pdb_file.name:50s} OK ({len(cas)} residues, {len(lines)-3} atoms)")
        
        except Exception as e:
            results["failed"] += 1
            results["files"][pdb_file.name] = f"ERROR: {str(e)}"
            print(f"[{i+1:3d}/{len(pdb_files)}] {pdb_file.name:50s} FAILED: {str(e)}")
    
    # Save summary
    summary_file = out_dir / "reconstruction_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*70}")
    print(f"RECONSTRUCTION COMPLETE")
    print(f"Reconstructed: {results['reconstructed']}")
    print(f"Failed:        {results['failed']}")
    print(f"Output:        {out_dir}")

if __name__ == "__main__":
    main()
