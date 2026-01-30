# MzymeD - Project Summary

## What Has Been Built

A complete AI-powered tool for analyzing enzyme-substrate molecular dynamics with ESM3 integration.

## Core Components

1. **File Handler** - Upload and validate FASTA, PDB, CIF files
2. **ESM Predictor** - AI-powered structure prediction using ESM3/ESM2
3. **MD Simulator** - Molecular dynamics simulations with OpenMM
4. **Active Site Analyzer** - Identify catalytic residues and binding sites
5. **Visualizer** - Generate 3D animations of molecular dynamics
6. **Web Interface** - Flask-based web application

## Quick Start

```bash
python demo.py              # Interactive demo
python example_usage.py     # Run laminarinase analysis
python app.py               # Web UI at localhost:5000
```

## Key Features

✓ File upload for enzymes (laminarinases) & substrates (laminarin)
✓ ESM3/ESM2 structure prediction from sequence
✓ Active site identification via contact prediction
✓ Molecular dynamics simulations
✓ 3D visualization & trajectory animation
✓ Residue optimization suggestions
✓ Flask web interface

## Example Workflow

1. Upload laminarinase sequence (FASTA)
2. ESM predicts 3D structure
3. Identify active site residues
4. Run MD simulation
5. Create 3D animation
6. Get optimization suggestions

## Tests

```bash
python tests/test_basic.py
```

All tests pass ✓
