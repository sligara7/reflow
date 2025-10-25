# Reflow - LLM Agent Guide

**Version**: 3.3.1
**Last Updated**: 2025-10-25

## What is Reflow?

Reflow is a **framework-agnostic systems engineering workflow** designed specifically for LLM agents to design, architect, and develop complex systems across multiple domains. It provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

**NEW in v3.1.0**: Support for 6+ architectural frameworks - UAF 1.2 (software/hardware), Systems Biology (gene networks, ecosystems), Social Network Analysis (organizations, communities), Ecological Systems (food webs), Complex Adaptive Systems (markets, emergent systems), and Custom frameworks.

## Critical Information for LLM Agents

### ⚠️ Version 3.0 Structure (IMPORTANT!)

This is **v3.0** with a **modular workflow structure**. The old v2.x monolithic `decision_flow.json` has been archived.

**Active Structure (v3.0)**:
- ✅ `workflows/*.json` - 6 separate, focused workflow files
- ✅ `workflow_steps/*/` - Step definitions organized by workflow
- ✅ `workflows_master_index.json` - Workflow routing

**Archived (DO NOT USE)**:
- ❌ `docs/archive/decision_flow.json.old` - Old monolithic workflow
- ❌ `docs/archive/workflow_driver_v2.py` - Incompatible with v3.0
- ❌ `docs/archive/architecture/`, `development/`, `feature_update/` - Old step files

### 🔑 Key Distinction: Tooling vs System Directories

Reflow operates on a **separation principle**:

1. **Reflow Tooling** (this directory - READ ONLY):
   - Location: `/path/to/reflow/`
   - Contains: workflows, tools, templates, definitions
   - **Do not modify** workflow files, templates, or tools
   - Think of this as a "library" you reference

2. **Your System** (separate directory - WRITABLE):
   - Location: Anywhere on filesystem (e.g., `~/projects/my_system/`)
   - Contains: your architecture specs, service code, documentation
   - **This is where you work** and create artifacts
   - Can be its own git repository

**Example**:
```
/home/user/dev/reflow/           ← Reflow tooling (read-only reference)
/home/user/projects/my_system/   ← Your system (where you work)
```

## Getting Started

### ⭐ Recommended: Web-Based Usage (PRIMARY METHOD)

**Reflow is designed for web-based, cloud-first development.** This is now the **PRIMARY** usage pattern, with local machine usage as an alternative.

#### Why Web-Based?

1. **Zero Local Setup**: Never touches user's local machine
2. **Context Preservation**: Web services (Claude.ai, Codespaces) store conversation history
3. **Multi-Day Projects**: Resume work seamlessly across sessions
4. **Device Agnostic**: Work from laptop, tablet, or phone
5. **Direct GitHub Integration**: Push/pull directly to GitHub repos
6. **Context Folder**: Your system repo's `context/` folder tracks exact progress

#### Web-Based Quick Start

**Option A: GitHub Codespaces - MOST ACCESSIBLE**

User opens Codespace, then:
```
Implement workflow in /workspaces/reflow/workflows/00-setup.json
on system in /workspaces/my_system
```

**How it works:**
1. Codespace clones both reflow and system repos
2. Full Linux environment with git, Python, all tools
3. Can use Claude Code CLI or web-based AI code editor in another tab
4. Commits push directly to GitHub
5. Context preserved in system repo

**Cost & Requirements:**
- Free tier: 60 hours/month
- Paid: ~$0.18/hour
- Only needs GitHub account

**Option B: Claude Code (Web) - https://claude.ai/code**

User creates GitHub repo, then in Claude Code:
```
Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
on system in github.com/yourname/my_system_repo
```

**How it works:**
1. Claude Code reads Reflow repo from GitHub (workflows, templates, tools)
2. Claude Code reads/writes to user's system repo on GitHub
3. All artifacts committed to user's system repo
4. Context stored in `context/working_memory.json` in system repo
5. Conversation history persists in Claude Code

**Cost & Requirements:**
- Requires Claude Pro ($20/month) or Max subscription
- **CRITICAL for PRIVATE repos**: Must install Claude GitHub app in all repositories
  - Install at: https://github.com/apps/claude-code
  - For public repos: App installation recommended but may not be required
  - For private repos: App installation is **required** or Claude Code cannot access the repo
- GitHub integration setup required

**Resuming work (next day/session):**
```
Continue workflow from context/working_memory.json in github.com/yourname/my_system_repo
```

**Option C: Other Web-Based Code Environments**

- **OpenAI Codex**: Similar functionality (subscription required)
- **Google Jules**: Google's code environment (subscription/requirements vary)
- **Gitpod**: Alternative to Codespaces (gitpod.io)
- **Replit**: Web-based IDE (replit.com)

**⚠️ IMPORTANT**: Regular chat interfaces (claude.ai chat, chatgpt.com, gemini.google.com) likely **won't work** for this workflow. You need:
- Code execution environment
- GitHub integration (read/write repos)
- File system operations
- Git operations

#### 🔑 Context Preservation for Multi-Day Projects

**CRITICAL**: Users often work on projects across multiple days/sessions. Context is preserved in **TWO WAYS**:

1. **`context/working_memory.json` (in system repo)** - MUST READ THIS FIRST
   ```json
   {
     "current_workflow": "01-systems_engineering",
     "current_step": "SE-02",
     "paths": {
       "reflow_root": "github.com/sligara7/reflow",
       "system_root": "github.com/yourname/my_system"
     },
     "operations_since_refresh": 2
   }
   ```

2. **Conversation History (in web service)**
   - Claude.ai: Conversations persist indefinitely
   - Codespaces: Terminal history preserved in session
   - User can say "continue from yesterday" or "what's next?"

**When user returns next day:**
```
User: "Continue workflow from context/working_memory.json in github.com/yourname/my_system"

LLM Agent Process:
1. Read context/working_memory.json from GitHub
2. Identify current_workflow and current_step
3. Load paths (reflow_root, system_root)
4. Continue from exact step where user left off
5. Update context after each operation
```

**IMPORTANT**: Always read `context/working_memory.json` FIRST before any operation. It tells you exactly where the project is.

### Alternative: Local Machine Usage (SECONDARY METHOD)

<details>
<summary>Click to expand local machine instructions</summary>

Local machine usage is still supported but is now the **alternative** approach:

#### Local Quick Start

```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system
```

**Example**:
```
Implement workflow in /home/user/dev/reflow/workflows/00-setup.json on system in /home/user/projects/smart_home
```

**Key Distinction**:
- Reflow tooling: `/home/user/dev/reflow/` (read-only reference)
- Your system: `/home/user/projects/smart_home/` (where you work)

</details>

### The 6 Workflows (In Order)

Reflow v3.0 consists of **6 focused workflows** that execute sequentially:

```
00-setup.json                    → Initial setup and path configuration (10-15 min)
    ↓
01-systems_engineering.json      → Architecture design, UAF 1.2 compliant (2-4 hours)
    ↓
02-artifacts_visualization.json  → ICDs, diagrams, documentation (1-2 hours)
    ↓
03-development.json              → Service implementation (days to weeks)
    ↓
04-testing_operations.json       → CI/CD, testing, deployment (1-2 weeks)
```

**Plus**: `feature_update.json` for updating existing systems

### 3. Workflow Entry Points

Each workflow file contains:
- **Metadata**: Workflow ID, version, description
- **Prerequisites**: Required templates and tools
- **Steps**: Array of workflow steps with step_file paths
- **Completion**: Next workflow to transition to
- **Quality Gates**: Validation requirements

## Supported Frameworks (NEW in v3.1.0!)

Reflow is **framework-agnostic** - all frameworks map to the same core abstraction: **nodes (components) + edges (connections)**. This allows the same workflow and tools to work across vastly different domains.

### UAF 1.2 - Unified Architecture Framework (DEFAULT)
- **Domain**: Engineered systems (software, hardware, enterprise, defense)
- **Nodes**: Services, components
- **Edges**: Interfaces, dependencies
- **Standard**: ISO/IEC 19540-1:2022
- **Use for**: Microservices, IoT, DoDAF/MODAF architectures

### Systems Biology Framework
- **Domain**: Biological systems (molecular to ecosystem scale)
- **Nodes**: Genes, proteins, metabolites, species, populations
- **Edges**: Activation, inhibition, catalysis, predation, mutualism
- **Use for**: Gene regulatory networks, metabolic pathways, food webs

### Social Network Analysis (SNA)
- **Domain**: Social systems, organizations, communities
- **Nodes**: Individuals, groups, organizations, roles
- **Edges**: Friendships, collaborations, communication, influence
- **Use for**: Organizational structure, social media analysis, collaboration networks

### Ecological Systems Framework
- **Domain**: Ecosystems, species interactions
- **Nodes**: Species, populations, functional groups
- **Edges**: Predation, competition, mutualism, parasitism
- **Use for**: Food web modeling, conservation planning, ecosystem resilience

### Complex Adaptive Systems (CAS)
- **Domain**: Emergent, self-organizing systems
- **Nodes**: Adaptive agents with learning rules
- **Edges**: Interactions with feedback loops
- **Use for**: Economic markets, urban systems, multi-agent simulations

### Custom Framework (LLM-Generated)
- **Domain**: Novel or hybrid systems
- **Process**: LLM researches domain and creates custom framework definition
- **Use for**: Cyber-physical-social systems, experimental domains

**Framework selection**: Happens in step S-01A of setup workflow. LLM agents should choose the framework that best matches the system domain.

## Workflow Progression

### Typical New System Flow

1. **Start**: Run `00-setup.json`
   - Configure all paths (reflow_root, system_root, tools_path)
   - **NEW**: Select architectural framework (S-01A) - UAF, Biology, Social, Ecological, CAS, or Custom
   - Create directory structure
   - Initialize `context/working_memory.json`
   - OPTIONAL: Configure git automation (S-03-A06)

2. **Architecture**: Run `01-systems_engineering.json`
   - Design component architectures using selected framework
   - Create `service_architecture_v{version}-{date}.json` for each service
   - Generate `system_of_systems_graph.json` with architectural issue detection
   - Validate architecture constraints (including async/sync consistency)

3. **Documentation**: Run `02-artifacts_visualization.json`
   - Generate Interface Contract Documents (ICDs)
   - Create Mermaid diagrams
   - Generate versioned documentation

4. **Build**: Run `03-development.json` (optional)
   - OPTIONAL: Research modern development best practices (D-01-A00)
   - Implement services
   - 80% test coverage required
   - Observability instrumentation

5. **Deploy**: Run `04-testing_operations.json` (optional)
   - CI/CD pipeline
   - Docker Compose
   - Operational testing

### Architecture-Only Flow

If you only need architecture (no implementation):
```
00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → DONE
```

## Important Conventions

### Context Management

Reflow uses **working memory** for context tracking:

**Location**: `<your_system>/context/working_memory.json`

**Key Fields**:
```json
{
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "paths": {
    "reflow_root": "/path/to/reflow",
    "system_root": "/path/to/your_system",
    "tools_path": "/path/to/reflow/tools",
    "templates_path": "/path/to/reflow/templates"
  },
  "operations_since_refresh": 2
}
```

**IMPORTANT**:
- Read `working_memory.json` before every step
- Update it after completing actions
- Refresh context every 4 operations

### Architecture Versioning (v3.0+)

All architecture files use **semantic versioning**:

```
# UAF framework example:
service_architecture_v1.0.0-20251024.json    ← Versioned file
service_architecture.json                     ← Symlink to current version

# Systems Biology framework example:
component_architecture_v1.0.0-20251025.json  ← Versioned file
component_architecture.json                   ← Symlink to current version
```

**Note**: File naming depends on selected framework (service_architecture, component_architecture, agent_profile, etc.)

**Benefits**:
- Complete history preserved
- Rollback support via symlinks
- `version_manifest.json` tracks all changes
- Human docs paired with architecture versions

### File Locations (Standard Structure)

**Your System Directory**:
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

## Quality Gates

Reflow enforces **10 quality gates** (7 blocking):

1. **Architecture Validation** (BLOCKING)
2. **Interface Registry Consistency** (BLOCKING)
3. **Contract Completeness** (BLOCKING)
4. **Test Coverage ≥80%** (BLOCKING)
5. **Observability Instrumentation** (BLOCKING)
6. **Docker Compose Validation** (BLOCKING)
7. **Operational Testing** (BLOCKING)
8. Security Scanning (WARNING)
9. Performance Testing (WARNING)
10. Documentation Completeness (WARNING)

## What to Avoid

### ❌ Don't Do This

1. **Don't modify reflow tooling files**:
   - Never edit workflow JSON files
   - Never modify templates or tools
   - Reflow is read-only reference material

2. **Don't use archived v2.x files**:
   - `decision_flow.json.old` is obsolete
   - `workflow_driver_v2.py` doesn't work with v3.0
   - Old `architecture/`, `development/` directories are archived

3. **Don't skip setup workflow**:
   - Always start with `00-setup.json`
   - It configures critical paths in `working_memory.json`

4. **Don't mix reflow and system directories**:
   - Keep system work separate from reflow tooling
   - Never create system artifacts in `/path/to/reflow/`

5. **Don't skip quality gates**:
   - Blocking gates must pass before proceeding
   - Use validation tools before advancing steps

### ✅ Do This Instead

1. **Reference reflow as read-only library**:
   - Read workflows, templates, tools
   - Execute tools from reflow/tools/
   - Copy templates to your system directory

2. **Work in your system directory**:
   - Create all artifacts in `<your_system>/`
   - Maintain `context/working_memory.json`
   - Track progress in `step_progress_tracker.json`

3. **Follow the workflow sequence**:
   - Start with setup, progress through workflows in order
   - Read each workflow file before starting
   - Update context after each step

4. **Use versioning**:
   - Create versioned architecture files
   - Update `version_manifest.json`
   - Use symlinks for "current" version

5. **Run validation tools**:
   - `validate_architecture.py` for architecture files
   - `verify_component_contract.py` for contracts
   - Check quality gates before advancing

## Tools Available (in /path/to/reflow/tools/)

Reflow provides **16 focused Python tools** (streamlined in v3.3.1 from 24):

**For complete tool documentation, see**: `docs/TOOL_USAGE_SUMMARY.md`

**Architecture** (Framework-Agnostic):
- `validate_architecture.py` - Validate architecture files against framework schemas
- `system_of_systems_graph_v2.py` - **FLAGSHIP TOOL** - Framework-agnostic graph generation with:
  - Universal node/edge schema (works across all frameworks)
  - **Knowledge gap detection** (6 gap types: orphaned interfaces, missing nodes, "dark matter" mediators, structural holes, etc.)
  - **Comprehensive NetworkX analysis** (25+ algorithms across 10 categories):
    - Centrality (degree, betweenness, closeness, eigenvector, PageRank)
    - Paths & distances (shortest paths, diameter, average path length, eccentricity)
    - Connectivity (components, bridges, node/edge connectivity)
    - Clustering (coefficient, transitivity, triangles)
    - Properties (density, assortativity, reciprocity, degree distribution)
    - **Community detection** (Louvain, label propagation, Girvan-Newman, modularity)
    - **Cycle detection** (simple cycles, cycle basis, feedback loops, cycle length distribution)
    - **Strongly connected components** (SCCs, condensation graph, component sizes)
    - **DAG analysis** (topological sort, longest path, topological levels)
    - **Flow analysis** (maximum flow, minimum cut, node connectivity)
  - Supports UAF, Biology, Social, Ecological, CAS, and Custom frameworks
  - Usage: `python3 system_of_systems_graph_v2.py index.json --detect-gaps --analyze-all`
  - Or selectively: `--centrality --community --cycles --scc --dag --flow`
- `generate_interface_contracts.py` - Create ICDs from architecture
- `validate_workflow_files.py` - **NEW in v3.3.1** - Validate workflow JSON files

**Development**:
- `bootstrap_development_context.py` - Initialize dev environment
- `verify_component_contract.py` - Validate implementation against contracts
- `analyze_features.py` - Feature analysis and planning

**Visualization**:
- `generate_mermaid_*.py` - Various diagram generators

**Context Management**:
- `context_refresh.py` - Refresh working memory
- `detect_context_drift.py` - Check for context drift

## Templates Available (in /path/to/reflow/templates/)

Over **36 templates** for:
- Service architecture (`service_architecture_template.json`)
- Interface contracts (`interface_contract_complete_template.json`)
- Working memory (`working_memory_template.json`)
- Component specs (`component_specification_complete_template.json`)
- Progress tracking, focus documents, registries, etc.

## Network Analysis Selection (IMPORTANT!)

### When to Select Analyses (Step SE-06)

During **graph generation in SE-06**, you MUST select appropriate NetworkX analyses based on your framework:

**Decision Process**:
1. Read `framework_id` from `working_memory.json -> framework_configuration.framework_id`
2. Load `{reflow_root}/definitions/framework_registry.json` → find your framework's `recommended_analyses`
3. Review `{reflow_root}/definitions/analysis_selection_guide.json` for detailed descriptions
4. Select **high_priority + medium_priority** analyses for your framework
5. Check if any require edge weights (especially **flow analysis**)
6. Construct command: `python3 system_of_systems_graph_v2.py index.json --detect-gaps --[FLAGS]`
7. Update `working_memory.json -> analysis_configuration`

### Framework-Specific Analysis Recommendations

**UAF Systems** (Microservices, IT systems):
```bash
--centrality --dag --scc --community --connectivity
# Why: Verify no circular deps, find critical services, identify deployment groups
```

**Systems Biology** (Gene networks, metabolic pathways):
```bash
--cycles --centrality --community --scc
# Why: Feedback loops are critical, find hub genes, gene modules, coupled regulators
```

**Social Networks** (Organizations, communities):
```bash
--centrality --community --clustering --connectivity
# Why: Find influencers, social groups, measure cohesion, identify bridges
```

**Ecological Systems** (Food webs, ecosystems):
```bash
--flow --centrality --connectivity --community --cycles
# Why: Energy flow is fundamental, keystone species, robustness, nutrient cycles
# CRITICAL: Requires edge weights (energy_transfer_rate or biomass_flow)!
```

**Complex Adaptive Systems** (Markets, emergent systems):
```bash
--cycles --community --scc --centrality
# Why: Feedback loops drive adaptation, emergent clusters, co-evolving groups
```

### Edge Weight Requirements

**When Flow Analysis is Selected**:
- **MUST add** `weight` field to edges in architecture files
- Semantic meaning depends on framework:
  - UAF: `request_rate` (req/sec) or `data_volume` (MB/sec)
  - Biology: `reaction_rate` (molecules/sec) or `binding_affinity`
  - Social: `interaction_frequency` (contacts/week) or `relationship_strength` (0-1)
  - Ecological: `energy_transfer_rate` (kcal/m²/year) or `biomass_flow` (kg/year)
  - CAS: `flow_rate` or `interaction_strength`

**Example** (adding weights to UAF interface):
```json
{
  "name": "character_api",
  "direction": "consumed",
  "connected_services": ["character_service"],
  "weight": 1000,
  "weight_semantic": "request_rate_per_second"
}
```

### Analysis Output Interpretation

Results appear in `system_of_systems_graph.json` under `networkx_analysis` section:
- **Centrality**: High scores = critical/influential nodes
- **Community**: Modularity score + community assignments
- **Cycles**: Feedback loops (expected in biology/CAS, problematic in UAF)
- **DAG**: Topological ordering (good for UAF dependencies, metabolic pathways)
- **Flow**: Maximum throughput and bottlenecks

## IT System Requirements (UAF Systems with Human Users) - CRITICAL!

### ⚠️ Modern, Interconnected World Requirements

**IMPORTANT**: IT systems with human users or external API access **MUST** address three critical requirements **UPFRONT** (not as afterthoughts):

1. **Security** - Authentication, authorization, encryption, audit logging
2. **Deployment Ease** - One-command deployment, automated rollback, clear documentation
3. **User Experience** - Intuitive APIs, clear error messages, straightforward positive experience

**Rationale**: IT systems operate in a modern, interconnected world where these requirements are fundamental to success. Retrofitting security, simplifying deployment, or fixing poor UX after launch is **10-100x more expensive** than designing correctly upfront.

### 🔒 Security Architecture (REQUIRED for UAF with Human Users)

**Applicability**:
- ✅ UAF framework with human users (web apps, mobile apps, admin dashboards)
- ✅ UAF framework with external API access (third-party developers, integrations)
- ❌ Internal machine-to-machine microservices (lighter security acceptable)

**When**: Step SE-02-A05 (during architecture design, before any code)

**Template**: `security_architecture_template.json`

**Required Sections**:
- **Security Posture**: Classification, user types, threat model, compliance requirements
- **Authentication**: Strategy (JWT, OAuth2, SAML), session management, MFA for privileged users
- **Authorization**: RBAC/ABAC, roles and permissions, enforcement points (API gateway, service layer)
- **API Gateway**: **MANDATORY** for human-facing systems (auth, rate limiting, SSL/TLS, CORS)
- **Rate Limiting**: Prevent abuse (e.g., 100 req/min per user, 5 login attempts per 15 min)
- **Input Validation**: XSS prevention, SQL injection prevention, schema validation
- **Encryption**: TLS 1.2+ in-transit, AES-256 at-rest, key management (KMS, Vault)
- **Audit Logging**: Log auth attempts, data access, admin actions; retention policy; alerting

**API Gateway Requirement**:
- If system has human users OR external APIs → api_gateway service **MUST** exist
- API gateway **MUST be fully implemented**, not just scaffolding (orphaned service check in SE-06)
- Responsibilities: Single entry point, authentication, rate limiting, SSL termination, request validation

**Validation**: Step SE-03-A05 (manual review + automated checks) - **BLOCKING GATE**

**Common Issues**:
- Missing API gateway or api_gateway defined but not implemented (orphaned service) → **CRITICAL**
- Weak authentication (no MFA for admins, weak password policy) → **HIGH RISK**
- No encryption at rest for sensitive data (passwords, PII) → **HIGH RISK**
- Insufficient rate limiting → **MEDIUM RISK** (vulnerable to DoS, brute force)

### 🚀 Deployment Architecture (REQUIRED for UAF/IT Systems)

**Applicability**:
- ✅ UAF framework (all IT systems requiring deployment infrastructure)
- ❌ Non-IT systems (biology, ecology, social networks)

**When**: Step SE-02-A06 (during architecture design)

**Template**: `deployment_architecture_template.json`

**Deployment Philosophy - SIMPLICITY FIRST**:
- **One-Command Deployment**: System MUST deploy with single command (`docker-compose up -d` OR `kubectl apply -f manifests/`)
- **Quick Start Time**: New developer can deploy entire system in **< 10 minutes** from git clone
- **Automated Rollback**: Failed deployments automatically revert in **< 5 minutes**
- **Clear Documentation**: README.md with step-by-step deployment instructions and expected outputs

**Required Sections**:
- **Containerization**: Docker/Podman, official base images, image scanning (Trivy, Snyk)
- **Orchestration**: Docker Compose (default for simplicity) OR Kubernetes (only if scale/HA needed)
- **CI/CD Pipeline**: Build → Test → Deploy stages; automated testing; rollback on failure
- **Environment Management**: Dev, staging, production with environment parity
- **Service Discovery**: DNS, health checks (`/health`), readiness probes (`/ready`)
- **Monitoring & Observability**: Metrics (Prometheus), logging (centralized), alerting (critical failures)
- **Backup & DR**: Backup strategy, restore testing, RTO/RPO targets

**Simplicity Guidelines**:
- **Default to Docker Compose** unless Kubernetes features absolutely necessary
- Avoid overcomplication - 3-service system doesn't need Kubernetes
- Document every deployment step - assume reader is new developer

**Validation**: Step SE-03-A06 (manual review + automated checks) - **BLOCKING GATE**

**Common Issues**:
- Overcomplicated orchestration (using K8s when docker-compose sufficient) → Slows iteration
- No health checks → Can't detect failures, no automated recovery
- Manual deployment steps → Error-prone, slow onboarding
- No rollback strategy → Prolonged outages from failed deployments
- Missing observability → Blind to system health, can't diagnose issues

### 🎨 User Experience & API Design (REQUIRED for UAF with Human Users/APIs)

**Applicability**:
- ✅ UAF framework with human users (web/mobile interfaces)
- ✅ UAF framework with external API consumers (third-party developers)
- ❌ Internal machine-to-machine systems

**When**: Step SE-02-A07 (during architecture design, before API contracts finalized)

**Template**: `ux_api_design_template.json`

**UX Philosophy**:
- **Simplicity First**: Intuitive design, clear feedback, error recovery
- **Time to First Success**: New user completes first action in **< 5 minutes**
- **API Time to First Call**: Developer makes first successful API call in **< 5 minutes** from reading docs
- **Task Success Rate**: **> 95%** of users complete common tasks without support

**Required Sections**:
- **API Design Principles**: RESTful design, consistent naming (snake_case or camelCase), backwards compatibility
- **REST API Design**: Resource modeling, pagination, filtering, sorting, consistent HTTP methods
- **Error Handling**: User-friendly messages (not technical jargon), validation errors, recovery guidance
- **API Documentation**: **MANDATORY** - OpenAPI spec, interactive docs (Swagger UI), getting started guide, code examples (curl, Python, JavaScript)
- **Versioning**: URL path versioning (`/api/v1/users`) recommended - most visible and explicit
- **Performance UX**: Response time targets (p95 < 500ms), caching, compression
- **Rate Limiting UX**: Transparent limits with headers (`X-RateLimit-Remaining`, `Retry-After`)
- **Authentication UX**: Clear auth flow, easy token management, sandbox environment for testing

**API Gateway Requirement** (CRITICAL):
- If human users OR external APIs → api_gateway service **MUST** exist in architecture
- Gateway **MUST be fully implemented** (not orphaned/scaffolding)
- Responsibilities: Single entry point (`https://api.example.com`), auth enforcement, rate limiting, request validation, SSL/TLS, CORS, request ID tracking

**Validation**: Step SE-03-A07 (manual review + automated checks) - **BLOCKING GATE**

**Common Issues**:
- Inconsistent API design (mixed naming conventions) → Developer confusion
- Poor error messages ("500 Internal Server Error" vs "Email is required. Please provide your email.") → Users can't recover
- Missing API documentation (no OpenAPI, no examples) → Can't use API
- No API gateway → Inconsistent auth, can't enforce rate limits, poor observability
- **api_gateway defined but not implemented (orphaned service)** → **CRITICAL** - system non-functional
- Unclear versioning (query params/headers vs URL path) → Hard to discover

**User Experience Targets**:
- **Time to first success**: < 5 minutes for new user
- **API time to first call**: < 5 minutes from reading docs
- **Task success rate**: > 95% complete common tasks without support
- **Error recovery**: Errors provide actionable guidance, not just failure messages

### 🎯 Orphaned Service Detection (UAF Systems)

**Problem**: Services defined in architecture but never implemented (scaffolding only)

**Example**: API gateway defined with `service_architecture.json` but only contains empty scaffolding code → System fails because gateway doesn't route requests

**Detection**: Step SE-06 - System of Systems Graph Analysis
```bash
python3 system_of_systems_graph_v2.py index.json --analyze-issues
```

**Checks**:
- Services with architecture files but no implementation directory
- Services with implementation directory but only scaffolding (< 50 lines, no functions/classes)
- Reports as `unimplemented_services` in `architectural_issues.unimplemented_services`

**Prevention**:
- Mark critical services (especially api_gateway) as mandatory in architecture
- Validate implementation exists before proceeding to testing/deployment
- Use CI/CD checks to ensure no orphaned services

### 📋 IT System Requirements Checklist

Before proceeding from SE-03 validation gate, verify:

**For UAF with Human Users OR External APIs**:
- [ ] `security_architecture.json` created with authentication, authorization, rate limiting, encryption, audit logging
- [ ] `deployment_architecture.json` created with one-command deployment, health checks, monitoring
- [ ] `ux_api_design.json` created with API standards, error handling, documentation requirements
- [ ] API gateway service exists in architecture and will be fully implemented (not orphaned)
- [ ] All three validated in SE-03-A05, SE-03-A06, SE-03-A07 (BLOCKING)

**For UAF IT Systems (All)**:
- [ ] `port_registry.json` created and validated (no port conflicts)
- [ ] Health check endpoints defined (`/health`, `/ready`) for all services
- [ ] Deployment documented in README with step-by-step instructions

**Rationale**: These requirements are NOT optional polish - they are fundamental to IT system success in modern, interconnected environments. Designing security, deployment ease, and UX upfront prevents expensive retrofitting and ensures competitive advantage.

## Operational Environment Design (UAF/IT Systems Going to Production) - CRITICAL!

### ⚠️ Systems Don't Operate in Vacuums - Design for Reality UPFRONT

**CRITICAL PRINCIPLE**: Operational environment is an **ARCHITECTURAL DECISION** made during systems engineering, NOT an operational problem solved during testing.

**User Quote**: "The real operational environment must be considered upfront in designing the system. Most systems function in a world that affects the system indirectly or directly - systems rarely operate in a benign, vacuum environment. Typically, this causes huge budget overages and costly delays in a program."

**Two-Phase Relationship**:
1. **Systems Engineering Phase (NOW)**: Design for real operational environment, decide which tests needed, establish success criteria
2. **Testing Phase (Later)**: Execute tests planned during SE phase, validate system survives operational conditions

**Testing phase does NOT define new tests** - those are architectural decisions made NOW.

### 🌍 Real Operational Environment Conditions

Systems will face (design for these, don't hope they won't happen):
- **Network failures and partitions** → Circuit breakers, timeouts, retries
- **Resource exhaustion** (CPU, memory, disk) → Resource limits, graceful degradation
- **Cascading failures** → Bulkheads, fail-fast, rate limiting
- **Traffic spikes** → Auto-scaling, queuing, caching
- **Security attacks** (DDoS, injection, credential stuffing) → WAF, rate limiting, input validation
- **Data corruption** → Validation, checksums, backup/restore
- **Third-party outages** → Fallbacks, circuit breakers, cached responses
- **Configuration drift** → IaC, validation, immutable infrastructure

### 📋 10 IT-Specific Operational Considerations (UPFRONT Design)

**Applicability**: UAF/IT systems going to production

**When**: Step SE-02-A08 (during architecture design)

**Template**: `operational_environment_template.json` (1100+ lines)

**The 10 Considerations**:

1. **Service Decomposition & Boundaries**
   - DDD bounded contexts, single responsibility per service
   - Data ownership (dedicated DB per service, no shared databases)
   - Inter-service communication (synchronous REST vs asynchronous events)
   - **Why upfront**: Service boundaries affect scalability, deployment independence, team organization - can't be easily changed

2. **Containerization & Packaging**
   - Docker from day one, multi-stage Dockerfiles
   - Orchestration choice (ECS vs EKS vs docker-compose) - justify simplicity vs features
   - Image scanning (Trivy, Snyk), base image selection
   - **Why upfront**: Determines deployment portability, environment consistency, CI/CD pipeline design

3. **Infrastructure as Code & Automation**
   - Ansible for deployment automation (deploy.yml, rollback.yml, provision.yml)
   - Terraform for AWS provisioning (VPCs, EC2, RDS, S3)
   - Environment separation (dev/staging/prod in separate VPCs or AWS accounts)
   - **Why upfront**: Enables reproducible deployments, disaster recovery, prevents manual configuration errors

4. **CI/CD Pipeline Integration**
   - Git workflow (gitflow, trunk-based), pipeline stages (build, test, deploy)
   - Automated testing strategy (unit, integration, security, performance)
   - Semantic versioning, secrets injection
   - **Why upfront**: Pipeline design determines deployment velocity, quality gates, rollback speed

5. **Scalability & Resilience**
   - Horizontal scaling (auto-scaling groups, target tracking)
   - Circuit breakers (Resilience4j), retries with exponential backoff, timeouts
   - Bulkheads, state management (stateless services, external state storage)
   - **Why upfront**: Resilience patterns prevent cascading failures - design for 10x growth from start

6. **Security & Compliance**
   - IAM roles (not hard-coded credentials), Secrets Manager
   - VPC design (public/private subnets), security groups, WAF
   - Encryption (TLS 1.2+, KMS), compliance (GDPR, HIPAA, PCI-DSS)
   - **Why upfront**: Security architecture determines compliance eligibility, audit capabilities - retrofitting is expensive

7. **Monitoring, Logging, Observability**
   - Metrics (Prometheus /metrics endpoint), structured JSON logging
   - Correlation IDs (request_id for tracing), distributed tracing
   - Alerting (critical vs warning), dashboards, performance baselines
   - **Why upfront**: Observability strategy determines debuggability, incident response time - no observability = blind operations

8. **Service Discovery & Networking**
   - Discovery mechanism (AWS Cloud Map, Consul, Kubernetes DNS)
   - API Gateway (single entry point), latency optimization (same VPC/AZ)
   - CDN, connection pooling
   - **Why upfront**: Service discovery enables dynamic scaling - hardcoded IPs break auto-scaling

9. **Cost Management & Optimization**
   - Right-sizing instances, spot instances, reserved instances
   - Auto-scaling to zero (non-prod), serverless options (Lambda, Fargate)
   - Tagging for cost allocation
   - **Why upfront**: Cost optimization designed in prevents runaway cloud costs

10. **Testing & Rollback Strategies**
    - Define which tests to run (unit, integration, performance, security, chaos, operational)
    - Canary deployments, feature flags, backup/DR, rollback procedures
    - **Why upfront**: Testing strategy defined NOW determines quality gates - testing phase executes this plan

### 🧪 Testing Strategy Defined During SE Phase

**IMPORTANT**: Testing phase (workflow 04) executes tests defined here - it does NOT invent new tests.

**Test Types to Plan**:
- **Unit Tests**: 80% coverage, run on every commit
- **Integration Tests**: Service interactions via real APIs/databases in isolated environment
- **Performance Tests**: Load at 2x, 5x, 10x traffic; success criteria: p95 < 500ms at 5x
- **Security Tests**: OWASP Top 10, penetration testing, dependency scanning
- **Chaos Tests**: Inject failures (kill instances, network latency, resource exhaustion)
- **Operational Tests**: Multi-AZ failover, database failover, auto-scaling, backup/restore

**Success Criteria Established NOW**:
- Availability target: 99.9%, 99.95%, 99.99%?
- Recovery Time Objective (RTO): 1 hour, 4 hours?
- Recovery Point Objective (RPO): 15 minutes, 1 hour data loss?
- Performance baselines: p50 < 100ms, p95 < 500ms, p99 < 1000ms

### ✅ Operational Environment Validation (SE-03-A08) - BLOCKING

Before proceeding from SE-03, validate:
- [ ] All 10 considerations addressed (not TBD or "will decide later")
- [ ] Real-world failure conditions explicitly designed for (not ideal conditions)
- [ ] Testing strategy complete with test types and success criteria defined
- [ ] Concrete technology choices made (not just "we'll use monitoring")
- [ ] Relationship between SE phase (design) and testing phase (execute) clear
- [ ] Design focuses on scalability, reliability, security, maintainability for production

**Cost Impact**: NOT considering operational environment upfront causes **budget overages and costly program delays**. Retrofitting production-readiness is **10-100x more expensive** than designing for it.

## Port Management (UAF/IT Systems ONLY)

### ⚠️ Applicability: Information Technology Systems Only

**Port management applies ONLY to**:
- ✅ UAF framework (IT systems with network services)
- ✅ Custom frameworks modeling networked IT systems

**Port management does NOT apply to**:
- ❌ Systems Biology (gene networks don't have ports)
- ❌ Social Network Analysis (social graphs don't have ports)
- ❌ Ecological Systems (food webs don't have ports)
- ❌ Complex Adaptive Systems (abstract models don't have ports)

**How to check**: Read `framework_registry.json` → `frameworks[framework_id].deployment_characteristics.port_management_applicable`
- If `true` → Execute SE-02-A04 (port assignment) and SE-03-A04 (port validation)
- If `false` → Skip both actions, proceed to next step

---

### Problem: Port Conflicts in Deployment (UAF Systems)

**Common Issue**: IT services fail to start with "Address already in use" because:
- Previous containers not shutdown (leftover from testing)
- Multiple services assigned same port
- Conflicts with well-known ports (PostgreSQL 5432, Redis 6379, etc.)

**Solution**: Architectural port management during SE phase, NOT operational fixing during deployment!

### Port Assignment (Step SE-02-A04)

**When**: During Systems Engineering workflow, after creating service architectures

**Process**:
1. **Categorize services**:
   - Application services (user-facing APIs) → 8000-8099
   - Internal services (background workers) → 8100-8199
   - Data services (databases, caches) → 8200-8299
   - Infrastructure (monitoring, logging) → 8300-8399

2. **Assign sequential ports**:
   - First app service → 8000
   - Second app service → 8001
   - First internal service → 8100
   - etc.

3. **Update architecture files**:
   - `service_architecture.json` → `deployment.ports.primary.port`
   - Create `specs/machine/port_registry.json` (centralized mapping)

4. **Validate** (Step SE-03-A04):
   ```bash
   python3 validate_port_registry.py <system_root>/specs/machine/port_registry.json
   ```

### Port Registry Structure

**Location**: `specs/machine/port_registry.json`

**Key sections**:
- `port_ranges`: Allocation strategy by service category
- `service_ports`: Each service's primary, metrics, admin ports
- `port_conflict_detection`: Validation rules (PC-01 through PC-05)
- `docker_compose_generation`: How to generate docker-compose.yml

**Example entry**:
```json
{
  "character_service": {
    "service_name": "Character Service",
    "classification": "application",
    "ports": {
      "primary": {
        "port": 8000,
        "protocol": "HTTP",
        "purpose": "REST API",
        "binding": "0.0.0.0",
        "public_facing": true,
        "docker_mapping": {
          "host_port": 8000,
          "container_port": 8000
        }
      },
      "metrics": {
        "port": 9000,
        "protocol": "HTTP",
        "purpose": "Prometheus metrics"
      }
    }
  }
}
```

### Validation Rules

**PC-01**: No duplicate primary ports (ERROR - blocking)
**PC-02**: No port overlap between services (ERROR - blocking)
**PC-03**: Ports within designated ranges (WARNING)
**PC-04**: Avoid privileged ports <1024 (WARNING)
**PC-05**: Docker host/container port consistency (INFO)

### Troubleshooting Port Conflicts

**"Address already in use"**:
```bash
# Find what's using the port
docker ps | grep <service>
netstat -tlnp | grep <port>  # Linux
lsof -i :<port>              # Mac

# Fix
docker-compose down          # Stop all containers
kill -9 <PID>                # Kill specific process
# Update port_registry.json and reassign conflicting port
```

**Service can't connect to another service**:
- In docker-compose: Use service name, NOT localhost: `http://character_service:8000`
- Verify docker network: `docker network inspect <network>`
- Check port_registry.json for correct port assignment

## Common Patterns

### Pattern 1: Web-Based New Greenfield System (PRIMARY)

**User Journey:**
```
Day 1: Initial Setup and Architecture
1. User creates GitHub repo: github.com/yourname/smart_home_system
2. User adds README with system description
3. User opens GitHub Codespaces or Claude Code (https://claude.ai/code)
4. User: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
         on system in github.com/yourname/smart_home_system"
5. LLM agent executes setup, framework selection, initial architecture
6. All context saved in github.com/yourname/smart_home_system/context/working_memory.json

Day 2: Continue Systems Engineering
1. User opens Codespaces or Claude Code (conversation persists in code environments!)
2. User: "Continue workflow from context/working_memory.json
         in github.com/yourname/smart_home_system"
3. LLM agent reads context, resumes from exact step
4. Continue through systems engineering workflow

Days 3-N: Development and Operations
1. Same pattern: open code environment, "continue workflow from context/working_memory.json"
2. LLM agent always reads context first, knows exactly where project is
3. Progress through: 01-systems_engineering → 02-artifacts_visualization →
   03-development → 04-testing_operations

Result: Fully designed, documented, implemented system - never touched local machine
```

**LLM Agent Best Practices:**
1. **ALWAYS** read `context/working_memory.json` first when user says "continue"
2. Check `current_workflow` and `current_step` to know where to resume
3. Update context after each operation
4. Commit changes to GitHub after major milestones
5. Reference conversation history if available (code environments store this)
6. **IMPORTANT**: Regular chat interfaces (claude.ai chat, chatgpt, gemini) likely won't work - need code execution environment

### Pattern 2: Web-Based Architecture-Only (No Code)

**User Journey:**
```
Day 1: Setup and Architecture Design
1. User creates GitHub repo with system description
2. User: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
         on system in github.com/yourname/my_system"
3. Progress through systems engineering workflow

Day 2: Documentation and Visualization
1. User: "Continue workflow from context/working_memory.json in github.com/yourname/my_system"
2. At 02-artifacts_visualization, choose "architecture-only" option
3. Generate diagrams, ICDs, documentation
4. STOP after workflow 02 (do not proceed to development)

Result: Complete architecture specs, diagrams, ICDs - no service code
Progression: 00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → END
```

### Pattern 3: Resuming After Break (Critical Pattern!)

**Scenario**: User worked on project 3 days ago, wants to continue

**User Message:**
```
"Continue workflow from context/working_memory.json in github.com/yourname/my_system"
```

**LLM Agent Process:**
```
1. Read github.com/yourname/my_system/context/working_memory.json
2. Extract:
   - current_workflow: "01-systems_engineering"
   - current_step: "SE-02-A03"
   - paths: reflow_root, system_root
   - operations_since_refresh: 5
3. Check if context refresh needed (>4 operations → refresh)
4. Load current workflow: github.com/sligara7/reflow/workflows/01-systems_engineering.json
5. Resume from SE-02-A03
6. Update context after each operation
7. Commit to GitHub at milestones
```

**CRITICAL**: Context folder IS the source of truth. Conversation history is supplemental.

### Pattern 4: Feature Update (Existing System)

**Web-Based:**
```
User: "Implement workflow in github.com/sligara7/reflow/workflows/feature_update.json
       on system in github.com/yourname/my_system"

Process:
1. Read existing architecture from system repo
2. Propose changes, validate impact
3. Update architecture with versioning
4. Generate updated ICDs, diagrams
5. Commit to GitHub

Result: Updated system with backward compatibility tracking
```

### Pattern 5: Local Machine (ALTERNATIVE - if web not available)

<details>
<summary>Click to expand local patterns</summary>

```
1. Clone reflow: git clone https://github.com/sligara7/reflow
2. Create system directory: mkdir ~/projects/my_system
3. Start workflow: "Implement workflow in /home/user/dev/reflow/workflows/00-setup.json
                    on system in ~/projects/my_system"
4. Resume work: "Continue workflow from context/working_memory.json in ~/projects/my_system"
5. Result: Fully designed, documented, and optionally implemented system
```

</details>

## Multi-Language Support

Reflow supports:
- Python, Java, TypeScript, Go, Rust
- System-agnostic architecture patterns
- Language-specific development steps in workflow 03

## Getting Help

- **README.md** - Overview and quick start
- **docs/TOOL_USAGE_SUMMARY.md** - **NEW v3.3.1** - Comprehensive guide to all 16 tools
- **docs/TOOL_VERSION_MANIFEST.md** - **NEW v3.3.1** - Tool version history
- **docs/RELEASE_NOTES_v3.3.1.md** - **NEW v3.3.1** - Latest release notes
- **docs/restructuring/NEW_STRUCTURE_README.md** - Quick reference
- **docs/restructuring/RESTRUCTURING_DESIGN.md** - Design rationale
- **docs/restructuring/MIGRATION_GUIDE.md** - v2.x to v3.0 migration
- **docs/GIT_AUTOMATION_GUIDE.md** - Git automation setup and usage
- **docs/DEVELOPMENT_RESEARCH_FEATURE.md** - Development best practices research

## Architecture Framework

Reflow is based on:
- **UAF 1.2** (Unified Architecture Framework)
- Systems engineering best practices
- Clean architecture principles
- Automated validation and quality gates

## New Features (v3.0.1 - October 2024)

### 🔄 Git Automation (OPTIONAL)

**Step**: S-03-A06 in `00-setup.json`

Reflow can automatically commit and push your work to a git repository at key milestones:

- **When**: Optional setup during S-03-A06
- **Asks user**: "Would you like to enable automatic git commits?"
- **If Yes**: Configure git remote, branch, and author
- **Commits**: ~36 automatic commits throughout workflows at logical checkpoints
- **Benefits**: Automatic backup, version history, collaboration, recovery

**Commit schedule**:
- After each service architecture (SE-02)
- After system graph validation (SE-06)
- After documentation generation (AV-03)
- After each service implementation (D-03)
- After CI/CD setup (TO-02)

**Documentation**: See `docs/GIT_AUTOMATION_GUIDE.md` for complete details

---

### 🔍 Development Best Practices Research (OPTIONAL)

**Step**: D-01-A00 in `03-development.json`

Before setting up development tooling, optionally research current industry standards:

- **When**: Optional at start of D-01
- **Asks user**: "Would you like to research current best practices?"
- **Time**: 5-10 minutes (quick search, top results)
- **Research areas**: Dependency management, containers, CI/CD, security, testing, linting, observability, build systems
- **Output**: `context/development_tooling_research_{date}.md`
- **Benefits**: Use modern tools (poetry vs requirements.txt, ruff vs pylint, etc.)

**Example findings**:
- Python: Use poetry/hatchling instead of requirements.txt
- JavaScript: Use pnpm/yarn instead of npm
- Linting: Use ruff (10-100x faster than alternatives)

**Documentation**: See `docs/DEVELOPMENT_RESEARCH_FEATURE.md`

---

### 🏗️ Enhanced Architecture Validation

**Step**: SE-06 in `01-systems_engineering.json`

The `system_of_systems_graph.py` tool now detects architectural consistency issues:

- **New detection**: Async/sync framework mismatches
- **Checks**: Async HTTP services (uvicorn) should use async database drivers (asyncpg, motor)
- **Output**: `specs/machine/architecture_issues.json` with structured recommendations
- **Severity levels**: Critical, Warning, Info
- **Benefits**: Catch architecture problems early, before implementation

**Example issue detected**:
```json
{
  "node": "character_service",
  "description": "Uses async HTTP but database driver not specified",
  "severity": "info",
  "recommendation": "Use asyncpg or async SQLAlchemy"
}
```

**Catches issues like**:
- Mixing sync database with async HTTP (blocks event loop)
- Circular dependencies between services
- Missing interface definitions
- Security boundary violations

---

## Summary for LLM Agents

### Primary Approach: Web-Based Usage

1. **Web-based is PRIMARY**: Users create GitHub repo, you read from `github.com/sligara7/reflow` and write to their repo
2. **Context is SOURCE OF TRUTH**: ALWAYS read `context/working_memory.json` FIRST when user says "continue"
3. **Multi-day projects are normal**: User may work for 10 minutes today, resume 3 days later - context preserves state
4. **Two context mechanisms**:
   - `context/working_memory.json` in system repo (PRIMARY - read this first!)
   - Conversation history in web service (SUPPLEMENTAL - reference if user mentions)
5. **Reflow is read-only reference**: Read workflows/templates from GitHub, never modify them
6. **Your system is separate**: All work happens in user's system repo (`github.com/username/system_name`)
7. **Start with 00-setup**: First workflow configures paths, framework, structure
8. **6 workflows in sequence**: 00-setup → 01-systems_engineering → 02-artifacts_visualization → 03-development → 04-testing_operations (+ feature_update)
9. **Quality gates enforced**: 10 gates (7 blocking) ensure quality before advancing
10. **v3.3.1 is current**: Streamlined tooling (16 tools), comprehensive documentation, operational environment design, IT requirements, versioning

### Secondary Approach: Local Machine

Local usage is alternative if user explicitly requests it or web not available.

---

**Ready to Start (Web-Based)?**

```
User creates GitHub repo, then in a code environment (Codespaces, Claude Code, etc.) says:
"Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
 on system in github.com/yourname/your_system_repo"
```

**Web-Based Environment Options:**
- **GitHub Codespaces** (most accessible - free tier available)
- **Claude Code** (https://claude.ai/code - requires Pro/Max)
- **OpenAI Codex, Google Jules, Gitpod, Replit**

**⚠️ Don't Use**: Regular chat interfaces (claude.ai chat, chatgpt, gemini) - they lack code execution and GitHub integration

**Resuming Work (Multi-Day Projects)?**

```
User says:
"Continue workflow from context/working_memory.json in github.com/yourname/your_system_repo"

Your process:
1. Read context/working_memory.json from their repo
2. Check current_workflow and current_step
3. Resume from exact step
4. Update context after operations
```

**Local Machine (Alternative)?**

```
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system"
```

Good luck building complex systems! 🚀
