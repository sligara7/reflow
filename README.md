# Reflow - Systems Engineering Workflow

[![Version](https://img.shields.io/badge/version-3.1.0-blue.svg)](https://github.com/anthropics/reflow)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-purple.svg)](LICENSE)
[![Frameworks](https://img.shields.io/badge/frameworks-6%2B-green.svg)](#supported-frameworks)

A comprehensive, **framework-agnostic** systems engineering workflow for designing, architecting, and developing complex systems across multiple domains.

**:tada: Version 3.1.0** - Now framework-agnostic! Model software systems (UAF), biological networks, social systems, ecosystems, and more with the same workflow!

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

### 1. Create Your System Folder
Create a new folder anywhere on your system (separate from reflow tooling):
```bash
mkdir ~/projects/my_system
# or anywhere else you prefer: /workspace/my_system, etc.
```

### 2. Describe Your System
Inside your system folder, create a text document describing:
- What system or system-of-systems you want to engineer
- High-level requirements and goals
- Any existing systems that need integration

Example:
```bash
echo "Smart Home Automation System - integrate lighting, security, HVAC, and entertainment systems" > ~/projects/my_system/system_description.txt
```

### 3. Start with Setup Workflow
Tell your LLM agent:
```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system
```

The setup workflow will:
- Configure all paths (reflow_root, system_root, tools_path)
- **Select architectural framework** (UAF, Biology, Social, Ecological, CAS, or Custom)
- Create the proper folder structure
- Initialize foundational documents
- Prepare for architecture and development

### 4. Progress Through Workflows
After setup, you'll progress through 5 focused workflows:
```
00-setup → 01-systems_engineering → 02-artifacts_visualization →
03-development → 04-testing_operations
```

Each workflow is focused, manageable, and builds on the previous one.

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

## :sparkles: Key Benefits

### :new: Optional Automation Features (v3.0.1)

<details>
<summary><b>Click to expand optional features</b></summary>

- :arrow_forward: **Git Automation**: Automatic commits and pushes at workflow milestones (~36 commits for full workflow)
- :mag: **Development Research**: Quick 5-10 min research of current best practices before coding
- :white_check_mark: **Enhanced Validation**: Automatic detection of async/sync mismatches and architectural issues

</details>

### Modular Workflows (v3.0)
- **Focused Workflows**: Each workflow has a clear purpose (80% easier to navigate)
- **Independent Updates**: Modify one workflow without affecting others
- **Clear Progress**: Know exactly where you are in the process
- **Flexible Execution**: Skip workflows as needed (e.g., architecture-only)

### Architecture Versioning (v3.0)
- **Complete History**: All architecture versions preserved with semantic versioning
- **Rollback Support**: Restore previous versions via symlinks
- **Version Tracking**: `version_manifest.json` tracks all changes and rationale
- **Human Docs Paired**: Documentation versions match architecture versions exactly
- **Mixed-Version Testing**: Test specific combinations of service versions
- **Architecture Evolution**: Dedicated workflow (SE-07) for updating architectures

### Clean Separation
- **No Repository Conflicts**: Systems are completely separate from reflow tooling
- **Independent Repositories**: Each system can be its own git repository
- **Flexible Locations**: Systems can be anywhere on your filesystem
- **Path Management**: All paths configured upfront in Setup workflow

### System Architecture
- **New Systems**: Complete systems engineering from concept to implementation
- **System-of-Systems**: Integrate multiple existing systems
- **Feature Updates**: Modify existing architectures safely with mandatory validation
- **Quality Gates**: 10 explicit quality gates (7 blocking) prevent issues

### Development Support
- **Multi-language**: Support for Python, Java, TypeScript, Go, Rust, and more
- **Validation**: Automated architecture validation and consistency checking
- **Documentation**: Auto-generated system documentation and interface contracts
- **Testing**: Comprehensive testing pyramid with coverage enforcement

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

### New System (Full Development)
```bash
# Start with setup
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system"

# Progress through all workflows
# 00-setup → 01-systems_engineering → 02-artifacts_visualization →
# 03-development → 04-testing_operations
```

### Architecture Only (No Development)
```bash
# Run through architecture workflows
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system"

# At artifacts workflow, choose "architecture-only"
# 00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → END
```

### Feature Update (Existing System)
```bash
# Use feature update workflow
"Implement workflow in /path/to/reflow/workflows/feature_update.json on system in ~/projects/my_system"
```

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
<summary><b>v3.1.0 (2025-10-25)</b> - Latest</summary>

- :globe_with_meridians: **Framework-agnostic architecture** - Support for 6+ frameworks (UAF, Biology, Social, Ecological, CAS, Custom)
- :dna: Systems Biology framework for gene networks, metabolic pathways, ecosystems
- :busts_in_silhouette: Social Network Analysis framework for organizations and communities
- :deciduous_tree: Ecological Systems framework for food webs and species interactions
- :mag: **Knowledge gap detection** - Identifies missing nodes/edges (like "dark matter" in systems)
- :chart_with_upwards_trend: **Comprehensive NetworkX analysis** - 25+ graph algorithms across 10 categories
  - Core analysis: centrality, paths, connectivity, clustering, properties
  - Advanced analysis: community detection, cycle detection, SCCs, DAG analysis, flow analysis
- :wrench: New tool: `system_of_systems_graph_v2.py` (1370+ lines, framework-agnostic)
- :file_folder: Framework selection in setup workflow (step S-01A)

</details>

<details>
<summary>v3.0.1 (2025-10-24)</summary>

- :white_check_mark: Added optional git automation (automatic commits at workflow milestones)
- :mag: Added optional development best practices research (5-10 min quick search)
- :shield: Enhanced architecture validation (async/sync consistency, architectural issues detection)
- :book: Updated documentation with feature guides

</details>

<details>
<summary>v3.0.0 (2025-10-24)</summary>

- :recycle: Restructured into 5 modular workflows for better maintainability
- :file_folder: Improved directory structure and path management
- :bookmark: Added architecture versioning with semantic versioning

</details>

<details>
<summary>v2.5.0 and earlier</summary>

Monolithic `decision_flow.json` (now archived as `decision_flow.json.old`)

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

**:sparkles: Version 3.1.0 - Now framework-agnostic! Model any complex system across multiple domains! :sparkles:**

Made with :heart: for systems engineers, biologists, social scientists, ecologists, and LLM agents

[Documentation](docs/) • [Issues](https://github.com/anthropics/reflow/issues) • [Discussions](https://github.com/anthropics/reflow/discussions)

</div>