# Tool Capability Test: Flow Analysis - No Edge Weights

## Test Category
**Tool Capabilities - system_of_systems_graph_v2.py**

## Framework
**UAF (Unified Architecture Framework)**

## Analysis Flags Tested
- `--flow`: Flow analysis (should be skipped with warning)
- `--centrality`: Centrality analysis (should succeed)
- `--detect-gaps`: Knowledge gap detection (should succeed)

## Purpose
Validate that the tool **gracefully handles missing edge weights** instead of crashing. Flow analysis REQUIRES edge weights, but the tool should:
1. ✅ Detect edge weights are missing
2. ✅ Issue a WARNING (not an error)
3. ✅ Skip flow analysis
4. ✅ Continue with other analyses (centrality, gaps, etc.)
5. ✅ Exit with code 0 (success)

## Scenario

**System**: Simple UAF microservices architecture

**Services**:
- **API Gateway**: Routes external requests to backend services
- **Service A**: User management (port 8001)
- **Service B**: Product catalog (port 8002)

**Dependencies**:
- API Gateway → Service A (NO edge_weight defined)
- API Gateway → Service B (NO edge_weight defined)

**Missing**: `edge_weight` field in all dependencies

## Expected Behavior

**When --flow flag is used WITHOUT edge weights**:

1. ✅ Tool detects missing edge weights
2. ✅ Issues WARNING message:
   ```
   WARNING: Flow analysis requires edge weights
   Edge weights not found in dependencies
   Skipping flow analysis
   Add edge_weight field to service_architecture.json dependencies
   ```
3. ✅ Skips flow analysis section
4. ✅ Continues with other analyses:
   - Centrality analysis (doesn't need weights)
   - Knowledge gap detection (doesn't need weights)
   - Interface validation (doesn't need weights)
5. ✅ Exits successfully (code 0)

## What Should NOT Happen

❌ **Tool crashes** with exception
❌ **Exits with error code** (non-zero)
❌ **Generates traceback**
❌ **Stops all analyses** (should only skip flow)
❌ **Silent failure** (must warn user)

## Graceful Degradation

**Philosophy**: Missing optional data should warn, not crash. Tool should do as much as possible with available data.

**Categorization**:
- **REQUIRED for all**: Service IDs, interfaces, framework
- **REQUIRED for flow analysis**: Edge weights
- **OPTIONAL**: Deployment config, version info

**Graceful Handling**:
```
if edge_weights_missing and flow_analysis_requested:
    print("WARNING: Flow analysis requires edge weights")
    print("Add edge_weight to dependencies in architectures")
    skip_flow_analysis()
    continue_with_other_analyses()
else:
    perform_flow_analysis()
```

## Pass Criteria

1. ✅ Tool executes without crash
2. ✅ Exit code = 0 (success)
3. ✅ WARNING message appears in output
4. ✅ Flow analysis section NOT in output
5. ✅ Centrality analysis section DOES appear
6. ✅ Knowledge gaps section DOES appear
7. ✅ No exceptions, tracebacks, or errors

## Comparison

**This Test (NO weights)**: Graceful warning, skip flow analysis, continue others

**Companion Test (WITH weights)**: `flow_analysis_with_weights/` - Flow analysis succeeds with comprehensive metrics

## Why This Matters

**Robustness**:
- Real-world architectures may be incomplete
- Early-stage designs may not have edge weights yet
- Tool should provide partial value, not fail completely

**User Experience**:
- Clear warning tells user what's missing
- Guidance on how to fix (add edge_weight field)
- Other valuable analyses still available

**Progressive Enhancement**:
- Start with basic architecture (no weights) → get centrality, gaps
- Add edge weights later → unlock flow analysis
- Don't block early-stage work on complete data

## Edge Weight Examples

If user wants to enable flow analysis, add to dependencies:

**UAF (request-based)**:
```json
"edge_weight": {
  "metric": "request_rate",
  "value": 100,
  "unit": "requests_per_second"
}
```

**Decision Flow (probability-based)**:
```json
"edge_weight": {
  "metric": "transition_probability",
  "value": 0.8,
  "unit": "probability"
}
```

## Test Architecture

**Files**:
- 3 service architectures (API GW, Service A, Service B)
- service_arch_index.json
- expected_output.json (pass criteria)
- README.md (this file)

**Total Lines**: ~90 (architectures) + test framework

## Execution

```bash
cd /home/user/reflow/tests/fixtures/tool_capabilities/system_of_systems_graph/flow_analysis_no_weights

# This should WARN but NOT crash
python3 /home/user/reflow/tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --flow --centrality --detect-gaps \
  --output specs/machine/graphs/output.json

echo "Exit code: $?"  # Should be 0

# Validate against expected_output.json
grep -i "warning" specs/machine/graphs/output.json
grep -i "edge.*weight" specs/machine/graphs/output.json
```

## Related Tests

- `flow_analysis_with_weights/` - Same scenario WITH edge weights (flow succeeds)
- `bottleneck_detection/` - Centrality analysis (no weights needed)
