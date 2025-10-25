# Standard System Directory Structure

## Overview

Every system in the reflow workflow follows a standardized 4-folder organization to maintain consistency and clarity across all projects.

## Required 4-Folder Structure

```
systems/<system_name>/
├── context/          # LLM agent tracking and workflow guidance
├── specs/           # System engineering artifacts
├── services/        # Actual developed service implementations  
├── docs/            # Human documentation and visual artifacts
```

## Detailed Folder Breakdown

### 1. `context/` - LLM Agent Workflow Guidance
**Purpose**: Track workflow state and guide LLM agent through decision_flow.json execution

**Contents**:
- `working_memory.json` - LLM agent context tracking
- `current_focus.md` - Current workflow focus
- `step_progress_tracker.json` - Progress through workflow steps
- `process_log.md` - Detailed process execution log
- `context_checkpoint.md` - Context recovery checkpoints
- `dev_working_memory.json` - Development context state (during development phase)
- `dev_current_focus.md` - Current development focus (during development phase)
- `dev_progress_tracker.json` - Development stage tracking (during development phase)
- `dev_process_log.md` - Development process log (during development phase)
- `dev_context_checkpoint.md` - Development context snapshots (during development phase)

### 2. `specs/` - System Engineering Artifacts
**Purpose**: Store machine-readable and human-readable system engineering artifacts

**Structure**:
```
specs/
├── machine/         # Machine-readable artifacts
│   ├── index.json   # System component index
│   ├── interface_registry.json # Interface definitions registry
│   ├── system_of_systems_graph.json # System topology
│   ├── service_arch/<service_name>/service_architecture.json # Per-service architecture
│   ├── interfaces/  # Interface Contract Documents (ICDs)
│   ├── graphs/      # Machine-readable graph data
│   └── registries/  # Additional registry files
└── human/           # Human-readable artifacts
    ├── visualizations/ # Human-readable diagrams and charts
    ├── reports/     # Analysis and summary reports
    └── documentation/ # Human-oriented documentation
```

### 3. `services/` - Service Implementations
**Purpose**: Store actual developed service code and implementations

**Contents**:
- `<service_name>/` - Individual service implementation directories
- `build_ready_index.json` - Ready-for-development service index
- Service-specific code, configurations, and deployment artifacts

### 4. `docs/` - Human Documentation
**Purpose**: Store human-facing documentation and visual artifacts

**Contents**:
- `SYSTEM_MISSION_STATEMENT.md` - System purpose and goals
- `USER_SCENARIOS.md` - User interaction scenarios
- `SUCCESS_CRITERIA.md` - System success metrics
- `ARCHITECTURE_CONTEXT_SUMMARY.md` - Architecture overview
- Additional human-readable documentation files

## Directory Creation

The decision_flow.json automatically creates this structure with:
```bash
mkdir -p systems/<system_name>/{context,specs/{machine/{service_arch,interfaces,graphs,registries},human/{visualizations,reports,documentation}},services,docs}
```

## File Path References

All workflow references now use the proper folder structure:

### Context Files
- `systems/<system_name>/context/working_memory.json`
- `systems/<system_name>/context/current_focus.md`
- `systems/<system_name>/context/step_progress_tracker.json`
- `systems/<system_name>/context/process_log.md`

### Architecture Files
- `systems/<system_name>/specs/machine/index.json`
- `systems/<system_name>/specs/machine/interface_registry.json`
- `systems/<system_name>/specs/machine/service_arch/<service>/service_architecture.json`

### Documentation Files
- `systems/<system_name>/docs/SYSTEM_MISSION_STATEMENT.md`
- `systems/<system_name>/docs/USER_SCENARIOS.md`

## Benefits

1. **Consistency**: All systems follow the same structure
2. **Clarity**: Clear separation of concerns between different artifact types
3. **Organization**: Easy to find specific types of files
4. **Tool Compatibility**: Machine-readable artifacts are clearly separated from human documentation
5. **Workflow Integration**: LLM agent tracking files are isolated from system artifacts

## Migration

Existing systems with flat structure should be reorganized to follow this 4-folder pattern for consistency and better workflow support.