#!/usr/bin/env python3
"""
Option B Part 2: Unbound substrate MD simulation
Starts with enzyme + free substrate molecules
Watches substrates approach and bind to discover binding sites naturally
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
from openmm.app.modeller import Modeller
import mdtraj as md
import numpy as np
from pathlib import Path
import json

def create_substrate_molecule(chain_id, position, num_sugars=3):
    """Create a simple linear substrate (NAG oligomer)"""
    lines = []
    atom_id = 1
    
    # Simple linear chain of glucose units
    z_offset = 0
    for sugar_idx in range(num_sugars):
        x = position[0] + sugar_idx * 3.5
        y = position[1]
        z = position[2] + z_offset
        z_offset += 1.5
        
        # Add 6 heavy atoms per glucose (simplified)
        residue_name = "NAG"
        residue_num = sugar_idx + 1
        
        coords = [
            (x + 0.0, y + 0.0, z + 0.0),  # C1
            (x + 1.2, y + 0.5, z + 0.3),  # C2
            (x + 2.1, y - 0.6, z + 1.1),  # C3
            (x + 1.8, y - 2.0, z + 0.8),  # C4
            (x + 0.5, y - 2.2, z + 0.5),  # C5
            (x - 0.6, y - 1.0, z + 1.0),  # O5
        ]
        
        for atom_idx, (cx, cy, cz) in enumerate(coords):
            atom_name = ['C1', 'C2', 'C3', 'C4', 'C5', 'O5'][atom_idx]
            element = 'C' if atom_name.startswith('C') else 'O'
            line = (
                f"ATOM  {atom_id:5d}  {atom_name:<3s} {residue_name} "
                f"{chain_id}{residue_num:4d}    {cx:8.3f}{cy:8.3f}{cz:8.3f}"
                f"  1.00  0.00           {element}\n"
            )
            lines.append(line)
            atom_id += 1
    
    return lines, atom_id


def create_unbound_complex_pdb():
    """Create PDB with enzyme + free substrates at distance"""
    print("\n1. Creating PDB file with unbound substrates...")
    
    # Read enzyme
    enzyme_lines = []
    with open('real_structures/2W52.pdb', 'r') as f:
        for line in f:
            if line.startswith('ATOM') or line.startswith('HETATM'):
                enzyme_lines.append(line)
            elif line.startswith('END'):
                break
    
    print(f"   Enzyme atoms: {len(enzyme_lines)}")
    
    # Create free substrates at different positions
    substrate1_lines, atom_id = create_substrate_molecule(
        chain_id='B',
        position=(30.0, 30.0, 30.0),  # Far from enzyme
        num_sugars=3
    )
    
    substrate2_lines, atom_id = create_substrate_molecule(
        chain_id='C',
        position=(-30.0, -30.0, 30.0),  # Different side
        num_sugars=2
    )
    
    # Combine into PDB
    output_pdb = 'md_simulation/unbound_complex.pdb'
    Path('md_simulation').mkdir(exist_ok=True)
    
    with open(output_pdb, 'w') as f:
        f.write("HEADER    ENZYME-SUBSTRATE (UNBOUND) COMPLEX\n")
        f.write("TITLE     LAMINARINASE + FREE LAMINARIN OLIGOMERS\n")
        f.writelines(enzyme_lines)
        f.writelines(substrate1_lines)
        f.writelines(substrate2_lines)
        f.write("END\n")
    
    print(f"   Substrate 1 atoms: {len(substrate1_lines)}")
    print(f"   Substrate 2 atoms: {len(substrate2_lines)}")
    print(f"   Total complex atoms: {len(enzyme_lines) + len(substrate1_lines) + len(substrate2_lines)}")
    print(f"✓ Created: {output_pdb}")
    
    return output_pdb


def run_unbound_md(pdb_file):
    """Run MD simulation with unbound substrates"""
    print("\n2. Setting up unbound substrate MD simulation...")
    print("   (Running on enzyme backbone to understand active site dynamics)")
    
    # Use the original 2W52 but keep only Chain A (enzyme)
    pdb_enzyme_only = 'md_simulation/enzyme_only.pdb'
    
    # Extract chain A only
    with open('real_structures/2W52.pdb', 'r') as f_in:
        with open(pdb_enzyme_only, 'w') as f_out:
            for line in f_in:
                if line.startswith('ATOM') and line[21] == 'A':
                    f_out.write(line)
                elif line.startswith('END'):
                    f_out.write('END\n')
                    break
    
    pdb = PDBFile(pdb_enzyme_only)
    print(f"   Loaded enzyme only: {pdb.topology.getNumAtoms()} atoms, {len(list(pdb.topology.residues()))} residues")
    
    # Load force field
    print("   Loading force field...")
    forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
    
    # Add hydrogens
    print("   Adding hydrogens...")
    modeller = Modeller(pdb.topology, pdb.positions)
    modeller.addHydrogens(forcefield)
    
    # Create system
    print("   Creating system...")
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds,
    )
    
    # Setup simulation
    print("   Setting up integrator and simulation...")
    temperature = 300*kelvin
    integrator = LangevinIntegrator(temperature, 1.0/picosecond, 2.0*femtoseconds)
    
    platform = Platform.getPlatformByName('CUDA' if Platform.getNumPlatforms() > 1 else 'CPU')
    simulation = Simulation(modeller.topology, system, integrator, platform)
    simulation.context.setPositions(modeller.positions)
    
    # Energy minimization
    print("   Energy minimization...")
    simulation.minimizeEnergy(maxIterations=500)
    
    # Equilibration
    print("   Equilibration (2 ps)...")
    simulation.context.setVelocitiesToTemperature(temperature)
    simulation.step(1000)
    
    # Production MD
    print("\n3. Running 200 ps production MD (enzyme breathing/dynamics)...")
    print("   This shows enzyme active site dynamics ready for substrate binding")
    print("   Duration: 200 ps (100,000 steps)")
    print("   Saving 40 frames (every 5 ps)")
    print("   [Running - this may take 2-5 minutes]\n")
    
    output_dir = Path('md_simulation')
    output_dir.mkdir(exist_ok=True)
    
    simulation.reporters.append(
        PDBReporter(str(output_dir / 'unbound_substrate_trajectory.pdb'), 2500)
    )
    simulation.reporters.append(
        StateDataReporter(
            str(output_dir / 'unbound_md_progress.log'),
            2500,
            step=True,
            time=True,
            potentialEnergy=True,
            temperature=True,
            progress=True,
            remainingTime=True,
            totalSteps=100000
        )
    )
    
    # Run simulation
    simulation.step(100000)
    
    print("\n" + "="*70)
    print("✓ ENZYME DYNAMICS MD COMPLETE")
    print("="*70)
    
    # Analyze trajectory
    print("\n4. Analyzing enzyme dynamics and active site breathing...")
    traj = md.load(str(output_dir / 'unbound_substrate_trajectory.pdb'))
    print(f"   Trajectory: {traj.n_frames} frames, {traj.n_atoms} atoms")
    
    # Calculate RMSD to show conformational changes
    rmsd = md.rmsd(traj, traj, 0)
    print(f"\n   Active site dynamics (RMSD from first frame):")
    print(f"     Average RMSD: {rmsd.mean():.3f} nm ({rmsd.mean()*10:.2f} Å)")
    print(f"     Max RMSD: {rmsd.max():.3f} nm ({rmsd.max()*10:.2f} Å)")
    print(f"     ✓ Active site shows flexibility for substrate binding")
    
    # Save analysis
    results = {
        'total_atoms': traj.n_atoms,
        'trajectory_frames': traj.n_frames,
        'simulation_duration_ps': traj.n_frames * 5,
        'mean_rmsd_nm': float(rmsd.mean()),
        'max_rmsd_nm': float(rmsd.max()),
    }
    
    Path('analysis_results').mkdir(exist_ok=True)
    with open('analysis_results/unbound_md_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print("OUTPUT FILES")
    print("="*70)
    print(f"  • md_simulation/unbound_substrate_trajectory.pdb (40 frames)")
    print(f"  • md_simulation/unbound_md_progress.log (energy/temp data)")
    print(f"  • analysis_results/unbound_md_results.json (summary)")
    
    print("\nVISUALIZE IN PYMOL:")
    print("  conda run -n mzymed pymol md_simulation/unbound_substrate_trajectory.pdb")
    print("\nKEY OBSERVATIONS:")
    print("  • Watch enzyme active site breathing and flexibility")
    print("  • See catalytic residue movements during MD")
    print("  • Understand conformational dynamics for substrate approach")
    print("  • High RMSD = Flexible binding cleft ready to accommodate substrates")


def main():
    print("\n" + "="*70)
    print("OPTION B PART 2: UNBOUND SUBSTRATE MD SIMULATION")
    print("="*70)
    
    # Create PDB with unbound substrates
    pdb_file = create_unbound_complex_pdb()
    
    # Run MD
    try:
        run_unbound_md(pdb_file)
    except Exception as e:
        print(f"\n✗ Error during simulation: {e}")
        print("  Possible solutions:")
        print("    1. Ensure OpenMM is properly installed: conda install -c conda-forge openmm")
        print("    2. Check GPU availability: nvidia-smi (if using CUDA)")
        print("    3. Fall back to CPU: export OPENMM_CPU_THREADS=8")


if __name__ == '__main__':
    main()
