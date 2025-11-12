# Reflow - LLM Agent Guide

**Version**: 3.14.1
**Last Updated**: 2025-11-12

## What is Reflow?

Reflow is a **framework-agnostic systems engineering workflow** designed for LLM agents to design, architect, and develop complex systems across multiple domains. Provides structured JSON workflows with automated validation, context management, and comprehensive tooling.

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

### The Workflows (v3.12.0 - Modular + Self-Sharpening)

**Core Workflows**:
```
00a-basic_setup.json             → Basic setup (5-10 min)
00b-framework_selection.json     → Framework selection [OPTIONAL] (5-10 min)
01a-approach_detection.json      → Auto-detect approach (<5 min)
01b-bottom_up_integration.json   → Bottom-up integration (2-3 hours)
01c-top_down_design.json         → Top-down design (2-4 hours)
01d-functional_analysis.json     → Functional analysis (2-6 hours)
02-artifacts_visualization.json  → ICDs, diagrams (1-2 hours)
03a-development_implementation.json → Implementation (days-weeks)
03b-development_validation.json  → Validation (1-2 days)
04a-testing.json                 → Testing workflows (1 week)
04b-operations.json              → Operations workflows (1 week)
feature_update.json              → Update existing systems
```

**Meta-Analysis** (For Reflow Itself):
```
98-reflow_feature_update.json    → Reflow feature update with AUTO meta-analysis
99-meta_analysis.json            → Comprehensive Reflow meta-analysis
```

## Workflow Progression

### Typical New System Flow

1. **Start**: `00a-basic_setup.json` - Paths, structure, `working_memory.json`
   - Optional: `00b-framework_selection.json` (55% context reduction if skipped)

2. **Architecture**: `01a-approach_detection.json` → Routes to 01b OR 01c
   - **Auto-detects** bottom-up (existing code) vs top-down (greenfield)
   - Routes based on directory scan (src/, requirements.txt, etc.)

3. **Documentation**: `02-artifacts_visualization.json` - ICDs, Mermaid diagrams

4. **Build** (optional): `03a-development_implementation.json` then `03b-development_validation.json`

5. **Deploy** (optional): `04a-testing.json` then `04b-operations.json`

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

### Reflow Meta-Analysis Flow (Self-Sharpening)

**CRITICAL**: When updating REFLOW ITSELF (not other systems), use `98-reflow_feature_update.json` or `99-meta_analysis.json`

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
- `docs/TOOL_USAGE_SUMMARY.md` - All 32 tools
- `docs/IT_SYSTEM_REQUIREMENTS.md` - IT system requirements
- `docs/NETWORKX_ANALYSIS_GUIDE.md` - NetworkX analysis (400+ lines)
- `docs/DECISION_FLOW_FRAMEWORK.md` - Decision Flow example
- `docs/GIT_AUTOMATION_GUIDE.md` - Git automation
- `docs/META_ANALYSIS_GUIDE.md` - Meta-analysis guide
- `docs/RELEASE_NOTES_v3.6.0.md` - v3.6.0 release notes
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
