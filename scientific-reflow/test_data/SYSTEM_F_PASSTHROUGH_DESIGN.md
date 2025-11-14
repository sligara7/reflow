# System F: Pass-Through Design Pattern

**Date**: 2025-11-14
**Design Decision**: System F is ALWAYS present, but configured as pass-through when not needed

---

## 🎯 Design Principle

**System F (Data Processing/Analysis) is ALWAYS in the architecture**, but its behavior is configuration-dependent:

```
ALWAYS:  System D → System E → System F → Observable
         (Sample)   (Detection) (Analysis)  (Measurement)
```

**Configuration determines transformation**:
- **Pass-through**: `data_in = data_out` (identity operation)
- **Processing**: `data_out = f(data_in)` (transformation operation)

---

## 📊 System F Configuration Schema

```json
{
  "component_id": "analysis_pipeline",
  "component_name": "Data Processing/Analysis Pipeline",
  "system_category": "system_f_analysis",
  "knowledge_state": "KNOWN",

  "processing_config": {
    "processing_type": "pass_through | async_daq | correlation_analysis | phase_retrieval | tomographic_reconstruction | fourier_transform | ...",

    "pass_through": {
      "enabled": true,
      "transformation": "identity",
      "latency": "negligible"
    },

    "active_processing": {
      "enabled": false,
      "algorithm": "N/A",
      "computational_cost": "N/A"
    }
  }
}
```

---

## 🔄 Three Beamline Examples

### Example 1: RIXS (2-ID SIX) - Pass-Through

```json
{
  "component_id": "rixs_analysis_passthrough",
  "component_name": "RIXS Data Processing (Pass-Through)",
  "system_category": "system_f_analysis",
  "knowledge_state": "KNOWN",
  "description": "Minimal processing - RIXS spectra are directly interpretable",

  "processing_config": {
    "processing_type": "pass_through",

    "pass_through": {
      "enabled": true,
      "transformation": "identity",
      "input_data": "I(ΔE) - RIXS energy-loss spectrum from spectrometer",
      "output_data": "I(ΔE) - Same spectrum (no transformation)",
      "processing_steps": [
        "Energy calibration (linear mapping)",
        "Detector normalization",
        "Background subtraction (optional)"
      ],
      "latency": "< 1 second",
      "computational_cost": "Negligible"
    },

    "active_processing": {
      "enabled": false
    }
  },

  "physical_interactions": ["int_005_detection_to_analysis"],
  "experimental_functions": [
    "Pass detector output to analysis workflow",
    "Apply minimal data reduction (calibration, normalization)",
    "Output is directly interpretable RIXS spectrum"
  ],

  "notes": "System F exists but does NOT transform the observable. I(ΔE) from detector = I(ΔE) to user."
}
```

**Data flow**:
```
Detector outputs I(ΔE) → System F (pass-through) → Observable I(ΔE)
```

---

### Example 2: XAS (8-ID ISS) - Async DAQ Processing

```json
{
  "component_id": "xas_async_daq",
  "component_name": "XAS Asynchronous Data Acquisition",
  "system_category": "system_f_analysis",
  "knowledge_state": "KNOWN",
  "description": "Active processing - synchronizes multi-channel data streams with 8ns timestamps",

  "processing_config": {
    "processing_type": "async_daq",

    "pass_through": {
      "enabled": false
    },

    "active_processing": {
      "enabled": true,
      "algorithm": "Asynchronous multi-channel timestamp synchronization",
      "input_data": [
        "Multi-element fluorescence detector counts (timestamped)",
        "Monochromator energy encoder (timestamped)",
        "I0 monitor (incident beam intensity, timestamped)",
        "Electrochemical cell voltage/current (timestamped)"
      ],
      "output_data": "μ(E,t) - Time-resolved absorption coefficient",
      "transformation": "Synchronize → Normalize (fluorescence/I0) → Energy calibration → μ(E,t)",
      "timestamp_resolution": "8 ns (NSLS2 timing system)",
      "latency": "Real-time (streaming analysis)",
      "computational_cost": "Moderate (multi-channel sync + normalization)"
    }
  },

  "physical_interactions": ["int_005_detection_to_analysis"],
  "experimental_functions": [
    "Synchronize asynchronous data streams using timestamps",
    "Normalize fluorescence yield by incident intensity",
    "Generate time-resolved absorption spectra μ(E,t)",
    "Enable operando measurements with 1s time resolution"
  ],

  "notes": "System F ACTIVELY TRANSFORMS data. Raw detector counts → μ(E,t) absorption spectrum."
}
```

**Data flow**:
```
Detector outputs [fluorescence, I0, E, V(t)] → System F (DAQ sync) → Observable μ(E,t)
```

---

### Example 3: XPCS (11-ID CHX) - Correlation Analysis

```json
{
  "component_id": "xpcs_correlation_analysis",
  "component_name": "XPCS Autocorrelation Analysis Pipeline",
  "system_category": "system_f_analysis",
  "knowledge_state": "KNOWN",
  "description": "Active processing - calculates g2(q,τ) from speckle pattern time-series",

  "processing_config": {
    "processing_type": "correlation_analysis",

    "pass_through": {
      "enabled": false
    },

    "active_processing": {
      "enabled": true,
      "algorithm": "Two-time temporal autocorrelation: g2(q,t1,t2) = ⟨I(q,t1)·I(q,t2)⟩ / ⟨I(q)⟩²",
      "input_data": "I(q,x,y,t) - Time-series of 2D speckle patterns (10^4-10^6 frames)",
      "output_data": "g2(q,τ) - Temporal autocorrelation function",
      "transformation": "Pixel-wise correlation → q-averaging → g2(q,τ) fitting",
      "computational_cost": "High - 4M pixels × 10^4 frames → ~40 GB data processing",
      "processing_steps": [
        "Azimuthal averaging I(q,x,y,t) → I(q,t)",
        "Calculate two-time correlation C(q,t1,t2) = ⟨I(q,t1)·I(q,t2)⟩",
        "Extract one-time correlation g2(q,τ) = C(q,t,t+τ) / ⟨I(q)⟩²",
        "Fit exponential decay: g2(q,τ) = β·exp(-2τ/τ_relax) + 1",
        "Extract relaxation timescale τ_relax(q)"
      ],
      "latency": "Minutes to hours (depending on dataset size)",
      "parallelization": "GPU-accelerated for real-time analysis",
      "software_tools": ["skbeam", "PyXPCS", "CHX beamline pipeline"]
    }
  },

  "physical_interactions": ["int_005_detection_to_analysis"],
  "experimental_functions": [
    "Calculate temporal autocorrelation function from speckle patterns",
    "Extract dynamics timescale τ_relax from g2(q,τ) decay",
    "Identify dynamics regimes (diffusive, ballistic, arrested)",
    "Generate two-time correlation maps for non-stationary dynamics"
  ],

  "notes": "System F is CRITICAL. Raw detector output I(q,t) is uninterpretable without correlation analysis. g2(q,τ) is the actual observable."
}
```

**Data flow**:
```
Detector outputs I(q,t) [time-series] → System F (correlation) → Observable g2(q,τ)
```

---

## 🏗️ Architectural Benefits

### 1. Consistent Graph Structure
**ALWAYS**: `D → E → F → Observable`

No conditional presence of System F. Every beamline has the same 6-system architecture (A, B, C, D, E, F).

### 2. Simplified Gap Closure
Measurement matrix B **always includes System F**:

```
Observable = B · [System_States]

where B includes:
- D → E interaction (sample → detector)
- E → F interaction (detector → analysis)
- F → Observable (analysis → measurement)
```

**For pass-through F**: E → F is identity (no change)
**For active F**: E → F is transformation matrix

### 3. Configuration-Driven Behavior
```python
if system_f.processing_config.processing_type == "pass_through":
    observable = detector_output  # Identity
elif system_f.processing_config.processing_type == "correlation_analysis":
    observable = calculate_g2(detector_output)  # Transformation
```

### 4. Extensibility
New analysis types? Just add processing_type:
- `"phase_retrieval"` - Ptychography, CDI
- `"tomographic_reconstruction"` - CT, XRF tomography
- `"pdf_fourier_transform"` - Pair distribution function G(r) from S(q)
- `"ml_inference"` - Machine learning-based analysis
- `"streaming_reduction"` - Real-time data reduction

---

## 📐 System-of-Systems Graph

### Before (Conditional F):
```
RIXS:  D → E → Output (no F)
XAS:   D → E → F → Output (F present)
XPCS:  D → E → F → Output (F present)
```
**Problem**: Graph structure varies, gap closure needs conditional logic

### After (Pass-Through F):
```
RIXS:  D → E → F (pass-through) → Output
XAS:   D → E → F (async DAQ)     → Output
XPCS:  D → E → F (correlation)   → Output
```
**Benefit**: Graph structure identical, only F configuration changes

---

## 🔧 Implementation in Validation Cases

### Update RIXS Case (Add Pass-Through F)

```json
{
  "component_id": "rixs_analysis_passthrough",
  "component_name": "RIXS Data Analysis (Pass-Through)",
  "system_category": "system_f_analysis",
  "knowledge_state": "KNOWN",
  "description": "Minimal processing pipeline - RIXS spectra directly interpretable",

  "processing_config": {
    "processing_type": "pass_through",
    "pass_through": {"enabled": true, "transformation": "identity"},
    "active_processing": {"enabled": false}
  },

  "physical_interactions": ["int_005_detection_to_analysis"],
  "experimental_functions": [
    "Energy calibration and detector normalization",
    "Pass RIXS spectrum I(ΔE) to analysis workflow"
  ],
  "notes": "System F exists but is pass-through. No transformation of observable."
}
```

**Add to physical_interactions**:
```json
{
  "interaction_id": "int_005_detection_to_analysis",
  "interaction_name": "RIXS Spectrometer to Analysis Pipeline",
  "interaction_type": "detection_to_analysis",
  "from_component": "rixs_spectrometer_six",
  "to_component": "rixs_analysis_passthrough",
  "causal_direction": "forward",
  "physical_mechanism": "Pass-through (identity transformation)",
  "interaction_strength": "I(ΔE) output = I(ΔE) input",
  "observability": "HIGH",
  "measured": true,
  "critical_for_gap_closure": false,
  "description": "System F passes RIXS spectrum through without transformation"
}
```

---

## 📊 Beamline Profile Schema (Updated)

```json
{
  "beamline_id": "2-ID-SIX",
  "beamline_name": "Soft Inelastic X-ray Scattering",
  "facility": "NSLS2",
  "technique": "Resonant Inelastic X-ray Scattering (RIXS)",

  "systems_config": {
    "system_a": { ... },
    "system_b": { ... },
    "system_c": { ... },
    "system_d": { ... },
    "system_e": { ... },

    "system_f": {
      "component_type": "analysis_pipeline",
      "processing_type": "pass_through",
      "configuration": {
        "transformation": "identity",
        "processing_steps": ["calibration", "normalization"],
        "latency": "negligible"
      }
    }
  },

  "data_flow": "D → E → F (pass-through) → Observable I(ΔE)"
}
```

Compare with XPCS:
```json
{
  "beamline_id": "11-ID-CHX",
  "beamline_name": "Coherent Hard X-ray Scattering",
  "facility": "NSLS2",
  "technique": "X-ray Photon Correlation Spectroscopy (XPCS)",

  "systems_config": {
    "system_a": { ... },
    "system_b": { ... },
    "system_c": { ... },
    "system_d": { ... },
    "system_e": { ... },

    "system_f": {
      "component_type": "analysis_pipeline",
      "processing_type": "correlation_analysis",
      "configuration": {
        "algorithm": "g2(q,τ) = ⟨I(q,t)·I(q,t+τ)⟩ / ⟨I(q)⟩²",
        "fitting_model": "exponential_decay",
        "output": "relaxation_timescale_τ",
        "computational_cost": "high",
        "software": ["skbeam", "PyXPCS"]
      }
    }
  },

  "data_flow": "D → E → F (correlation) → Observable g2(q,τ)"
}
```

**Same structure, different F configuration** ✅

---

## 🎯 Gap Closure Implications

### Observable Definition
```python
# RIXS (pass-through F)
observable_rixs = system_e.output  # I(ΔE) from detector
# system_f is identity, so observable = detector output

# XPCS (correlation F)
observable_xpcs = system_f.output  # g2(q,τ) from correlation analysis
# system_f TRANSFORMS detector output I(q,t) → g2(q,τ)
```

### Measurement Matrix B

**RIXS**:
```
Observable[I(ΔE)] = B_RIXS · [A, B, C, D, E, F_passthrough]
                  = B_E→F · B_D→E · ... (where B_E→F = Identity)
```

**XPCS**:
```
Observable[g2(τ)] = B_XPCS · [A, B, C, D, E, F_correlation]
                  = B_E→F · B_D→E · ... (where B_E→F = g2_transform)
```

### SVD-Based Gap Closure
```python
# Both cases use same algorithm
A_unknown = SVD_solve(B, Observable)

# But Observable and B differ:
# RIXS: Observable = I(ΔE), B includes identity F
# XPCS: Observable = g2(τ), B includes correlation F
```

---

## 🔄 Processing Type Taxonomy

Catalog of System F processing types:

| Processing Type | Input | Output | Techniques |
|----------------|-------|--------|------------|
| **pass_through** | I(E), I(q), I(2θ) | Same | RIXS, XRD, SAXS, XRF |
| **async_daq** | Multi-channel streams | μ(E,t) | Fast XAS, operando |
| **correlation_analysis** | I(q,t) time-series | g2(q,τ) | XPCS, XSVS |
| **phase_retrieval** | Diffraction I(q) | ρ(r) real-space | Ptychography, CDI |
| **tomographic_reconstruction** | I(θ) projections | ρ(x,y,z) 3D | XRF-CT, absorption CT |
| **fourier_transform** | S(q) structure factor | G(r) PDF | Pair distribution function |
| **deconvolution** | I_measured(E) | I_true(E) | Resolution correction |
| **ml_inference** | Raw data | Classified/predicted | Anomaly detection, phase ID |

---

## ✅ Decision: Implement Pass-Through System F

### Changes Required:

1. **Add System F to all validation cases** ✅
   - RIXS: pass_through
   - XAS: async_daq
   - XPCS: correlation_analysis

2. **Update system definitions** ✅
   - Create `system_f_analysis.json` schema
   - Include `processing_type` field
   - Define pass_through and active processing configs

3. **Update workflows** ✅
   - System F always present in system-of-systems graph
   - Step to configure F processing type
   - Workflow asks: "Does your technique require data transformation?"

4. **Update tools** ✅
   - `system_of_systems_graph_v2.py` - Always include F node
   - `validate_architecture.py` - Check F configuration
   - Gap closure tools - Handle F in measurement matrix

---

## 📝 Summary

**Design Pattern**: System F is ALWAYS present, configured as:
- **Pass-through**: When detector output = observable (RIXS, XRD, etc.)
- **Active processing**: When transformation required (XPCS, XAS, ptychography)

**Benefits**:
- ✅ Consistent 6-system architecture (A, B, C, D, E, F)
- ✅ Simpler graph generation (no conditional nodes)
- ✅ Configuration-driven behavior (same code, different configs)
- ✅ Extensible (add new processing types without architecture changes)

**Implementation**: Update all three validation cases to include System F with appropriate processing_type.

---

**Generated**: 2025-11-14
**Design Decision**: System F pass-through pattern
**Status**: Ready for implementation
