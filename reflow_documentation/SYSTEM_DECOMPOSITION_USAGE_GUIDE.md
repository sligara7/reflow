# System-of-Systems Decomposition Workflow Usage Guide

## Overview

The System-of-Systems Decomposition workflow (Arch-00) has been added as an optional phase before the standard architecture workflow. This workflow is designed to handle scenarios where you need to integrate multiple existing systems and want to understand:

1. The internal structure of each system
2. How systems should interface with each other
3. What modifications are needed in each system for integration
4. A unified view of the integrated system architecture

## When to Use the Decompose Workflow

### Primary Use Cases

1. **System-of-Systems Integration**: You have multiple independent systems (e.g., Python packages, microservices, applications) that need to work together as an integrated solution.

2. **Brownfield Development**: Adding new capabilities to an existing ecosystem of systems.

3. **Migration Projects**: Moving from multiple disparate systems to a unified architecture.

4. **Interface Discovery**: Understanding what interfaces need to be created or modified between existing systems.

### Example Scenario (Python Packages Integration)

You have:
- 3 Python packages deployed as individual services
- A new Python package that needs to integrate with the existing ones
- A high-level document describing how everything should work together
- Need to determine what changes are required in each package

## Workflow Entry Point

To use the decompose workflow, when starting a new concept/system in the decision flow:

1. Choose **"new_concept_or_system"** entry point
2. Select **"with_system_decomposition"** option
3. This routes you to `architecture/Arch-00-SystemDecomposition.json`

## Decompose Workflow Steps

### Step 1: Capture Integration Requirements
- **Input**: High-level integration requirements document
- **Output**: `context/integration_requirements.json`
- **Purpose**: Document what the integrated system should accomplish

### Step 2: Enumerate Target Systems  
- **Input**: System inventory, access information
- **Output**: `context/target_systems_inventory.json`
- **Purpose**: List all systems that need integration

### Step 3: System Structure Analysis (per system)
- **Input**: System codebase/documentation
- **Output**: `specs/machine/decomposition/<system_id>/system_structure.json`
- **Purpose**: Analyze internal structure of each system

For Python packages, this means:
- **System Level**: The entire Python package
- **Subsystem Level**: Major modules or functional groups
- **Component Level**: Individual classes, functions, or scripts

### Step 4: Cross-System Interface Analysis
- **Input**: Integration requirements + all system structures
- **Output**: `specs/machine/integration_analysis.json`
- **Purpose**: Identify where interfaces are needed between systems

### Step 5: Integration Impact Assessment
- **Input**: Integration analysis + system structures
- **Output**: `specs/machine/integration_impact_assessment.json`
- **Purpose**: Assess what changes are needed in each system

### Step 6: Generate Unified System Architecture
- **Input**: All previous artifacts
- **Output**: `specs/machine/unified_system_architecture.json`
- **Purpose**: Create integrated view for standard architecture workflow

## Generic System Analysis Approach

The workflow is designed to be system-agnostic. For any type of system:

### Analysis Levels
- **System Level**: The entire system being analyzed
- **Subsystem Level**: Major functional groups within the system  
- **Component Level**: Individual functional units that could be integration points

### Analysis Dimensions
- Functional responsibilities
- Data inputs and outputs
- External interaction points
- Internal communication mechanisms
- Resource dependencies
- Operational characteristics

## Templates and Artifacts

### New Templates Added
1. **`integration_requirements_template.json`**: Captures high-level integration goals
2. **`system_decomposition_template.json`**: Analyzes individual system structure
3. **`component_analysis_template.json`**: Detailed component analysis (optional)

### Key Artifacts Created
- Integration requirements and constraints
- System structure analysis for each target system
- Interface requirements between systems
- Impact assessment for each system
- Unified system architecture

## Handoff to Standard Architecture Workflow

After completing the decompose workflow:

1. **Context Prepared**: Working memory updated with decomposed system structures
2. **Integration Requirements**: Clear understanding of needed interfaces
3. **Impact Assessment**: Knowledge of required changes per system
4. **Unified Architecture**: Input ready for Arch-01 (Setup and Context)

The workflow then continues with the standard architecture process (Arch-01 through Arch-06), but now with a comprehensive understanding of the existing systems and integration requirements.

## Benefits of Using the Decompose Workflow

1. **Systematic Analysis**: Ensures all systems are thoroughly understood before integration
2. **Interface Discovery**: Identifies exactly what interfaces need to be created/modified
3. **Impact Assessment**: Provides clear picture of required changes per system
4. **Risk Mitigation**: Reduces integration risks through thorough upfront analysis
5. **Documentation**: Creates comprehensive documentation of system structures
6. **Unified View**: Provides single architectural view across all systems

## Example Decision Path

```
D0: Is this a new concept/system or change to existing?
→ "new" (new integrated system)

Entry Point: new_concept_or_system
→ Choose "with_system_decomposition"

Route: architecture/Arch-00-SystemDecomposition.json
→ Complete 6 steps of decomposition analysis

Handoff: architecture/Arch-01-SetupAndContext.json
→ Continue with standard architecture workflow
```

This approach ensures that system-of-systems integration projects have a solid foundation of understanding before moving into detailed architecture design.