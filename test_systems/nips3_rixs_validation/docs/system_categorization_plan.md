# System Categorization Plan

**Framework**: Experimental Scientific Systems (ESS)
**5-System Model**: A (Source) → B (Manipulation) → D (Sample) → E (Detection), with C (Environment) → D

---

## System A: Source (KNOWN)

**Components**:
- **EPU49 Undulator**

**Properties**:
- Type: Elliptically Polarizing Undulator
- Length: 2.0 m, Period: 49 mm
- Energy range: 400-1600 eV
- Flux: ~10¹³ photons/sec
- Knowledge state: **KNOWN** (fully characterized)

**Role**: Generate soft X-ray photons for RIXS

---

## System B: Manipulation (KNOWN)

**Components**:
- **Monochromator** (energy selection)
- **Focusing Optics** (beam conditioning)

**Properties**:
- Monochromator: R = 17,000 - 35,000, selects 853.4 eV
- Focusing: KB mirrors, focal spot ~10-50 μm
- Knowledge state: **KNOWN** (calibrated optics)

**Role**: Select incident energy (Ni L-edge) and focus beam onto sample

---

## System C: Environment (KNOWN)

**Components**:
- **Cryostat** (temperature control)

**Properties**:
- Temperature: 40 K (measurement)
- Range: 10-300 K
- Stability: ±0.5 K
- Knowledge state: **KNOWN** (measured and controlled)

**Role**: Cool sample to 40 K (< TN = 155 K) to study antiferromagnetic state

---

## System D: Sample - **KNOWLEDGE GAP** (UNKNOWN)

**Component**:
- **NiPS3 Single Crystal**

**Known Properties** (from prior characterization):
- Crystal structure: Monoclinic C2/m
- Lattice parameters: a=5.812 Å, b=10.07 Å, c=6.632 Å
- Magnetic order: Antiferromagnetic, TN=155 K
- Bandgap: ~1.6 eV

**UNKNOWN Properties** (target of RIXS discovery):
- ❌ **Exciton energy** ← PRIMARY GOAL (published: 1.47 eV)
- ❌ **Exciton dispersion**
- ❌ **Hund's exchange strength**

**Knowledge state**: **PARTIALLY_KNOWN** (structure known, excitations unknown)

**Role**: The sample under investigation - **THIS IS THE KNOWLEDGE GAP!**

---

## System E: Detection (KNOWN)

**Components**:
- **Centurion RIXS Spectrometer**
- **EMCCD Detector**

**Properties**:
- Spectrometer arm: 50 feet long
- Resolving power: 100,000 at 1000 eV (design)
- Energy resolution: ~17 meV at 853 eV
- Detector: Electron-multiplying CCD, photon counting mode
- Knowledge state: **KNOWN** (calibrated instrument)

**Role**: Measure inelastically scattered X-rays (RIXS spectrum)

---

## Data Flow

```
System A (EPU49)
    ↓
System B (Monochromator + Focusing) → 853.4 eV X-rays
    ↓
System D (NiPS3 Sample) ← System C (Cryostat at 40 K)
    ↓ [RIXS scattering - energy loss ΔE]
System E (RIXS Spectrometer) → Measures exciton at ΔE = 1.47 eV
```

**Critical Measurement**: The D→E interaction (sample to spectrometer) encodes the **exciton energy** in the RIXS spectrum!

---

## Summary

| System | Category | Components | Knowledge State | Role |
|--------|----------|------------|----------------|------|
| **A** | Source | EPU49 Undulator | KNOWN | Generate X-rays |
| **B** | Manipulation | Monochromator, Optics | KNOWN | Select 853.4 eV, focus |
| **C** | Environment | Cryostat | KNOWN | Cool to 40 K |
| **D** | Sample | NiPS3 crystal | **UNKNOWN** | **Knowledge gap!** |
| **E** | Detection | RIXS Spectrometer | KNOWN | Measure RIXS spectrum |

✅ **Categorization approved for validation test**
