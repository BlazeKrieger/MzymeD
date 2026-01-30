# 🧬 MzymeD - Laminarinase Structure & Affinity Analysis

**Status**: ✅ Analysis Complete | 🚀 Ready for Experimental Validation

---

## 📁 Quick Navigation

```
MzymeD/
├── scripts/           👈 ALL ANALYSIS SCRIPTS (organized by workflow)
├── results/           👈 ALL OUTPUTS & ANALYSIS (organized by type)
├── data/              👈 INPUT SEQUENCES & SUBSTRATES
├── docs/              👈 DOCUMENTATION & GUIDES
├── config/            👈 CONFIGURATION & SETUP
└── app.py             👈 Main application
```

## 🚀 Quick Start

### View Project Structure
```bash
cat docs/PROJECT_STRUCTURE.md
```

### Run Analyses
```bash
# Analyze AlphaFold predictions
cd scripts/analysis && python analyze_alphafold_predictions.py

# Run affinity assessment
cd scripts/md && python run_structural_affinity_analysis.py

# Test everything
cd scripts/utilities && python test_workflow.py
```

### Find Results
- **Affinity Rankings**: `results/analysis/alphafold_enzyme_affinity/affinity_scores.json`
- **Top Enzyme Structures**: `results/predictions/predicted_structures_cleaned/`
- **Analysis Report**: `docs/AFFINITY_ASSESSMENT_RESULTS.md`

---

## 📊 Project Status

| Component | Status | Details |
|-----------|--------|---------|
| AlphaFold Predictions | ✅ Complete | 20/80 sequences (GPU timeout) |
| Prediction Quality | ✅ Verified | pLDDT 93.9±2.8 (VERY HIGH) |
| Affinity Analysis | ✅ Complete | 20 enzymes ranked |
| Top Candidates | ✅ Identified | 2VY0, AAC25554.2, BAC67687.1 |
| Experimental Validation | ⏳ Ready | Phase 1 candidates prepared |

---

## 🎯 Top 5 Enzymes (Recommended for Testing)

| Rank | Enzyme | Score | Size | GH Family |
|------|--------|-------|------|-----------|
| 1 | **2VY0** | 0.8785 | 264 aa | GH16 |
| 2 | **AAC25554.2** | 0.8644 | 297 aa | GH16 |
| 3 | **BAC67687.1** | 0.8627 | 318 aa | GH16 |
| 4 | **BAH84971.1** | 0.8534 | 366 aa | GH16 |
| 5 | **BAE02683.1** | 0.8388 | 251 aa | GH16 |

→ See `docs/AFFINITY_ASSESSMENT_RESULTS.md` for full ranking & methodology

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| `PROJECT_STRUCTURE.md` | 📁 Directory organization guide |
| `AFFINITY_ASSESSMENT_RESULTS.md` | 📊 Complete analysis & methodology |
| `QUICK_START.md` | 🚀 Getting started guide |
| `README.md` | 📖 Original project overview |
| `USAGE.md` | 🔧 Detailed usage instructions |

---

## 🔧 Key Resources

### Scripts
- **Analysis**: `scripts/analysis/` (22 files)
  - AlphaFold prediction analysis
  - Visualization & plotting
  - Enzyme ranking
- **MD Simulations**: `scripts/md/` (14 files)
  - PDB cleaning & preparation
  - Affinity assessment
  - Structure validation
- **Utilities**: `scripts/utilities/` (11 files)
  - Testing & validation
  - Demos & examples

### Results
- **Predictions**: `results/predictions/` (711 files)
  - Raw ColabFold outputs
  - Cleaned PDB structures
- **Analysis**: `results/analysis/` (22 files)
  - Affinity scores JSON
  - Prediction quality metrics
- **MD Simulations**: `results/md_simulations/` (39 files)
  - Trajectories & logs
  - Analysis results
- **Research Data**: `results/laminarinases/` (95 enzyme FASTA files)

---

## 💡 Workflow Overview

```
Input Sequences (80 laminarinases)
         ↓
ColabFold Predictions (20 completed)
         ↓
PDB Structure Validation & Cleaning
         ↓
Structural Affinity Analysis
         ↓
Ranking & Top 5 Selection
         ↓
Prepared for Experimental Testing
```

---

## 🧪 Next Steps: Experimental Validation

### Phase 1: Biochemical Characterization
1. **Expression & Purification** → Top 5 enzymes
2. **Enzyme Kinetics** → Michaelis-Menten parameters
3. **Structural Validation** → X-ray/Cryo-EM (for top hit)

### Phase 2: Advanced Analysis
- Thermostability assays
- Substrate specificity testing
- Product characterization
- Dynamics validation via MD

### Phase 3: Scale-Up
- Complete remaining 60 enzyme predictions
- Test additional candidates if needed

---

## 📋 System Requirements

- **Python**: 3.9+
- **Key Dependencies**: See `config/requirements.txt`
- **GPU** (optional): CUDA for MD simulations

### Setup
```bash
pip install -r config/requirements.txt
python config/setup.py
```

---

## 🔍 File Mapping

**Need to find something?**

| Looking for | Path |
|-------------|------|
| Run affinity analysis | `scripts/analysis/analyze_alphafold_predictions.py` |
| Download PDB files | `results/predictions/predicted_structures_cleaned/` |
| View enzyme sequences | `data/sequences/laminarinases_all_80_sequences.fasta` |
| Check affinity scores | `results/analysis/alphafold_enzyme_affinity/affinity_scores.json` |
| Prediction quality plots | `results/predictions/colabfold_results/*_plddt.png` |
| Methodology explanation | `docs/AFFINITY_ASSESSMENT_RESULTS.md` |

---

## 📞 Contact & Notes

**Project**: Laminarinase Structure Prediction & Affinity Assessment  
**Date**: January 23, 2025  
**Status**: Ready for experimental validation  
**Organization**: High-level structure → Scripts → Results

---

**💡 Pro Tip**: Start with `docs/PROJECT_STRUCTURE.md` for detailed navigation, then use the quick-access paths above to find what you need!
