# Reflow - LLM Agent Guide

**Version**: 4.1.2
**Last Updated**: 2025-12-06

## What is Reflow?

Reflow is a **framework-agnostic systems engineering workflow** designed for LLM agents to design, architect, and develop complex systems across multiple domains. Provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

**NEW in v4.1.2**: **Abstraction Level Analysis for Language Migration** - Critical new tool and workflow update based on SMB (SuperMarioBros-C → Python) case study:
- **NEW TOOL**: `analyze_abstraction_level.py` - Analyzes source code to determine abstraction level (1-4) and recommends translation strategy
- **NEW CONCEPT**: Abstraction Gap determines translation strategy:
  - Gap = 0: LITERAL translation (syntax changes only, e.g., Python 2 → Python 3)
  - Gap = 1: DIRECT translation (idiom mapping, e.g., C++ → Java)
  - Gap >= 2: SEMANTIC translation (translate behavior, not implementation)
- **UPDATED**: LM-04 now includes abstraction analysis before defining translation rules
- **UPDATED**: LM-05 includes strategy-specific guidance based on abstraction gap
- **NEW DOC**: `docs/TRANSLATION_LEARNINGS.md` - Detailed case study from SMB migration

**Key Insight**: Translating C++ (mimicking ASM, Level 2-3) to Python (Level 4) with gap >= 2 using literal translation produced 1,654 states and 7,862 operations. Semantic translation produced ~1,500 lines of clean, working code.

See `tools/analyze_abstraction_level.py` and `docs/TRANSLATION_LEARNINGS.md` for details.

**NEW in v4.1.1**: **System Overhaul Refinements** - Bug fixes and enhancements based on real-world testing with Blocktran (Fortran→Python) and SuperMarioBros-C (C++→Python):
- **FIX**: `analyze_service_organization.py` KeyError when no functional flows defined
- **NEW**: REAL_TIME operation type for games, emulators, and simulations
- **NEW**: Entry point detection for C/C++ (main), Fortran (PROGRAM), and Rust (fn main)
- **NEW**: Fortran version detection (F77/F90/F95/F2003/F2008)
- **FIX**: Fortran comment detection (! and fixed-form comments)
- **NEW**: Missing workflow step files (RE-02 through RE-07)
- **NEW**: Migration templates (migration_scope_template.json, cutover_plan_template.json)

See `docs/changes/CHANGE_PROPOSAL_20251205_V411_REFINEMENTS.md` for full details.

**NEW in v4.1.0**: **System Overhaul Feature** - Two major capabilities for legacy system modernization:
1. **Reverse Engineering Workflow (01e)**: Extract functional architecture from ANY existing codebase - Reflow or not. Systematically analyzes unknown systems to generate codebase inventory, extract functions and interfaces, synthesize functional architecture, and infer service boundaries.
2. **Language Migration Workflow (01f)**: Systematic language transformation (e.g., COBOL→Python, Python2→Python3, Java→Go) with **interface-stable behavior preservation**. Extracts interface contracts BEFORE migration, validates them AFTER migration.

**Key Principle**: Functions and interfaces are language-agnostic. Extract the functional architecture first, then swap implementations while preserving interfaces.

See `workflows/01e-reverse_engineering.json`, `workflows/01f-language_migration.json`, and `docs/changes/CHANGE_PROPOSAL_20251205_OVERHAUL_FEATURE.md`.

**NEW in v3.23.0**: **Plugin-Based Architecture Validation Support** - Validation tools now properly handle plugin-based architectures. Added `service_type` classification (`deployed_service`, `library_plugin`, `sidecar`, `external_dependency`) to port registry. Library plugins no longer fail validation for missing primary ports since they are imported at runtime, not deployed as separate processes. Fixes GitHub issue #41. See updated `validate_port_registry.py` and `templates/port_registry_template.json`.

**NEW in v3.22.0**: **LLM Compliance & Constraint Enforcement** - Pre-execution constraint mechanisms to ensure LLM agents follow workflows correctly. Problem: LLMs optimize for "getting to the answer" not "following the process" - TC-004 showed 46% time lost to friction. Solution: (1) JSON schemas for critical files (functional_architecture_schema.json, service_architecture_schema.json), (2) Tool CONTRACT.json pattern documenting exact input requirements, (3) Schema-First mechanism in FA-02 (mandatory schema read BEFORE artifact creation), (4) Execution proof requirements (tool output files as verification), (5) Objective quality gates with measurable criteria. See `schemas/`, `tools/contracts/`, and updated FA-02 workflow.

**NEW in v3.21.0**: **Plugin-Based Modular Architecture** - Added as 4th service organization option (alongside domain-based, workflow-based, hybrid). Tool now analyzes extensibility requirements and outputs strategy scores. LLM agents are instructed to make EDUCATED recommendations by synthesizing tool analysis with user context - NOT just echo "tool recommends X".

**NEW in v3.20.0**: **Development Standards Configuration** - Centralized language-specific development standards configured once during setup (S-03-A07). For Python: Protocol + DI interfaces (default), Hatchling dependency management, lock file generation, pytest, ruff. Service organization strategy (plugin-based vs domain-based vs workflow-based vs hybrid) recommended during functional allocation based on analysis. Eliminates repeated decision prompts.

**NEW in v3.19.0**: **Deployment Environment Specification** - Define WHERE and HOW the system will be deployed BEFORE development begins. New workflow (02b-deployment_environment.json) captures deployment context upfront: target platforms, containerization strategy, scaling requirements, security constraints, observability needs, and infrastructure dependencies. Prevents late-stage deployment surprises.

**NEW in v3.19.1**: **Architectural Context Refresh** - Periodic re-grounding in system architecture during development. Each development step (D-01, D-02, D-04) now starts with a mandatory architectural context refresh that reads system_of_systems_graph.json, service_architecture.json, and interface_registry.json. Prevents "tunnel vision" during long development phases.

**NEW in v3.17.0**: **Service Interface Contracts** - Embedded architectural "hooks" that warn LLMs before making breaking changes to service functions or interfaces. Proactive drift prevention through minimal JSON contracts in each service directory.

**NEW in v3.16.0**: **Testing Framework** - GAN-inspired automated testing infrastructure for Reflow workflows. Separate agent architecture (Generator vs Discriminator) validates workflow outputs against ground truth, avoiding "conflict of interests."

**NEW in v3.15.0**: **Architecture Synchronization Loop** - Systematic iterative loop that keeps architecture synchronized with implementation during development and testing. Detects drift, versions changes with rationale, and enforces synchronization gates.

**NEW in v3.1.0**: Support for 6+ architectural frameworks - UAF 1.2, Systems Biology, Social Network Analysis, Ecological Systems, Complex Adaptive Systems, Decision Flow, and Custom frameworks.

## Critical Information for LLM Agents

### ⚠️ Version 3.0 Structure

**Active (v3.12.0)**:
- ✅ `workflows/*.json` - 17 workflow files (9 modular + 4 deprecated + 4 special)
- ✅ `workflow_steps/*/` - Step definitions by workflow
- ✅ `workflows_master_index.json` - Workflow routing with branching
- ✅ **Context Reduction**: 60-95% reduction via workflow splitting
- ✅ **Self-Sharpening**: Meta-analysis workflows for Reflow continuous improvement

**Archived (DO NOT USE)**:
- ❌ `docs/archive/decision_flow.json.old` - Old monolithic workflow

### 🔑 Key Distinction: Tooling vs System

1. **Reflow Tooling** (READ ONLY): `/path/to/reflow/` - workflows, tools, templates
2. **Your System** (WRITABLE): Separate directory for your architecture/code

## Getting Started

### 🤖 FIRST: LLM Self-Reporting (v3.9.1)

**⚠️ CRITICAL FOR ALL LLMs**: Before starting/resuming ANY workflow, you MUST self-report your context capabilities!

**Quick Self-Report (Recommended)**:
When user says "Implement workflow..." or "Continue workflow...", immediately respond:

```
I'm [YOUR MODEL NAME] with a [YOUR CONTEXT WINDOW] token context window.
Let me configure my capabilities and proceed with workflow.
```

**Your Context Window**:
- Claude Sonnet 4.5: **200,000 tokens** (threshold: 160k)
- GPT-4 Turbo: **128,000 tokens** (threshold: 102k)
- GPT-3.5: **16,000 tokens** (threshold: 12k)

**Result**: Your capabilities stored in `working_memory.json` for automatic context flow analysis.

---

### 🎯 User Preferences (NEW in v3.14.1)

**Stakeholder Approval**: During setup (S-03-A03A), LLM asks if formal stakeholder approval is required:

- **Yes**: Enterprise/production - stakeholder validation (FA-04) MANDATORY and BLOCKING
- **No**: Personal/hobby - stakeholder validation SKIPPED, proceed to technical validation

**Storage**: `working_memory.json` → `user_preferences.stakeholder_approval_required` (true/false)

---

### ⭐ Web-Based Usage (PRIMARY)

**Why Web-Based?**
- Zero local setup, context preservation across sessions
- Multi-day projects resume seamlessly
- GitHub integration (push/pull directly)

**Options**: GitHub Codespaces (60 hrs/month free), Claude Code, Gitpod, Replit

**Quick Start**:
```
Implement workflow in github.com/sligara7/reflow/workflows/00a-basic_setup.json
on system in github.com/yourname/my_system_repo
```

**Resume Work**:
```
Continue workflow from context/working_memory.json in github.com/yourname/my_system_repo
```

**⚠️ CRITICAL**: Always read `context/working_memory.json` FIRST - it's the source of truth.

**⚠️ Don't Use**: Regular chat interfaces (claude.ai chat, chatgpt) - need code execution + GitHub integration

### Alternative: Local Machine

```
Implement workflow in /path/to/reflow/workflows/00a-basic_setup.json on system in /path/to/your_system
```

### Pixi Setup (v3.11.0 - Recommended)

**Why Pixi?** 2-5x faster than pip, reproducible via lockfile, cross-platform.

**Install** (optional):
```bash
curl -fsSL https://pixi.sh/install.sh | bash
cd /path/to/reflow && pixi install
pixi run validate-arch <system_path>  # Shortcuts available
```

**Fallback**: `pip install networkx>=3.0`

### The Workflows (v4.1.0 - Modular + Self-Sharpening + Overhaul)

**Core Workflows**:
```
00a-basic_setup.json             → Basic setup (5-10 min)
00b-framework_selection.json     → Framework selection [OPTIONAL] (5-10 min)
01a-approach_detection.json      → Auto-detect approach (<5 min) [UPDATED v4.1.0]
01b-bottom_up_integration.json   → Bottom-up integration (2-3 hours)
01c-top_down_design.json         → Top-down design (2-4 hours)
01d-functional_analysis.json     → Functional analysis (2-6 hours)
01e-reverse_engineering.json     → Reverse engineer unknown codebases (2-4 hours) [NEW v4.1.0]
01f-language_migration.json      → Language migration with interface preservation (days-weeks) [NEW v4.1.0]
02-artifacts_visualization.json  → ICDs, diagrams (1-2 hours)
02b-deployment_environment.json  → Deployment environment spec (1-2 hours) [NEW v3.19.0]
03a-development_implementation.json → Implementation (days-weeks)
03b-development_validation.json  → Validation (1-2 days)
04a-testing.json                 → Testing workflows (1 week)
04b-operations.json              → Operations workflows (1 week)
feature_update.json              → Update existing systems
```

**Meta-Analysis & Testing** (For Reflow Itself):
```
97-GAN-inspired-test.json        → GAN-inspired execution audit testing (RECOMMENDED: run weekly/monthly)
98-reflow_feature_update.json    → Reflow feature update with AUTO meta-analysis
99-meta_analysis.json            → Comprehensive Reflow meta-analysis
```

**Workflow Chaining** (Automatic Continuous Improvement):
```
97 (Test) → 98 (Fix) → 99 (Validate)
```
- **97** discovers issues via GAN testing (Agent B executes, Agent A observes)
- **98** fixes issues (auto-triggered if P0/P1 issues found)
- **99** validates fixes via meta-analysis
- **Result**: Continuous self-improvement loop

## Workflow Progression

### Typical New System Flow

1. **Start**: `00a-basic_setup.json` - Paths, structure, `working_memory.json`
   - Optional: `00b-framework_selection.json` (55% context reduction if skipped)

2. **Architecture**: `01a-approach_detection.json` → Routes to 01b OR 01c
   - **Auto-detects** bottom-up (existing code) vs top-down (greenfield)
   - Routes based on directory scan (src/, requirements.txt, etc.)

3. **Documentation**: `02-artifacts_visualization.json` - ICDs, Mermaid diagrams

4. **Deployment Environment** (NEW v3.19.0): `02b-deployment_environment.json` - Define WHERE/HOW before coding
   - Target platforms (cloud, on-prem, hybrid, edge)
   - Containerization strategy (Docker, K8s, serverless)
   - Scaling, security, observability requirements
   - Infrastructure dependencies (databases, caches, queues)

5. **Build** (optional): `03a-development_implementation.json` then `03b-development_validation.json`

6. **Deploy** (optional): `04a-testing.json` then `04b-operations.json`

### Functional Analysis Flow (NEW v3.13.0)

**Purpose**: Focus on WHAT functions exist and HOW they interact, WITHOUT allocating to services.

**When to use**: Architecture-only deliverables, stakeholder validation, functional completeness analysis

**IMPORTANT: Framework-Agnostic** - Functional architecture is always a DAG, framework doesn't matter.

**Flow**:
```
00a-basic_setup → 01d-functional_analysis → DONE (or continue to 01b/01c)

FA-01: Extract functional requirements
FA-02: Define functional flows
FA-03: Generate visualizations (BPMN, UML, Mermaid)
FA-04: Stakeholder validation (CONDITIONAL - based on user preference)
FA-05: Technical analysis (gaps, redundancies)
FA-06: Iterative refinement
FA-07: Finalization → USER DECISION (continue to service allocation OR stop)
```

**Deliverables**: 11+ artifacts (functional_requirements.json, functional_architecture.json, 4 diagram types, FUNCTIONAL_ARCHITECTURE.md)

### Automated Gap Closure (NEW v3.13.0)

**Purpose**: Auto-propose solutions for gaps using matrix analysis and architecture linking.

**Gap Types**: Functional gaps (unreachable/dead-end functions), Allocation gaps (unallocated functions), Interface gaps (orphaned services)

**Tools**:
- `tools/reflow_gap_closure.py` - Integration wrapper
- `tools/matrix_gap_detection.py` - Matrix-based gap solver (B = C × A⁻¹)
- `tools/link_architectures.py` - Architecture linking engine

**Workflow Integration**:
- FA-06-A02B: Automated functional gap closure (OPTIONAL but RECOMMENDED)
- SE-01-A00B: Automated allocation gap closure (OPTIONAL but RECOMMENDED)

**Note**: Proposals require LLM/human review (not auto-applied).

### GAN-Inspired Testing Flow (Self-Testing) NEW v3.17.1

**Purpose**: Continuous automated testing of Reflow workflows to detect friction points, tool/workflow misalignments, and usability issues.

**Method**: GAN-inspired approach - Agent B (Generator/Executor) builds systems following workflows, Agent A (Discriminator/Observer) watches and identifies issues.

**When to Use**: Weekly/monthly or before major releases to benchmark Reflow quality and detect regressions.

**Flow**:
```
97-GAN-inspired-test → (if P0/P1 issues) → 98-reflow_feature_update → 99-meta_analysis

GAN-01: Load test cases from tests/execution_audit/test_cases.json
GAN-02: Agent B executes workflows on each test case (blind to expected outputs)
GAN-03: Agent A analyzes Agent B's execution, categorizes issues (P0/P1/P2)
GAN-04: Aggregate metrics, compare to baseline, detect regressions
GAN-05: Decision gate - auto-trigger fixes if critical issues found
GAN-06: (Conditional) Trigger 98-reflow_feature_update with fix specification
GAN-Post: Generate reports, archive results, update baseline
```

**Deliverables**:
- Agent B execution transcripts (how workflows were executed)
- Agent B reports (deviations, friction points discovered)
- Agent A meta-analysis (root causes, patterns, recommendations)
- GAN test summary (aggregate metrics, baseline comparison)
- Fix specification (if auto-triggering 98)

**Benchmarking**: Each run compares to baseline metrics (friction %, deviations, time) to detect regressions or improvements.

**Test Cases**: Defined in `tests/execution_audit/test_cases.json` - can be extended with new test cases over time.

---

### Reflow Meta-Analysis Flow (Self-Sharpening)

**CRITICAL**: When updating REFLOW ITSELF (not other systems), use `97-GAN-inspired-test.json`, `98-reflow_feature_update.json`, or `99-meta_analysis.json`

**Purpose**: Reflow analyzes itself, detects context bottlenecks, fixes implementation via META-05B (Self-Sharpening).

## Supported Frameworks

**⚠️ Framework Selection is Architectural** - DO NOT default to UAF!

**Selection Process** (S-01A): Semantic matching questionnaire → Score ALL frameworks (5-criteria rubric) → Map analyses → User confirmation (BLOCKING)

**Available**:
- **UAF 1.2**: Engineered systems (microservices, IoT)
- **Systems Biology**: Biological systems (gene networks, metabolic pathways)
- **Social Network Analysis**: Social systems, organizations
- **Ecological Systems**: Ecosystems, species interactions
- **Complex Adaptive Systems**: Emergent, self-organizing systems
- **Decision Flow**: Workflows, state machines
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
4. **NEVER** hardcode paths or guess locations
5. **VERIFY** tool exists before invoking: `ls {paths.tools_path}/system_of_systems_graph_v2.py`

### Architecture Versioning

```
service_architecture_v1.0.0-20251024.json    ← Versioned file
service_architecture.json                     ← Symlink to current
```

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

**32+ Python tools** (see `docs/TOOL_USAGE_SUMMARY.md`):

**Key Tools**:
- `system_of_systems_graph_v2.py` - **FLAGSHIP**: Graph generation, gap detection, 25+ NetworkX algorithms
- `validate_architecture.py` - Framework-agnostic validation
- `generate_interface_contracts.py` - ICD generation (JSON-based)
- `generate_interface_abc.py` - **NEW v3.10.0**: Language-native contracts (Python ABC, TypeScript, Rust, C++, Java, Go)
- `generate_human_documentation.py` - Machine → Human translation
- `parse_human_documentation.py` - Human → Machine translation
- `context_refresh.py`, `detect_context_drift.py` - Context management

**36+ templates** for architecture, contracts, working memory, specs, registries

## IT System Requirements (UAF with Human Users)

**Applicability**: UAF framework systems with human users or external API access

**⚠️ Design Upfront, Not Retrofit**: IT systems with human users/APIs MUST address these upfront:

1. **Security** (SE-02-A05) - Auth, authorization, API gateway (MANDATORY), rate limiting, encryption
2. **Deployment** (SE-02-A06) - One-command deploy, health checks, CI/CD, monitoring
3. **UX/API** (SE-02-A07) - RESTful design, OpenAPI docs (MANDATORY), versioning
4. **Operational Environment** (SE-02-A08) - Design for failures, attacks, scale

**Validation Gates**: SE-03-A05, SE-03-A06, SE-03-A07, SE-03-A08 (ALL BLOCKING)

**📖 Full Documentation**: See `docs/IT_SYSTEM_REQUIREMENTS.md`

## Common Patterns

### Pattern 1: Web-Based Greenfield System (PRIMARY)

**Day 1**: User creates GitHub repo → Opens Codespaces/Claude Code → "Implement workflow in..." → LLM executes → Context saved

**Day 2+**: Opens environment → "Continue workflow from context/working_memory.json..." → LLM reads context, resumes

**LLM Best Practices**:
- ALWAYS read `context/working_memory.json` first
- **EXTRACT AND STORE** the `paths` object
- **USE** extracted paths for ALL tool/template/workflow references (NEVER hardcode)

### Pattern 2: Resuming After Break

**User**: "Continue workflow from context/working_memory.json in github.com/yourname/my_system"

**LLM Process**:
1. Read `context/working_memory.json`
2. **EXTRACT**: `current_workflow`, `current_step`, **`paths` object** (STORE THIS!)
3. Resume from exact step
4. **USE extracted paths** for ALL references
5. Update context after operations

**CRITICAL**: Context folder IS the source of truth. **PATHS MUST BE EXTRACTED FROM working_memory.json** - NEVER hardcode!

## Troubleshooting

### "Can't find tool X" or "Tool doesn't exist"

**Root Cause**: Paths not extracted from `working_memory.json`

**Fix**:
1. **READ** `{system_root}/context/working_memory.json`
2. **EXTRACT** the `paths` object
3. **VERIFY** tool exists: `ls {paths.tools_path}/system_of_systems_graph_v2.py`
4. **USE** extracted path: `python3 {paths.tools_path}/system_of_systems_graph_v2.py ...`

**NEVER**:
- ❌ Hardcode paths like `/home/user/reflow/tools/`
- ❌ Download templates/tools from GitHub using `curl` - Reflow is ALREADY LOCAL!
- ❌ Fetch from `https://raw.githubusercontent.com/sligara7/reflow/` URLs

**ALWAYS**:
- ✅ Read `working_memory.json` FIRST before EVERY workflow step
- ✅ Extract all paths from the `paths` object
- ✅ Use LOCAL extracted paths in ALL commands

### "Working memory doesn't exist"

**Fix**: Run `00a-basic_setup.json` first to create `context/working_memory.json`

## What to Avoid vs Do

**❌ Don't**:
- Modify reflow tooling files (workflows, templates, tools)
- Use archived v2.x files
- Skip setup workflow
- Hardcode paths or guess tool locations
- Create new tools when existing ones can't be found
- Download from GitHub (Reflow is local!)

**✅ Do**:
- Reference reflow as read-only library
- Work in your system directory
- Follow workflow sequence
- Always read `working_memory.json` FIRST and extract paths
- Verify tools exist before invoking them

## File Structure

```
<your_system>/
├── context/                     # LLM workflow tracking
│   ├── working_memory.json      # SOURCE OF TRUTH for paths
│   ├── step_progress_tracker.json
│   └── current_focus.md
├── specs/                       # Architecture specifications
│   ├── machine/                # Machine-readable (JSON)
│   │   ├── service_arch/
│   │   ├── interfaces/
│   │   └── graphs/
│   └── human/                  # Human-readable (Markdown, diagrams)
│       ├── visualizations/
│       └── documentation/
├── services/                    # Service implementations (optional)
└── docs/                        # Foundational documents
```

## New Features Summary

### v3.20.0 - Development Standards Configuration System
**Problem Solved**: Users face repeated decision prompts during development (interface strategy, dependency manager, tooling). Preferences are scattered across multiple files. No standardized Python project generation.

**Key Features**:
- **Centralized Standards**: Single `development_standards.json` configured once during S-03-A07
- **Python Standards**: Protocol + DI (default), Hatchling, lock files, pytest, ruff, mypy
- **Service Organization**: LLM analyzes functional architecture and recommends workflow-based vs domain-based allocation
- **Project Generation**: `generate_python_project.py` creates consistent pyproject.toml and project structure

**Python Defaults**:
| Setting | Default | Alternatives |
|---------|---------|--------------|
| Interface Strategy | `protocol_di` | abc, manual |
| Dependency Manager | `hatchling` | poetry, uv, setuptools |
| Lock Files | `true` | false |
| Web Framework | `fastapi` | flask, django, litestar |
| Testing | `pytest` | unittest |
| Linting | `ruff` | flake8_black, pylint |

**New Tools**:
1. `configure_development_standards.py` - Configure standards interactively or with defaults
2. `generate_python_project.py` - Generate pyproject.toml and project structure

**Workflow Integration**:
- **S-03-A07** (NEW): Configure Development Standards during setup
- **D-01-A04.5**: Uses standards (no longer prompts - reads from config)
- **D-01-A04.6** (NEW): Generate Python project structure per service
- **FA-07**: Service organization strategy recommendation

**Service Organization Strategy** (during FA-07):
- Analyzes coordination complexity, workflow span, operation types
- Recommends: workflow-based, domain-based, or hybrid
- Stores choice in `development_standards.json`

**Impact**:
- Eliminates 5+ decision prompts during development workflow
- Consistent project structure across all services
- Modern Python packaging (PEP 517/518/621)
- 2-4 hours saved per project setup

**Full Documentation**: See `docs/DEVELOPMENT_STANDARDS.md`

### v3.19.0 - Deployment Environment Specification Workflow
**Problem Solved**: Deployment environment is often an afterthought, scattered across multiple workflows (SE-04, AV-02-A04, D-06_5) and discovered late during implementation. Developers make containerization, security, and scaling decisions without knowing the target platform upfront.

**Key Features**:
- **New Workflow**: `02b-deployment_environment.json` - Define WHERE and HOW before coding
- **Structured Specification**: Machine-readable `deployment_environment_spec.json` covering all deployment concerns
- **Six Key Areas**: Target platforms, containerization, scaling, security, observability, infrastructure dependencies
- **Development Alignment**: Deployment spec informs language/framework decisions in development phase

**New Artifacts**:
- `specs/deployment/deployment_environment_spec.json` - Complete deployment specification
- `templates/deployment_environment_spec_template.json` - Template for new systems

**Workflow Integration**:
- **02b-deployment_environment**: New workflow between artifacts (02) and development (03a)
- **DE-01**: Deployment Environment Specification (1-2 hours)
- **DE-02**: Deployment Environment Validation & Integration

**Workflow Position**:
```
01b/01c/01d (architecture) → 02 (artifacts) → [NEW] 02b (deployment env) → 03a (development)
```

**Impact**:
- Prevents late-stage deployment surprises
- Informs development decisions upfront (containerization, scaling, security designed in)
- Enables infrastructure team to provision in parallel with development
- Reduces 3-5 days rework per service from deployment constraints discovered late

**Full Documentation**: See `docs/changes/CHANGE_PROPOSAL_20251121_DEPLOYMENT_ENVIRONMENT.md`

### v3.21.0 - Plugin-Based Modular Architecture Option (NEW)
**Problem Solved**: LLM agents would just echo "tool recommends X" without making an educated recommendation. Also, plugin-based modular architecture wasn't offered as a standard option despite being the most flexible pattern for modern systems.

**Key Features**:
- **Plugin-Based as 4th Option**: Added plugin-based modular architecture alongside domain-based, workflow-based, and hybrid
- **Extensibility Analysis**: Tool now analyzes extensibility/modularity keywords to detect systems that need plugin architecture
- **Educated Recommendations**: LLM agents are now instructed to synthesize analysis scores with user context, NOT just echo tool output
- **Strategy Scoring**: Tool outputs numerical scores for each strategy, enabling transparent decision-making

**Updated Tool**: `analyze_service_organization.py` v3.21.0
- Analyzes 5 factors: coordination, workflow span, operations, state management, extensibility
- Outputs strategy scores for all 4 options
- Explicit guidance for LLM to make educated recommendations

**Workflow Integration**:
- **SE-02-A00**: Now offers 4 options with scores and explicit LLM guidance
- LLM must consider: tool scores + user requirements + system complexity + team experience

**📖 See**: `workflow_steps/systems_engineering/SE-02-ServiceArchitecture.json` for updated LLM instructions

### v3.18.0 - Protocol-Based Interfaces, Dependency Injection & Service Organization Strategies
**Problem Solved**: ABCs cause metaclass conflicts with frameworks (FastAPI, SQLAlchemy, Pydantic). Need flexible service organization strategies (domain-based vs workflow-based). Single implementation model limits multi-facility deployments.

**Key Features**:
- **Protocol-Based Interfaces**: Use Python Protocols instead of ABCs - no metaclass conflicts, structural typing, multiple implementations without inheritance
- **Dependency Injection**: Services declare dependencies via Protocol type hints, startup code provides implementations - easy testing, different impls per facility
- **Behavior Mixins**: Reusable components (HasLifecycle, HasLogging, RequiresAuth, TracksMetrics) - wide inheritance pattern (depth=1) instead of deep hierarchies
- **Service Organization Strategies**: LLM analyzes system and recommends plugin-based, domain-based, workflow-based, or hybrid organization based on coordination complexity, workflow span, operation types, and extensibility requirements (updated in v3.21.0)

**New Tools**:
1. `generate_interface_protocols.py` - Generate Protocols + DI infrastructure (alternative to `generate_interface_abc.py`)
2. `analyze_service_organization.py` - Analyze system and recommend organization strategy (v3.21.0: now includes plugin-based option)

**Workflow Integration**:
- **D-01-A04.5**: CHOICE - Protocol-based (recommended) vs ABC-based vs Skip
- **SE-02-A00** (NEW): Analyze coordination/workflows/extensibility → Recommend strategy → User chooses plugin/domain/workflow/hybrid

**Generated Artifacts** (Protocol-based):
```
services/common/protocols/*.py     # Protocol definitions (CanExecutePlans, ProvidesDeviceRegistry)
services/common/mixins/*.py        # Behavior mixins (HasLifecycle, HasLogging, RequiresAuth, TracksMetrics)
services/common/di/container.py    # DI container template
services/common/di/dependencies.py # FastAPI dependencies template
```

**Benefits**:
- No metaclass conflicts: Works with FastAPI, SQLAlchemy, Pydantic, domain frameworks
- Multi-facility: Different implementations per facility without code changes
- Testability: Inject mocks easily for testing
- Optimal organization: Choose domain/workflow/hybrid based on system characteristics (5-10 days saved via reduced distributed state complexity)

**Migration Path**: ABCs and Protocols can coexist - add Protocols alongside ABCs, gradually migrate type hints

**📖 Full Documentation**: See `docs/ARCHITECTURAL_PATTERNS_PROTOCOLS_DI.md` and `docs/changes/CHANGE_PROPOSAL_20251119_PROTOCOLS_DI_ARCHITECTURE.md`

### v3.17.0 - Service Interface Contracts (Embedded Architectural Hooks)
**Problem Solved**: LLMs can unknowingly modify service functions or interfaces without realizing the downstream impact on dependent services. Current architecture synchronization (v3.15.0) detects drift **after it happens**. Need **proactive** prevention.

**Key Features**:
- **SERVICE_CONTRACT.json**: Minimal JSON manifest embedded in each service's root directory
- **Contracted Functions**: Declares WHAT functions the service must implement
- **Contracted Interfaces**: Declares WHO the service talks to (provides/consumes)
- **Architecture Reference**: Points to authoritative architecture source of truth
- **LLM Warnings**: Explicit warnings about architectural impact of changes

**New Tools**:
1. `generate_service_contracts.py` - Generate contracts from service_architecture.json
2. `validate_service_contracts.py` - Validate implementations match contracts

**Workflow Integration**:
- **D-02-A05** (NEW): Generate contracts after domain model implementation
- **D-04-A06.5** (NEW): Validate contracts after integration surfaces
- **D-06-A02.5** (NEW): Validate contracts against as-built architecture
- **D-06.5-A04.5** (NEW): Regenerate contracts when architecture changes
- **D-07-A07.5** (NEW): Final pre-deployment contract validation

**Contract Structure** (example):
```json
{
  "service_name": "UserService",
  "contracted_functions": {
    "functions": ["CreateUser", "AuthenticateUser"],
    "warning": "DO NOT modify without updating functional architecture"
  },
  "contracted_interfaces": {
    "provides": ["UserManagementAPI"],
    "consumes": ["EmailNotificationAPI"],
    "warning": "Interface changes are BREAKING changes"
  },
  "llm_warnings": {
    "before_modifying_functions": "⚠️ WARNING: 2 contracted functions...",
    "before_modifying_interfaces": "⚠️ WARNING: Affects 2 consumer services..."
  }
}
```

**Impact**:
- **Proactive** drift prevention - warns LLMs **BEFORE** changes, not AFTER
- 2-4 hours saved per service (average drift reconciliation time)
- Complements existing tools (ABC contracts, ICD verification, architecture sync loop)

**📖 Full Documentation**: See `docs/changes/CHANGE_PROPOSAL_20251119_SERVICE_INTERFACE_CONTRACTS.md`

### v3.16.0 - Testing Framework
**Problem Solved**: Need automated validation that Reflow workflows produce correct outputs. Manual testing doesn't scale.

**Key Features**:
- **GAN-Inspired Architecture**: Separate Generator (Agent A) and Discriminator (Agent B) agents
- **Test Runner**: Orchestrates workflow execution on test systems
- **Test Validator**: Compares actual outputs against ground truth with similarity scoring
- **Test Cases**: Pre-defined test systems with requirements and expected outputs
- **No Conflict of Interests**: Agent A builds blind (no access to expected outputs), Agent B evaluates with ground truth

**Components**:
1. `tests/test_runner.py` - Workflow orchestration (Agent A controller)
2. `tests/test_validator.py` - Output validation (Agent B - discriminator)
3. `tests/test_systems/` - Test cases with requirements and expected outputs
4. First test case: `microservices_basic` (e-commerce, 19 functions, 7 services)

**Usage**:
```bash
# List test cases
python3 tests/test_runner.py --list-tests

# Validate outputs
python3 tests/test_validator.py --test-case microservices_basic
```

**Impact**: Enables regression testing, workflow validation, and continuous quality improvement for Reflow itself

**📖 Full Documentation**: See `docs/TESTING_GUIDE.md` and `tests/README.md`

### v3.15.0 - Architecture Synchronization Loop
**Problem Solved**: Implementations diverge from designed architectures during development/testing due to requirements creep, performance optimization, and operational realities. Architecture documents become stale.

**Key Features**:
- **NEW TOOL**: `version_architecture.py` - Systematic architecture versioning with semantic versioning
- **NEW WORKFLOW STEP**: `D-06.5` Architecture Synchronization & Versioning Loop
  - Detects drift after D-06 as-built comparison
  - Enforces MANDATORY synchronization when similarity < 0.7
  - Classifies root causes (requirements_creep, performance_optimization, etc.)
  - Versions architecture changes with complete history
  - Iterates until architecture matches implementation (similarity >= 0.95)
- **ENHANCED**: `D-Post-A02` Final Architecture Synchronization Verification (BLOCKING gate)
- **NEW ACTIONS**: `TO-05-A05.5` and `TO-05-A05.6` - Operational testing architecture update loop
- **NEW TEMPLATES**: 5 templates for version history, root cause analysis, decisions, signoffs

**Root Cause Categories**:
- requirements_creep, performance_optimization, technical_constraints, security_hardening, operational_reality, developer_mistake

**Impact**: Prevents stale architecture docs, provides complete audit trail of why architecture changed, systematic synchronization during development and operational testing

**📖 Full Documentation**: See `docs/changes/CHANGE_PROPOSAL_ARCHITECTURE_SYNC_LOOP.md`

### v3.6.0 - Early Testing Integration
**Problem Solved**: Prevents "toss it over the fence" between development and operational testing.

**Key Features**:
- **Pre-Deployment Validation (D-06.5)**: 7 automated checks catch 80-90% of deployment blockers
- **3 New Tools**: `validate_dependencies.py`, `validate_module_structure.py`, `validate_configuration_consistency.py`
- **Incremental Gates (D-0X-A99)**: "Prove-it-works" validation at each development step
- **Risk-Based Testing**: SE-02-A10 assesses risk per service (low/medium/high), tailors testing strategy
- **Testing as Architecture**: SE-02-A09 defines testability upfront (not operational afterthought)

**Impact**: 3-5 days saved per service (24-40 days for 8-service system)

**📖 Full Documentation**: See `docs/RELEASE_NOTES_v3.6.0.md`

### v3.10.0 - Language-Native Interface Contracts
**Problem Solved**: Bridges gap between JSON ICDs and code implementation.

**Key Features**:
- **New Tool**: `generate_interface_abc.py` - Auto-generates strongly-typed interfaces from ICDs
- **6 Languages**: Python (ABC), TypeScript, Rust (traits), C++, Java, Go
- **Compile-time validation**: Catch mismatches before runtime
- **IDE autocomplete**: Full IntelliSense for interface methods

**Integration**: D-01-A04.5 (automatically invoked after development environment setup)

**Impact**: 3-5 days saved per service (catch interface mismatches at compile time vs integration testing)

**📖 Full Documentation**: See `docs/changes/CHANGE_PROPOSAL_20251104_ABC_INTERFACE_CONTRACTS.md`

### v3.11.0 - Pixi Package Manager
Fast, reproducible Python environments (2-5x faster than pip).

### v3.13.0 - Functional Analysis + Automated Gap Closure
Framework-agnostic functional architecture workflow with mathematical gap detection.

## Multi-Language Support

Python, Java, TypeScript, Go, Rust - system-agnostic architecture patterns, language-specific development steps.

## Getting Help

**Documentation**:
- `docs/TESTING_GUIDE.md` - Testing framework (v3.16.0) - GAN-inspired automated testing
- `docs/TOOL_USAGE_SUMMARY.md` - All 32 tools
- `docs/IT_SYSTEM_REQUIREMENTS.md` - IT system requirements
- `docs/NETWORKX_ANALYSIS_GUIDE.md` - NetworkX analysis (400+ lines)
- `docs/DECISION_FLOW_FRAMEWORK.md` - Decision Flow example
- `docs/GIT_AUTOMATION_GUIDE.md` - Git automation
- `docs/META_ANALYSIS_GUIDE.md` - Meta-analysis guide
- `docs/RELEASE_NOTES_v3.6.0.md` - v3.6.0 release notes
- `tests/README.md` - Quick start for testing framework
- `README.md` - Overview and quick start

## Summary for LLM Agents

### Primary Approach: Web-Based Usage

1. **Web-based is PRIMARY**: Users create GitHub repo, read from `github.com/sligara7/reflow`, write to their repo
2. **Context is SOURCE OF TRUTH**: ALWAYS read `context/working_memory.json` FIRST
3. **⚠️ EXTRACT PATHS**: Read `working_memory.json` → Extract `paths` → Use for ALL references - NEVER hardcode
4. **Multi-day projects normal**: Context preserves state across sessions
5. **Reflow is read-only**: Never modify workflows/templates/tools
6. **Start with 00a-basic_setup**: Configures paths, framework, structure
7. **Modular workflows**: 00a → [00b?] → 01a → (01b OR 01c OR 01d) → 02 → 03a → 03b → 04a → 04b
8. **Quality gates enforced**: 10 gates (7 blocking)

**CRITICAL PATH EXTRACTION FLOW**:
```
1. User says: "Continue workflow from context/working_memory.json"
2. LLM reads: {system_root}/context/working_memory.json
3. LLM extracts: paths.tools_path, paths.templates_path, paths.reflow_root, etc.
4. LLM uses: python3 {paths.tools_path}/system_of_systems_graph_v2.py
5. LLM NEVER: Hardcodes paths or creates new tools or downloads from GitHub
```

---

**Ready to Start?**

**Web-Based**:
```
"Implement workflow in github.com/sligara7/reflow/workflows/00a-basic_setup.json
 on system in github.com/yourname/your_system_repo"
```

**Environment Options**: GitHub Codespaces (60 hrs/month free), Claude Code, Gitpod, Replit

**Resuming**:
```
"Continue workflow from context/working_memory.json in github.com/yourname/your_system_repo"
```

**Local Machine (Alternative)**:
```
"Implement workflow in /path/to/reflow/workflows/00a-basic_setup.json on system in /path/to/your_system"
```

Good luck building complex systems! 🚀
