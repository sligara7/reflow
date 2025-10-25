# Reflow Workflow System - Success Criteria

## Measurable Success Criteria

### 1. Completeness Metrics

**Definition**: All required workflow steps are executed, no critical steps skipped

**Measurements**:
- **Step Completion Rate**: ≥ 95% of required steps completed per workflow execution
- **Gate Passage Rate**: 100% of blocking quality gates passed before workflow progression
- **Orphaned Step Detection**: 0 workflow steps defined but never executed in normal flows

**Validation**:
- Analyze step_progress_tracker.json across multiple workflow runs
- Compare executed steps vs. required steps in workflow definitions
- Run meta-analysis (system_of_systems_graph_v2.py) to detect unreachable steps

---

### 2. Quality Metrics

**Definition**: Generated artifacts meet validation standards and architectural best practices

**Measurements**:
- **Architecture Validation Pass Rate**: ≥ 90% of architectures pass validation on first attempt
- **Interface Consistency**: 100% of interfaces in interface_registry.json match service architectures
- **Contract Completeness**: 100% of required contract fields populated (no "TBD" in production architectures)
- **Knowledge Gap Detection**: System detects ≥ 80% of architectural issues (orphaned services, missing nodes, structural holes)

**Validation**:
- Run validate_architecture.py on generated architectures
- Run system_of_systems_graph_v2.py --detect-gaps to identify issues
- Manual review of generated ICDs and documentation

---

### 3. Efficiency Metrics

**Definition**: Workflows execute in reasonable time without excessive rework

**Measurements**:
- **Setup Workflow**: 10-15 minutes (95th percentile)
- **Systems Engineering Workflow**: 2-4 hours for 5-10 service system (95th percentile)
- **Artifacts Visualization**: 1-2 hours (95th percentile)
- **Rework Cycles**: ≤ 2 validation failures per workflow requiring rework
- **Context Refreshes**: ≤ 10 context refreshes per complete workflow execution

**Validation**:
- Track workflow_metrics.json timestamps and counters
- Calculate time-per-step and identify bottlenecks
- Analyze validation_failures and rework_cycles

---

### 4. Flexibility Metrics

**Definition**: Same workflow structure works across different domains and frameworks

**Measurements**:
- **Framework Support**: 6 frameworks supported (UAF, Systems Biology, SNA, Ecological, CAS, Custom)
- **Framework Switching Cost**: ≤ 5 minutes to switch frameworks for same system
- **Cross-Framework Tool Compatibility**: 100% of tools (validate_architecture.py, system_of_systems_graph_v2.py) work across all frameworks
- **Domain Coverage**: Successful workflow execution in ≥ 4 distinct domains (IT, biology, social, ecological)

**Validation**:
- Test workflow execution with each framework
- Verify tool compatibility via framework adapter tests
- Case studies of real-world usage across domains

---

### 5. Reliability Metrics

**Definition**: Context management prevents drift and supports multi-day projects

**Measurements**:
- **Context Drift Rate**: < 5% of workflow executions experience context drift (forgetting system name, current step, etc.)
- **Context Recovery**: 100% of sessions resumed from working_memory.json successfully
- **Token Efficiency**: Context refresh reduces token usage by ≥ 30% vs. loading all workflow files
- **Session Gap Tolerance**: Workflows successfully resume after ≥ 7 days between sessions

**Validation**:
- Analyze degradation_signals_detected in working_memory.json
- Test session resumption after various time gaps
- Measure token usage with/without context management

---

### 6. Discoverability Metrics

**Definition**: Automated analysis identifies architectural issues and knowledge gaps

**Measurements**:
- **Issue Detection Rate**: System detects ≥ 80% of known architectural issues (based on test cases)
- **False Positive Rate**: < 10% of detected issues are false positives
- **Knowledge Gap Types**: Detects ≥ 6 gap types (orphaned interfaces, missing nodes, dark matter, structural holes, circular deps, isolated components)
- **Analysis Coverage**: NetworkX analysis covers ≥ 10 analysis categories (centrality, paths, connectivity, clustering, properties, community, cycles, SCC, DAG, flow)

**Validation**:
- Create test architectures with known issues
- Run system_of_systems_graph_v2.py --detect-gaps --analyze-all
- Compare detected issues vs. ground truth
- Calculate precision and recall

---

## Functional Requirements

### FR-1: Multi-Workflow Support
**Requirement**: System must support 6+ workflows (setup, systems engineering, artifacts visualization, development, testing/operations, feature update)
**Acceptance**: All 6 workflows execute end-to-end without errors

### FR-2: Quality Gate Enforcement
**Requirement**: System must enforce blocking quality gates and prevent progression when gates fail
**Acceptance**: Attempting to advance past failed gate produces error and halts workflow

### FR-3: Framework Agnosticism
**Requirement**: System must support ≥ 5 architectural frameworks with same workflow structure
**Acceptance**: Setup workflow allows framework selection, subsequent workflows adapt terminology

### FR-4: Context Preservation
**Requirement**: System must maintain workflow state in working_memory.json and support session resumption
**Acceptance**: LLM agent resumes from correct step after reading working_memory.json, 0 steps repeated unnecessarily

### FR-5: Automated Validation
**Requirement**: System must provide automated validation tools for architectures, interfaces, ports, and contracts
**Acceptance**: Validation tools detect ≥ 80% of injected errors in test cases

### FR-6: Graph-Based Analysis
**Requirement**: System must generate system-of-systems graph and perform NetworkX analysis
**Acceptance**: Graph generation succeeds for all frameworks, ≥ 10 analysis types available

### FR-7: Documentation Generation
**Requirement**: System must auto-generate ICDs, Mermaid diagrams, and human-readable documentation
**Acceptance**: All artifact types generated from architecture files without manual intervention

---

## Non-Functional Requirements

### NFR-1: Performance
**Requirement**: Workflows execute in reasonable time (see Efficiency Metrics)
**Target**: Setup < 15 min, SE < 4 hours, Artifacts < 2 hours (p95)

### NFR-2: Usability (LLM Agent Perspective)
**Requirement**: Workflow instructions must be clear enough for LLM agents to follow without human clarification
**Target**: ≥ 90% of workflow steps executed correctly on first attempt

### NFR-3: Maintainability
**Requirement**: Workflows must be modular and independently updateable
**Target**: Update to 1 workflow does not break others, version compatibility tracked

### NFR-4: Extensibility
**Requirement**: New frameworks can be added without modifying core workflow structure
**Target**: Add new framework by creating 2 files (architectural_definitions_X.json, X_node_template.json), 0 workflow file changes

### NFR-5: Token Efficiency
**Requirement**: Context management must reduce token usage in long workflows
**Target**: ≥ 30% token reduction vs. loading all definitions every operation

---

## Meta-Analysis Success Criteria (This Session)

**Goal**: Use Reflow to analyze Reflow itself and identify workflow inefficiencies

**Success Criteria**:
1. **Architecture Creation**: Create service_architecture.json for ≥ 20 workflow steps (across all 6 workflows)
2. **Graph Generation**: Generate system_of_systems_graph.json representing workflow dependencies
3. **Issue Detection**: Detect ≥ 3 knowledge gaps or inefficiencies:
   - Orphaned steps (defined but unreachable)
   - Missing data handoffs (step produces artifact but no step consumes it)
   - Circular dependencies (workflow A → B → A)
   - Implicit dependencies (step assumes context not explicitly provided)
   - Structural holes (workflow phases poorly connected)
4. **Analysis Insights**: NetworkX analysis provides insights on:
   - Critical steps (high centrality - removing them breaks workflow)
   - Workflow phases (community detection groups related steps)
   - Dependency ordering (DAG topological sort shows execution order)
   - Feedback loops (cycle detection identifies iterative refinement steps)
5. **Documentation**: Generate Mermaid diagram visualizing entire workflow system
6. **Actionable Improvements**: Identify ≥ 3 concrete improvements to workflow structure

**Validation**:
- architectural_issues.json contains ≥ 3 issues
- system_of_systems_graph.json generated successfully
- Mermaid diagram renders without errors
- Human can understand workflow structure from visualizations
