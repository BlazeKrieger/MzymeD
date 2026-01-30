# Cleanup Plan - Analysis & Categorization

## ✅ KEEP - Working Solutions
These are the scripts that work and produce results:
- `scripts/analysis/analyze_alphafold_predictions.py` - Primary analysis
- `scripts/md/clean_alphafold_pdbs.py` - PDB preparation (working)
- `scripts/md/run_structural_affinity_analysis.py` - **MAIN SOLUTION** (produces affinity scores)
- `scripts/utilities/test_workflow.py` - Testing framework

## 📁 KEEP - Alternative Workflows (different approaches)
Keep these as they represent different valid approaches to explore:

### Analysis Alternatives:
- `create_enzyme_substrate_visualization.py` - Enzyme-substrate visualization
- `create_web_visualization.py` - Web-based visualization
- `generate_md_trajectory.py` - Trajectory generation
- `generate_pymol_files.py` - PyMOL script generation
- `visualize_*.py` (4 files) - Different visualization approaches
- `select_top5_for_experimental_validation.py` - Selection methodology

### MD Alternatives:
- `run_all_structures_md.py` - Batch MD runner
- `run_real_md_simulation.py` - Real OpenMM simulation
- `run_batch_md_sequential.py` - Sequential MD approach

## 🚮 DELETE - Obsolete/Failed Attempts
These are dead-ends or superseded by working solutions:

### Failed MD Approaches (terminal group issues, force field problems):
- `run_enzyme_affinity_assessment.py` - FAILED (force field errors)
- `run_enzyme_affinity_assessment_v2.py` - FAILED (force field errors)
- `run_ca_md_affinity.py` - FAILED (Quantity/API issues)
- `run_enzyme_substrate_affinity_md.py` - FAILED (substrate issues)
- `run_enzyme_substrate_md.py` - FAILED (substrate issues)
- `run_enzyme_substrate_md_fixed.py` - FAILED (substrate issues)
- `run_cleaned_md.py` - FAILED (deprecated)
- `run_complex_md_working.py` - FAILED (misleading name, actually broken)
- `run_real_openmm_md.py` - FAILED (architecture mismatch)
- `run_glucan_complex_md.py` - FAILED (substrate issues)
- `run_batch_alphafold_md.py` - FAILED (batch processing error)

### Outdated Report Generators:
- `create_comprehensive_ranking_report.py` - Superseded by analysis
- `create_validation_evidence_summary.py` - Redundant
- `generate_known_structures_report.py` - Redundant
- `generate_md_dashboard.py` - Redundant
- `generate_prediction_report.py` - Redundant
- `generate_ranking_report.py` - Redundant

### Dead-End Visualization:
- `visualize_md_mock.py` - Mock/test visualization
- `visualize_md_validation.py` - Redundant validation

### Utility Clutter:
- `demo.py` - Just a demo, not needed
- `regenerate_mechanism.py` - One-time script
- `regenerate_structures_gpu.py` - GPU workaround (outdated)
- `test_pdb_load.py` - Test utility (redundant with test_workflow.py)

## 📂 DELETE - Old Temporary Directories
These are from failed attempts or old experiments:
- alphafold_md_results/
- alphafold_enzyme_substrate_md/
- all_laminarinase_structures/
- analysis_results/
- batch_md_results/
- esmfold_structures/
- fast_validation_results/
- known_structures_report/
- laminarinase_sequences/
- md_validation_results/
- predicted_activity_analysis/
- ranking_report/
- temp_download/
- test_outputs/
- uploads/

## 📊 Summary
- **KEEP scripts**: ~10 essential + alternatives
- **DELETE scripts**: ~25 obsolete/failed attempts
- **DELETE directories**: 15 old/temporary folders
- **Result**: Clean, maintainable codebase with alternatives available
