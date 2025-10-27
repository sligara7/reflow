# Framework-Specific Test: Cycle Detection - Decision Flow

## Framework

**Decision Flow** (Workflows and State Machines)

## Purpose

Validate that rework loops in workflows are detected with **WARNING** severity and efficiency metrics.

## Scenario

**System**: Architecture design workflow with validation gate:

```
SE-02 (Design) → SE-03 (Validation) → SE-02 (Rework if failed)
```

**Rework Loop**:
- SE-02: Design service architectures
- SE-03: Validate architecture (quality gate)
- If validation fails (30% probability) → return to SE-02 for fixes
- If validation passes (70% probability) → proceed to SE-04

## Why This Is Different (Workflow Context)

In workflow systems, rework loops are:
1. **Expected but Costly**: Quality gates should catch issues, but rework slows workflow
2. **Measurable**: 30% rework rate = efficiency metric
3. **Optimizable**: Reduce rework by improving SE-02 or relaxing SE-03 criteria
4. **Not Errors**: Validation gates intentionally create loops, but measure them

**This is WARNING - not an error, but something to monitor and optimize.**

## Expected Detection

**Command**:
```bash
python3 tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --framework decision_flow \
  --cycles \
  --flow \
  --output detected_output.json
```

**Expected Output**:
```json
{
  "graph_analysis": {
    "cycles": {
      "detected": true,
      "count": 1,
      "cycles": [
        ["SE-02", "SE-03", "SE-02"]
      ],
      "severity": "warning",
      "interpretation": "Rework loop - validation failures require iteration",
      "rework_metrics": {
        "rework_rate": 0.3,
        "avg_iterations": 1.43,
        "efficiency": 0.70
      }
    },
    "flow": {
      "critical_path": ["SE-02", "SE-03", "SE-04"],
      "bottleneck": "SE-03",
      "rework_impact": "30% workflows iterate, adding ~40% time"
    }
  }
}
```

## Workflow Efficiency Analysis

**Rework Rate**: 30%
- First pass success: 70%
- Second pass success: 70% * 30% = 21%
- Third pass success: 70% * 9% = 6.3%
- Average iterations: 1 / 0.7 = 1.43 iterations

**Cost**: Each rework iteration costs time and resources

**Optimization Strategies**:
1. Improve SE-02 quality → reduce rework rate
2. Add interim checks → catch issues earlier
3. Relax SE-03 criteria → higher pass rate (if acceptable)

## Pass Criteria

- Cycle detected (SE-02 → SE-03 → SE-02)
- Severity: **WARNING** (not error, not just info)
- Rework rate calculated from transition probabilities
- Efficiency metrics provided

## Related Tests

- `cycle_detection_uaf` - Same structure, ERROR severity (bad in IT)
- `cycle_detection_biology` - Same structure, INFO severity (good in biology)
- `flow_analysis_decision_flow` - Critical path analysis
