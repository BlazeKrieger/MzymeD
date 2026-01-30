#!/usr/bin/env python3
"""
Run full enzyme-substrate molecular dynamics simulation with laminarinases and laminarin.
"""

from pathlib import Path
import sys

sys.path.insert(0, "src")
from mzymed.app import MzymeDApp


def main():
    print("=" * 70)
    print("MzymeD - Laminarinase + Laminarin MD Simulation")
    print("=" * 70)
    
    base = Path(__file__).parent
    
    # Select laminarinase enzyme
    enzyme_path = base / "laminarinases" / "GH16" / "BxLam16A.fasta"
    substrate_path = base / "laminarin_substrate.fasta"
    
    if not enzyme_path.exists():
        print(f"❌ Enzyme file not found: {enzyme_path}")
        return
    
    if not substrate_path.exists():
        print(f"❌ Substrate file not found: {substrate_path}")
        return
    
    print(f"📁 Enzyme: {enzyme_path.name}")
    print(f"📁 Substrate: {substrate_path.name}")
    
    # Initialize app with GPU support
    import torch
    device = "cuda" if torch.cuda.is_available() else "cpu"
    print(f"🖥️  Using device: {device.upper()}")
    if torch.cuda.is_available():
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
    
    app = MzymeDApp(output_dir="simulation_outputs")
    
    # Process enzyme
    print("\n" + "=" * 70)
    if not app.process_enzyme(str(enzyme_path)):
        print("❌ Failed to process enzyme")
        return
    
    # Process substrate
    print("\n" + "=" * 70)
    if not app.process_substrate(str(substrate_path)):
        print("❌ Failed to process substrate")
        return
    
    # Analyze interactions
    print("\n" + "=" * 70)
    results = app.analyze_interactions()
    
    if results:
        print("\n" + "=" * 70)
        print("SIMULATION RESULTS")
        print("=" * 70)
        
        if "binding_energy" in results:
            print(f"🔬 Binding Energy: {results['binding_energy']:.2f} kcal/mol")
        
        if "active_site" in results:
            print(f"🧬 Active Site Residues: {len(results['active_site'])}")
        
        if "contact_map" in results:
            print(f"📊 Contact Map: {results['contact_map'].shape if hasattr(results['contact_map'], 'shape') else 'Available'}")
        
        print("\n✅ Simulation completed successfully!")
        print(f"📂 Output directory: simulation_outputs/")
    else:
        print("❌ No results generated")


if __name__ == "__main__":
    main()
