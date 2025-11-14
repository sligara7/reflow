# Scientific Reflow - Master Documentation Index

**Version**: 1.0.0
**Last Updated**: 2025-11-14

---

## 📚 Documentation Overview

This directory contains all documentation for **Scientific Reflow**, a specialized spinoff of Reflow designed for scientific discovery through knowledge gap inference.

---

## Core Documents

### 1. **[../README.md](../README.md)** - Start Here!
**Purpose**: High-level overview of Scientific Reflow
**Contents**:
- What is Scientific Reflow?
- The 5-system model (A, B, C, D, E)
- Quick start (3-step workflow)
- Example: NSLS2 beamline X-ray scattering
- Scientific Reflow vs standard Reflow

**Read this first** to understand the philosophy and approach.

---

### 2. **[QUICK_START.md](QUICK_START.md)** - Hands-On Tutorial
**Purpose**: Step-by-step walkthrough from zero to scientific hypothesis in 2 hours
**Contents**:
- Complete beamline XRD example
- What LLM will ask you
- What you define (Systems A-E, interactions)
- What you get (hypothesis, validation plan)
- Troubleshooting common issues

**Use this** for your first Scientific Reflow project.

---

## Workflow Documentation

### 3. **[../workflows/00-scientific_setup.json](../workflows/00-scientific_setup.json)**
**Workflow ID**: 00-scientific_setup
**Duration**: 10-15 minutes
**Purpose**: Initialize project, define scientific goals, configure tools
**Key Steps**:
- SS-01: Project initialization
- SS-02: Define scientific goal
- SS-03: System categorization planning
- SS-04: Tool configuration
- SS-05: Workflow completion

---

### 4. **[../workflows/01-experimental_modeling.json](../workflows/01-experimental_modeling.json)**
**Workflow ID**: 01-experimental_modeling
**Duration**: 30-60 minutes
**Purpose**: Model experimental apparatus as system-of-systems graph
**Key Steps**:
- EM-01: Model System A (Source)
- EM-02: Model System B (Manipulation)
- EM-03: Model System C (Environment)
- EM-04: Model System D (Sample - **UNKNOWN**)
- EM-05: Model System E (Detection)
- EM-06: Review and validate architecture
- EM-07: Workflow completion

**Critical Output**: `experimental_system_architecture.json`

---

### 5. **[../workflows/02-knowledge_gap_discovery.json](../workflows/02-knowledge_gap_discovery.json)**
**Workflow ID**: 02-knowledge_gap_discovery
**Duration**: 15-20 minutes
**Purpose**: Use system_of_systems_graph_v2.py to detect gaps and analyze graph
**Key Steps**:
- KG-01: Generate system-of-systems graph
- KG-02: Analyze graph structure (DAG, centrality, paths)
- KG-03: Gap detection (identify System D as UNKNOWN)
- KG-04: Identify missing measurements (if under-constrained)
- KG-05: Visualization
- KG-06: Workflow completion

**Critical Output**: `experimental_system_graph.json`, gap detection report

---

### 6. **[../workflows/03-gap_closure_analysis.json](../workflows/03-gap_closure_analysis.json)**
**Workflow ID**: 03-gap_closure_analysis
**Duration**: 20-30 minutes
**Purpose**: Matrix transformation + SVD to infer System D properties
**Key Steps**:
- GC-01: Matrix transformation (DAG → matrices A, B, C)
- GC-02: Run reflow_gap_closure.py (SVD-based inference)
- GC-03: Analyze SVD results (singular values, condition number)
- GC-04: Generate scientific hypotheses
- GC-05: Physical plausibility check
- GC-06: Design validation experiments
- GC-07: Generate final report
- GC-08: Workflow completion

**Critical Output**: `gap_closure_proposals.json`, `scientific_hypotheses.md`, `GAP_CLOSURE_REPORT.md`

---

## Framework & Templates

### 7. **[../definitions/experimental_scientific_systems_framework.json](../definitions/experimental_scientific_systems_framework.json)**
**Purpose**: Complete definition of the Experimental Scientific Systems (ESS) framework
**Contents**:
- Framework philosophy (inverse problem solving)
- System categories (A, B, C, D, E) with beamline examples
- Knowledge states (KNOWN, UNKNOWN, PARTIALLY_KNOWN)
- Interaction types (source→manipulation, sample→detection, etc.)
- Recommended NetworkX analyses (DAG, centrality, gap detection)
- Gap closure workflow (5 steps)
- Beamline example (NSLS2 X-ray scattering)
- Tools integration (system_of_systems_graph_v2.py, reflow_gap_closure.py)

**Reference this** to understand the theoretical foundation.

---

### 8. **[../templates/experimental_system_template.json](../templates/experimental_system_template.json)**
**Purpose**: Template for creating `experimental_system_architecture.json`
**Use**: Copy and fill in for your experiment
**Sections**:
- Metadata (facility, beamline, scientific goal)
- Experimental components (Systems A-E)
- Physical interactions (A→B→D→E, C→D)
- Gap closure configuration (SVD tolerance, confidence threshold)

---

### 9. **[../templates/beamline_component_template.json](../templates/beamline_component_template.json)**
**Purpose**: Template for individual experimental components
**Use**: Define each source, optic, environment, sample, detector

---

### 10. **[../templates/working_memory_template.json](../templates/working_memory_template.json)**
**Purpose**: Template for workflow state tracking
**Use**: Automatically generated by `00-scientific_setup.json`

---

## Tool Usage

### Reflow Tools Used by Scientific Reflow

| Tool | Purpose | Workflow Step | Documentation |
|------|---------|---------------|---------------|
| `system_of_systems_graph_v2.py` | Graph generation, gap detection, NetworkX analyses | KG-01 | [../tools/system_of_systems_graph_v2.py](../../tools/system_of_systems_graph_v2.py) |
| `reflow_gap_closure.py` | Integration wrapper for gap closure | GC-02 | [../tools/reflow_gap_closure.py](../../tools/reflow_gap_closure.py) |
| `matrix_gap_detection.py` | Matrix transformation + SVD solver | GC-02 (internal) | [../tools/matrix_gap_detection.py](../../tools/matrix_gap_detection.py) |
| `link_architectures.py` | Architecture linking engine | GC-02 (internal) | [../tools/link_architectures.py](../../tools/link_architectures.py) |

**Main Reflow Tool Documentation**: [../docs/TOOL_USAGE_SUMMARY.md](../../docs/TOOL_USAGE_SUMMARY.md)

---

## Examples

### Beamline X-ray Scattering (Complete Example)

**Scenario**: Determine crystal structure of unknown oxide at NSLS2

**System Decomposition**:
- System A: Undulator (5-30 keV, 10¹³ ph/s)
- System B: DCM + KB mirrors
- System C: Cryostat (10-300 K)
- System D: **Unknown oxide** (crystal structure, lattice parameters **UNKNOWN**)
- System E: Pilatus 2D detector

**Gap Closure Result**: FCC crystal, a=3.92±0.05 Å, space group Fm-3m

**See**: [QUICK_START.md](QUICK_START.md) for step-by-step walkthrough

---

### Other Applicable Domains

Scientific Reflow can be adapted to:

1. **Neutron Scattering**
   - System A: Neutron source (reactor, spallation)
   - System D: Magnetic structure, phonon dispersion (UNKNOWN)

2. **Laser Spectroscopy**
   - System A: Laser source (wavelength, pulse duration)
   - System D: Electronic structure, vibrational modes (UNKNOWN)

3. **Electron Microscopy**
   - System A: Electron gun (energy, coherence)
   - System D: Atomic structure, defects (UNKNOWN)

4. **Chemical Analysis**
   - System A: Excitation source (X-ray, laser)
   - System D: Chemical composition, bonding (UNKNOWN)

---

## Key Concepts

### Knowledge States
- **KNOWN**: Engineered/calibrated/controlled (Systems A, B, C, E)
- **UNKNOWN**: Target of discovery (System D)
- **PARTIALLY_KNOWN**: Some constraints known (e.g., space group symmetry)

### Observability
- **HIGH**: Directly measured (detector readout) - **required for gap closure**
- **MEDIUM**: Indirectly inferred (temperature sensor)
- **LOW**: Poorly constrained (surface roughness)

### Gap Closure Feasibility
Gap closure is feasible if:
1. System D has **UNKNOWN** properties (knowledge gap exists)
2. System D is influenced by **KNOWN** systems (A, B, C)
3. System D is observed by **KNOWN** detectors (E) with **HIGH** observability
4. D→E interactions are **critical_for_gap_closure=TRUE**

If all conditions met → SVD-based inference can infer System D properties.

---

## Troubleshooting

### Common Issues

| Issue | Symptom | Solution | Reference |
|-------|---------|----------|-----------|
| Gap not feasible | "System D not observable" | Add D→E interaction with HIGH observability | [QUICK_START.md](QUICK_START.md) |
| High condition number | κ >> 100, poor inference | Add more measurements (more detectors, angles) | [QUICK_START.md](QUICK_START.md) |
| Unphysical hypothesis | Negative lattice parameter, impossible structure | Add constraints to System D | Framework definition |
| SVD fails | Numerical errors, singular matrix | Check measurement matrix B for zeros/NaNs | Workflow 03 |

---

## Workflow Progression Summary

```
00-scientific_setup (10-15 min)
    ↓
01-experimental_modeling (30-60 min)
    ↓ [generates experimental_system_architecture.json]
02-knowledge_gap_discovery (15-20 min)
    ↓ [uses system_of_systems_graph_v2.py]
03-gap_closure_analysis (20-30 min)
    ↓ [uses reflow_gap_closure.py + SVD]
Scientific Hypotheses + Validation Plan
```

**Total Time**: ~1.5-2 hours

---

## Comparison: Scientific Reflow vs Standard Reflow

| Aspect | Standard Reflow | Scientific Reflow |
|--------|----------------|-------------------|
| Domain | Engineering (microservices, IT systems) | Experimental science (beamlines, labs) |
| Goal | Build working systems | Discover unknown properties |
| Knowledge Gaps | Errors to fix | Desired features (the target!) |
| Primary Tool | Architecture validation | Gap closure + SVD |
| Node Types | Services, functions | Experimental components (sources, detectors, samples) |
| Edge Types | Interfaces, dependencies | Physical interactions (irradiation, scattering, detection) |
| Validation | Functional correctness | Physical plausibility + experimental testability |
| Output | Implemented system | Scientific hypotheses |

---

## Quick Links

- **Main Reflow README**: [../../README.md](../../README.md)
- **Main Reflow Guide (for LLMs)**: [../../CLAUDE.md](../../CLAUDE.md)
- **Reflow Tool Summary**: [../../docs/TOOL_USAGE_SUMMARY.md](../../docs/TOOL_USAGE_SUMMARY.md)
- **NetworkX Analysis Guide**: [../../docs/NETWORKX_ANALYSIS_GUIDE.md](../../docs/NETWORKX_ANALYSIS_GUIDE.md)
- **Scientific Reflow GitHub**: https://github.com/sligara7/reflow (tag issues with `[scientific-reflow]`)

---

## Getting Help

1. **Read [QUICK_START.md](QUICK_START.md)** - Most common questions answered here
2. **Check Troubleshooting section** in this document
3. **Review framework definition** - [../definitions/experimental_scientific_systems_framework.json](../definitions/experimental_scientific_systems_framework.json)
4. **Open GitHub issue** with `[scientific-reflow]` tag

---

## Contributing

Scientific Reflow is a **research prototype**. We welcome:
- Experimental validation case studies (your beamline results!)
- New domain adaptations (neutron, electron, laser, chemical)
- Enhanced gap closure algorithms (Bayesian, ML-based)
- Visualization improvements
- Bug fixes and documentation improvements

---

**Ready to start? Go to [QUICK_START.md](QUICK_START.md) and begin your first scientific discovery workflow! 🚀**
