# 🧬 MzymeD - Complete Beginner's Guide

**AI-Powered Tool for Enzyme-Substrate Molecular Dynamics Analysis**

---

## 📖 What is MzymeD? (In Simple Terms)

MzymeD is software that helps you study how enzymes work using your computer. No lab needed!

**What it does:**
1. **Takes your enzyme sequence** → From a FASTA file (like from UniProt)
2. **Predicts 3D structure** → Uses AI models (ESM2/ESM3)
3. **Simulates movement** → Shows how molecules move
4. **Finds active sites** → Where the enzyme does chemistry
5. **Creates animations** → 3D movies you can share
6. **Suggests mutations** → Ways to improve the enzyme

**Who should use this:**
- 🎓 Students learning enzyme mechanisms
- 🔬 Researchers studying proteins
- 🧪 Protein engineers
- 💊 Drug designers

---

## ⚡ 10-Minute Quick Start

### Step 1: Installation (5 min)

```bash
# Download the code
git clone https://github.com/BlazeKrieger/MzymeD.git
cd MzymeD

# Create environment (keeps packages organized)
conda create -n mzymed python=3.10 -y
conda activate mzymed

# Install required packages
pip install -r requirements.txt
```

### Step 2: See Demo (2 min)

```bash
python demo.py
```

Shows all features without running heavy computations.

### Step 3: Run Real Analysis (3 min)

```bash
python example_usage.py
```

Analyzes the included laminarinase enzyme and shows you the results.

---

## 📚 Step-by-Step Tutorials

### Tutorial 1: Analyze Your Own Enzyme

**Goal:** Get the 3D structure and active site of your enzyme

**Steps:**
1. Get your enzyme sequence from UniProt or GenBank (FASTA format)
2. Save it as `my_enzyme.fasta` in the MzymeD folder
3. Create this Python script (`my_analysis.py`):

```python
from mzymed.app import MzymeDApp

app = MzymeDApp()
app.process_enzyme("my_enzyme.fasta")
results = app.analyze_interactions()

print(f"Active site residues: {results['active_site_residues']}")
```

4. Run it: `python my_analysis.py`

### Tutorial 2: Run Molecular Dynamics

**Goal:** See enzyme movement at body temperature

```bash
python run_cleaned_md.py  # Takes 3-5 minutes
pymol md_simulation/real_md_trajectory.pdb  # View result
```

### Tutorial 3: Web Interface (No Coding!)

**Goal:** Use a browser-based interface

```bash
python app.py
# Open http://localhost:5000 in your browser
```

---

## 🔧 Troubleshooting

### Problem: "Module not found"

**Solution:**```bash
conda install pymol-open-source -c conda-forge
```

---

## ❓ FAQ

**Q: Need powerful computer?** No! 8GB RAM laptop works  
**Q: Use my enzyme?** Yes, FASTA format  
**Q: How long?** 1-10 minutes  
**Q: Free?** Yes, MIT License  
**Q: Need programming?** No! Use web interface

---

## 📖 Resources

**Where to get sequences:**
- UniProt: https://www.uniprot.org/
- RCSB PDB: https://www.rcsb.org/
- GenBank: https://www.ncbi.nlm.nih.gov/

**Learn more:**
- See README.md for advanced features
- Check USAGE.md for API documentation
- View examples in the `scripts/` folder

---

## 🎯 Next Steps

After mastering the basics:

1. Try the 81 included laminarinase sequences
2. Run comparative analysis on multiple enzymes
3. Explore advanced MD features
4. Create custom visualizations
5. Contribute to the project!

---

**Happy enzyme analysis! 🧬✨**
