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