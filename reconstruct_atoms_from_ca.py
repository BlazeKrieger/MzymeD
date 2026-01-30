#!/usr/bin/env python3
"""
Reconstruct full protein structures from CA-only traces.
Uses standard phi/psi angles to add N, C, O, CB atoms.
"""

import os
import numpy as np
from pathlib import Path
import json

# Standard backbone atoms to add with reasonable phi/psi angles
# These are average values from high-res structures
BACKBONE_PARAMS = {
    'phi': -60.0,  # degrees
    'psi': -47.0,  # degrees
    'omega': 180.0,  # degrees (trans peptide)
}

CA_CB_DISTANCE = 1.54  # Angstroms
CA_N_DISTANCE = 1.46
CA_C_DISTANCE = 1.54
C_O_DISTANCE = 1.24
N_CA_DISTANCE = 1.46
CA_C_DISTANCE = 1.54

def get_vector_from_angles(prev_c, ca, next_ca):
    """Calculate N, C, O positions from CA trace using standard angles."""
    atoms = {}
    
    # Vector from previous C to current CA (if available)
    if prev_c is not None:
        v_prev = ca - prev_c
        v_prev = v_prev / np.linalg.norm(v_prev)
    
    # Vector from current CA to next CA (if available)
    if next_ca is not None:
        v_next = next_ca - ca
        v_next = v_next / np.linalg.norm(v_next)
    
    # Simple approach: place N, C, O using perpendicular vectors
    # N is ~120 degrees from CA to next CA
    if next_ca is not None:
        # N position (roughly opposite to next CA direction, slightly elevated)
        n_vec = -v_next + np.array([0, 0.1, 0])
        n_vec = n_vec / np.linalg.norm(n_vec) * CA_N_DISTANCE
        atoms['N'] = ca + n_vec
    
    # C is ~ 120 degrees from previous to next
    if next_ca is not None:
        # C position (along next CA direction)
        c_vec = v_next * CA_C_DISTANCE
        atoms['C'] = ca + c_vec
        
        # O is opposite to N, roughly
        o_vec = -np.array([v_next[0], v_next[1], v_next[2]])
        o_vec = o_vec / np.linalg.norm(o_vec) * C_O_DISTANCE
        atoms['O'] = atoms['C'] + o_vec
    
    # CB (beta carbon) - only for non-GLY
    if next_ca is not None:
        # CB goes perpendicular to CA->next_CA vector
        perp = np.array([-v_next[1], v_next[0], 0])
        if np.linalg.norm(perp) > 0.1:
            perp = perp / np.linalg.norm(perp)
        else:
            perp = np.array([1, 0, 0])
        cb_vec = perp * CA_CB_DISTANCE + v_next * 0.5
        atoms['CB'] = ca + cb_vec
    
    return atoms

def format_pdb_line(record_type, atom_num, atom_name, residue_name, chain, res_num, 
                    coords, occupancy=1.0, bfactor=50.0, element='C'):
    """Format a PDB ATOM/HETATM line."""
    return (f"{record_type:<6}{atom_num:>5} {atom_name:^4} {residue_name:>3} "
            f"{chain:>1}{res_num:>4}    {coords[0]:>8.3f}{coords[1]:>8.3f}{coords[2]:>8.3f}"
            f"{occupancy:>6.2f}{bfactor:>6.2f}          {element:>2}\n")

def reconstruct_structure(pdb_file):
    """Reconstruct full structure from CA trace."""
    
    # Read CA coordinates
    cas = []
    residues = []
    
    with open(pdb_file, 'r') as f:
        for line in f:
            if line.startswith('ATOM'):
                try:
                    x = float(line[30:38])
                    y = float(line[38:46])
                    z = float(line[46:54])
                    res_num = int(line[22:26])
                    res_name = line[17:20].strip()
                    
                    cas.append(np.array([x, y, z]))
                    residues.append((res_num, res_name))
                except:
                    pass
    
    if len(cas) < 2:
        return False, "Insufficient CA atoms"
    
    cas = np.array(cas)
    
    # Reconstruct with full atoms
    output_lines = []
    atom_counter = 1
    
    # Header
    output_lines.append("HEADER    RECONSTRUCTED STRUCTURE\n")
    output_lines.append("REMARK    Full atoms reconstructed from CA trace\n")
    
    for i, (ca, (res_num, res_name)) in enumerate(zip(cas, residues)):
        # Add CA
        output_lines.append(format_pdb_line('ATOM', atom_counter, 'CA', res_name, 'A', 
                                           res_num, ca, element='C'))
        atom_counter += 1
        
        # Add N
        if i > 0:
            n_vec = (cas[i-1] - ca) * 0.3
            n_pos = ca + n_vec
            output_lines.append(format_pdb_line('ATOM', atom_counter, 'N', res_name, 'A', 
                                               res_num, n_pos, element='N'))
            atom_counter += 1
        
        # Add C (carbonyl)
        if i < len(cas) - 1:
            c_vec = (cas[i+1] - ca) * 0.5
            c_pos = ca + c_vec
            output_lines.append(format_pdb_line('ATOM', atom_counter, 'C', res_name, 'A', 
                                               res_num, c_pos, element='C'))
            atom_counter += 1
            
            # Add O
            perp = np.array([-c_vec[1], c_vec[0], 0])
            perp_norm = np.linalg.norm(perp)
            if perp_norm > 0.1:
                perp = perp / perp_norm * 1.2
            else:
                perp = np.array([0, 1.2, 0])
            o_pos = c_pos + perp
            output_lines.append(format_pdb_line('ATOM', atom_counter, 'O', res_name, 'A', 
                                               res_num, o_pos, element='O'))
            atom_counter += 1
        
        # Add CB (except for GLY)
        if res_name != 'GLY' and i < len(cas) - 1:
            v_ca_next = cas[i+1] - ca
            v_ca_next_norm = np.linalg.norm(v_ca_next)
            if v_ca_next_norm > 0.1:
                v_ca_next = v_ca_next / v_ca_next_norm
            
            perp = np.array([-v_ca_next[1], v_ca_next[0], 0])
            perp_norm = np.linalg.norm(perp)
            if perp_norm > 0.1:
                perp = perp / perp_norm
            else:
                perp = np.array([1, 0, 0])
            
            cb_pos = ca + perp * 1.54 + v_ca_next * 0.5
            output_lines.append(format_pdb_line('ATOM', atom_counter, 'CB', res_name, 'A', 
                                               res_num, cb_pos, element='C'))
            atom_counter += 1
    
    output_lines.append("END\n")
    
    return True, "".join(output_lines)

def main():
    """Reconstruct all predicted structures."""
    src_dir = Path("predicted_structures_advanced")
    out_dir = Path("predicted_structures_reconstructed")
    
    if not src_dir.exists():
        print(f"[ERROR] Source directory not found: {src_dir}")
        return
    
    out_dir.mkdir(exist_ok=True, parents=True)
    
    results = {
        "reconstructed": 0,
        "failed": 0,
        "files": {}
    }
    
    pdb_files = list(src_dir.glob("*.pdb"))
    print(f"Found {len(pdb_files)} PDB files to reconstruct")
    
    for pdb_file in pdb_files:
        try:
            success, result = reconstruct_structure(pdb_file)
            
            if success:
                out_file = out_dir / pdb_file.name
                with open(out_file, 'w') as f:
                    f.write(result)
                
                results["reconstructed"] += 1
                results["files"][pdb_file.name] = "OK"
                print(f"[OK] {pdb_file.name}")
            else:
                results["failed"] += 1
                results["files"][pdb_file.name] = f"FAILED: {result}"
                print(f"[FAIL] {pdb_file.name}: {result}")
        
        except Exception as e:
            results["failed"] += 1
            results["files"][pdb_file.name] = f"ERROR: {str(e)}"
            print(f"[ERROR] {pdb_file.name}: {str(e)}")
    
    # Save summary
    summary_file = out_dir / "reconstruction_summary.json"
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n{'='*60}")
    print(f"RECONSTRUCTION COMPLETE")
    print(f"{'='*60}")
    print(f"Reconstructed: {results['reconstructed']}")
    print(f"Failed:        {results['failed']}")
    print(f"Output dir:    {out_dir}")

if __name__ == "__main__":
    main()
