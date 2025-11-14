# BLOP Integration Analysis for Systems A-F Architecture

**Date**: 2025-11-14
**Purpose**: Identify Bayesian optimization opportunities in Systems A-F, particularly System B (Manipulation)

---

## 🎯 Executive Summary

**BLOP (Bayesian Learning and Optimization Platform)** is NSLS-II's adaptive beamline optimization tool. After analyzing three validated beamlines (RIXS, XAS, XPCS), we identified **significant System B optimization opportunities** at all three beamlines.

**Key Finding**: System B is the PRIMARY target for BLOP, but **Systems A, C, and E also have optimization opportunities** depending on technique requirements.

**Recommendation**: Integrate BLOP into Scientific Reflow workflows as **System B.5 (Adaptive Alignment/Optimization)** - an optional sub-system between B and D.

---

## 📊 BLOP Overview

### What is BLOP?

**BLOP** = Bayesian Learning and Optimization Platform for autonomous beamline alignment

**Key Capabilities**:
- Bayesian optimization of beamline components (motors, optics)
- Works with Bluesky data acquisition framework
- Autonomous alignment and tuning
- Handles noisy/low-fidelity data (dynamic pruning)
- Multi-objective optimization (flux vs resolution, spot size vs divergence)

**Typical Use Cases**:
- Monochromator crystal alignment
- Focusing optics positioning (KB mirrors, lenses)
- Beam steering and centering
- Energy calibration
- Multi-element optimization (maximize flux, minimize spot size)

**Reference**: Morris et al., "A general Bayesian algorithm for the autonomous alignment of beamlines", J. Synchrotron Rad. 31, 1446-1456 (2024)

---

## 🔬 Three-Beamline BLOP Analysis

### Case 1: 2-ID SIX (RIXS) - Resolution-Critical

**System B Components**:
- Grating monochromator (energy selection)
- Kirkpatrick-Baez focusing mirrors

**Optimization Objective**: **Maximize energy resolution** (minimize ΔE, target: 14-17 meV @ 853 eV)

#### BLOP Opportunities in System B:

| Component | Degrees of Freedom (DOF) | Optimization Target | Constraints | Priority |
|-----------|-------------------------|---------------------|-------------|----------|
| **Grating Monochromator** | Grating pitch angle, entrance slit width, exit slit width, crystal alignment (roll, pitch, yaw) | Maximize resolving power R = E/ΔE (target: 100,000 @ 1000 eV) | Energy range: 400-1600 eV | **HIGH** |
| **KB Focusing Mirrors** | Mirror pitch, yaw, horizontal/vertical positions | Minimize spot size on sample (<50 μm) | Maintain flux throughput | **MEDIUM** |
| **Beam Steering** | Upstream mirror angles | Center beam on sample position | Avoid clipping apertures | **MEDIUM** |

#### Multi-Objective Optimization:
```
Objectives:
1. MAXIMIZE: Energy resolution (ΔE → minimum)
2. MAXIMIZE: Flux on sample (photons/sec)
3. MINIMIZE: Spot size (beam FWHM)

Tradeoff: Resolution ↔ Flux
- Narrow slits → better resolution, lower flux
- Wider slits → worse resolution, higher flux
```

#### BLOP Integration Point:
**After System B, before System D** → "System B.5: RIXS Alignment Optimization"

**Workflow**:
1. User sets desired energy (e.g., 853 eV for Ni L-edge)
2. BLOP optimizes monochromator + KB mirrors for maximum resolution at that energy
3. Verification: Measure elastic line width (should be instrument-limited)
4. Proceed to System D (sample measurement)

#### Expected Impact:
- **Resolution improvement**: 10-20% better ΔE (e.g., 17 meV → 14 meV)
- **Setup time reduction**: 30-60 min manual alignment → 10-15 min BLOP auto-alignment
- **Reproducibility**: Consistent alignment across experiments

---

### Case 2: 8-ID ISS (XAS) - Flux/Speed-Critical

**System B Components**:
- Double-crystal monochromator (DCM)
- Kirkpatrick-Baez focusing mirrors
- Beam position monitors

**Optimization Objective**: **Maximize flux throughput** (for fast 1s XAS scans)

#### BLOP Opportunities in System B:

| Component | Degrees of Freedom (DOF) | Optimization Target | Constraints | Priority |
|-----------|-------------------------|---------------------|-------------|----------|
| **Double-Crystal Monochromator** | Crystal pitch (Bragg angle), crystal 2 roll compensation, vertical position | Maximize flux transmission (>30% efficiency) | Energy range: 5-30 keV, ΔE/E ~ 10^-4 | **HIGH** |
| **KB Mirrors** | Mirror pitch, yaw, bending radii | Maximize flux density at sample (minimize focal spot to ~50-100 μm) | Flux > 10^11 ph/s at sample | **HIGH** |
| **Beam Position** | Upstream slits, mirror angles | Center beam through all apertures (minimize clipping losses) | Beam stable over 1500h operando experiment | **MEDIUM** |

#### Multi-Objective Optimization:
```
Objectives:
1. MAXIMIZE: Flux at sample (photons/sec)
2. MINIMIZE: Focal spot size (for concentrated samples)
3. MAINTAIN: Energy stability (prevent drift during long operando experiments)

Tradeoff: Flux ↔ Spot Size
- Tight focus → high flux density, harder alignment
- Looser focus → lower flux density, easier alignment
```

#### BLOP Integration Point:
**After System B, before operando measurement** → "System B.5: XAS Fast Alignment"

**Workflow**:
1. User sets XAS edge energy (e.g., 22.1 keV for Ru K-edge)
2. BLOP optimizes DCM + KB for maximum flux at that energy
3. Verification: Measure I0 (incident flux) and transmission through sample
4. Proceed to operando XAS (1500h stability required)

#### Special Consideration - Operando Stability:
- **Challenge**: Electrochemical cell generates gas bubbles (O2), can block beam
- **BLOP Opportunity**: Real-time beam position adjustment during operando measurement
- **Implementation**: Monitor I0 flux, re-optimize KB mirrors if flux drops >10%

#### Expected Impact:
- **Flux improvement**: 20-30% more photons at sample (better signal-to-noise ratio)
- **Stability**: Maintain alignment over 1500h operando experiments
- **Speed**: 1s XAS scans require maximum flux (BLOP ensures optimal throughput)

---

### Case 3: 11-ID CHX (XPCS) - Coherence-Critical

**System B Components**:
- Double-crystal Si(111) monochromator
- Compound Refractive Lenses (CRLs) or KB mirrors
- Coherence slits

**Optimization Objective**: **Maximize spatial coherence** while maintaining flux for speckle formation

#### BLOP Opportunities in System B:

| Component | Degrees of Freedom (DOF) | Optimization Target | Constraints | Priority |
|-----------|-------------------------|---------------------|-------------|----------|
| **Coherence Slits** | Horizontal/vertical slit openings | Maximize transverse coherence length (10-50 μm) | Balance coherence vs flux loss | **CRITICAL** |
| **Monochromator** | Crystal pitch, longitudinal coherence control | Maximize speckle contrast (β > 0.5) | ΔE/E ~ 10^-4 for temporal coherence | **HIGH** |
| **Focusing Optics (CRL/KB)** | Lens positions, mirror angles | Minimize wavefront distortion (preserve coherence) | Focal spot size ~ coherence length | **CRITICAL** |

#### Multi-Objective Optimization:
```
Objectives:
1. MAXIMIZE: Transverse coherence length (for sharp speckles)
2. MAXIMIZE: Speckle contrast β = ⟨I²⟩/⟨I⟩² - 1 (>0.5 desired)
3. MAINTAIN: Sufficient flux for kHz frame rate (10^9 ph/s minimum)

Tradeoff: Coherence ↔ Flux
- Tighter slits → better coherence, much lower flux
- Wider slits → worse coherence (poor speckles), higher flux

CRITICAL: Without coherence, XPCS doesn't work (no speckles → no g2(τ))
```

#### BLOP Integration Point:
**After System B, with feedback from System E** → "System B.5: XPCS Coherence Optimization"

**Workflow**:
1. User sets energy (e.g., 9 keV for ferroelectric sample)
2. BLOP optimizes slits + monochromator for coherence
3. **Verification**: Acquire test speckle pattern (System E), calculate speckle contrast β
4. BLOP adjusts slits based on β measurement (closed-loop optimization)
5. Proceed to XPCS time-series acquisition

#### Special Consideration - Speckle Contrast Feedback:
- **Unique to XPCS**: System B optimization REQUIRES System E feedback
- **BLOP Advantage**: Can optimize based on actual speckle quality (not just beam size)
- **Metric**: Speckle contrast β = (variance/mean² - 1) from detector image

#### Expected Impact:
- **Coherence improvement**: 30-50% better speckle contrast
- **XPCS quality**: Higher g2(τ) signal-to-noise ratio
- **Reproducibility**: Consistent coherence properties across experiments

---

## 🎯 System-by-System BLOP Opportunities

### System A (Source) - Limited but Possible

| Beamline | Component | BLOP Opportunity | Priority |
|----------|-----------|------------------|----------|
| **RIXS** | EPU49 undulator gap | Optimize gap for maximum flux at desired energy | LOW (usually pre-calibrated) |
| **XAS** | Damping wiggler | N/A (fixed source) | NONE |
| **XPCS** | Coherent undulator gap | Optimize for maximum coherent flux | MEDIUM (if coherent flux < desired) |

**Note**: System A is usually pre-optimized by beamline design. BLOP rarely needed here.

---

### System B (Manipulation) - **PRIMARY BLOP TARGET** ✅

| Beamline | Components | BLOP Opportunities | Priority |
|----------|------------|-------------------|----------|
| **RIXS** | Monochromator, KB mirrors | Resolution optimization, spot size minimization | **HIGH** |
| **XAS** | DCM, KB mirrors, beam position | Flux maximization, stability over 1500h | **HIGH** |
| **XPCS** | Slits, monochromator, CRL/KB | **Coherence maximization with speckle feedback** | **CRITICAL** |

**Summary**: System B has 5-10 degrees of freedom per beamline → **Ideal for BLOP**

**Common Optimization Tasks**:
1. Crystal alignment (pitch, yaw, roll)
2. Mirror positioning (horizontal, vertical, angles)
3. Slit openings (aperture control)
4. Beam steering (upstream mirrors/slits)

---

### System C (Environment) - Moderate Opportunity

| Beamline | Component | BLOP Opportunity | Priority |
|----------|-----------|------------------|----------|
| **RIXS** | Cryostat temperature | N/A (static environment) | NONE |
| **XAS** | Electrochemical cell voltage | **Optimize OER conditions for maximum Ru oxidation signal** | MEDIUM |
| **XPCS** | Electric field strength/timing | **Optimize field for domain switching dynamics** | MEDIUM |

**Note**: System C BLOP is more about **experimental parameter optimization** (not alignment).

**XAS Example**: Optimize applied voltage to maximize Ru edge shift (measure degradation kinetics)
**XPCS Example**: Optimize E-field pulse duration to maximize domain relaxation signal in g2(τ)

---

### System D (Sample) - No BLOP (Target of Discovery)

System D is **PARTIALLY_KNOWN** with gaps → Cannot optimize what you're trying to discover!

**Exception**: Sample positioning/orientation (part of System C or B mechanical stage)
- **RIXS**: Optimize sample orientation for maximum RIXS scattering intensity
- **XAS**: Optimize sample position in beam (maximize transmission signal)
- **XPCS**: Optimize sample angle for desired q-range

---

### System E (Detection) - Limited Opportunity

| Beamline | Component | BLOP Opportunity | Priority |
|----------|-----------|------------------|----------|
| **RIXS** | Spectrometer alignment | Optimize grating angle for maximum resolution | LOW (pre-aligned) |
| **XAS** | Fluorescence detector position | Optimize solid angle (maximize count rate) | MEDIUM |
| **XPCS** | Detector distance | Optimize for desired q-range in speckle pattern | MEDIUM |

**Note**: System E is usually aligned once and rarely re-optimized during experiment.

---

### System F (Analysis) - No Direct BLOP

System F is computational → BLOP doesn't apply to data processing.

**Exception**: **Hyperparameter optimization** for analysis algorithms
- **XPCS**: Optimize g2(τ) fitting parameters (τ_relax initial guess, β constraint)
- **XAS**: Optimize background subtraction parameters

**Different tool needed**: Standard ML hyperparameter optimization (not BLOP)

---

## 🔧 BLOP Integration into Scientific Reflow

### Proposed: System B.5 (Adaptive Alignment/Optimization)

**Concept**: Add BLOP as optional sub-system between System B and System D

```
Current Flow:
A (Source) → B (Manipulation) → D (Sample) → E (Detection) → F (Analysis)

With BLOP:
A (Source) → B (Manipulation) → B.5 (BLOP Optimization) → D (Sample) → E (Detection) → F (Analysis)
                                       ↑___________________|
                                       Feedback loop (for XPCS)
```

### System B.5 Schema:

```json
{
  "component_id": "blop_optimizer",
  "component_name": "BLOP Adaptive Beamline Alignment",
  "system_category": "system_b5_optimization",
  "knowledge_state": "KNOWN",
  "optimization_type": "bayesian_alignment",

  "optimization_config": {
    "target": "system_b_components",
    "objectives": [
      {"objective": "maximize_flux", "weight": 0.4},
      {"objective": "maximize_resolution", "weight": 0.6}
    ],
    "degrees_of_freedom": [
      {"component": "monochromator", "dof": "crystal_pitch", "range": [-0.1, 0.1]},
      {"component": "kb_mirrors", "dof": "mirror1_pitch", "range": [-0.5, 0.5]}
    ],
    "feedback_source": "system_e_detector",
    "optimization_metric": "speckle_contrast | flux | resolution",
    "max_iterations": 50,
    "convergence_threshold": 0.01
  },

  "bluesky_integration": {
    "adaptive_plan": "blop.Agent",
    "acquisition_function": "expected_improvement",
    "model": "gaussian_process"
  }
}
```

### Workflow Integration (Example: XPCS at CHX):

```
Step EM-01: Model Experimental System (Systems A-E)
  ↓
Step EM-02: Define Optimization Goals
  → User: "I want maximum speckle contrast for XPCS"
  ↓
Step EM-03: BLOP Optimization (System B.5)
  → BLOP optimizes: coherence slits + monochromator
  → Feedback from System E: measure β (speckle contrast)
  → Iterate until β > 0.5
  ↓
Step EM-04: Proceed to Measurement (System D → E)
  → Acquire XPCS time-series with optimized coherence
```

---

## 📊 BLOP Priority Matrix

### High-Priority BLOP Integration:

| Beamline | System B Components | Optimization Goal | Estimated DOF | Expected Improvement | Implementation Priority |
|----------|---------------------|-------------------|---------------|----------------------|------------------------|
| **11-ID CHX (XPCS)** | Slits + Mono + CRL | Maximize coherence (speckle contrast β) | 6-8 | 30-50% better g2 SNR | **🔥 CRITICAL** |
| **2-ID SIX (RIXS)** | Grating + KB mirrors | Maximize resolution (minimize ΔE) | 5-7 | 10-20% better ΔE | **⚡ HIGH** |
| **8-ID ISS (XAS)** | DCM + KB + Position | Maximize flux (speed + SNR) | 4-6 | 20-30% more flux | **⚡ HIGH** |

### Why CHX (XPCS) is CRITICAL Priority:

1. **Coherence is non-negotiable**: Without coherence, XPCS doesn't work (no speckles)
2. **Complex tradeoff**: Coherence ↔ Flux is highly nonlinear (Bayesian optimization ideal)
3. **Feedback loop required**: Must measure speckle quality (β) from System E to optimize System B
4. **Manual alignment is difficult**: 6-8 DOF with nonlinear interactions → perfect for BLOP

---

## 🚀 Implementation Roadmap

### Phase 1: Proof-of-Concept (CHX XPCS) - **Recommended First**

**Why XPCS first?**
- Coherence optimization is CRITICAL (not optional)
- Clear metric: speckle contrast β (easy to measure)
- Strong collaboration opportunity (your team develops BLOP, CHX needs it)

**Steps**:
1. Identify CHX System B components (slits, mono, CRL)
2. Define optimization objectives (maximize β, maintain flux > 10^9 ph/s)
3. Implement BLOP agent with feedback from detector
4. Validate: Compare manual alignment vs BLOP (measure β, g2 quality)
5. **Success metric**: BLOP achieves β > 0.5 in <15 min vs >30 min manual

### Phase 2: High-Throughput Optimization (ISS XAS)

**Why XAS second?**
- Flux optimization is valuable (faster scans = more operando data)
- Less critical than XPCS (XAS works even with non-optimal flux)
- Large user base → high impact

**Steps**:
1. Identify ISS System B components (DCM, KB mirrors)
2. Optimize for maximum flux at sample
3. Add stability constraint (maintain alignment over 1500h)
4. Validate: Compare 1s XAS scan quality (BLOP vs manual)

### Phase 3: Resolution Optimization (SIX RIXS)

**Why RIXS third?**
- Resolution is important but less critical than XPCS coherence
- Manual alignment already good (RIXS experts are skilled)
- BLOP adds consistency/reproducibility more than raw performance

**Steps**:
1. Optimize grating + KB for minimum ΔE at desired energy
2. Validate: Measure elastic line width (instrument resolution)
3. Compare BLOP vs expert alignment

---

## 💡 Beyond System B: Creative BLOP Applications

### System A + B Joint Optimization (XPCS):
```
Optimize:
- Undulator gap (System A) - maximize coherent flux
- Slits (System B) - maximize coherence length
- Monochromator (System B) - temporal coherence

Joint objective: Maximize β (speckle contrast) with constraints on total flux
```

### System C Experimental Parameter Optimization (XAS):
```
Optimize:
- Applied voltage (System C) - electrochemical potential
- Scan rate (System C) - balance speed vs equilibration

Objective: Maximize observable Ru oxidation signal in μ(E,t)
```

### Multi-Beamline BLOP (Cross-Facility):
```
Use BLOP models trained at one beamline to initialize optimization at another
Example: XPCS coherence optimization at CHX (NSLS-II) → transfer to ALS 8.0.1 (LBNL)
```

---

## 📋 Summary Table: BLOP Integration Points

| System | BLOP Applicable? | Optimization Type | Example | Priority |
|--------|-----------------|-------------------|---------|----------|
| **System A (Source)** | Rarely | Source tuning (gap, taper) | Undulator gap for max coherent flux | LOW |
| **System B (Manipulation)** | **YES** ✅ | Alignment, focusing, slits | Monochromator + KB + slits optimization | **HIGH** |
| **System C (Environment)** | Sometimes | Experimental parameters | Voltage, E-field, temperature | MEDIUM |
| **System D (Sample)** | No (discovery target) | N/A | - | NONE |
| **System E (Detection)** | Rarely | Detector positioning | Fluorescence detector solid angle | LOW |
| **System F (Analysis)** | No (computational) | Hyperparameter tuning (not BLOP) | g2 fitting parameters | NONE |
| **System B.5 (NEW)** | **YES** ✅ | Adaptive alignment | BLOP agent for multi-objective optimization | **HIGH** |

---

## 🎯 Recommendations for Your Team

### 1. Start with CHX (11-ID) XPCS ⭐ **Top Priority**

**Why**: Coherence optimization is:
- **Critical** for XPCS (not optional)
- **Complex** (6-8 DOF, nonlinear tradeoffs)
- **Measurable** (speckle contrast β is clear objective)
- **High-impact** (XPCS user community needs this)

**Collaboration**: Work with CHX beamline scientists to implement System B.5 (BLOP) for coherence optimization.

### 2. Extend to ISS (8-ID) XAS - High Impact

**Why**: Flux optimization enables:
- Faster 1s XAS scans (better for operando)
- More stable alignment (1500h experiments)
- Large user community (battery/catalyst research)

### 3. Integrate into Scientific Reflow Workflows

**Proposed Workflow Step**: **EM-02.5: Adaptive Beamline Alignment (BLOP)**

```
Workflow Step EM-02.5: BLOP Optimization (Optional)

Description: Use BLOP to optimize System B components for experimental objectives

User Input:
- Optimization goal: [maximize_flux | maximize_resolution | maximize_coherence | multi_objective]
- Constraints: [min_flux, max_acquisition_time, ...]

BLOP Actions:
1. Identify System B degrees of freedom from beamline profile
2. Set up Bayesian optimization with objectives
3. Run BLOP adaptive plan (with Bluesky integration)
4. Verify convergence (measure metric from System E)
5. Save optimized motor positions to working_memory.json

Output: Optimized beamline configuration ready for System D measurement
```

### 4. Document BLOP Integration in Beamline Profiles

Add to profile schema:

```json
{
  "blop_config": {
    "applicable": true,
    "optimization_target": "system_b",
    "typical_objectives": ["maximize_coherence", "maintain_flux"],
    "degrees_of_freedom": [
      {"component": "coherence_slits", "dof": ["h_opening", "v_opening"]},
      {"component": "monochromator", "dof": ["crystal_pitch"]},
      {"component": "crl", "dof": ["lens_positions"]}
    ],
    "feedback_metric": "speckle_contrast_beta",
    "estimated_optimization_time": "10-15 minutes",
    "bluesky_plan": "blop.coherence_optimization"
  }
}
```

---

## 📖 Further Reading

1. **BLOP Documentation**: https://nsls-ii.github.io/blop/
2. **BLOP GitHub**: https://github.com/NSLS-II/blop
3. **Publication**: Morris et al., "A general Bayesian algorithm for the autonomous alignment of beamlines", J. Synchrotron Rad. 31, 1446-1456 (2024)
4. **Bluesky Integration**: BLOP works with Bluesky adaptive plans

---

## ✅ Conclusion

**BLOP Integration Summary**:
- ✅ **System B is the primary target** for BLOP (5-10 DOF per beamline)
- ✅ **All three beamlines benefit** from System B optimization (XPCS most critical)
- ✅ **System A, C, E have limited opportunities** (source tuning, experimental parameters, detector positioning)
- ✅ **Propose System B.5** as adaptive alignment sub-system in Scientific Reflow
- ✅ **Start with CHX (XPCS)** - highest priority, clearest benefit

**Impact**: BLOP can **reduce alignment time** (30-60 min → 10-15 min), **improve performance** (20-50% better metrics), and **increase reproducibility** (consistent alignment across experiments).

**Next Action**: Collaborate with CHX beamline to implement BLOP for coherence optimization as proof-of-concept! 🚀

---

**Generated**: 2025-11-14
**Analysis**: BLOP integration opportunities in Systems A-F architecture
**Contact**: Your team actively develops BLOP - let's integrate it into Scientific Reflow! 🎯
