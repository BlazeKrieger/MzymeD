#!/usr/bin/env python3
"""
Enzyme-Substrate MD: Use PDBFixer on combined structure
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
from pdbfixer import PDBFixer
import mdtraj as md

print("="*70)
print("ENZYME-SUBSTRATE MD: Fixed PDBFixer Approach")
print("="*70)

# Step 1: Extract just chains B, C, D from original
print("\n1. Preparing files...")
from Bio.PDB import PDBParser, PDBIO, Select

parser = PDBParser(QUIET=True)
struct = parser.get_structure('2W52', 'real_structures/2W52.pdb')

class SelectSubstrate(Select):
    def accept_chain(self, chain):
        return chain.id in ['B', 'C', 'D']

class SelectProtein(Select):
    def accept_chain(self, chain):
        return chain.id == 'A'

# Save just protein A
io = PDBIO()
io.set_structure(struct)
io.save('md_simulation/protein_A.pdb', select=SelectProtein())
print("   ✓ Extracted Chain A")

# Save just substrate BCD
io.save('md_simulation/substrate_BCD.pdb', select=SelectSubstrate())
print("   ✓ Extracted Chains BCD")

# Step 2: Fix protein with PDBFixer
print("\n2. Cleaning protein with PDBFixer...")
fixer = PDBFixer('md_simulation/protein_A.pdb')
fixer.removeHeterogens(keepWater=False)
fixer.findNonstandardResidues()
fixer.replaceNonstandardResidues()

# Write fixed protein
from openmm.app import PDBFile
PDBFile.writeFile(fixer.topology, fixer.positions, open('md_simulation/protein_A_fixed.pdb', 'w'))
print(f"   ✓ Fixed protein ({fixer.topology.getNumAtoms()} atoms)")

# Step 3: Load fixed protein and add hydrogens
print("\n3. Loading fixed protein and adding hydrogens...")
pdb_protein = PDBFile('md_simulation/protein_A_fixed.pdb')
forcefield = ForceField('amber14-all.xml')
modeller = Modeller(pdb_protein.topology, pdb_protein.positions)
modeller.addHydrogens(forcefield)

PDBFile.writeFile(modeller.topology, modeller.positions, open('md_simulation/protein_A_H.pdb', 'w'))
print(f"   ✓ Protein with hydrogens ({modeller.topology.getNumAtoms()} atoms)")

# Step 4: Combine with substrate
print("\n4. Combining protein + substrate...")

# Read PDB files
with open('md_simulation/protein_A_H.pdb', 'r') as f:
    protein_lines = f.readlines()

with open('md_simulation/substrate_BCD.pdb', 'r') as f:
    substrate_lines = f.readlines()

# Extract ATOM/HETATM lines
protein_atoms = [l for l in protein_lines if l.startswith(('ATOM  ', 'HETATM'))]
substrate_atoms = [l for l in substrate_lines if l.startswith(('ATOM  ', 'HETATM'))]

print(f"   Protein atoms: {len(protein_atoms)}")
print(f"   Substrate atoms: {len(substrate_atoms)}")

# Renumber all atoms and write combined
combined = []
protein_count = len(protein_atoms)

# Add protein atoms
for i, line in enumerate(protein_atoms):
    atom_num = i + 1
    # Standard PDB format: columns 6-11 are the atom number
    new_line = line[:6] + f'{atom_num:5d}' + line[11:]
    combined.append(new_line)

# Add substrate atoms (with new chain identifiers and renumbering)
for i, line in enumerate(substrate_atoms):
    atom_num = protein_count + i + 1
    new_line = line[:6] + f'{atom_num:5d}' + line[11:]
    combined.append(new_line)

# Write combined PDB
os.makedirs('md_simulation', exist_ok=True)
with open('md_simulation/complex_enzyme_substrate.pdb', 'w') as f:
    f.write("REMARK Enzyme-Substrate Complex (Protein + Glucose)\n")
    f.writelines(combined)
    f.write("END\n")

print(f"   ✓ Combined: {protein_count} protein + {len(substrate_atoms)} substrate = {protein_count + len(substrate_atoms)} total")

# Step 5: Load combined and create system
print("\n5. Loading combined structure...")
pdb = PDBFile('md_simulation/complex_enzyme_substrate.pdb')
print(f"   Total atoms: {pdb.topology.getNumAtoms()}")

# Count chains
for chain in pdb.topology.chains():
    atoms = list(chain.atoms())
    print(f"   Chain {chain.id}: {len(atoms)} atoms")

# Step 6: Create MD system
print("\n6. Creating OpenMM system...")
forcefield_ff = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

modeller_complex = Modeller(pdb.topology, pdb.positions)

# Create system
try:
    system = forcefield_ff.createSystem(
        modeller_complex.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds
    )
    print("   ✓ System created with HBonds constraints")
except Exception as e:
    print(f"   Retrying without constraints: {e}")
    system = forcefield_ff.createSystem(
        modeller_complex.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers
    )
    print("   ✓ System created without constraints")

print(f"   Particles: {system.getNumParticles()}")

# Step 7: Setup integrator
print("\n7. Setting up MD...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds
integrator = LangevinIntegrator(temperature, friction, timestep)

# Create simulation
try:
    platform = Platform.getPlatformByName('CUDA')
    properties = {'CudaPrecision': 'mixed'}
    simulation = Simulation(modeller_complex.topology, system, integrator, platform, properties)
    print("   Platform: CUDA (GPU)")
except:
    platform = Platform.getPlatformByName('CPU')
    simulation = Simulation(modeller_complex.topology, system, integrator, platform)
    print("   Platform: CPU")

simulation.context.setPositions(modeller_complex.positions)

# Step 8: Energy minimization
print("\n8. Energy minimization...")
state = simulation.context.getState(getEnergy=True)
print(f"   Initial energy: {state.getPotentialEnergy()}")

simulation.minimizeEnergy(maxIterations=500)

state = simulation.context.getState(getEnergy=True)
print(f"   Final energy: {state.getPotentialEnergy()}")

# Step 9: Equilibration
print("\n9. Equilibration (2 ps)...")
simulation.context.setVelocitiesToTemperature(temperature)
simulation.step(1000)

# Step 10: Production MD
print("\n10. Production MD (100 ps, 50 frames)...")
simulation.reporters.append(PDBReporter('md_simulation/enzyme_substrate_trajectory.pdb', 1000))
simulation.reporters.append(StateDataReporter(
    'md_simulation/enzyme_substrate_log.txt',
    1000,
    step=True, time=True, potentialEnergy=True, temperature=True,
    speed=True, progress=True, remainingTime=True, totalSteps=50000
))

simulation.step(50000)

print("\n" + "="*70)
print("✓ COMPLETE!")
print("="*70)
print("\nOutput files:")
print("  - md_simulation/enzyme_substrate_trajectory.pdb")
print("  - md_simulation/enzyme_substrate_log.txt")
print("  - md_simulation/complex_enzyme_substrate.pdb (initial structure)")

# Analyze trajectory
print("\n11. Analyzing trajectory...")
traj = md.load('md_simulation/enzyme_substrate_trajectory.pdb')
print(f"   Trajectory: {traj.n_frames} frames, {traj.n_atoms} atoms")

ca_indices = traj.topology.select('name CA')
if len(ca_indices) > 0:
    rmsd = md.rmsd(traj, traj[0], atom_indices=ca_indices)
    print(f"   Protein RMSD: min={rmsd.min():.3f} Å, max={rmsd.max():.3f} Å, mean={rmsd.mean():.3f} Å")

print("\nVisualization (PyMOL):")
print("  pymol md_simulation/enzyme_substrate_trajectory.pdb")
print("  show cartoon, chain A")
print("  show sticks, chain B+C+D")
print("  color cyan, chain B+C+D")
print("  color red, resi 107")
print("  color orange, resi 256")
print("  color yellow, resi 257")
print("  mplay")
