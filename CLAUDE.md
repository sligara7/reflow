# Reflow - LLM Agent Guide

**Version**: 3.9.1
**Last Updated**: 2025-10-28

## What is Reflow?

Reflow is a **framework-agnostic systems engineering workflow** designed for LLM agents to design, architect, and develop complex systems across multiple domains. Provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

**NEW in v3.1.0**: Support for 6+ architectural frameworks - UAF 1.2, Systems Biology, Social Network Analysis, Ecological Systems, Complex Adaptive Systems, Decision Flow, and Custom frameworks.

## Critical Information for LLM Agents

### ⚠️ Version 3.0 Structure

**Active (v3.7.0)**:
- ✅ `workflows/*.json` - 15 workflow files (9 modular + 4 deprecated + 2 special)
- ✅ `workflow_steps/*/` - Step definitions by workflow
- ✅ `workflows_master_index.json` - Workflow routing with branching
- ✅ **Context Reduction**: 60-95% reduction via workflow splitting

**Archived (DO NOT USE)**:
- ❌ `docs/archive/decision_flow.json.old` - Old monolithic workflow

### 🔑 Key Distinction: Tooling vs System

1. **Reflow Tooling** (READ ONLY): `/path/to/reflow/` - workflows, tools, templates
2. **Your System** (WRITABLE): Separate directory for your architecture/code

## Getting Started

### 🤖 FIRST: LLM Self-Reporting (v3.9.1)

**⚠️ CRITICAL FOR ALL LLMs**: Before starting/resuming ANY workflow, you MUST self-report your context capabilities!

**Why**: Enables automatic threshold adjustment for your specific model (Claude 200k vs GPT-4 128k vs GPT-3.5 16k)

**When to Run**:
- Starting a new workflow (`Implement workflow in...`)
- Resuming a workflow (`Continue workflow from...`)
- After context refresh (switching models)

**How to Self-Report** (choose ONE method):

**Method 1: Quick Self-Report (Recommended)**
When user says "Implement workflow..." or "Continue workflow...", immediately respond:

```
I'm [YOUR MODEL NAME] with a [YOUR CONTEXT WINDOW] token context window.

Let me configure my capabilities:
- Model: [YOUR MODEL]
- Context Window: [NUMBER] tokens
- Recommended Threshold: [80% of window] tokens

[Then proceed with workflow]
```

**Method 2: Using Detection Tool**
```bash
python3 {paths.tools_path}/detect_llm_capabilities.py \
  --model "YOUR MODEL NAME" \
  --context-window YOUR_WINDOW \
  --update-working-memory {paths.system_root}
```

**Examples**:
- Claude Sonnet 4.5: `--model "Claude Sonnet 4.5" --context-window 200000` → threshold 160k
- GPT-4 Turbo: `--model "GPT-4 Turbo" --context-window 128000` → threshold 102k
- GPT-3.5: `--model "GPT-3.5" --context-window 16000` → threshold 12k

**Your Context Window**:
- If you're Claude Sonnet 4.5: **200,000 tokens**
- If you're GPT-4 Turbo: **128,000 tokens**
- If you're GPT-3.5: **16,000 tokens**
- If uncertain: State your model name and I'll look it up

**Result**: Your capabilities are stored in `working_memory.json` and all context flow analysis automatically uses YOUR threshold!

---

### ⭐ Web-Based Usage (PRIMARY)

**Why Web-Based?**
- Zero local setup
- Context preservation across sessions
- Multi-day projects resume seamlessly
- GitHub integration (push/pull directly)
- Device agnostic (laptop, tablet, phone)

**Options**:
- **GitHub Codespaces**: Most accessible, 60 hrs/month free, full Linux environment
- **Claude Code**: https://claude.ai/code (requires Pro/Max, install GitHub app for private repos)
- **Other**: Gitpod, Replit, OpenAI Codex, Google Jules

**Quick Start**:
```
Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
on system in github.com/yourname/my_system_repo
```

**Resume Work (Critical for Multi-Day Projects)**:
```
Continue workflow from context/working_memory.json in github.com/yourname/my_system_repo
```

**⚠️ CRITICAL**: Always read `context/working_memory.json` FIRST - it's the source of truth showing exact project state (current workflow, current step, paths).

**Context Preservation** - Two mechanisms:
1. `context/working_memory.json` (PRIMARY) - Exact state, always read this first
2. Conversation history (SUPPLEMENTAL) - Available in code environments

**⚠️ Don't Use**: Regular chat interfaces (claude.ai chat, chatgpt) - need code execution + GitHub integration

### Alternative: Local Machine

```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system
```

### The Workflows (v3.7.0 - Modular)

**NEW in v3.7.0**: Split workflows for **60-95% LLM context reduction**

```
00a-basic_setup.json             → Basic setup (5-10 min)
00b-framework_selection.json     → Framework selection [OPTIONAL] (5-10 min)
01a-approach_detection.json      → Auto-detect approach (<5 min)
01b-bottom_up_integration.json   → Bottom-up integration (2-3 hours)
01c-top_down_design.json         → Top-down design (2-4 hours)
02-artifacts_visualization.json  → ICDs, diagrams (1-2 hours)
03a-development_implementation.json → Implementation (days-weeks)
03b-development_validation.json  → Validation (1-2 days)
04a-testing.json                 → Testing workflows (1 week)
04b-operations.json              → Operations workflows (1 week)
feature_update.json              → Update existing systems
```

**Deprecated (backwards compatibility)**:
- `00-setup.json`, `01-systems_engineering.json`, `03-development.json`, `04-testing_operations.json`

## Workflow Progression

### Typical New System Flow

1. **Start**: Run `00a-basic_setup.json`
   - Configure paths (reflow_root, system_root)
   - Create directory structure
   - Initialize `context/working_memory.json`
   - **Optional**: Run `00b-framework_selection.json` for detailed framework analysis (55% context reduction if skipped)

2. **Architecture**: Run `01a-approach_detection.json` → Routes to 01b OR 01c
   - **Automatic Approach Detection (SE-00)** - LLM examines system directory (95% context reduction)
   - **If existing components found** → Routes to `01b-bottom_up_integration.json` (BU-01 through BU-06)
     - Component inventory, gap analysis, exact code-level deltas
   - **If empty/greenfield** → Routes to `01c-top_down_design.json` (SE-01 through SE-06)
     - Service identification, architecture design, validation
   - **Context Benefit**: LLM loads only relevant path (60% reduction)

3. **Documentation**: Run `02-artifacts_visualization.json`
   - Generate ICDs, Mermaid diagrams
   - Create versioned documentation

4. **Build** (optional): Run `03a-development_implementation.json` then `03b-development_validation.json`
   - 03a: Implement services (58% context reduction - coding separated from validation)
   - 03b: 80% test coverage validation, pre-deployment checks (43% context reduction)

5. **Deploy** (optional): Run `04a-testing.json` then `04b-operations.json`
   - 04a: CI/CD, testing workflows (55% context reduction - testing separated from ops)
   - 04b: Docker Compose, operational testing (42% context reduction)

### Automatic Approach Detection (NEW!)

**LLM automatically detects** whether to use bottom-up (existing components) or top-down (greenfield):

**Detection Process (SE-00)**:
1. LLM scans `system_root` directory (3 levels deep)
2. Looks for indicators:
   - **Bottom-up**: Source code dirs (src/, services/), package manifests (requirements.txt, package.json), build files (Dockerfile), existing architecture files
   - **Top-down**: Empty directory, only docs/context folders
3. **Decision rule**:
   - ≥2 bottom-up indicators → Route to BU-01 (bottom-up integration)
   - 0-1 indicators, system empty → Route to SE-01 (top-down design)
   - Ambiguous (exactly 1 weak indicator) → Ask user to confirm
4. Records decision in `context/approach_detection_result.json`
5. Proceeds to appropriate workflow path

**User sees**: "✓ Auto-detection: BOTTOM-UP approach selected. Found existing components: [services/, requirements.txt]. Proceeding to BU-01."

**Manual Override**: Use legacy entry points `from_existing_components` (force bottom-up) or `from_setup` (force top-down) if automatic detection is unwanted.

### Architecture-Only Flow

```
00a-basic_setup → [optional: 00b-framework_selection] → 01a-approach_detection
→ 01b or 01c → 02-artifacts_visualization (minimal) → DONE
```

## Supported Frameworks

### ⚠️ Framework Selection is Architectural

**DO NOT default to UAF!** Framework determines:
- Which NetworkX analyses you can run (flow requires edge weights)
- What insights you discover (cycles = rework loops OR bugs?)
- System semantics (state machines vs services vs networks)

**Wrong framework = Wrong insights**

**Selection Process** (enforced in S-01A):
1. **Semantic Matching** - 6-question questionnaire (nodes? edges? conditions?)
2. **Score ALL frameworks** - 5-criteria rubric
   - Domain match (weight 2.0)
   - Semantic match (weight 2.5) - HIGHEST
   - Analysis match (weight 2.0)
   - Edge weight feasibility (weight 1.5)
   - Complexity (weight 1.0)
3. **Map analyses** - Show which NetworkX analyses each enables/blocks
4. **User confirmation** - Present scores, require explicit approval (BLOCKING gate)

**Time investment**: 10-15 min analysis saves hours of rework

**Available Frameworks**:

- **UAF 1.2**: Engineered systems (software, hardware, enterprise)
  - Nodes: Services, components
  - Edges: Interfaces, dependencies
  - Use for: Microservices, IoT, DoDAF/MODAF

- **Systems Biology**: Biological systems (molecular to ecosystem)
  - Nodes: Genes, proteins, metabolites, species
  - Edges: Activation, inhibition, catalysis
  - Use for: Gene networks, metabolic pathways

- **Social Network Analysis**: Social systems, organizations
  - Nodes: Individuals, groups, roles
  - Edges: Friendships, collaborations, influence
  - Use for: Organizational structure, social media

- **Ecological Systems**: Ecosystems, species interactions
  - Nodes: Species, populations
  - Edges: Predation, competition, mutualism
  - Use for: Food webs, conservation planning

- **Complex Adaptive Systems**: Emergent, self-organizing
  - Nodes: Adaptive agents
  - Edges: Interactions with feedback
  - Use for: Economic markets, multi-agent simulations

- **Decision Flow**: Workflows, state machines
  - Nodes: Process steps, decision nodes
  - Edges: Transitions (conditional, sequential, rework)
  - Use for: Workflows with quality gates, conditional routing
  - Enables: Flow analysis (critical paths), cycle detection (rework loops)

- **Custom**: LLM-generated for novel domains

See: `docs/NETWORKX_ANALYSIS_GUIDE.md`, `docs/DECISION_FLOW_FRAMEWORK.md`

## Context Management

**Location**: `<your_system>/context/working_memory.json`

**⚠️ CRITICAL FOR LLM AGENTS**: `working_memory.json` contains THE ONLY SOURCE OF TRUTH for paths. You MUST read this file FIRST before any workflow operation and extract the paths.

**Key fields**:
```json
{
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "paths": {
    "reflow_root": "/path/to/reflow",
    "system_root": "/path/to/your_system",
    "tools_path": "/path/to/reflow/tools",
    "templates_path": "/path/to/reflow/templates",
    "workflow_steps_path": "/path/to/reflow/workflow_steps",
    "definitions_path": "/path/to/reflow/definitions"
  },
  "operations_since_refresh": 2
}
```

**MANDATORY Path Usage Rules**:
1. **ALWAYS** read `context/working_memory.json` FIRST before any operation
2. **EXTRACT** the `paths` object and store in your working context
3. **USE** these paths for ALL tool/template/workflow references:
   - Tools: `python3 {paths.tools_path}/system_of_systems_graph_v2.py`
   - Templates: `{paths.templates_path}/service_architecture_template.json`
   - Workflows: `{paths.workflow_steps_path}/systems_engineering/SE-06-GraphGeneration.json`
   - Definitions: `{paths.definitions_path}/framework_registry.json`
4. **NEVER** hardcode paths or guess locations
5. **VERIFY** tool exists before invoking: `ls {paths.tools_path}/system_of_systems_graph_v2.py`

**Context Update Rules**:
- Read before every step
- Update after completing actions
- Refresh context every 4 operations

### Architecture Versioning

```
service_architecture_v1.0.0-20251024.json    ← Versioned file
service_architecture.json                     ← Symlink to current
```

**Benefits**: Complete history, rollback support, version manifest tracking

## Human Documentation Workflow (v3.8.0)

**Purpose**: Enable human-in-the-loop architecture editing with bidirectional translation

**Workflow**:
1. Generate human docs from machine specs:
   ```bash
   python3 {paths.tools_path}/generate_human_documentation.py --system-root {paths.system_root}
   ```

2. Human reviews/edits markdown files:
   ```bash
   vim specs/human/documentation/services/my_service.md
   ```

3. Parse human docs back to machine specs:
   ```bash
   python3 {paths.tools_path}/parse_human_documentation.py --system-root {paths.system_root} --validate
   ```

4. If validation passes: Changes committed
   If validation fails: Conflict report generated

**Key Files**:
- **Human Docs**: `specs/human/documentation/services/*.md`
- **Machine Specs**: `specs/machine/service_arch/*/service_architecture.json`
- **Visualizations**: `specs/human/visualizations/*.{mmd,png,svg}`

**Tools**:
- `generate_human_documentation.py` - Machine → Human translation
- `parse_human_documentation.py` - Human → Machine translation (with validation)
- `component_swap.py` - Safe component replacement with compatibility checking

**Component Swapping Example**:
```bash
# Replace Apache proxy with HAProxy
python3 {paths.tools_path}/component_swap.py \
  --index specs/machine/index.json \
  --remove apache_proxy \
  --add haproxy_proxy \
  --validate
```

**Benefits**:
- ✅ Non-technical stakeholders can review architecture
- ✅ Propose changes via markdown edits (not JSON)
- ✅ Automatic validation prevents broken dependencies
- ✅ Version control tracks architecture evolution
- ✅ PNG/SVG diagrams for presentations and wikis

**When to Use**:
- Step AV-01-A04: Auto-generate human docs after creating service architectures
- Step AV-02-A05: Render Mermaid diagrams to PNG/SVG for distribution
- User-initiated: When stakeholders request architecture review
- User-initiated: When proposing component replacements

## Context Flow Analysis (v3.9.0)

**Purpose**: Predictive context management for LLM agents - prevent context overflow before it happens

**Key Concept**: Model LLM context as a first-class architectural parameter, enabling proactive refresh recommendations

**Usage**:
```bash
python3 {paths.tools_path}/system_of_systems_graph_v2.py \
  {paths.system_root}/specs/machine/index.json \
  --context-flow --context-threshold 40000
```

**What It Does**:
1. **Analyzes workflow paths** - Traces all possible paths through your workflow
2. **Calculates cumulative context** - Tracks token accumulation step-by-step
3. **Identifies bottlenecks** - Flags steps exceeding threshold (default 40k tokens)
4. **Recommends refresh points** - Suggests where to refresh BEFORE overflow

**Output**:
```json
{
  "context_flow": {
    "paths_analyzed": 5,
    "bottlenecks": {
      "total_count": 3,
      "critical_count": 1,
      "details": [
        {
          "step_id": "SE-06",
          "cumulative_context": 45000,
          "severity": "CRITICAL",
          "overflow_tokens": 5000
        }
      ]
    },
    "refresh_recommendations": [
      {
        "refresh_before_step": "SE-06",
        "refresh_after_step": "SE-05",
        "reason": "Predicted overflow (45000 tokens > 40000 threshold)"
      }
    ],
    "optimization_opportunities": {
      "context_efficiency": "MEDIUM",
      "suggestions": [
        "Consider splitting high-context steps or inserting additional refresh points"
      ]
    }
  }
}
```

**Benefits**:
- ✅ **Predictive** (not reactive) - Prevent context loss before it happens
- ✅ **Workflow optimization** - Identify high-context steps (SE-06, D-02, D-03)
- ✅ **LLM capability matching** - Recommend minimum LLM for workflow paths
- ✅ **Context efficiency metric** - Architectural quality parameter

**When to Use**:
- Step SE-06: Auto-run context flow analysis when generating system graph
- User-initiated: When experiencing context degradation signals
- Workflow design: Optimize new workflows for context efficiency

**working_memory.json Integration**:
```json
{
  "context_management": {
    "cumulative_context_tokens": 38000,
    "context_flow_analysis": {
      "enabled": true,
      "predicted_cumulative": 53000,
      "threshold": 40000,
      "refresh_recommended": true,
      "refresh_reason": "Predicted overflow at SE-06"
    }
  }
}
```

**LLMs should**: Read `refresh_recommended` field, auto-execute refresh when `true`

## Quality Gates

**10 gates (7 blocking)**:
1. Architecture Validation (BLOCKING)
2. Interface Registry Consistency (BLOCKING)
3. Contract Completeness (BLOCKING)
4. Test Coverage ≥80% (BLOCKING)
5. Observability Instrumentation (BLOCKING)
6. Docker Compose Validation (BLOCKING)
7. Operational Testing (BLOCKING)
8. Security Scanning (WARNING)
9. Performance Testing (WARNING)
10. Documentation Completeness (WARNING)

## Tools & Templates

**19 Python tools** (see `docs/TOOL_USAGE_SUMMARY.md`):

**Architecture** (Framework-Agnostic):
- `system_of_systems_graph_v2.py` - **FLAGSHIP**: Graph generation with:
  - Knowledge gap detection (6 types: orphaned interfaces, missing nodes, structural holes)
  - 25+ NetworkX algorithms (centrality, community, cycles, SCC, DAG, flow)
  - Supports all frameworks
- `validate_architecture.py` - Framework-agnostic validation
- `generate_interface_contracts.py` - ICD generation

**Development**:
- `bootstrap_development_context.py`, `verify_component_contract.py`, `analyze_features.py`

**Visualization**:
- `generate_mermaid_*.py` - Various diagram generators

**Human Documentation** (v3.8.0):
- `generate_human_documentation.py` - Machine → Human translation
- `parse_human_documentation.py` - Human → Machine translation with validation
- `component_swap.py` - Safe component replacement with compatibility checking

**Context**:
- `context_refresh.py`, `detect_context_drift.py`

**36+ templates** for architecture, contracts, working memory, specs, registries

## Network Analysis Selection

**When**: Step SE-06 (graph generation)

**Process**:
1. Read `framework_id` from `working_memory.json`
2. Load `framework_registry.json` → find `recommended_analyses`
3. Select high+medium priority analyses
4. Check edge weight requirements (flow analysis NEEDS weights)
5. Run: `python3 system_of_systems_graph_v2.py index.json --detect-gaps --[FLAGS]`

**Framework-Specific Examples**:
- **UAF**: `--centrality --dag --scc --community` (find critical services, verify no cycles)
- **Biology**: `--cycles --centrality --community` (feedback loops are expected, hub genes)
- **Social**: `--centrality --community --clustering` (influencers, groups, cohesion)
- **Ecology**: `--flow --centrality --connectivity` (energy flow, keystone species - NEEDS weights!)

**Edge Weights** (if flow analysis selected):
- UAF: `request_rate` (req/sec), `data_volume` (MB/sec)
- Biology: `reaction_rate` (molecules/sec)
- Social: `interaction_frequency` (contacts/week)
- Ecology: `energy_transfer_rate` (kcal/m²/year)

**Output**: `system_of_systems_graph.json` → `networkx_analysis` section

## IT System Requirements (UAF with Human Users) - CRITICAL!

**Applicability**: UAF framework systems with human users or external API access

**⚠️ Design Upfront, Not Retrofit**: IT systems with human users/external APIs **MUST** address these upfront (not afterthoughts):

1. **Security** (SE-02-A05) - Authentication, authorization, **API gateway** (MANDATORY), rate limiting, encryption, audit logging
2. **Deployment** (SE-02-A06) - One-command deploy, health checks, CI/CD, monitoring, RTO/RPO targets
3. **UX/API** (SE-02-A07) - RESTful design, user-friendly errors, **OpenAPI docs** (MANDATORY), versioning, performance targets
4. **Operational Environment** (SE-02-A08) - Design for failures, attacks, scale; define testing strategy NOW

**Rationale**: Retrofitting after launch is **10-100x more expensive** than designing correctly upfront.

**When**: Steps SE-02-A05 through SE-02-A08 during architecture design (workflows `01b-bottom_up_integration.json` or `01c-top_down_design.json`)

**Validation Gates**: SE-03-A05, SE-03-A06, SE-03-A07, SE-03-A08 (ALL BLOCKING)

**CRITICAL Requirements**:
- **API Gateway**: MUST be fully implemented (not orphaned scaffolding) - Checked in SE-06 orphaned service detection
- **Security**: MFA for admins, TLS 1.2+, AES-256 at-rest encryption for sensitive data
- **Deployment**: `docker-compose up -d` or equivalent, <10 min developer setup, <5 min rollback
- **UX/API**: OpenAPI spec, Swagger UI, error messages with field names and descriptions
- **Operations**: 10 IT considerations (service decomposition, containerization, IaC, CI/CD, scalability, security, monitoring, networking, cost, testing)

**Checklist** (Before SE-03):
- [ ] `security_architecture.json` created (auth, authorization, API gateway, rate limiting, encryption, audit)
- [ ] `deployment_architecture.json` created (Docker, CI/CD, health checks, monitoring, RTO/RPO)
- [ ] `ux_api_design.json` created (RESTful, errors, OpenAPI, versioning, performance)
- [ ] `operational_environment.json` created (availability target, testing strategy, failure scenarios)
- [ ] API gateway exists in architecture and will be fully implemented (not orphaned)
- [ ] `port_registry.json` created and validated (for all UAF IT systems)

**📖 Full Documentation**: See [docs/IT_SYSTEM_REQUIREMENTS.md](docs/IT_SYSTEM_REQUIREMENTS.md) for comprehensive guidance (security, deployment, UX, operations, checklist, templates)

## Port Management (UAF/IT Only)

**Applicability**: UAF framework only (not biology/social/ecology)

**Check**: `framework_registry.json` → `deployment_characteristics.port_management_applicable`

**Steps**: SE-02-A04 (assign), SE-03-A04 (validate)

**Process**:
1. **Categorize**: App (8000-8099), Internal (8100-8199), Data (8200-8299), Infrastructure (8300-8399)
2. **Assign sequential**: First app → 8000, second app → 8001, etc.
3. **Update architecture**: `service_architecture.json` → `deployment.ports.primary.port`
4. **Create**: `specs/machine/port_registry.json`
5. **Validate**: `python3 validate_port_registry.py <system_root>/specs/machine/port_registry.json`

**Validation Rules**:
- PC-01: No duplicate primary ports (ERROR - blocking)
- PC-02: No port overlap (ERROR - blocking)
- PC-03: Ports within ranges (WARNING)
- PC-04: Avoid privileged <1024 (WARNING)
- PC-05: Docker host/container consistency (INFO)

**Troubleshooting**:
```bash
# Find what's using port
docker ps | grep <service>
netstat -tlnp | grep <port>  # Linux
lsof -i :<port>              # Mac

# Fix
docker-compose down
kill -9 <PID>
# Update port_registry.json
```

**Service connectivity**: Use service name in docker-compose: `http://character_service:8000` (NOT localhost)

## Common Patterns

### Pattern 1: Web-Based Greenfield System (PRIMARY)

**Day 1: Setup and Architecture**
1. User creates GitHub repo with system description
2. Opens Codespaces/Claude Code
3. "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json on system in github.com/yourname/smart_home_system"
4. LLM executes setup, framework selection, initial architecture
5. Context saved in `context/working_memory.json`

**Day 2+: Continue**
1. Opens Codespaces/Claude Code (conversation persists!)
2. "Continue workflow from context/working_memory.json in github.com/yourname/smart_home_system"
3. LLM reads context, resumes from exact step
4. Progress: 00-setup → 01-SE → 02-artifacts → 03-dev → 04-test

**Result**: Fully designed, documented, implemented system - never touched local machine

**LLM Best Practices**:
- ALWAYS read `context/working_memory.json` first when user says "continue"
- **EXTRACT AND STORE** the `paths` object - you'll need it for EVERY tool invocation
- Check `current_workflow` and `current_step` to know where to resume
- **USE** extracted paths for all tool/template/workflow references (NEVER hardcode)
- Update context after each operation
- Commit to GitHub after major milestones

### Pattern 2: Architecture-Only

```
00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → STOP
Result: Complete architecture specs, diagrams, ICDs - no service code
```

### Pattern 3: Resuming After Break (Critical!)

**Scenario**: User worked 3 days ago, wants to continue

**User**: "Continue workflow from context/working_memory.json in github.com/yourname/my_system"

**LLM Process**:
1. Read `github.com/yourname/my_system/context/working_memory.json`
2. **EXTRACT** (MANDATORY):
   - `current_workflow` (e.g., "01-systems_engineering")
   - `current_step` (e.g., "SE-06")
   - **`paths` object** (reflow_root, system_root, tools_path, templates_path, etc.) - STORE THIS!
   - `operations_since_refresh`
3. Check if refresh needed (>4 operations → refresh)
4. Load workflow: `{paths.reflow_root}/workflows/{current_workflow}.json`
5. Load step definition: `{paths.workflow_steps_path}/systems_engineering/{current_step}-*.json`
6. Resume from exact step
7. **USE extracted paths** for ALL tool/template references:
   - Example: `python3 {paths.tools_path}/system_of_systems_graph_v2.py {paths.system_root}/specs/machine/index.json`
8. Update context after operations
9. Commit to GitHub at milestones

**CRITICAL**:
- Context folder IS the source of truth. Conversation history is supplemental.
- **PATHS MUST BE EXTRACTED FROM working_memory.json** - NEVER hardcode or guess locations!

### Pattern 4: Feature Update

```
"Implement workflow in github.com/sligara7/reflow/workflows/feature_update.json on system in github.com/yourname/my_system"

Process: Read existing architecture → Propose changes → Validate impact → Update with versioning → Generate updated ICDs/diagrams
Result: Updated system with backward compatibility tracking
```

## Troubleshooting

### "Can't find tool X" or "Tool doesn't exist"

**Symptom**: LLM claims `system_of_systems_graph_v2.py` or other tools don't exist

**Root Cause**: Paths not extracted from `working_memory.json`

**Fix (for LLM agents)**:
1. **READ** `{system_root}/context/working_memory.json`
2. **EXTRACT** the `paths` object:
   ```json
   {
     "reflow_root": "/actual/path/to/reflow",
     "tools_path": "/actual/path/to/reflow/tools",
     ...
   }
   ```
3. **VERIFY** tool exists: `ls {paths.tools_path}/system_of_systems_graph_v2.py`
4. **USE** extracted path: `python3 {paths.tools_path}/system_of_systems_graph_v2.py ...`

**NEVER**:
- ❌ Hardcode paths like `/home/user/reflow/tools/`
- ❌ Guess locations like `./tools/`
- ❌ Create new tools when existing ones can't be found
- ❌ Skip reading `working_memory.json` because you "know" the paths
- ❌ Download templates/tools from GitHub using `curl` - Reflow is ALREADY LOCAL!
- ❌ Fetch from `https://raw.githubusercontent.com/sligara7/reflow/` URLs

**ALWAYS**:
- ✅ Read `working_memory.json` FIRST before EVERY workflow step
- ✅ Extract all paths from the `paths` object
- ✅ Verify tool exists before invoking: `ls {paths.tools_path}/system_of_systems_graph_v2.py`
- ✅ Use LOCAL extracted paths in ALL commands
- ✅ Read LOCAL templates: `cat {paths.templates_path}/service_architecture_template.json`
- ✅ Run LOCAL tools: `python3 {paths.tools_path}/system_of_systems_graph_v2.py`

### "Downloading templates from GitHub with curl"

**Symptom**: LLM tries to download templates/tools using `curl https://raw.githubusercontent.com/sligara7/reflow/...`

**Root Cause**: LLM doesn't realize Reflow is ALREADY installed locally

**Why This is Wrong**:
- Reflow tooling is ALREADY on your machine (local installation)
- Templates, tools, workflows are LOCAL files, not remote
- `working_memory.json` contains paths to LOCAL installation

**Fix (for LLM agents)**:
1. **STOP** using `curl` to download from GitHub
2. **READ** `{system_root}/context/working_memory.json`
3. **EXTRACT** paths: `paths.templates_path`, `paths.tools_path`, etc.
4. **USE** local files:
   - ❌ WRONG: `curl https://raw.githubusercontent.com/sligara7/reflow/main/templates/service_architecture_template.json`
   - ✅ CORRECT: `cat {paths.templates_path}/service_architecture_template.json`

**Example from Real Session** (what NOT to do):
```bash
# WRONG - Downloading from GitHub
curl -s https://raw.githubusercontent.com/sligara7/reflow/main/templates/service_architecture_template_uaf.json -o templates/...
# Result: 0 lines (file doesn't exist remotely)

# CORRECT - Use local installation
cat /path/extracted/from/working_memory/templates/service_architecture_template.json
# Result: 400+ lines (file exists locally)
```

### "Working memory doesn't exist"

**Symptom**: `context/working_memory.json` file not found

**Root Cause**: Setup workflow (00a-basic_setup.json) not run yet

**Fix**:
1. Run: `Implement workflow in github.com/sligara7/reflow/workflows/00a-basic_setup.json on system in {your_system_path}`
2. This creates `context/working_memory.json` with all required paths
3. Then proceed with your intended workflow (01a, 01b, 01c, etc.)

## What to Avoid vs Do

**❌ Don't**:
- Modify reflow tooling files (workflows, templates, tools)
- Use archived v2.x files
- Skip setup workflow
- Mix reflow and system directories
- Skip quality gates
- Hardcode paths or guess tool locations
- Create new tools when existing ones can't be found

**✅ Do**:
- Reference reflow as read-only library
- Work in your system directory
- Follow workflow sequence
- Use versioning (semver, symlinks)
- Run validation tools before advancing
- Always read `working_memory.json` FIRST and extract paths
- Verify tools exist before invoking them

## File Structure

```
<your_system>/
├── context/                     # LLM workflow tracking
│   ├── working_memory.json
│   ├── step_progress_tracker.json
│   └── current_focus.md
├── specs/                       # Architecture specifications
│   ├── machine/                # Machine-readable
│   │   ├── service_arch/      # service_architecture.json files
│   │   ├── interfaces/        # Interface Contract Documents
│   │   └── graphs/            # system_of_systems_graph.json
│   └── human/                  # Human-readable
│       ├── visualizations/    # Mermaid diagrams
│       └── documentation/     # Architecture docs
├── services/                    # Service implementations (optional)
└── docs/                        # Foundational documents
```

## New Features (v3.0.1)

### Git Automation (Optional)
- Step S-03-A06 in `00-setup.json`
- ~36 auto-commits at milestones (after service architecture, system graph validation, docs, implementations)
- See `docs/GIT_AUTOMATION_GUIDE.md`

### Development Research (Optional)
- Step D-01-A00 in `03-development.json`
- 5-10 min industry standards search (dependency mgmt, containers, CI/CD, security, testing)
- Output: `context/development_tooling_research_{date}.md`
- Example findings: poetry vs requirements.txt, ruff vs pylint

### Enhanced Validation
- Step SE-06 in `01-systems_engineering.json`
- Detects async/sync framework mismatches, circular dependencies, orphaned services
- Output: `specs/machine/architecture_issues.json`

## New Features (v3.6.0 - Early Testing Integration)

### 🎯 Problem Solved
Prevents "toss it over the fence" problem between development and operational testing. Previously, operational testing discovered 15+ critical deployment blockers that should have been caught during development (missing dependencies, circular imports, configuration drift, database permission issues, Docker build failures).

### Pre-Deployment Validation (D-06.5)
**NEW Workflow Step**: `workflow_steps/development/D-06_5-PreDeploymentValidation.json`
- **Purpose**: Comprehensive validation step that catches 80-90% of deployment blockers BEFORE operational testing
- **7 Validation Actions**:
  - D-06.5-A01: Validate Dependencies (prevents ModuleNotFoundError, ImportError, version conflicts)
  - D-06.5-A02: Validate Module Structure (prevents circular imports, missing `__init__.py`)
  - D-06.5-A03: Validate Configuration Consistency (code config matches docker-compose.yml)
  - D-06.5-A04: Validate Database Permissions (migrations run as service user, not superuser)
  - D-06.5-A05: Validate Docker Build (all services build successfully)
  - D-06.5-A06: Run Smoke Tests (basic functionality validation, < 30 seconds)
  - D-06.5-A07: Validate Contracts (implementation matches architecture)
- **Quality Gate**: G-D-06.5 (BLOCKING) - Must pass all 7 validations before operational testing
- **Time**: 30-60 minutes vs days of debugging in operational testing
- **Impact**: Saves 3-5 days per service (24-40 days for 8-service system)

### 3 New Validation Tools
**`tools/validate_dependencies.py`** (380 lines)
- AST-based import analysis
- Compares code imports against requirements.txt
- Detects: Missing dependencies, unused dependencies, version conflicts, missing `__init__.py`
- Usage: `python3 validate_dependencies.py /path/to/system_root`

**`tools/validate_module_structure.py`** (380 lines)
- Detects missing `__init__.py` files
- Finds circular imports (A imports B, B imports A)
- Identifies module shadowing (local module shadows stdlib)
- Tests module imports programmatically
- Usage: `python3 validate_module_structure.py /path/to/system_root`

**`tools/validate_configuration_consistency.py`** (490 lines)
- Validates code configuration matches docker-compose.yml
- Checks: DATABASE_URL format, host/port/user/database consistency, Redis URL, message queue config
- Prevents: "Can't connect to localhost" errors (code uses localhost but docker-compose uses service names)
- Usage: `python3 validate_configuration_consistency.py /path/to/system_root`

### Incremental Validation Gates (D-0X-A99)
**NEW Actions**: "Prove-it-works" validation gates at each development step
- **D-02-A99**: Prove It Works - Domain Model (service starts, /health OK, basic smoke test)
- **D-03-A99**: Prove It Works - Persistence (database connection, migrations run, CRUD works)
- **D-04-A99**: Prove It Works - Integration & Security (service-to-service calls, auth enforced)
- **D-05-A99**: Prove It Works - Observability (/metrics endpoint, structured logs, traces)
- **Philosophy**: Catch issues incrementally during development (when cheap to fix) rather than at the end (when expensive)
- **Time**: 5-20 minutes per gate
- **Non-blocking**: Warnings only, doesn't block progression

### Risk-Based Testing Strategy
**SE-02-A10: Service Risk Assessment** (NEW)
- Template: `templates/service_risk_assessment_template.json` (520+ lines)
- Output: `specs/machine/service_arch/{service}/risk_assessment.json` (per service)
- **3 Risk Categories** (1-3 scale):
  - Deployment risk (complexity of deploying/configuring)
  - Integration risk (dependencies on other services)
  - Operational risk (impact of failure)
- **Overall Risk Score**: (deployment + integration + operational) / 3
- **Risk Levels**: low (1.0-1.5), medium (1.6-2.5), high (2.6-3.0)
- **Testing Strategy by Risk**:
  - **High risk (2.6-3.0)**: 85% coverage, load at 5x traffic, chaos tests, failover tests, pentesting
  - **Medium risk (1.6-2.5)**: 80% coverage, load at 2x traffic, contract tests
  - **Low risk (1.0-1.5)**: 60% coverage, basic integration tests
- **Impact**: Focuses effort on high-risk services (payment, auth, API gateway), avoids over-testing low-risk (logging, metrics)

### Testing as Architecture
**SE-02-A09: Operational Testing Objectives** (NEW)
- Template: `templates/operational_testing_objectives_template.json` (317 lines)
- Output: `specs/machine/service_arch/{service}/operational_testing_objectives.json` (per service)
- **Defines per-service**:
  - Testability requirements (health endpoints `/health`, `/ready`, observability hooks `/metrics`, structured logging)
  - 5 deployment test scenarios (startup validation, database connection, dependency handling, config validation, resource limits)
  - 6 operational acceptance criteria with measurable targets (startup < 30s, health check < 100ms, etc.)
  - Smoke test requirements (< 30 seconds total: CRUD, auth, migrations, inter-service, error handling)
- **Philosophy**: Testability is an architectural requirement, not an operational concern

**SE-06-A05: System Test Strategy** (NEW)
- Template: `templates/system_test_strategy_template.json` (800+ lines)
- Output: `specs/machine/system_test_strategy.json` (system-wide)
- **6 Test Strategy Sections**:
  - **Unit Test Strategy**: Coverage targets (risk-based), frameworks (pytest, Jest, JUnit), mocking strategy
  - **Integration Test Strategy**: Service pairs to test (from system graph edges), test environment (Docker Compose)
  - **Contract Test Strategy**: Consumer-driven contracts, tools (Pact), versioning (semantic)
  - **Performance Test Strategy**: Load/stress/soak testing, target metrics (p95 < 500ms, 99.9% availability)
  - **Security Test Strategy**: OWASP Top 10, dependency scanning, pentesting, SAST/DAST
  - **Operational Test Strategy**: Deployment tests (cold start, upgrade, rollback), failover tests, chaos tests (high-risk only), backup/restore
- **Critical Principle**: Testing strategy defined HERE (SE phase), implemented in Development (D-02 to D-05), executed in Testing (TO-01 to TO-05). Testing phase does NOT invent new tests.
- **Integration Targets**: Every edge in `system_of_systems_graph.json` requires at least one integration test
- **Contract Targets**: Every interface with `external_api: true` requires contract test

### Optional Rapid Prototype (D-01-A06)
**NEW Action**: `D-01-A06 - Create Lightweight Service Prototype (OPTIONAL)`
- **Purpose**: 2-4 hour validation of architecture assumptions for high-risk services
- **When to use**: High-risk service (score >= 2.6), complex deployment, unfamiliar tech stack, external dependencies
- **What to build**: Single endpoint, basic database connection, minimal business logic, no tests/observability (barebones only)
- **Time investment**: 2-4 hours now saves days of rework later if architecture assumptions are wrong

### SE Workflow Refactoring
**Resolved Token Limit Issue**:
- **Before**: `workflows/01-systems_engineering.json` had 2,063 lines, 27,556 tokens (exceeded 25,000 limit)
- **Solution**: Extracted SE-02 and SE-06 to dedicated step files
  - `workflow_steps/systems_engineering/SE-02-ServiceArchitecture.json` (444 lines)
  - `workflow_steps/systems_engineering/SE-06-GraphGeneration.json` (261 lines)
- **After**: Main workflow reduced to 1,507 lines, 18,900 tokens (-27% lines, -31% tokens)
- **Benefit**: Avoids context exceeded errors, follows established modular pattern

### Documentation
- **Release Notes**: `docs/RELEASE_NOTES_v3.6.0.md` - Comprehensive release notes with examples, usage, migration guide
- **Tool Documentation**: `docs/TOOL_USAGE_SUMMARY.md` - Updated with 3 new validation tools
- **Templates**: 3 new comprehensive templates with inline documentation and LLM agent guidance

### Usage Example
```
Systems Engineering Phase:
1. SE-02-A09: Define operational testing objectives for each service
2. SE-02-A10: Assess risk for each service (low/medium/high)
3. SE-06-A05: Define system test strategy (aggregates all service risk assessments)

Development Phase:
1. D-01-A06: Create rapid prototype (OPTIONAL, for high-risk services)
2. D-02-A99: Prove It Works - Domain Model (service starts, basic smoke test)
3. D-03-A99: Prove It Works - Persistence (database connection, CRUD operations)
4. D-04-A99: Prove It Works - Integration & Security (service calls work, auth enforced)
5. D-05-A99: Prove It Works - Observability (/metrics endpoint, structured logs)
6. D-06.5: Pre-Deployment Integration Validation (7 automated checks) - BLOCKING GATE

Operational Testing Phase:
- Executes tests defined in SE-06-A05 system test strategy
- 80-90% fewer blockers discovered (caught by D-06.5)
- Focus on real operational concerns (not deployment issues)
```

### Impact Summary
✅ Prevents "toss it over the fence" between development and operations
✅ Catches 80-90% of deployment blockers before operational testing (D-06.5)
✅ Incremental validation gates catch issues during development (D-0X-A99)
✅ Risk-based testing focuses effort on high-risk services
✅ Testing as architecture - testability requirements defined upfront (SE-02-A09)
✅ Comprehensive test strategy - defined in SE phase, not ad-hoc (SE-06-A05)
✅ 3 automated validation tools (dependencies, module structure, configuration)
✅ 3 comprehensive templates (operational objectives, risk assessment, test strategy)
✅ **Estimated impact**: 3-5 days saved per service (24-40 days for 8-service system)

## Multi-Language Support

Python, Java, TypeScript, Go, Rust - system-agnostic architecture patterns, language-specific development steps in workflow 03

## Getting Help

- `docs/TOOL_USAGE_SUMMARY.md` - Comprehensive guide to all 32 tools
- `docs/IT_SYSTEM_REQUIREMENTS.md` - IT system requirements (security, deployment, UX, operations)
- `docs/NETWORKX_ANALYSIS_GUIDE.md` - NetworkX analysis guide (400+ lines)
- `docs/DECISION_FLOW_FRAMEWORK.md` - Decision Flow example (500+ lines)
- `docs/GIT_AUTOMATION_GUIDE.md` - Git automation setup
- `docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md` - Human documentation analysis (973 lines)
- `README.md` - Overview and quick start

## Summary for LLM Agents

### Primary Approach: Web-Based Usage

1. **Web-based is PRIMARY**: Users create GitHub repo, you read from `github.com/sligara7/reflow`, write to their repo
2. **Context is SOURCE OF TRUTH**: ALWAYS read `context/working_memory.json` FIRST when user says "continue"
3. **⚠️ EXTRACT PATHS**: Read `working_memory.json` → Extract `paths` object → Use for ALL tool/template/workflow references - NEVER hardcode or guess
4. **Multi-day projects normal**: User may work 10 min today, resume 3 days later - context preserves state
5. **Two context mechanisms**:
   - `context/working_memory.json` (PRIMARY - read this first!)
   - Conversation history (SUPPLEMENTAL - reference if user mentions)
6. **Reflow is read-only**: Read workflows/templates from GitHub, never modify them
7. **Your system is separate**: All work in user's repo (`github.com/username/system_name`)
8. **Start with 00a-basic_setup**: Configures paths, framework, structure
9. **Modular workflows with branching**: 00a → [00b?] → 01a → (01b OR 01c) → 02 → 03a → 03b → 04a → 04b (+ feature_update)
10. **Quality gates enforced**: 10 gates (7 blocking) ensure quality before advancing
11. **v3.9.0 current**: 32 tools (context flow analysis integrated), 15 workflows, 60-95% context reduction, predictive context management

**CRITICAL PATH EXTRACTION FLOW**:
```
1. User says: "Continue workflow from context/working_memory.json"
2. LLM reads: {system_root}/context/working_memory.json
3. LLM extracts: paths.tools_path, paths.templates_path, paths.reflow_root, etc.
4. LLM uses: python3 {paths.tools_path}/system_of_systems_graph_v2.py
5. LLM NEVER: Hardcodes paths or creates new tools
```

### Secondary Approach: Local Machine

Use if user explicitly requests or web not available.

---

**Ready to Start (Web-Based)?**

```
User creates GitHub repo, then in code environment (Codespaces, Claude Code, etc.) says:
"Implement workflow in github.com/sligara7/reflow/workflows/00a-basic_setup.json
 on system in github.com/yourname/your_system_repo"

(Note: Use 00a-basic_setup for v3.7.0. Legacy 00-setup.json still works but deprecated)
```

**Environment Options**:
- **GitHub Codespaces** (most accessible - free tier 60 hrs/month)
- **Claude Code** (https://claude.ai/code - requires Pro/Max)
- **OpenAI Codex, Google Jules, Gitpod, Replit**

**⚠️ Don't Use**: Regular chat (claude.ai chat, chatgpt, gemini) - they lack code execution and GitHub integration

**Resuming Work (Multi-Day Projects)?**

```
User: "Continue workflow from context/working_memory.json in github.com/yourname/your_system_repo"

Your process:
1. Read context/working_memory.json from their repo
2. Check current_workflow and current_step
3. Resume from exact step
4. Update context after operations
```

**Local Machine (Alternative)?**

```
"Implement workflow in /path/to/reflow/workflows/00a-basic_setup.json on system in /path/to/your_system"

(Note: Use 00a-basic_setup for v3.7.0. Legacy 00-setup.json still works but deprecated)
```

Good luck building complex systems! 🚀
