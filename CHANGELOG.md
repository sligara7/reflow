# Changelog

All notable changes to the Reflow workflow system will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [3.8.0] - 2025-10-28

### Added

- **Human Documentation Workflow** - Comprehensive human-readable documentation generation
  - `generate_human_documentation.py` - Convert machine specs to human-readable markdown
  - `parse_human_documentation.py` - Parse human edits back to machine specs with validation
  - `component_swap.py` - Safe component swapping with interface compatibility checking
  - Bidirectional translation: Human ↔ Machine documentation synchronization
- **PNG/SVG Rendering Support** - Mermaid diagrams can now be rendered to distributable image formats
- **Component Swap Validation** - Automated compatibility checking when replacing services
  - Interface compatibility validation
  - Protocol and data format checking
  - Automatic rollback on validation failure

### Changed

- **`02-artifacts_visualization.json`** - Human documentation now MANDATORY (removed "conditional" flag)
- **Workflow AV-02** - Added AV-02-A05 step for PNG/SVG rendering
- **Workflow AV-01** - Added AV-01-A04 step for human documentation generation

### Fixed

- **Documentation Consistency** - LLMs no longer skip human documentation steps
- **Stakeholder Review** - Stakeholders can now review PNG/SVG diagrams (not just .mmd files)
- **Architecture Editing** - Architecture changes can be proposed via markdown edits (not just JSON)

### Documentation

- Added `docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md` - Comprehensive analysis (973 lines)
- Added `docs/changes/CHANGE_PROPOSAL_2025-10-28_human_documentation.md` - Feature proposal
- Added `docs/changes/IMPLEMENTATION_GUIDE_human_documentation.md` - Implementation guide (1,257 lines)
- Added `docs/proposals/CONTEXT_FLOW_ANALYSIS_v3.9.0.md` - Future feature proposal

---

## [3.7.0] - 2025-10-27

### Added

- **Modular Workflows** - Split monolithic workflows for 60-95% context reduction
  - `00a-basic_setup.json` - Basic setup (55% context reduction if skipping 00b)
  - `00b-framework_selection.json` - Framework selection (optional, detailed analysis)
  - `01a-approach_detection.json` - Automatic approach detection (95% context reduction)
  - `01b-bottom_up_integration.json` - Bottom-up integration path
  - `01c-top_down_design.json` - Top-down design path
  - `02-artifacts_visualization.json` - Documentation and diagrams
  - `03a-development_implementation.json` - Implementation (58% context reduction)
  - `03b-development_validation.json` - Validation (43% context reduction)
  - `04a-testing.json` - Testing workflows (55% context reduction)
  - `04b-operations.json` - Operations workflows (42% context reduction)
- **Workflow Routing** - `workflows_master_index.json` with branching support
- **Context Reduction Metrics** - Documented context savings per workflow split

### Changed

- **Deprecated workflows** - `00-setup.json`, `01-systems_engineering.json`, `03-development.json`, `04-testing_operations.json` (backwards compatible)

### Documentation

- Updated `CLAUDE.md` - Modular workflow guidance
- Updated `README.md` - v3.7.0 features

---

## [3.6.1] - 2025-10-26

### Fixed

- **Path Extraction** - Fixed template field mismatch (`path_configuration` → `paths`)
- **Tool Discovery** - Enhanced CLAUDE.md with explicit path extraction instructions
- **Template Consistency** - Added missing `definitions_path` field to working_memory_template.json

### Documentation

- Added troubleshooting section: "Can't find tool X" with diagnostic steps
- Added troubleshooting section: "Downloading from GitHub with curl" anti-pattern
- Enhanced CLAUDE.md with 6 sections on path extraction requirements

---

## [3.5.0] - 2025-10-25

### Added

- **As-Fielded Architecture Tracking** - Architecture lifecycle management
  - `track_as_fielded_architecture.py` - Track deployed architecture state
  - `compare_architecture_versions.py` - Compare designed vs as-built vs as-fielded
  - `generate_architecture_delta_report.py` - Generate delta reports
- **Workflow Steps** - D-06 (development), TO-06 (operations)
- **Template** - `as_fielded_architecture_template.json`

### Documentation

- Added `docs/AS_FIELDED_ARCHITECTURE_TRACKING.md`
- Updated workflow documentation

---

## [3.4.0] - 2025-10-24

### Added

- **Decision Flow Framework** - Workflow modeling with state machines
  - Node types: process_step, decision_node, quality_gate
  - Transition probabilities for flow analysis
  - Rework loops as semantic cycles
  - Flow analysis capabilities in system_of_systems_graph_v2.py
- **Framework-Specific Test Suite** - 9 tests covering all frameworks
  - UAF, Biology, Social, Ecological, Complex Adaptive, Decision Flow
  - 49 test files created

### Documentation

- Added `docs/DECISION_FLOW_FRAMEWORK.md` - Comprehensive guide (500+ lines)
- Added `docs/NETWORKX_ANALYSIS_GUIDE.md` - Analysis guide (400+ lines)

---

## [3.3.0] - 2025-10-23

### Added

- **Framework Registry** - Centralized framework definitions
  - `definitions/framework_registry.json`
  - Support for UAF, Biology, Social, Ecological, Complex Adaptive, Decision Flow
  - Framework-specific analysis recommendations
- **Bottom-Up Integration** - Integration of existing components
  - Workflow: `01b-bottom_up_integration.json`
  - Steps: BU-01 through BU-06

---

## [3.2.0] - 2025-10-22

### Added

- **Multiple Framework Support** - 6+ architectural frameworks
  - Systems Biology
  - Social Network Analysis
  - Ecological Systems
  - Complex Adaptive Systems
  - Custom framework support
- **Framework Selection Workflow** - Step 00b with semantic matching

### Changed

- **UAF no longer default** - Framework selection based on system semantics

---

## [3.1.0] - 2025-10-21

### Added

- **NetworkX Analysis Integration** - 25+ graph algorithms
  - Centrality analysis (betweenness, closeness, eigenvector, PageRank)
  - Community detection (Louvain, Girvan-Newman)
  - Cycle detection
  - Strongly Connected Components (SCC)
  - DAG validation
  - Flow analysis (requires edge weights)
- **Knowledge Gap Detection** - 6 types
  - Orphaned interfaces
  - Missing provider nodes
  - Structural holes
  - Bridge interfaces
  - Interface mismatch
  - Dead-end services

### Changed

- **system_of_systems_graph_v2.py** - Flagship tool with comprehensive analysis

---

## [3.0.0] - 2025-10-20

### Changed

- **Major restructure** - Workflow splitting and modular design
- **File structure** - `workflows/*.json` + `workflow_steps/*/`
- **Versioning** - Semantic versioning with symlinks

### Breaking Changes

- Archived monolithic `decision_flow.json.old`
- New workflow entry points

---

## [2.x] - Historical

See `docs/archive/` for v2.x changelog.

---

## Format

- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes
- **Documentation** for documentation-only changes
