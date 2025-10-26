# Reflow Tooling Version Manifest

**Purpose**: Track changes to Reflow's tooling architecture over time

---

## Current Version: v3.5.0 (2025-10-26)

**Tool Count**: 19 (up from 16)
**Change Type**: MINOR (as-fielded architecture tracking feature)
**Status**: Active

### Tools (19 Total)

#### Core Workflow Tools (15)
1. `system_of_systems_graph_v2.py` - System graph generation with NetworkX analysis
2. `validate_architecture.py` - Architecture file validation
3. `generate_interface_contracts.py` - ICD generation
4. `bootstrap_development_context.py` - Development environment initialization
5. `verify_component_contract.py` - Contract compliance verification
6. `generate_as_built_architecture.py` - Reverse-engineer architecture from code (NEW in v3.5.0)
7. `generate_as_fielded_architecture.py` - Capture architecture from deployed system (NEW in v3.5.0)
8. `compare_architectures.py` - Compare architecture graphs and generate delta reports (NEW in v3.5.0)
9. `validate_directory_structure.py` - Directory structure validation
10. `validate_port_registry.py` - Port conflict detection (UAF/IT systems)
11. `validate_foundational_alignment.py` - Foundational document alignment
12. `validate_workflow_files.py` - Workflow JSON validation (v3.3.1)
13. `analyze_features.py` - Feature analysis and service identification
14. `select_development_languages.py` - Language selection for services
15. `identify_integration_points.py` - System-of-systems integration points

#### Optional/Advanced Tools (3)
16. `generate_rag_embeddings.py` - RAG context management (optional)
17. `rag_agent_wrapper.py` - RAG-enhanced LLM queries (optional)
18. `export_system_to_github.py` - Architecture-only export (optional)

#### Standalone Tools (1)
19. `reflow_mcp_server.py` - Model Context Protocol server (standalone utility)

### Changes from v3.3.1

**Additions (3 new tools)**:
- `generate_as_built_architecture.py` - Reverse-engineer architecture from implemented code (AST parsing + dependency analysis)
- `generate_as_fielded_architecture.py` - Capture architecture from deployed/running system (Docker inspection + docker-compose analysis)
- `compare_architectures.py` - Compare two architecture graphs, generate delta reports with similarity scores and change classification

**Workflow Updates (2 workflows)**:
- `workflows/03-development.json` - Added step D-06 (As-Built Architecture Generation)
- `workflows/04-testing_operations.json` - Added step TO-06 (As-Fielded Architecture Capture)

**Template Additions**:
- `templates/architecture_delta_report_template.json` - Template for delta report output

**Feature**: As-Fielded Architecture Tracking
- Track architecture lifecycle: designed → built → fielded
- Compare implementations against design to identify drift
- Generate delta reports with similarity scores (Jaccard similarity)
- Classify changes as breaking vs non-breaking
- Document rationale for architectural deviations
- Feed operational insights back into design phase

**Addresses**: GitHub Issue #6 (Architecture Lifecycle Tracking)

**Breaking Changes**: NONE
**Migration Required**: NO (feature is additive)

---

## Previous Version: v3.3.1 (2025-10-25)

**Tool Count**: 16
**Change Type**: PATCH (tool cleanup, non-breaking)
**Status**: Superseded

### Changes from v3.3.0

**Deletions (8 tools)**:
- `tools/inject_tools.py` - Injection system (deprecated)
- `tools/inject_workflows.py` - Injection system (deprecated)
- `tools/create_embedded_scripts.py` - Injection system (deprecated)
- `tools/execute_injection_flow.py` - Injection system (deprecated)
- `tools/validate_injection_readiness.py` - Injection system (deprecated)
- `tools/system_of_systems_graph.py` - Legacy v1 (replaced by v2)
- `tools/retrieve_rag_context.py` - Redundant with rag_agent_wrapper.py
- `tools/analyze_system_structure.py` - Unclear purpose, not referenced

**Updates (3 workflows)**:
- `workflows/00-setup.json` - 1 reference updated (v1→v2 graph tool)
- `workflows/01-systems_engineering.json` - 18 references updated (v1→v2 graph tool)
- `workflows/feature_update.json` - 3 references updated (v1→v2 graph tool)

**Additions**:
- `docs/TOOL_USAGE_SUMMARY.md` - Comprehensive tool documentation (1100+ lines)
- `tools/validate_workflow_files.py` - Created during meta-analysis (v3.3.1)

**Rationale**: Reduce tool proliferation (33% reduction), improve clarity, eliminate deprecated code

**Breaking Changes**: NONE
**Migration Required**: NO

---

## Previous Version: v3.3.0 (2025-10-24)

**Tool Count**: 24
**Change Type**: MINOR (operational environment design added)
**Status**: Superseded

### Tools (24 Total)
- All 16 current tools
- Plus 8 deleted tools (injection system, legacy v1, redundant tools)

### Changes from v3.2.0
- Added operational environment design templates
- Enhanced IT system requirements (security, deployment, UX)
- Framework-agnostic improvements

---

## Version History Summary

| Version | Date | Tools | Change Type | Key Changes |
|---------|------|-------|-------------|-------------|
| v3.5.0 | 2025-10-26 | 19 | MINOR | As-fielded architecture tracking (+3 tools, D-06, TO-06) |
| v3.3.1 | 2025-10-25 | 16 | PATCH | Tool cleanup (-8 tools), v1→v2 updates |
| v3.3.0 | 2025-10-24 | 24 | MINOR | Operational environment design |
| v3.2.0 | 2025-10-23 | 24 | MINOR | Port management, git automation |
| v3.1.0 | 2025-10-20 | 24 | MINOR | Multi-framework support (6 frameworks) |
| v3.0.0 | 2025-10-15 | 23 | MAJOR | Modular workflow structure (6 workflows) |

---

## Tool Categories Over Time

| Category | v3.0.0 | v3.3.0 | v3.3.1 | v3.5.0 | Change |
|----------|--------|--------|--------|--------|--------|
| Core Workflow | 12 | 12 | 12 | 15 | +3 (architecture lifecycle) |
| Validation | 4 | 4 | 4 | 4 | No change |
| Optional/Advanced | 3 | 3 | 3 | 3 | No change |
| Standalone | 1 | 1 | 1 | 1 | No change |
| Deprecated | 3 | 4 | 0 | 0 | Deleted |
| **Total** | **23** | **24** | **16** | **19** | **+3 from v3.3.1** |

---

## Validation Results (v3.3.1)

### Workflow Validation
```bash
python3 /home/user/reflow/tools/validate_workflow_files.py /home/user/reflow/workflows/

Result: PASSED
- 6 workflows validated
- 0 errors
- 17 warnings (external tools - expected)
```

### Foundational Alignment
```bash
python3 /home/user/reflow/tools/validate_foundational_alignment.py /home/user/reflow \
  --change-proposal docs/changes/CHANGE_PROPOSAL_20251025_tool_cleanup.md

Result: PASSED
- Mission alignment: PASS
- Overall status: PASS
- Blocking issues: 0
```

---

## Next Version Planning

### v3.4.0 (Potential - MINOR)
**Proposed Changes**:
- Enhanced system_of_systems_graph_v2.py with knowledge gap visualization
- Template improvements based on meta-analysis findings
- JSON schema validation integration in all tools

**Rationale**: New capabilities (knowledge gap viz, schema integration)
**Type**: MINOR (new features, backward compatible)

### v4.0.0 (Future - MAJOR)
**Proposed Changes**:
- Potential workflow structure changes
- Breaking changes to tool interfaces
- New quality gates

**Rationale**: Breaking changes requiring migration
**Type**: MAJOR

---

## Deprecation Policy

**Deprecated tools retained for**: 1 minor version
**Deletion timeline**: Next major version

**Example**:
- v3.3.0: Mark injection system tools as deprecated
- v3.3.1: Delete deprecated tools (this version)
- v4.0.0: Major changes, clean slate

---

## Tool Documentation

**Primary Reference**: `/home/user/reflow/docs/TOOL_USAGE_SUMMARY.md`

**Updated**: 2025-10-25
**Completeness**: Comprehensive (all 16 tools documented)
**Format**: Markdown with usage examples, workflow integration, best practices

---

## Maintenance Notes

**Last Tool Audit**: 2025-10-25 (meta-analysis)
**Tools Added Since Audit**: 0
**Tools Deleted Since Audit**: 8
**Workflows Updated**: 3 (v1→v2 references)

**Next Audit Recommended**: When adding/deprecating tools or at major version increments
