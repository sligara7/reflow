# Reflow - LLM Agent Guide

**Version**: 3.3.1
**Last Updated**: 2025-10-25

## What is Reflow?

Reflow is a **framework-agnostic systems engineering workflow** designed for LLM agents to design, architect, and develop complex systems across multiple domains. Provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

**NEW in v3.1.0**: Support for 6+ architectural frameworks - UAF 1.2, Systems Biology, Social Network Analysis, Ecological Systems, Complex Adaptive Systems, Decision Flow, and Custom frameworks.

## Critical Information for LLM Agents

### ⚠️ Version 3.0 Structure

**Active (v3.0)**:
- ✅ `workflows/*.json` - 6 separate workflow files
- ✅ `workflow_steps/*/` - Step definitions by workflow
- ✅ `workflows_master_index.json` - Workflow routing

**Archived (DO NOT USE)**:
- ❌ `docs/archive/decision_flow.json.old` - Old monolithic workflow

### 🔑 Key Distinction: Tooling vs System

1. **Reflow Tooling** (READ ONLY): `/path/to/reflow/` - workflows, tools, templates
2. **Your System** (WRITABLE): Separate directory for your architecture/code

## Getting Started

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

### The 6 Workflows (In Order)

```
00-setup.json                    → Setup, framework selection (10-15 min)
01-systems_engineering.json      → Architecture design (2-4 hours)
02-artifacts_visualization.json  → ICDs, diagrams (1-2 hours)
03-development.json              → Service implementation (days-weeks)
04-testing_operations.json       → CI/CD, testing (1-2 weeks)
feature_update.json              → Update existing systems
```

## Workflow Progression

### Typical New System Flow

1. **Start**: Run `00-setup.json`
   - Configure paths (reflow_root, system_root)
   - Select architectural framework (S-01A)
   - Create directory structure
   - Initialize `context/working_memory.json`

2. **Architecture**: Run `01-systems_engineering.json`
   - **NEW: Automatic Approach Detection (SE-00)** - LLM examines system directory
   - **If existing components found** → Bottom-up integration (BU-01 through BU-06)
     - Component inventory, gap analysis, exact code-level deltas
   - **If empty/greenfield** → Top-down design (SE-01 through SE-06)
     - Service identification, architecture design, validation
   - Both approaches merge at common validation steps

3. **Documentation**: Run `02-artifacts_visualization.json`
   - Generate ICDs, Mermaid diagrams
   - Create versioned documentation

4. **Build** (optional): Run `03-development.json`
   - Implement services
   - 80% test coverage required

5. **Deploy** (optional): Run `04-testing_operations.json`
   - CI/CD, Docker Compose, operational testing

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
00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → DONE
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

**Key fields**:
```json
{
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "paths": {
    "reflow_root": "/path/to/reflow",
    "system_root": "/path/to/your_system"
  },
  "operations_since_refresh": 2
}
```

**Rules**:
- Read before every step
- Update after completing actions
- Refresh context every 4 operations

### Architecture Versioning

```
service_architecture_v1.0.0-20251024.json    ← Versioned file
service_architecture.json                     ← Symlink to current
```

**Benefits**: Complete history, rollback support, version manifest tracking

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

**16 Python tools** (see `docs/TOOL_USAGE_SUMMARY.md`):

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

### ⚠️ Design Upfront, Not Retrofit

**IMPORTANT**: IT systems with human users/external APIs **MUST** address upfront (not afterthoughts):

1. **Security** - Authentication, authorization, encryption, audit logging
2. **Deployment Ease** - One-command deployment, automated rollback
3. **User Experience** - Intuitive APIs, clear errors, documentation

**Rationale**: Retrofitting after launch is **10-100x more expensive** than designing correctly upfront.

**When**: Steps SE-02-A05 through SE-02-A08 during architecture design

### Security Architecture (SE-02-A05)

**Applicability**:
- ✅ UAF with human users (web/mobile apps)
- ✅ UAF with external API access
- ❌ Internal machine-to-machine only

**Template**: `security_architecture_template.json`

**Required Sections**:
- Authentication (JWT/OAuth2/SAML), MFA for admins
- Authorization (RBAC/ABAC), roles, permissions
- **API Gateway** (MANDATORY for human-facing) - single entry, auth, rate limits, SSL/TLS
- Rate limiting (e.g., 100 req/min per user, 5 login attempts per 15 min)
- Input validation (XSS prevention, SQL injection prevention)
- Encryption (TLS 1.2+ in-transit, AES-256 at-rest, KMS/Vault)
- Audit logging (auth attempts, data access, admin actions)

**API Gateway Requirement**:
- IF human users OR external APIs → api_gateway **MUST** exist
- Gateway must be **fully implemented** (not orphaned scaffolding)
- Checked in SE-06 orphaned service detection

**Validation**: SE-03-A05 (BLOCKING)

**Common Issues**:
- Missing/orphaned API gateway → **CRITICAL**
- Weak auth (no MFA) → **HIGH RISK**
- No encryption at rest for sensitive data → **HIGH RISK**

### Deployment Architecture (SE-02-A06)

**Template**: `deployment_architecture_template.json`

**Philosophy - SIMPLICITY FIRST**:
- One-command deploy (`docker-compose up -d`)
- <10 min setup for new developer
- <5 min automated rollback
- Clear README with step-by-step instructions

**Required**:
- Containerization (Docker/Podman), image scanning
- Orchestration (Docker Compose default, K8s only if scale/HA needed)
- CI/CD (build → test → deploy, rollback on failure)
- Health checks (`/health`, `/ready`)
- Monitoring (Prometheus, centralized logging, alerting)
- Backup & DR (RTO/RPO targets)

**Validation**: SE-03-A06 (BLOCKING)

**Common Issues**:
- Overcomplicated orchestration → Slows iteration
- No health checks → Can't detect failures
- Manual deployment → Error-prone

### UX & API Design (SE-02-A07)

**Template**: `ux_api_design_template.json`

**Targets**:
- Time to first success: <5 min
- API time to first call: <5 min
- Task success rate: >95%

**Required**:
- RESTful design, consistent naming
- User-friendly errors ("Email is required" vs "500 Internal Server Error")
- **API Documentation** (MANDATORY) - OpenAPI spec, Swagger UI, code examples
- Versioning (URL path: `/api/v1/users`)
- Performance (p95 <500ms), caching

**Validation**: SE-03-A07 (BLOCKING)

**Common Issues**:
- Inconsistent naming → Developer confusion
- Poor error messages → Users can't recover
- Missing docs → Can't use API
- Orphaned API gateway → System non-functional

### Operational Environment Design (SE-02-A08)

**CRITICAL PRINCIPLE**: Operational environment is **ARCHITECTURAL DECISION** made NOW, NOT operational problem solved during testing.

**Template**: `operational_environment_template.json` (1100+ lines)

**Design for Reality** - Systems face:
- Network failures, partitions
- Resource exhaustion (CPU, memory, disk)
- Cascading failures
- Traffic spikes
- Security attacks (DDoS, injection, credential stuffing)
- Data corruption
- Third-party outages
- Configuration drift

**10 IT-Specific Considerations** (UPFRONT Design):

1. **Service Decomposition** - DDD bounded contexts, single responsibility, data ownership
2. **Containerization** - Docker from day one, multi-stage Dockerfiles, image scanning
3. **Infrastructure as Code** - Ansible (deploy.yml, rollback.yml), Terraform (AWS provisioning)
4. **CI/CD Integration** - Pipeline stages, automated testing, semantic versioning
5. **Scalability & Resilience** - Auto-scaling, circuit breakers, retries, timeouts, bulkheads
6. **Security & Compliance** - IAM roles, VPC design, encryption, GDPR/HIPAA/PCI-DSS
7. **Monitoring & Observability** - Prometheus metrics, structured logging, correlation IDs, alerting
8. **Service Discovery** - AWS Cloud Map, Consul, K8s DNS, API Gateway
9. **Cost Management** - Right-sizing, spot instances, auto-scale to zero (non-prod)
10. **Testing & Rollback** - Define test types NOW (unit, integration, perf, security, chaos, operational)

**Testing Strategy Defined NOW**:
- Unit: 80% coverage, every commit
- Integration: Real APIs/DBs in isolated env
- Performance: 2x/5x/10x load, p95 <500ms at 5x
- Security: OWASP Top 10, penetration testing
- Chaos: Inject failures (kill instances, network latency, resource exhaustion)
- Operational: Multi-AZ failover, DB failover, auto-scaling, backup/restore

**Success Criteria**:
- Availability: 99.9%, 99.95%, 99.99%?
- RTO: 1 hour, 4 hours?
- RPO: 15 min, 1 hour data loss?
- Performance: p50 <100ms, p95 <500ms, p99 <1000ms

**Validation**: SE-03-A08 (BLOCKING)

**Cost Impact**: NOT designing for ops upfront causes **budget overages and costly program delays**

### Orphaned Service Detection (UAF)

**Problem**: Services defined in architecture but never implemented (scaffolding only)

**Example**: API gateway defined with `service_architecture.json` but only empty scaffolding → System fails

**Detection**: SE-06 - `python3 system_of_systems_graph_v2.py index.json --analyze-issues`

**Checks**:
- Services with architecture but no implementation
- Services with implementation but only scaffolding (<50 lines, no functions/classes)
- Reports as `unimplemented_services` in `architectural_issues`

### IT System Requirements Checklist

Before proceeding from SE-03 validation gate:

**For UAF with Human Users OR External APIs**:
- [ ] `security_architecture.json` created
- [ ] `deployment_architecture.json` created
- [ ] `ux_api_design.json` created
- [ ] API gateway exists in architecture and will be fully implemented (not orphaned)
- [ ] All three validated in SE-03-A05, SE-03-A06, SE-03-A07 (BLOCKING)

**For UAF IT Systems (All)**:
- [ ] `port_registry.json` created and validated
- [ ] Health checks defined (`/health`, `/ready`)
- [ ] Deployment documented in README

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
- Check `current_workflow` and `current_step` to know where to resume
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
2. Extract: `current_workflow`, `current_step`, `paths`, `operations_since_refresh`
3. Check if refresh needed (>4 operations → refresh)
4. Load workflow: `github.com/sligara7/reflow/workflows/{current_workflow}.json`
5. Resume from exact step
6. Update context after operations
7. Commit to GitHub at milestones

**CRITICAL**: Context folder IS the source of truth. Conversation history is supplemental.

### Pattern 4: Feature Update

```
"Implement workflow in github.com/sligara7/reflow/workflows/feature_update.json on system in github.com/yourname/my_system"

Process: Read existing architecture → Propose changes → Validate impact → Update with versioning → Generate updated ICDs/diagrams
Result: Updated system with backward compatibility tracking
```

## What to Avoid vs Do

**❌ Don't**:
- Modify reflow tooling files (workflows, templates, tools)
- Use archived v2.x files
- Skip setup workflow
- Mix reflow and system directories
- Skip quality gates

**✅ Do**:
- Reference reflow as read-only library
- Work in your system directory
- Follow workflow sequence
- Use versioning (semver, symlinks)
- Run validation tools before advancing

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

- `docs/TOOL_USAGE_SUMMARY.md` - Comprehensive guide to all 16 tools
- `docs/NETWORKX_ANALYSIS_GUIDE.md` - NetworkX analysis guide (400+ lines)
- `docs/DECISION_FLOW_FRAMEWORK.md` - Decision Flow example (500+ lines)
- `docs/GIT_AUTOMATION_GUIDE.md` - Git automation setup
- `README.md` - Overview and quick start

## Summary for LLM Agents

### Primary Approach: Web-Based Usage

1. **Web-based is PRIMARY**: Users create GitHub repo, you read from `github.com/sligara7/reflow`, write to their repo
2. **Context is SOURCE OF TRUTH**: ALWAYS read `context/working_memory.json` FIRST when user says "continue"
3. **Multi-day projects normal**: User may work 10 min today, resume 3 days later - context preserves state
4. **Two context mechanisms**:
   - `context/working_memory.json` (PRIMARY - read this first!)
   - Conversation history (SUPPLEMENTAL - reference if user mentions)
5. **Reflow is read-only**: Read workflows/templates from GitHub, never modify them
6. **Your system is separate**: All work in user's repo (`github.com/username/system_name`)
7. **Start with 00-setup**: Configures paths, framework, structure
8. **6 workflows in sequence**: 00-setup → 01-SE → 02-artifacts → 03-dev → 04-test (+ feature_update)
9. **Quality gates enforced**: 10 gates (7 blocking) ensure quality before advancing
10. **v3.3.1 current**: 16 tools, comprehensive documentation, operational environment design, IT requirements, versioning

### Secondary Approach: Local Machine

Use if user explicitly requests or web not available.

---

**Ready to Start (Web-Based)?**

```
User creates GitHub repo, then in code environment (Codespaces, Claude Code, etc.) says:
"Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
 on system in github.com/yourname/your_system_repo"
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
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system"
```

Good luck building complex systems! 🚀
