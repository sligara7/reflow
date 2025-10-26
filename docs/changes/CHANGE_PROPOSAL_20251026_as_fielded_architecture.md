# Change Proposal: As-Fielded Architecture Tracking

**Proposal ID**: CP-2025-10-26-001
**Date**: 2025-10-26
**Author**: User Request
**Status**: Proposed
**Priority**: HIGH
**Complexity**: MEDIUM

## Executive Summary

Track the difference between "as-designed" architecture (from systems engineering phase) and "as-fielded" architecture (from actual operational deployment). This addresses a critical systems engineering gap: the designed architecture inevitably differs from what gets deployed in production due to development and operational realities.

## Problem Statement

Currently, Reflow generates a `system_of_systems_graph.json` at the end of the systems engineering phase (workflow 01). This represents the "as-designed" or "idealized" architecture. However:

1. **Development changes**: During implementation (workflow 03), developers may make architectural adjustments due to technical constraints, discovered issues, or better solutions
2. **Operational changes**: During testing/operations (workflow 04), operational requirements may necessitate architecture modifications
3. **No comparison mechanism**: There's no way to compare the designed vs fielded architecture to understand:
   - How close the final system is to the original design
   - What architectural deltas occurred
   - Why deviations happened
   - Whether deviations should be incorporated back into the design

## Proposed Solution

### Core Concept

Introduce a three-tier architecture versioning system:

1. **As-Designed Architecture** (`system_of_systems_graph.json`)
   - Created at end of systems engineering (SE-06)
   - Represents the validated, idealized architecture
   - Located: `specs/machine/graphs/system_of_systems_graph.json`

2. **As-Built Architecture** (`system_of_systems_graph_as_built.json`)
   - Created after development (workflow 03 completion)
   - Represents architecture as actually implemented
   - Includes implementation-driven changes
   - Located: `specs/machine/graphs/system_of_systems_graph_as_built.json`

3. **As-Fielded Architecture** (`system_of_systems_graph_as_fielded.json`)
   - Created after operational testing (workflow 04 completion - TO-06)
   - Represents architecture as actually deployed in operational environment
   - Includes operational-driven changes
   - Located: `specs/machine/graphs/system_of_systems_graph_as_fielded.json`

### Delta Analysis

Create a comparison tool: `tools/compare_architectures.py`

**Functionality**:
- Compare two architecture graphs (designed vs built, designed vs fielded, built vs fielded)
- Generate delta report showing:
  - Added/removed services/components
  - Added/removed interfaces
  - Modified interfaces (changes to endpoints, protocols, data models)
  - Changed dependencies
  - Changed deployment characteristics
  - Similarity score (0-100%)

**Output**: `specs/machine/graphs/architecture_delta_report_{from}_{to}_{date}.json`

### Workflow Integration

**Workflow 03 (Development) - New Step D-06**:
- **After**: All services implemented and validated
- **Action**: Generate as-built architecture
- **Tool**: `python3 tools/generate_as_built_architecture.py`
- **Process**: Scan actual implemented code, reverse-engineer architecture, compare to as-designed

**Workflow 04 (Testing & Operations) - Enhanced Step TO-06**:
- **After**: Operational testing complete
- **Action**: Generate as-fielded architecture
- **Tool**: `python3 tools/generate_as_fielded_architecture.py`
- **Process**: Inspect deployed system, capture actual runtime architecture, compare to as-designed and as-built

**Both new steps include**:
- Delta report generation (compared to as-designed)
- Similarity score calculation
- Rationale capture (why deviations occurred)
- Recommendation: Incorporate changes back into design? Or fix implementation?

## Benefits

1. **Architectural Accountability**: Know how closely implementation matches design
2. **Continuous Improvement**: Feed fielded architecture insights back to design process
3. **Change Management**: Understand when/why architecture deviates
4. **Validation**: Verify systems engineering phase produced realistic, implementable designs
5. **Documentation**: Complete architecture history (designed → built → fielded)
6. **Compliance**: Many industries require as-built documentation (defense, aerospace, medical)

## Impact Analysis

### Impacted Components

| Component | Change Type | Impact |
|-----------|-------------|--------|
| `workflows/03-development.json` | ADD STEP | Add D-06: Generate As-Built Architecture |
| `workflows/04-testing_operations.json` | ENHANCE STEP | Enhance TO-06 to generate As-Fielded Architecture |
| `tools/` | NEW TOOLS | Add 3 new tools (generate_as_built, generate_as_fielded, compare_architectures) |
| `templates/` | NEW TEMPLATE | Add architecture_delta_report_template.json |
| `docs/` | UPDATE | Update TOOL_USAGE_SUMMARY.md, workflow documentation |

### Backward Compatibility

- **Fully backward compatible**: Existing systems unaffected
- New steps are OPTIONAL (can skip if desired)
- Existing `system_of_systems_graph.json` remains unchanged
- New files are additive (as-built, as-fielded, delta reports)

### Version Increment

- **Reflow Version**: 3.4.0 → 3.5.0 (MINOR - new feature, backward compatible)
- **Workflow Version**: 03-development.json (1.0.0 → 1.1.0), 04-testing_operations.json (1.0.0 → 1.1.0)

## Implementation Plan

### Phase 1: Tool Creation
1. Create `tools/generate_as_built_architecture.py`
   - Scan `services/*/` directories for implemented code
   - Reverse-engineer interfaces from code (REST endpoints, function signatures, etc.)
   - Generate graph matching system_of_systems_graph.json format
   - Add metadata: `architecture_type: "as_built"`

2. Create `tools/generate_as_fielded_architecture.py`
   - Inspect deployment artifacts (docker-compose.yml, deployed containers)
   - Query runtime environment for actual service topology
   - Capture operational characteristics (ports, health endpoints, actual resource usage)
   - Generate graph with metadata: `architecture_type: "as_fielded"`

3. Create `tools/compare_architectures.py`
   - Load two architecture graphs
   - Compute deltas (added/removed/modified nodes and edges)
   - Calculate similarity score
   - Generate delta report

### Phase 2: Workflow Integration
1. Add step D-06 to `workflows/03-development.json`
2. Enhance step TO-06 in `workflows/04-testing_operations.json`
3. Create workflow step files:
   - `workflow_steps/development/D-06-AsBuiltArchitecture.json`
   - Update `workflow_steps/testing_operations/TO-06-ReleaseReadiness.json`

### Phase 3: Templates & Documentation
1. Create `templates/architecture_delta_report_template.json`
2. Update `docs/TOOL_USAGE_SUMMARY.md` (add 3 new tools)
3. Update README.md (mention as-fielded architecture tracking)
4. Update CLAUDE.md (document new feature)

### Phase 4: Validation
1. Test tools with example architectures
2. Validate delta calculation accuracy
3. Ensure backward compatibility
4. Update validation report

## Success Criteria

- [ ] As-built architecture generation works on implemented services
- [ ] As-fielded architecture generation works on deployed systems
- [ ] Delta comparison produces accurate reports
- [ ] Similarity score is meaningful and useful
- [ ] Workflow integration is seamless
- [ ] Documentation is complete
- [ ] Backward compatibility maintained
- [ ] All tests pass

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Reverse-engineering is inaccurate | MEDIUM | HIGH | Combine static analysis with runtime inspection; validate against contracts |
| Too much complexity | LOW | MEDIUM | Make steps OPTIONAL; provide skip guidance |
| Performance overhead | LOW | LOW | Tools run offline after completion, not during runtime |

## Alternative Approaches Considered

1. **Manual tracking**: User creates as-fielded manually
   - **Rejected**: Error-prone, inconsistent, no automation

2. **Only as-fielded (no as-built)**: Skip as-built, only track fielded
   - **Rejected**: Misses development phase insights, loses granularity

3. **Version control only**: Use git history to track changes
   - **Rejected**: Doesn't capture why changes happened or provide comparison

## Estimated Effort

- Tool creation: 12-16 hours
- Workflow integration: 4-6 hours
- Templates & documentation: 4-6 hours
- Testing & validation: 4-6 hours
- **Total**: 24-34 hours

## Approval

**Requires approval from**:
- [ ] User (feature requester)
- [ ] Reflow maintainers

**Next Steps After Approval**:
1. Proceed to FU-02: Identify impacted components (detailed analysis)
2. FU-03: Design detailed changes
3. FU-04: Implement changes
4. FU-05: Update documentation
5. FU-06: Validate and test
