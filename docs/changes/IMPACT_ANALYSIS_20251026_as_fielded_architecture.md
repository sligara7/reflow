# Impact Analysis: As-Fielded Architecture Tracking

**Feature**: As-Fielded Architecture Tracking
**Analysis Date**: 2025-10-26
**Analyst**: Feature Update Workflow (FU-02)

## Component Impact Summary

| Component | Impact Level | Change Type | Breaking | Est. Effort |
|-----------|--------------|-------------|----------|-------------|
| workflows/03-development.json | MEDIUM | ADD STEP | NO | 2h |
| workflows/04-testing_operations.json | MEDIUM | ENHANCE STEP | NO | 2h |
| workflow_steps/development/ | MEDIUM | NEW FILE | NO | 4h |
| workflow_steps/testing_operations/ | LOW | MODIFY FILE | NO | 2h |
| tools/ | HIGH | 3 NEW TOOLS | NO | 16h |
| templates/ | LOW | NEW TEMPLATE | NO | 2h |
| docs/ | MEDIUM | UPDATE | NO | 6h |
| README.md | LOW | UPDATE | NO | 1h |
| CLAUDE.md | LOW | UPDATE | NO | 1h |

**Total Estimated Effort**: 36 hours

## Detailed Component Analysis

### 1. Workflows (`workflows/03-development.json`, `workflows/04-testing_operations.json`)

**Current State**:
- `03-development.json`: 6 steps (D-01 through D-06), ends at D-06 (Release Build)
- `04-testing_operations.json`: 6 steps (TO-01 through TO-06), ends at TO-06 (Release Readiness)

**Proposed Changes**:

**Option A**: Add new step D-07 (As-Built Architecture) to 03-development.json
- New step after D-06
- Generates as-built architecture
- **Issue**: Changes step numbering

**Option B** (RECOMMENDED): Enhance existing D-06 to include as-built generation
- Keep D-06 as final step of development
- Add action D-06-A07: Generate As-Built Architecture
- Less disruptive, maintains step numbering

**For 04-testing_operations.json**:
- Enhance TO-06 (Release Readiness) to add action TO-06-A08: Generate As-Fielded Architecture
- Add action TO-06-A09: Compare As-Fielded to As-Designed
- Generates as-fielded architecture and delta report

**Impact**: MEDIUM - Workflow files need updating but no breaking changes

### 2. Workflow Step Files

**New File Required**:
- None (using Option B - enhance existing steps)

**Modified Files**:
- `workflow_steps/development/D-06-ReleaseBuild.json`
  - Add action D-06-A07: Generate As-Built Architecture
  - Add outputs: `specs/machine/graphs/system_of_systems_graph_as_built.json`
  - Add outputs: `specs/machine/graphs/architecture_delta_as_built_{date}.json`

- `workflow_steps/testing_operations/TO-06-ReleaseReadiness.json`
  - Add action TO-06-A08: Generate As-Fielded Architecture
  - Add action TO-06-A09: Compare As-Fielded to As-Designed
  - Add outputs: `specs/machine/graphs/system_of_systems_graph_as_fielded.json`
  - Add outputs: `specs/machine/graphs/architecture_delta_as_fielded_{date}.json`

**Impact**: MEDIUM - Two existing step files need enhancement

### 3. Tools (`tools/`)

**New Tools Required**:

#### Tool 1: `generate_as_built_architecture.py` (v1.0.0)
**Purpose**: Reverse-engineer architecture from implemented code
**Functionality**:
- Scan `services/*/src/` directories
- Parse code to extract:
  - Service names (from directory names)
  - REST endpoints (from Flask/FastAPI route decorators)
  - Function signatures (Python functions/methods)
  - Dependencies (from requirements.txt, imports)
  - Database connections (from config files)
  - Message queues (from RabbitMQ/Kafka clients)
- Generate `system_of_systems_graph_as_built.json` in same format as designed graph
- Add metadata: `architecture_type: "as_built"`, `generation_date`, `source: "code_analysis"`

**Estimated Lines**: 600-800 lines
**Effort**: 8-12 hours

#### Tool 2: `generate_as_fielded_architecture.py` (v1.0.0)
**Purpose**: Capture architecture from deployed/running system
**Functionality**:
- Inspect deployment artifacts:
  - Parse `docker-compose.yml` for service definitions
  - Query Docker API for running containers
  - Check port mappings (actual ports in use)
  - Health endpoint status (`/health`, `/ready`)
  - Resource usage (actual vs configured)
- Runtime topology discovery:
  - Network connections (netstat/lsof)
  - Service dependencies (observed traffic patterns)
  - Database connections (active connections)
- Generate `system_of_systems_graph_as_fielded.json`
- Add metadata: `architecture_type: "as_fielded"`, `deployment_date`, `environment`, `source: "runtime_inspection"`

**Estimated Lines**: 700-900 lines
**Effort**: 10-14 hours

#### Tool 3: `compare_architectures.py` (v1.0.0)
**Purpose**: Compare two architecture graphs and generate delta report
**Functionality**:
- Load two graphs (JSON format)
- Compute node deltas:
  - Added services/components
  - Removed services/components
  - Modified properties (ports, dependencies, capabilities)
- Compute edge deltas:
  - Added interfaces/connections
  - Removed interfaces/connections
  - Modified interfaces (protocol, endpoints, data models)
- Calculate similarity score:
  - Node similarity: Jaccard similarity of node sets
  - Edge similarity: Jaccard similarity of edge sets
  - Property similarity: Field-by-field comparison
  - Overall score: Weighted average (nodes: 40%, edges: 40%, properties: 20%)
- Generate delta report (`architecture_delta_report_{from}_{to}_{date}.json`)
- Categorize changes: BREAKING (removed interfaces, incompatible changes) vs NON-BREAKING (additions, compatible changes)

**Estimated Lines**: 500-700 lines
**Effort**: 6-10 hours

**Total Tool Impact**: HIGH - 3 new production tools, 1,800-2,400 lines of code, 24-36 hours effort

### 4. Templates (`templates/`)

**New Template Required**:

#### `architecture_delta_report_template.json`
```json
{
  "delta_metadata": {
    "comparison_date": "YYYY-MM-DD",
    "from_architecture": "<file_path>",
    "to_architecture": "<file_path>",
    "from_type": "as_designed | as_built | as_fielded",
    "to_type": "as_designed | as_built | as_fielded"
  },
  "similarity_score": {
    "overall": 0.0-1.0,
    "nodes": 0.0-1.0,
    "edges": 0.0-1.0,
    "properties": 0.0-1.0
  },
  "node_deltas": {
    "added": [...],
    "removed": [...],
    "modified": [...]
  },
  "edge_deltas": {
    "added": [...],
    "removed": [...],
    "modified": [...]
  },
  "breaking_changes": [...],
  "non_breaking_changes": [...],
  "recommendations": [...]
}
```

**Estimated Lines**: 150-200 lines
**Effort**: 2-3 hours

### 5. Documentation (`docs/`)

**Files Requiring Updates**:

#### `docs/TOOL_USAGE_SUMMARY.md`
- Add 3 new tool entries (generate_as_built_architecture, generate_as_fielded_architecture, compare_architectures)
- Document usage, parameters, examples
- **Effort**: 2-3 hours

#### `docs/TOOL_VERSION_MANIFEST.md`
- Add version entries for 3 new tools
- **Effort**: 30 minutes

#### `README.md`
- Add bullet point in "What You Get" section: "As-built and as-fielded architecture tracking"
- Add bullet point in "Key Features" section: "Architecture lifecycle tracking (designed → built → fielded)"
- **Effort**: 1 hour

#### `CLAUDE.md`
- Add section "Architecture Lifecycle Tracking" explaining three-tier versioning
- Document when as-built and as-fielded graphs are generated
- **Effort**: 1 hour

**Total Documentation Impact**: MEDIUM - 4 files updated, 4.5 hours effort

### 6. System Directory Structure (`<user_system>/`)

**New Files Created by Tools** (in user systems, not Reflow repo):
- `specs/machine/graphs/system_of_systems_graph_as_built.json`
- `specs/machine/graphs/system_of_systems_graph_as_fielded.json`
- `specs/machine/graphs/architecture_delta_as_built_{date}.json`
- `specs/machine/graphs/architecture_delta_as_fielded_{date}.json`

**Impact**: LOW - Additive files, no existing files modified

## Dependency Analysis

**External Dependencies**:
- None - all new tools use standard Python libraries (json, pathlib, argparse, ast for code parsing)
- Optional: `docker` Python library for runtime inspection (can use subprocess + docker CLI)

**Internal Dependencies**:
- New tools depend on:
  - Existing `system_of_systems_graph.json` format (as reference)
  - Workflow completion signals (D-06 complete → trigger as-built, TO-06 complete → trigger as-fielded)

**Impact**: LOW - No new external dependencies required

## Backward Compatibility Analysis

**Breaking Changes**: NONE

**Compatibility Guarantees**:
- ✅ Existing workflows work unchanged (new steps are additive)
- ✅ Existing tools unaffected
- ✅ Existing templates unaffected
- ✅ Existing `system_of_systems_graph.json` format unchanged
- ✅ Users can skip new steps if desired (optional feature)
- ✅ No changes to existing APIs or interfaces

**Migration Required**: NO - Fully backward compatible

## Testing Requirements

**New Tests Needed**:
1. Tool tests for `generate_as_built_architecture.py`:
   - Test code parsing (REST endpoints, function signatures)
   - Test graph generation
   - Test metadata inclusion

2. Tool tests for `generate_as_fielded_architecture.py`:
   - Test docker-compose parsing
   - Test runtime inspection (mocked Docker API)
   - Test graph generation

3. Tool tests for `compare_architectures.py`:
   - Test delta calculation (added/removed/modified nodes/edges)
   - Test similarity score calculation
   - Test breaking change detection

4. Workflow integration tests:
   - Test D-06-A07 generates as-built graph
   - Test TO-06-A08/A09 generate as-fielded graph and delta

5. End-to-end test:
   - Run full workflow (00-setup → 04-testing_operations)
   - Verify as-designed, as-built, as-fielded graphs all generated
   - Verify delta reports created
   - Verify similarity scores reasonable

**Effort**: 8-12 hours

## Risk Assessment

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Code parsing inaccurate | MEDIUM | MEDIUM | Use AST parsing + runtime inspection; validate against ICDs |
| Runtime inspection fails | LOW | MEDIUM | Fallback to static analysis if runtime unavailable |
| Similarity score unhelpful | LOW | LOW | Iterate on formula based on user feedback |
| Tool complexity too high | LOW | MEDIUM | Provide simple mode + advanced mode; good documentation |

## Approval Checklist

- [x] Impact on all components identified
- [x] Backward compatibility confirmed
- [x] Effort estimated (36 hours total)
- [x] Testing requirements defined
- [x] Risks identified and mitigated
- [ ] User approval received

**Next Step**: Proceed to FU-03 (Design Changes) upon approval
