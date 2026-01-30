# ColabFold Setup Guide

## Quick Start (3 Steps)

### Step 1: Open Google Colab
Go to: https://colab.research.google.com/

### Step 2: Create New Notebook
1. Click "File" → "New notebook"
2. Copy-paste the code from `colabfold_colab_script.py` (in this directory)
3. Run all cells (Runtime → Run all)

### Step 3: Upload FASTA
When prompted, upload: `laminarinases_medium_large_61.fasta`

**That's it!** Wait 30-90 minutes, then download the results.

---

## Detailed Instructions

### 1. Prepare Your Environment

**On Google Colab:**
- Free GPU access (Tesla T4 or better)
- No installation needed
- No account required (but recommended for saving work)

**Files you need:**
- `laminarinases_medium_large_61.fasta` (62 sequences, 400-2435 aa)

### 2. Create Colab Notebook

**Option A: Use provided script**
1. Open: https://colab.research.google.com/
2. New notebook
3. Copy entire contents of `colabfold_colab_script.py` into first cell
4. Run the cell

**Option B: Use official ColabFold notebook**
1. Open: https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb
2. Follow instructions in notebook
3. Upload your FASTA file when prompted

### 3. Configuration Settings

```python
# Recommended settings for your batch:
jobname = "laminarinases_batch"
num_models = 1           # Use 1 for speed, 5 for max accuracy
num_recycles = 3         # Default
use_amber = True         # Relaxation with AMBER force field
```

**Speed vs Quality:**
- `num_models=1`: ~30-45 minutes (good quality)
- `num_models=5`: ~90-180 minutes (best quality, ensemble)

### 4. Expected Runtime

**For 62 sequences:**
- Small (400-600 aa): ~30 seconds each
- Medium (600-1000 aa): ~60 seconds each  
- Large (>1000 aa): ~90-120 seconds each

**Total time:** ~30-90 minutes depending on settings

### 5. Download Results

After completion, you'll get:
- `laminarinases_batch_results.zip` (~50-100 MB)

**Contents:**
```
laminarinases_batch/
├── ACU35625.1_rank_001_alphafold2_ptm_model_1_seed_000.pdb
├── ACU35625.1.json                     # Confidence scores
├── ACU35625.1_coverage.png             # MSA coverage plot
├── ACU35625.1_pae.png                  # Predicted aligned error
├── AOR29491.1_rank_001_*.pdb
├── ... (62 sequences total)
```

### 6. Process Results Locally

**After downloading:**

```powershell
# Extract ZIP
Expand-Archive laminarinases_batch_results.zip -DestinationPath .

# Process and organize
python process_colabfold_results.py
```

This will:
- Extract best models (rank 1)
- Rename to standard format: `{accession}_alphafold.pdb`
- Copy to `predicted_structures_alphafold/`
- Generate summary report with confidence scores

### 7. Combine All Predictions

```powershell
# You'll have:
# - 19 ESMFold predictions (predicted_structures_ml/)
# - 62 AlphaFold predictions (predicted_structures_alphafold/)
# - 4 known structures (known_structures/)

# Combine into final directory
python combine_all_predictions.py
```

---

## Troubleshooting

### "Runtime disconnected"
- Colab free tier has 12-hour limit
- Save notebook frequently
- If disconnected, re-run from checkpoint

### "Out of memory"
- Reduce `num_models` to 1
- Try splitting into smaller batches
- Use Colab Pro for more RAM

### "No GPU available"
- Go to: Runtime → Change runtime type
- Select: GPU (T4)
- Restart runtime

### "Upload failed"
- Check file size (<100 MB recommended)
- Try splitting FASTA into smaller batches
- Use Google Drive mount instead

---

## Alternative: Batch Processing Script

If you want to run smaller batches:

```python
# Split FASTA into 3 batches
python split_fasta.py laminarinases_medium_large_61.fasta --batches 3

# Result:
# batch_1.fasta (20 sequences)
# batch_2.fasta (21 sequences)  
# batch_3.fasta (21 sequences)

# Run each batch separately on Colab
```

---

## Quality Assessment

**pLDDT (per-residue confidence):**
- >90: Very high confidence
- 70-90: Good confidence
- 50-70: Low confidence
- <50: Should not be trusted

**Expected quality for your sequences:**
- Most should be >70 pLDDT
- Catalytic domains typically >80
- Disordered regions may be <70 (normal)

---

## Next Steps After Getting Results

1. ✅ Process results: `python process_colabfold_results.py`
2. ✅ Combine with ESMFold: 19 + 62 = 81 total
3. ✅ Run batch MD: All 84 structures (4 known + 80 predicted)
4. ✅ Generate ranking: Stability analysis + activity scores
5. ✅ Identify top candidates: Select best 10-20 for further study

---

## Cost & Time Summary

| Method | Cost | Setup Time | Prediction Time | Quality |
|--------|------|------------|-----------------|---------|
| ColabFold Colab | Free | 0 min | 30-90 min | High |
| AlphaFold Server | Free | 0 min | 15-60 min | High |
| LocalColabFold | Free | 60 min | 20-40 min | High |
| ESMFold API | Free | 0 min | 5-10 min | Good |

**Recommended:** Use ColabFold Colab for complete automation with no setup.
