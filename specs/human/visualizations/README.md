# Reflow System Visualizations

This directory contains Mermaid-based visualizations of the Reflow workflow system, generated from the meta-analysis architecture files.

**Framework Used**: Decision Flow Framework (workflows modeled as state machines with conditional transitions)

**Generated**: 2025-10-26

---

## Available Diagrams

### 1. System Architecture (`reflow_system_architecture.mmd`)

**Purpose**: High-level overview of all Reflow workflow steps and their relationships

**Shows**:
- All 6 workflows (00-setup through 04-testing_operations)
- Key workflow steps within each workflow
- Transitions between steps (sequential and conditional)
- Critical data artifacts (working_memory.json, system_decomposition.json, etc.)
- Rework loops (e.g., SE-03 validation fail → back to SE-02)

**Use this to**:
- Understand the complete Reflow workflow system
- See how workflows connect and transition
- Identify critical artifacts produced at each stage

**Color Coding**:
- Blue: Setup workflow
- Purple: Systems Engineering workflow
- Green: Artifacts & Visualization workflow
- Orange: Development workflow
- Pink: Testing & Operations workflow
- Yellow (dashed): Data artifacts

---

### 2. Workflow Sequence (`reflow_workflow_sequence.mmd`)

**Purpose**: High-level view of the 6 main workflows and decision points

**Shows**:
- The 6 workflows in sequence
- Duration estimates for each workflow
- Key outputs from each workflow
- Quality gates (blocking validation points)
- Architecture-only vs. full development paths
- Feature update workflow (for existing systems)
- Supported frameworks (UAF, Decision Flow, Biology, Social, Ecological, CAS)

**Use this to**:
- Plan project timeline
- Understand decision points (architecture-only vs. full development)
- See quality gates that must pass
- Choose the right path for your project

**Quality Gates**:
- S-01A-QG: Framework Selection Confirmation (BLOCKING)
- SE-03-QG: Architecture Validation (BLOCKING)
- D-03-QG: Test Coverage ≥80% (BLOCKING)
- TO-03-QG: Operational Testing (BLOCKING)

---

### 3. Data Flow Diagram (`reflow_data_flow.mmd`)

**Purpose**: Shows how artifacts flow through the entire Reflow system

**Shows**:
- User inputs (requirements, paths, framework selection)
- Context & configuration artifacts
- Machine-readable architecture artifacts
- Human-readable documentation
- Development artifacts (code, CI/CD, deployment)
- Feedback loops and rework paths
- Quality gates in the data flow
- Versioning strategy (semantic version + date stamps)

**Use this to**:
- Understand what artifacts are produced when
- See dependencies between artifacts
- Identify feedback loops where rework occurs
- Plan artifact versioning and management

**Key Insight**: Architecture artifacts are versioned (v1.0.0-YYYYMMDD) and human docs match those versions

---

### 4. Framework Selection Flow (`S-01A_framework_selection_flow.mmd`)

**Purpose**: Detailed view of the S-01A framework selection process (LESSON-01 implementation)

**Shows**:
- 9 actions in S-01A step
- Semantic matching questionnaire (6 questions)
- Evaluation of ALL frameworks (not just one)
- NetworkX analysis mapping
- Objective scoring rubric (5 criteria with weights)
- User confirmation requirement (BLOCKING)
- Custom framework research path
- S-01A-QG quality gate with 5 validation checks

**Use this to**:
- Understand how to select the right framework
- See the semantic matching process
- Learn the objective scoring criteria
- Understand why user confirmation is required

**Critical**: This is the most important architectural decision. Wrong framework = wrong insights. The 10-15 minute investment here saves hours of rework later.

**Scoring Criteria**:
1. Domain Match (weight 2.0)
2. **Semantic Match (weight 2.5) - HIGHEST** - Match abstractions, not just domain
3. Analysis Match (weight 2.0) - Which NetworkX analyses are enabled?
4. Edge Weight Feasibility (weight 1.5) - Can you add weights for flow analysis?
5. Complexity (weight 1.0) - Simpler is better

---

### 5. SE-02 Component View (`SE-02_service_architecture_components.mmd`)

**Purpose**: Detailed component-level view of the SE-02 (Service Architecture) step

**Shows**:
- Input interfaces (system_decomposition.json, templates, working_memory)
- 6 internal components with their responsibilities
- Output artifacts (service_architecture files, interface_registry)
- Consuming steps (SE-06, AV-01)
- Validation feedback loop

**Use this to**:
- Understand how SE-02 internally works
- See which components are responsible for what
- Learn the inputs and outputs
- Understand the validation process

**Components**:
- **TemplateLoader**: Loads framework-specific templates
- **InterfaceDesigner**: Designs consumed/produced interfaces
- **ComponentModeler**: Defines internal components
- **ArchitectureGenerator**: Generates versioned architecture files
- **InterfaceRegistrar**: Builds centralized interface registry
- **ArchitectureValidator**: Validates architecture completeness

---

## Viewing the Diagrams

### Option 1: Mermaid Live Editor (Easiest)

1. Go to https://mermaid.live
2. Copy the contents of any `.mmd` file
3. Paste into the editor
4. View the rendered diagram
5. Export as PNG/SVG if needed

### Option 2: VS Code with Mermaid Extension

1. Install "Mermaid Preview" extension
2. Open any `.mmd` file
3. Right-click → "Preview Mermaid"

### Option 3: GitHub (if files are in GitHub repo)

GitHub automatically renders `.mmd` files as diagrams when viewing them.

### Option 4: Command Line Rendering

```bash
# Install mermaid-cli
npm install -g @mermaid-js/mermaid-cli

# Render to PNG
mmdc -i reflow_system_architecture.mmd -o reflow_system_architecture.png

# Render to SVG
mmdc -i reflow_system_architecture.mmd -o reflow_system_architecture.svg
```

---

## Diagram Generation Process

These diagrams were generated by:
1. Reading Reflow architecture files from `specs/machine/service_arch/`
2. Analyzing index.json for component relationships
3. Extracting interface dependencies and data flows
4. Manually creating Mermaid syntax based on architecture data
5. Following the 02-artifacts_visualization workflow (AV-02 step)

**Source Architecture Framework**: Initially UAF 1.2 (wrong choice), migrated to Decision Flow Framework
**Migration Tool Used**: `tools/migrate_framework.py` (LESSON-08 implementation)

---

## Related Documentation

- **Architecture Files**: `specs/machine/service_arch/*/service_architecture_v*.json`
- **System Graph**: `specs/machine/graphs/system_of_systems_graph.json`
- **Interface Registry**: `specs/machine/interfaces/interface_registry.json`
- **Working Memory**: `context/working_memory.json`
- **Workflow Definitions**: `workflows/*.json`

---

## Lessons Learned Integration

These visualizations incorporate insights from the 8 lessons learned from Reflow meta-analysis:

- **LESSON-01**: S-01A framework selection flow shows explicit analysis process
- **LESSON-02**: Diagrams reference NetworkX Analysis Guide for framework-specific analyses
- **LESSON-04**: Framework selection flow shows semantic matching questionnaire
- **LESSON-05**: User confirmation explicitly shown as BLOCKING gate
- **LESSON-06**: Objective scoring rubric visualized in framework selection flow
- **LESSON-07**: Warnings about "don't default to UAF" reflected in multi-framework support
- **LESSON-08**: Migration tool used to convert original UAF architecture to Decision Flow

---

**Last Updated**: 2025-10-26
**Reflow Version**: v3.4.0
**Generated by**: Reflow meta-analysis (Reflow analyzing itself)
