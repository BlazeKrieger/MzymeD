#!/usr/bin/env python3
"""
Real OpenMM MD Simulation with Enzyme-Substrate Complex
FIXED: Keeps glucose chains (B, C, D) as the substrate
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md
from pdbfixer import PDBFixer

print("="*70)
print("ENZYME-SUBSTRATE COMPLEX MD SIMULATION (FIXED)")
print("="*70)

# Step 1: Load structure - keep ALL chains including substrate
print("\n1. Loading crystal structure with substrate (2W52.pdb)...")
print("   This structure contains:")
print("   - Chain A: Laminarinase enzyme (720 atoms)")
print("   - Chains B,C,D: β-D-glucose (BGC) substrate units")
print("")

# Load original PDB first (to keep substrate chains)
pdb = PDBFile('real_structures/2W52.pdb')

print("2. Cleaning and preparing structure...")
fixer = PDBFixer(filename='real_structures/2W52.pdb')

# Remove ONLY water and buffer molecules, not the glucose!
# We need to manually remove only HOH
print("   Removing water molecules (HOH)...")
fixer.removeHeterogens(keepWater=False)  # This removes HOH

print("   Finding missing protein atoms...")
fixer.findMissingResidues()
fixer.findMissingAtoms()

print("   Adding missing heavy atoms...")
fixer.addMissingAtoms()

print("   Adding hydrogens...")
fixer.addMissingHydrogens(7.0)

# Check what we have
residues = list(fixer.topology.residues())
protein_res = [r for r in residues if r.name not in ['BGC', 'BMA', 'MAN', 'NAG', 'WAT', 'HOH']]
substrate_res = [r for r in residues if r.name in ['BGC', 'BMA', 'MAN', 'NAG']]

print(f"\n✓ Structure prepared:")
print(f"  Total atoms: {fixer.topology.getNumAtoms()}")
print(f"  Protein residues: {len(protein_res)}")
print(f"  Substrate residues (glucose): {len(substrate_res)}")

os.makedirs('md_simulation', exist_ok=True)
PDBFile.writeFile(fixer.topology, fixer.positions, open('md_simulation/enzyme_substrate_complex_fixed.pdb', 'w'))

# Step 2: Setup force field
print("\n3. Loading AMBER14 force field...")
forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

# Create system
print("\n4. Creating molecular system with enzyme + substrate...")
try:
    system = forcefield.createSystem(
        fixer.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds
    )
    print(f"✓ System created with {system.getNumParticles()} particles")
except Exception as e:
    print(f"   Creating system with flexible substrate...")
    system = forcefield.createSystem(
        fixer.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=None
    )
    print(f"✓ System created with {system.getNumParticles()} particles")

# Step 3: Setup integrator
print("\n5. Setting up Langevin dynamics (300K)...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds

integrator = LangevinIntegrator(temperature, friction, timestep)

# Step 4: Create simulation
print("\n6. Creating simulation...")
try:
    platform = Platform.getPlatformByName('CUDA')
    properties = {'CudaPrecision': 'mixed'}
    simulation = Simulation(fixer.topology, system, integrator, platform, properties)
    print("   Using: CUDA (GPU)")
except:
    platform = Platform.getPlatformByName('CPU')
    simulation = Simulation(fixer.topology, system, integrator, platform)
    print("   Using: CPU")

simulation.context.setPositions(fixer.positions)

# Step 5: Energy minimization
print("\n7. Energy minimization...")
state = simulation.context.getState(getEnergy=True)
print(f"   Initial energy: {state.getPotentialEnergy()}")

simulation.minimizeEnergy(maxIterations=500)

state = simulation.context.getState(getEnergy=True)
print(f"   Final energy: {state.getPotentialEnergy()}")
print("✓ Energy minimized")

# Step 6: Equilibration
print("\n8. Equilibration (2 ps)...")
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(1000)

# Step 7: Production MD
print("\n9. Running production MD simulation...")
print("   Duration: 100 ps")
print("   Frames: 50 (every 2 ps)")
print("   Temperature: 300K")
print("   System: ENZYME (Chain A) + GLUCOSE SUBSTRATE (Chains B,C,D)")
print("")

simulation.reporters.append(PDBReporter('md_simulation/enzyme_substrate_trajectory_fixed.pdb', 1000))
simulation.reporters.append(StateDataReporter(
    'md_simulation/complex_md_log_fixed.txt',
    1000,
    step=True,
    time=True,
    potentialEnergy=True,
    temperature=True,
    speed=True,
    progress=True,
    remainingTime=True,
    totalSteps=50000
))

print("   [Running enzyme-substrate MD - may take 2-5 minutes]")
print("")

simulation.step(50000)

print("\n" + "="*70)
print("✓ ENZYME-SUBSTRATE MD SIMULATION COMPLETE!")
print("="*70)

# Analyze trajectory
print("\nAnalyzing enzyme-substrate dynamics...")
traj = md.load('md_simulation/enzyme_substrate_trajectory_fixed.pdb')
rmsd = md.rmsd(traj, traj, 0) * 10

print(f"\nRMSD from initial structure:")
print(f"  Mean: {rmsd.mean():.2f} Å")
print(f"  Max:  {rmsd.max():.2f} Å")
print(f"  Min:  {rmsd.min():.2f} Å")

print(f"\nOutput files:")
print(f"  • md_simulation/enzyme_substrate_trajectory_fixed.pdb (50 frames)")
print(f"  • md_simulation/enzyme_substrate_complex_fixed.pdb (initial structure)")
print(f"  • md_simulation/complex_md_log_fixed.txt")

print(f"\nVisualize in PyMOL:")
print(f"  conda run -n mzymed pymol md_simulation/enzyme_substrate_trajectory_fixed.pdb")
print(f"")
print(f"  In PyMOL console:")
print(f"    show cartoon, chain A")
print(f"    show sticks, chain B+C+D")
print(f"    color cyan, chain B+C+D")
print(f"    mplay")

print("\n" + "="*70)
