# Change Proposal: Context Flow Analysis (v3.9.0)

**Date**: 2025-10-28
**Proposal ID**: FU-v3.9.0-context-flow
**Type**: Feature Enhancement
**Priority**: HIGH
**Complexity**: MEDIUM

---

## 1. Executive Summary

Model **LLM context** as a **first-class flow parameter** in Reflow's Decision Flow framework, enabling **predictive context management** instead of reactive degradation detection.

**Core User Insight**:
> "Can we include 'context' as a 'flow' from workflow to workflow in the system_of_systems_graph.json? Then AI agent context is a parameter that is purposefully built into the architecture."

---

## 2. Business Justification

### Problem Statement

**Current State (Reactive)**:
- LLMs lose context mid-workflow without warning
- `operations_since_refresh` counter is manual and imprecise
- Context degradation detected AFTER problems occur
- User must manually intervene when LLM forgets system name, current step

**Impact**:
- Workflow interruptions
- Loss of architectural context
- Manual refresh interventions
- Reduced LLM agent reliability

### Proposed Solution

**Future State (Predictive)**:
- Model context as edge weight in Decision Flow framework
- Flow analysis predicts context accumulation before overflow
- Auto-trigger context refresh BEFORE problems
- Optimize workflow sequences to minimize context cost

### Expected Benefits

1. **Predictive Context Management**: 90% reduction in context drift incidents
2. **Workflow Optimization**: Identify optimal step ordering to minimize context
3. **LLM Capability Matching**: Recommend minimum LLM for each workflow path
4. **Architecture Quality Metric**: "Context Efficiency" as architectural parameter

---

## 3. Technical Approach

### 3.1. Add `context_cost` to Edge Weights

Extend workflow step definitions with context cost metadata:

```json
{
  "step_id": "SE-06",
  "step_name": "Graph Generation",
  "context_metadata": {
    "context_cost": 15000,
    "context_cost_unit": "tokens",
    "context_rationale": "Loads all architectures, runs NetworkX analysis",
    "context_accumulation": "cumulative"
  },
  "transitions": [
    {
      "to_step": "AV-01",
      "transition_probability": 1.0,
      "context_cost": 15000
    }
  ]
}
```

### 3.2. Extend system_of_systems_graph_v2.py

Add `--context-flow` analysis mode:

**Algorithm**:
```python
def analyze_context_flow(graph, start_step, end_step, threshold=40000):
    """
    Analyze cumulative context cost along workflow paths.

    Returns:
    - Cumulative context at each step
    - Context bottlenecks (steps exceeding threshold)
    - Recommended refresh points
    """
    paths = nx.all_simple_paths(graph, start_step, end_step)

    for path in paths:
        cumulative = 0
        bottlenecks = []

        for step in path:
            cumulative += step.get('context_cost', 0)
            if cumulative > threshold:
                bottlenecks.append({
                    'step': step,
                    'cumulative': cumulative,
                    'severity': 'CRITICAL' if cumulative > 50000 else 'WARNING'
                })

        return {
            'path': path,
            'cumulative_by_step': cumulative_tracking,
            'bottlenecks': bottlenecks,
            'refresh_recommendations': generate_refresh_points(bottlenecks)
        }
```

### 3.3. Enhanced working_memory.json

Add context flow tracking:

```json
{
  "context_management": {
    "operations_since_refresh": 2,
    "cumulative_context_tokens": 25000,
    "context_flow_analysis": {
      "current_step": "SE-05",
      "next_step": "SE-06",
      "predicted_cumulative": 40000,
      "threshold": 40000,
      "refresh_recommended": true,
      "refresh_reason": "Predicted overflow at SE-06",
      "recommended_refresh_before": "SE-06"
    }
  }
}
```

### 3.4. Context Flow Visualization

Create `visualize_context_flow.py`:
- Mermaid diagram showing context accumulation
- Highlight bottleneck steps
- Show refresh points

---

## 4. Implementation Plan

### Phase 1: Foundation (v3.9.0 MVP)
**Duration**: 2 weeks
**Deliverables**:
- Add context_cost to workflow step templates
- Extend system_of_systems_graph_v2.py with --context-flow
- Update working_memory template with context_flow_analysis
- Initial context cost estimates (conservative)
- Basic visualization

### Phase 2: Data Collection (v3.9.1)
**Duration**: 2-4 weeks
**Deliverables**:
- Instrument real Reflow executions
- Collect actual context cost measurements
- Refine estimates based on data
- Tune thresholds (40k vs 50k)

### Phase 3: Automation (v3.9.2)
**Duration**: 1 week
**Deliverables**:
- Auto-trigger refresh when predicted overflow
- Workflow optimization recommendations
- LLM capability matching

---

## 5. Impact Analysis

### 5.1. Files Modified

**Tools** (1 file):
- `tools/system_of_systems_graph_v2.py` - Add --context-flow mode

**Tools Added** (1 file):
- `tools/visualize_context_flow.py` - Context flow visualization

**Templates** (2 files):
- `templates/workflow_step_template.json` - Add context_metadata
- `templates/working_memory_template.json` - Add context_flow_analysis

**Workflows** (15 files):
- All workflow_steps/*.json - Add context_cost estimates

**Documentation** (3 files):
- `CLAUDE.md` - Add Context Flow Analysis section
- `README.md` - Update v3.9.0 features
- `CHANGELOG.md` - Add v3.9.0 entry

### 5.2. Backward Compatibility

✅ **Fully backward compatible**:
- context_cost is optional field (defaults to 0)
- Existing workflows work without modification
- --context-flow is new optional flag

### 5.3. Dependencies

**No new dependencies** - uses existing NetworkX for path analysis

---

## 6. Testing Strategy

### 6.1. Unit Tests

- `test_context_flow_analysis()` - Test cumulative calculation
- `test_bottleneck_detection()` - Test threshold detection
- `test_refresh_recommendations()` - Test recommendation logic

### 6.2. Integration Tests

- Run Reflow on Reflow (architecture-only path)
- Verify context bottleneck predictions
- Validate refresh recommendations

### 6.3. Validation Criteria

1. Context flow analysis completes without errors
2. Bottlenecks identified at expected steps (SE-06, D-02)
3. Refresh recommendations reduce predicted overflow
4. Visualization generates valid Mermaid diagrams

---

## 7. Documentation Updates

### 7.1. CLAUDE.md

Add section after "Human Documentation Workflow":

```markdown
## Context Flow Analysis (v3.9.0)

**Purpose**: Predictive context management through flow analysis

**Key Concept**: Model LLM context as edge weight parameter

**Usage**:
```bash
python3 {paths.tools_path}/system_of_systems_graph_v2.py \\
  {paths.system_root}/specs/machine/index.json \\
  --context-flow --threshold 40000
```

**Output**: Context bottlenecks, refresh recommendations, optimization opportunities
```

### 7.2. README.md

Update Key Features section:

```markdown
**Context Flow Analysis (NEW v3.9.0):**
- Model LLM context as first-class architectural parameter
- Predictive context management (not reactive)
- Automatic refresh recommendations before overflow
- Workflow optimization for context efficiency
- LLM capability matching (Claude 200k vs GPT-4 128k)
```

---

## 8. Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| Context cost estimates inaccurate | Medium | Start conservative, refine with real data in Phase 2 |
| Overhead of flow analysis | Low | Cache results, only recompute when workflows change |
| False positive refresh triggers | Medium | Tune thresholds (40k default, configurable) |
| Complexity for users | Low | Feature is optional, existing workflows unchanged |

---

## 9. Success Metrics

1. **Feature Completeness**: --context-flow mode implemented and tested
2. **Prediction Accuracy**: Identify 3+ context bottlenecks in real workflows
3. **Documentation**: Context Flow section added to CLAUDE.md and README.md
4. **Backward Compatibility**: All existing workflows work without modification

**v3.9.1 Metrics** (Phase 2):
- 90% reduction in context drift incidents
- 80% prediction accuracy for actual overflows

---

## 10. Alignment with Reflow Mission

**Reflow Mission**: Enable LLM agents to design complex systems with framework-agnostic workflows

**How This Aligns**:
- ✅ **LLM-native design**: Treats LLM context as architectural parameter
- ✅ **Prevents failures**: Proactive context management prevents mid-workflow failures
- ✅ **Framework-agnostic**: Context flow works for all frameworks (UAF, Biology, Social, Decision Flow)
- ✅ **Quality**: Context efficiency as architectural quality metric

---

## 11. Approval & Sign-off

**Status**: ✅ APPROVED (user initiated implementation request)
**Approved By**: User
**Approved Date**: 2025-10-28

**Next Steps**:
1. ✅ Change proposal created (FU-01)
2. ⏳ Implement context flow analysis (FU-02)
3. ⏳ Update workflow templates (FU-03)
4. ⏳ Create visualization tool (FU-04)
5. ⏳ Testing (FU-05)
6. ⏳ Documentation (FU-06)
7. ⏳ Tag v3.9.0

---

**Created**: 2025-10-28
**Session**: claude/implement-reflow-workflow-011CUUc22HJAhrR8frW45JAx
**Previous**: v3.8.0 (Human Documentation)
**Next**: v3.9.0 (Context Flow Analysis)
