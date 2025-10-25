# Reflow - Systems Engineering Workflow

[![Version](https://img.shields.io/badge/version-3.3.0-blue.svg)](https://github.com/anthropics/reflow)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Frameworks](https://img.shields.io/badge/frameworks-6%2B-green.svg)](#supported-frameworks)

A **framework-agnostic** systems engineering workflow for LLM agents to design, architect, and develop complex systems. Model software systems (UAF), biological networks, social systems, ecosystems, and more.

**:tada: Version 3.3.0** - Production-ready systems from day one! Design for real operational environments UPFRONT - not as an afterthought.

---

## :book: Table of Contents

- [Quick Start](#quick-start)
- [Supported Frameworks](#supported-frameworks)
- [The 5 Workflows](#the-5-workflows)
- [Key Benefits](#key-benefits)
- [Directory Structure](#directory-structure)
- [What You Get](#what-you-get)
- [Usage Patterns](#common-usage-patterns)
- [Documentation](#documentation)
- [Requirements](#requirements)
- [Version History](#version-history)
- [Contributing](#contributing)
- [License](#license)

## :rocket: Quick Start

### :cloud: Web-Based (Recommended)

**Never touches your local machine - everything in the cloud!**

#### 1. Create Your System Repo on GitHub
```
1. Go to github.com → New Repository
2. Name: my_system (or smart_home_system, etc.)
3. Add README with system description:
   - What system you want to engineer
   - High-level requirements and goals
   - Any existing systems to integrate
4. Create repository
```

#### 2. Open in Web-Based Environment

**Option A: GitHub Codespaces** - Most Accessible
```
1. Open your system repo on github.com
2. Click "Code" → "Codespaces" → "Create codespace"
3. In terminal: git clone https://github.com/sligara7/reflow
4. Install Claude Code CLI or use web-based AI code editor in another tab
5. Say: "Implement workflow in /workspaces/reflow/workflows/00-setup.json
   on system in /workspaces/my_system"
```
- **Cost**: Free tier available (60 hours/month), then ~$0.18/hour
- **Requirements**: GitHub account

**Option B: Claude Code (Web)** - Anthropic's Web IDE
```
1. Go to https://claude.ai/code (requires Claude Pro or Max subscription)
2. Start new project
3. Say: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
   on system in github.com/yourname/my_system"
4. Claude Code reads both repos and executes workflow
```
- **Cost**: Claude Pro ($20/month) or Max subscription required
- **Requirements**: Claude Pro/Max subscription, GitHub integration

**Option C: Other Web-Based Code Environments**
- **OpenAI Codex**: Similar functionality (subscription required)
- **Google Jules**: Google's code environment (subscription/requirements vary)
- **Gitpod**: Alternative to Codespaces (gitpod.io)
- **Replit**: Web-based IDE (replit.com)

**⚠️ Note**: Regular chat interfaces (claude.ai chat, chatgpt.com, gemini.google.com) likely **won't work** - you need a code execution environment with GitHub integration.

#### 3. Progress Through Workflows
After setup, continue with:
```
00-setup → 01-systems_engineering → 02-artifacts_visualization →
03-development → 04-testing_operations
```

#### 4. Resuming Work (Next Day/Session)
Your system repo has a `context/` folder that tracks progress:
```
"Continue workflow from context/working_memory.json in github.com/yourname/my_system"
```
The context folder remembers:
- Which workflow you're on
- Which step you're at
- All paths and configurations
- Operations since last refresh

**Web-based services store conversations** - you can also reference previous chat history!

---

### :computer: Local Machine (Alternative)

<details>
<summary><b>Click to expand local machine instructions</b></summary>

#### 1. Clone Reflow
```bash
git clone https://github.com/sligara7/reflow
cd reflow
```

#### 2. Create System Folder
```bash
mkdir ~/projects/my_system
echo "Smart Home System - integrate lighting, security, HVAC" > ~/projects/my_system/system_description.txt
```

#### 3. Start Workflow
With Claude Code CLI or VS Code with Claude/GPT:
```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system
```

#### 4. Resuming Work
```
Continue workflow from context/working_memory.json in ~/projects/my_system
```

</details>

## :globe_with_meridians: Supported Frameworks

Reflow is **framework-agnostic** - it works with multiple architectural frameworks across different domains. All frameworks map to the same core abstraction: **nodes (components) + edges (connections)**.

### :desktop_computer: UAF 1.2 - Unified Architecture Framework (Default)
- **Best for**: Software systems, hardware, enterprise architecture, defense systems
- **Nodes**: Services, components
- **Edges**: Interfaces, dependencies
- **Examples**: Microservices, IoT systems, DoDAF architectures
- **Standard**: ISO/IEC 19540-1:2022

### :dna: Systems Biology Framework
- **Best for**: Gene networks, metabolic pathways, protein interactions, ecosystems
- **Nodes**: Genes, proteins, metabolites, species, populations
- **Edges**: Activation, inhibition, catalysis, predation, mutualism
- **Examples**: p53 regulatory network, glycolysis pathway, food webs
- **Analysis**: Boolean networks, ODEs, agent-based models

### :busts_in_silhouette: Social Network Analysis (SNA)
- **Best for**: Organizations, communities, influence networks
- **Nodes**: Individuals, groups, organizations, roles
- **Edges**: Friendships, collaborations, communication, influence
- **Examples**: Corporate org charts, social media analysis, team networks
- **Analysis**: Centrality, community detection, information diffusion

### :deciduous_tree: Ecological Systems Framework
- **Best for**: Food webs, species interactions, ecosystem dynamics
- **Nodes**: Species, populations, functional groups
- **Edges**: Predation, competition, mutualism, parasitism
- **Examples**: Yellowstone wolf-elk-vegetation cascade, coral reef ecosystems
- **Analysis**: Trophic levels, resilience, biodiversity

### :recycle: Complex Adaptive Systems (CAS)
- **Best for**: Emergent systems, markets, cities, hybrid systems
- **Nodes**: Adaptive agents with learning rules
- **Edges**: Interactions with feedback
- **Examples**: Stock markets, urban traffic, ant colonies
- **Analysis**: Emergence, self-organization, multiscale dynamics

### :wrench: Custom Framework (LLM-Generated)
- **Best for**: Novel domains, hybrid systems, experimental research
- **Process**: LLM researches domain and creates custom framework
- **Examples**: Cyber-physical-social systems, unique research domains

**Framework selection happens in step S-01A during setup workflow.**

---

## :gear: The 5 Workflows

Reflow uses **5 separate, focused workflows** instead of one monolithic file:

### :one: Setup (`workflows/00-setup.json`)
- Configure paths (reflow_root, system_root, tools)
- **NEW**: Select architectural framework (UAF, Biology, Social, Ecological, CAS, Custom)
- Create directory structure
- Initialize foundational documents
- **Optional**: Enable automatic git commits at workflow milestones
- **Duration**: 10-15 minutes

### :two: Systems Engineering (`workflows/01-systems_engineering.json`)
- Design architecture using selected framework
- Create **versioned** component architecture files (`*_architecture_v{version}-{date}.json`)
- Generate **framework-agnostic** `system_of_systems_graph.json` using NetworkX
- **NEW**: Knowledge gap detection (missing nodes, edges, "dark matter" components)
- Create `version_manifest.json` for tracking architecture history
- Validate architecture constraints (circular dependencies, orphaned nodes, structural holes)
- Generate `architecture_issues.json` with structured recommendations
- **NEW**: Comprehensive graph analysis (centrality, paths, connectivity, clustering, communities, cycles, SCCs, DAG analysis, flow)
- **Duration**: 2-4 hours

### :three: Artifacts & Visualization (`workflows/02-artifacts_visualization.json`)
- Generate Interface Contract Documents (ICDs)
- Create Mermaid diagrams (system, service, sequence, deployment)
- Generate **versioned** architecture documentation (`system_description_v{version}-{date}.md`)
- Human docs are version-paired with architecture files
- **Conditional**: Skip if architecture-only
- **Duration**: 1-2 hours

### :four: Development (`workflows/03-development.json`)
- **Optional**: Research current development best practices (dependency mgmt, CI/CD, testing, security)
- Implement services according to architecture
- Modern tooling recommendations (poetry vs requirements.txt, ruff vs pylint, etc.)
- 80% test coverage enforcement
- Observability instrumentation
- **Duration**: Days to weeks

### :five: Testing & Operations (`workflows/04-testing_operations.json`)
- CI/CD pipeline setup
- Docker Compose validation
- Operational testing (DTE, OTE)
- Release certification
- **Duration**: 1-2 weeks

**:gift: Bonus**: `workflows/feature_update.json` for updating existing systems

---

## :chart_with_upwards_trend: Network Analysis Selection

Reflow **automatically recommends** appropriate NetworkX analyses based on your chosen framework:

### Framework-Specific Recommendations

| Framework | Recommended Analyses | Why |
|-----------|---------------------|-----|
| **UAF** | `--centrality --dag --scc --community` | Verify no circular deps, find critical services |
| **Biology** | `--cycles --centrality --community --scc` | Feedback loops, hub genes, gene modules |
| **Social** | `--centrality --community --clustering` | Influencers, social groups, cohesion |
| **Ecological** | `--flow --centrality --connectivity` | Energy flow, keystone species, robustness ⚠️ **Requires edge weights!** |
| **CAS** | `--cycles --community --scc --centrality` | Feedback, emergent clusters, co-evolution |

### When to Add Edge Weights

**Flow analysis REQUIRES edge weights.** Add `weight` field to edges in architecture files:

- **UAF**: `request_rate` (req/sec) or `data_volume` (MB/sec)
- **Biology**: `reaction_rate` (molecules/sec) or `binding_affinity`
- **Social**: `interaction_frequency` or `relationship_strength` (0-1)
- **Ecological**: `energy_transfer_rate` (kcal/m²/year) or `biomass_flow`
- **CAS**: `flow_rate` or `interaction_strength`

See `definitions/framework_registry.json` and `definitions/analysis_selection_guide.json` for complete guidance.

---

## :sparkles: Why Reflow?

### :globe_with_meridians: Framework-Agnostic (v3.1.0)
Model **any complex system** - software (UAF), biological networks, social systems, ecosystems, or create your own custom framework.

### :rocket: Production-Ready from Day One (v3.3.0)
**Design for real operational environments UPFRONT** - not as an afterthought that causes budget overages:
- **10 IT Considerations**: Service decomposition, containerization, IaC, CI/CD, scalability, security, monitoring, networking, cost, testing
- **Real-World Conditions**: Design for failures, attacks, load spikes, network partitions (not benign vacuum environments)
- **Testing Strategy Defined Early**: Systems engineering phase defines which tests to run and why; testing phase executes them
- **Prevents Costly Retrofitting**: Addressing operational environment upfront prevents 10-100x cost overruns

### :shield: Enterprise Requirements Built-In (v3.2.0)
For UAF/IT systems with human users:
- **Security**: Authentication, authorization, API gateway, rate limiting, encryption, audit logging
- **Deployment**: One-command deployment, automated rollback, health checks, monitoring
- **UX**: Intuitive APIs, clear error messages, comprehensive documentation

### :bookmark: Architecture Versioning (v3.0)
- **Complete History**: All architecture versions preserved with semantic versioning
- **Rollback Support**: Restore previous versions via symlinks
- **Version Tracking**: Track changes, rationale, and evolution over time

### :gear: Modular & Flexible
- **5 Focused Workflows**: Each with clear purpose (setup, architecture, artifacts, development, operations)
- **Skip What You Don't Need**: Architecture-only? Stop after workflow 2
- **Clean Separation**: Your system directory is completely separate from reflow tooling
- **Quality Gates**: 10 explicit gates (7 blocking) ensure quality

---

## :file_folder: Directory Structure

### Reflow Tooling (One Place)
```
reflow/
├── workflows/                    # NEW - 6 modular workflow files
│   ├── 00-setup.json
│   ├── 01-systems_engineering.json
│   ├── 02-artifacts_visualization.json
│   ├── 03-development.json
│   ├── 04-testing_operations.json
│   └── feature_update.json
├── workflow_steps/              # NEW - Detailed step definitions
├── workflows_master_index.json  # NEW - Workflow routing
├── tools/                       # 22 Python tools
├── templates/                   # 36+ templates
└── definitions/                 # Architectural definitions
```

### Your System (Anywhere on Filesystem)
Each system gets a standardized structure:
```
<your_system_path>/
├── context/                     # LLM workflow tracking
│   ├── working_memory.json     # Current state & paths
│   ├── step_progress_tracker.json
│   └── current_focus.md
├── specs/                       # Architecture specifications
│   ├── machine/                # Machine-readable
│   │   ├── service_arch/      # service_architecture.json files
│   │   ├── interfaces/        # Interface Contract Documents
│   │   ├── port_registry.json # Centralized port assignments (prevents conflicts!)
│   │   ├── security_architecture.json  # Security requirements (UAF with human users)
│   │   ├── deployment_architecture.json  # Deployment strategy (UAF/IT systems)
│   │   ├── ux_api_design.json  # UX and API design standards (UAF with human users)
│   │   ├── operational_environment.json  # Real operational conditions, 10 IT considerations (UAF production systems)
│   │   └── graphs/            # system_of_systems_graph.json
│   └── human/                  # Human-readable
│       ├── visualizations/    # Mermaid diagrams
│       └── documentation/     # Architecture docs
├── services/                    # Service implementations
│   ├── <service_name>/
│   │   ├── src/
│   │   └── tests/
│   └── build_ready_index.json
└── docs/                        # Foundational documents
    ├── SYSTEM_MISSION_STATEMENT.md
    ├── USER_SCENARIOS.md
    └── SUCCESS_CRITERIA.md
```

---

## :package: What You Get

### Machine-Readable Artifacts
- `service_architecture.json` for each service (UAF 1.2 compliant)
- `system_of_systems_graph.json` (complete system graph)
- `interface_registry.json` (all interfaces cataloged)
- `port_registry.json` (port assignments - prevents deployment conflicts!)
- Interface Contract Documents (ICDs) for all APIs
- `version_manifest.json` (artifact versioning)

### Human-Readable Artifacts
- Mermaid diagrams (system, service, sequence, deployment, data flow)
- Architecture documentation and reports
- Architecture Decision Records (ADRs)
- Operational runbooks and procedures
- Development handoff documentation

### Implementation & Operations
- Fully implemented services with 80%+ test coverage
- CI/CD pipelines configured and working
- Docker Compose for local deployment
- Monitoring and alerting configured
- Release certification and production readiness

### Quality Assurance
- 10 quality gates (7 blocking gates)
- Automated validation and consistency checking
- Contract compliance verification
- Regression testing
- Security and performance testing

---

## :bulb: Common Usage Patterns

### :cloud: New System (Web-Based - Recommended)
```
Day 1: Initial Architecture
1. Create GitHub repo: github.com/yourname/smart_home_system
2. Add README with system description
3. Open GitHub Codespaces or Claude Code (https://claude.ai/code)
4. Say: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
   on system in github.com/yourname/smart_home_system"
5. Continue through systems engineering workflow

Day 2: Continue Development
1. Open Codespaces or Claude Code (conversation persists!)
2. Say: "Continue workflow from context/working_memory.json
   in github.com/yourname/smart_home_system"
3. LLM agent picks up exactly where you left off
4. All progress tracked in context/ folder

Benefits:
✅ Never touches local machine
✅ Work from any device (laptop, tablet, phone)
✅ Conversation history preserved (in code environments)
✅ Context folder tracks progress
✅ Direct GitHub integration
✅ Codespaces: Free tier available (60 hours/month)
```

### :cloud: Architecture Only (Web-Based)
```
Use case: Generate architecture specs, no code implementation

1. Create GitHub repo with system description
2. Run: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
   on system in github.com/yourname/my_system"
3. At artifacts workflow, choose "architecture-only"
4. Result: Complete architecture specs, diagrams, ICDs (no service code)

Progression: 00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → END
```

### :cloud: Resuming Multi-Day Projects
```
Context is preserved in TWO ways:

1. context/working_memory.json (in your system repo)
   - Current workflow and step
   - All paths and configurations
   - Operations counter

2. Conversation history (in web-based services)
   - Claude.ai: Conversations persist indefinitely
   - Codespaces: Terminal history preserved
   - Can reference "continue from yesterday" or "what's next?"

Command to resume:
"Continue workflow from context/working_memory.json in github.com/yourname/my_system"
```

### Feature Update (Existing System)
```
"Implement workflow in github.com/sligara7/reflow/workflows/feature_update.json
on system in github.com/yourname/my_system"
```

### :computer: Local Machine Usage
<details>
<summary>Click to expand local patterns</summary>

```bash
# New system
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system"

# Resume work
"Continue workflow from context/working_memory.json in ~/projects/my_system"

# Feature update
"Implement workflow in /path/to/reflow/workflows/feature_update.json on system in ~/projects/my_system"
```
</details>

---

## :books: Documentation

### Workflow Structure
- :page_facing_up: [NEW_STRUCTURE_README.md](docs/restructuring/NEW_STRUCTURE_README.md) - Quick reference for new workflow structure
- :page_facing_up: [RESTRUCTURING_DESIGN.md](docs/restructuring/RESTRUCTURING_DESIGN.md) - Detailed design rationale
- :page_facing_up: [MIGRATION_GUIDE.md](docs/restructuring/MIGRATION_GUIDE.md) - Migration from v2.x to v3.0

### New Features (v3.0.1)
- :page_facing_up: [GIT_AUTOMATION_GUIDE.md](docs/GIT_AUTOMATION_GUIDE.md) - Setup and usage of automatic git commits
- :page_facing_up: [DEVELOPMENT_RESEARCH_FEATURE.md](docs/DEVELOPMENT_RESEARCH_FEATURE.md) - Development best practices research

<details>
<summary>Archived v2.x documentation</summary>

For archived v2.x documentation, see `docs/archive/` and `docs/old_documentation/`.

</details>

---

## :wrench: Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.8+ | Core runtime |
| networkx | latest | Graph operations |
| LLM Agent | Claude/GPT-4 | Workflow execution |
| Docker | optional | Deployment validation |

<details>
<summary>Installation</summary>

```bash
# Clone the repository
git clone https://github.com/anthropics/reflow.git
cd reflow

# Install Python dependencies
pip install networkx

# Verify installation
python3 -c "import networkx; print('✓ Dependencies installed')"
```

</details>

---

## :memo: Version History

<details open>
<summary><b>v3.3.0 (2025-10-25)</b> - Latest</summary>

- :rocket: **Operational Environment Design** - Design for REAL operational conditions UPFRONT (not as afterthought)
  - 10 IT considerations: service decomposition, containerization, IaC, CI/CD, scalability, security, monitoring, networking, cost, testing
  - Real-world conditions: failures, attacks, load spikes, network issues
  - Testing strategy defined during SE phase (testing phase executes it)
  - Prevents budget overages from retrofitting production-readiness (10-100x cost savings)
- :file_folder: New template: `operational_environment_template.json` (1100+ lines)
- :gear: Updated SE workflow with operational environment design and validation steps (SE-02-A08, SE-03-A08)

</details>

<details>
<summary>v3.2.0 (2025-10-25)</summary>

- :shield: **IT System Requirements** - Security, deployment, UX enforced upfront for UAF systems with human users
- :mag: Orphaned service detection
- :wrench: Port management at architecture level

</details>

<details>
<summary>v3.1.0 (2025-10-25)</summary>

- :globe_with_meridians: **Framework-agnostic** - Support for 6+ frameworks (UAF, Biology, Social, Ecological, CAS, Custom)
- :chart_with_upwards_trend: **Comprehensive graph analysis** - 25+ NetworkX algorithms
- :mag: Knowledge gap detection (missing nodes/edges)

</details>

<details>
<summary>v3.0.x (2025-10-24)</summary>

- :recycle: Restructured into 5 modular workflows
- :bookmark: Architecture versioning with semantic versioning
- :white_check_mark: Optional git automation and development research

</details>

<details>
<summary>v2.x and earlier</summary>

Monolithic `decision_flow.json` (now archived)

</details>

---

## :handshake: Contributing

We welcome contributions! Here's how you can help:

- [ ] Report bugs or issues
- [ ] Suggest new features or improvements
- [ ] Improve documentation
- [ ] Submit pull requests

> [!NOTE]
> For major changes, please open an issue first to discuss what you would like to change.

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines (if available).

---

## :page_with_curl: License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## :star2: Acknowledgments

Built on:
- **Multiple architectural frameworks** - UAF 1.2, Systems Biology, SNA, Ecological Systems, CAS
- **NetworkX** - Graph analysis and algorithms
- **Systems Engineering** best practices
- **Clean Architecture** principles
- **Automated context management** for LLM agents

---

<div align="center">

**:sparkles: Version 3.3.0 - Production-ready systems from day one! :sparkles:**

Made with :heart: for systems engineers and LLM agents

[Documentation](docs/) • [Issues](https://github.com/anthropics/reflow/issues) • [Discussions](https://github.com/anthropics/reflow/discussions)

</div>