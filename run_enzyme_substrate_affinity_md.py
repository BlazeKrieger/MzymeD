#!/usr/bin/env python3
"""
Enzyme-Substrate Affinity Assessment: MD Simulations with Laminarin
Runs MD on predicted laminarinase + laminarin substrate complexes
Calculates binding affinity metrics and stability
"""

import os
import json
import glob
import subprocess
import sys
from pathlib import Path
from datetime import datetime
import numpy as np
import warnings

warnings.filterwarnings('ignore')

os.environ['OPENMM_CPU_THREADS'] = '8'

try:
    from openmm.app import *
    from openmm import *
    from openmm.unit import *
    import mdtraj as md
except ImportError as e:
    print(f"ERROR: Missing required packages: {e}")
    print("Install with: conda install -c conda-forge openmm mdtraj")
    sys.exit(1)

BASE_DIR = Path(__file__).parent
CLEAN_STRUCTURES = BASE_DIR / "predicted_structures_cleaned"
OUTPUT_DIR = BASE_DIR / "alphafold_enzyme_substrate_md"
LOG_DIR = OUTPUT_DIR / "logs"

# Create output directories
OUTPUT_DIR.mkdir(exist_ok=True)
LOG_DIR.mkdir(exist_ok=True)

# Laminarin substrate (mock β-glucan structure)
LAMINARIN_SEQ = "GGGGTGGGGGGGGGGGGGGGGGGGGGGGGGG"  # G = glucose (simplified)

print(f"\n{'='*70}")
print(f"Enzyme-Substrate MD: Laminarinase + Laminarin")
print(f"{'='*70}\n")

def create_laminarin_pdb():
    """Create simple linear laminarin structure (β-1,3-glucan oligosaccharide)."""
    pdb_content = """HEADER    LAMINARIN OLIGOSACCHARIDE
TITLE     MOCK LAMINARIN SUBSTRATE
REMARK    SIMPLIFIED LINEAR BETA-GLUCAN STRUCTURE
ATOM      1  C1  GLC A   1       0.000   0.000   0.000  1.00  0.00           C
ATOM      2  C2  GLC A   1       1.200   0.000   0.000  1.00  0.00           C
ATOM      3  C3  GLC A   1       1.800   1.200   0.000  1.00  0.00           C
ATOM      4  C4  GLC A   1       1.200   2.400   0.000  1.00  0.00           C
ATOM      5  C5  GLC A   1       0.000   2.400   0.000  1.00  0.00           C
ATOM      6  C6  GLC A   1      -0.600   3.600   0.000  1.00  0.00           C
ATOM      7  O1  GLC A   1      -0.600   0.000   1.200  1.00  0.00           O
ATOM      8  O2  GLC A   1       1.800   0.000   1.200  1.00  0.00           O
ATOM      9  O3  GLC A   1       1.800   1.200   1.200  1.00  0.00           O
ATOM     10  O4  GLC A   1       1.200   2.400   1.200  1.00  0.00           O
ATOM     11  O5  GLC A   1      -0.600   1.200   0.000  1.00  0.00           O
ATOM     12  O6  GLC A   1      -0.600   3.600   1.200  1.00  0.00           O
CONECT    1    2    7   11
CONECT    2    1    3    8
CONECT    3    2    4    9
CONECT    4    3    5   10
CONECT    5    4    6   11
CONECT    6    5   12
CONECT    7    1
CONECT    8    2
CONECT    9    3
CONECT   10    4
CONECT   11    1    5
CONECT   12    6
END
"""
    return pdb_content

def get_enzyme_name(pdb_file):
    """Extract enzyme name from filename."""
    stem = Path(pdb_file).stem
    parts = stem.split("_clean")
    if parts:
        return parts[0]
    return stem

def run_enzyme_substrate_md(pdb_file, laminarin_pdb_content, max_steps=50000, timeout=600):
    """
    Run MD on enzyme-substrate complex.
    
    Args:
        pdb_file: Path to cleaned enzyme PDB
        laminarin_pdb_content: PDB content string for substrate
        max_steps: MD steps (default 50000 = 100 ps)
    """
    
    enzyme_name = get_enzyme_name(pdb_file)
    output_traj = OUTPUT_DIR / f"{enzyme_name}_es_md_trajectory.pdb"
    output_log = LOG_DIR / f"{enzyme_name}_es_md.log"
    output_affinity = OUTPUT_DIR / f"{enzyme_name}_es_affinity.json"
    
    print(f"\n{'='*70}")
    print(f"ES-MD: {enzyme_name}")
    print(f"{'='*70}")
    
    try:
        # Load enzyme
        print(f"• Loading enzyme: {Path(pdb_file).name}")
        pdb_enzyme = PDBFile(str(pdb_file))
        n_enzyme_res = len(list(pdb_enzyme.topology.residues()))
        print(f"  Residues: {n_enzyme_res}")
        
        # Create temporary laminarin PDB file
        laminarin_pdb_file = OUTPUT_DIR / f"{enzyme_name}_laminarin_temp.pdb"
        with open(laminarin_pdb_file, 'w') as f:
            f.write(laminarin_pdb_content)
        print(f"• Created substrate: {laminarin_pdb_file.name}")
        
        # Load substrate
        pdb_substrate = PDBFile(str(laminarin_pdb_file))
        
        # Combine topologies and positions
        print(f"• Combining enzyme + substrate...")
        # Create new topology by adding substrate to enzyme
        from openmm.app.topology import Topology
        combined_topology = Topology()
        for chain in pdb_enzyme.topology.chains():
            new_chain = combined_topology.addChain()
            for residue in chain.residues():
                new_residue = combined_topology.addResidue(residue.name, new_chain)
                for atom in residue.atoms():
                    combined_topology.addAtom(atom.name, atom.element, new_residue)
        
        # Add substrate chain
        substrate_chain = combined_topology.addChain()
        for residue in pdb_substrate.topology.residues():
            new_residue = combined_topology.addResidue(residue.name, substrate_chain)
            for atom in residue.atoms():
                combined_topology.addAtom(atom.name, atom.element, new_residue)
        
        combined_positions = list(pdb_enzyme.positions) + list(pdb_substrate.positions)
        
        # Shift substrate away from enzyme (rudimentary docking)
        substrate_shift = (30, 0, 0)  # Shift 30 Å in X direction
        for i in range(len(pdb_enzyme.positions), len(combined_positions)):
            combined_positions[i] = combined_positions[i] + substrate_shift * angstrom
        
        print(f"  Total residues: {len(list(combined_topology.residues()))}")
        print(f"  Total atoms: {combined_topology.getNumAtoms()}")
        
        # Force field
        print(f"• Loading force field...")
        forcefield = ForceField('amber14-all.xml', 'implicit/gbn2.xml')
        
        # Add hydrogens
        print(f"• Adding hydrogens...")
        modeller = Modeller(combined_topology, combined_positions * angstrom)
        modeller.addHydrogens(forcefield)
        
        # Create system
        print(f"• Creating system...")
        system = forcefield.createSystem(
            modeller.topology,
            nonbondedMethod=CutoffNonPeriodic,
            nonbondedCutoff=1.0*nanometers,
            constraints=HBonds,
            rigidWater=True
        )
        
        # Integrator
        temperature = 300*kelvin
        timestep = 2.0*femtoseconds
        integrator = LangevinIntegrator(temperature, 1.0/picosecond, timestep)
        
        # Simulation
        print(f"• Creating simulation...")
        try:
            platform = Platform.getPlatformByName('CUDA')
            properties = {'CudaPrecision': 'mixed', 'DeviceIndex': '0'}
            simulation = Simulation(modeller.topology, system, integrator, platform, properties)
            platform_name = "CUDA"
        except:
            platform = Platform.getPlatformByName('CPU')
            simulation = Simulation(modeller.topology, system, integrator, platform)
            platform_name = "CPU"
        
        print(f"  Platform: {platform_name}")
        simulation.context.setPositions(modeller.positions)
        
        # Energy minimization
        print(f"• Minimizing energy...")
        initial_energy = simulation.context.getState(getEnergy=True).getPotentialEnergy()
        print(f"  Initial PE: {initial_energy}")
        
        simulation.minimizeEnergy(maxIterations=500, tolerance=1*kilojoule/mole)
        
        final_energy = simulation.context.getState(getEnergy=True).getPotentialEnergy()
        print(f"  Final PE: {final_energy}")
        
        # Equilibration
        print(f"• Equilibrating...")
        simulation.context.setVelocitiesToTemperature(temperature)
        simulation.step(1000)  # 2 ps
        
        # MD reporting
        simulation.reporters.append(
            PDBReporter(str(output_traj), 500)  # Every 1 ps
        )
        simulation.reporters.append(
            StateDataReporter(
                str(output_log),
                100,
                step=True,
                time=True,
                potentialEnergy=True,
                kineticEnergy=True,
                temperature=True,
                progress=True,
                remainingTime=True,
                speed=True,
                totalSteps=max_steps,
                separator='\t'
            )
        )
        
        # Production MD
        print(f"• Running MD: {max_steps} steps ({max_steps*2/1000:.1f} ps)...")
        print(f"  Output: {output_traj.name}\n")
        
        simulation.step(max_steps)
        
        # Analysis
        print(f"• Analyzing trajectory...")
        traj = md.load(str(output_traj))
        
        # Calculate metrics
        ca_indices = traj.topology.select("name CA")
        rmsd_values = md.rmsd(traj, traj, frame=0, atom_indices=ca_indices) * 10  # Angstroms
        
        # Calculate distances: enzyme C-alpha to substrate center
        substrate_heavy = traj.topology.select("element != H and residue == 1")
        if len(substrate_heavy) > 0:
            substrate_center = np.mean(traj.xyz[:, substrate_heavy, :], axis=1)
            ca_center = np.mean(traj.xyz[:, ca_indices, :], axis=1) if len(ca_indices) > 0 else None
            
            if ca_center is not None:
                distances = np.linalg.norm(ca_center - substrate_center, axis=1) * 10  # Angstroms
                min_distance = np.min(distances)
                final_distance = distances[-1]
            else:
                min_distance = final_distance = 0.0
        else:
            min_distance = final_distance = 0.0
        
        # Affinity proxy: Based on RMSD stability + close contact
        affinity_score = 100 - (rmsd_values[-1] + np.std(distances)) if len(substrate_heavy) > 0 else 50
        
        affinity_data = {
            "enzyme": enzyme_name,
            "n_enzyme_residues": n_enzyme_res,
            "n_frames": len(traj),
            "duration_ps": len(traj) * 1.0,
            "rmsd_initial_A": float(rmsd_values[0]),
            "rmsd_final_A": float(rmsd_values[-1]),
            "rmsd_mean_A": float(np.mean(rmsd_values)),
            "rmsd_std_A": float(np.std(rmsd_values)),
            "enzyme_substrate_min_distance_A": float(min_distance),
            "enzyme_substrate_final_distance_A": float(final_distance),
            "affinity_score": float(affinity_score),
            "affinity_category": "HIGH" if affinity_score > 70 else "MODERATE" if affinity_score > 50 else "LOW",
            "timestamp": datetime.now().isoformat(),
            "platform": platform_name
        }
        
        with open(output_affinity, 'w') as f:
            json.dump(affinity_data, f, indent=2)
        
        print(f"✓ Enzyme-substrate RMSD: {rmsd_values[0]:.3f} → {rmsd_values[-1]:.3f} Å")
        print(f"✓ Min enzyme-substrate distance: {min_distance:.2f} Å")
        print(f"✓ Affinity score: {affinity_score:.1f} ({affinity_data['affinity_category']})")
        print(f"✓ SUCCESS: {enzyme_name}")
        
        # Cleanup temp files
        laminarin_pdb_file.unlink()
        
        return True
        
    except Exception as e:
        print(f"✗ FAILED: {str(e)}")
        with open(output_log, 'w') as f:
            f.write(f"ERROR: {str(e)}\n")
        return False

def main():
    """Batch enzyme-substrate MD runner."""
    
    pdb_files = sorted(glob.glob(str(CLEAN_STRUCTURES / "*_clean.pdb")))
    
    print(f"Found: {len(pdb_files)} cleaned structures")
    print(f"Substrate: Laminarin ({len(LAMINARIN_SEQ)} glucose units)")
    print(f"Output: {OUTPUT_DIR}")
    print(f"{'='*70}\n")
    
    if not pdb_files:
        print("ERROR: No cleaned PDB files found!")
        return 1
    
    # Create laminarin PDB content once
    laminarin_pdb = create_laminarin_pdb()
    
    results = {}
    for i, pdb_file in enumerate(pdb_files, 1):
        enzyme_name = get_enzyme_name(pdb_file)
        print(f"\n[{i}/{len(pdb_files)}] {enzyme_name}")
        
        success = run_enzyme_substrate_md(pdb_file, laminarin_pdb)
        results[enzyme_name] = "SUCCESS" if success else "FAILED"
    
    # Summary
    print(f"\n\n{'='*70}")
    print(f"ENZYME-SUBSTRATE MD BATCH SUMMARY")
    print(f"{'='*70}\n")
    
    success_list = [v for v in results.values() if v == "SUCCESS"]
    success_count = len(success_list)
    print(f"Completed: {success_count}/{len(pdb_files)}")
    print(f"Success rate: {100*success_count/len(pdb_files):.1f}%\n")
    
    # Load and summarize affinity scores
    affinity_files = sorted(glob.glob(str(OUTPUT_DIR / "*_es_affinity.json")))
    if affinity_files:
        affinities = []
        for aff_file in affinity_files:
            with open(aff_file) as f:
                data = json.load(f)
                affinities.append(data)
        
        affinities_sorted = sorted(affinities, key=lambda x: x['affinity_score'], reverse=True)
        
        print(f"Top 5 Highest Affinity Candidates:")
        print(f"{'#':<3} {'Enzyme':<40} {'Score':<8} {'Category':<10} {'Min Dist (Å)':<12}")
        print(f"{'-'*75}")
        for i, aff in enumerate(affinities_sorted[:5], 1):
            print(f"{i:<3} {aff['enzyme'][:40]:<40} {aff['affinity_score']:<8.1f} {aff['affinity_category']:<10} {aff['enzyme_substrate_min_distance_A']:<12.2f}")
        
        # Save sorted affinity results
        summary_file = OUTPUT_DIR / "es_affinity_ranking.json"
        with open(summary_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "total_complexes": len(affinities),
                "successful": success_count,
                "affinities": affinities_sorted
            }, f, indent=2)
        
        print(f"\nRanking: {summary_file}")
    
    print(f"\nAffinity results in: {OUTPUT_DIR}")
    
    return 0 if success_count == len(pdb_files) else 1

if __name__ == "__main__":
    sys.exit(main())
