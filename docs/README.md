#+#+#+#+ markdown
# 🧬 MzymeD

**AI-Powered Tool for Enzyme-Substrate Molecular Dynamics Analysis**

> Analyze enzyme-substrate interactions using AI structure prediction, molecular dynamics simulations,
 and 3D visualization. Perfect for researchers studying enzyme mechanisms, protein engineering, and drug design.
---

## 👋 New to MzymeD?

**📘 [Complete Beginner's Guide](BEGINNERS_GUIDE.md)** - Start here if you're new!

**Quick Links:**
- 🎓 **Beginners** → [Beginner's Guide](BEGINNERS_GUIDE.md)
- 🔬 **Researchers** → See features below
- 💻 **Developers** → [USAGE.md](USAGE.md)
- 🚀 **Try it now** → `python demo.py`

---

## 📋 Table of Contents

- [What is MzymeD?](#what-is-mzymed)
- [Quick Start (3 minutes)](#-quick-start-3-minutes)
- [Features](#-features)
- [Installation Guide](#-installation-guide)
- [Usage Examples](#-usage-examples)
- [Project Structure](#-project-structure)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)

---

## What is MzymeD?

MzymeD helps you understand how enzymes interact with their substrates by:

1. **Taking enzyme sequences** (like laminarinase) in FASTA or PDB format
2. **Predicting 3D structures** using AI (ESM2/ESM3 models)
3. **Running molecular dynamics** simulations to see real molecular motion
4. **Identifying active sites** where catalysis happens
5. **Creating 3D animations** you can view and share
6. **Suggesting mutations** to optimize enzyme activity

**Perfect for:** Biochemists, protein engineers, computational biologists, and students learning about
 enzyme mechanisms.
---

## ⚡ Quick Start (3 minutes)

### Option 1: See a Demo (No Installation Required)

```bash
# Clone the repository
git clone https://github.com/BlazeKrieger/MzymeD.git
cd MzymeD

# View the demo (shows all features)
python demo.py
```

### Option 2: Run Real Molecular Dynamics

```bash
# 1. Set up environment (one-time setup)
conda create -n mzymed python=3.10 -y
conda activate mzymed
pip install -r requirements.txt

# 2. Run a real MD simulation
python run_cleaned_md.py

# 3. View the animation in PyMOL
conda install -c conda-forge pymol-open-source -y
pymol md_simulation/real_md_trajectory.pdb
```

**What you'll see:** A 50-frame animation showing real enzyme movement at 300K over 100 picoseconds!  

### Option 3: Web Interface

```bash
# Start the web server
python app.py

# Open in browser: http://localhost:5000
# Upload your enzyme FASTA file and analyze!
```

---

## ✨ Features

| Feature | Description | Use Case |
|---------|-------------|----------|
| 📤 **File Upload** | FASTA, PDB, CIF, GenBank formats | Upload any enzyme sequence |
| 🧬 **AI Prediction** | ESM2/ESM3 structure prediction | Get 3D structure from sequence alone |      
| 🔬 **Active Site ID** | Automatic detection of catalytic residues | Find where chemistry happens |  
| 🎬 **3D Animation** | Interactive molecular dynamics movies | See enzyme motion in real-time |      
| 📊 **Interaction Analysis** | Quantify binding strength | Compare different substrates |
| 💡 **Optimization** | Suggest beneficial mutations | Engineer better enzymes |

---

---

## 📦 Installation Guide

### Prerequisites

- **Operating System:** Windows 10/11, macOS, or Linux
- **Python:** 3.8 or higher (3.10 recommended)
- **Storage:** 5 GB free space
- **RAM:** 8 GB minimum (16 GB recommended)
- **GPU (Optional):** NVIDIA GPU with CUDA for faster simulations

### Step-by-Step Installation

#### 1. Install Conda (If You Don't Have It)

**Windows/macOS/Linux:**
```bash
# Download Miniconda from: https://docs.conda.io/en/latest/miniconda.html
# Or use the command line:
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

#### 2. Clone the Repository

```bash
git clone https://github.com/BlazeKrieger/MzymeD.git
cd MzymeD
```

#### 3. Create Environment and Install Dependencies

```bash
# Create a new conda environment
conda create -n mzymed python=3.10 -y

# Activate the environment
conda activate mzymed

# Install required packages
pip install -r requirements.txt

# Install ESM for AI structure prediction (optional but recommended)
pip install fair-esm

# Install OpenMM for molecular dynamics
conda install -c conda-forge openmm=8.2 -y

# Install PyMOL for visualization (optional)
conda install -c conda-forge pymol-open-source -y
```

#### 4. Verify Installation

```bash
# Check if everything is installed correctly
python -c "import openmm; print('OpenMM:', openmm.__version__)"
python -c "import Bio; print('BioPython:', Bio.__version__)"
python -c "import torch; print('PyTorch:', torch.__version__)"
```

✅ If you see version numbers, you're ready to go!

### GPU Setup (Optional - For Faster Simulations)

If you have an NVIDIA GPU:

```bash
# Install CUDA-enabled PyTorch
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Verify GPU is detected
python -c "import torch; print('GPU Available:', torch.cuda.is_available())"
```

---

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