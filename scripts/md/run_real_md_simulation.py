#!/usr/bin/env python3
"""
Real laminarinase-laminarin MD simulation with actual PDB structures.
Downloads complexes from RCSB PDB and runs OpenMM molecular dynamics.
"""

from pathlib import Path
import sys
import urllib.request
import gzip
import shutil
import numpy as np

sys.path.insert(0, "src")
from mzymed.file_handler import FileUploader

# GPU support check
import torch
device = "cuda" if torch.cuda.is_available() else "cpu"


def download_pdb_structure(pdb_id: str, output_dir: Path):
    """Download PDB structure from RCSB."""
    url = f"https://files.rcsb.org/download/{pdb_id}.pdb.gz"
    gz_path = output_dir / f"{pdb_id}.pdb.gz"
    pdb_path = output_dir / f"{pdb_id}.pdb"
    
    if pdb_path.exists():
        print(f"✓ {pdb_id}.pdb already downloaded")
        return pdb_path
    
    print(f"Downloading {pdb_id} from RCSB PDB...")
    try:
        urllib.request.urlretrieve(url, gz_path)
        
        # Decompress
        with gzip.open(gz_path, 'rb') as f_in:
            with open(pdb_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        gz_path.unlink()  # Remove .gz file
        print(f"✓ Downloaded {pdb_id}.pdb")
        return pdb_path
    except Exception as e:
        print(f"✗ Failed to download {pdb_id}: {e}")
        return None


def extract_substrate_from_pdb(pdb_path: Path):
    """Extract laminarin substrate coordinates from PDB."""
    from Bio.PDB import PDBParser
    
    parser = PDBParser(QUIET=True)
    structure = parser.get_structure("complex", pdb_path)
    
    # Look for heteroatoms (substrate/ligand)
    substrate_atoms = []
    enzyme_atoms = []
    
    for model in structure:
        for chain in model:
            for residue in chain:
                hetflag = residue.id[0]
                if hetflag.startswith("H_"):  # Heteroatom (substrate)
                    for atom in residue:
                        substrate_atoms.append({
                            'name': atom.name,
                            'coord': atom.coord,
                            'residue': residue.resname
                        })
                elif hetflag == " ":  # Protein (enzyme)
                    for atom in residue:
                        if atom.name == "CA":  # Alpha carbon only
                            enzyme_atoms.append({
                                'name': atom.name,
                                'coord': atom.coord,
                                'residue': residue.resname,
                                'res_id': residue.id[1]
                            })
    
    return enzyme_atoms, substrate_atoms


def identify_interaction_sites(enzyme_atoms, substrate_atoms, distance_cutoff=5.0):
    """Identify enzyme residues interacting with substrate."""
    interactions = []
    
    if not substrate_atoms:
        print("⚠️  No substrate atoms found")
        return interactions
    
    # Calculate distances
    for enz_atom in enzyme_atoms:
        enz_coord = enz_atom['coord']
        
        for sub_atom in substrate_atoms:
            sub_coord = sub_atom['coord']
            distance = np.linalg.norm(enz_coord - sub_coord)
            
            if distance < distance_cutoff:
                interactions.append({
                    'enzyme_residue': enz_atom['residue'],
                    'enzyme_res_id': enz_atom['res_id'],
                    'distance': distance,
                    'substrate_residue': sub_atom['residue']
                })
                break  # One interaction per enzyme residue
    
    return interactions


def run_openmm_simulation(pdb_path: Path, num_steps=1000):
    """Run OpenMM molecular dynamics simulation."""
    try:
        import openmm as mm
        from openmm.app import PDBFile, ForceField, Simulation, StateDataReporter
        from openmm import LangevinIntegrator, Platform
        from openmm import unit
        
        print("\n📊 Setting up OpenMM simulation...")
        
        # Load structure
        pdb = PDBFile(str(pdb_path))
        
        # Select force field
        forcefield = ForceField('amber14-all.xml', 'amber14/tip3pfb.xml')
        
        # Create system
        print("  Creating molecular system...")
        system = forcefield.createSystem(
            pdb.topology,
            nonbondedMethod=mm.app.NoCutoff,
            constraints=mm.app.HBonds
        )
        
        # Set up integrator
        integrator = LangevinIntegrator(
            300*unit.kelvin,  # Temperature
            1/unit.picosecond,  # Friction coefficient
            0.002*unit.picoseconds  # Time step
        )
        
        # Try to use GPU if available
        try:
            if device == "cuda":
                platform = Platform.getPlatformByName('CUDA')
                print(f"  ✓ Using CUDA GPU acceleration")
            else:
                platform = Platform.getPlatformByName('CPU')
                print(f"  ✓ Using CPU")
        except:
            platform = Platform.getPlatformByName('CPU')
            print(f"  ⚠️  GPU unavailable, using CPU")
        
        # Create simulation
        simulation = Simulation(pdb.topology, system, integrator, platform)
        simulation.context.setPositions(pdb.positions)
        
        # Minimize energy
        print("  Minimizing energy...")
        simulation.minimizeEnergy()
        
        # Run MD
        print(f"  Running {num_steps} MD steps...")
        simulation.step(num_steps)
        
        # Get final state
        state = simulation.context.getState(getPositions=True, getEnergy=True)
        potential_energy = state.getPotentialEnergy()
        
        print(f"  ✓ Simulation complete")
        print(f"  Final potential energy: {potential_energy}")
        
        return {
            'energy': potential_energy,
            'positions': state.getPositions(asNumpy=True),
            'success': True
        }
        
    except Exception as e:
        print(f"  ✗ OpenMM simulation failed: {e}")
        print(f"     (This is OK - will use structure analysis only)")
        return {'success': False, 'error': str(e)}


def main():
    print("=" * 80)
    print("REAL LAMINARINASE-LAMINARIN MD SIMULATION")
    print("=" * 80)
    
    base = Path(__file__).parent
    pdb_dir = base / "real_structures"
    pdb_dir.mkdir(exist_ok=True)
    
    # PDB structures with laminarinase-laminarin complexes
    pdb_structures = {
        '2W52': 'Laminarinase 16A + 6-O-glucosyl-laminaritriose (1.56Å)',
        '2W39': 'Laminarinase 16A + disaccharide (1.1Å)',
        '4BPZ': 'LamA + laminaritriose complex (1.13Å)',
        '4BOW': 'LamA + laminaritriose/tetraose (1.35Å)',
    }
    
    print(f"\n🖥️  Device: {device.upper()}")
    if device == "cuda":
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    
    print(f"\n📥 Downloading {len(pdb_structures)} enzyme-substrate complex structures...")
    
    for pdb_id, description in pdb_structures.items():
        print(f"\n{'─'*80}")
        print(f"Structure: {pdb_id} - {description}")
        print(f"{'─'*80}")
        
        # Download PDB
        pdb_path = download_pdb_structure(pdb_id, pdb_dir)
        if not pdb_path:
            continue
        
        # Extract enzyme and substrate
        print("\n🔬 Analyzing structure...")
        enzyme_atoms, substrate_atoms = extract_substrate_from_pdb(pdb_path)
        
        print(f"  ✓ Enzyme atoms (CA): {len(enzyme_atoms)}")
        print(f"  ✓ Substrate atoms: {len(substrate_atoms)}")
        
        # Identify interactions
        interactions = identify_interaction_sites(enzyme_atoms, substrate_atoms)
        
        print(f"\n🎯 INTERACTION SITES (within 5Å):")
        if interactions:
            unique_residues = {}
            for inter in interactions:
                res_key = f"{inter['enzyme_residue']}{inter['enzyme_res_id']}"
                if res_key not in unique_residues:
                    unique_residues[res_key] = inter['distance']
            
            print(f"  Found {len(unique_residues)} enzyme residues near substrate:")
            sorted_residues = sorted(unique_residues.items(), key=lambda x: x[1])
            for res, dist in sorted_residues[:20]:  # Top 20
                print(f"    • {res:8s} - {dist:.2f} Å")
        else:
            print("  ⚠️  No interactions found (structure may lack substrate)")
        
        # Run MD simulation
        md_result = run_openmm_simulation(pdb_path, num_steps=100)
        
        if md_result['success']:
            print(f"\n✅ MD Simulation successful!")
            print(f"   Energy: {md_result['energy']}")
        else:
            print(f"\n⚠️  MD simulation skipped (analysis only)")
    
    print(f"\n{'='*80}")
    print("✅ ANALYSIS COMPLETE")
    print(f"{'='*80}")
    print(f"\n📂 Real PDB structures saved to: {pdb_dir}/")
    print(f"   - 2W52.pdb: Laminarinase 16A with substrate (high resolution)")
    print(f"   - 4BPZ.pdb: LamA with laminaritriose")
    print(f"   - 4BOW.pdb: LamA with oligosaccharides")
    print(f"\n💡 These structures show real enzyme-substrate interactions!")
    print(f"   Open them in PyMOL to see binding site details.")


if __name__ == "__main__":
    main()
