# Framework-Specific Test: Cycle Detection - Systems Biology

## Framework

**Systems Biology**

## Purpose

Validate that feedback loops in biological systems are detected with **INFO** severity (not error).

## Scenario

**System**: p53-MDM2 negative feedback loop (famous regulatory circuit):

```
p53 → MDM2 → p53 (inhibition)
```

**Feedback Loop**:
- p53 activates transcription of MDM2
- MDM2 protein ubiquitinates p53 for degradation
- Less p53 → less MDM2 → p53 levels recover
- Creates oscillating homeostasis

## Why This Is GOOD (Biology Context)

In biological systems, feedback loops are:
1. **Fundamental Mechanisms**: How cells maintain homeostasis
2. **Expected Behavior**: NOT a design flaw, but intentional regulation
3. **Critical Function**: p53-MDM2 loop prevents uncontrolled cell death
4. **Common Pattern**: Negative feedback in virtually all regulatory pathways

**This is NOT an error - this is how biology works!**

## Expected Detection

**Command**:
```bash
python3 tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --framework systems_biology \
  --cycles \
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
        ["gene_p53", "gene_mdm2", "gene_p53"]
      ],
      "severity": "info",
      "interpretation": "Negative feedback loop - regulatory circuit for homeostasis",
      "biological_significance": "p53-MDM2 loop prevents excessive apoptosis"
    }
  }
}
```

## Biological Significance

The p53-MDM2 loop is one of the most studied regulatory circuits:
- **Discovery**: Led to Nobel Prize work
- **Cancer Research**: Mutations in this loop cause cancer
- **Drug Targets**: MDM2 inhibitors in clinical trials

## Pass Criteria

- Cycle detected (p53 → MDM2 → p53)
- Severity: **INFO** (not error or warning)
- Interpretation: Feedback loop (not circular dependency)
- Tool recognizes this is expected in biology

## Related Tests

- `cycle_detection_uaf` - Same cycle structure, ERROR severity (bad in IT)
- `cycle_detection_decision_flow` - Rework loops, WARNING severity
