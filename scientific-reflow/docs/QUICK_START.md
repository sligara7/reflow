# Scientific Reflow - Quick Start Guide

**Goal**: Get from zero to scientific hypotheses in 2 hours.

---

## Prerequisites

```bash
# Install Python dependencies
pip install networkx>=3.0 numpy scipy

# Or use Pixi (recommended)
cd /path/to/reflow
pixi install
```

---

## Step-by-Step Example: Determine Crystal Structure from X-ray Diffraction

### Step 1: Setup (10 minutes)

```bash
# Option 1: Web-based (GitHub Codespaces, Claude Code, etc.)
"Implement workflow in github.com/sligara7/reflow/scientific-reflow/workflows/00-scientific_setup.json
 on system in github.com/yourname/my_xrd_experiment"

# Option 2: Local
"Implement workflow in /path/to/reflow/scientific-reflow/workflows/00-scientific_setup.json
 on system in /path/to/my_xrd_experiment"
```

LLM will ask:
1. **Facility/beamline?** → "NSLS2 beamline 28-ID-2"
2. **What are you discovering?** → "Crystal structure of unknown oxide sample"
3. **What's unknown about System D?** → "Crystal structure, lattice parameters, space group"
4. **Success criteria?** → "Determine space group and lattice parameters to ±0.05 Å"

**Output**: `context/working_memory.json`, `docs/scientific_goal.md`

---

### Step 2: Model Your Experimental System (30 minutes)

LLM proceeds to `01-experimental_modeling.json`.

**Define System A (Source)**:
- Component: "Undulator insertion device"
- Properties: Energy 5-30 keV, Flux 10¹³ ph/s, Beam size 100 μm × 50 μm
- Knowledge state: KNOWN

**Define System B (Manipulation)**:
- Component 1: "Double Crystal Monochromator (DCM)"
  - Properties: Energy resolution 10⁻⁴, Reflectivity 0.7
  - Knowledge state: KNOWN
- Component 2: "KB focusing mirrors"
  - Properties: Focal spot 1 μm × 1 μm, Reflectivity 0.9
  - Knowledge state: KNOWN

**Define System C (Environment)**:
- Component: "Cryostat"
- Properties: Temperature 10-300 K, Stability ±0.1 K
- Knowledge state: KNOWN

**Define System D (Sample - THE UNKNOWN)**:
- Component: "Unknown oxide sample"
- Properties:
  - crystal_structure: **UNKNOWN** (goal!)
  - lattice_parameters: **UNKNOWN** (goal!)
  - space_group: PARTIALLY_KNOWN (assumed centrosymmetric from optical observations)
  - chemical_composition: PARTIALLY_KNOWN (XRF shows Fe, Ti, O)
- Knowledge state: **UNKNOWN**
- Gap closure goal: "Infer crystal structure and lattice parameters from XRD pattern"

**Define System E (Detection)**:
- Component: "Pilatus 2D X-ray detector"
- Properties: Pixel size 172 μm, Dynamic range 20-bit, QE 0.9 at 12 keV
- Knowledge state: KNOWN

**Define Interactions**:
1. Undulator → DCM (source_to_manipulation, observability=HIGH)
2. DCM → KB mirrors (source_to_manipulation, observability=HIGH)
3. KB mirrors → Sample (manipulation_to_sample, observability=MEDIUM)
4. Cryostat → Sample (environment_to_sample, observability=MEDIUM)
5. **Sample → Pilatus detector** (sample_to_detection, **observability=HIGH**, **critical_for_gap_closure=TRUE**) ← **THIS IS YOUR DATA**

**Output**: `specs/machine/experimental_systems/experimental_system_architecture.json`

---

### Step 3: Discover Knowledge Gaps (15 minutes)

LLM proceeds to `02-knowledge_gap_discovery.json`.

**Run graph generation**:
```bash
python3 /path/to/reflow/tools/system_of_systems_graph_v2.py \
  --framework experimental_scientific_systems \
  specs/machine/experimental_systems/experimental_system_architecture.json
```

**LLM analyzes**:
- **DAG check**: ✅ Graph is a DAG (Undulator → DCM → KB → Sample → Detector)
- **Centrality**: Sample has **highest betweenness centrality** (bottleneck between source and detector)
- **Paths**: One primary path A→B→D→E (good - clean signal)
- **Gap detection**: **System D (Sample) identified as knowledge gap** with HIGH observability via D→E

**Output**: `specs/machine/graphs/experimental_system_graph.json`, `docs/gap_detection_report.md`

---

### Step 4: Close Gaps with SVD (20 minutes)

LLM proceeds to `03-gap_closure_analysis.json`.

**Matrix transformation**:
- Adjacency matrix A (5×5): Undulator, DCM, KB, Sample, Detector
- Measurement matrix B: Sample→Detector diffraction pattern (HIGH observability)
- Causal matrix C: Known for A, B, C, E; **UNKNOWN for D**

**Run gap closure**:
```bash
python3 /path/to/reflow/tools/reflow_gap_closure.py \
  specs/machine/experimental_systems/experimental_system_architecture.json
```

**SVD analysis**:
- Singular values: σ₁=12.5, σ₂=8.3, σ₃=0.7 (well-constrained)
- Condition number κ = 17.9 (good - problem is well-posed)

**Inferred System D properties**:
```json
{
  "crystal_structure": "Face-Centered Cubic (FCC)",
  "lattice_parameter_a": "3.92 ± 0.05 Å",
  "space_group": "Fm-3m (No. 225)",
  "confidence": "HIGH"
}
```

**Generated hypothesis**:
> **Hypothesis 1**: Sample is an FCC crystal with lattice parameter a=3.92±0.05 Å, space group Fm-3m.
>
> **Testable predictions**:
> - Diffraction peaks at 2θ = 38.5°, 44.7°, 65.1° (Cu Kα, if measured with lab source)
> - Systematic absences: h,k,l all even or all odd
> - Cubic symmetry → peak positions scale as √(h²+k²+l²)
>
> **Validation experiments**:
> 1. Collect full reciprocal space map → verify cubic symmetry
> 2. Measure higher-order reflections → refine lattice parameter
> 3. Perform Rietveld refinement → confirm space group

**Output**: `specs/machine/gap_closure/gap_closure_proposals.json`, `docs/scientific_hypotheses.md`, `docs/GAP_CLOSURE_REPORT.md`

---

## Result Summary

| Workflow | Time | Key Achievement |
|----------|------|----------------|
| 00-scientific_setup | 10 min | Defined scientific goal: "Determine crystal structure" |
| 01-experimental_modeling | 30 min | Modeled experimental system (5 systems, 5 interactions) |
| 02-knowledge_gap_discovery | 15 min | Identified System D gap, verified HIGH observability |
| 03-gap_closure_analysis | 20 min | **Inferred FCC structure, a=3.92 Å, Fm-3m space group** |
| **TOTAL** | **75 min** | **From unknown sample to testable hypothesis** |

---

## What You Get

1. **Scientific hypothesis**: FCC crystal, a=3.92±0.05 Å, Fm-3m
2. **Confidence assessment**: HIGH (condition number 17.9, 3 large singular values)
3. **Testable predictions**: Diffraction peak positions at 2θ = 38.5°, 44.7°, 65.1°
4. **Validation plan**: Full reciprocal space mapping, higher-order reflections, Rietveld refinement
5. **Complete documentation**: 10+ markdown files, JSON architecture, graph analysis

---

## Iteration

Scientific discovery is iterative! If you want to refine:

```bash
# Add more measurements (e.g., spectroscopy)
# → Update 01-experimental_modeling (add System E component)
# → Re-run 02, 03

# Refine System D constraints (e.g., "must be cubic")
# → Update experimental_system_architecture.json
# → Re-run 03-gap_closure_analysis

# Explore alternative hypotheses
# → Review gap_closure_proposals.json for alternative solutions
# → Check SVD singular values for degeneracies
```

---

## Troubleshooting

### "Gap closure not feasible"
**Problem**: System D not observable by System E.
**Fix**: Add D→E measurement interaction with observability=HIGH.

### "Condition number too high (κ >> 100)"
**Problem**: Under-constrained problem (too many unknowns, too few measurements).
**Fix**: Add more measurements (more detectors, multi-angle, spectroscopy).

### "Hypotheses not physically plausible"
**Problem**: Inferred properties violate physical laws.
**Fix**: Add constraints to System D (e.g., "lattice_parameter > 0", "space_group must be centrosymmetric").

### "No hypothesis generated"
**Problem**: SVD failed (numerical issues, singular matrix).
**Fix**: Check measurement matrix B for zeros/NaNs. Ensure D→E interactions have non-zero interaction_strength.

---

## Next Steps

1. **Validate hypothesis experimentally** (collect validation data)
2. **Iterate** (refine model, add measurements, update constraints)
3. **Explore Reflow tools** (see `docs/TOOL_USAGE_SUMMARY.md`)
4. **Adapt to your domain** (neutron scattering, electron microscopy, etc.)

---

**Congratulations! You've used Scientific Reflow to generate a testable scientific hypothesis from experimental data. 🎉🔬**
