# 🗂️ MzymeD File Index & Quick Access

## 📍 I Need To...

### 🔍 Find Something
| Need | Quick Path |
|------|-----------|
| See all my scripts | `scripts/` |
| Find analysis scripts | `scripts/analysis/` |
| Find MD scripts | `scripts/md/` |
| Find test/demo scripts | `scripts/utilities/` |
| See all my results | `results/` |
| Check affinity scores | `results/analysis/alphafold_enzyme_affinity/affinity_scores.json` |
| Download top PDB files | `results/predictions/predicted_structures_cleaned/` |
| View enzyme sequences | `data/sequences/` |
| Read documentation | `docs/` |
| Check configuration | `config/` |

---

### 🚀 Run Something
| Task | Command |
|------|---------|
| Analyze predictions | `cd scripts/analysis && python analyze_alphafold_predictions.py` |
| Run affinity assessment | `cd scripts/md && python run_structural_affinity_analysis.py` |
| Clean PDB files | `cd scripts/md && python clean_alphafold_pdbs.py` |
| Test everything | `cd scripts/utilities && python test_workflow.py` |
| View results | `cat results/analysis/alphafold_enzyme_affinity/affinity_scores.json` |

---

### 📖 Read Something
| Document | File | Purpose |
|----------|------|---------|
| Quick Start | `README_NEW_STRUCTURE.md` | 2-minute overview |
| Detailed Map | `docs/PROJECT_STRUCTURE.md` | Complete directory guide |
| Analysis Report | `docs/AFFINITY_ASSESSMENT_RESULTS.md` | Full results & methodology |
| Getting Started | `docs/QUICK_START.md` | Setup & first steps |
| Original Readme | `docs/README.md` | Project overview |

---

### 🔧 Configure Something
| Config File | Purpose |
|-------------|---------|
| `config/requirements.txt` | Python dependencies |
| `config/setup.py` | Package setup script |

---

## 🗺️ Directory Tree

```
MzymeD/
├── scripts/              ← ALL SCRIPTS (organized by workflow)
│   ├── analysis/        (22 files: AlphaFold analysis, visualization)
│   ├── md/              (14 files: MD simulations, affinity assessment)
│   └── utilities/       (11 files: testing, demos)
│
├── results/             ← ALL OUTPUTS (organized by type)
│   ├── predictions/     (ColabFold + cleaned PDBs)
│   ├── analysis/        (Affinity scores, metrics)
│   ├── md_simulations/  (MD trajectories, logs)
│   ├── laminarinases/   (95 enzyme sequences)
│   ├── catalytic_mechanism/
│   ├── pymol_scripts/
│   └── real_structures/
│
├── data/                ← INPUT DATA
│   ├── sequences/       (4 FASTA files)
│   └── substrates/
│
├── docs/                ← DOCUMENTATION (25+ files)
│   ├── PROJECT_STRUCTURE.md
│   ├── AFFINITY_ASSESSMENT_RESULTS.md
│   ├── QUICK_START.md
│   └── ... (25+ more)
│
├── config/              ← CONFIGURATION
│   ├── requirements.txt
│   └── setup.py
│
└── app.py               ← MAIN APPLICATION
```

---

## 📊 File Statistics

| Category | Location | Count | Examples |
|----------|----------|-------|----------|
| **Scripts** | `scripts/` | 48 | analyze_alphafold_predictions.py, run_structural_affinity_analysis.py |
| **Results** | `results/` | 711+ | PDB files, JSON scores, trajectories |
| **Sequences** | `data/sequences/` | 4 | laminarinases_all_80_sequences.fasta |
| **Documentation** | `docs/` | 25+ | README.md, QUICK_START.md |
| **Configuration** | `config/` | 2 | requirements.txt, setup.py |

---

## 🎯 Most Important Files

| Priority | File | What It Does |
|----------|------|--------------|
| 🔴 **CRITICAL** | `AFFINITY_ASSESSMENT_RESULTS.md` | Top 5 enzymes + full methodology |
| 🟠 **IMPORTANT** | `results/analysis/alphafold_enzyme_affinity/affinity_scores.json` | Affinity ranking data |
| 🟠 **IMPORTANT** | `results/predictions/predicted_structures_cleaned/` | Best PDB structures for testing |
| 🟡 **USEFUL** | `PROJECT_STRUCTURE.md` | Navigation guide |
| 🟡 **USEFUL** | `README_NEW_STRUCTURE.md` | Quick start |
| 🟢 **REFERENCE** | `docs/` | All documentation |

---

## 🏆 Top 5 Results to Check

### 1. Affinity Scores
```
results/analysis/alphafold_enzyme_affinity/affinity_scores.json
```
Complete ranking of all 20 enzymes with scores.

### 2. Top PDB Files
```
results/predictions/predicted_structures_cleaned/
├── 2VY0_..._clean.pdb           (Score: 0.8785 - TOP CHOICE)
├── AAC25554.2_..._clean.pdb    (Score: 0.8644)
├── BAC67687.1_..._clean.pdb    (Score: 0.8627)
└── ... (17 more enzymes)
```

### 3. ColabFold Raw Outputs
```
results/predictions/colabfold_results/
├── [20 directories with confidence plots]
├── *.pdb                        (PDB structures)
├── *_scores_rank_001_*.json    (Confidence metrics)
└── *.png                        (pLDDT & PAE plots)
```

### 4. Enzyme Sequences
```
data/sequences/laminarinases_all_80_sequences.fasta
results/laminarinases/GH16/      (95 enzyme FASTAs organized by family)
```

### 5. Analysis Report
```
docs/AFFINITY_ASSESSMENT_RESULTS.md
```

---

## 💻 Script Directory Reference

### scripts/analysis/ (22 files)
Primary: AlphaFold analysis, visualization, ranking
- `analyze_alphafold_predictions.py`
- `process_colabfold_results.py`
- `create_enzyme_substrate_visualization.py`
- `generate_pymol_files.py`
- ... and 18 more

### scripts/md/ (14 files)
Primary: Molecular dynamics, affinity assessment
- `clean_alphafold_pdbs.py`
- `run_structural_affinity_analysis.py`
- `run_enzyme_affinity_assessment.py`
- `run_enzyme_substrate_affinity_md.py`
- ... and 10 more

### scripts/utilities/ (11 files)
Primary: Testing, validation, demos
- `test_workflow.py`
- `demo.py`
- `verify_md.py`
- ... and 8 more

---

## 📂 Results Directory Reference

### results/predictions/ (711 files)
**ColabFold raw outputs** + **Cleaned PDB structures**
- `colabfold_results/` - Raw outputs (20 enzyme directories)
- `predicted_structures_alphafold/` - Rank-001 PDB copies
- `predicted_structures_cleaned/` - Force-field compatible PDBs ✨

### results/analysis/ (22 files)
**Affinity assessment & quality metrics**
- `alphafold_analysis/` - Prediction quality JSON
- `alphafold_enzyme_affinity/` - Affinity scores JSON ✨

### results/md_simulations/ (39 files)
**MD trajectories & validation logs**
- `md_simulation/` - Original logs
- `simulation_outputs/` - Trajectories

### results/laminarinases/ (95 files)
**Reference enzyme sequences (FASTA)**
- `GH16/`, `GH17/`, `GH3/`, `GH55/`, `GH64/` - By family

---

## 🔗 Cross-References

**To find the top 5 enzymes:**
1. Open: `results/analysis/alphafold_enzyme_affinity/affinity_scores.json`
2. Top scores: 2VY0, AAC25554.2, BAC67687.1, BAH84971.1, BAE02683.1
3. Get PDBs: `results/predictions/predicted_structures_cleaned/[NAME]_clean.pdb`

**To understand the ranking:**
1. Read: `docs/AFFINITY_ASSESSMENT_RESULTS.md`
2. Methodology section explains scoring formula
3. Limitations section explains validation

**To run analyses:**
1. Go to: `scripts/[category]/`
2. Run: `python [script_name].py`
3. Check outputs: `results/[relevant_folder]/`

---

## ✅ Verification

To verify the reorganization is complete:

```bash
# Check scripts count
find scripts -name "*.py" | wc -l          # Should be ~48

# Check results
find results -type f | wc -l               # Should be 700+

# Check data
find data -name "*.fasta" | wc -l         # Should be 4

# Check docs
find docs -name "*.md" | wc -l            # Should be 25+
```

---

## 🎓 Pro Tips

1. **Bookmark this file** - Keep it for reference
2. **Use relative paths** - `../results/analysis/...` when in scripts/
3. **Read the guides** - Start with `README_NEW_STRUCTURE.md`
4. **Keep it organized** - New files should go into appropriate folders:
   - New analysis scripts → `scripts/analysis/`
   - New results → `results/[type]/`
   - New data → `data/[type]/`

---

## 📝 Quick Cheat Sheet

```bash
# Navigate to scripts
cd scripts/analysis      # Analysis scripts
cd scripts/md            # MD scripts
cd scripts/utilities     # Test scripts

# View results
cat results/analysis/alphafold_enzyme_affinity/affinity_scores.json

# Get top PDBs
ls results/predictions/predicted_structures_cleaned/ | head -5

# Read docs
cat docs/AFFINITY_ASSESSMENT_RESULTS.md
cat docs/PROJECT_STRUCTURE.md

# Run tests
cd scripts/utilities && python test_workflow.py
```

---

**Last Updated**: January 23, 2025  
**Purpose**: Quick access guide to reorganized MzymeD project  
**Feedback**: Use this index to find anything quickly!
