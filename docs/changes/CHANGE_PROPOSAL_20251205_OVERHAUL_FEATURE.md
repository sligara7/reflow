# Change Proposal: System Overhaul Feature

**Date**: 2025-12-05
**Proposal ID**: CP-2025-12-05-001
**Feature**: System Overhaul - Reverse Engineering & Language Migration
**Priority**: High
**Workflow Version**: 4.0.x → 4.1.0

## Executive Summary

Introduce a comprehensive **System Overhaul** capability to Reflow with two major sub-features:

1. **Reverse Engineering (01e-reverse_engineering.json)**: Take ANY existing codebase (Reflow-created or not) and extract functional architecture, interfaces, and system understanding through systematic analysis.

2. **Language Migration (01f-language_migration.json)**: Systematically convert a codebase from one language to another (e.g., COBOL → Python, Fortran → Rust, Python 2 → Python 3.12) while preserving functional behavior through interface-stable transformation.

**Key Principle**: Functions and interfaces are language-agnostic. By extracting the functional architecture first, we can "swap out" implementations in one language and "swap in" implementations in another - provided interfaces remain stable.

## Business Justification

### Current State

Reflow v4 supports:
- **Top-down design** (01c): Greenfield systems designed from requirements
- **Bottom-up integration** (01b): Existing Reflow-compatible components integrated
- **Functional analysis** (01d): Architecture-only deliverables without service allocation

**Gap**: No systematic approach for:
- Taking over non-Reflow systems (no working_memory.json, no specs/)
- Modernizing legacy codebases (COBOL, Fortran, Python 2, Java 6, etc.)
- Language migration while preserving system behavior

### Problems Addressed

1. **Legacy System Takeover**: Organizations inherit systems with no documentation, no architecture specs, and tribal knowledge. Current Reflow requires starting from scratch or manual reverse engineering.

2. **Technical Debt Migration**: Legacy systems in outdated languages (COBOL, Fortran, Visual Basic, Python 2) need modernization but risk behavior changes during rewrite.

3. **Platform Migration**: Moving from one tech stack to another (Java → Go, Python → Rust) requires preserving business logic while changing implementation.

4. **Knowledge Extraction**: Critical business logic buried in legacy code needs extraction before original developers retire.

### Value Proposition

| Scenario | Without Overhaul | With Overhaul |
|----------|------------------|---------------|
| Take over unknown system | Weeks of manual analysis | Structured 2-3 day workflow |
| COBOL → Python migration | 6-12 month risky rewrite | Systematic interface-stable migration |
| Understand legacy interfaces | Reading 10K+ lines of code | Automated extraction + visualization |
| Validate behavior preservation | Manual testing + prayer | Formal interface contract validation |

**Time Savings**: 2-6 weeks per legacy system modernization project

## Feature Description

### Architecture Overview

```
                    ┌─────────────────────────────────────┐
                    │         OVERHAUL FEATURE            │
                    └─────────────────────────────────────┘
                                    │
            ┌───────────────────────┼───────────────────────┐
            │                       │                       │
            ▼                       ▼                       ▼
    ┌───────────────┐     ┌─────────────────┐     ┌───────────────┐
    │  01e-reverse  │     │  01f-language   │     │  Existing BU  │
    │  engineering  │     │   migration     │     │   (01b)       │
    └───────────────┘     └─────────────────┘     └───────────────┘
            │                       │                       │
            │ Extracts              │ Transforms            │ Integrates
            ▼                       ▼                       ▼
    ┌───────────────┐     ┌─────────────────┐     ┌───────────────┐
    │  Functional   │────▶│  Interface-     │────▶│  Validated    │
    │  Architecture │     │  Stable Swap    │     │  New System   │
    └───────────────┘     └─────────────────┘     └───────────────┘
```

### Part 1: Reverse Engineering Workflow (01e)

**Purpose**: Extract functional architecture from ANY codebase - Reflow or not.

**Entry Scenarios**:
1. **Unknown system takeover**: "We inherited this codebase, no docs exist"
2. **Pre-migration analysis**: "Before migrating, understand what we have"
3. **Documentation generation**: "Generate architecture docs from code"
4. **Audit/compliance**: "Prove what this system actually does"

#### Workflow Steps: RE-01 through RE-07

```json
{
  "workflow_id": "01e-reverse_engineering",
  "name": "Reverse Engineering Workflow",
  "version": "1.0.0",
  "phase": "P2_architecture_allocation",
  "purpose": "Extract functional architecture from existing codebase"
}
```

**RE-01: Codebase Discovery & Inventory**
- Scan source directories for all code files
- Detect programming language(s) and frameworks
- Identify entry points (main functions, API endpoints, CLI handlers)
- Catalog dependencies (requirements.txt, package.json, pom.xml, etc.)
- Detect configuration files and environment variables
- **Output**: `specs/reverse/codebase_inventory.json`

**RE-02: Function Extraction**
- Parse code to extract all functions/methods
- Identify function signatures (inputs, outputs, side effects)
- Detect function dependencies (which functions call which)
- Classify functions by type (pure, stateful, I/O, coordination)
- Extract docstrings and comments as function descriptions
- **Output**: `specs/reverse/extracted_functions.json`

**RE-03: Interface Detection**
- Identify external interfaces (APIs, databases, file systems, networks)
- Extract API contracts (endpoints, request/response schemas)
- Detect internal interfaces (service boundaries, module interfaces)
- Map data flows between components
- Identify integration points with external systems
- **Output**: `specs/reverse/detected_interfaces.json`

**RE-04: Functional Architecture Synthesis**
- Synthesize extracted functions into functional_architecture.json
- Build function dependency graph
- Identify functional clusters (high cohesion groups)
- Detect functional gaps and redundancies
- Map to user scenarios (if foundational docs exist)
- **Output**: `specs/functional/functional_architecture.json` (standard format)

**RE-05: Service Boundary Inference**
- Analyze function clusters for natural service boundaries
- Detect existing service/module boundaries in code
- Propose service decomposition based on cohesion analysis
- Identify cross-cutting concerns (auth, logging, config)
- **Output**: `specs/reverse/inferred_services.json`

**RE-06: Validation & Gap Analysis**
- Validate extracted architecture against code
- Identify gaps (functions not mapped, interfaces not documented)
- Detect inconsistencies (code does X, extracted architecture says Y)
- Generate coverage report (% of code analyzed)
- **Output**: `specs/reverse/extraction_validation_report.json`

**RE-07: Architecture Finalization**
- Refine functional architecture based on validation
- Generate human-readable documentation
- Create visualizations (function dependency graph, service diagram)
- Integrate with standard Reflow specs (if continuing to implementation)
- **Output**: Standard Reflow architecture files + `docs/REVERSE_ENGINEERING_REPORT.md`

#### Reverse Engineering Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `analyze_codebase.py` | Scan and inventory codebase | Source directory | `codebase_inventory.json` |
| `extract_functions.py` | Parse and extract functions | Source files | `extracted_functions.json` |
| `detect_interfaces.py` | Identify internal/external interfaces | Source files + inventory | `detected_interfaces.json` |
| `synthesize_architecture.py` | Build functional architecture | Extracted functions + interfaces | `functional_architecture.json` |
| `infer_service_boundaries.py` | Propose service decomposition | Functional architecture | `inferred_services.json` |
| `validate_extraction.py` | Validate extraction completeness | All extracted specs + source | Validation report |

### Part 2: Language Migration Workflow (01f)

**Purpose**: Transform codebase from source language to target language while preserving functional behavior.

**Entry Scenarios**:
1. **Legacy modernization**: "Migrate COBOL mainframe to Python microservices"
2. **Platform shift**: "Move from Python to Rust for performance"
3. **Version upgrade**: "Upgrade Python 2 to Python 3.12"
4. **Ecosystem migration**: "Convert Java Spring to Go with standard library"

**Key Principle**: **Interface-Stable Transformation**
- Extract interfaces BEFORE migration
- Transform implementation WHILE preserving interfaces
- Validate interfaces AFTER migration
- Result: Behavior preservation guaranteed at interface boundaries

#### Workflow Steps: LM-01 through LM-09

```json
{
  "workflow_id": "01f-language_migration",
  "name": "Language Migration Workflow",
  "version": "1.0.0",
  "phase": "P2_architecture_allocation",
  "purpose": "Systematic language transformation with behavior preservation"
}
```

**LM-01: Migration Scope Definition**
- Define source language/version and target language/version
- Identify migration scope (full system vs specific services)
- Define migration constraints (timeline, team skills, dependencies)
- Establish success criteria (performance, test coverage, feature parity)
- **Output**: `specs/migration/migration_scope.json`

**LM-02: Pre-Migration Reverse Engineering**
- Execute RE-01 through RE-07 (or use existing if already done)
- Extract complete functional architecture
- Document ALL interfaces (critical for preservation)
- **Prerequisite**: `specs/functional/functional_architecture.json` must exist

**LM-03: Interface Contract Extraction**
- Extract formal interface contracts from source code
- Document input/output types, error conditions, side effects
- Generate interface test cases (golden tests)
- Create interface validation suite
- **Output**: `specs/migration/interface_contracts.json`, `tests/migration/interface_tests/`

**LM-04: Language Translation Rules Definition**
- Define type mappings (source types → target types)
- Define pattern mappings (idioms, design patterns)
- Define dependency mappings (libraries → equivalents)
- Define build system mapping (source build → target build)
- **Output**: `specs/migration/translation_rules.json`

**LM-05: Component-by-Component Translation**
- For each component/service:
  - Translate types and data structures
  - Translate function signatures (preserve interface contracts)
  - Translate function bodies (using idioms of target language)
  - Translate tests
- **Output**: New source files in target language

**LM-06: Interface Validation**
- Run interface test suite against new implementation
- Verify all interface contracts satisfied
- Compare function behavior (same inputs → same outputs)
- Document any intentional behavioral changes
- **Gate**: All interface tests must pass

**LM-07: Integration Testing**
- Test migrated components with existing components
- Verify data flow consistency
- Test error handling and edge cases
- Performance comparison (source vs target)
- **Output**: `specs/migration/integration_test_results.json`

**LM-08: Incremental Cutover Strategy**
- Define cutover sequence (which components migrate first)
- Create rollback plan for each component
- Define validation checkpoints
- Plan for hybrid operation (some old, some new)
- **Output**: `specs/migration/cutover_plan.json`

**LM-09: Migration Completion & Documentation**
- Finalize all migrated components
- Update architecture specs to reflect new implementation
- Document migration decisions and rationale
- Archive source language artifacts
- **Output**: Complete target language codebase + `docs/MIGRATION_REPORT.md`

#### Language Migration Tools

| Tool | Purpose | Input | Output |
|------|---------|-------|--------|
| `extract_interface_contracts.py` | Formalize interface contracts | Source code + functional arch | `interface_contracts.json` |
| `generate_interface_tests.py` | Create interface validation tests | Interface contracts | Test files |
| `define_translation_rules.py` | Interactive translation rule definition | Source/target languages | `translation_rules.json` |
| `translate_component.py` | Translate single component | Source component + rules | Target component |
| `validate_interface_preservation.py` | Verify interfaces match | Source + target + contracts | Validation report |
| `generate_migration_report.py` | Create comprehensive migration docs | All migration artifacts | `MIGRATION_REPORT.md` |

#### Translation Rules Template

```json
{
  "schema_version": "1.0.0",
  "source_language": {
    "name": "python",
    "version": "2.7",
    "framework": "django_1.11"
  },
  "target_language": {
    "name": "python",
    "version": "3.12",
    "framework": "fastapi"
  },
  "type_mappings": {
    "unicode": "str",
    "str": "bytes",
    "long": "int",
    "dict.iteritems()": "dict.items()",
    "print x": "print(x)"
  },
  "pattern_mappings": {
    "class_based_view": "function_based_router",
    "synchronous_orm": "async_orm",
    "manual_serialization": "pydantic_models"
  },
  "dependency_mappings": {
    "django": "fastapi",
    "django.db": "sqlalchemy_async",
    "django.forms": "pydantic",
    "requests": "httpx",
    "celery": "arq"
  },
  "build_system_mapping": {
    "setup.py": "pyproject.toml",
    "requirements.txt": "pyproject.toml[dependencies]",
    "tox.ini": "pyproject.toml[tool.tox]"
  },
  "idiom_mappings": {
    "try_except_unicode": "native_str",
    "itertools.izip": "zip",
    "xrange": "range"
  }
}
```

### Common Templates

#### `codebase_inventory_template.json`

```json
{
  "schema_version": "1.0.0",
  "inventory_date": "2025-12-05T00:00:00Z",
  "source_root": "/path/to/legacy/code",

  "languages_detected": [
    {
      "language": "python",
      "version_detected": "2.7",
      "file_count": 234,
      "lines_of_code": 45000,
      "primary": true
    }
  ],

  "frameworks_detected": [
    {
      "name": "django",
      "version": "1.11",
      "usage_areas": ["web_api", "orm", "admin"]
    }
  ],

  "entry_points": [
    {
      "type": "wsgi",
      "file": "myapp/wsgi.py",
      "function": "application"
    },
    {
      "type": "cli",
      "file": "manage.py",
      "commands": ["runserver", "migrate", "shell"]
    }
  ],

  "dependencies": {
    "runtime": ["django==1.11", "psycopg2==2.7", "celery==4.0"],
    "development": ["pytest", "mock", "coverage"],
    "system": ["postgresql", "redis", "nginx"]
  },

  "configuration": {
    "files": ["settings.py", ".env", "config/production.py"],
    "environment_variables": ["DATABASE_URL", "SECRET_KEY", "REDIS_URL"]
  },

  "directory_structure": {
    "pattern": "django_standard",
    "apps": ["users", "orders", "inventory", "reporting"],
    "shared": ["common", "utils", "middleware"]
  },

  "code_metrics": {
    "total_files": 312,
    "total_lines": 52000,
    "test_coverage_detected": 0.45,
    "documentation_detected": "partial"
  }
}
```

#### `extracted_functions_template.json`

```json
{
  "schema_version": "1.0.0",
  "extraction_date": "2025-12-05T00:00:00Z",

  "functions": [
    {
      "function_id": "users.views.create_user",
      "name": "create_user",
      "location": {
        "file": "users/views.py",
        "line_start": 45,
        "line_end": 78
      },
      "signature": {
        "inputs": [
          {"name": "request", "type": "HttpRequest", "required": true},
          {"name": "user_data", "type": "dict", "required": true}
        ],
        "outputs": [
          {"type": "HttpResponse", "description": "JSON response with user ID"}
        ],
        "raises": ["ValidationError", "IntegrityError"]
      },
      "classification": {
        "type": "coordinator",
        "purity": "impure",
        "side_effects": ["database_write", "email_send"],
        "io_operations": ["http_response"]
      },
      "dependencies": {
        "calls": ["users.models.User.create", "common.email.send_welcome"],
        "imports": ["django.http", "users.models", "common.email"]
      },
      "description": "Create a new user account and send welcome email",
      "extracted_from_docstring": true
    }
  ],

  "function_graph": {
    "nodes": ["users.views.create_user", "users.models.User.create", "..."],
    "edges": [
      {"from": "users.views.create_user", "to": "users.models.User.create", "call_type": "direct"}
    ]
  },

  "statistics": {
    "total_functions": 456,
    "by_type": {"pure": 234, "impure": 156, "coordinator": 66},
    "avg_complexity": 4.2,
    "max_depth": 8
  }
}
```

#### `interface_contracts_template.json`

```json
{
  "schema_version": "1.0.0",
  "contracts": [
    {
      "interface_id": "UserManagementAPI",
      "type": "rest_api",
      "description": "User CRUD operations",

      "operations": [
        {
          "operation_id": "create_user",
          "method": "POST",
          "path": "/api/users",
          "request": {
            "content_type": "application/json",
            "schema": {
              "email": {"type": "string", "format": "email", "required": true},
              "password": {"type": "string", "min_length": 8, "required": true},
              "name": {"type": "string", "required": false}
            }
          },
          "response": {
            "success": {
              "status": 201,
              "schema": {
                "id": {"type": "string", "format": "uuid"},
                "email": {"type": "string"},
                "created_at": {"type": "string", "format": "datetime"}
              }
            },
            "errors": [
              {"status": 400, "code": "VALIDATION_ERROR", "when": "Invalid input"},
              {"status": 409, "code": "DUPLICATE_EMAIL", "when": "Email exists"}
            ]
          },
          "side_effects": ["Creates user in database", "Sends welcome email"],
          "idempotent": false
        }
      ],

      "golden_tests": [
        {
          "test_id": "create_user_success",
          "input": {"email": "test@example.com", "password": "securepass123"},
          "expected_status": 201,
          "expected_fields": ["id", "email", "created_at"]
        },
        {
          "test_id": "create_user_duplicate",
          "precondition": "User test@example.com exists",
          "input": {"email": "test@example.com", "password": "securepass123"},
          "expected_status": 409,
          "expected_code": "DUPLICATE_EMAIL"
        }
      ]
    }
  ]
}
```

#### `migration_scope_template.json`

```json
{
  "schema_version": "1.0.0",
  "migration_id": "legacy-modernization-2025",

  "source": {
    "language": "cobol",
    "version": "COBOL-85",
    "platform": "ibm_mainframe",
    "codebase_age_years": 35,
    "approximate_loc": 500000
  },

  "target": {
    "language": "python",
    "version": "3.12",
    "framework": "fastapi",
    "platform": "kubernetes"
  },

  "scope": {
    "type": "incremental",
    "phases": [
      {
        "phase": 1,
        "name": "Core business logic",
        "components": ["calculation_engine", "validation_rules"],
        "priority": "critical"
      },
      {
        "phase": 2,
        "name": "Data access layer",
        "components": ["db2_queries", "file_handlers"],
        "priority": "high"
      }
    ]
  },

  "constraints": {
    "timeline": {
      "start": "2025-01-01",
      "end": "2025-12-31",
      "milestones": ["phase_1_complete: 2025-06-01", "phase_2_complete: 2025-10-01"]
    },
    "team": {
      "cobol_experts": 2,
      "python_developers": 5,
      "qa_engineers": 3
    },
    "budget": "allocated",
    "dependencies": ["mainframe_access", "test_environment", "production_cutover_window"]
  },

  "success_criteria": {
    "functional_parity": "100% of existing functionality preserved",
    "performance": "Equal or better response times",
    "test_coverage": "95% code coverage in target",
    "downtime": "Maximum 4 hours during cutover"
  },

  "risks": [
    {
      "risk": "Undocumented business rules in COBOL",
      "mitigation": "Extended reverse engineering phase with SME interviews",
      "impact": "high"
    },
    {
      "risk": "Data format changes",
      "mitigation": "Comprehensive data migration testing",
      "impact": "medium"
    }
  ]
}
```

## Impact Analysis

### Phase Integration (v4 Hierarchical)

| Phase | Impact | Changes |
|-------|--------|---------|
| **P0_setup** | Minor | Add overhaul-specific setup options |
| **P1_functional_analysis** | None | Uses existing FA workflow after RE |
| **P2_architecture_allocation** | **Major** | New workflows (01e, 01f) added here |
| **P3_development** | Minor | Language-specific implementation using migration output |
| **P4_validation** | Minor | Interface contract validation added |
| **P5_operations** | None | Standard deployment |
| **PM_meta** | None | Standard meta-analysis applies |

### Workflow Integration

```
                        ┌─────────────────┐
                        │   01a-approach  │
                        │   detection     │
                        └────────┬────────┘
                                 │
         ┌───────────────────────┼───────────────────────┐
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  01b-bottom_up  │    │  01c-top_down   │    │  01d-functional │
│  (existing)     │    │  (greenfield)   │    │  (arch only)    │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                                             │
         │ ◄────────────────────┬──────────────────────┘
         │                      │
         │            ┌─────────▼─────────┐
         │            │  01e-reverse_eng  │ ◄── NEW
         │            │  (unknown system) │
         │            └─────────┬─────────┘
         │                      │
         │            ┌─────────▼─────────┐
         │            │  01f-language_mig │ ◄── NEW
         │            │  (modernization)  │
         │            └─────────┬─────────┘
         │                      │
         └──────────────────────┴──────────────────────┐
                                                       │
                                              ┌────────▼────────┐
                                              │  02-artifacts   │
                                              │  visualization  │
                                              └─────────────────┘
```

### Affected Components

1. **Workflows** (4 new, 3 modified):
   - `workflows/01e-reverse_engineering.json` (NEW)
   - `workflows/01f-language_migration.json` (NEW)
   - `workflows/01a-approach_detection.json` (MODIFY - add overhaul detection)
   - `workflows/phases/P2_architecture_allocation/phase_definition.json` (MODIFY)
   - `workflow_steps/reverse_engineering/` (NEW directory, 7 step files)
   - `workflow_steps/language_migration/` (NEW directory, 9 step files)

2. **Tools** (12 new):
   - `tools/analyze_codebase.py` (NEW)
   - `tools/extract_functions.py` (NEW)
   - `tools/detect_interfaces.py` (NEW)
   - `tools/synthesize_architecture.py` (NEW)
   - `tools/infer_service_boundaries.py` (NEW)
   - `tools/validate_extraction.py` (NEW)
   - `tools/extract_interface_contracts.py` (NEW)
   - `tools/generate_interface_tests.py` (NEW)
   - `tools/define_translation_rules.py` (NEW)
   - `tools/translate_component.py` (NEW)
   - `tools/validate_interface_preservation.py` (NEW)
   - `tools/generate_migration_report.py` (NEW)

3. **Templates** (8 new):
   - `templates/codebase_inventory_template.json` (NEW)
   - `templates/extracted_functions_template.json` (NEW)
   - `templates/detected_interfaces_template.json` (NEW)
   - `templates/inferred_services_template.json` (NEW)
   - `templates/extraction_validation_template.json` (NEW)
   - `templates/interface_contracts_template.json` (NEW)
   - `templates/translation_rules_template.json` (NEW)
   - `templates/migration_scope_template.json` (NEW)

4. **Documentation** (2 new):
   - `docs/REVERSE_ENGINEERING_GUIDE.md` (NEW)
   - `docs/LANGUAGE_MIGRATION_GUIDE.md` (NEW)
   - `CLAUDE.md` (MODIFY - add overhaul guidance)

### Breaking Changes

**None** - This is purely additive. Existing workflows continue to work unchanged.

### New Directory Structure

```
{system_root}/
├── specs/
│   ├── reverse/                           # NEW - reverse engineering artifacts
│   │   ├── codebase_inventory.json
│   │   ├── extracted_functions.json
│   │   ├── detected_interfaces.json
│   │   ├── inferred_services.json
│   │   └── extraction_validation_report.json
│   ├── migration/                         # NEW - migration artifacts
│   │   ├── migration_scope.json
│   │   ├── interface_contracts.json
│   │   ├── translation_rules.json
│   │   ├── cutover_plan.json
│   │   └── integration_test_results.json
│   ├── functional/                        # EXISTING - populated by RE workflow
│   │   └── functional_architecture.json
│   └── machine/                           # EXISTING
├── tests/
│   └── migration/                         # NEW - migration test artifacts
│       └── interface_tests/
└── docs/
    ├── REVERSE_ENGINEERING_REPORT.md      # NEW
    └── MIGRATION_REPORT.md                # NEW
```

## Implementation Plan

### Phase 1: Reverse Engineering Foundation (Week 1-2)

1. Create `workflows/01e-reverse_engineering.json`
2. Create `workflow_steps/reverse_engineering/` with RE-01 through RE-07
3. Create templates: `codebase_inventory_template.json`, `extracted_functions_template.json`
4. Create core tools: `analyze_codebase.py`, `extract_functions.py`
5. Update `01a-approach_detection.json` to detect "overhaul" scenarios

### Phase 2: Interface & Architecture Synthesis (Week 2-3)

1. Create tools: `detect_interfaces.py`, `synthesize_architecture.py`
2. Create templates: `detected_interfaces_template.json`, `inferred_services_template.json`
3. Create tools: `infer_service_boundaries.py`, `validate_extraction.py`
4. Create template: `extraction_validation_template.json`
5. Test RE workflow end-to-end on sample legacy codebase

### Phase 3: Language Migration Foundation (Week 3-4)

1. Create `workflows/01f-language_migration.json`
2. Create `workflow_steps/language_migration/` with LM-01 through LM-09
3. Create templates: `migration_scope_template.json`, `interface_contracts_template.json`
4. Create tools: `extract_interface_contracts.py`, `generate_interface_tests.py`

### Phase 4: Translation Engine (Week 4-5)

1. Create `translation_rules_template.json`
2. Create tools: `define_translation_rules.py`, `translate_component.py`
3. Create tool: `validate_interface_preservation.py`
4. Create tool: `generate_migration_report.py`
5. Test LM workflow on Python 2 → Python 3 migration

### Phase 5: Integration & Documentation (Week 5-6)

1. Update `workflows/phases/P2_architecture_allocation/phase_definition.json`
2. Update `workflow_master.json` (if needed)
3. Create `docs/REVERSE_ENGINEERING_GUIDE.md`
4. Create `docs/LANGUAGE_MIGRATION_GUIDE.md`
5. Update `CLAUDE.md` with overhaul guidance
6. End-to-end testing with multiple language pairs

## Success Criteria

1. ✅ RE workflow extracts functional architecture from unknown Python codebase
2. ✅ RE workflow extracts functional architecture from unknown Java codebase
3. ✅ LM workflow migrates Python 2 → Python 3 with interface preservation
4. ✅ LM workflow migrates simple COBOL → Python (proof of concept)
5. ✅ Interface test suite validates behavior preservation
6. ✅ All tools have CONTRACT.json files (v3.22.0 pattern)
7. ✅ Integration with existing Reflow workflows (01b, 01d, etc.)
8. ✅ Documentation complete and tested

## Testing Strategy

### Test Cases for GAN Testing (97-GAN-inspired-test.json)

1. **TC-RE-001**: Reverse engineer sample Django application
2. **TC-RE-002**: Reverse engineer sample Java Spring Boot application
3. **TC-RE-003**: Reverse engineer multi-language project (Python + JavaScript)
4. **TC-LM-001**: Migrate Python 2.7 CLI tool to Python 3.12
5. **TC-LM-002**: Migrate sync Python to async Python (requests → httpx)
6. **TC-LM-003**: Migrate simple Java class to Kotlin (proof of concept)

### Interface Preservation Validation

For each migration:
1. Extract interface contracts from source
2. Generate golden test cases
3. Run tests against source implementation (baseline)
4. Run tests against target implementation
5. Compare results - 100% match required

## Open Questions

1. **Q: How deep should function extraction go?**
   - Proposal: Configurable depth (module-level, class-level, method-level)
   - Default: Method-level for small codebases, class-level for large

2. **Q: Should we support non-textual code (binary, compiled)?**
   - Proposal: v1.0 focuses on source code only
   - Future: Could add decompiler integration

3. **Q: How to handle undocumented business rules?**
   - Proposal: Flag as "UNKNOWN_RULE" in extraction, require SME review
   - Tool generates interview questions for domain experts

4. **Q: Cross-language dependency mapping completeness?**
   - Proposal: Start with common mappings (Python ↔ TypeScript, Java ↔ Kotlin)
   - Allow user-defined mappings in translation_rules.json

## Approval

This change proposal requires approval before implementation per RFU-01/FU-01 gate.

**Change Type**: Major Feature Addition
**Version Impact**: Minor version bump (4.0.x → 4.1.0)

---

**Prepared by**: Claude (LLM Agent)
**Date**: 2025-12-05
**Status**: PENDING APPROVAL
