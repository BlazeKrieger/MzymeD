# Final Codebase Cleanup Plan

## Root-Level File Organization Status

### DANGEROUS: Many files still in root directory!
The root contains 40+ active files. Goal: Move ALL to organized folders (scripts/, results/, data/, docs/)

---

## Root Scripts to DELETE (Failed/Obsolete - 23 files)

### Failed MD Attempts (11 files):
❌ run_enzyme_affinity_assessment.py - AMBER force field terminal group errors
❌ run_enzyme_affinity_assessment_v2.py - CHARMM API incompatibility 
❌ run_enzyme_substrate_final.py - Substrate connectivity issues
❌ run_enzyme_substrate_hybrid.py - Mixed approach failed
❌ run_enzyme_substrate_simple.py - Still substrate issues
❌ unbound_substrate_md.py - Substrate generation failed
❌ validate_esmfold_structures_md.py - ESMFold integration failed
❌ validate_ranking_dynamic_features.py - Dynamic features approach failed
❌ md_validation_all_laminarinases.py - Old validation script
❌ md_validation_with_hydrogens.py - Hydrogen addition approach failed
❌ download_all_pdb_laminarinases.py - Replaced by better download method

### Failed Analysis Attempts (8 files):
❌ complete_ml_prediction.py - ML pipeline failed
❌ compare_predicted_and_known.py - Comparison approach superseded
❌ compare_static_vs_activity.py - Static analysis approach failed
❌ analyze_all_laminarinases.py - Redundant analysis
❌ analyze_binding_sites.py - Binding site approach not working
❌ assess_glucanase_activity.py - Different enzyme family
❌ search_all_laminarinases.py - Old search method
❌ predict_top_candidates_esmfold.py - ESMFold approach abandoned

### Utility Clutter (4 files):
❌ demo.py - Demo file
❌ example_usage.py - Example file (kept in docs)
❌ reconstruct_atoms_from_ca.py - Experimental utility
❌ reconstruct_backbone_v2.py - Experimental utility
❌ simple_backbone_add.py - Experimental utility

### Files to DELETE (12 prediction scripts - likely superseded):
❌ predict_enzymes.py - Superseded
❌ predict_laminarinase_structures.py - Old approach
❌ predict_structures_advanced.py - Multiple variants
❌ predict_structures_gpu.py - Multiple variants
❌ predict_structures_proper.py - Multiple variants
❌ predict_structures_gpu.py - Duplicate
❌ prepare_alphafold_batch.py - Old batch prep
❌ colabfold_colab_script.py - Old script version
❌ setup_structure_prediction.py - Old setup
❌ compare_enzyme_affinity.py - Redundant comparison
❌ fast_stability_analysis.py - Old stability script
❌ fast_validation_comparison.py - Old validation

### Other Obsolete (4 files):
❌ assess_predicted_structures.py - Old assessment
❌ download_structures.py - Redundant download
❌ run_simulation.py - Old simulation runner

---

## Directories/Archives to DELETE (7 items)

❌ outputs/ - Old output directory
❌ predicted_structures/ - Old predictions (should be in results/)
❌ glucanase_activity_analysis/ - Wrong enzyme family
❌ experimental_validation_plan/ - Incomplete old plan
❌ forcefields/ - Old force field configs
❌ visual_outputs/ - Old visualizations (moved to results/)
❌ *.zip - Old archives (results-20260123*.zip, laminarinases.zip)
❌ *.log - Build/run logs (batch_md_live.log, alphafold_md_batch.log, etc.)
❌ *.pse - Old PyMOL sessions (first_enzyme_substrate_md.pse)

---

## Log Files to DELETE (6 files)

❌ batch_md_live.log
❌ batch_md_results.log
❌ batch_run_fixed.log
❌ complete_prediction.log
❌ predict_gpu.log
❌ regenerate_gpu.log
❌ structure_prediction.log
❌ structure_predictions_full.log

---

## JSON Files to Evaluate

MOVE to results/analysis/ (if important):
- comprehensive_laminarinase_ranking.json
- comprehensive_pdb_search_results.json
- enzyme_affinity_comparison.json
- prediction_gpu_results.json
- prediction_results.json
- structure_predictions.json
- structure_predictions_advanced.json

PNG Images to MOVE to results/analysis/:
- comprehensive_laminarinase_ranking.png
- enzyme_affinity_comparison.png
- md_validation_evidence_summary.png
- static_vs_activity_comparison.png

---

## Notebooks to MOVE to scripts/

- colabfold_batch_prediction.ipynb → scripts/analysis/

---

## Summary Statistics

**Total files to DELETE: ~50 items**
- Scripts: 35 failed/obsolete
- Directories: 7
- Logs: 6+
- Archives: 2

**Root directory will be cleaned from 80+ items to ~10 key items (docs + config pointers)**

---

## Execution Order

1. Move root scripts → scripts/{analysis,md,utilities}/
2. Move root JSON/PNG → results/analysis/
3. Move notebooks → scripts/analysis/
4. Delete all obsolete scripts
5. Delete all obsolete directories
6. Delete all log files
7. Delete all archives
8. Verify results/ and scripts/ are complete
9. Update documentation with new structure

---

## Keep in Root (only):
- .git/ (version control)
- .gitignore (git ignore)
- .pytest_cache/ (test cache)
- scripts/ (organized scripts)
- results/ (organized results)
- data/ (organized data)
- docs/ (organized documentation)
- config/ (organized config)
- src/ (source code)
- tests/ (test suite)
- README.md (main entry point)
- setup.py (package setup)
- requirements.txt (dependencies)
- INDEX.md (quick reference)
- PROJECT_STRUCTURE.md (structure guide)
- README_NEW_STRUCTURE.md (organization guide)

