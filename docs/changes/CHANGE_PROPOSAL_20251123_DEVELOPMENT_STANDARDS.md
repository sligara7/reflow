# Change Proposal: Development Standards Configuration System

**Date**: 2025-11-23
**Proposal ID**: CP-2025-11-23-001
**Feature**: Development Standards Configuration - Language-specific defaults with user preference overrides
**Priority**: High
**Workflow Version**: 3.19.x → 3.20.0

## Executive Summary

Introduce a **Development Standards Configuration System** that establishes sensible defaults for each programming language while allowing users to customize via a structured preference file. For Python, the **standards** become:
- **Interface Contracts**: Python typing Protocols with Dependency Injection (not ABC)
- **Dependency Management**: Hatchling (modern, standards-compliant)
- **Project Structure**: pyproject.toml-based configuration

The system:
1. Creates `development_standards.json` with language-specific defaults
2. Prompts users during setup (S-03 or D-01) to confirm/customize preferences
3. Uses preferences to drive template generation and tool selection throughout development workflow

## Business Justification

### Current State (v3.18.0)

- Protocol-based interfaces exist but are **optional** (user must choose)
- ABC is still the default mental model
- No dependency management configuration - defaults to `pip install` examples
- No `pyproject.toml` generation
- Preferences scattered across multiple files (`development_language_configuration.json`, `working_memory.json`)

### Problems

1. **Analysis Paralysis**: Users must choose at D-01-A04.5 without context
2. **Inconsistent Defaults**: Different tools assume different package managers
3. **No Standard Project Structure**: Each system ends up with ad-hoc configuration
4. **Fragmented Preferences**: Hard to know where preferences are stored/used

### Proposed Solution

1. **Development Standards Configuration** (`development_standards.json`)
   - Centralized file for all development preferences
   - Language-specific sections with sensible defaults
   - User preferences stored alongside defaults with rationale

2. **Python Standards** (when Python is primary language)
   - Interface Strategy: **Protocol + DI** (default, not optional)
   - Dependency Manager: **Hatchling** (default)
   - Project Config: **pyproject.toml** (standard)
   - Testing: **pytest** (default)
   - Linting: **ruff** (default)

3. **LLM-Prompted Customization**
   - During S-03 (after foundational docs) or D-01 (before bootstrap)
   - Present defaults with rationale, ask if user wants to customize
   - Store choices with user's rationale

4. **Language-Agnostic Equivalents**
   - TypeScript: npm/pnpm/bun, interfaces, vitest/jest
   - Rust: Cargo (no choice), traits, built-in testing
   - Go: go mod (no choice), interfaces, go test
   - Java: Maven/Gradle, interfaces, JUnit

### Impact

**Time Savings**: 2-4 hours per project setup
- No more analysis paralysis at decision points
- Consistent project structure reduces cognitive load
- Template generation uses correct tooling automatically

**Quality Improvement**
- Modern Python packaging (PEP 517/518/621 compliant)
- Consistent development experience across projects
- Type-safe interfaces from the start

## Feature Description

### 1. New Configuration File: `development_standards.json`

**Location**: `{system_root}/specs/development/development_standards.json`

**Structure**:
```json
{
  "schema_version": "1.0.0",
  "created": "2025-11-23T10:00:00Z",
  "last_modified": "2025-11-23T10:00:00Z",
  "llm_prompted": true,

  "primary_language": {
    "language": "python",
    "version": "3.11+",
    "selection_rationale": "User specified Python for ML/data science capabilities"
  },

  "language_standards": {
    "python": {
      "interface_strategy": {
        "value": "protocol_di",
        "options": ["protocol_di", "abc", "manual"],
        "default": "protocol_di",
        "user_customized": false,
        "rationale": "Protocol + DI provides structural typing, no metaclass conflicts, and easy testing via dependency injection"
      },
      "dependency_manager": {
        "value": "hatchling",
        "options": ["hatchling", "poetry", "uv", "setuptools", "pip_requirements"],
        "default": "hatchling",
        "user_customized": false,
        "rationale": "Hatchling is PEP 517/518/621 compliant, fast, and requires minimal configuration"
      },
      "lock_file_generation": {
        "value": true,
        "options": [true, false],
        "default": true,
        "lock_tool_by_manager": {
          "hatchling": "pip-tools (pip-compile)",
          "poetry": "poetry.lock (built-in)",
          "uv": "uv.lock (built-in)",
          "setuptools": "pip-tools (pip-compile)",
          "pip_requirements": "pip-tools (pip-compile)"
        },
        "user_customized": false,
        "rationale": "Lock files ensure reproducible builds across environments"
      },
      "project_config": {
        "value": "pyproject_toml",
        "options": ["pyproject_toml", "setup_py", "setup_cfg"],
        "default": "pyproject_toml",
        "user_customized": false,
        "rationale": "pyproject.toml is the modern Python standard (PEP 518/621)"
      },
      "testing_framework": {
        "value": "pytest",
        "options": ["pytest", "unittest", "nose2"],
        "default": "pytest",
        "user_customized": false,
        "rationale": "pytest is the de facto standard with excellent ecosystem support"
      },
      "linting": {
        "value": "ruff",
        "options": ["ruff", "flake8_black", "pylint", "none"],
        "default": "ruff",
        "user_customized": false,
        "rationale": "ruff replaces flake8, black, isort with a single fast tool"
      },
      "type_checking": {
        "value": "mypy",
        "options": ["mypy", "pyright", "none"],
        "default": "mypy",
        "user_customized": false,
        "rationale": "mypy is the standard, pyright is faster but less ecosystem support"
      },
      "web_framework": {
        "value": "fastapi",
        "options": ["fastapi", "flask", "django", "litestar", "none"],
        "default": "fastapi",
        "user_customized": false,
        "rationale": "FastAPI is async-native with automatic OpenAPI docs and excellent typing support"
      },
      "orm": {
        "value": "sqlalchemy",
        "options": ["sqlalchemy", "sqlmodel", "tortoise", "raw_sql", "none"],
        "default": "sqlalchemy",
        "user_customized": false,
        "rationale": "SQLAlchemy 2.0 is the industry standard with excellent typing support"
      },
      "configuration": {
        "value": "pydantic_settings",
        "options": ["pydantic_settings", "python_dotenv", "dynaconf", "none"],
        "default": "pydantic_settings",
        "user_customized": false,
        "rationale": "Pydantic Settings provides type-safe configuration with validation"
      },
      "logging": {
        "value": "structlog",
        "options": ["structlog", "stdlib_logging", "loguru"],
        "default": "structlog",
        "user_customized": false,
        "rationale": "structlog provides structured JSON logs ideal for observability"
      },
      "http_client": {
        "value": "httpx",
        "options": ["httpx", "requests", "aiohttp"],
        "default": "httpx",
        "user_customized": false,
        "rationale": "httpx is async-native with an API similar to requests"
      }
    },

    "typescript": {
      "interface_strategy": {
        "value": "typescript_interfaces",
        "options": ["typescript_interfaces", "manual"],
        "default": "typescript_interfaces",
        "user_customized": false,
        "rationale": "TypeScript interfaces are the native structural typing mechanism"
      },
      "package_manager": {
        "value": "pnpm",
        "options": ["pnpm", "npm", "yarn", "bun"],
        "default": "pnpm",
        "user_customized": false,
        "rationale": "pnpm is fast, disk-efficient, and strict about dependencies"
      },
      "testing_framework": {
        "value": "vitest",
        "options": ["vitest", "jest", "mocha"],
        "default": "vitest",
        "user_customized": false,
        "rationale": "vitest is fast, ESM-native, and compatible with Vite projects"
      },
      "linting": {
        "value": "eslint_prettier",
        "options": ["eslint_prettier", "biome", "none"],
        "default": "eslint_prettier",
        "user_customized": false,
        "rationale": "ESLint + Prettier is the established standard for TypeScript"
      }
    },

    "rust": {
      "interface_strategy": {
        "value": "traits",
        "options": ["traits"],
        "default": "traits",
        "user_customized": false,
        "rationale": "Rust traits are the only interface mechanism"
      },
      "build_system": {
        "value": "cargo",
        "options": ["cargo"],
        "default": "cargo",
        "user_customized": false,
        "rationale": "Cargo is the only build system for Rust"
      }
    },

    "go": {
      "interface_strategy": {
        "value": "interfaces",
        "options": ["interfaces"],
        "default": "interfaces",
        "user_customized": false,
        "rationale": "Go interfaces are implicit and the only interface mechanism"
      },
      "module_system": {
        "value": "go_mod",
        "options": ["go_mod"],
        "default": "go_mod",
        "user_customized": false,
        "rationale": "Go modules are the standard dependency system"
      }
    },

    "java": {
      "interface_strategy": {
        "value": "interfaces",
        "options": ["interfaces", "abstract_classes"],
        "default": "interfaces",
        "user_customized": false,
        "rationale": "Java interfaces provide clean contracts without implementation coupling"
      },
      "build_system": {
        "value": "gradle",
        "options": ["gradle", "maven"],
        "default": "gradle",
        "user_customized": false,
        "rationale": "Gradle is more flexible and faster than Maven"
      },
      "testing_framework": {
        "value": "junit5",
        "options": ["junit5", "junit4", "testng"],
        "default": "junit5",
        "user_customized": false,
        "rationale": "JUnit 5 is the modern standard with better extension model"
      }
    }
  },

  "cross_cutting": {
    "containerization": {
      "value": "docker",
      "options": ["docker", "podman", "none"],
      "default": "docker",
      "user_customized": false,
      "rationale": "Docker is the industry standard for containerization"
    },
    "ci_cd": {
      "value": "github_actions",
      "options": ["github_actions", "gitlab_ci", "jenkins", "none"],
      "default": "github_actions",
      "user_customized": false,
      "rationale": "GitHub Actions integrates well with GitHub-hosted repositories"
    }
  },

  "service_organization": {
    "strategy": {
      "value": null,
      "options": ["workflow_based", "domain_based", "hybrid"],
      "default": null,
      "user_customized": false,
      "rationale": null,
      "note": "Set during functional allocation (FA-07 or SE-01) based on LLM analysis"
    },
    "analysis_results": {
      "coordination_complexity": null,
      "workflow_span": null,
      "operation_types": null,
      "recommendation": null,
      "recommendation_rationale": null
    },
    "allocation_details": {
      "workflow_services": [],
      "domain_services": [],
      "shared_services": []
    }
  },

  "user_notes": "Project uses Python for backend services with FastAPI. TypeScript for frontend."
}
```

### 2. Workflow Integration: New Step S-03-A07

**New action in S-03 (Foundational Documents)**:

```json
{
  "action_id": "S-03-A07",
  "description": "Configure Development Standards",
  "purpose": "Establish language-specific development standards with user input",
  "llm_prompt": {
    "introduction": "I'll now configure development standards for your project. Each language has sensible defaults based on modern best practices.",
    "per_language_prompt": "For {LANGUAGE}, the recommended standards are:\n\n- Interface Strategy: {DEFAULT_INTERFACE} - {RATIONALE}\n- Dependency Manager: {DEFAULT_DEP_MANAGER} - {RATIONALE}\n- Testing: {DEFAULT_TESTING} - {RATIONALE}\n\nWould you like to:\n1. Accept these defaults (recommended)\n2. Customize one or more settings\n3. Skip configuration (will use defaults later)",
    "customization_prompt": "Which setting would you like to customize?\n{OPTIONS_WITH_DESCRIPTIONS}",
    "confirmation": "Development standards configured. Stored in specs/development/development_standards.json"
  },
  "outputs": [
    "specs/development/development_standards.json"
  ],
  "blocking": false,
  "skip_condition": "If user says 'skip' or project is brownfield with existing configuration"
}
```

### 3. Template Generation: New Tool `generate_python_project.py`

**Purpose**: Generate project structure based on development standards

**Usage**:
```bash
python3 {reflow_root}/tools/generate_python_project.py {system_root} \
  --standards specs/development/development_standards.json \
  --service {service_name}
```

**Generated Files** (for hatchling + pytest + ruff):
```
{service_name}/
├── pyproject.toml          # Hatchling configuration
├── src/
│   └── {service_name}/
│       ├── __init__.py
│       └── main.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── .ruff.toml              # Ruff configuration
```

**Example `pyproject.toml`** (generated):
```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{service_name}"
version = "0.1.0"
description = "Generated by Reflow"
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
dependencies = [
    "fastapi>=0.104.0",
    "uvicorn[standard]>=0.24.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=7.4.0",
    "pytest-cov>=4.1.0",
    "pytest-asyncio>=0.21.0",
    "ruff>=0.1.0",
    "mypy>=1.7.0",
]

[tool.hatch.build.targets.wheel]
packages = ["src/{service_name}"]

[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"

[tool.ruff]
line-length = 88
target-version = "py311"
select = ["E", "F", "I", "N", "W", "UP"]

[tool.mypy]
python_version = "3.11"
strict = true
```

### 4. Updated D-01-A04.5: Interface Contract Generation

**Changed behavior**: Instead of asking user for choice, **use development_standards.json**:

```json
{
  "action_id": "D-01-A04.5",
  "description": "Generate interface contracts based on development standards",
  "behavior": {
    "read": "specs/development/development_standards.json",
    "if_interface_strategy_is_protocol_di": {
      "tool": "generate_interface_protocols.py",
      "outputs": ["services/common/protocols/", "services/common/di/"]
    },
    "if_interface_strategy_is_abc": {
      "tool": "generate_interface_abc.py",
      "outputs": ["services/{service}/interfaces/"]
    },
    "if_interface_strategy_is_manual": {
      "action": "Skip generation, user will implement manually"
    }
  },
  "no_user_prompt": true,
  "uses_preference_from": "development_standards.json → language_standards.{language}.interface_strategy"
}
```

### 5. New Template: `development_standards_template.json`

**Location**: `templates/development_standards_template.json`

Provides the schema and defaults for `development_standards.json`.

## Impact Analysis

### Affected Components

1. **Workflows** (3 files modified):
   - `workflow_steps/setup/S-03-FoundationalDocs.json` - Add S-03-A07
   - `workflow_steps/development/D-01-InitBootstrap.json` - Update D-01-A04.5 to read standards
   - `workflow_steps/development/D-01-InitBootstrap.json` - Update D-01.4 to use standards for project setup

2. **Tools** (2 new tools):
   - `tools/generate_python_project.py` (NEW) - Generate pyproject.toml, structure
   - `tools/configure_development_standards.py` (NEW) - Interactive standards configuration

3. **Templates** (3 new templates):
   - `templates/development_standards_template.json` (NEW) - Standards schema
   - `templates/pyproject_toml_hatchling_template.toml` (NEW) - Hatchling pyproject.toml
   - `templates/pyproject_toml_poetry_template.toml` (NEW) - Poetry alternative

4. **Documentation** (3 files):
   - `docs/DEVELOPMENT_STANDARDS.md` (NEW) - Standards guide
   - `CLAUDE.md` - Add development standards guidance
   - `docs/TOOL_USAGE_SUMMARY.md` - Add new tool documentation

### Breaking Changes

**Minor behavioral change**:
- D-01-A04.5 no longer prompts for interface strategy (uses standards file)
- If `development_standards.json` doesn't exist, falls back to current behavior (prompt user)

**Migration path**: Existing systems without `development_standards.json` continue to work - standards file is created on next S-03 execution or can be manually created.

### New Directory Structure

```
{system_root}/
├── specs/
│   └── development/               # NEW directory
│       └── development_standards.json
├── services/
│   └── {service_name}/
│       ├── pyproject.toml         # NEW (generated)
│       ├── src/
│       └── tests/
```

## Python-Specific Standards Rationale

### Why Hatchling (over Poetry, setuptools)?

| Criteria | Hatchling | Poetry | setuptools |
|----------|-----------|--------|------------|
| PEP 517/518/621 | ✅ Full | ✅ Full | ⚠️ Partial |
| Configuration | Minimal | More verbose | Complex |
| Speed | Fast | Medium | Slow |
| Lock files | No (use pip-tools) | Yes | No |
| Workspace support | Yes | Experimental | No |
| Standards-compliant | ✅ Pure pyproject.toml | ✅ Plus poetry-specific | ⚠️ Needs setup.py/cfg |

**Decision**: Hatchling is standards-compliant, minimal configuration, and fast. For users who need lock files, they can customize to Poetry or use pip-tools alongside Hatchling.

### Why Protocol + DI as Default (not ABC)?

| Criteria | Protocol + DI | ABC |
|----------|---------------|-----|
| Metaclass conflicts | None | Conflicts with FastAPI, SQLAlchemy, Pydantic |
| Structural typing | Yes | No (nominal) |
| Multiple implementations | Easy | Requires inheritance |
| Testing (mocking) | Easy (inject mock) | Harder (mock inheritance) |
| Learning curve | Slightly higher | Familiar |

**Decision**: Protocol + DI is the modern approach that avoids metaclass conflicts common in Python web frameworks. ABCs remain available for users who prefer them.

### Why Ruff (over flake8 + black + isort)?

| Criteria | Ruff | flake8 + black + isort |
|----------|------|------------------------|
| Speed | 10-100x faster | Baseline |
| Single tool | Yes | Three tools |
| Configuration | Single file | Three files |
| Compatibility | Drop-in replacement | N/A |

**Decision**: Ruff provides the same functionality in a single, much faster tool.

### Why uv as an Option?

| Criteria | uv | pip | poetry |
|----------|-----|-----|--------|
| Speed | 10-100x faster | Baseline | 2-5x faster |
| Lock files | Yes (uv.lock) | No (use pip-tools) | Yes |
| Maturity | New (2024) | Mature | Mature |
| Compatibility | pip-compatible | N/A | Separate ecosystem |

**Decision**: uv is added as an option (not default) due to its speed. Users who want bleeding-edge tooling can opt in. Default remains hatchling for stability.

### Lock File Generation

| Tool | Lock File Support | Notes |
|------|-------------------|-------|
| Hatchling | No (use pip-tools) | `pip-compile` generates `requirements.lock` |
| Poetry | Yes (poetry.lock) | Built-in |
| uv | Yes (uv.lock) | Built-in |
| pip | No | Use pip-tools |

**Decision**: Lock file generation is a separate preference. Default: **generate lock files** using the appropriate tool for the chosen dependency manager.

### Additional Python Standards (Frameworks & Libraries)

| Category | Default | Alternatives | Rationale |
|----------|---------|--------------|-----------|
| **Web Framework** | FastAPI | Flask, Django, Litestar, None | Async-native, auto OpenAPI docs, excellent typing |
| **ORM** | SQLAlchemy 2.0 | SQLModel, Tortoise, raw SQL, None | Industry standard, excellent typing in v2.0 |
| **Configuration** | Pydantic Settings | python-dotenv, dynaconf | Type-safe config with validation |
| **Logging** | structlog | stdlib logging, loguru | Structured JSON logs for observability |
| **HTTP Client** | httpx | requests, aiohttp | Async-native, similar API to requests |
| **Serialization** | Pydantic | marshmallow, attrs | Already required by FastAPI |

**Note**: These are recommendations shown during S-03-A07. User can accept, customize, or mark as "not applicable" for their project.

### Service Organization Strategy (Functional Allocation)

**Integration with SE-01/FU-02 (Functional Allocation)**:

The LLM analyzes the functional architecture and recommends a service organization strategy:

| Strategy | When Recommended | Characteristics |
|----------|------------------|-----------------|
| **Workflow-based** | High coordination, cross-domain flows, workflow-heavy | Services grouped by user workflows (e.g., ExperimentExecutionService) |
| **Domain-based** | Low coordination, single-domain, CRUD-heavy | Services grouped by business domain (e.g., UserService, DeviceService) |
| **Hybrid** | Mixed characteristics | Workflow services for complex flows + domain services for shared resources |

**Analysis Criteria**:
1. **Coordination Complexity**: Count functions with coordination keywords (lock, synchronize, queue)
2. **Workflow Span**: Do primary workflows cross multiple domains?
3. **Operation Types**: Ratio of workflow operations vs CRUD operations

**Storage**: Choice stored in `development_standards.json` → `service_organization.strategy`

**User Experience** (during FA-07 or SE-01):
> "Based on functional architecture analysis:
> - Coordination Complexity: **HIGH** (5 coordination points)
> - Workflow Span: **CROSS-DOMAIN** (workflows span 3 domains)
> - Operations: **WORKFLOW-HEAVY** (70% workflows, 30% CRUD)
>
> **Recommendation: Workflow-based organization**
> This keeps coordination logic local and makes workflows self-contained.
>
> Would you like to:
> 1. Accept workflow-based (recommended)
> 2. Use domain-based instead
> 3. Use hybrid approach"

## Implementation Plan

### Phase 1: Core Infrastructure (Day 1-2)
1. Create `development_standards_template.json`
2. Create `configure_development_standards.py` tool
3. Add S-03-A07 to setup workflow
4. Update `working_memory_template.json` to reference standards

### Phase 2: Python Project Generation (Day 2-3)
1. Create `generate_python_project.py` tool
2. Create `pyproject_toml_hatchling_template.toml`
3. Create `pyproject_toml_poetry_template.toml` (alternative)
4. Integrate with D-01.4 (language-specific setup)

### Phase 3: Protocol/DI Integration (Day 3-4)
1. Update D-01-A04.5 to read standards instead of prompting
2. Update `generate_interface_protocols.py` to use standards
3. Test Protocol generation with hatchling project structure

### Phase 4: Documentation & Testing (Day 4-5)
1. Create `docs/DEVELOPMENT_STANDARDS.md`
2. Update CLAUDE.md with new guidance
3. Test end-to-end: S-03 → D-01 → project generation
4. Create example project demonstrating standards

## Success Criteria

1. ✅ `development_standards.json` created during S-03-A07
2. ✅ LLM presents defaults with clear rationale
3. ✅ User can accept defaults or customize
4. ✅ D-01-A04.5 uses standards without re-prompting
5. ✅ Python project generates with pyproject.toml (hatchling)
6. ✅ Generated project passes `hatch build` and `pytest`
7. ✅ Protocol + DI interfaces generated correctly
8. ✅ Standards file is human-readable and editable
9. ✅ Existing systems without standards file continue to work

## Questions & Decisions

### Resolved

1. **Q: Should standards be per-project or per-user?**
   **A**: Per-project (stored in `specs/development/`). Different projects may have different requirements.

2. **Q: What if user skips S-03-A07?**
   **A**: D-01 will create standards file with defaults if it doesn't exist.

3. **Q: How to handle multi-language projects?**
   **A**: Standards file has sections per language. Primary language gets full setup; secondary languages get interface generation only.

### Open

1. **Q: Should we support uv as dependency manager option?**
   - uv is very new but extremely fast
   - Recommend adding as option with note "experimental"

2. **Q: Should lock file generation be separate preference?**
   - Hatchling doesn't generate lock files
   - Could add `lock_file_tool: pip-tools | pip-compile | none` preference

## Approval

This change proposal requires approval before implementation per RFU-01/FU-01 gate.

**Change Type**: Feature Addition (minor breaking - behavioral change in D-01-A04.5)
**Version Impact**: Minor version bump (3.19.x → 3.20.0)

---

**Prepared by**: Claude (LLM Agent)
**Date**: 2025-11-23
**Status**: PENDING APPROVAL
