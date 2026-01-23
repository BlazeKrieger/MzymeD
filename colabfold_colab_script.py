"""
ColabFold Batch Prediction Script
Copy-paste this entire code into Google Colab to predict all 62 medium/large laminarinases
"""

# ============================================================================
# STEP 1: Install ColabFold (run this cell first)
# ============================================================================
import os
import sys

# Check if in Colab
try:
    from google.colab import files
    IN_COLAB = True
    print("✅ Running in Google Colab")
except:
    IN_COLAB = False
    print("⚠️  Not in Colab - this script is designed for Google Colab")
    sys.exit(1)

# Install ColabFold
print("\n📦 Installing ColabFold...")
!pip install -q "colabfold[alphafold] @ git+https://github.com/sokrypton/ColabFold"

print("✅ Installation complete!")

# ============================================================================
# STEP 2: Upload your FASTA file
# ============================================================================
print("\n" + "="*80)
print("UPLOAD YOUR FASTA FILE")
print("="*80)
print("Click 'Choose Files' below and select:")
print("  laminarinases_medium_large_61.fasta")
print("="*80)

uploaded = files.upload()
fasta_file = list(uploaded.keys())[0]
print(f"\n✅ Uploaded: {fasta_file}")

# Check sequences
from Bio import SeqIO
records = list(SeqIO.parse(fasta_file, "fasta"))
print(f"✅ Found {len(records)} sequences")
print(f"   Size range: {min(len(r.seq) for r in records)} - {max(len(r.seq) for r in records)} aa")

# ============================================================================
# STEP 3: Configure prediction settings
# ============================================================================
print("\n" + "="*80)
print("CONFIGURATION")
print("="*80)

# Settings
jobname = "laminarinases_batch"
output_dir = f"/content/{jobname}"
num_models = 1  # Use 1 for speed, 5 for accuracy
num_recycles = 3  # Default, higher = more accurate but slower

print(f"Job name:        {jobname}")
print(f"Output dir:      {output_dir}")
print(f"Models:          {num_models}")
print(f"Recycles:        {num_recycles}")
print(f"GPU:             {os.system('nvidia-smi -L')}")
print("="*80)

# ============================================================================
# STEP 4: Run ColabFold batch prediction
# ============================================================================
print("\n" + "="*80)
print("RUNNING PREDICTIONS")
print("="*80)
print(f"⏳ Processing {len(records)} sequences...")
print("   This will take 30-90 minutes depending on sequence sizes")
print("="*80)

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Run ColabFold
!colabfold_batch \
    {fasta_file} \
    {output_dir} \
    --num-models {num_models} \
    --num-recycle {num_recycles} \
    --use-gpu-relax

print("\n✅ Predictions complete!")

# ============================================================================
# STEP 5: Review results
# ============================================================================
print("\n" + "="*80)
print("RESULTS SUMMARY")
print("="*80)

import glob
pdb_files = glob.glob(f"{output_dir}/*_rank_001_*.pdb")
json_files = glob.glob(f"{output_dir}/*.json")

print(f"PDB structures:  {len(pdb_files)}")
print(f"Confidence data: {len(json_files)}")

# Show confidence scores
if json_files:
    import json
    print("\nTop 10 predictions by confidence (pLDDT):")
    confidence_data = []
    for json_file in json_files:
        with open(json_file) as f:
            data = json.load(f)
            name = os.path.basename(json_file).replace('.json', '')
            plddt = data.get('plddt', data.get('mean_plddt', 0))
            confidence_data.append((name, plddt))
    
    confidence_data.sort(key=lambda x: x[1], reverse=True)
    for i, (name, score) in enumerate(confidence_data[:10], 1):
        print(f"  {i:2d}. {name:40s} pLDDT: {score:.2f}")

print("="*80)

# ============================================================================
# STEP 6: Download results
# ============================================================================
print("\n" + "="*80)
print("DOWNLOAD RESULTS")
print("="*80)

# Create ZIP file
print("📦 Creating ZIP archive...")
!zip -r -q {jobname}_results.zip {output_dir}

print(f"✅ Created: {jobname}_results.zip")
print("   Click below to download:")
files.download(f"{jobname}_results.zip")

print("\n" + "="*80)
print("COMPLETE!")
print("="*80)
print("Next steps:")
print("1. Extract the ZIP file on your local machine")
print("2. Copy PDB files to: predicted_structures_alphafold/")
print("3. Run the processing script: python process_colabfold_results.py")
print("="*80)
