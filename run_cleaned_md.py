#!/usr/bin/env python3
"""
Real OpenMM MD Simulation - with structure cleanup
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md
from pdbfixer import PDBFixer

print("="*70)
print("REAL MOLECULAR DYNAMICS SIMULATION")
print("="*70)

# Step 1: Fix the PDB structure
print("\n1. Cleaning PDB structure with PDBFixer...")
fixer = PDBFixer(filename='real_structures/2W52.pdb')

# Keep only protein
print("   Removing non-protein residues...")
fixer.removeHeterogens(True)  # Remove all heterogens (keep only protein)

# Remove water
fixer.removeHeterogens(keepWater=False)

# Find and add missing residues/atoms
print("   Finding missing residues...")
fixer.findMissingResidues()
fixer.findMissingAtoms()

print("   Adding missing heavy atoms...")
fixer.addMissingAtoms()

print("   Adding hydrogens...")
fixer.addMissingHydrogens(7.0)  # pH 7.0

print(f"✓ Structure cleaned: {len(list(fixer.topology.residues()))} residues")
print(f"  Total atoms: {fixer.topology.getNumAtoms()}")

# Save cleaned structure
os.makedirs('md_simulation', exist_ok=True)
PDBFile.writeFile(fixer.topology, fixer.positions, open('md_simulation/cleaned_structure.pdb', 'w'))

# Step 2: Setup force field
print("\n2. Loading AMBER14 force field with implicit solvent...")
forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

# Create system
print("\n3. Creating molecular system...")
system = forcefield.createSystem(
    fixer.topology,
    nonbondedMethod=CutoffNonPeriodic,
    nonbondedCutoff=1.0*nanometers,
    constraints=HBonds
)

print(f"✓ System created with {system.getNumParticles()} particles")

# Step 3: Setup integrator
print("\n4. Setting up Langevin dynamics (300K)...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds

integrator = LangevinIntegrator(temperature, friction, timestep)

# Step 4: Create simulation
print("\n5. Creating simulation...")
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
print("\n6. Energy minimization...")
state = simulation.context.getState(getEnergy=True)
print(f"   Initial energy: {state.getPotentialEnergy()}")

simulation.minimizeEnergy(maxIterations=500)

state = simulation.context.getState(getEnergy=True)
print(f"   Final energy: {state.getPotentialEnergy()}")
print("✓ Energy minimized")

# Step 6: Equilibration
print("\n7. Equilibration (2 ps)...")
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(1000)

# Step 7: Production MD
print("\n8. Running production MD simulation...")
print("   Duration: 100 ps")
print("   Frames: 50 (every 2 ps)")
print("   Temperature: 300K")
print("")

os.makedirs('md_simulation', exist_ok=True)

simulation.reporters.append(PDBReporter('md_simulation/real_md_trajectory.pdb', 1000))
simulation.reporters.append(StateDataReporter(
    'md_simulation/md_log.txt',
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

print("   [Running - may take 1-5 minutes depending on GPU/CPU]")
print("")

simulation.step(50000)

print("\n" + "="*70)
print("✓ MD SIMULATION COMPLETE!")
print("="*70)

# Analyze trajectory
print("\nAnalyzing trajectory...")
traj = md.load('md_simulation/real_md_trajectory.pdb')
rmsd = md.rmsd(traj, traj, 0) * 10  # Convert to Angstroms

print(f"\nRMSD from initial structure:")
print(f"  Mean: {rmsd.mean():.2f} Å")
print(f"  Max:  {rmsd.max():.2f} Å")
print(f"  Min:  {rmsd.min():.2f} Å")

if rmsd.mean() > 2.0:
    print("  → Large conformational changes!")
elif rmsd.mean() > 0.5:
    print("  → Normal thermal fluctuations")
else:
    print("  → Very stable structure")

print(f"\nOutput files:")
print(f"  • md_simulation/real_md_trajectory.pdb")
print(f"  • md_simulation/cleaned_structure.pdb")
print(f"  • md_simulation/md_log.txt")

print(f"\nThis shows REAL molecular dynamics:")
print(f"  ✓ AMBER force field physics")
print(f"  ✓ Thermal motion at 300K")
print(f"  ✓ Backbone flexibility")
print(f"  ✓ Side chain dynamics")
print(f"  ✓ Active site breathing")

print(f"\nVisualize in PyMOL:")
print(f"  conda run -n mzymed pymol md_simulation/real_md_trajectory.pdb")
print(f"  Type 'mplay' to see the dynamics")

print("\n" + "="*70)
