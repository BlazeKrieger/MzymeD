# TOP 5 CANDIDATES - EXPERIMENTAL VALIDATION PLAN

## Report Generated: 2026-01-18 21:54:34

---

## SELECTION SUMMARY

Selected based on comprehensive sequence-based activity predictions:
- **Activity Score**: Weighted combination of catalytic conservation, active site geometry, substrate specificity
- **Validation**: Compared against 20 experimentally characterized enzymes
- **Confidence**: HIGH - all candidates score >93/100

---

## TOP 5 CANDIDATES

### #1. ACU35625.1

**Activity Score**: 95.3/100

**Key Metrics**:
- Catalytic Conservation: 100.0
- Active Site Geometry: 100.0
- Substrate Specificity: 76.3
- Sequence Length: 648 aa
- Family: Unknown

**Rationale for Selection**:
- Elite activity prediction (95.3/100)
- Perfect catalytic residue conservation
- Optimal size for expression (648 aa)

**Family Notes**: N/A

**Expression Strategy**: Standard size - excellent E. coli expression expected

---

### #2. AOR29491.1

**Activity Score**: 94.6/100

**Key Metrics**:
- Catalytic Conservation: 100.0
- Active Site Geometry: 100.0
- Substrate Specificity: 72.9
- Sequence Length: 782 aa
- Family: Unknown

**Rationale for Selection**:
- Elite activity prediction (94.6/100)
- Perfect catalytic residue conservation

**Family Notes**: N/A

**Expression Strategy**: Moderate size - E. coli possible, insect cells recommended

---

### #3. BAF52916.1

**Activity Score**: 94.3/100

**Key Metrics**:
- Catalytic Conservation: 100.0
- Active Site Geometry: 100.0
- Substrate Specificity: 71.3
- Sequence Length: 750 aa
- Family: Unknown

**Rationale for Selection**:
- Elite activity prediction (94.3/100)
- Perfect catalytic residue conservation

**Family Notes**: N/A

**Expression Strategy**: Moderate size - E. coli possible, insect cells recommended

---

### #4. CAB01407.1

**Activity Score**: 94.2/100

**Key Metrics**:
- Catalytic Conservation: 100.0
- Active Site Geometry: 100.0
- Substrate Specificity: 70.8
- Sequence Length: 720 aa
- Family: Unknown

**Rationale for Selection**:
- Elite activity prediction (94.2/100)
- Perfect catalytic residue conservation

**Family Notes**: N/A

**Expression Strategy**: Moderate size - E. coli possible, insect cells recommended

---

### #5. ADU06434.1

**Activity Score**: 94.2/100

**Key Metrics**:
- Catalytic Conservation: 100.0
- Active Site Geometry: 100.0
- Substrate Specificity: 71.0
- Sequence Length: 599 aa
- Family: Unknown

**Rationale for Selection**:
- Elite activity prediction (94.2/100)
- Perfect catalytic residue conservation
- Optimal size for expression (599 aa)

**Family Notes**: N/A

**Expression Strategy**: Standard size - excellent E. coli expression expected

---

## RECOMMENDED EXPERIMENTAL WORKFLOW

### Phase 1: Gene Synthesis & Cloning (2-3 weeks)
1. Order synthetic genes from IDT/GenScript/Twist
   - Codon-optimize for E. coli
   - Include N-terminal His6-TEV tag
   - Add restriction sites for subcloning
2. Clone into expression vector (pET28a/pET22b)
3. Confirm sequence by Sanger sequencing

### Phase 2: Expression Optimization (2-4 weeks)
1. Transform into BL21(DE3), Rosetta2(DE3), or C41(DE3)
2. Test expression conditions:
   - Temperature: 18°C, 25°C, 37°C
   - IPTG concentration: 0.1-1.0 mM
   - Induction time: 4-20 hours
3. Analyze by SDS-PAGE (soluble vs insoluble)
4. Select optimal conditions

### Phase 3: Purification (1-2 weeks per protein)
1. **Step 1**: Ni-NTA affinity chromatography
   - Load cell lysate
   - Wash with 20 mM imidazole
   - Elute with 250 mM imidazole
2. **Step 2** (Optional): TEV protease cleavage
   - Dialyze into low-salt buffer
   - Add TEV protease (1:100 ratio)
   - Incubate overnight at 4°C
3. **Step 3**: Size exclusion chromatography
   - Superdex 200 16/600
   - Buffer: 20 mM Tris pH 8.0, 150 mM NaCl
   - Collect peak fractions
4. **Step 4**: Concentration & storage
   - Concentrate to 10-20 mg/mL
   - Flash freeze in liquid N2
   - Store at -80°C

### Phase 4: Biophysical Characterization (2-3 weeks)
1. **Quality Control**:
   - SDS-PAGE (purity >95%)
   - Mass spectrometry (sequence verification)
   - Dynamic light scattering (monodispersity)
2. **Stability Assessment**:
   - Differential scanning fluorimetry (Tm)
   - Thermal stability at different pH
3. **Substrate Binding**:
   - Isothermal titration calorimetry (Kd, ΔH, ΔS)
   - Surface plasmon resonance (kinetics)

### Phase 5: Enzyme Kinetics (3-4 weeks)
1. **Activity Assay Development**:
   - Substrate: Laminarin (Sigma)
   - Detection: Reducing sugar assay (DNS or PAHBAH)
   - Optimize conditions (pH, temperature, ionic strength)
2. **Kinetic Parameters**:
   - Michaelis-Menten: kcat, Km, kcat/Km
   - pH optimum (pH 4-9)
   - Temperature optimum (20-60°C)
3. **Substrate Specificity**:
   - Test panel: laminarin, lichenan, barley β-glucan, CMC
   - Calculate relative activities

### Phase 6: Structural Biology (3-6 months)
1. **Crystallization**:
   - Screen with commercial kits (JCSG+, PACT, ProPlex)
   - Optimize promising conditions
   - Co-crystallize with substrate analogs
2. **Data Collection**:
   - Synchrotron X-ray diffraction
   - Aim for <2.5 Å resolution
3. **Structure Determination**:
   - Molecular replacement (use PDB 2W52 as search model)
   - Model building and refinement
   - Validation (MolProbity, wwPDB)
4. **Structure Deposition**:
   - Submit to RCSB PDB
   - Prepare manuscript

---

## TIMELINE ESTIMATE

**Total: 6-12 months from gene synthesis to structure**

- Months 1-2: Cloning and expression optimization
- Months 2-3: Purification and initial characterization
- Months 3-5: Detailed kinetics and substrate specificity
- Months 6-12: Crystallization and structure determination

---

## BUDGET ESTIMATE (per protein)

- Gene synthesis: $400-800
- Expression/purification reagents: $500-1000
- Biophysical characterization: $1000-2000
- Kinetics assays: $500-1000
- Crystallization: $2000-5000
- Synchrotron beamtime: $0 (free access at many facilities)

**Total per protein: $4,400-9,800**
**For 5 proteins: $22,000-49,000**

---

## SUCCESS CRITERIA

✓ **Minimum**: At least 3/5 proteins express solubly and purify to >10 mg/mL
✓ **Good**: At least 2/5 show measurable activity on laminarin (kcat/Km > 10³ M⁻¹s⁻¹)
✓ **Excellent**: At least 1/5 crystallizes and structure determined to <2.5 Å

Based on sequence predictions, expecting 4/5 to meet minimum criteria.

---

## FILES GENERATED

- **Detailed JSON Report**: `top5_experimental_validation_plan.json`
- **Visual Summary**: `top5_experimental_validation.png`
- **This Report**: `TOP5_EXPERIMENTAL_PLAN.md`

---

**Report prepared by**: Laminarinase Structure Prediction Pipeline  
**Next step**: Review candidates and initiate gene synthesis orders
