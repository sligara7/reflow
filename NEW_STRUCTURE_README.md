# Reflow New Structure - Quick Reference

## 🎉 What Changed?

Reflow has been **restructured from a monolithic `decision_flow.json` into 5 separate, manageable workflows**!

### Before (v2.5.0)
- ❌ Single massive file (128KB, 2,351 lines)
- ❌ Hard to navigate and update
- ❌ Everything in one place

### After (v3.0.0)
- ✅ 5 focused workflows (setup, architecture, artifacts, development, testing)
- ✅ Clear separation of concerns
- ✅ Easy to maintain and update
- ✅ Better path management
- ✅ Architecture versioning with complete history and rollback support

---

## 📁 New Directory Structure

```
reflow/
├── workflows/                          # NEW - Main workflow files
│   ├── 00-setup.json                  # Setup: paths, directories, foundational docs
│   ├── 01-systems_engineering.json    # Architecture: service_architecture.json, graphs
│   ├── 02-artifacts_visualization.json # Artifacts: ICDs, Mermaid diagrams, docs
│   ├── 03-development.json            # Development: implement services
│   ├── 04-testing_operations.json     # Testing: DTE, OTE, CI/CD, release
│   └── feature_update.json            # Feature updates for existing systems
│
├── workflow_steps/                     # NEW - Detailed step definitions
│   ├── setup/
│   ├── systems_engineering/
│   ├── artifacts_visualization/
│   ├── development/
│   ├── testing_operations/
│   └── feature_update/
│
├── workflows_master_index.json         # NEW - Workflow routing and metadata
│
├── decision_flow.json.old              # ARCHIVED - Old monolithic file
│
├── tools/                              # UNCHANGED - 22 Python tools
├── templates/                          # UNCHANGED - 36+ templates
├── definitions/                        # UNCHANGED - Architectural definitions
└── instructions/                       # UNCHANGED - Behavioral rules
```

---

## 🚀 Quick Start

### For New Systems

```bash
# 1. Tell your LLM agent to run the setup workflow
"Implement workflow in /path/to/reflow/workflows/00-setup.json on system in /path/to/my_system"

# 2. Progress through workflows automatically:
# 00-setup → 01-systems_engineering → 02-artifacts_visualization →
# 03-development → 04-testing_operations
```

### For Existing Systems (Updates)

```bash
# Use the feature update workflow
"Implement workflow in /path/to/reflow/workflows/feature_update.json on system in /path/to/my_system"
```

### For Architecture-Only (No Development)

```bash
# Run through workflows, choose "architecture-only" at step 02
# 00-setup → 01-systems_engineering → 02-artifacts_visualization (minimal) → END
```

---

## 🔄 The 5 Workflows

### 1️⃣ **Setup** (`00-setup.json`)
**What it does**: Configure paths, create directories, initialize system

**Key outputs**:
- System directory structure
- Path configuration (reflow_root, system_root, tools_path)
- Foundational documents (mission, scenarios, success criteria)

**Duration**: 10-15 minutes

---

### 2️⃣ **Systems Engineering** (`01-systems_engineering.json`)
**What it does**: Design architecture, create service specs, generate graphs

**Key outputs**:
- `service_architecture_v{version}-{date}.json` for each service (UAF 1.2, versioned)
- `service_architecture.json` (symlink to latest version)
- `system_of_systems_graph.json`
- `interface_registry.json`
- `index.json` and `version_manifest.json`

**New steps**:
- **SE-07**: Architecture Evolution (update existing architectures with proper versioning)
- **SE-08**: Mixed-Version Validation (test specific service version combinations)

**Duration**: 2-4 hours (depends on complexity)

---

### 3️⃣ **Artifacts & Visualization** (`02-artifacts_visualization.json`)
**What it does**: Create human-readable docs, diagrams, and handoff materials

**Key outputs**:
- `system_description_v{version}-{date}.md` (versioned human-readable docs per service)
- `system_description.md` (symlink to latest version)
- Interface Contract Documents (ICDs)
- Mermaid diagrams (system, service, sequence, deployment)
- Architecture documentation
- Architecture Decision Records (ADRs)

**Versioning note**: Human docs are version-paired with architecture files

**Conditional**: Skip detailed artifacts if architecture-only

**Duration**: 1-2 hours

---

### 4️⃣ **Development** (`03-development.json`)
**What it does**: Implement services according to architecture

**Key outputs**:
- Implemented services (src/, tests/)
- Unit tests (80% coverage minimum)
- Integration tests
- Observability instrumentation

**Duration**: Days to weeks (depends on system size)

---

### 5️⃣ **Testing & Operations** (`04-testing_operations.json`)
**What it does**: Test, deploy, and release the system

**Key outputs**:
- CI/CD pipelines
- Docker Compose validation
- Operational runbooks
- Release certification
- Production deployment

**Duration**: 1-2 weeks

---

### 🔧 **Feature Update** (`feature_update.json`)
**What it does**: Safely update existing systems

**Key features**:
- Mandatory foundational alignment validation
- **Architecture versioning** (follows SE-07 workflow, creates new versioned files)
- **Semantic versioning decisions** (major/minor/patch based on impact)
- Delta analysis
- Regression testing
- Human doc versioning (paired with architecture updates)

**When to use**: Modifying existing systems

**Versioning behavior**: Creates new versioned files, never overwrites old versions

---

## 📊 Workflow Flow Diagram

```
New System:
┌──────────┐     ┌─────────────┐     ┌────────────┐     ┌─────────────┐     ┌─────────────┐
│          │     │             │     │            │     │             │     │             │
│  Setup   │ --> │   Systems   │ --> │ Artifacts  │ --> │ Development │ --> │   Testing   │
│          │     │ Engineering │     │    &       │     │             │     │      &      │
│          │     │             │     │    Viz     │     │             │     │     Ops     │
└──────────┘     └─────────────┘     └────────────┘     └─────────────┘     └─────────────┘
                                          │
                                          │ (if architecture-only)
                                          ▼
                                        [END]

Existing System (Feature Update):
┌──────────────┐     ┌──────────────┐     ┌──────────┐     ┌──────────┐     ┌──────────┐
│              │     │              │     │          │     │          │     │          │
│   Change     │ --> │ Architecture │ --> │  Delta   │ --> │   Dev    │ --> │ Testing  │
│  Proposal    │     │    Update    │     │  Review  │     │  Update  │     │    &     │
│  + Validate  │     │              │     │          │     │          │     │ Release  │
│              │     │              │     │          │     │          │     │          │
└──────────────┘     └──────────────┘     └──────────┘     └──────────┘     └──────────┘
     (MANDATORY)
```

---

## 📚 Documentation

- **[RESTRUCTURING_DESIGN.md](RESTRUCTURING_DESIGN.md)** - Detailed design rationale and architecture
- **[MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** - Complete migration guide with mapping tables
- **[WORKFLOW_DRIVER_UPDATES_NEEDED.md](WORKFLOW_DRIVER_UPDATES_NEEDED.md)** - Required updates to workflow_driver.py

---

## 🎯 Key Features

### 1. **Path-Aware**
All paths configured in Setup workflow and stored in `working_memory.json`:
- `reflow_root` - Where reflow tools are installed
- `system_root` - Where the system is being developed
- `tools_path`, `templates_path`, `workflow_steps_path` - Derived paths

No more path confusion!

### 2. **Modular**
Each workflow is independent:
- Update one without affecting others
- Clear entry points and prerequisites
- Explicit quality gates

### 3. **Flexible**
- Skip workflows as needed (e.g., architecture-only)
- Conditional execution
- Can subdivide workflows further

### 4. **Well-Documented**
Each workflow includes:
- Purpose and description
- Prerequisites
- Actions and tools
- Expected outputs
- Quality gates
- LLM agent guidance

### 5. **Architecture Versioning** ✨
Complete version tracking and management:
- **Versioned filenames**: `service_architecture_v1.0.0-20251024.json`
- **Semantic versioning**: major.minor.patch with clear rules
- **Symlink management**: Latest version always accessible via `service_architecture.json`
- **Human doc pairing**: `system_description_v1.0.0-20251024.md` matches architecture version
- **Architecture Evolution** (SE-07): Workflow for updating existing architectures
- **Mixed-Version Validation** (SE-08): Test specific service version combinations
- **Rollback support**: Restore previous versions by updating symlinks
- **Complete history**: All versions preserved, never deleted

**Example version evolution**:
```
Initial:     service_architecture_v1.0.0-20251024.json → service_architecture.json (symlink)
Bug fix:     service_architecture_v1.0.1-20251025.json → service_architecture.json (updated symlink)
New feature: service_architecture_v1.1.0-20251030.json → service_architecture.json (updated symlink)
Breaking:    service_architecture_v2.0.0-20251115.json → service_architecture.json (updated symlink)
```

**Version tracking**: All versions tracked in `version_manifest.json` with:
- Version history
- Change descriptions
- Breaking change indicators
- Rollback procedures
- Mixed-version test scenarios

---

## ⚠️ Important Notes

### Workflow Driver Updates
`workflow_driver.py` needs updates to fully support the new structure. See [WORKFLOW_DRIVER_UPDATES_NEEDED.md](WORKFLOW_DRIVER_UPDATES_NEEDED.md) for details.

**Until updated**, use workflows manually:
```bash
# Tell LLM agent which workflow to implement
"Implement workflow in /path/to/reflow/workflows/01-systems_engineering.json on system in /path/to/my_system"
```

### Backward Compatibility
- Old structure still available (`decision_flow.json.old`)
- Old directories retained (architecture/, development/, feature_update/)
- New structure recommended for all new projects

### Migration Path
See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for:
- Step mapping table (old → new)
- Migration instructions
- Compatibility notes

---

## 🔍 What Each Workflow Produces

| Workflow | Machine-Readable | Human-Readable |
|----------|-----------------|----------------|
| **Setup** | `working_memory.json`<br>`step_progress_tracker.json` | Foundational docs<br>(mission, scenarios, criteria) |
| **Systems Engineering** | `service_architecture_v{version}-{date}.json` (versioned)<br>`service_architecture.json` (symlink to latest)<br>`system_of_systems_graph.json`<br>`interface_registry.json`<br>`index.json`<br>`version_manifest.json` | (none - see Artifacts workflow) |
| **Artifacts & Viz** | Interface Contract Docs (ICDs) | `system_description_v{version}-{date}.md` (versioned)<br>`system_description.md` (symlink to latest)<br>Mermaid diagrams<br>Architecture docs<br>ADRs<br>Reports |
| **Development** | Source code<br>Tests<br>`build_ready_index.json` | Code documentation<br>Development notes |
| **Testing & Ops** | `dte_artifacts.json`<br>`ote_artifacts.json`<br>CI/CD configs | Runbooks<br>SLOs<br>Release certification |

---

## 🚦 Quality Gates

Each workflow has explicit quality gates:

- **G-S-03**: Foundational Documents Complete
- **G-SE-03**: Architecture Validation Gate (BLOCKING)
- **G-SE-05**: Specification Completeness Gate (BLOCKING)
- **G-SE-06**: Architecture Completion Gate (BLOCKING)
- **G-D-04**: Interface Contract Compliance (BLOCKING)
- **G-D-05**: Testing & Observability Gate (BLOCKING)
- **G-TO-01**: Development Testing Gate (BLOCKING)
- **G-TO-03**: Deployment Validation Gate (BLOCKING)
- **G-TO-05**: Release Certification Gate (BLOCKING - FINAL)

**Blocking gates cannot be skipped!**

---

## 💡 Tips

1. **Always start with Setup workflow** for new systems
2. **Use absolute paths** when invoking tools
3. **Track current workflow** in `working_memory.json`
4. **Don't skip quality gates** - they prevent downstream issues
5. **Read workflow files** to understand what each step does
6. **Update documentation** as you progress

---

## 📞 Support

- **Design Questions**: See [RESTRUCTURING_DESIGN.md](RESTRUCTURING_DESIGN.md)
- **Migration Help**: See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)
- **Workflow Driver**: See [WORKFLOW_DRIVER_UPDATES_NEEDED.md](WORKFLOW_DRIVER_UPDATES_NEEDED.md)
- **Old Structure**: `decision_flow.json.old` (read-only reference)

---

## ✨ Benefits Summary

| Before | After |
|--------|-------|
| 1 massive file | 5 focused workflows |
| Hard to navigate | Easy to find content |
| Difficult to update | Simple to modify |
| Path confusion | Clear path management |
| Monolithic | Modular and flexible |
| Hidden dependencies | Explicit prerequisites |
| Unclear progress | Clear workflow stages |

---

**Welcome to Reflow v3.0! 🎊**

The reflow project is now more maintainable, more modular, and easier to navigate. Happy building!

---

*Last updated: 2025-10-24*
*Version: 3.0.0*
