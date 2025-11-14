# BLOP Quick Reference for Scientific Reflow Integration

**Date**: 2025-11-14
**BLOP Version**: 0.8.1 (Latest - Released Nov 6, 2025)

---

## 📦 Installation

```bash
# Standard installation
pip install blop

# Or with pixi (recommended for Reflow environments)
pixi add blop

# Requires Python 3.10+ (3.10, 3.11, 3.12 supported)
```

**PyPI**: https://pypi.org/project/blop/
**Docs**: https://nsls-ii.github.io/blop/
**GitHub**: https://github.com/NSLS-II/blop

---

## 🎯 What is BLOP?

**BLOP** = **B**eamline **L**earning and **O**ptimization **P**latform

**Purpose**: Autonomous beamline alignment using Bayesian optimization

**Key Capabilities**:
- Multi-objective optimization (flux vs resolution, coherence vs throughput)
- Works with Bluesky data acquisition framework
- Gaussian Process models for noisy experimental data
- Dynamic pruning of low-fidelity data points
- Real-time adaptive alignment during experiments

**Research**: Morris et al., "A general Bayesian algorithm for the autonomous alignment of beamlines", J. Synchrotron Rad. 31, 1446-1456 (2024)

---

## 🔧 BLOP Integration Points in Systems A-F

### Primary Target: **System B (Manipulation)** ✅

**What BLOP optimizes**:
- Monochromator crystal alignment (pitch, roll, yaw)
- Focusing mirror positions (KB mirrors, CRLs)
- Slit openings (coherence control)
- Beam steering and centering

**Why System B is ideal**:
- 5-10 degrees of freedom (multi-parameter optimization)
- Nonlinear tradeoffs (resolution ↔ flux, coherence ↔ flux)
- Measurable objectives (flux, spot size, resolution, speckle contrast)
- Time-consuming to align manually (30-60 min → 10-15 min with BLOP)

---

## 📊 Beamline-Specific BLOP Use Cases

### 1. **CHX (11-ID) - XPCS Coherence Optimization** 🔥 CRITICAL

**Challenge**: XPCS requires spatial coherence for speckle patterns, but coherence ↔ flux tradeoff is highly nonlinear

**System B components to optimize**:
- Coherence slits (horizontal/vertical openings) - 2 DOF
- Monochromator crystal pitch - 1 DOF
- CRL/KB mirror positions - 3-4 DOF
- **Total: ~6-8 degrees of freedom**

**Optimization objectives**:
```python
# Multi-objective with constraints
objectives = [
    {"name": "speckle_contrast_beta", "target": "maximize", "weight": 0.7},
    {"name": "flux_at_sample", "target": "maximize", "weight": 0.3, "min_constraint": 1e9}  # ph/s
]
```

**Success metric**: Speckle contrast β > 0.5 (measured from detector images)

**BLOP advantage**: Needs feedback from System E (detector) → BLOP can optimize in closed loop

**Implementation**:
```python
from blop import Agent
from blop.dofs import DOF
from blop.objectives import Objective

# Define degrees of freedom
dofs = [
    DOF(name="h_slit", range=(0.01, 0.5), units="mm"),  # Horizontal slit
    DOF(name="v_slit", range=(0.01, 0.5), units="mm"),  # Vertical slit
    DOF(name="mono_pitch", range=(-0.1, 0.1), units="deg"),
    DOF(name="crl_z", range=(-5, 5), units="mm")
]

# Define objectives
objectives = [
    Objective(name="beta", target="max", weight=0.7),
    Objective(name="flux", target="max", weight=0.3, min=1e9)
]

# Create BLOP agent
agent = Agent(dofs=dofs, objectives=objectives, db=databroker)

# Run optimization (integrates with Bluesky)
agent.learn(method="expected_improvement", n_iter=50)
```

**Expected improvement**:
- β improvement: 0.3 → 0.6 (2× better speckle quality)
- Setup time: 60 min → 15 min
- Reproducibility: Consistent alignment across experiments

---

### 2. **ISS (8-ID) - XAS Flux Maximization** ⚡ HIGH PRIORITY

**Challenge**: Fast 1s XAS scans require maximum flux, but DCM + KB alignment is 6-dimensional

**System B components to optimize**:
- Double-crystal monochromator (crystal pitch, roll compensation) - 2 DOF
- KB mirrors (pitch, yaw, positions) - 4 DOF
- **Total: ~6 degrees of freedom**

**Optimization objectives**:
```python
objectives = [
    {"name": "flux_at_sample", "target": "maximize", "weight": 0.8},
    {"name": "spot_size", "target": "minimize", "weight": 0.2, "max_constraint": 100}  # μm
]
```

**Success metric**: Flux > 10^12 photons/sec at sample (measured by I0 monitor)

**Implementation**:
```python
dofs = [
    DOF(name="dcm_pitch", range=(-0.05, 0.05), units="deg"),
    DOF(name="dcm_roll", range=(-0.02, 0.02), units="deg"),
    DOF(name="kb1_pitch", range=(-0.5, 0.5), units="mrad"),
    DOF(name="kb1_yaw", range=(-0.5, 0.5), units="mrad"),
    DOF(name="kb2_pitch", range=(-0.5, 0.5), units="mrad"),
    DOF(name="kb2_yaw", range=(-0.5, 0.5), units="mrad")
]

objectives = [
    Objective(name="I0_flux", target="max", weight=0.8),
    Objective(name="focal_spot_fwhm", target="min", weight=0.2, max=100)
]

agent = Agent(dofs=dofs, objectives=objectives, db=databroker)
agent.learn(method="expected_improvement", n_iter=40)
```

**Expected improvement**:
- Flux increase: 20-30% more photons (better SNR for 1s scans)
- Stability: Maintain alignment over 1500h operando experiments
- Setup time: 45 min → 12 min

---

### 3. **SIX (2-ID) - RIXS Resolution Optimization** ⚡ HIGH PRIORITY

**Challenge**: RIXS requires maximum energy resolution (minimize ΔE), but grating + KB + slits create complex optimization landscape

**System B components to optimize**:
- Grating monochromator (pitch, slits) - 3 DOF
- KB focusing mirrors (positions, angles) - 4 DOF
- **Total: ~7 degrees of freedom**

**Optimization objectives**:
```python
objectives = [
    {"name": "energy_resolution_delta_E", "target": "minimize", "weight": 0.8},
    {"name": "flux_at_sample", "target": "maximize", "weight": 0.2, "min_constraint": 1e11}
]
```

**Success metric**: ΔE < 15 meV at 853 eV (measured from elastic line width)

**Implementation**:
```python
dofs = [
    DOF(name="grating_pitch", range=(-0.1, 0.1), units="deg"),
    DOF(name="entrance_slit", range=(0.01, 0.2), units="mm"),
    DOF(name="exit_slit", range=(0.01, 0.2), units="mm"),
    DOF(name="kb1_pitch", range=(-0.3, 0.3), units="mrad"),
    DOF(name="kb2_pitch", range=(-0.3, 0.3), units="mrad")
]

objectives = [
    Objective(name="elastic_linewidth", target="min", weight=0.8),  # Energy resolution
    Objective(name="rixs_count_rate", target="max", weight=0.2, min=1e11)
]

agent = Agent(dofs=dofs, objectives=objectives, db=databroker)
agent.learn(method="expected_improvement", n_iter=45)
```

**Expected improvement**:
- Resolution: 17 meV → 14 meV (18% better)
- Consistent alignment (reduces user-to-user variation)
- Setup time: 50 min → 15 min

---

## 🔄 BLOP Workflow Integration

### Proposed Scientific Reflow Workflow Step:

**Step EM-02.5: Adaptive Beamline Alignment (BLOP)** - *Optional but Recommended*

```
Input:
- Beamline profile with blop_config
- User-specified optimization goals (from Step EM-02)

Process:
1. Load System B degrees of freedom from beamline profile
2. Initialize BLOP agent with objectives + constraints
3. Run Bayesian optimization (integrates with Bluesky)
4. Measure optimization metrics from System E (detector feedback)
5. Iterate until convergence (typically 30-50 iterations)
6. Save optimized motor positions to working_memory.json

Output:
- Optimized beamline configuration
- Validation report (achieved vs target metrics)
- Ready for System D measurement

Estimated time: 10-20 minutes (vs 30-60 min manual)
```

---

## 📋 Beamline Profile Schema Update

Add BLOP configuration to beamline profiles:

```json
{
  "systems_config": {
    "system_b": {
      "component_type": "monochromator_focusing",
      "optimization": "coherence_preservation",

      "blop_config": {
        "applicable": true,
        "optimization_priority": "critical",
        "degrees_of_freedom": [
          {
            "component": "coherence_slits",
            "dof": "h_opening",
            "range": [0.01, 0.5],
            "units": "mm",
            "motor_name": "h_slit"
          },
          {
            "component": "coherence_slits",
            "dof": "v_opening",
            "range": [0.01, 0.5],
            "units": "mm",
            "motor_name": "v_slit"
          },
          {
            "component": "monochromator",
            "dof": "crystal_pitch",
            "range": [-0.1, 0.1],
            "units": "deg",
            "motor_name": "dcm_pitch"
          }
        ],

        "objectives": [
          {
            "name": "speckle_contrast_beta",
            "target": "maximize",
            "weight": 0.7,
            "measurement_source": "system_e_detector",
            "calculation": "variance(I) / mean(I)^2 - 1"
          },
          {
            "name": "flux_at_sample",
            "target": "maximize",
            "weight": 0.3,
            "min_constraint": 1e9,
            "measurement_source": "i0_monitor"
          }
        ],

        "optimization_settings": {
          "method": "expected_improvement",
          "max_iterations": 50,
          "convergence_threshold": 0.01,
          "initial_samples": 10,
          "estimated_time_minutes": 15
        },

        "bluesky_integration": {
          "adaptive_plan": "blop.Agent.learn",
          "acquisition_function": "expected_improvement",
          "model": "gaussian_process",
          "databroker_required": true
        }
      }
    }
  }
}
```

---

## 🚀 Getting Started: BLOP + Scientific Reflow

### Step 1: Install BLOP in Reflow Environment

```bash
# From Reflow root directory
pixi add blop

# Or add to pixi.toml
[dependencies]
blop = ">=0.8.1"
```

### Step 2: Update Beamline Profiles with BLOP Config

Add `blop_config` to System B in beamline profiles (see schema above)

### Step 3: Implement BLOP Workflow Step

Create new workflow step: `EM-02.5-adaptive_alignment.json`

```json
{
  "step_id": "EM-02.5",
  "step_name": "Adaptive Beamline Alignment (BLOP)",
  "description": "Use Bayesian optimization to align System B components for optimal performance",
  "optional": true,
  "recommended_for": ["xpcs", "high_resolution_rixs", "operando_xas"],

  "actions": [
    {
      "action_id": "EM-02.5-A01",
      "description": "Load BLOP configuration from beamline profile",
      "details": "Extract blop_config from system_b in beamline profile"
    },
    {
      "action_id": "EM-02.5-A02",
      "description": "Initialize BLOP agent",
      "command": "python {tools_path}/run_blop_optimization.py --profile {beamline_profile} --objectives {user_objectives}",
      "details": "Create BLOP agent with DOFs and objectives from profile"
    },
    {
      "action_id": "EM-02.5-A03",
      "description": "Run Bayesian optimization",
      "details": "Execute agent.learn() with Bluesky integration, measure objectives from System E",
      "estimated_time": "10-20 minutes"
    },
    {
      "action_id": "EM-02.5-A04",
      "description": "Validate optimization results",
      "details": "Compare achieved metrics to target values, verify convergence",
      "validation": "Metrics within 5% of target OR improvement > 20% vs initial"
    },
    {
      "action_id": "EM-02.5-A05",
      "description": "Save optimized configuration",
      "output": "context/blop_optimized_positions.json",
      "details": "Save motor positions, achieved metrics, optimization history"
    }
  ]
}
```

### Step 4: Create BLOP Wrapper Tool

Create `scientific-reflow/tools/run_blop_optimization.py`:

```python
#!/usr/bin/env python3
"""
BLOP optimization wrapper for Scientific Reflow

Integrates BLOP Bayesian optimization into System B alignment workflow.
"""

import json
from pathlib import Path
from blop import Agent
from blop.dofs import DOF
from blop.objectives import Objective

def load_blop_config(beamline_profile_path: str):
    """Load BLOP configuration from beamline profile."""
    with open(beamline_profile_path, 'r') as f:
        profile = json.load(f)

    return profile['systems_config']['system_b'].get('blop_config', {})

def create_blop_agent(blop_config, databroker):
    """Create BLOP agent from configuration."""

    # Create DOFs
    dofs = [
        DOF(
            name=dof['motor_name'],
            range=tuple(dof['range']),
            units=dof.get('units', '')
        )
        for dof in blop_config['degrees_of_freedom']
    ]

    # Create objectives
    objectives = [
        Objective(
            name=obj['name'],
            target=obj['target'],
            weight=obj.get('weight', 1.0),
            min=obj.get('min_constraint'),
            max=obj.get('max_constraint')
        )
        for obj in blop_config['objectives']
    ]

    # Create agent
    agent = Agent(
        dofs=dofs,
        objectives=objectives,
        db=databroker
    )

    return agent

def run_optimization(agent, blop_config):
    """Run BLOP optimization."""
    settings = blop_config.get('optimization_settings', {})

    method = settings.get('method', 'expected_improvement')
    max_iter = settings.get('max_iterations', 50)

    # Run optimization
    agent.learn(method=method, n_iter=max_iter)

    # Get results
    best_point = agent.best
    history = agent.table

    return {
        'best_point': best_point,
        'history': history,
        'converged': agent.converged
    }

def main():
    # Parse args, load config, run optimization
    # ... (implementation details)
    pass

if __name__ == "__main__":
    main()
```

---

## 📊 Success Metrics

### BLOP Effectiveness Metrics:

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Setup time reduction** | 30-60 min → 10-20 min | Compare manual vs BLOP alignment time |
| **Performance improvement** | 20-50% better objective | Compare achieved metric to manual alignment |
| **Reproducibility** | <5% variation | Standard deviation across multiple optimizations |
| **Convergence rate** | <50 iterations | Number of iterations to reach target |

### Beamline-Specific Success:

- **XPCS (CHX)**: β > 0.5, flux > 10^9 ph/s
- **XAS (ISS)**: Flux > 10^12 ph/s, spot < 100 μm
- **RIXS (SIX)**: ΔE < 15 meV, flux > 10^11 ph/s

---

## 🎯 Priority Roadmap

### Phase 1: Proof-of-Concept (CHX XPCS) - **Start Here**
- Implement BLOP for coherence optimization (slits + mono + CRL)
- Validate with real XPCS experiments
- Measure β improvement (manual vs BLOP)
- **Timeline**: 2-4 weeks

### Phase 2: Extend to ISS (XAS) and SIX (RIXS)
- Flux optimization (ISS)
- Resolution optimization (SIX)
- **Timeline**: 4-6 weeks

### Phase 3: Integration into Scientific Reflow Workflows
- Add EM-02.5 workflow step
- Update beamline profiles with blop_config
- Create BLOP wrapper tools
- **Timeline**: 6-8 weeks

### Phase 4: Scale to 10+ NSLS-II Beamlines
- Create BLOP configs for all techniques
- Beamline-wide deployment
- **Timeline**: 3-6 months

---

## 📞 Resources

**BLOP**:
- PyPI: https://pypi.org/project/blop/ (v0.8.1)
- Docs: https://nsls-ii.github.io/blop/
- GitHub: https://github.com/NSLS-II/blop

**Scientific Reflow**:
- BLOP Integration Analysis: `test_data/BLOP_INTEGRATION_ANALYSIS.md`
- Validation Results: `test_data/VALIDATION_RESULTS_THREE_BEAMLINES.md`
- Beamline Profiles: `definitions/beamline_profiles/`

**Contact**:
- Your team develops BLOP - let's collaborate on integration! 🚀

---

**Generated**: 2025-11-14
**BLOP Version**: 0.8.1 (Latest)
**Status**: Ready for integration into Scientific Reflow workflows
