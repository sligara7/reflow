# Reflow - LLM Agent Guide

**Version**: 3.1.0
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

### 1. Quick Start Command

Tell your LLM agent:
```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system
```

**Example**:
```
Implement workflow in /home/user/dev/reflow/workflows/00-setup.json on system in /home/user/projects/smart_home
```

### 2. The 6 Workflows (In Order)

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

Reflow provides **23 Python tools** including:

**Architecture** (Framework-Agnostic):
- `validate_architecture.py` - Validate architecture files against framework schemas
- `system_of_systems_graph_v2.py` - **NEW!** Framework-agnostic graph generation with:
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
- `system_of_systems_graph.py` - Legacy tool (v1, UAF-only, still works for backward compatibility)
- `generate_interface_contracts.py` - Create ICDs from architecture

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

## Port Management (CRITICAL for UAF Systems!)

### Problem: Port Conflicts in Deployment

**Common Issue**: Services fail to start with "Address already in use" because:
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

### Pattern 1: New Greenfield System
```
1. Create system directory: mkdir ~/projects/my_system
2. Start workflow: "Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system"
3. Progress through all 5 workflows sequentially
4. Result: Fully designed, documented, and optionally implemented system
```

### Pattern 2: Architecture-Only (No Code)
```
1. Run 00-setup
2. Run 01-systems_engineering
3. Run 02-artifacts_visualization (choose "architecture-only" option)
4. Result: Complete architecture specifications and documentation
```

### Pattern 3: System-of-Systems Integration
```
1. Run 00-setup
2. For multi-system integration, may use S-04-SystemOfSystems.json step
3. Run standard workflows
4. Result: Unified architecture for multiple integrated systems
```

### Pattern 4: Feature Update
```
1. Use feature_update.json workflow
2. Propose changes, validate impact
3. Update architecture with versioning
4. Result: Updated system with backward compatibility tracking
```

## Multi-Language Support

Reflow supports:
- Python, Java, TypeScript, Go, Rust
- System-agnostic architecture patterns
- Language-specific development steps in workflow 03

## Getting Help

- **README.md** - Overview and quick start
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

1. **Reflow is a library**: Read-only reference, don't modify
2. **Your system is separate**: Work happens in your system directory
3. **Start with 00-setup**: Always configure paths first
4. **6 workflows in sequence**: Follow the progression
5. **Optional features available**: Git automation, development research, enhanced validation
6. **Context is critical**: Maintain working_memory.json
7. **Versioning matters**: Use semantic versioning for architecture
8. **Quality gates enforced**: Validate before advancing
9. **v3.0.1 is current**: Ignore archived v2.x files

---

**Ready to Start?**

```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system
```

Good luck building complex systems! 🚀
