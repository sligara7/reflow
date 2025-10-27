# Tool Capability Test: Flow Analysis - With Edge Weights

## Test Category
**Tool Capabilities - system_of_systems_graph_v2.py**

## Framework
**Decision Flow**

## Analysis Flags Tested
- `--flow`: Flow analysis and path calculations
- `--cycles`: Cycle detection (rework loops)
- `--dag`: DAG validation (expect FALSE - has cycles)

## Purpose
Validate that flow analysis **succeeds** when edge weights are properly defined. Flow analysis requires edge weights to calculate:
- Critical paths
- Success probabilities
- Expected iterations
- Rework loop impact

## Scenario

**System**: Software development workflow with quality gates

**Process Steps**:
1. **WF-REQ**: Requirements Review (start node)
2. **WF-DESIGN**: Design Phase (quality gate, 80% pass / 20% rework)
3. **WF-IMPL**: Implementation Phase
4. **WF-TEST**: Testing Phase (quality gate, 70% pass / 30% rework)
5. **WF-PROD**: Production Deployment (end node)

**Rework Loops**:
- Design rejection (20%) → Requirements rework → Re-review
- Testing failure (30%) → Implementation rework → Re-test

**Edge Weights Defined**:
```
REQ → DESIGN: 1.0 (100% - always proceed)
DESIGN → IMPL: 0.8 (80% - design passes)
DESIGN → REQ-REWORK: 0.2 (20% - design rejected)
IMPL → TEST: 1.0 (100% - always proceed)
TEST → PROD: 0.7 (70% - testing passes)
TEST → IMPL-REWORK: 0.3 (30% - testing failed)
```

## Expected Behavior

**Flow Analysis Should**:
1. ✅ Detect edge weights are present
2. ✅ Calculate critical path: REQ → DESIGN → IMPL → TEST → PROD
3. ✅ Calculate success probability (first-pass): 0.8 × 0.7 = 0.56 (56%)
4. ✅ Detect 2 rework loops:
   - Design → Requirements: 20% rework rate
   - Testing → Implementation: 30% rework rate
5. ✅ Calculate expected iterations:
   - Design phase: 1 / (1 - 0.2) = 1.25 iterations
   - Testing phase: 1 / (1 - 0.3) = 1.43 iterations
6. ✅ Calculate total expected time considering rework
7. ✅ No errors about missing edge weights

## Flow Analysis Calculations

**Critical Path Time** (first pass):
- Requirements: 40 hours
- Design: 80 hours
- Implementation: 160 hours
- Testing: 60 hours
- Production: 8 hours
- **Total**: 348 hours

**Expected Time with Rework**:
- Design iterations: 80 × 1.25 = 100 hours
- Testing iterations: 60 × 1.43 = 85.8 hours
- **Total expected**: 40 + 100 + 160 + 85.8 + 8 = 393.8 hours

**Success Metrics**:
- First-pass success: 56%
- Design rework: 20% of projects
- Testing rework: 30% of projects
- Overall efficiency: 348 / 393.8 = 88.4%

## Pass Criteria

1. ✅ Tool executes without errors
2. ✅ Flow analysis section appears in output
3. ✅ Edge weights detected and used
4. ✅ Critical path identified
5. ✅ Success probability calculated
6. ✅ Rework loops detected (2 cycles)
7. ✅ Expected iterations calculated
8. ✅ No warnings about missing edge weights

## Comparison

**This Test (WITH weights)**: Flow analysis succeeds, comprehensive metrics calculated

**Companion Test (NO weights)**: `flow_analysis_no_weights/` - Tool should gracefully handle absence, warn but not crash

## Why This Matters

**Edge Weights Enable Flow Analysis**:
- Without weights: Cannot calculate flow, probabilities, or optimization
- With weights: Can identify bottlenecks, optimize paths, predict outcomes

**Framework-Specific**:
- Decision Flow: Probabilities (0.0 - 1.0)
- UAF: Request rates (req/sec), data volumes (MB/sec)
- Biology: Reaction rates (molecules/sec)
- Ecology: Energy transfer (kcal/m²/year)

**Real-World Applications**:
- Workflow optimization (reduce rework)
- Resource allocation (critical path focus)
- Risk assessment (success probability)
- Process improvement (identify high-rework steps)

## Test Architecture

**Files**:
- 7 architecture files (5 main steps + 2 rework connectors)
- service_arch_index.json
- expected_output.json (pass criteria)
- README.md (this file)

**Total Lines**: ~240 (architectures) + test framework

## Execution

```bash
cd /home/user/reflow/tests/fixtures/tool_capabilities/system_of_systems_graph/flow_analysis_with_weights

python3 /home/user/reflow/tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --flow --cycles --dag --detect-gaps \
  --output specs/machine/graphs/flow_analysis_output.json

# Validate against expected_output.json
```

## Related Tests

- `flow_analysis_no_weights/` - Same workflow WITHOUT edge weights (should warn gracefully)
- `cycle_detection_decision_flow/` - Cycle detection interpretation for Decision Flow
