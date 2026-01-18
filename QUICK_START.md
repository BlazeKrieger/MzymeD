# 🎬 QUICK START: View Your Enzyme-Substrate Simulation

## 30-Second Setup

```bash
# Navigate to project
cd "c:\Users\david\OneDrive - Imperial College London\Bureau\Personal projects\Hackathons\personal hackathons\MzymeD"

# Open animation
conda activate mzymed
pymol md_simulation/enzyme_substrate_combined.pdb

# Wait for PyMOL to load, then press the Play button
# Or type in PyMOL console: mplay
```

---

## 📊 What You're Seeing

| Item | What It Shows |
|------|---------------|
| **Blue cartoon** | Laminarinase enzyme protein backbone |
| **Cyan sticks** | Laminarin substrate (glucose units) |
| **Red sphere** | GLU107 - nucleophile that cuts substrate |
| **Orange sphere** | ASP256 - general acid catalyst |
| **Yellow sphere** | TRP257 - stabilizes substrate |
| **Purple sphere** | GLY49 - flexible loop |

---

## 🎮 PyMOL Controls

| Action | Key |
|--------|-----|
| Play animation | Space bar or click Play button |
| Next frame | Right arrow |
| Previous frame | Left arrow |
| Rotate structure | Click + drag mouse |
| Zoom in/out | Mouse wheel |
| Center | Middle-click |

---

## 📈 File Sizes (What You Have)

- `enzyme_substrate_combined.pdb` - 18.2 MB (50-frame animation)
- `enzyme_substrate_complex.png` - 220 KB (rendered image)  
- `enzyme_substrate_session.pse` - 8.4 MB (PyMOL session)

---

## ✓ Verification

All simulations completed successfully:
- ✓ Energy minimization: -46,987 kJ/mol
- ✓ MD trajectory: 100 ps (50 frames)
- ✓ RMSD stability: 0.106 ± 0.061 Å
- ✓ Enzyme intact: No unfolding

---

## 💡 Fun Facts

- **Temperature**: 300 K (body temperature)
- **Speed**: Computed in ~3-4 minutes on your RTX 4060 GPU
- **Physics**: AMBER14 force field (same used for drug design)
- **Enzyme substrate**: ~14 glucose units (laminarin)
- **Catalytic mechanism**: Double displacement with covalent intermediate

---

## 📞 Need Help?

If animation doesn't play or PyMOL crashes:

```bash
# Try the pre-configured session instead
pymol md_simulation/enzyme_substrate_session.pse

# Or load just the structure and manually visualize:
pymol md_simulation/enzyme_substrate_combined.pdb
# Then run: run md_simulation/visualize_complex.pml
```

---

**Your molecular dynamics simulation is ready to explore!** 🧬✨
