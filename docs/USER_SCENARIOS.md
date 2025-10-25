# Reflow Workflow System - User Scenarios

## Primary User: LLM Agents

### Persona: Claude Code Agent
- **Role**: AI coding assistant executing workflows on behalf of human users
- **Goals**: Complete structured workflows correctly, maintain context, produce high-quality architectures
- **Challenges**: Context drift over long workflows, forgetting critical steps, token exhaustion
- **Needs**: Clear step-by-step guidance, validation tools, context management mechanisms

## User Scenarios

### Scenario 1: New Greenfield IT System (Web-Based)

**Actor**: LLM Agent (Claude Code) + Human User
**Context**: Human wants to design a new microservices architecture for a smart home system
**Trigger**: Human says "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json on system in github.com/user/smart_home"

**Flow**:
1. LLM agent executes 00-setup.json:
   - Configures paths (reflow_root, system_root)
   - Human selects UAF framework (IT system)
   - Creates directory structure
   - Human provides mission statement and success criteria
   - Initializes working_memory.json with workflow state
2. LLM agent proceeds to 01-systems_engineering.json:
   - Human describes system components
   - LLM creates service_architecture.json for each service
   - LLM runs system_of_systems_graph_v2.py to generate system graph
   - Graph analysis detects orphaned services and missing interfaces
   - LLM fixes issues and re-validates
3. LLM agent proceeds to 02-artifacts_visualization.json:
   - Generates Interface Contract Documents (ICDs)
   - Creates Mermaid diagrams
   - Produces human-readable documentation
4. (Optional) Development and operations workflows
5. Commits all artifacts to GitHub repo

**Success Criteria**:
- All workflow steps completed without skipping
- All quality gates passed
- Architecture validated with 0 critical issues
- Human can resume work days later using context/working_memory.json

---

### Scenario 2: Multi-Day Project with Context Preservation

**Actor**: LLM Agent + Human User
**Context**: Human worked on project 3 days ago, wants to continue
**Trigger**: Human says "Continue workflow from context/working_memory.json in github.com/user/my_system"

**Flow**:
1. LLM agent reads context/working_memory.json from GitHub:
   ```json
   {
     "current_workflow": "01-systems_engineering",
     "current_step": "SE-02-A03",
     "operations_since_refresh": 5
   }
   ```
2. LLM identifies need for context refresh (operations >= 5)
3. LLM executes context refresh sequence:
   - Reads workflow file (01-systems_engineering.json)
   - Reads step definition (SE-02-A03)
   - Reads current_focus.md
   - Confirms: "System: My System, Workflow: Systems Engineering, Step: SE-02-A03 (Create service architecture for user_service), Next action: Create specs/machine/service_arch/user_service_architecture.json"
4. LLM resumes from exact step, completes action
5. LLM updates working_memory.json, resets operations_since_refresh = 0
6. LLM proceeds to next step

**Success Criteria**:
- LLM correctly identifies current step from context
- No context drift (system name, workflow, step all remembered)
- Work continues seamlessly across sessions

---

### Scenario 3: Framework-Agnostic Usage (Systems Biology)

**Actor**: LLM Agent + Human User (Bioinformatician)
**Context**: Human wants to model a gene regulatory network
**Trigger**: Human says "Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/gene_network"

**Flow**:
1. LLM agent executes setup, presents framework options
2. Human selects "Systems Biology Framework"
3. LLM loads architectural_definitions_systems_biology.json:
   - component_term: "gene/protein"
   - connection_term: "regulatory_interaction"
   - architecture_file_type: "component_architecture.json"
4. LLM proceeds through systems engineering workflow:
   - Creates component_architecture.json for each gene/protein
   - Uses same workflow steps but different terminology
   - Runs system_of_systems_graph_v2.py with --cycles flag (feedback loops expected)
   - Detects biological network properties (hubs, feedback loops, regulatory modules)
5. Generates biological network visualizations

**Success Criteria**:
- Same workflow works for biology domain with no code changes
- Terminology matches domain (genes, not services)
- Analysis results are biologically meaningful (feedback loops detected, not reported as errors)

---

### Scenario 4: Self-Improvement - Workflow Retrospective

**Actor**: LLM Agent + Human User
**Context**: Workflow completed, user wants to improve process
**Trigger**: End of workflow, retrospective step

**Flow**:
1. LLM agent completes final workflow step
2. LLM reads context/workflow_metrics.json:
   ```json
   {
     "total_operations": 142,
     "total_validations": 12,
     "validation_failures": 3,
     "rework_cycles": 2,
     "time_per_step": {...}
   }
   ```
3. LLM generates context/workflow_retrospective_{date}.md:
   - "What worked well: Automatic graph analysis caught 6 architectural issues"
   - "What was confusing: Step SE-02-A05 unclear about port assignment for non-IT systems"
   - "What could be automated: Interface deduction from architecture files"
   - "What took longer than expected: SE-06 graph generation (15 min vs 5 min expected)"
4. LLM appends improvement suggestions to WORKFLOW_IMPROVEMENTS_BACKLOG.md
5. Human reviews and prioritizes improvements

**Success Criteria**:
- Retrospective document generated with concrete observations
- Metrics accurately captured during workflow
- Improvement backlog updated with actionable items

---

### Scenario 5: Meta-Analysis - Reflow Analyzes Itself (Current Scenario!)

**Actor**: LLM Agent (this session)
**Context**: Human wants to use Reflow to analyze Reflow's own workflow structure
**Trigger**: Human says "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json on itself"

**Flow**:
1. LLM treats workflow steps as "services"
2. LLM treats data artifacts as "interfaces"
3. LLM creates architecture files for each workflow step
4. LLM runs system_of_systems_graph_v2.py to analyze workflow dependencies
5. Graph analysis detects:
   - Orphaned steps (defined but never used)
   - Circular dependencies between workflows
   - Missing data handoffs between steps
   - "Dark matter" - implicit dependencies not documented
6. LLM generates report of workflow inefficiencies
7. Human uses findings to refactor workflows

**Success Criteria**:
- Reflow successfully analyzes its own structure
- Detects at least 3 knowledge gaps or inefficiencies
- Demonstrates framework's versatility (self-applicable)

## User Journey Maps

### Journey Map: First-Time User (Setup → Architecture → Documentation)

```
Human: "I want to design a new system"
  ↓
LLM: Execute 00-setup.json (10-15 min)
  ↓
Human: Provide system details, select framework
  ↓
LLM: Execute 01-systems_engineering.json (2-4 hours)
  ↓
Human: Describe components, review architectures
  ↓
LLM: Run graph analysis, detect issues
  ↓
Human: Approve fixes
  ↓
LLM: Execute 02-artifacts_visualization.json (1-2 hours)
  ↓
Human: Review ICDs and diagrams
  ↓
**OUTCOME**: Complete architecture, ready for development or handoff
```

### Journey Map: Returning User (Multi-Day Project)

```
Day 1: Setup + SE steps 1-5
  ↓
Human: "Continue from context"
  ↓
Day 3: LLM reads context, resumes from step 6
  ↓
Human: Approve next actions
  ↓
Day 5: LLM completes SE workflow, transitions to artifacts
  ↓
**OUTCOME**: Seamless multi-day workflow with no context loss
```
