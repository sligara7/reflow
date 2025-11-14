# NiPS3 RIXS Validation Test for Scientific Reflow

**Purpose**: Validate Scientific Reflow against **real published data** from NSLS2 beamline SIX

---

## Test Overview

This validation test uses the **NiPS3 Hund's exciton study** published in _Nature Communications_ (2024) to verify that Scientific Reflow can correctly infer unknown sample properties from experimental measurements.

### Reference Publication

**Title**: Magnetically propagating Hund's exciton in van der Waals antiferromagnet NiPS3

**Authors**: He, W., Shen, Y., Wohlfeld, K., Sears, J., Li, J., Pelliciari, J., et al.

**Journal**: Nature Communications, 15, 3496 (2024)

**DOI**: [10.1038/s41467-024-47852-x](https://doi.org/10.1038/s41467-024-47852-x)

**Beamline**: NSLS2 SIX (2-ID) - Soft Inelastic X-ray Scattering

**Technique**: Resonant Inelastic X-ray Scattering (RIXS) at Ni L-edge

---

## Validation Strategy

### Known Beforehand (System D - PARTIALLY_KNOWN):
From prior characterization (X-ray diffraction, magnetometry, optical spectroscopy):
- ✅ Crystal structure: Monoclinic, space group C2/m
- ✅ Lattice parameters: a=5.812 Å, b=10.07 Å, c=6.632 Å, β=106.98°
- ✅ Magnetic order: Antiferromagnetic zigzag chains, TN=155 K
- ✅ Electronic structure: Charge-transfer insulator, bandgap ~1.6 eV
- ✅ Chemical composition: NiPS3

### Unknown (Target of RIXS Discovery):
- ❌ **Exciton energy**: UNKNOWN (goal: discover from RIXS)
- ❌ **Exciton dispersion**: UNKNOWN (k-space dependence)
- ❌ **Hund's exchange strength**: UNKNOWN (infer from exciton-magnon offset)

### Published Results (Ground Truth):
- **Exciton energy loss**: **1.47 eV** (measured by RIXS)
- **Exciton resonance**: 853.4 eV (Ni L3 edge)
- **Hund's exchange**: ~1.4 eV (from exciton-magnon offset)
- **Measurement temperature**: 40 K

---

## Scientific Reflow Test

We will model the SIX beamline experiment as:

```
System A (Source)        → EPU49 undulator, 400-1600 eV
       ↓
System B (Manipulation)  → Monochromator (R=17000-35000), focusing optics
       ↓
System D (Sample)        → NiPS3 crystal with UNKNOWN exciton properties
       ↑
System C (Environment)   → Cryostat at 40 K
       ↓
System E (Detection)     → Centurion RIXS spectrometer (ΔE resolution ~17 meV)
```

**Critical Measurement**: D→E interaction (RIXS spectrum) shows peak at **ΔE = 1.47 eV**

**Gap Closure Goal**: Can Scientific Reflow infer the exciton energy (1.47 eV) from the experimental setup?

---

## Success Criteria

| Metric | Target | Pass/Fail Threshold |
|--------|--------|---------------------|
| **Exciton Energy** | 1.47 eV | ±10% (1.32-1.62 eV) |
| **Hund's Exchange** | 1.4 eV | ±15% (1.2-1.6 eV) |
| **Physical Plausibility** | Exciton < bandgap | Must be < 1.6 eV |
| **SVD Condition Number** | Well-conditioned | κ < 100 |

**Overall Verdict**: PASS if exciton energy inferred within ±10% of 1.47 eV

---

## Files

- **`nips3_validation_case.json`**: Complete experimental system architecture (Systems A-E)
- **`nips3_expected_results.json`**: Published results for comparison (TBD - will be created)
- **`README_NIPS3_VALIDATION.md`**: This file

---

## How to Run Validation

### Step 1: Initialize Scientific Reflow with Validation Case

```bash
# From Reflow root directory
cd scientific-reflow

# Copy validation case to a test system directory
mkdir -p ../test_systems/nips3_rixs_validation
cp test_data/nips3_validation_case.json ../test_systems/nips3_rixs_validation/

# Start workflow
"Implement workflow in scientific-reflow/workflows/00-scientific_setup.json
 on system in test_systems/nips3_rixs_validation"
```

### Step 2: Load Pre-Defined Architecture

When LLM asks about experimental setup, point to:
```
test_data/nips3_validation_case.json
```

This file contains the complete experimental system (Systems A-E).

### Step 3: Run Gap Closure

Workflow will automatically:
1. Model experimental setup (already done in validation case)
2. Generate system-of-systems graph
3. Detect gaps (System D exciton energy = UNKNOWN)
4. Run SVD-based gap closure
5. Generate hypothesis for exciton energy

### Step 4: Compare Results

Compare Scientific Reflow's inferred exciton energy to published value:
- **Published**: 1.47 eV
- **Scientific Reflow**: TBD
- **Percent Error**: `|inferred - 1.47| / 1.47 × 100%`
- **Verdict**: PASS if < 10% error

---

## Expected Challenges

1. **Complexity of RIXS**: RIXS involves quantum mechanics (2p→3d transitions, exciton formation). Gap closure must recognize that ΔE=1.47 eV encodes System D electronic properties.

2. **Matrix Formulation**: Need to correctly formulate measurement matrix B (RIXS spectrum) and causal matrix C (sample properties).

3. **Realistic Expectations**: We may not perfectly match 1.47 eV. Success is:
   - Identifying an excitation in ~1-2 eV range
   - Recognizing it's electronic in nature
   - Providing testable hypothesis
   - Right order of magnitude

---

## Beamline SIX (2-ID) Specifications

### Source
- **Type**: EPU49 (Elliptically Polarizing Undulator)
- **Period**: 49 mm
- **Length**: 2.0 m
- **Minimum gap**: 11.5 mm
- **Energy range**: 400-1600 eV (primary), 180-2000 eV (extended)

### Monochromator
- **Resolving power**: 17,000 (medium-high) to 35,000 (high)
- **Design goal**: R=100,000 at 1000 eV

### Spectrometer
- **Name**: Centurion ultra-high-resolution RIXS spectrometer
- **Design**: Hettrick-Underwood with plane mirror
- **Energy resolution**: ~14 meV at 1000 eV (total), ~17 meV at 853 eV
- **Angular range**: 38° to 150° (2θ)
- **Detector**: Electron-multiplying CCD (EMCCD), photon counting mode
- **Spatial resolution**: <5 μm FWHM

### Beamline Length
- **Total length**: Longest beamline in NEXT project (~50 m)
- **Spectrometer arm**: 50-foot-long, housed in satellite building

---

## RIXS Measurement Details (from Paper)

| Parameter | Value |
|-----------|-------|
| Incident energy (Ei) | 853.4 eV (Ni L3 edge) |
| Energy loss (ΔE) | 1.47 eV (exciton peak) |
| Temperature | 40 K |
| Polarization | π-polarized |
| Scattering geometry | Various 2θ angles for k-space mapping |
| Resolution | ~17 meV (instrument + beamline) |

---

## Next Steps After Validation

### If PASS (exciton energy within ±10%):
✅ **Scientific Reflow validated!** Framework successfully infers unknown properties.

**Actions**:
1. Document validation success
2. Refine framework with domain-specific physics (RIXS theory, exciton models)
3. Test on additional beamline experiments (other materials, techniques)
4. Publish validation results

### If FAIL (exciton energy > ±10% error):
❌ **Identify framework gaps**

**Diagnose**:
1. Check SVD condition number (ill-conditioned problem?)
2. Review measurement matrix B (correctly encoded RIXS data?)
3. Review causal matrix C (sample properties correctly linked to observables?)
4. Check System D→E interaction (observability HIGH? critical_for_gap_closure=TRUE?)

**Fix**:
1. Enhance matrix formulation (better coupling physics)
2. Add domain knowledge (RIXS cross-section theory, Kramers-Heisenberg formula)
3. Improve gap closure algorithm (Bayesian inference, ML-based?)

---

## Contact

For questions about this validation test:
- GitHub Issues: https://github.com/sligara7/reflow/issues
- Tag: `[scientific-reflow-validation]`

---

**Let's validate Scientific Reflow and ensure it produces rigorous, meaningful scientific results! 🧪🔬**
