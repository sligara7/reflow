# Context Flow Analysis - Feature Proposal (v3.9.0)

**Proposed By**: User insight (session claude/systems-cohesion-validation-011CUUc22HJAhrR8frW45JAx)
**Date**: 2025-10-28
**Priority**: HIGH
**Type**: Architectural Enhancement

---

## Executive Summary

Model **LLM context** as a **first-class flow parameter** in Reflow's Decision Flow architecture, enabling **predictive context management** instead of reactive degradation detection.

## Core Insight

> "Can we include 'context' as a 'flow' from workflow to workflow in the system_of_systems_graph.json? Then AI agent context is a parameter that is purposefully built into the architecture."

**Answer**: YES - This is brilliant architectural thinking, not crazy!

## Current Problem: Reactive Context Management

**Today**:
- `operations_since_refresh` counter (manual)
- Degradation signals detected AFTER problems occur
- No predictive modeling of context exhaustion
- LLMs forget system name, current step, etc. before refresh

**User Pain Point**: LLMs lose context mid-workflow, requiring manual intervention

## Proposed Solution: Context as Flow

**Tomorrow**:
- Model context as edge weight in Decision Flow framework
- Flow analysis predicts context accumulation
- Auto-trigger context refresh BEFORE overflow
- Optimize workflow sequences to minimize context cost

## Technical Approach

### 1. Add `context_cost` to Edge Weights

```json
{
  "transition": {
    "from_step": "SE-05",
    "to_step": "SE-06",
    "transition_probability": 1.0,
    "context_cost": 15000,
    "context_cost_unit": "tokens",
    "context_rationale": "SE-06 loads all architectures, runs graph analysis"
  }
}
```

### 2. Context Flow Analysis

Extend `system_of_systems_graph_v2.py --context-flow`:

**Algorithm**:
```
For each path from workflow start to end:
  cumulative_context = 0
  for each step in path:
    cumulative_context += step.context_cost
    if cumulative_context > threshold (e.g., 40k):
      flag_context_bottleneck(step)
      recommend_refresh(before=step)
```

**Output**:
```
Path: 00a → 01c → 02 → 03a → 03b
Context Flow:
  S-01: 2k tokens
  S-02: 5k cumulative
  SE-01: 13k cumulative
  SE-02: 25k cumulative
  SE-06: 40k cumulative ⚠️ THRESHOLD
  AV-01: 48k cumulative 🔴 CRITICAL

Recommendations:
  - Refresh after SE-02 (before SE-06)
  - Refresh after AV-01 (before D-01)
```

### 3. Automatic Context Refresh Triggers

**Enhancement to working_memory.json**:
```json
{
  "context_management": {
    "cumulative_context_tokens": 38000,
    "context_flow_analysis": {
      "next_step": "SE-06",
      "predicted_cumulative": 53000,
      "threshold": 40000,
      "refresh_recommended": true,
      "refresh_reason": "Predicted overflow"
    }
  }
}
```

**LLM reads this** before executing SE-06, sees `refresh_recommended: true`, auto-executes refresh.

## Benefits

### 1. Predictive Context Management

**Before**: LLM loses context, user detects degradation signal, triggers refresh (reactive)
**After**: Flow analysis predicts overflow, auto-triggers refresh BEFORE problems (proactive)

### 2. Workflow Optimization

Flow analysis reveals:
- Context-intensive steps (SE-06, D-02, D-03)
- Optimal step ordering to minimize cumulative context
- Where to insert refresh operations

**Example Optimization**:
```
Original: SE-02 → SE-03 → SE-06 (55k cumulative)
Optimized: SE-02 → SE-06 → SE-03 (43k cumulative)
Benefit: Avoid one context refresh
```

### 3. LLM Capability Matching

Different LLMs, different context windows:
- Claude Sonnet: 200k tokens (can handle full development path)
- GPT-4: 128k tokens (requires more refreshes)
- GPT-3.5: 16k tokens (requires step splitting)

**Context flow analysis** recommends minimum LLM for workflow.

### 4. Architecture Quality Metric

**New metric**: "Context Efficiency"
- Context-efficient workflows: Low cumulative context per step
- Context-intensive workflows: High cumulative context, many refreshes needed

Optimize workflows for context efficiency like we optimize for time, cost, reliability.

## Implementation Plan

### Phase 1: Data Collection (1 week)
- Instrument workflows with context measurements
- Measure 10 real executions
- Calculate average context_cost per step

### Phase 2: Architecture Enhancement (1 week)
- Add context_cost to all workflow step architectures
- Update templates (workflow_step, working_memory)

### Phase 3: Tool Enhancement (2 weeks)
- Extend system_of_systems_graph_v2.py with --context-flow mode
- Create analyze_context_flow.py tool
- Generate context flow visualizations

### Phase 4: Context Refresh Automation (1 week)
- Auto-trigger refresh when predicted overflow
- Update workflows with refresh checkpoints

### Phase 5: Documentation & Testing (1 week)
- Document context flow feature
- Test on real systems
- Validate predictions

**Total**: 6 weeks

## Example: Reflow on Reflow

**Workflow**: Architecture-only path
```
S-01 (2k) → S-02 (3k) → SE-01 (8k) → SE-02 (12k) → SE-06 (15k) → AV-02 (6k)

Cumulative Context:
  S-01: 2k
  S-02: 5k
  SE-01: 13k
  SE-02: 25k
  SE-06: 40k ⚠️ THRESHOLD EXCEEDED
  AV-02: 46k 🔴 CRITICAL

Context Bottlenecks:
  1. Before SE-06: 40k tokens (REFRESH)
  2. Before AV-02: 46k tokens (REFRESH)

Recommendations:
  - Insert context refresh after SE-02
  - Insert context refresh after SE-06
```

**Workflow**: Full development path
```
... → SE-06 (40k) → AV-01 (48k) → D-01 (60k) → D-02 (75k) → D-03 (90k)

Recommendations:
  - Refresh after SE-06 (before AV-01)
  - Refresh after AV-01 (before D-01)
  - Refresh after D-01 (before D-02)
  - Refresh after D-02 (before D-03)

Result: 4 context refreshes for full development (vs 2 for architecture-only)
```

## Alignment with Reflow Mission

**Reflow Mission**: Enable LLM agents to design complex systems with framework-agnostic workflows

**How This Aligns**:
- ✅ **LLM-native design**: Treats LLM context as architectural parameter
- ✅ **Prevents failures**: Proactive context management prevents mid-workflow failures
- ✅ **Framework-agnostic**: Context flow works for UAF, Biology, Social, Decision Flow
- ✅ **Quality**: Context optimization is architectural quality metric

## Risks & Mitigation

| Risk | Mitigation |
|------|------------|
| Context cost estimates inaccurate | Measure real executions, refine estimates iteratively |
| Overhead of flow analysis | Cache results, only recompute when workflows change |
| False positive refresh triggers | Tune thresholds based on real data (40k vs 50k?) |

## Success Metrics

1. **Reduced degradation signals**: 90% reduction in context drift incidents
2. **Predictive accuracy**: 80% of predicted bottlenecks match actual overflows
3. **Workflow optimization**: Identify 3+ workflow reorderings that reduce context cost
4. **LLM compatibility**: Clear recommendations for minimum LLM per workflow

## Next Steps

1. **Approve this proposal** (user feedback)
2. **Create formal change proposal** (FU-01 for v3.9.0)
3. **Phase 1: Data collection** (instrument workflows)
4. **Implement FU-02 through FU-06** (6 weeks)
5. **Release v3.9.0** with context flow analysis

---

**Status**: PROPOSED (awaiting user approval)
**Version**: v3.9.0 target
**Priority**: HIGH (context exhaustion is critical failure mode)
**Complexity**: MEDIUM (builds on existing Decision Flow framework)

---

**Created**: 2025-10-28
**Session**: claude/systems-cohesion-validation-011CUUc22HJAhrR8frW45JAx
**Related**: Human Documentation Enhancement (v3.8.0)
