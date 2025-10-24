# Reflow Restructuring Design

## Overview
This document outlines the restructuring of the monolithic `decision_flow.json` into 5 separate, manageable workflows.

## Current State
- **decision_flow.json**: 128KB, 2,351 lines - monolithic and difficult to manage
- **Existing phases**:
  - 7 Architecture workflows (Arch-00 to Arch-06)
  - 9 Development workflows (Dev-01 to Dev-Post)
  - 5 Feature Update workflows (FU-01 to FU-05)
- **22 tools** and **36+ templates** already exist

## New Workflow Structure

### Workflow 1: Setup Workflow (`00-setup.json`)
**Purpose**: Initialize system, establish paths, configure environment

**Key Responsibilities**:
- Configure `path_root` - where the system is being developed (e.g., `/home/user/projects/my_system`)
- Configure `reflow_root` - where reflow tools are located (e.g., `/home/user/dev/reflow`)
- Configure `workflow_steps_path` - path to workflow definitions
- Set up tool paths for all reflow tools
- Create system directory structure (context/, specs/, services/, docs/)
- Initialize foundational documents (SYSTEM_MISSION_STATEMENT.md, USER_SCENARIOS.md, etc.)
- Optional: System-of-Systems decomposition (if multi-system integration)

**Maps from current workflow**:
- Entry point routing (new_concept_or_system)
- Arch-00: System-of-Systems Decomposition (optional)
- Arch-01: Setup and Context
- Language selection (extracted from Dev-01)

**Tools used**:
- `validate_reflow_setup.py`
- `validate_directory_structure.py`
- `bootstrap_development_context.py`
- `analyze_system_structure.py`

**Outputs**:
- System directory structure
- `context/working_memory.json`
- `context/step_progress_tracker.json`
- Foundational documents
- Path configuration file

---

### Workflow 2: Systems Engineering & Architecture (`01-systems_engineering.json`)
**Purpose**: Design and validate complete system architecture, create machine-readable architecture products

**Key Responsibilities**:
- System analysis and service decomposition
- Create `service_architecture.json` for each service (UAF-based)
- Validate architectural constraints and template compliance
- Reconcile logical vs deployment architecture
- Generate `system_of_systems_graph.json` using `system_of_systems_graph.py`
- Run architecture consistency checks
- Create interface registry
- Finalize all machine-readable architecture artifacts

**Maps from current workflow**:
- Arch-02: Analysis and Decomposition
- Arch-03: Constraints and Template Validation
- Arch-04: Deployment and Deep Dive
- Arch-05: Consistency and Specification Verification
- Part of Arch-06 (machine-readable artifacts only)

**Tools used**:
- `analyze_features.py`
- `validate_architecture.py`
- `system_of_systems_graph.py`
- `identify_integration_points.py`
- `validate_foundational_alignment.py`

**Outputs**:
- `specs/machine/service_arch/<service>/service_architecture_v*.json` (per service)
- `specs/machine/system_of_systems_graph.json`
- `specs/machine/interface_registry.json`
- `specs/machine/index.json`
- `specs/machine/version_manifest.json`

---

### Workflow 3: Artifacts & Visualization (`02-artifacts_visualization.json`)
**Purpose**: Create human-readable artifacts, visualizations, and documentation (conditional - only if user plans to develop)

**Key Responsibilities**:
- Ask user if they plan to develop/implement the system
- If YES, generate all development artifacts:
  - Interface Contract Documents (ICDs)
  - Mermaid-based visualizations (architecture diagrams, sequence diagrams, component diagrams)
  - Human-readable architecture documentation
  - Architecture reports and summaries
  - Deployment diagrams
  - Handoff documentation
- If NO (architecture only):
  - Generate minimal artifacts for handoff
  - Create GitHub export package

**Maps from current workflow**:
- Arch-06: Implementation Artifacts and Completion (human-readable parts)
- architecture_only_completion route
- GitHub export (D4)

**Tools used**:
- `generate_interface_contracts.py`
- `export_system_to_github.py`
- Architecture visualization generation (may need new tool)
- Mermaid diagram generation (may need new tool or template)

**Outputs**:
- `specs/human/service_arch/` - Human-readable service descriptions
- `specs/human/visualizations/` - Mermaid diagrams, PNG/SVG exports
- `specs/human/documentation/` - Architecture Decision Records, design docs
- `specs/machine/interfaces/` - Interface Contract Documents (ICDs)
- `specs/human/reports/` - Architecture summary reports
- Optional: GitHub export package

---

### Workflow 4: Development (`03-development.json`)
**Purpose**: Implement services according to architecture specifications

**Key Responsibilities**:
- Development environment bootstrap
- Core domain model implementation
- Persistence layer and data models
- API integration surfaces
- Security hardening
- Observability (metrics, logs, traces)
- Unit and integration testing
- Continuous implementation tracking

**Maps from current workflow**:
- Dev-01: Initialization & Environment Bootstrap
- Dev-02: Core & Domain Model Realization
- Dev-03: Persistence & Migration Enablement
- Dev-04: Integration Surfaces & Security Hardening
- Dev-05: Observability & Testing Pyramid (implementation parts)
- Dev-Post: Feedback Loop Initialization

**Tools used**:
- `bootstrap_development_context.py`
- `select_development_languages.py`
- `create_embedded_scripts.py`
- `verify_component_contract.py`
- `inject_workflows.py`
- `inject_tools.py`

**Outputs**:
- `services/<service_name>/src/` - Implementation code
- `services/<service_name>/tests/` - Unit and integration tests
- `services/<service_name>/docker-compose.yml` - Local deployment
- `services/build_ready_index.json` - Build tracking
- `context/dev_working_memory.json` - Development progress

**Note**: This workflow could be subdivided into smaller workflows:
- `03a-development_foundation.json` (Dev-01, Dev-02)
- `03b-development_integration.json` (Dev-03, Dev-04)
- `03c-development_quality.json` (Dev-05)

---

### Workflow 5: Testing & Operations (`04-testing_operations.json`)
**Purpose**: Validate, test, deploy, and release the system

**Key Responsibilities**:
- Development Test Execution (DTE) - unit, integration, contract tests
- CI/CD pipeline setup and automation
- Deployment validation (Docker Compose, container orchestration)
- Operational Test Execution (OTE) - end-to-end, user acceptance
- Operational readiness verification
- Runbook creation
- Release certification
- Performance benchmarking

**Maps from current workflow**:
- Dev-05: Observability & Testing Pyramid (testing parts)
- Dev-06: CI/CD & Deployment
- Dev-07: Operational Readiness & Runbooks
- Dev-08: Operational Validation & Release

**Tools used**:
- Test execution frameworks (pytest, jest, etc. - language-specific)
- `verify_component_contract.py`
- Docker Compose validation
- CI/CD automation tools

**Outputs**:
- `specs/machine/dte_artifacts.json` - Development test results
- `specs/machine/ote_artifacts.json` - Operational test results
- `services/<service>/ci/` - CI/CD configurations
- `docs/runbooks/` - Operational runbooks
- Release certification report

---

## Master Workflow Index

A new `workflows_master_index.json` will map workflow IDs to their respective files:

```json
{
  "workflows": {
    "00-setup": {
      "id": "00-setup",
      "name": "Setup Workflow",
      "file": "workflows/00-setup.json",
      "description": "Initialize system, configure paths, set up environment",
      "entry_points": ["new_system", "system_of_systems"],
      "next_workflow": "01-systems_engineering"
    },
    "01-systems_engineering": {
      "id": "01-systems_engineering",
      "name": "Systems Engineering & Architecture",
      "file": "workflows/01-systems_engineering.json",
      "description": "Design and validate architecture, create service_architecture.json products",
      "prerequisites": ["00-setup"],
      "next_workflow": "02-artifacts_visualization"
    },
    "02-artifacts_visualization": {
      "id": "02-artifacts_visualization",
      "name": "Artifacts & Visualization",
      "file": "workflows/02-artifacts_visualization.json",
      "description": "Generate human-readable documentation, Mermaid diagrams, ICDs",
      "prerequisites": ["01-systems_engineering"],
      "conditional": true,
      "next_workflow": "03-development"
    },
    "03-development": {
      "id": "03-development",
      "name": "Development Workflow",
      "file": "workflows/03-development.json",
      "description": "Implement services according to architecture",
      "prerequisites": ["02-artifacts_visualization"],
      "next_workflow": "04-testing_operations"
    },
    "04-testing_operations": {
      "id": "04-testing_operations",
      "name": "Testing & Operations",
      "file": "workflows/04-testing_operations.json",
      "description": "Test, validate, deploy, and release the system",
      "prerequisites": ["03-development"],
      "next_workflow": null
    }
  },
  "feature_update_workflow": {
    "id": "feature_update",
    "name": "Feature Update Workflow",
    "file": "workflows/feature_update.json",
    "description": "Handle changes to existing systems",
    "entry_points": ["feature_change", "service_change"]
  }
}
```

---

## Directory Structure Changes

### Current Structure
```
/home/ajs7/project/reflow/
├── decision_flow.json (128KB - MONOLITHIC)
├── architecture/ (7 files)
├── development/ (9 files)
├── feature_update/ (5 files)
└── ...
```

### New Structure
```
/home/ajs7/project/reflow/
├── workflows_master_index.json (NEW - workflow routing)
├── workflows/ (NEW - consolidated workflows)
│   ├── 00-setup.json
│   ├── 01-systems_engineering.json
│   ├── 02-artifacts_visualization.json
│   ├── 03-development.json
│   ├── 04-testing_operations.json
│   └── feature_update.json
├── workflow_steps/ (RENAMED from architecture/, development/, feature_update/)
│   ├── setup/
│   │   ├── S-01-PathConfiguration.json
│   │   ├── S-02-DirectoryStructure.json
│   │   ├── S-03-FoundationalDocuments.json
│   │   └── S-04-SystemOfSystems.json (optional)
│   ├── systems_engineering/
│   │   ├── SE-01-AnalysisAndDecomposition.json
│   │   ├── SE-02-ServiceArchitecture.json
│   │   ├── SE-03-ConstraintsValidation.json
│   │   ├── SE-04-DeploymentArchitecture.json
│   │   ├── SE-05-ConsistencyVerification.json
│   │   └── SE-06-GraphGeneration.json
│   ├── artifacts_visualization/
│   │   ├── AV-01-InterfaceContracts.json
│   │   ├── AV-02-MermaidDiagrams.json
│   │   ├── AV-03-Documentation.json
│   │   └── AV-04-Reports.json
│   ├── development/
│   │   ├── D-01-InitBootstrap.json
│   │   ├── D-02-CoreAndDomain.json
│   │   ├── D-03-Persistence.json
│   │   ├── D-04-IntegrationAndSecurity.json
│   │   ├── D-05-ObservabilityAndTesting.json
│   │   └── D-Post-Feedback.json
│   └── testing_operations/
│       ├── TO-01-DevelopmentTesting.json
│       ├── TO-02-CICDSetup.json
│       ├── TO-03-DeploymentValidation.json
│       ├── TO-04-OperationalReadiness.json
│       └── TO-05-OperationalTesting.json
├── tools/ (unchanged - 22 tools)
├── templates/ (unchanged - 36+ templates)
├── definitions/ (unchanged)
├── instructions/ (unchanged)
└── workflow_driver.py (UPDATED - support new workflow structure)
```

---

## Workflow Driver Updates

The `workflow_driver.py` will be updated to:

1. **Load master workflow index** (`workflows_master_index.json`)
2. **Support workflow transitions** (setup → systems_engineering → artifacts → development → testing)
3. **Track current workflow** in `working_memory.json`
4. **Validate prerequisites** before advancing to next workflow
5. **Support workflow-specific commands**:
   ```bash
   workflow_driver.py <system> --workflow 00-setup
   workflow_driver.py <system> --next-workflow
   workflow_driver.py <system> --current-workflow
   workflow_driver.py <system> --list-workflows
   ```

---

## Migration Path

1. **Create new directory structure** (`workflows/`, `workflow_steps/`)
2. **Extract and restructure** decision_flow.json into 5 workflows
3. **Reorganize step files** from architecture/, development/, feature_update/ into workflow_steps/
4. **Update workflow_driver.py** to support new structure
5. **Create workflows_master_index.json**
6. **Test new workflow structure** with sample system
7. **Archive old decision_flow.json** (rename to `decision_flow.json.old`)

---

## Benefits of New Structure

1. **Modularity**: Each workflow is independent and focused
2. **Maintainability**: Easier to update individual workflows without affecting others
3. **Clarity**: Clear separation of concerns (setup, architecture, artifacts, development, testing)
4. **Flexibility**: Can skip workflows (e.g., architecture-only, no development)
5. **Scalability**: Can subdivide workflows further if needed (e.g., split development into 3a, 3b, 3c)
6. **Path awareness**: Setup workflow establishes all paths needed for tools
7. **Reusability**: Common patterns can be shared across workflows

---

## Next Steps

1. Review and approve this design
2. Implement the restructuring
3. Test with sample system
4. Update documentation
5. Migrate existing systems (if any)
