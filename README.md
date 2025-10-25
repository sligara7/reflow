# Reflow - Systems Engineering Workflow

A comprehensive systems engineering workflow for designing, architecting, and developing complex systems and system-of-systems.

**Version 3.0.0** - Now with modular workflows for better maintainability!

## Quick Start

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

## The 5 Workflows

Reflow uses **5 separate, focused workflows** instead of one monolithic file:

### 1️⃣ **Setup** (`workflows/00-setup.json`)
- Configure paths (reflow_root, system_root, tools)
- Create directory structure
- Initialize foundational documents
- **Duration**: 10-15 minutes

### 2️⃣ **Systems Engineering** (`workflows/01-systems_engineering.json`)
- Design architecture (UAF 1.2 compliant)
- Create **versioned** `service_architecture_v{version}-{date}.json` for each service
- Generate `system_of_systems_graph.json`
- Create `version_manifest.json` for tracking architecture history
- Validate architecture constraints
- **New**: SE-07 (Architecture Evolution) and SE-08 (Mixed-Version Validation)
- **Duration**: 2-4 hours

### 3️⃣ **Artifacts & Visualization** (`workflows/02-artifacts_visualization.json`)
- Generate Interface Contract Documents (ICDs)
- Create Mermaid diagrams (system, service, sequence, deployment)
- Generate **versioned** architecture documentation (`system_description_v{version}-{date}.md`)
- Human docs are version-paired with architecture files
- **Conditional**: Skip if architecture-only
- **Duration**: 1-2 hours

### 4️⃣ **Development** (`workflows/03-development.json`)
- Implement services according to architecture
- 80% test coverage enforcement
- Observability instrumentation
- **Duration**: Days to weeks

### 5️⃣ **Testing & Operations** (`workflows/04-testing_operations.json`)
- CI/CD pipeline setup
- Docker Compose validation
- Operational testing (DTE, OTE)
- Release certification
- **Duration**: 1-2 weeks

**Bonus**: `workflows/feature_update.json` for updating existing systems

## Key Benefits

### Modular Workflows (NEW in v3.0!)
- **Focused Workflows**: Each workflow has a clear purpose (80% easier to navigate)
- **Independent Updates**: Modify one workflow without affecting others
- **Clear Progress**: Know exactly where you are in the process
- **Flexible Execution**: Skip workflows as needed (e.g., architecture-only)

### Architecture Versioning (NEW in v3.0!)
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

## Reflow Directory Structure

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

## What You Get

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

## Common Usage Patterns

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

## Documentation

- **[NEW_STRUCTURE_README.md](NEW_STRUCTURE_README.md)** - Quick reference for new workflow structure
- **[RESTRUCTURING_DESIGN.md](RESTRUCTURING_DESIGN.md)** - Detailed design rationale
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Migration from v2.x to v3.0
- **[how_to_use.md](how_to_use.md)** - Detailed usage instructions

## Requirements
- Python 3.8+ with dependencies: `networkx`
- LLM agent capable of following structured JSON workflows
- Docker (optional, for deployment validation)

## Version History

- **v3.0.0 (2025-10-24)**: Restructured into 5 modular workflows for better maintainability
- **v2.5.0 and earlier**: Monolithic decision_flow.json (now archived as decision_flow.json.old)

---

*Built on UAF 1.2 architecture framework with automated context management*

**🆕 Version 3.0 brings modular workflows, better path management, and comprehensive documentation!**