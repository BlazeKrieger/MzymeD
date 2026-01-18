# MzymeD

AI-Powered Tool for Enzyme-Substrate Molecular Dynamics Analysis

## Overview

MzymeD is an advanced AI tool that analyzes enzyme-substrate interactions using:
- **ESM3** (or ESM2) for protein structure prediction from sequences
- **Molecular Dynamics** simulations for dynamic analysis
- **Active Site Identification** using contact predictions
- **3D Visualization** and animation of enzyme-substrate interactions
- **Optimization Suggestions** for residue mutations

## Features

- 📤 **File Upload**: Support for FASTA, PDB, CIF, and GenBank formats
- 🧬 **AI Structure Prediction**: Uses ESM models for protein structure from sequence
- 🔬 **Active Site Analysis**: Identifies key residues involved in catalysis
- 🎬 **3D Animation**: Creates animated visualizations of molecular dynamics
- 📊 **Interaction Analysis**: Quantifies enzyme-substrate binding strength
- 💡 **Optimization**: Suggests residue mutations to improve binding

## Installation

```bash
# Clone the repository
git clone https://github.com/BlazeKrieger/MzymeD.git
cd MzymeD

# Install dependencies
pip install -r requirements.txt

# For full ESM functionality
pip install fair-esm
```

## Quick Start

### Real Molecular Dynamics Simulation (Production-Ready) ✅

This is the **fastest way** to see real enzyme dynamics:

```bash
# 1. Run real MD simulation (100 ps with AMBER force field)
conda run -n mzymed python run_cleaned_md.py

# 2. Visualize the dynamics in PyMOL (50 frames)
conda run -n mzymed pymol md_simulation/real_md_trajectory.pdb

# 3. In PyMOL console, type:
show cartoon
mplay
```

**What you'll see:**
- Real thermal motion of the enzyme at 300K
- Backbone flexibility (~1.45 Å RMSD)
- Active site breathing motions
- Loop dynamics
- 100 ps of actual molecular dynamics using AMBER force field

**Output files:**
- `md_simulation/real_md_trajectory.pdb` - 50-frame trajectory
- `md_simulation/cleaned_structure.pdb` - cleaned protein structure
- `md_simulation/md_log.txt` - energy/temperature data

---

### Test with Laminarinases (81 Sequences) ✅

```bash
# 1. Test file loading from laminarinases folder
python test_laminarinases.py

# Output: ✓ Successfully loaded all 81 laminarinase sequences
# - GH16: 27 sequences
# - GH17: 5 sequences  
# - GH3: 1 sequence
# - GH55: 45 sequences
# - GH64: 3 sequences
```

---

### Download & Visualize Real Crystal Structures ✅

```bash
# 1. Download 4 real laminarinase-laminarin complexes from RCSB PDB
python run_real_md_simulation.py

# 2. View structures in PyMOL
conda run -n mzymed pymol real_structures/2W52.pdb

# Structures downloaded:
# - 2W52.pdb (1.56 Å resolution) - Laminarinase + laminarin
# - 2W39.pdb (1.1 Å resolution)  - Highest resolution
# - 4BPZ.pdb (1.13 Å resolution)
# - 4BOW.pdb (1.35 Å resolution)
```

---

### Web-Based 3D Visualization

```bash
# 1. Start web server
cd visual_outputs
conda run -n mzymed python -m http.server 8000

# 2. Open browser
# http://localhost:8000/mechanism.html

# Interactive features:
# - Play/pause animation
# - Frame-by-frame navigation
# - Zoom and rotate (scroll wheel, middle-drag)
# - 50-frame trajectory with enzyme dynamics
```

---

### Command Line Usage

```bash
# Run example analysis
python example_usage.py
```

### Web Interface

```bash
# Start the web server
python app.py

# Open browser to http://localhost:5000
```

### Python API

```python
from mzymed.app import MzymeDApp

# Initialize
app = MzymeDApp()

# Process enzyme sequence (e.g., laminarinase)
app.process_enzyme("laminarinase.fasta")

# Process substrate (e.g., laminarin)
app.process_substrate("laminarin.fasta")

# Analyze interactions
results = app.analyze_interactions()

# Get optimization suggestions
print(results['optimization_suggestions'])
```

## Use Cases

### Laminarinase-Laminarin Analysis

MzymeD can analyze the interaction between laminarinases (β-1,3-glucanases) and their substrate laminarin:

1. Upload laminarinase sequence (FASTA or PDB)
2. Upload laminarin structure
3. Identify active site residues
4. Visualize 3D structure with highlighted active site
5. Run molecular dynamics simulation
6. Get optimization suggestions for improved catalysis

## System Requirements

### Hardware
- **GPU**: NVIDIA GPU with CUDA compute capability 7.0+ (RTX 4060, RTX 3080, A100, etc.)
  - GPU acceleration: 1-5 minutes for 100 ps MD
  - CPU fallback available: 10-30 minutes for 100 ps MD

### Software
- **Python**: 3.10+
- **Conda**: For environment management
- **CUDA Toolkit**: 11.8+ (if using GPU)

### Environment Setup

```bash
# Create conda environment
conda create -n mzymed python=3.12 -y
conda activate mzymed

# Install core dependencies
pip install -r requirements.txt

# Install GPU support (CUDA 12.4)
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124

# Install OpenMM with CUDA support
conda install -c conda-forge openmm=8.2

# Install additional tools
conda install -c conda-forge pymol-open-source pdbfixer mdtraj -y
```

### Verify GPU Setup

```bash
# Check CUDA availability
python -c "import torch; print(f'GPU: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0)}')"

# Check OpenMM CUDA
python -c "from openmm import Platform; print([Platform.getPlatform(i).getName() for i in range(Platform.getNumPlatforms())])"
```

## Architecture

```
src/mzymed/
├── file_handler.py       # File upload and validation
├── models/
│   ├── esm_predictor.py  # ESM3 integration
│   └── md_simulator.py   # Molecular dynamics
├── analysis/
│   └── active_site.py    # Active site identification
├── visualization/
│   └── visualizer.py     # 3D visualization
└── app.py                # Main application
```

## Output Files Generated

### Real MD Simulation
```
md_simulation/
├── real_md_trajectory.pdb    # 50 frames (100 ps total)
├── cleaned_structure.pdb     # Prepared structure
└── md_log.txt               # Energy/temperature data
```

### Downloaded Crystal Structures
```
real_structures/
├── 2W52.pdb                 # Laminarinase + laminarin
├── 2W39.pdb                 # High resolution complex
├── 4BPZ.pdb                 # GH55 laminarinase
└── 4BOW.pdb                 # GH55 laminarinase
```

### Web Visualization
```
visual_outputs/
├── mechanism.html           # Interactive 3D viewer
├── catalysis_dynamics.pdb   # 50-frame animation
└── real_md_trajectory.pdb   # Real MD trajectory
```

## Troubleshooting

### No GPU detected
```bash
# Check CUDA installation
nvidia-smi

# Reinstall PyTorch with correct CUDA version
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124 --force-reinstall
```

### PDB parsing errors
- PDB files are automatically cleaned with PDBFixer
- Non-standard residues are removed
- Missing atoms and hydrogens are added automatically

### PyMOL not found
```bash
conda install -c conda-forge pymol-open-source -y
```

## Performance Benchmarks

**Hardware: NVIDIA RTX 4060 Laptop GPU**

| Task | Duration |
|------|----------|
| Load structure (PDBFixer) | ~30 sec |
| Energy minimization (500 steps) | ~15 sec |
| MD equilibration (2 ps) | ~5 sec |
| MD production (100 ps, 50 frames) | ~2-3 min |
| **Total** | **~3-4 minutes** |

RMSD Analysis: Average structural fluctuation **1.45 Å** (normal thermal motion)

## References

### Laminarinase Structure
- **Family**: GH16 (Carbohydrate-Active enZYmes)
- **Substrate**: β-1,3-glucans (laminarin, pustulan)
- **Mechanism**: Double-displacement with covalent intermediate
- **Catalytic residues**:
  - GLU107 - Nucleophile
  - ASP256 - General acid
  - TRP257 - Substrate binding
  - GLY49 - Active site loop

### References
- Becker et al. (2008) - GH16 structure and mechanism
- RCSB PDB - Crystal structures (2W52, 2W39, 4BPZ, 4BOW)
- OpenMM Manual - Molecular dynamics simulations

## Requirements

- Python 3.8+
- PyTorch (for ESM models)
- BioPython (for sequence handling)
- OpenMM (for MD simulations)
- py3Dmol (for 3D visualization)
- Flask (for web interface)

## Examples

See `example_laminarinase.fasta` for a sample enzyme sequence.

## Contributing

Contributions welcome! Please open an issue or PR.

## License

MIT License

## Citation

If you use MzymeD in your research, please cite:
```
MzymeD: AI-Powered Enzyme-Substrate Molecular Dynamics Analysis Tool
```

## Support

For questions or issues, please open a GitHub issue