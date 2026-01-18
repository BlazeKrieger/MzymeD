#!/usr/bin/env python3
"""
Enzyme-Substrate MD: Simple approach loading full PDB as-is
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md

print("="*70)
print("ENZYME-SUBSTRATE MD (Simple: Full PDB Approach)")
print("="*70)

# Load the full PDB (chains A, B, C, D)
print("\n1. Loading full PDB structure (2W52)...")
pdb = PDBFile('real_structures/2W52.pdb')
print(f"   Total atoms: {pdb.topology.getNumAtoms()}")
print(f"   Chains: {[chain.id for chain in pdb.topology.chains()]}")

# Count atoms per chain
for chain in pdb.topology.chains():
    atom_list = list(chain.atoms())
    residues = list(chain.residues())
    res_names = set(r.name for r in residues)
    print(f"   Chain {chain.id}: {len(atom_list)} atoms, {len(residues)} residues, types: {res_names}")

# Count substrate residues (should be in chains B, C, D)
substrate_count = 0
for chain in pdb.topology.chains():
    if chain.id in ['B', 'C', 'D']:
        for residue in chain.residues():
            substrate_count += 1
print(f"\n   Substrate residues (chains B, C, D): {substrate_count}")

if substrate_count == 0:
    print("   WARNING: No substrate found! Original 2W52 may not have accessible substrate.")
    print("   Proceeding with enzyme-only structure for comparison.")

# Create force field
print("\n2. Creating force field...")
forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

# Create modeller
print("\n3. Setting up system...")
modeller = Modeller(pdb.topology, pdb.positions)

# Add hydrogens
try:
    print("   Adding hydrogens...")
    modeller.addHydrogens(forcefield, addMissingAtoms=True)
except Exception as e:
    print(f"   Warning: {e}")
    print("   Trying without missing atom addition...")
    modeller.addHydrogens(forcefield)

print(f"   Atoms after adding H: {modeller.topology.getNumAtoms()}")

# Create system
print("\n4. Creating OpenMM system...")
try:
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds
    )
except:
    print("   Retrying without H-bond constraints...")
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers
    )

print(f"   System particles: {system.getNumParticles()}")

# Setup integrator
print("\n5. Setting up integrator...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds
integrator = LangevinIntegrator(temperature, friction, timestep)

# Create simulation
print("\n6. Creating simulation...")
try:
    platform = Platform.getPlatformByName('CUDA')
    properties = {'CudaPrecision': 'mixed'}
    simulation = Simulation(modeller.topology, system, integrator, platform, properties)
    print("   Using: CUDA (GPU)")
except:
    platform = Platform.getPlatformByName('CPU')
    simulation = Simulation(modeller.topology, system, integrator, platform)
    print("   Using: CPU")

simulation.context.setPositions(modeller.positions)

# Energy minimization
print("\n7. Energy minimization...")
state = simulation.context.getState(getEnergy=True)
print(f"   Initial energy: {state.getPotentialEnergy()}")

simulation.minimizeEnergy(maxIterations=500)

state = simulation.context.getState(getEnergy=True)
print(f"   Final energy: {state.getPotentialEnergy()}")

# Equilibration
print("\n8. Equilibration (2 ps)...")
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(1000)

# Production run
print("\n9. Running MD (100 ps, 50 frames)...")
os.makedirs('md_simulation', exist_ok=True)
simulation.reporters.append(PDBReporter('md_simulation/enzyme_substrate_trajectory.pdb', 1000))
simulation.reporters.append(StateDataReporter(
    'md_simulation/enzyme_substrate_log.txt',
    1000,
    step=True, time=True, potentialEnergy=True, temperature=True,
    speed=True, progress=True, remainingTime=True, totalSteps=50000
))

simulation.step(50000)

print("\n✓ COMPLETE!")
print("\nOutput files:")
print("  - md_simulation/enzyme_substrate_trajectory.pdb")
print("  - md_simulation/enzyme_substrate_log.txt")
print("\nVisualize:")
print("  pymol md_simulation/enzyme_substrate_trajectory.pdb")
print("  show cartoon, chain A")
print("  show sticks, chain B+C+D")
print("  color cyan, chain B+C+D")
print("  mplay")

# Analyze trajectory
print("\n10. Analyzing trajectory...")
traj = md.load('md_simulation/enzyme_substrate_trajectory.pdb')
print(f"   Trajectory: {traj.n_frames} frames, {traj.n_atoms} atoms")

# RMSD analysis
ca_indices = traj.topology.select('name CA')
rmsd = md.rmsd(traj, traj[0], atom_indices=ca_indices)
print(f"   RMSD: min={rmsd.min():.3f} Å, max={rmsd.max():.3f} Å, mean={rmsd.mean():.3f} Å")

print("\nDone!")
