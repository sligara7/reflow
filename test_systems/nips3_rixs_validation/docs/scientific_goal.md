# Scientific Goal: NiPS3 RIXS Validation Test

**Date**: 2025-11-14
**Facility**: NSLS2
**Beamline**: SIX (2-ID) - Soft Inelastic X-ray Scattering
**Technique**: Resonant Inelastic X-ray Scattering (RIXS)

---

## Experiment Description

### What facility/beamline are we using?
**NSLS2 Beamline SIX (2-ID)** - The Soft Inelastic X-ray Scattering beamline at Brookhaven National Laboratory's National Synchrotron Light Source II.

### What are we trying to discover?
We are trying to discover the **electronic excitation spectrum** of NiPS3, specifically:
- **Exciton energy** and dispersion
- **Hund's exchange interaction** strength
- **Electronic structure** and correlation effects

### What sample/system is under investigation?
**NiPS3 (Nickel Phosphorus Trisulfide)** - A van der Waals layered antiferromagnetic material with:
- Known crystal structure (Monoclinic C2/m)
- Known magnetic ordering (TN = 155 K)
- **Unknown** electronic excitation properties

### What measurements will be performed?
**RIXS measurements at the Ni L-edge** (853.4 eV):
- Measure inelastically scattered X-rays
- Map energy loss spectrum (0-3 eV range)
- Identify electronic excitations (excitons, magnons)
- Measure k-space dispersion (various scattering angles)

---

## Knowledge Gaps

### What properties of System D (sample) are UNKNOWN?

1. **Exciton Energy** (PRIMARY TARGET):
   - Energy of the Hund's exciton (energy loss in RIXS spectrum)
   - **Ground Truth** (from published paper): 1.47 eV
   - **Scientific Reflow Goal**: Infer this value from experimental setup

2. **Exciton Dispersion**:
   - How exciton energy varies with momentum (k-space)
   - Bandwidth and propagation characteristics

3. **Hund's Exchange Interaction**:
   - Strength of Hund's coupling (~1.4 eV from published data)
   - Role in exciton formation and propagation

4. **Exciton-Magnon Coupling**:
   - Relationship between exciton and magnetic excitations
   - Energy offset (~1.4 eV indicates Hund's exchange dominance)

---

## Success Criteria

### What would constitute successful gap closure?

**Primary Success Criterion**:
✅ **Infer exciton energy within ±10% of published value (1.47 eV)**
- Acceptable range: **1.32 - 1.62 eV**

**Secondary Success Criteria**:
- Identify the excitation as **electronic in nature** (not phonon/magnon)
- Recognize the role of **Hund's exchange** interaction
- Propose physically plausible hypotheses (exciton energy < bandgap of 1.6 eV)
- Generate **testable predictions** for validation

**Validation Metrics**:
- **SVD condition number**: κ < 100 (well-conditioned problem)
- **Confidence level**: HIGH or MEDIUM (not LOW)
- **Physical plausibility**: All constraints satisfied

---

## Validation Context

This is a **validation test** of Scientific Reflow using real published data:

**Reference**: He, W., et al. "Magnetically propagating Hund's exciton in van der Waals antiferromagnet NiPS3." _Nature Communications_ 15, 3496 (2024). DOI: 10.1038/s41467-024-47852-x

**Known Beforehand** (from prior characterization):
- Crystal structure: Monoclinic C2/m, a=5.812 Å, b=10.07 Å, c=6.632 Å
- Magnetic order: Antiferromagnetic, TN=155 K
- Electronic structure: Charge-transfer insulator, bandgap ~1.6 eV

**Discovered by RIXS** (ground truth):
- **Exciton energy: 1.47 eV** ← Target for Scientific Reflow
- Resonance at 853.4 eV (Ni L3 edge)
- Hund's exchange: ~1.4 eV

**Success = Scientific Reflow infers exciton energy close to 1.47 eV!** 🎯
