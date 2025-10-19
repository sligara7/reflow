# Reflow: Stand-Alone Rigorous Architecture Workflow System

## Overview

The `/reflow` directory is a stand-alone, rigorous system architecture workflow framework that incorporates the battle-tested rigor from `architecture_workflow.json` while providing a modern, modular decision-flow approach.

## Stand-Alone Design

This directory contains all necessary components to run architecture workflows independently:

- **Tools**: All validation, analysis, and graph generation tools
- **Templates**: Complete set of JSON templates and tracking formats
- **Definitions**: UAF 1.2 architectural definitions and terminology
- **Workflows**: Modular workflow files for architecture, development, and feature updates

## Key Features

### 1. Rigorous Prerequisite Checking
- Validates all required tools, templates, and definitions before starting
- Ensures Python dependencies and system packages are installed
- Prevents workflow failures due to missing components

### 2. Automated Context Management
- System isolation to prevent cross-contamination between projects
- Automatic context refresh based on operation count and time
- Degradation signal detection and recovery
- Comprehensive progress tracking

### 3. Quality Gates and Validation
- Template validation using `validate_architecture.py`
- Graph consistency checking using `system_of_systems_graph.py`
- Interface contract generation using `generate_interface_contracts.py`
- Multi-layer validation before handoff to development

### 4. UAF 1.2 Compliance
- Based on Unified Architecture Framework version 1.2
- Standardized terminology and hierarchy levels
- Consistent implementation status tracking with justification

## Directory Structure

```
reflow/
├── tools/                          # Validation and analysis tools
│   ├── validate_architecture.py    # Template and consistency validation
│   ├── system_of_systems_graph.py  # Graph generation and issue detection
│   ├── generate_interface_contracts.py  # ICD generation
│   └── analyze_features.py         # Feature analysis
├── templates/                      # JSON templates and formats
│   ├── service_architecture_template.json
│   ├── index_template.json
│   ├── interface_registry_template.json
│   ├── working_memory_template.json
│   ├── current_focus_template.md
│   └── step_progress_tracker_template.json
├── definitions/                    # UAF definitions and terminology
│   └── architectural_definitions.json
├── architecture/                   # Architecture workflow steps
├── development/                    # Development workflow steps
├── feature_update/                # Feature update workflow steps
├── shared/                        # Shared components
└── decision_flow.json             # Main decision flow with integrated rigor
```

## Workflow Integration

### Entry Points

1. **New Concept/System**
   - Full prerequisite validation
   - Context setup and tracking file initialization
   - Routes to architecture workflow with rigor

2. **Feature/Service Change**
   - Validates existing system artifacts
   - Impact analysis on existing interfaces
   - Routes to feature update workflow

3. **Implementation from Final Specs**
   - Comprehensive validation gate checking
   - Handoff artifact verification
   - Routes to development workflow

### Quality Gates

- **Architecture Completion Gate**: Validates all architecture artifacts
- **Development Readiness Gate**: Ensures operational mission artifacts exist
- **Template Validation**: All JSON files conform to schemas
- **Graph Validation**: No critical architectural issues
- **Interface Validation**: Complete ICDs for all interfaces

## Key Improvements Over Original

### 1. Modular Design
- Workflows split into logical, reusable components
- Decision-based routing instead of linear progression
- Easier maintenance and evolution

### 2. Enhanced Validation
- Multi-tool validation pipeline
- Critical file dependency tracking
- Automated issue detection and reporting

### 3. Better Context Management
- Explicit tracking file templates
- Automated degradation detection
- Context refresh triggers

### 4. Comprehensive Handoff
- Operational mission artifacts for development
- Complete validation before handoff
- Quality assurance checkpoints

## Usage

### Prerequisites Installation
```bash
# Install Python dependencies
pip install networkx matplotlib pygraphviz

# Install system packages (Ubuntu/Debian)
sudo apt-get install graphviz graphviz-dev
```

### Basic Usage
```bash
# Start new system architecture
python3 -c "import json; print('Route to: architecture/Arch-01-SetupAndContext.json')"

# Validate existing architecture
python3 ./tools/validate_architecture.py /path/to/systems/<system_name>

# Generate system graph
python3 ./tools/system_of_systems_graph.py /path/to/systems/<system_name>/index.json --analyze-issues

# Generate interface contracts
python3 ./tools/generate_interface_contracts.py /path/to/systems/<system_name>
```

## Context Management

The workflow enforces strict context management:

1. **System Isolation**: Each system works in its own directory
2. **Progress Tracking**: Automatic tracking of steps and substeps
3. **Context Refresh**: Periodic reloading of definitions and templates
4. **Degradation Detection**: Automatic detection of context loss

## Validation Pipeline

1. **Template Validation**: Ensure all files conform to JSON schemas
2. **Graph Validation**: Detect cycles, orphaned nodes, missing interfaces
3. **Interface Validation**: Verify complete interface contracts
4. **Deployment Validation**: Reconcile logical and deployment architectures

## Handoff to Development

The workflow ensures complete handoff with:

- Technical specifications (`build_ready_index.json`)
- Operational mission artifacts (`SYSTEM_MISSION_STATEMENT.md`, etc.)
- Complete interface contracts (ICDs)
- Quality gate validation passes
- Integration test strategy

## Migration from Original

Existing systems using `architecture_workflow.json` can migrate to this system by:

1. Moving to the reflow framework
2. Using the enhanced templates and validation
3. Benefiting from modular workflow design
4. Maintaining all existing rigor and quality gates

This reflow system maintains the proven rigor of the original architecture workflow while providing enhanced modularity, validation, and context management capabilities.