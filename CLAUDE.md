# Reflow - LLM Agent Guide

**Version**: 3.0.0
**Last Updated**: 2025-10-24

## What is Reflow?

Reflow is a **systems engineering workflow framework** designed specifically for LLM agents to design, architect, and develop complex systems and system-of-systems. It provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

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

## Workflow Progression

### Typical New System Flow

1. **Start**: Run `00-setup.json`
   - Configure all paths (reflow_root, system_root, tools_path)
   - Create directory structure
   - Initialize `context/working_memory.json`

2. **Architecture**: Run `01-systems_engineering.json`
   - Design service architectures (UAF 1.2)
   - Create `service_architecture_v{version}-{date}.json` for each service
   - Generate `system_of_systems_graph.json`
   - Validate architecture constraints

3. **Documentation**: Run `02-artifacts_visualization.json`
   - Generate Interface Contract Documents (ICDs)
   - Create Mermaid diagrams
   - Generate versioned documentation

4. **Build**: Run `03-development.json` (optional)
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

### Architecture Versioning (NEW in v3.0!)

All architecture files use **semantic versioning**:

```
service_architecture_v1.0.0-20251024.json    ← Versioned file
service_architecture.json                     ← Symlink to current version
```

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

Reflow provides **22 Python tools** including:

**Architecture**:
- `validate_architecture.py` - Validate service_architecture.json against UAF 1.2
- `system_of_systems_graph.py` - Generate system integration graph
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

## Architecture Framework

Reflow is based on:
- **UAF 1.2** (Unified Architecture Framework)
- Systems engineering best practices
- Clean architecture principles
- Automated validation and quality gates

## Summary for LLM Agents

1. **Reflow is a library**: Read-only reference, don't modify
2. **Your system is separate**: Work happens in your system directory
3. **Start with 00-setup**: Always configure paths first
4. **6 workflows in sequence**: Follow the progression
5. **Context is critical**: Maintain working_memory.json
6. **Versioning matters**: Use semantic versioning for architecture
7. **Quality gates enforced**: Validate before advancing
8. **v3.0 is current**: Ignore archived v2.x files

---

**Ready to Start?**

```
Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/your_system
```

Good luck building complex systems! 🚀
