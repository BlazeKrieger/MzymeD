#!/usr/bin/env python3
"""
Ultra-simple backbone reconstruction - just duplicate CA as CB and offset for C, O, N.
These are placeholder structures for MD testing, not meant to be physically realistic.
"""

from pathlib import Path
import json

def simple_reconstruct(pdb_file):
    """Add minimal backbone atoms to CA-only PDB."""
    lines = []
    atom_counter = 1
    
    # Header
    lines.append("HEADER    BACKBONE RECONSTRUCTED\n")
    lines.append("REMARK    Simple N,C,O,CB from CA trace\n")
    
    # Read original atoms
    with open(pdb_file) as f:
        for line in f:
            if line.startswith('ATOM'):
                lines.append(line)
                atom_counter += 1
                
                # After each CA, add N, C, O, CB
                if 'CA' in line[12:16]:
                    # Extract coordinate
                    try:
                        x = float(line[30:38])
                        y = float(line[38:46])
                        z = float(line[46:54])
                        res_name = line[17:20]
                        chain = line[21]
                        res_num = line[22:26]
                        
                        # Add N (slightly offset in -Z)
                        lines.append(f"ATOM  {atom_counter:>5} {'N':^4} {res_name} {chain}{res_num}    "
                                    f"{x-0.5:>8.3f}{y:>8.3f}{z-1.5:>8.3f}  1.00 50.00           N\n")
                        atom_counter += 1
                        
                        # Add C (offset in +X)
                        lines.append(f"ATOM  {atom_counter:>5} {'C':^4} {res_name} {chain}{res_num}    "
                                    f"{x+1.5:>8.3f}{y:>8.3f}{z:>8.3f}  1.00 50.00           C\n")
                        atom_counter += 1
                        
                        # Add O (offset in +Y, +Z)
                        lines.append(f"ATOM  {atom_counter:>5} {'O':^4} {res_name} {chain}{res_num}    "
                                    f"{x+1.2:>8.3f}{y+1.2:>8.3f}{z+0.8:>8.3f}  1.00 50.00           O\n")
                        atom_counter += 1
                        
                        # Add CB unless GLY (just duplicate CA position)
                        if res_name != 'GLY':
                            lines.append(f"ATOM  {atom_counter:>5} {'CB':^4} {res_name} {chain}{res_num}    "
                                        f"{x-1.0:>8.3f}{y+1.5:>8.3f}{z:>8.3f}  1.00 50.00           C\n")
                            atom_counter += 1
                    except:
                        pass
    
    lines.append("END\n")
    return "".join(lines)

def main():
    src_dir = Path("predicted_structures_advanced")
    out_dir = Path("predicted_structures")  # Replace directly
    
    pdb_files = sorted(src_dir.glob("*.pdb"))
    print(f"[*] Simple reconstruction for {len(pdb_files)} structures...")
    
    results = {"ok": 0, "failed": 0}
    
    for i, pdb_file in enumerate(pdb_files):
        try:
            new_pdb = simple_reconstruct(pdb_file)
            out_file = out_dir / pdb_file.name
            with open(out_file, 'w') as f:
                f.write(new_pdb)
            results["ok"] += 1
            print(f"[{i+1:3d}/{len(pdb_files)}] {pdb_file.name}")
        except Exception as e:
            results["failed"] += 1
            print(f"[ERR] {pdb_file.name}: {e}")
    
    print(f"\nComplete: {results['ok']} OK, {results['failed']} failed")

if __name__ == "__main__":
    main()
