# Reflow - Systems Engineering Workflow

**Version 3.4.0** | Framework-agnostic systems engineering for LLM agents

## What is Reflow?

Reflow is a structured workflow that guides LLM agents (Claude, GPT-4, etc.) through designing, architecting, and building complex systems. It provides step-by-step workflows, automated validation, and comprehensive tooling for creating production-ready architectures.

**Key capabilities:**
- Framework-agnostic: Works with software (UAF), biology, social networks, ecosystems, workflows, and custom frameworks
- Automatic approach detection: Bottom-up (existing components) or top-down (greenfield)
- Production-ready: Designs for real operational conditions from day one
- Modular: 6 separate workflows - use what you need, skip what you don't

## Quick Start

### Web-Based Usage (Recommended)

**GitHub Codespaces** (Most accessible - free tier available):
```
1. Create your system repo on GitHub
2. Open repo → Code → Codespaces → Create codespace
3. Clone reflow: git clone https://github.com/sligara7/reflow
4. Say: "Implement workflow in /workspaces/reflow/workflows/00-setup.json
   on system in /workspaces/my_system"
```

**Claude Code** (https://claude.ai/code - requires Pro/Max):
```
1. Install Claude GitHub app in your repositories (required for private repos)
2. Say: "Implement workflow in github.com/sligara7/reflow/workflows/00-setup.json
   on system in github.com/yourname/my_system"
```

**Resuming work** (next day/session):
```
"Continue workflow from context/working_memory.json in github.com/yourname/my_system"
```

### Local Machine Usage

```bash
# Clone Reflow
git clone https://github.com/sligara7/reflow
mkdir ~/projects/my_system

# Start workflow
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in ~/projects/my_system"

# Resume work
"Continue workflow from context/working_memory.json in ~/projects/my_system"
```

## The 6 Workflows

### 1. Setup (`00-setup.json`) - 10-15 minutes
- Configure paths (reflow_root, system_root)
- Select architectural framework (UAF, Biology, Social, Ecological, CAS, Decision Flow, Custom)
- Create directory structure
- Initialize foundational documents
- Optional: Enable automatic git commits

### 2. Systems Engineering (`01-systems_engineering.json`) - 2-4 hours
- **NEW: Automatic approach detection** - LLM scans system directory and routes to:
  - **Bottom-up integration** (if existing components found) - Steps BU-01 through BU-06
    - Component inventory, gap analysis (9 gap types), exact code-level deltas, integration architecture
  - **Top-down design** (if empty/greenfield) - Steps SE-01 through SE-06
    - Service identification, architecture design, validation
- Create versioned architecture files
- Generate system_of_systems_graph.json with NetworkX analysis
- Validate architecture constraints

**Automatic Detection Process:**
- LLM scans system directory for source code, package manifests, build files
- Decision: ≥2 indicators → bottom-up, 0-1 indicators → top-down
- Informs user: "Auto-detection: BOTTOM-UP approach selected. Found: [services/, requirements.txt]"
- Manual override available via legacy entry points

### 3. Artifacts & Visualization (`02-artifacts_visualization.json`) - 1-2 hours
- Generate Interface Contract Documents (ICDs)
- Create Mermaid diagrams
- Generate versioned documentation
- Optional: Skip if architecture-only

### 4. Development (`03-development.json`) - Days to weeks
- Optional: Research current development best practices
- Implement services with 80% test coverage
- Observability instrumentation

### 5. Testing & Operations (`04-testing_operations.json`) - 1-2 weeks
- CI/CD pipeline setup
- Docker Compose validation
- Operational testing

### 6. Feature Update (`feature_update.json`) - Variable
- Update existing systems with versioning and backward compatibility tracking

## Workflow Usage Patterns

### New System (Greenfield)
```
00-setup → 01-systems_engineering (auto-detects empty dir → top-down SE-01) →
02-artifacts → 03-development → 04-testing_operations
```

### Existing Components (Bottom-Up Integration)
```
00-setup → 01-systems_engineering (auto-detects existing code → bottom-up BU-01) →
02-artifacts → 03-development → 04-testing_operations
```

Example: Integrating 10 Python packages
- LLM scans directory, finds packages, manifests, code
- Routes to BU-01: Creates component inventory
- BU-02: Defines integration requirements
- BU-03: Detects 9 gap types (missing interfaces, protocol mismatches, etc.)
- BU-04: Generates exact code-level deltas (function signatures, file locations)
- BU-05: Designs integration architecture
- BU-06: Validates and merges with top-down at common validation steps

### Architecture Only (No Code)
```
00-setup → 01-systems_engineering → 02-artifacts (minimal) → END

Result: Architecture specs, diagrams, ICDs - no service implementation
```

### Feature Update (Existing System)
```
feature_update.json

Process: Read existing architecture → Propose changes → Validate impact →
Update with versioning → Generate updated artifacts
```

## Supported Frameworks

**Framework selection happens in step S-01A with user confirmation required.**

- **UAF 1.2** - Software/hardware systems (microservices, IoT)
- **Systems Biology** - Gene networks, metabolic pathways
- **Social Network Analysis** - Organizations, communities, influence networks
- **Ecological Systems** - Food webs, species interactions
- **Complex Adaptive Systems** - Markets, emergent systems
- **Decision Flow** - Workflows, state machines, decision processes
- **Custom** - LLM-generated for novel domains

**Important**: Framework choice determines which NetworkX analyses you can run. See `docs/NETWORKX_ANALYSIS_GUIDE.md` for detailed guidance.

## What You Get

**Machine-readable artifacts:**
- Component/service architecture files (versioned)
- System of systems graph with NetworkX analysis
- Interface Contract Documents (ICDs)
- Port registry (prevents deployment conflicts)
- Version manifest

**Human-readable artifacts:**
- Mermaid diagrams (system, service, sequence, deployment)
- Architecture documentation
- Architecture Decision Records (ADRs)

**Implementation & operations:**
- Fully implemented services with 80%+ test coverage
- CI/CD pipelines configured
- Docker Compose for deployment
- Monitoring and alerting

**Quality assurance:**
- 10 quality gates (7 blocking)
- Automated validation
- Contract compliance verification

## Bottom-Up Integration (NEW in v3.4.0)

Reflow now supports **bottom-up integration** for existing components:

**Use cases:**
- Integrating 10+ Python packages into a cohesive system
- Integrating legacy systems not designed to work together
- Need exact component-level deltas (function/module changes)

**Process:**
1. **Component Inventory (BU-01)**: Catalog existing components, interfaces, dependencies
2. **Integration Requirements (BU-02)**: Define how components should work together
3. **Gap Analysis (BU-03)**: Detect 9 gap types using production-ready tool:
   - missing_interface, protocol_mismatch, data_model_incompatibility, missing_mediator
   - circular_dependency, conflicting_requirements, version_incompatibility
   - performance_gap, security_gap
4. **Component Deltas (BU-04)**: Generate exact code changes at function/class/module level
   - Example: "Add function get_user_permissions(user_id: str) -> List[str] to src/auth.py"
   - Includes: Function signatures, dependencies to add, configuration changes
   - Automatic semantic versioning (1.0.0 → 2.0.0 if breaking changes)
5. **Integration Architecture (BU-05)**: Design multi-tier nested architecture
6. **Validation (BU-06)**: Validate deltas, architecture, dependencies

**Tools provided:**
- `analyze_integration_gaps.py` (850+ lines) - Detects all 9 gap types
- `generate_component_deltas.py` (690+ lines) - Generates exact code-level changes
- `validate_component_deltas.py` (580+ lines) - Validates delta feasibility

## Directory Structure

**Reflow tooling (read-only reference):**
```
reflow/
├── workflows/           # 6 modular workflow files
├── workflow_steps/      # Detailed step definitions
├── tools/              # 19 Python tools
├── templates/          # 36+ templates
└── definitions/        # Framework definitions
```

**Your system (where you work):**
```
<your_system>/
├── context/            # LLM tracking (working_memory.json)
├── specs/
│   ├── machine/       # Architecture JSONs, ICDs, graphs
│   └── human/         # Diagrams, docs
├── services/          # Service implementations
└── docs/              # Foundational documents
```

## Key Features

**Automatic Approach Detection (NEW):**
- LLM automatically detects bottom-up vs top-down by scanning system directory
- No human intervention required
- Evidence-based decision with transparent reasoning
- Fallback to user confirmation if ambiguous

**Production-Ready from Day One:**
- 10 IT considerations: Service decomposition, containerization, IaC, CI/CD, scalability, security, monitoring, networking, cost, testing
- Design for real operational conditions: failures, attacks, load spikes, network partitions
- Testing strategy defined upfront (systems engineering phase)
- Prevents costly retrofitting (10-100x savings)

**Enterprise Requirements Built-In (UAF/IT systems):**
- Security: Authentication, authorization, API gateway, rate limiting, encryption, audit logging
- Deployment: One-command deployment, automated rollback, health checks
- UX: Intuitive APIs, clear error messages, comprehensive documentation

**Architecture Lifecycle Tracking (NEW v3.5.0):**
- Track architecture evolution: designed → as-built → as-fielded
- Compare implementation vs design to identify drift
- Delta reports with similarity scores and change classification
- Document rationale for deviations, feed insights back to design

**Architecture Versioning:**
- Semantic versioning for all architecture files
- Complete history preserved
- Rollback support via symlinks

## Requirements

| Requirement | Version | Purpose |
|-------------|---------|---------|
| Python | 3.8+ | Core runtime |
| networkx | latest | Graph operations |
| LLM Agent | Claude/GPT-4 | Workflow execution |
| Docker | optional | Deployment validation |

## Documentation

**Tool Reference:**
- [TOOL_USAGE_SUMMARY.md](docs/TOOL_USAGE_SUMMARY.md) - Comprehensive guide to all 19 tools
- [TOOL_VERSION_MANIFEST.md](docs/TOOL_VERSION_MANIFEST.md) - Tool version history (v3.5.0)

**Workflow & Features:**
- [NETWORKX_ANALYSIS_GUIDE.md](docs/NETWORKX_ANALYSIS_GUIDE.md) - Framework-specific NetworkX analysis guidance (400+ lines)
- [DECISION_FLOW_FRAMEWORK.md](docs/DECISION_FLOW_FRAMEWORK.md) - Decision Flow Framework documentation (500+ lines)
- [BOTTOM_UP_INTEGRATION_DESIGN.md](docs/BOTTOM_UP_INTEGRATION_DESIGN.md) - Bottom-up integration design
- [GIT_AUTOMATION_GUIDE.md](docs/GIT_AUTOMATION_GUIDE.md) - Automatic git commits setup
- [NEW_STRUCTURE_README.md](docs/restructuring/NEW_STRUCTURE_README.md) - Workflow structure reference

## Version History

**v3.4.0 (2025-10-26)** - Current
- Bottom-up integration workflow with 9 gap types, exact code-level deltas
- Automatic approach detection (LLM scans directory and routes to bottom-up or top-down)
- Framework selection enhancement with semantic matching, scoring rubric, user confirmation
- Decision Flow Framework for workflows and state machines
- Framework migration tool
- NetworkX analysis guide (400+ lines)

**v3.3.1 (2025-10-25)**
- Tool cleanup: 24 → 16 focused tools
- Comprehensive tool documentation

**v3.3.0 (2025-10-25)**
- Operational environment design (10 IT considerations)
- Real-world condition planning upfront

**v3.2.0 (2025-10-25)**
- IT system requirements (security, deployment, UX)
- Orphaned service detection
- Port management

**v3.1.0 (2025-10-25)**
- Framework-agnostic support (6+ frameworks)
- Comprehensive NetworkX analysis (25+ algorithms)
- Knowledge gap detection

**v3.0.x (2025-10-24)**
- Modular workflow restructure (5 workflows)
- Architecture versioning
- Git automation, development research

## Contributing

Contributions welcome. For major changes, open an issue first to discuss.

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Version 3.4.0** - Framework-agnostic systems engineering with automatic approach detection and bottom-up integration

[Documentation](docs/) • [Issues](https://github.com/sligara7/reflow/issues)
