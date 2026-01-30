# Enzyme-Substrate Affinity Assessment: MD with Laminarin

**Status**: 🔄 Running MD simulations (background process)

## Workflow Overview

### 1. **Substrate Preparation**
- **Compound**: Laminarin (β-1,3-glucan oligosaccharide)
- **Structure**: Simplified linear glucose polymer (32 units)
- **Position**: Placed 30 Å from enzyme active site
- **Force Field**: AMBER14 + GBN2 implicit solvent

### 2. **Complex Preparation**
For each of 20 predicted laminarinase structures:
1. Load cleaned enzyme structure
2. Create laminarin substrate mock structure
3. Combine topologies (enzyme + substrate)
4. Position substrate for initial interaction
5. Add hydrogens with force field
6. Create molecular system

### 3. **MD Simulation Protocol**
- **Minimization**: Energy optimization (500 iterations)
- **Equilibration**: 2 ps heating to 300K
- **Production**: 100 ps MD (50,000 steps × 2 fs)
- **Platform**: CUDA GPU or CPU fallback
- **Temperature**: 300K (physiological)
- **Implicit Solvent**: GBN2 (fast, no explicit water needed)

### 4. **Affinity Metrics**
For each trajectory, calculating:
- **RMSD**: Enzyme backbone stability (Cα atoms)
- **Enzyme-Substrate Distance**: Minimum and final distances
- **Affinity Score**: Composite metric (0-100)
  - Based on: RMSD stability + substrate proximity
  - HIGH (>70), MODERATE (50-70), LOW (<50)
- **Trajectory Frames**: 50 frames (every 1 ps)

## Expected Results

### Outputs
- `alphafold_enzyme_substrate_md/`
  - `{enzyme_name}_es_md_trajectory.pdb` - Trajectory file
  - `{enzyme_name}_es_affinity.json` - Metrics per enzyme
  - `{enzyme_name}_es_md.log` - Energy progression
  - `es_affinity_ranking.json` - Top candidates ranked

### Top Candidates (Expected)
Will rank by:
1. **Affinity Score** (binding propensity)
2. **Enzyme Stability** (RMSD < 3 Å)
3. **Close Contact** (min distance < 5 Å)

## Quality Thresholds

| Metric | Good | Acceptable | Poor |
|--------|------|-----------|------|
| **Affinity Score** | >70 | 50-70 | <50 |
| **RMSD (Å)** | <2 | 2-4 | >4 |
| **Min Distance (Å)** | <5 | 5-8 | >8 |
| **Stability** | Converged | Drifting | Unstable |

## Estimated Runtime
- Per structure: 8-15 minutes (depending on size)
- Total batch: 160-300 minutes (~3-5 hours)
- Running on: RTX 4060 (8GB VRAM) with CUDA

## Interpreting Results

### Affinity Score
- **>80**: Excellent substrate binding (prioritize for experimental testing)
- **70-80**: Good binding (likely active)
- **60-70**: Moderate binding (may need optimization)
- **<60**: Weak binding (lower priority)

### Enzyme Stability
- **RMSD < 1 Å**: High stability
- **RMSD 1-2 Å**: Good stability
- **RMSD 2-3 Å**: Acceptable flexibility
- **RMSD > 3 Å**: Significant structural change

### Enzyme-Substrate Contact
- **< 3 Å**: Very close contact (likely binding)
- **3-5 Å**: Contact range (possible interaction)
- **5-8 Å**: Near contact (weak interaction)
- **> 8 Å**: No interaction

## Next Steps
1. Wait for MD batch to complete
2. Review `es_affinity_ranking.json` for top candidates
3. Analyze trajectories of top 5 structures
4. Generate visualization of enzyme-substrate complexes
5. Make experimental validation recommendations

---

**Script**: `run_enzyme_substrate_affinity_md.py`  
**Started**: 2026-01-23  
**Status**: In Progress ⏳
