#!/usr/bin/env python3
"""
Installation and setup guide for structure prediction tools.
This script helps you set up ESMFold or OmegaFold for real 3D structure predictions.
"""

import subprocess
import sys

def check_tool(tool_name):
    """Check if a tool is installed."""
    try:
        result = subprocess.run([tool_name, "--help"], capture_output=True)
        return result.returncode == 0
    except:
        return False

def install_esmfold():
    """Install ESMFold."""
    print("\n" + "="*80)
    print("INSTALLING ESMFold")
    print("="*80)
    print("\nESMFold is a fast, accurate structure predictor from Meta AI Research")
    print("Installation may take 5-10 minutes and requires ~2GB disk space\n")
    
    commands = [
        "pip install fair-esm[esmfold]",
        "pip install 'esmfold @ git+https://github.com/sokrypton/ESMFold.git'",
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        try:
            subprocess.run(cmd, shell=True, check=True)
            print("✓ Installation successful!")
            return True
        except Exception as e:
            print(f"✗ Installation failed: {e}")
            continue
    
    return False

def install_omegafold():
    """Install OmegaFold."""
    print("\n" + "="*80)
    print("INSTALLING OmegaFold")
    print("="*80)
    print("\nOmegaFold is a lightweight structure predictor")
    print("Installation typically takes 3-5 minutes and requires ~500MB disk space\n")
    
    cmd = "pip install omegafold"
    
    print(f"Running: {cmd}")
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("✓ Installation successful!")
        return True
    except Exception as e:
        print(f"✗ Installation failed: {e}")
        return False

def install_colabfold():
    """Install ColabFold (easier cloud-based option)."""
    print("\n" + "="*80)
    print("ColabFold - CLOUD-BASED OPTION")
    print("="*80)
    print("\nColabFold is the easiest option - no installation needed!")
    print("\nSteps:")
    print("1. Go to: https://colab.research.google.com/")
    print("2. Create new notebook")
    print("3. Install ColabFold:")
    print("   !pip install colabfold[alphafold2] -q")
    print("4. Import and use:")
    print("   from colabfold.predict import predict")
    print("   predict(sequences=['YOUR_SEQUENCE'])")
    print("\nBenefit: Free, GPU-accelerated, no local installation needed!")

def main():
    print("\n" + "="*80)
    print("STRUCTURE PREDICTION TOOL SETUP GUIDE")
    print("="*80)
    
    print("\nYour next steps after this analysis:")
    print("\nPhase 1: Install a structure prediction tool (choose one):")
    print("  Option A: ESMFold (fastest, meta.ai - recommended)")
    print("  Option B: OmegaFold (lightweight alternative)")
    print("  Option C: ColabFold (cloud-based, easiest)")
    
    print("\nPhase 2: Predict structures for top 15 candidates:")
    print("  - ACU35625.1 (activity 95.3)")
    print("  - AOR29491.1 (activity 94.6)")
    print("  - BAF52916.1 (activity 94.3)")
    print("  - ... (12 more candidates)")
    
    print("\nPhase 3: Validate predictions with molecular dynamics")
    
    print("\nPhase 4: Prepare for experimental structure determination")
    
    print("\n" + "="*80)
    print("INSTALLATION OPTIONS")
    print("="*80)
    
    print("\n[1] ESMFold (Recommended)")
    print("    - Fastest: 1-5 minutes per protein")
    print("    - Accurate: Matches AlphaFold2 quality")
    print("    - Local: Runs on your computer")
    print("    - Command: pip install 'esmfold'")
    
    print("\n[2] OmegaFold")
    print("    - Lightweight: ~500MB disk space")
    print("    - Accurate: Good quality predictions")
    print("    - Local: Runs on your computer")
    print("    - Command: pip install omegafold")
    
    print("\n[3] ColabFold (Easiest)")
    print("    - Cloud-based: No local installation")
    print("    - Free: Google Colab GPU access")
    print("    - Very Fast: GPU-accelerated")
    print("    - Web: https://colab.research.google.com/")
    
    print("\n[4] Exit")
    
    choice = input("\nSelect option (1-4): ").strip()
    
    if choice == "1":
        success = install_esmfold()
        if success:
            print("\n✓ ESMFold installed successfully!")
            print("\nNext: Modify predict_structures_advanced.py to use ESMFold")
            print("Then run: python predict_structures_advanced.py")
    elif choice == "2":
        success = install_omegafold()
        if success:
            print("\n✓ OmegaFold installed successfully!")
            print("\nNext: Modify predict_structures_advanced.py to use OmegaFold")
            print("Then run: python predict_structures_advanced.py")
    elif choice == "3":
        install_colabfold()
    else:
        print("\nSetup guide complete. You can run this script anytime to install tools.")
    
    print("\n" + "="*80)
    print("WHAT'S NEXT")
    print("="*80)
    print("""
RECOMMENDED WORKFLOW:

1. Choose your prediction tool:
   - ESMFold is fastest and most accurate for local use
   - ColabFold is easiest if you prefer cloud-based

2. Install the tool using this script

3. Update predict_structures_advanced.py to use real predictions
   (Currently it generates mock structures for testing)

4. Run predictions on your sequences:
   python predict_structures_advanced.py

5. Validate predictions with MD simulations

6. Select top 5 candidates for experimental work

7. Proceed with recombinant expression and characterization

CURRENT STATUS:
✓ 81 sequences analyzed and scored
✓ Activity predictions complete
✓ Top candidates identified
✓ Mock structures generated for testing
⏳ Awaiting real structure predictions
⏳ Ready for experimental validation

START HERE: Run this script to install a structure prediction tool!
""")

if __name__ == "__main__":
    main()
