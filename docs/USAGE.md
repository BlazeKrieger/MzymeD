# MzymeD Usage Guide

> 📘 **New user?** Check [BEGINNERS_GUIDE.md](BEGINNERS_GUIDE.md) for step-by-step tutorials

## Installation
```bash
pip install -r requirements.txt
pip install fair-esm torch  # Optional for full ESM functionality
```

## Quick Start
```bash
python demo.py              # See demo
python example_usage.py     # Run analysis
python app.py               # Web UI at http://localhost:5000
```

## Python API
```python
from mzymed.app import MzymeDApp

app = MzymeDApp()
app.process_enzyme("enzyme.fasta")
results = app.analyze_interactions()
```

## Supported Formats
- FASTA (.fasta, .fa)
- PDB (.pdb)
- CIF (.cif)
- GenBank (.gb)

## Output
Results saved in `outputs/` directory
