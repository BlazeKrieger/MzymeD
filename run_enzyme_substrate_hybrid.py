#!/usr/bin/env python3
"""
Enzyme-Substrate MD: Clean protein then add back substrate manually
"""

import os
os.environ['OPENMM_CPU_THREADS'] = '8'

from openmm.app import *
from openmm import *
from openmm.unit import *
from pdbfixer import PDBFixer
import mdtraj as md
from Bio.PDB import PDBParser, PDBIO, Select

print("="*70)
print("ENZYME-SUBSTRATE MD: Hybrid Approach")
print("="*70)

# Step 1: Clean protein chain A with PDBFixer
print("\n1. Cleaning Chain A (protein) with PDBFixer...")
fixer = PDBFixer(filename='real_structures/2W52.pdb')
fixer.removeHeterogens(keepWater=False)
fixer.findNonstandardResidues()
fixer.replaceNonstandardResidues()

PDBFile.writeFile(fixer.topology, fixer.positions, open('md_simulation/protein_only_cleaned.pdb', 'w'))
print("   ✓ Cleaned protein saved")

# Step 2: Extract substrate chains from original PDB
print("\n2. Extracting substrate chains (B, C, D) from original...")
parser = PDBParser(QUIET=True)
struct = parser.get_structure('2W52', 'real_structures/2W52.pdb')
model = struct[0]

class SelectSubstrate(Select):
    def accept_chain(self, chain):
        return chain.id in ['B', 'C', 'D']
    def accept_residue(self, residue):
        return 1
    def accept_atom(self, atom):
        return 1

io = PDBIO()
io.set_structure(struct)
io.save('md_simulation/substrate_only.pdb', select=SelectSubstrate())
print("   ✓ Substrate extracted")

# Step 3: Combine protein and substrate
print("\n3. Combining protein + substrate...")

# Read cleaned protein
with open('md_simulation/protein_only_cleaned.pdb', 'r') as f:
    protein_lines = f.readlines()

# Read substrate
with open('md_simulation/substrate_only.pdb', 'r') as f:
    substrate_lines = f.readlines()

# Filter: keep ATOM/HETATM lines
protein_atoms = [l for l in protein_lines if l.startswith(('ATOM', 'HETATM'))]
substrate_atoms = [l for l in substrate_lines if l.startswith(('ATOM', 'HETATM'))]

# Renumber substrate atoms
protein_count = len(protein_atoms)
renumbered_substrate = []
for i, line in enumerate(substrate_atoms):
    # Renumber atom index
    atom_num = protein_count + i + 1
    new_line = line[:6] + f'{atom_num:5d}' + line[11:]
    renumbered_substrate.append(new_line)

# Write combined PDB
with open('md_simulation/complex_combined.pdb', 'w') as f:
    # Write header
    f.write("REMARK   Combined Enzyme-Substrate Complex\n")
    # Write protein atoms
    f.writelines(protein_atoms)
    # Write substrate atoms
    f.writelines(renumbered_substrate)
    # Write end
    f.write("END\n")

print(f"   ✓ Combined: {len(protein_atoms)} protein atoms + {len(substrate_atoms)} substrate atoms")

# Step 4: Load combined structure
print("\n4. Loading combined structure...")
pdb = PDBFile('md_simulation/complex_combined.pdb')

total_atoms = pdb.topology.getNumAtoms()
print(f"   Total atoms: {total_atoms}")

# Count chains
chain_count = {}
for chain in pdb.topology.chains():
    chain_atoms = list(chain.atoms())
    chain_count[chain.id] = len(chain_atoms)

print(f"   Chains: {chain_count}")

# Step 5: Create system
print("\n5. Creating OpenMM system...")
forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')

modeller = Modeller(pdb.topology, pdb.positions)

# Simplest approach: don't add hydrogens to heterogens, let FF handle it
try:
    print("   Adding hydrogens to protein only...")
    # Create a forcefield just to add H to protein chain
    ff_simple = ForceField('amber14-all.xml')
    modeller.addHydrogens(ff_simple)
except Exception as e:
    print(f"   Skipping H addition: {e}")

print(f"   Atoms after prep: {modeller.topology.getNumAtoms()}")

# Create system
try:
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers,
        constraints=HBonds
    )
except Exception as e:
    print(f"   Error with constraints: {e}")
    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0*nanometers
    )

print(f"   System particles: {system.getNumParticles()}")

# Step 6: Run MD
print("\n6. Setting up MD...")
temperature = 300*kelvin
friction = 1.0/picosecond
timestep = 2.0*femtoseconds
integrator = LangevinIntegrator(temperature, friction, timestep)

# Create simulation
try:
    platform = Platform.getPlatformByName('CUDA')
    properties = {'CudaPrecision': 'mixed'}
    simulation = Simulation(modeller.topology, system, integrator, platform, properties)
    print("   Platform: CUDA (GPU)")
except:
    platform = Platform.getPlatformByName('CPU')
    simulation = Simulation(modeller.topology, system, integrator, platform)
    print("   Platform: CPU")

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

# Production MD
print("\n9. Production MD (100 ps, 50 frames)...")
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
print("  - md_simulation/complex_combined.pdb")

# Trajectory analysis
print("\n10. Analyzing trajectory...")
traj = md.load('md_simulation/enzyme_substrate_trajectory.pdb')
print(f"   Frames: {traj.n_frames}, Atoms: {traj.n_atoms}")

# RMSD
ca_indices = traj.topology.select('name CA')
if len(ca_indices) > 0:
    rmsd = md.rmsd(traj, traj[0], atom_indices=ca_indices)
    print(f"   Protein RMSD: min={rmsd.min():.3f} Å, max={rmsd.max():.3f} Å, mean={rmsd.mean():.3f} Å")

print("\nVisualize:")
print("  pymol md_simulation/enzyme_substrate_trajectory.pdb")
print("  show cartoon, chain A")
print("  show sticks, chain B+C+D")
print("  color cyan, chain B+C+D")
print("  mplay")
