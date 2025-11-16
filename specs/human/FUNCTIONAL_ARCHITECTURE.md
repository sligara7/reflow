---
document_type: functional_architecture
system_name: Reflow Workflow System
version: 1.0.0
framework: Functional Flow Framework v1.0.0
last_updated: 2025-11-04
---

# Functional Architecture: Reflow Workflow System

**Version**: 1.0.0
**Framework**: Functional Flow Framework v1.0.0
**Created**: 2025-11-04
**Last Updated**: 2025-11-04

## Purpose

Define HOW Reflow achieves functional requirements through process flows, decision flows, and data flows with AI agent context consumption tracking

## Source Documents

- `specs/functional/functional_requirements.json`
- `workflows/*.json`
- `tools/*.py`

## Summary

- **Total Flows**: 8
- **Total Functions**: 55
- **Total Context Consumption**: 193,500 tokens

**Functions by Type**:
- decide: 6
- generate: 13
- iterate: 2
- process: 19
- read: 9
- validate: 6

## Functional Flows

This system implements 8 primary functional flows:

### Workflow Execution Flow (`FLOW-001`)

Core flow for executing structured workflows step-by-step

- **Entry Point**: `F-001`
- **Exit Points**: `F-007`
- **Implements Requirements**: FR-001, FR-012, FR-020
- **Estimated Context Consumption**: 15000-30000 tokens per workflow execution
- **Typical Path**: `F-001` → `F-002` → `F-003` → `F-004` → `F-005` → `F-006` → `F-007`

### Context Management Flow (`FLOW-002`)

Manages AI agent context window to prevent exhaustion

- **Entry Point**: `F-010`
- **Exit Points**: `F-014A`
- **Implements Requirements**: FR-002, FR-012
- **Estimated Context Consumption**: 5000-10000 tokens per context refresh cycle
- **Typical Path**: `F-010` → `F-011` → `F-012` → `F-013` → `F-014` → `F-014A`

*Note: Updated v3.13.0: Added F-014A to enable context-aware workflow routing*

### Architecture Generation Flow (`FLOW-003`)

Creates machine-readable architecture artifacts

- **Entry Point**: `F-020`
- **Exit Points**: `F-025`
- **Implements Requirements**: FR-004, FR-003
- **Estimated Context Consumption**: 8000-15000 tokens per architecture file
- **Typical Path**: `F-020` → `F-021` → `F-022` → `F-023` → `F-024` → `F-025`

### Graph Analysis Flow (`FLOW-004`)

Analyzes system-of-systems graphs for architectural issues

- **Entry Point**: `F-030`
- **Exit Points**: `F-036`
- **Implements Requirements**: FR-006, FR-017
- **Estimated Context Consumption**: 15000-40000 tokens for large graphs
- **Typical Path**: `F-030` → `F-031` → `F-032` → `F-033` → `F-034` → `F-035` → `F-036`

### Validation Flow (`FLOW-005`)

Validates architecture artifacts for completeness and correctness

- **Entry Point**: `F-040`
- **Exit Points**: `F-045`
- **Implements Requirements**: FR-005
- **Estimated Context Consumption**: 5000-12000 tokens per validation cycle
- **Typical Path**: `F-040` → `F-041` → `F-042` → `F-043` → `F-044` → `F-045`

### Functional Architecture Flow (`FLOW-006`)

Defines and validates functional architecture before system allocation (NEW in v2.1.0)

- **Entry Point**: `F-050`
- **Exit Points**: `F-061`
- **Implements Requirements**: FR-008, FR-009, FR-010, FR-011
- **Estimated Context Consumption**: 25000-50000 tokens for complete functional architecture with iterations
- **Typical Path**: `F-050` → `F-051` → `F-052` → `F-053` → `F-054` → `F-055` → `F-056` → `F-057` → `F-058` → `F-059` → `F-060` → `F-061`

### Documentation Generation Flow (`FLOW-007`)

Generates human-readable documentation from machine-readable architectures

- **Entry Point**: `F-070`
- **Exit Points**: `F-074`
- **Implements Requirements**: FR-007
- **Estimated Context Consumption**: 10000-20000 tokens per documentation set
- **Typical Path**: `F-070` → `F-071` → `F-072` → `F-073` → `F-074`

### Context Bottleneck Analysis Flow (`FLOW-008`)

Analyzes workflows for context consumption bottlenecks (META-ANALYSIS)

- **Entry Point**: `F-080`
- **Exit Points**: `F-085`
- **Implements Requirements**: FR-013, FR-020
- **Estimated Context Consumption**: 8000-15000 tokens per context analysis
- **Typical Path**: `F-080` → `F-081` → `F-082` → `F-083` → `F-084` → `F-085`

## Functions

This system implements 55 functions:

### Functions in Workflow Execution Flow

#### Load Workflow Definition (`F-001`)

**Type**: read  
**Description**: Read workflow JSON file from workflows/ directory

**Inputs**:
- `workflow_id`
- `reflow_root`

**Outputs**:
- `workflow_definition_object`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 2s

**Implements Requirements**: FR-001

**Error Handling**: Return error if workflow file not found or invalid JSON

#### Read Current Step Definition (`F-002`)

**Type**: read  
**Description**: Read detailed step definition from workflow

**Inputs**:
- `workflow_definition`
- `current_step_id`

**Outputs**:
- `step_definition`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 1s

**Implements Requirements**: FR-001

**Error Handling**: Return error if step not found in workflow

#### Parse Step Actions (`F-003`)

**Type**: process  
**Description**: Extract and interpret action list from step definition

**Inputs**:
- `step_definition`

**Outputs**:
- `action_list`

**Performance**:
- Context Consumption: 1000 tokens
- Execution Time: 1s

**Implements Requirements**: FR-001

**Error Handling**: Validate action structure, return errors for invalid actions

#### Execute Step Actions (`F-004`)

**Type**: process  
**Description**: Execute each action in step (call tools, generate files, etc.)

**Inputs**:
- `action_list`
- `system_context`

**Outputs**:
- `action_results`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 60s

**Implements Requirements**: FR-001

**Error Handling**: Catch execution errors, rollback if needed

*Note: Context consumption varies widely based on action type (tool calls can be high)*

#### Check Quality Gates (`F-005`)

**Type**: decide  
**Description**: Evaluate quality gate conditions for step completion

**Inputs**:
- `step_definition`
- `action_results`

**Outputs**:
- `gate_status (PASS/FAIL)`
- `blocking_issues`

**Performance**:
- Context Consumption: 1500 tokens
- Execution Time: 5s

**Implements Requirements**: FR-005

**Error Handling**: Block progression if gates fail

#### Update Workflow State (`F-006`)

**Type**: generate  
**Description**: Update working_memory.json with new state after step completion

**Inputs**:
- `current_state`
- `step_results`
- `next_step_id`

**Outputs**:
- `updated_working_memory`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 2s

**Implements Requirements**: FR-002

**Error Handling**: Backup old state before updating

#### Determine Next Step (`F-007`)

**Type**: decide  
**Description**: Use workflow routing logic to determine next step

**Inputs**:
- `workflow_definition`
- `current_step`
- `step_results`

**Outputs**:
- `next_step_id or WORKFLOW_COMPLETE`

**Performance**:
- Context Consumption: 1000 tokens
- Execution Time: 1s

**Implements Requirements**: FR-001

**Error Handling**: Handle conditional routing and dynamic paths

### Functions in Context Management Flow

#### Track Context Operations (`F-010`)

**Type**: process  
**Description**: Increment operations_since_refresh counter in working_memory

**Inputs**:
- `working_memory`

**Outputs**:
- `updated_counter`

**Performance**:
- Context Consumption: 200 tokens
- Execution Time: 0.5s

**Implements Requirements**: FR-012

**Error Handling**: Initialize counter if missing

#### Check Context Threshold (`F-011`)

**Type**: decide  
**Description**: Compare operations_since_refresh against refresh_threshold

**Inputs**:
- `operations_since_refresh`
- `refresh_threshold`

**Outputs**:
- `needs_refresh (boolean)`

**Performance**:
- Context Consumption: 100 tokens
- Execution Time: 0.1s

**Implements Requirements**: FR-012

**Error Handling**: Use default threshold if not configured

#### Execute Context Refresh (`F-012`)

**Type**: process  
**Description**: Reload critical context (workflow, step, current_focus)

**Inputs**:
- `working_memory`
- `reflow_root`
- `system_root`

**Outputs**:
- `refreshed_context`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-012

**Error Handling**: Graceful degradation if refresh fails

*Note: High context consumption - loads multiple files*

#### Reset Context Counter (`F-013`)

**Type**: process  
**Description**: Set operations_since_refresh = 0 after refresh

**Inputs**:
- `working_memory`

**Outputs**:
- `updated_working_memory`

**Performance**:
- Context Consumption: 200 tokens
- Execution Time: 0.5s

**Implements Requirements**: FR-012

**Error Handling**: Always succeed

#### Update Context Health Status (`F-014`)

**Type**: process  
**Description**: Set context_health (HEALTHY/WARNING/CRITICAL) based on analysis

**Inputs**:
- `current_context_usage`
- `degradation_signals`

**Outputs**:
- `context_health_status`

**Performance**:
- Context Consumption: 300 tokens
- Execution Time: 1s

**Implements Requirements**: FR-012

**Error Handling**: Conservative (prefer WARNING over HEALTHY if uncertain)

#### Route Based on Context Health (`F-014A`)

**Type**: decide  
**Description**: Route workflow execution based on context health status - enables context-aware workflow execution by acting on context monitoring results

**Inputs**:
- `context_health_status`

**Outputs**:
- `routing_decision`

**Performance**:
- Context Consumption: 200 tokens
- Execution Time: 0.5s

**Implements Requirements**: FR-012

**Error Handling**: Default to refresh if uncertain

### Functions in Architecture Generation Flow

#### Load Framework Configuration (`F-020`)

**Type**: read  
**Description**: Read framework definition (UAF, Decision Flow, etc.)

**Inputs**:
- `framework_id`
- `definitions_path`

**Outputs**:
- `framework_config`

**Performance**:
- Context Consumption: 1500 tokens
- Execution Time: 2s

**Implements Requirements**: FR-003

**Error Handling**: Fallback to UAF if framework not found

#### Load Architecture Template (`F-021`)

**Type**: read  
**Description**: Load JSON schema template for architecture file

**Inputs**:
- `framework_config`
- `templates_path`

**Outputs**:
- `architecture_template`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 2s

**Implements Requirements**: FR-004

**Error Handling**: Return error if template missing

#### Populate Architecture Data (`F-022`)

**Type**: generate  
**Description**: Fill template with component/service data from step inputs

**Inputs**:
- `architecture_template`
- `component_data`

**Outputs**:
- `populated_architecture`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-004

**Error Handling**: Validate required fields populated

#### Validate Architecture Schema (`F-023`)

**Type**: validate  
**Description**: Check architecture against JSON schema

**Inputs**:
- `architecture_object`
- `schema`

**Outputs**:
- `validation_result`

**Performance**:
- Context Consumption: 1500 tokens
- Execution Time: 3s

**Implements Requirements**: FR-005

**Error Handling**: Return detailed validation errors

#### Add Version Metadata (`F-024`)

**Type**: process  
**Description**: Add version, timestamp, author metadata to architecture

**Inputs**:
- `architecture_object`

**Outputs**:
- `versioned_architecture`

**Performance**:
- Context Consumption: 500 tokens
- Execution Time: 1s

**Implements Requirements**: FR-016

**Error Handling**: Use current timestamp if not provided

#### Write Architecture File (`F-025`)

**Type**: generate  
**Description**: Save architecture JSON to file system

**Inputs**:
- `architecture_object`
- `file_path`

**Outputs**:
- `file_written_confirmation`

**Performance**:
- Context Consumption: 1000 tokens
- Execution Time: 2s

**Implements Requirements**: FR-004

**Error Handling**: Create parent directories if needed, backup existing file

### Functions in Graph Analysis Flow

#### Load All Architecture Files (`F-030`)

**Type**: read  
**Description**: Read all service/component architecture files from system

**Inputs**:
- `system_root`
- `framework_config`

**Outputs**:
- `architecture_list`

**Performance**:
- Context Consumption: 15000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-006

**Error Handling**: Skip invalid files, report warnings

*Note: HIGH context consumption - loads multiple large files*

#### Build System Graph (`F-031`)

**Type**: process  
**Description**: Construct NetworkX directed graph from architecture files

**Inputs**:
- `architecture_list`
- `framework_config`

**Outputs**:
- `system_graph (NetworkX)`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 15s

**Implements Requirements**: FR-006

**Error Handling**: Handle missing interfaces, undefined connections

#### Run Graph Analysis (`F-032`)

**Type**: process  
**Description**: Execute NetworkX analysis (centrality, paths, cycles, etc.)

**Inputs**:
- `system_graph`
- `analysis_config`

**Outputs**:
- `analysis_results`

**Performance**:
- Context Consumption: 8000 tokens
- Execution Time: 20s

**Implements Requirements**: FR-006

**Error Handling**: Handle disconnected graphs, empty graphs

#### Detect Architectural Issues (`F-033`)

**Type**: process  
**Description**: Identify orphans, missing interfaces, cycles, disconnected components

**Inputs**:
- `system_graph`
- `analysis_results`

**Outputs**:
- `issues_list`

**Performance**:
- Context Consumption: 4000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-017

**Error Handling**: Categorize issues by severity (critical, warning, info)

#### Format Analysis Report (`F-034`)

**Type**: generate  
**Description**: Create human-readable report from analysis results

**Inputs**:
- `analysis_results`
- `issues_list`

**Outputs**:
- `report_text`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 5s

**Implements Requirements**: FR-006

**Error Handling**: Always generate report even if no issues found

#### Export Graph Data (`F-035`)

**Type**: generate  
**Description**: Export graph as node_link_data JSON

**Inputs**:
- `system_graph`

**Outputs**:
- `graph_json`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 5s

**Implements Requirements**: FR-006

**Error Handling**: Handle large graphs (streaming if needed)

#### Write Graph and Analysis Files (`F-036`)

**Type**: generate  
**Description**: Save graph JSON and analysis report to files

**Inputs**:
- `graph_json`
- `report_text`
- `output_path`

**Outputs**:
- `files_written`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 3s

**Implements Requirements**: FR-006

**Error Handling**: Create directories, handle write permissions

### Functions in Validation Flow

#### Load Architecture for Validation (`F-040`)

**Type**: read  
**Description**: Read architecture file to validate

**Inputs**:
- `architecture_path`

**Outputs**:
- `architecture_object`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 2s

**Implements Requirements**: FR-005

**Error Handling**: Return error if file not found or invalid JSON

#### Validate Completeness (`F-041`)

**Type**: validate  
**Description**: Check all required fields present in architecture

**Inputs**:
- `architecture_object`
- `framework_schema`

**Outputs**:
- `completeness_issues`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 3s

**Implements Requirements**: FR-005

**Error Handling**: List all missing required fields

#### Validate Interface Consistency (`F-042`)

**Type**: validate  
**Description**: Check interfaces match connected components

**Inputs**:
- `architecture_object`
- `related_architectures`

**Outputs**:
- `interface_issues`

**Performance**:
- Context Consumption: 2500 tokens
- Execution Time: 5s

**Implements Requirements**: FR-005

**Error Handling**: Report mismatches with specific interface names

#### Validate Foundational Alignment (`F-043`)

**Type**: validate  
**Description**: Check architecture aligns with mission/scenarios

**Inputs**:
- `architecture_object`
- `mission_statement`
- `user_scenarios`

**Outputs**:
- `alignment_issues`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 8s

**Implements Requirements**: FR-005

**Error Handling**: Report specific alignment violations

#### Aggregate Validation Results (`F-044`)

**Type**: process  
**Description**: Combine all validation issues into report

**Inputs**:
- `completeness_issues`
- `interface_issues`
- `alignment_issues`

**Outputs**:
- `validation_report`

**Performance**:
- Context Consumption: 1500 tokens
- Execution Time: 2s

**Implements Requirements**: FR-005

**Error Handling**: Categorize by severity, count critical issues

#### Determine Validation Status (`F-045`)

**Type**: decide  
**Description**: Return PASS/FAIL based on critical issues

**Inputs**:
- `validation_report`

**Outputs**:
- `validation_status (PASS/FAIL)`

**Performance**:
- Context Consumption: 500 tokens
- Execution Time: 1s

**Implements Requirements**: FR-005

**Error Handling**: FAIL if any critical issues, PASS otherwise

### Functions in Functional Architecture Flow

#### Extract Functional Requirements (`F-050`)

**Type**: read  
**Description**: Parse foundational docs to extract functional requirements (NEW v2.1.0)

**Inputs**:
- `mission_statement`
- `user_scenarios`
- `success_criteria`

**Outputs**:
- `functional_requirements_list`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-008

**Error Handling**: Ensure all user scenarios covered by requirements

#### Define Functional Flows (`F-051`)

**Type**: process  
**Description**: Create process flows, decision flows, data flows (NEW v2.1.0)

**Inputs**:
- `functional_requirements`
- `user_scenarios`

**Outputs**:
- `functional_architecture_object`

**Performance**:
- Context Consumption: 8000 tokens
- Execution Time: 20s

**Implements Requirements**: FR-008

**Error Handling**: Validate flows cover all user scenarios

#### Decompose into Functions (`F-052`)

**Type**: process  
**Description**: Break down flows into atomic functions (NEW v2.1.0)

**Inputs**:
- `functional_flows`

**Outputs**:
- `function_list`

**Performance**:
- Context Consumption: 4000 tokens
- Execution Time: 15s

**Implements Requirements**: FR-008

**Error Handling**: Ensure functions are atomic and traceable to flows

#### Generate Human Visualizations (`F-053`)

**Type**: generate  
**Description**: Create BPMN process flows, UML diagrams, decision trees (NEW v2.1.0)

**Inputs**:
- `functional_architecture`

**Outputs**:
- `visualization_files (SVG)`

**Performance**:
- Context Consumption: 12000 tokens
- Execution Time: 30s

**Implements Requirements**: FR-010

**Error Handling**: Use standard notation (BPMN 2.0, UML 2.5)

*Note: HIGH context consumption - generates multiple large diagrams*

#### Conduct Stakeholder Review (`F-054`)

**Type**: iterate  
**Description**: Present visualizations, collect feedback (NEW v2.1.0)

**Inputs**:
- `visualizations`
- `stakeholders`

**Outputs**:
- `stakeholder_feedback`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 600s

**Implements Requirements**: FR-010

**Error Handling**: Multiple iterations expected, track feedback history

*Note: Context per iteration, may iterate 2-5 times*

#### Build Functional Architecture Graph (`F-055`)

**Type**: process  
**Description**: Create NetworkX graph of functions and dependencies (NEW v2.1.0)

**Inputs**:
- `functional_architecture`

**Outputs**:
- `functional_graph (NetworkX)`

**Performance**:
- Context Consumption: 4000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-009

**Error Handling**: Handle circular dependencies (may be intentional)

#### Analyze Functional Architecture (`F-056`)

**Type**: process  
**Description**: Detect gaps, redundancies, inefficiencies in functions (NEW v2.1.0)

**Inputs**:
- `functional_graph`

**Outputs**:
- `functional_issues_report`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 15s

**Implements Requirements**: FR-009

**Error Handling**: Categorize issues (gaps, redundancy, inefficiency)

#### Refine Functional Architecture (`F-057`)

**Type**: iterate  
**Description**: Address issues from stakeholder feedback AND technical analysis (NEW v2.1.0)

**Inputs**:
- `stakeholder_feedback`
- `functional_issues_report`

**Outputs**:
- `refined_functional_architecture`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 30s

**Implements Requirements**: FR-009

**Error Handling**: Iterate until both stakeholder and technical validation pass

*Note: May iterate multiple times, accumulates context*

#### Validate Functional Completeness (`F-058`)

**Type**: validate  
**Description**: Ensure all user scenarios covered, no gaps (NEW v2.1.0)

**Inputs**:
- `functional_architecture`
- `user_scenarios`

**Outputs**:
- `completeness_status`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 8s

**Implements Requirements**: FR-009

**Error Handling**: Block progression if gaps found

#### Obtain Stakeholder Sign-off (`F-059`)

**Type**: decide  
**Description**: Get formal approval from stakeholders (NEW v2.1.0)

**Inputs**:
- `visualizations`
- `functional_architecture`

**Outputs**:
- `sign_off_status`

**Performance**:
- Context Consumption: 1000 tokens
- Execution Time: 300s

**Implements Requirements**: FR-010

**Error Handling**: Block progression without sign-off

#### Create Functional Allocation Matrix (`F-060`)

**Type**: process  
**Description**: Map functions to services/components (NEW v2.1.0)

**Inputs**:
- `function_list`
- `service_candidates`

**Outputs**:
- `functional_allocation_matrix`

**Performance**:
- Context Consumption: 4000 tokens
- Execution Time: 20s

**Implements Requirements**: FR-011

**Error Handling**: Ensure 100% functional coverage, high cohesion, low coupling

#### Validate Functional Allocation (`F-061`)

**Type**: validate  
**Description**: Check allocation quality (cohesion, coupling, balance) (NEW v2.1.0)

**Inputs**:
- `functional_allocation_matrix`

**Outputs**:
- `allocation_validation_result`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 5s

**Implements Requirements**: FR-011

**Error Handling**: Recommend refactoring if poor allocation quality

### Functions in Documentation Generation Flow

#### Load Architectures for Documentation (`F-070`)

**Type**: read  
**Description**: Read all architecture files to document

**Inputs**:
- `system_root`

**Outputs**:
- `architecture_list`

**Performance**:
- Context Consumption: 10000 tokens
- Execution Time: 8s

**Implements Requirements**: FR-007

**Error Handling**: Skip invalid files, warn user

#### Generate Interface Contract Documents (`F-071`)

**Type**: generate  
**Description**: Create ICDs for each service/component interface

**Inputs**:
- `architecture_list`

**Outputs**:
- `icd_documents`

**Performance**:
- Context Consumption: 8000 tokens
- Execution Time: 20s

**Implements Requirements**: FR-007

**Error Handling**: Generate placeholder if interface undefined

#### Generate Mermaid Diagrams (`F-072`)

**Type**: generate  
**Description**: Create Mermaid architecture diagrams

**Inputs**:
- `architecture_list`
- `system_graph`

**Outputs**:
- `mermaid_diagrams`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 15s

**Implements Requirements**: FR-007

**Error Handling**: Handle large graphs (split into multiple diagrams)

#### Generate Architecture Handoff Document (`F-073`)

**Type**: generate  
**Description**: Create comprehensive handoff doc for humans

**Inputs**:
- `architecture_list`
- `system_graph`
- `analysis_report`

**Outputs**:
- `handoff_document`

**Performance**:
- Context Consumption: 6000 tokens
- Execution Time: 25s

**Implements Requirements**: FR-007

**Error Handling**: Include all critical information

#### Write Documentation Files (`F-074`)

**Type**: generate  
**Description**: Save all documentation to file system

**Inputs**:
- `icd_documents`
- `diagrams`
- `handoff_doc`

**Outputs**:
- `files_written`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 5s

**Implements Requirements**: FR-007

**Error Handling**: Create directory structure, handle permissions

### Functions in Context Bottleneck Analysis Flow

#### Load Functional Architecture for Analysis (`F-080`)

**Type**: read  
**Description**: Read functional architecture with context annotations (META)

**Inputs**:
- `functional_architecture_path`

**Outputs**:
- `functional_architecture_object`

**Performance**:
- Context Consumption: 5000 tokens
- Execution Time: 3s

**Implements Requirements**: FR-013

**Error Handling**: Require context consumption data in architecture

#### Build Context-Weighted Graph (`F-081`)

**Type**: process  
**Description**: Create graph with context consumption as edge weights (META)

**Inputs**:
- `functional_architecture`

**Outputs**:
- `context_weighted_graph`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 8s

**Implements Requirements**: FR-013

**Error Handling**: Use estimates if exact values not available

#### Calculate Path Context Consumption (`F-082`)

**Type**: process  
**Description**: Sum context along all paths to find cumulative consumption (META)

**Inputs**:
- `context_weighted_graph`

**Outputs**:
- `path_context_report`

**Performance**:
- Context Consumption: 4000 tokens
- Execution Time: 12s

**Implements Requirements**: FR-013

**Error Handling**: Handle cycles (infinite paths)

#### Detect Context Bottlenecks (`F-083`)

**Type**: process  
**Description**: Identify paths exceeding usable context (160k tokens) (META)

**Inputs**:
- `path_context_report`
- `context_threshold`

**Outputs**:
- `bottleneck_list`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 5s

**Implements Requirements**: FR-013, FR-020

**Error Handling**: Flag paths > 160k as CRITICAL, >140k as WARNING

#### Generate Optimization Recommendations (`F-084`)

**Type**: generate  
**Description**: Suggest refactorings to reduce context consumption (META)

**Inputs**:
- `bottleneck_list`
- `functional_architecture`

**Outputs**:
- `optimization_recommendations`

**Performance**:
- Context Consumption: 3000 tokens
- Execution Time: 10s

**Implements Requirements**: FR-013

**Error Handling**: Provide specific, actionable recommendations

#### Write Context Analysis Report (`F-085`)

**Type**: generate  
**Description**: Save context bottleneck analysis to file (META)

**Inputs**:
- `bottleneck_list`
- `recommendations`

**Outputs**:
- `context_analysis_report`

**Performance**:
- Context Consumption: 2000 tokens
- Execution Time: 3s

**Implements Requirements**: FR-013

**Error Handling**: Always generate report even if no bottlenecks found

---

**Generated**: 2025-11-16 11:12:11  
**Source**: `specs/functional/functional_architecture.json`  
**Tool**: `generate_functional_documentation.py` (v3.14.6)
