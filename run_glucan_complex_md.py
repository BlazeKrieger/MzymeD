#!/usr/bin/env python3
"""
Full ligand-in MD on real laminarinase–laminarin complexes using GLYCAM.

What is GLYCAM?
  - A carbohydrate force field (GLYCAM06) for glycans/oligosaccharides.
  - Provided via openmmforcefields as glycam_06j-1.xml.
  - Needed so laminarin (glucan) ligands get proper bonded/nonbonded params.

Pipeline (per PDB):
 1) Load crystal complex (keeps ligand).
 2) Remove crystallographic waters; keep ligands (HETATM) and protein.
 3) Add missing heavy atoms/hydrogens via Modeller (forcefield templates).
 4) Build system with AMBER14 protein + GLYCAM06 for glycans + GBn2 implicit solvent.
 5) Minimize, equilibrate, run short production MD.

Outputs:
  - md_simulation/glucan_complex_<pdb>.pdb      (frames every `report_interval` steps)
  - md_simulation/glucan_complex_<pdb>.log      (energy/temp/progress)
  - analysis_results/glucan_complex_<pdb>_rmsd.json

Usage:
  conda run -n mzymed python run_glucan_complex_md.py --pdb 2W52 --steps 50000

Notes:
  - Assumes ligands use standard sugar residue names (GLC, BGC, BMA, LMT, etc.).
  - If a ligand is unsupported, forcefield.createSystem will fail; we will report it.
  - For speed we use implicit solvent (GBn2). Switch to explicit TIP3P-FB by replacing
    'implicit/gbn2.xml' with 'amber14/tip3pfb.xml' and adding a water box.
"""

from __future__ import annotations

import argparse
import json
import shutil
import tempfile
from pathlib import Path

from openmm.app import (
    ForceField,
    Modeller,
    PDBFile,
    PDBReporter,
    Simulation,
    StateDataReporter,
    CutoffNonPeriodic,
    HBonds,
)
from openmm import Platform, LangevinIntegrator, unit
import mdtraj as md
from pdbfixer import PDBFixer


BASE = Path(__file__).parent
REAL_DIR = BASE / "real_structures"
PREDICTED_DIR = BASE / "predicted_structures"
MD_DIR = BASE / "md_simulation"
ANALYSIS_DIR = BASE / "analysis_results"
FF_DIR = BASE / "forcefields"
MD_DIR.mkdir(exist_ok=True)
ANALYSIS_DIR.mkdir(exist_ok=True)
FF_DIR.mkdir(exist_ok=True)


def load_forcefield():
    """Load AMBER14 + GLYCAM06j-1 + GBn2, preferring local glycam file if present."""
    local_glycam = FF_DIR / "glycam_06j-1.xml"
    if local_glycam.exists():
        print(f"  Using local GLYCAM: {local_glycam}")
        return ForceField(
            "amber14-all.xml",
            str(local_glycam),
            "implicit/gbn2.xml",
        )
    print("  Using package GLYCAM (glycam_06j-1.xml)")
    return ForceField(
        "amber14-all.xml",
        "glycam_06j-1.xml",
        "implicit/gbn2.xml",
    )


def list_hetero_residues(pdb_path: Path):
    """Return unique HETATM residue names to confirm ligand presence."""
    het_names = set()
    with open(pdb_path) as f:
        for line in f:
            if line.startswith("HETATM"):
                het_names.add(line[17:20].strip())
    return sorted(het_names)


def prepare_model(pdb_path: Path, forcefield: ForceField):
    """Load PDB, strip waters, rebuild missing heavy atoms with PDBFixer, then add H."""
    print(f"\nLoading {pdb_path.name} ...")

    # Map PDB residue names to unambiguous GLYCAM names
    res_rename = {
        "BGC": "0GB",  # beta-D-glucose
        "BMA": "0MB",  # beta-D-mannose
    }

    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdb") as tmp:
        tmp_path = Path(tmp.name)
        with open(pdb_path) as f_in:
            for line in f_in:
                if line.startswith(("ATOM", "HETATM")):
                    resname = line[17:20]
                    if resname in res_rename:
                        line = f"{line[:17]}{res_rename[resname]:>3}{line[20:]}"
                tmp.write(line.encode())

    fixer = PDBFixer(filename=str(tmp_path))
    fixer.findMissingResidues()
    fixer.findMissingAtoms()
    fixer.addMissingAtoms()
    fixer.addMissingHydrogens(pH=7.0)

    modeller = Modeller(fixer.topology, fixer.positions)

    # Remove crystallographic waters only; keep ligands of interest
    waters = [res for res in modeller.topology.residues() if res.name in {"HOH", "WAT"}]
    if waters:
        modeller.delete(waters)
        print(f"  Removed {len(waters)} crystallographic waters")

    # Keep only protein + laminarin-like sugars (BGC, BMA); drop other heterogens (e.g., NAG, MAN) to avoid template ambiguity
    allowed_ligands = {"BGC", "BMA"}
    aa = {
        "ALA","ARG","ASN","ASP","CYS","GLU","GLN","GLY","HIS","ILE","LEU","LYS","MET","PHE","PRO","SER","THR","TRP","TYR","VAL","SEC","PYL",
    }
    to_delete = []
    for res in modeller.topology.residues():
        if res.name in aa:
            continue  # protein
        if res.name in allowed_ligands:
            continue
        if res.name in {"HOH", "WAT"}:
            continue
        # any other heterogen removed
        to_delete.append(res)

    if to_delete:
        modeller.delete(to_delete)
        print(f"  Removed {len(to_delete)} non-target ligands (kept laminarin ligands: {', '.join(sorted(allowed_ligands))})")

    print("  Added missing heavy atoms and hydrogens (protein + ligands)")
    print(f"  Total atoms after fix: {modeller.topology.getNumAtoms()}")

    # Cleanup temp file
    try:
        tmp_path.unlink(missing_ok=True)  # type: ignore
    except Exception:
        pass

    return modeller


def build_simulation(modeller: Modeller, temperature: unit.Quantity, platform: Platform):
    """Create OpenMM simulation with AMBER14 + GLYCAM + implicit GBn2."""
    forcefield = load_forcefield()

    system = forcefield.createSystem(
        modeller.topology,
        nonbondedMethod=CutoffNonPeriodic,
        nonbondedCutoff=1.0 * unit.nanometer,
        constraints=HBonds,
    )

    integrator = LangevinIntegrator(
        temperature,
        1.0 / unit.picosecond,
        2.0 * unit.femtoseconds,
    )

    simulation = Simulation(modeller.topology, system, integrator, platform)
    simulation.context.setPositions(modeller.positions)
    return simulation


def run_md(pdb_id: str, steps: int, report_interval: int):
    # Try real_structures first, then predicted_structures
    pdb_path = REAL_DIR / f"{pdb_id}.pdb"
    if not pdb_path.exists():
        pdb_path = PREDICTED_DIR / f"{pdb_id}_predicted.pdb"
    if not pdb_path.exists():
        raise FileNotFoundError(f"Missing {REAL_DIR}/{pdb_id}.pdb or {PREDICTED_DIR}/{pdb_id}_predicted.pdb")

    # Quick ligand check
    hets = list_hetero_residues(pdb_path)
    print(f"Ligands detected (HETATM residue names): {', '.join(hets) if hets else 'None'}")

    # Force field upfront (needed for addHydrogens)
    ff = load_forcefield()

    # Prepare
    modeller = prepare_model(pdb_path, ff)

    # Platform selection: GPU-ONLY (CUDA > OpenCL, NO CPU fallback)
    platform = None
    gpu_used = False
    cuda_error = None
    opencl_error = None
    simulation = None
    
    # Try CUDA first
    try:
        platform = Platform.getPlatformByName("CUDA")
        props = {"CudaPrecision": "mixed", "DeviceIndex": "0"}
        simulation = build_simulation(modeller, 300 * unit.kelvin, platform)
        simulation.context.setPlatformProperties(props)
        print("  [GPU-CUDA] Using CUDA GPU (device 0, mixed precision)")
        gpu_used = True
    except Exception as e:
        cuda_error = str(e)
        print(f"  [WARN] CUDA unavailable: {cuda_error}")
        
        # Try OpenCL second
        try:
            platform = Platform.getPlatformByName("OpenCL")
            simulation = build_simulation(modeller, 300 * unit.kelvin, platform)
            # OpenCL doesn't have setPlatformProperties, but we can try to set device
            try:
                props = {"DeviceIndex": "0"}
                simulation.context.setPlatformProperties(props)
            except:
                pass  # OpenCL context doesn't support this, that's ok
            print("  [GPU-OPENCL] Using OpenCL GPU (device 0)")
            gpu_used = True
        except Exception as e2:
            opencl_error = str(e2)
            print(f"  [WARN] OpenCL unavailable: {opencl_error}")
            
            # Fall back to CPU if GPU unavailable
            try:
                platform = Platform.getPlatformByName("CPU")
                simulation = build_simulation(modeller, 300 * unit.kelvin, platform)
                print("  [CPU] WARNING: Using CPU - simulation will be slow!")
                gpu_used = False
            except Exception as e3:
                print(f"\n*** ERROR: NO COMPUTING PLATFORM AVAILABLE ***")
                print(f"  CUDA error:   {cuda_error}")
                print(f"  OpenCL error: {opencl_error}")
                print(f"  CPU error:    {str(e3)}")
                raise RuntimeError("Failed to find any available computing platform")

    # Minimize
    print("  Energy minimization...")
    simulation.minimizeEnergy(maxIterations=500)

    # Equilibrate
    print("  Equilibration (2 ps)...")
    simulation.context.setVelocitiesToTemperature(300 * unit.kelvin)
    simulation.step(1000)  # 2 ps

    # Reporters
    traj_path = MD_DIR / f"glucan_complex_{pdb_id}.pdb"
    log_path = MD_DIR / f"glucan_complex_{pdb_id}.log"
    simulation.reporters.append(PDBReporter(str(traj_path), report_interval))
    simulation.reporters.append(
        StateDataReporter(
            str(log_path),
            report_interval,
            step=True,
            time=True,
            potentialEnergy=True,
            temperature=True,
            progress=True,
            remainingTime=True,
            speed=True,
            totalSteps=steps,
        )
    )

    # Production
    print(f"  Production MD: {steps} steps (~{steps*2e-3:.1f} ps)")
    simulation.step(steps)

    print("  MD complete, analyzing RMSD...")
    traj = md.load(str(traj_path))
    rmsd = md.rmsd(traj, traj, 0)

    rmsd_json = {
        "pdb_id": pdb_id,
        "frames": int(traj.n_frames),
        "atoms": int(traj.n_atoms),
        "mean_rmsd_nm": float(rmsd.mean()),
        "max_rmsd_nm": float(rmsd.max()),
        "min_rmsd_nm": float(rmsd.min()),
    }

    with open(ANALYSIS_DIR / f"glucan_complex_{pdb_id}_rmsd.json", "w") as f:
        json.dump(rmsd_json, f, indent=2)

    print(f"  RMSD avg: {rmsd.mean()*10:.2f} Å  max: {rmsd.max()*10:.2f} Å")
    print(f"  Saved: {traj_path}")
    print(f"  Saved: {log_path}")
    print(f"  Saved: {ANALYSIS_DIR / f'glucan_complex_{pdb_id}_rmsd.json'}")


def parse_args():
    p = argparse.ArgumentParser(description="Ligand-in MD with GLYCAM for laminarin complexes")
    p.add_argument("--pdb", default="2W52", help="PDB ID in real_structures/ (e.g., 2W52, 4BPZ)")
    p.add_argument("--steps", type=int, default=50000, help="MD steps (2 fs timestep)")
    p.add_argument(
        "--report-interval",
        type=int,
        default=1000,
        help="Reporter stride (steps)",
    )
    return p.parse_args()


def main():
    args = parse_args()

    print("=" * 80)
    print("LIGAND-IN MD WITH GLYCAM (LAMINARINASE + LAMINARIN)")
    print("=" * 80)
    print(f"Complex: {args.pdb}")
    print(f"Steps: {args.steps} | Report every {args.report_interval} steps")
    print("Force fields: AMBER14 protein + GLYCAM06j-1 glycans + GBn2 implicit solvent")

    try:
        run_md(args.pdb, args.steps, args.report_interval)
    except Exception as e:
        print(f"\n[ERROR] Simulation failed: {e}")
        print("Common fixes:")
        print("  - Ensure openmmforcefields installed: pip install openmmforcefields pdbfixer")
        print("  - Unsupported ligand residue name? Check ligand codes in the PDB")
        print("  - Try shorter steps or CPU if CUDA fails")


if __name__ == "__main__":
    main()