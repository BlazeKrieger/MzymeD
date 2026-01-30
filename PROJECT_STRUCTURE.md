# MzymeD Project Structure Guide

## 📁 Directory Organization

```
MzymeD/
├── 📂 scripts/                          # All analysis and computation scripts
│   ├── 📂 prediction/                   # ColabFold & AlphaFold scripts (future)
│   ├── 📂 analysis/                     # Data analysis & visualization
│   │   ├── analyze_alphafold_predictions.py
│   │   ├── process_colabfold_results.py
│   │   ├── create_enzyme_substrate_visualization.py
│   │   ├── create_web_visualization.py
│   │   ├── generate_pymol_files.py
│   │   ├── generate_pymol_labeled_scripts.py
│   │   ├── generate_realistic_catalysis.py
│   │   ├── select_top5_for_experimental_validation.py
│   │   └── ...visualization & analysis scripts
│   ├── 📂 md/                           # Molecular dynamics simulations
│   │   ├── clean_alphafold_pdbs.py
│   │   ├── run_enzyme_affinity_assessment.py
│   │   ├── run_structural_affinity_analysis.py
│   │   ├── run_enzyme_substrate_affinity_md.py
│   │   ├── run_enzyme_affinity_assessment_v2.py
│   │   ├── run_ca_md_affinity.py
│   │   └── ...other MD scripts
│   └── 📂 utilities/                    # Test, demo, and utility scripts
│       ├── demo.py
│       ├── demo_output.txt
│       ├── test_workflow.py
│       ├── verify_md.py
│       ├── simulate_catalytic_mechanism.py
│       ├── regenerate_mechanism.py
│       ├── print_affinity_ranking.py
│       └── ...utilities
│
├── 📂 data/                             # Input data
│   ├── 📂 sequences/                    # FASTA files of enzyme sequences
│   │   ├── laminarinases_all_80_sequences.fasta
│   │   ├── example_laminarinase.fasta
│   │   ├── example_usage.py
│   │   └── laminarin_substrate.fasta
│   └── 📂 substrates/                   # Substrate structure files (future)
│
├── 📂 results/                          # All analysis outputs & results
│   ├── 📂 predictions/                  # AlphaFold prediction results
│   │   ├── 📂 colabfold_results/        # Raw ColabFold outputs
│   │   │   ├── [20 enzyme predictions with PDBs, JSON, PNG plots]
│   │   ├── 📂 predicted_structures_alphafold/    # Rank-001 PDB copies
│   │   └── 📂 predicted_structures_cleaned/      # Force-field compatible PDBs
│   │
│   ├── 📂 analysis/                     # Structural & affinity analysis
│   │   ├── 📂 alphafold_analysis/       # Prediction quality metrics
│   │   │   └── alphafold_predictions_summary.json
│   │   └── 📂 alphafold_enzyme_affinity/# Affinity assessment results
│   │       ├── affinity_scores.json
│   │       └── 📂 logs/
│   │
│   ├── 📂 md_simulations/               # MD simulation results
│   │   ├── 📂 md_simulation/            # Original MD logs
│   │   └── 📂 simulation_outputs/       # MD trajectories & outputs
│   │
│   ├── 📂 laminarinases/                # Reference enzyme sequences
│   │   ├── 📂 GH16/ ... GH64/          # Grouped by enzyme family
│   │   └── [FASTA files for each laminarinase]
│   │
│   ├── 📂 real_structures/              # Experimental crystal structures (if any)
│   ├── 📂 catalytic_mechanism/          # Mechanism visualization scripts
│   └── 📂 pymol_scripts/                # PyMOL visualization scripts
│
├── 📂 docs/                             # Documentation
│   ├── README.md
│   ├── QUICK_START.md
│   ├── USAGE.md
│   ├── PROJECT_SUMMARY.md
│   ├── ENZYME_SUBSTRATE_SIMULATION.md
│   ├── SIMULATION_SUMMARY.md
│   ├── AFFINITY_ASSESSMENT_RESULTS.md
│   └── TEST_REPORT.md
│
├── 📂 config/                           # Configuration & setup
│   ├── requirements.txt
│   └── setup.py
│
├── 📂 src/                              # Source package (Python module)
│   └── 📂 mzymed/                       # Main package
│
├── app.py                               # Main application entry point
└── 📂 [test outputs, uploads, visual outputs] (temporary/working directories)
```

---

## 🚀 Quick Navigation Guide

### Running Workflows

**1. Analyzing AlphaFold Predictions**
```bash
cd scripts/analysis
python analyze_alphafold_predictions.py
```

**2. Running MD Simulations**
```bash
cd scripts/md
python run_structural_affinity_analysis.py
```

**3. Cleaning PDB Files for Force Fields**
```bash
cd scripts/md
python clean_alphafold_pdbs.py
```

**4. Testing & Utilities**
```bash
cd scripts/utilities
python demo.py
python test_workflow.py
```

---

## 📊 Key Results Files

| What | Location |
|------|----------|
| **Affinity Ranking** | `results/analysis/alphafold_enzyme_affinity/affinity_scores.json` |
| **Prediction Quality** | `results/analysis/alphafold_analysis/alphafold_predictions_summary.json` |
| **Affinity Report** | `docs/AFFINITY_ASSESSMENT_RESULTS.md` |
| **Best PDB Structures** | `results/predictions/predicted_structures_cleaned/` |
| **ColabFold Raw Predictions** | `results/predictions/colabfold_results/` |

---

## 🔧 Configuration

- **Dependencies**: See `config/requirements.txt`
- **Setup**: `config/setup.py`
- **Documentation**: See `docs/` folder

---

## 📚 Documentation Quick Links

| Document | Purpose |
|----------|---------|
| `README.md` | Project overview |
| `QUICK_START.md` | Getting started guide |
| `AFFINITY_ASSESSMENT_RESULTS.md` | Affinity analysis results & methodology |
| `PROJECT_SUMMARY.md` | Project scope and objectives |
| `USAGE.md` | Detailed usage instructions |

---

## 🎯 Current Status

✅ **Completed:**
- 20 high-confidence AlphaFold predictions (pLDDT > 90)
- Structural affinity analysis & ranking
- Top 5 enzyme candidates identified

⏳ **Next Steps:**
- Experimental biochemical validation (Phase 1)
- Complete remaining 60 enzyme predictions (Phase 2, if needed)
- Full MD simulations with substrate complexes

---

## 💡 Tips for Navigation

- All **scripts** are in `scripts/` organized by workflow type
- All **results** are in `results/` organized by analysis type
- All **input data** is in `data/` (sequences, substrates)
- All **documentation** is in `docs/`
- Use relative paths when referring to results from scripts, e.g.: `../results/predictions/colabfold_results/`

---

## 🔍 Finding Specific Files

| Need | Path |
|------|------|
| Run affinity analysis | `scripts/analysis/analyze_alphafold_predictions.py` |
| Clean PDB files | `scripts/md/clean_alphafold_pdbs.py` |
| View enzyme sequences | `data/sequences/laminarinases_all_80_sequences.fasta` |
| Affinity scores | `results/analysis/alphafold_enzyme_affinity/affinity_scores.json` |
| Prediction plots | `results/predictions/colabfold_results/*_plddt.png` |
| Test the setup | `scripts/utilities/test_workflow.py` |

---

**Last Updated:** January 23, 2025
