# ColabFold Batch Prediction via Google Colab

## Overview
ColabFold provides free AlphaFold2 predictions via Google Colab with no manual installation.

## Method 1: Use Official ColabFold Notebook (Easiest)

### Steps:
1. **Open**: https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb

2. **Upload your FASTA**:
   - Click "Files" icon on left sidebar
   - Upload: `laminarinases_medium_large_61.fasta`

3. **Configure settings**:
   ```python
   # In the notebook, set:
   query_sequence = ""  # Leave empty to use uploaded FASTA
   jobname = "laminarinases_batch"
   num_models = 1  # Faster, or use 5 for higher accuracy
   ```

4. **Run all cells** (Runtime → Run all)

5. **Wait**: ~30-90 minutes for 62 predictions

6. **Download**: Results appear in `/content/` folder
   - ZIP file with all PDB structures
   - Confidence scores (pLDDT)

## Method 2: Programmatic ColabFold (Advanced)

If you want to automate this from Python:

### Install LocalColabFold (Windows)
```powershell
# Download installer
wget https://github.com/YoshitakaMo/localcolabfold/releases/latest/download/localcolabfold_windows_installer.zip

# Extract and run installer
# Requires: GPU with CUDA support
```

### Run batch prediction
```bash
colabfold_batch laminarinases_medium_large_61.fasta output_structures/
```

## Method 3: Use ColabFold Web Server (Simplest)

**Alternative to Colab:**
- Website: https://colabfold.mmseqs.com/
- Upload FASTA (up to 1000 sequences)
- Email notification when done
- Free, no account needed

**Limitations:**
- Queue can be long (hours to days)
- Public server (less privacy)

## Comparison

| Method | Speed | Setup | Cost | Control |
|--------|-------|-------|------|---------|
| AlphaFold Server | Fast | None | Free | Low |
| ColabFold Colab | Moderate | None | Free | Medium |
| ColabFold Web | Slow | None | Free | Low |
| LocalColabFold | Fast | Complex | Free | High |
| ESMFold API | Very Fast | None | Free | High |

## Recommended Workflow

**For your 62 sequences:**

1. **Upload to ColabFold Colab** (no setup needed)
   - Link: https://colab.research.google.com/github/sokrypton/ColabFold/blob/main/batch/AlphaFold2_batch.ipynb
   - Upload: `laminarinases_medium_large_61.fasta`
   - Runtime: ~30-90 minutes
   - Quality: High (AlphaFold2-based)

2. **Download results**
   - 62 PDB files
   - pLDDT confidence scores
   - Prediction aligned error (PAE) plots

3. **Combine with existing ESMFold predictions**
   - 19 ESMFold (already have)
   - 62 ColabFold (from Colab)
   - Total: 81 high-quality ML predictions

## Why Not Local Installation?

**LocalColabFold requirements:**
- CUDA-capable GPU (RTX series recommended)
- ~60 GB disk space
- Complex dependency chain
- We tried earlier, had build errors

**Colab advantages:**
- Free GPU access (T4 or better)
- No installation needed
- Proven to work
- Same quality as local

## Next Steps

**Easiest path:**
1. Open ColabFold Colab notebook (link above)
2. Upload `laminarinases_medium_large_61.fasta`
3. Run all cells
4. Download results after 30-90 minutes
5. Copy PDB files to `predicted_structures_alphafold/`
6. Run batch MD on all 84 structures (4 known + 80 predicted)

