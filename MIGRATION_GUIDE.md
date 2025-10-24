# Reflow Restructuring Migration Guide

## Overview

The reflow project has been restructured from a monolithic `decision_flow.json` (128KB, 2,351 lines) into **5 separate, manageable workflows**. This migration guide explains the changes and how to use the new structure.

## What Changed

### Old Structure (v2.5.0)
```
reflow/
├── decision_flow.json (MONOLITHIC - 128KB)
├── architecture/ (7 files)
├── development/ (9 files)
├── feature_update/ (5 files)
├── workflows_index.json
└── workflow_driver.py
```

### New Structure (v3.0.0)
```
reflow/
├── workflows/ (NEW - 6 workflow files)
│   ├── 00-setup.json
│   ├── 01-systems_engineering.json
│   ├── 02-artifacts_visualization.json
│   ├── 03-development.json
│   ├── 04-testing_operations.json
│   └── feature_update.json
├── workflow_steps/ (NEW - organized by workflow)
│   ├── setup/
│   ├── systems_engineering/
│   ├── artifacts_visualization/
│   ├── development/
│   ├── testing_operations/
│   └── feature_update/
├── workflows_master_index.json (NEW)
├── decision_flow.json.old (ARCHIVED)
├── architecture/ (old - kept for reference)
├── development/ (old - kept for reference)
└── feature_update/ (old - kept for reference)
```

## New Workflow Organization

### 1. Setup Workflow (`workflows/00-setup.json`)
**Purpose**: Initialize system, configure paths, set up environment

**Key Responsibilities**:
- Configure `path_root` (where system is developed)
- Configure `reflow_root` (where reflow tools are)
- Configure `workflow_steps_path`
- Create system directory structure
- Initialize foundational documents
- Optional: System-of-systems decomposition

**Entry Points**: `new_system`, `new_concept_or_system`, `system_of_systems`

**Next Workflow**: `01-systems_engineering`

---

### 2. Systems Engineering & Architecture (`workflows/01-systems_engineering.json`)
**Purpose**: Design and validate architecture, create machine-readable products

**Key Responsibilities**:
- System analysis and service decomposition
- Create `service_architecture.json` for each service (UAF 1.2)
- Validate architectural constraints
- Reconcile logical vs deployment architecture
- Generate `system_of_systems_graph.json`
- Finalize machine-readable architecture artifacts

**Prerequisites**: `00-setup`

**Next Workflow**: `02-artifacts_visualization`

---

### 3. Artifacts & Visualization (`workflows/02-artifacts_visualization.json`)
**Purpose**: Create human-readable documentation and visualizations

**Key Responsibilities**:
- Ask if user plans to develop (conditional workflow)
- Generate Interface Contract Documents (ICDs)
- Generate Mermaid diagrams (system, service, sequence, deployment)
- Create human-readable architecture documentation
- Create Architecture Decision Records (ADRs)
- Generate reports and handoff documentation

**Conditional**: Skip detailed artifacts if architecture-only

**Prerequisites**: `01-systems_engineering`

**Next Workflow**: `03-development` (or END if architecture-only)

---

### 4. Development (`workflows/03-development.json`)
**Purpose**: Implement services according to architecture

**Key Responsibilities**:
- Development environment bootstrap
- Core domain model implementation
- Persistence layer
- API integration surfaces
- Security hardening
- Observability (metrics, logs, traces)
- Comprehensive testing (80% coverage minimum)

**Prerequisites**: `02-artifacts_visualization`

**Next Workflow**: `04-testing_operations`

---

### 5. Testing & Operations (`workflows/04-testing_operations.json`)
**Purpose**: Test, validate, deploy, and release

**Key Responsibilities**:
- Development Test Execution (DTE)
- CI/CD pipeline setup
- Docker Compose validation
- Operational readiness (runbooks, monitoring)
- Operational Test Execution (OTE)
- Release certification

**Prerequisites**: `03-development`

**Next Workflow**: None (END - system production-ready)

---

### Feature Update Workflow (`workflows/feature_update.json`)
**Purpose**: Handle changes to existing systems

**Key Responsibilities**:
- Change proposal and impact analysis
- **MANDATORY**: Foundational alignment validation
- Architecture re-engineering
- Delta highlighting and approval
- Implementation and validation

**Entry Points**: `feature_or_service_change`

**Independent Workflow**: Can be entered at any time for existing systems

---

## Key Improvements

### 1. **Modularity**
- Each workflow is independent and focused
- Easier to navigate and understand
- Clear separation of concerns

### 2. **Maintainability**
- Update individual workflows without affecting others
- Easier to add new steps or modify existing ones
- Version control friendly (smaller files, clearer diffs)

### 3. **Flexibility**
- Can skip workflows (e.g., architecture-only, no development)
- Conditional execution (artifacts only if developing)
- Workflows can be subdivided further if needed

### 4. **Path Awareness**
- Setup workflow establishes all paths upfront
- Eliminates path confusion and errors
- Supports systems located anywhere on filesystem

### 5. **Better Documentation**
- Each workflow clearly documents its purpose
- Entry points and prerequisites explicit
- Quality gates well-defined
- LLM agent guidance included

---

## How to Use the New Structure

### Starting a New System

1. **Run Setup Workflow**:
   ```bash
   # Tell your LLM agent:
   "Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/my_system"
   ```

2. **The workflow will**:
   - Configure paths (reflow_root, system_root, tools_path, etc.)
   - Create directory structure
   - Initialize foundational documents
   - Store all paths in `context/working_memory.json`

3. **Progress through workflows**:
   - 00-setup → 01-systems_engineering → 02-artifacts_visualization → 03-development → 04-testing_operations

### Updating an Existing System

1. **Use Feature Update Workflow**:
   ```bash
   "Implement workflow in /path/to/reflow/workflows/feature_update.json on system in /path/to/my_system"
   ```

2. **Mandatory steps**:
   - Change proposal
   - Foundational alignment validation (MANDATORY)
   - Architecture update
   - Implementation and validation

### Architecture-Only (No Development)

1. **Run through workflows**:
   - 00-setup → 01-systems_engineering → 02-artifacts_visualization

2. **At artifacts workflow**:
   - Choose "architecture-only" option
   - Receive minimal handoff package
   - Workflow ends (skip development and testing)

---

## Workflow Driver Updates Needed

### Current Limitations

The existing `workflow_driver.py` needs updates to support the new structure:

1. **Path Handling**: Currently assumes systems in `reflow_root/systems/`
   - **Needed**: Accept system path as argument
   - **Needed**: Use paths from `workflows_master_index.json`

2. **Workflow Transitions**: Currently uses single `decision_flow.json`
   - **Needed**: Load workflow from `workflows/` directory
   - **Needed**: Track current workflow in `working_memory.json`
   - **Needed**: Support `--next-workflow` command

3. **Index File**: Currently uses `workflows_index.json`
   - **Needed**: Use `workflows_master_index.json`
   - **Needed**: Load step files from `workflow_steps/` directory

### Proposed Enhancements

```bash
# New commands needed
workflow_driver.py <system_path> --workflow 00-setup
workflow_driver.py <system_path> --next-workflow
workflow_driver.py <system_path> --current-workflow
workflow_driver.py <system_path> --list-workflows
```

### Backward Compatibility

- Old `decision_flow.json` archived as `decision_flow.json.old`
- Old `architecture/`, `development/`, `feature_update/` directories retained
- New `workflow_steps/` contains copied files (not moved)
- Can continue using old structure if needed (not recommended)

---

## Migration for Existing Systems

### If You Have Systems Using Old Structure

1. **Complete in-progress systems using old structure**:
   - Continue with `decision_flow.json.old` if needed
   - Or migrate to new structure (see below)

2. **To migrate an in-progress system**:
   - Identify current step in old structure
   - Map to equivalent step in new structure (see mapping table below)
   - Update `working_memory.json` to reference new workflow
   - Continue from mapped step

### Step Mapping Table

| Old Step ID | New Workflow | New Step ID | Notes |
|-------------|-------------|-------------|-------|
| Arch-00 | 00-setup | S-04 | System-of-systems decomposition |
| Arch-01 | 00-setup | S-01, S-02, S-03 | Setup, directory, foundational docs |
| Arch-02 | 01-systems_engineering | SE-01 | Analysis and decomposition |
| Arch-03 | 01-systems_engineering | SE-03 | Constraints validation |
| Arch-04 | 01-systems_engineering | SE-04 | Deployment architecture |
| Arch-05 | 01-systems_engineering | SE-05 | Consistency verification |
| Arch-06 (machine) | 01-systems_engineering | SE-06 | Graph generation |
| Arch-06 (human) | 02-artifacts_visualization | AV-01, AV-02, AV-03 | ICDs, diagrams, docs |
| Dev-01 | 03-development | D-01 | Init bootstrap |
| Dev-02 | 03-development | D-02 | Core and domain |
| Dev-03 | 03-development | D-03 | Persistence |
| Dev-04 | 03-development | D-04 | Integration and security |
| Dev-05 | 03-development | D-05 | Observability and testing |
| Dev-06 | 04-testing_operations | TO-02 | CI/CD setup |
| Dev-07 | 04-testing_operations | TO-04 | Operational readiness |
| Dev-08 | 04-testing_operations | TO-05 | Operational testing |
| Dev-Post | 03-development | D-Post | Feedback |
| FU-01 | feature_update | FU-01 | (unchanged) |
| FU-02 | feature_update | FU-02 | (unchanged) |
| FU-03 | feature_update | FU-03 | (unchanged) |
| FU-04 | feature_update | FU-04 | (unchanged) |
| FU-05 | feature_update | FU-05 | (unchanged) |

---

## Benefits Realized

1. **Easier to Update**: Modify one workflow without touching others
2. **Clearer Flow**: Each workflow has distinct purpose and boundaries
3. **Better Navigation**: Smaller files, easier to find specific content
4. **Version Control**: Clearer diffs, easier code review
5. **Path Management**: All paths configured upfront, no confusion
6. **Conditional Execution**: Architecture-only option clearly defined
7. **Documentation**: Each workflow self-documenting
8. **Quality Gates**: Explicitly defined in each workflow

---

## Next Steps

1. **For New Projects**: Use new workflow structure immediately
2. **For Existing Projects**: Complete with old structure or migrate
3. **Workflow Driver**: Update `workflow_driver.py` to support new structure
4. **Testing**: Validate new structure with sample systems
5. **Documentation**: Update user guides and how-to documents

---

## Support

- **Old Structure**: `decision_flow.json.old` (archived, read-only)
- **New Structure**: `workflows/*.json` (active, recommended)
- **Questions**: See `RESTRUCTURING_DESIGN.md` for detailed design rationale

---

## Version History

- **v2.5.0 and earlier**: Monolithic `decision_flow.json`
- **v3.0.0 (2025-10-24)**: Restructured into 5 separate workflows

---

## Files Created in This Restructuring

- `workflows/00-setup.json`
- `workflows/01-systems_engineering.json`
- `workflows/02-artifacts_visualization.json`
- `workflows/03-development.json`
- `workflows/04-testing_operations.json`
- `workflows/feature_update.json`
- `workflows_master_index.json`
- `workflow_steps/` (entire directory structure)
- `RESTRUCTURING_DESIGN.md` (design document)
- `MIGRATION_GUIDE.md` (this document)

---

**Congratulations!** The reflow project is now more modular, maintainable, and easier to navigate.
