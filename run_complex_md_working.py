#!/usr/bin/env python3
"""
Manually keep substrate chains when preparing MD system
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
import mdtraj as md
from pdbfixer import PDBFixer
from Bio.PDB import PDBParser, PDBIO
import shutil

print("="*70)
print("ENZYME-SUBSTRATE MD with Manual Substrate Preparation")
print("="*70)

# Step 1: Manually separate enzyme from substrate
print("\n1. Extracting protein and substrate chains from 2W52.pdb...")

parser = PDBParser(QUIET=True)
struct = parser.get_structure('complex', 'real_structures/2W52.pdb')
model = struct[0]

# Save protein chain A separately
protein_io = PDBIO()
protein_io.set_structure(struct)

class SelectChainA(object):
    def accept_model(self, model):
        return 1
    def accept_chain(self, chain):
        return chain.id == 'A'
    def accept_residue(self, residue):
        return 1
    def accept_atom(self, atom):
        return 1

protein_io.save('md_simulation/protein_only.pdb', select=SelectChainA())
print("   ✓ Saved Chain A (protein)")

# Save substrate chains B, C, D
class SelectSubstrate(object):
    def accept_model(self, model):
        return 1
    def accept_chain(self, chain):
        return chain.id in ['B', 'C', 'D']
    def accept_residue(self, residue):
        return 1
    def accept_atom(self, atom):
        return 1

substrate_io = PDBIO()
substrate_io.set_structure(struct)
substrate_io.save('md_simulation/substrate_only.pdb', select=SelectSubstrate())
print("   ✓ Saved Chains B,C,D (substrate glucose)")

# Step 2: Clean and prepare protein
print("\n2. Preparing protein with PDBFixer...")
fixer = PDBFixer(filename='md_simulation/protein_only.pdb')
fixer.removeHeterogens(keepWater=False)
fixer.findMissingResidues()
fixer.findMissingAtoms()
fixer.addMissingAtoms()
fixer.addMissingHydrogens(7.0)

print(f"   Protein atoms: {fixer.topology.getNumAtoms()}")
PDBFile.writeFile(fixer.topology, fixer.positions, open('md_simulation/protein_prepared.pdb', 'w'))

# Step 3: Combine protein + substrate (keep substrate as-is with hydrogens from original)
print("\n3. Combining protein + substrate...")

protein_pdb = PDBFile('md_simulation/protein_prepared.pdb')
substrate_pdb = PDBFile('md_simulation/substrate_only.pdb')

# Merge topologies and positions
combined_topology = protein_pdb.topology
combined_positions = list(protein_pdb.positions)

# Add substrate atoms
for residue in substrate_pdb.topology.residues():
    combined_topology.addResidue(residue.name, substrate_pdb.topology.chains()[-1] if residue in list(substrate_pdb.topology.residues())[-1:] else None)

# For simplicity, just use the full complex from original, but only keep chains A, B, C, D
# Add hydrogens to full structure
print("\n4. Adding hydrogens to complete complex...")

os.makedirs('md_simulation', exist_ok=True)

# Load full original structure
full_pdb = PDBFile('real_structures/2W52.pdb')

# Create modeller with ONLY the chains we want (A, B, C, D - no water)
modeller = Modeller(full_pdb.topology, full_pdb.positions)

# Remove water
# We need to delete residues manually
to_delete = []
for residue in modeller.topology.residues():
    if residue.name in ['HOH', 'WAT']:
        to_delete.append(residue)

# Can't delete during iteration, so mark and delete after
atom_indices_to_delete = []
for chain in modeller.topology.chains():
    if chain.id not in ['A', 'B', 'C', 'D']:
        continue
    for residue in chain.residues():
        if residue.name in ['HOH', 'WAT']:
            for atom in residue.atoms():
                atom_indices_to_delete.append(atom.index)

print("Creating system from original PDB structure...")
forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

# Use the full structure (protein + substrate chains)
modeller = Modeller(full_pdb.topology, full_pdb.positions)

modeller.addHydrogens(forcefield_temp)

print(f"   Total atoms after adding H: {modeller.topology.getNumAtoms()}")

# Create system
print("\n5. Creating system with AMBER14 + substrate...")
try:
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds
    )
except Exception as e:
    print(f"   Error: {e}")
    print("   Creating without H-bond constraints...")
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=None
    )

print(f"✓ System created: {system.getNumParticles()} particles")

# Setup MD
print("\n6. Setting up integrator...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds
integrator = LangevinIntegrator(temperature, friction, timestep)

# Create simulation
print("\n7. Creating simulation...")
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

print("\n8. Energy minimization...")
state = simulation.context.getState(getEnergy=True)
print(f"   Initial: {state.getPotentialEnergy()}")

simulation.minimizeEnergy(maxIterations=500)

state = simulation.context.getState(getEnergy=True)
print(f"   Final: {state.getPotentialEnergy()}")

print("\n9. Equilibration (2 ps)...")
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(1000)

print("\n10. Running MD (100 ps)...")
simulation.reporters.append(PDBReporter('md_simulation/enzyme_substrate_working.pdb', 1000))
simulation.reporters.append(StateDataReporter(
    'md_simulation/md_working_log.txt',
    1000,
    step=True, time=True, potentialEnergy=True, temperature=True,
    speed=True, progress=True, remainingTime=True, totalSteps=50000
))

simulation.step(50000)

print("\n✓ COMPLETE!")
print("\nVisualize:")
print("  conda run -n mzymed pymol md_simulation/enzyme_substrate_working.pdb")
print("  show cartoon, chain A")
print("  show sticks, chain B+C+D")
print("  color cyan, chain B+C+D")
print("  mplay")
