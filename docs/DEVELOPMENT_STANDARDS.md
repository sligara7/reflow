# Development Standards Configuration System

**Version**: 3.20.0
**Created**: 2025-11-23

## Overview

The Development Standards Configuration System establishes language-specific defaults for development tooling, with user preference overrides. It eliminates repeated decision prompts by configuring standards once during setup (S-03-A07) and using them throughout the development workflow.

## Quick Start

### During Setup (S-03-A07)

The LLM will prompt you:

```
For Python, the recommended development standards are:
- Interface Strategy: Protocol + DI (structural typing, no metaclass conflicts)
- Dependency Manager: Hatchling (PEP 517/518/621 compliant)
- Lock Files: Generate (reproducible builds)
- Testing: pytest
- Linting: ruff

Would you like to:
1. Accept these defaults (recommended)
2. Customize one or more settings
3. Skip (will use defaults when needed)
```

### File Location

```
{system_root}/specs/development/development_standards.json
```

## Python Standards

### Interface Strategy (Default: Protocol + DI)

| Option | Description | When to Use |
|--------|-------------|-------------|
| `protocol_di` | Python Protocols with Dependency Injection | **Recommended** - no metaclass conflicts, structural typing |
| `abc` | Abstract Base Classes | Legacy systems, simple inheritance patterns |
| `manual` | No generation | Custom implementation |

**Why Protocol + DI?**
- No metaclass conflicts with FastAPI, SQLAlchemy, Pydantic
- Multiple implementations without inheritance coupling
- Easy testing with mock implementations
- Different implementations per facility/environment

### Dependency Manager (Default: Hatchling)

| Option | Lock Files | Speed | Standards |
|--------|------------|-------|-----------|
| `hatchling` | pip-tools | Fast | PEP 517/518/621 |
| `poetry` | poetry.lock | Medium | PEP 517 |
| `uv` | uv.lock | Very Fast | PEP 517/518/621 |
| `setuptools` | pip-tools | Slow | Legacy |

**Why Hatchling?**
- Minimal configuration (just pyproject.toml)
- PEP 517/518/621 compliant
- Fast build times
- Active development

### Lock File Generation (Default: true)

Lock files ensure reproducible builds across environments:

| Manager | Lock Tool | Command |
|---------|-----------|---------|
| hatchling | pip-tools | `pip-compile pyproject.toml -o requirements.lock` |
| poetry | built-in | `poetry lock` |
| uv | built-in | `uv lock` |

### Web Framework (Default: FastAPI)

| Option | Type | Async | OpenAPI |
|--------|------|-------|---------|
| `fastapi` | Modern | Yes | Auto |
| `flask` | Traditional | No* | Manual |
| `django` | Full-stack | Yes** | DRF |
| `litestar` | Modern | Yes | Auto |

*Flask-async available
**Django 4.1+ async views

### Additional Standards

| Setting | Default | Alternatives |
|---------|---------|--------------|
| ORM | `sqlalchemy` | sqlmodel, tortoise, raw_sql |
| Configuration | `pydantic_settings` | python_dotenv, dynaconf |
| Logging | `structlog` | stdlib_logging, loguru |
| HTTP Client | `httpx` | requests, aiohttp |
| Testing | `pytest` | unittest |
| Linting | `ruff` | flake8_black, pylint |
| Type Checking | `mypy` | pyright |

## Service Organization Strategy

During functional allocation (FA-07), the LLM analyzes your functional architecture to recommend a service organization strategy:

### Analysis Criteria

1. **Coordination Complexity**: Functions with coordination keywords (lock, synchronize, queue)
2. **Workflow Span**: Do workflows cross domain boundaries?
3. **Operation Types**: CRUD vs workflow-heavy operations

### Strategies

| Strategy | When | Example Services |
|----------|------|------------------|
| **Workflow-based** | High coordination, cross-domain, workflow-heavy | ExperimentExecutionService, DataPipelineService |
| **Domain-based** | Low coordination, single-domain, CRUD-heavy | UserService, DeviceService, ConfigService |
| **Hybrid** | Mixed characteristics | WorkflowOrchestrator + DeviceRegistry |

### Example Prompt

```
Based on functional architecture analysis:
- Coordination Complexity: HIGH (5 coordination points)
- Workflow Span: CROSS-DOMAIN (70% flows cross domains)
- Operations: WORKFLOW-HEAVY (75% workflows, 25% CRUD)

Recommendation: Workflow-based organization
This keeps coordination logic local and makes workflows self-contained.

Would you like to:
1. Accept workflow-based (recommended)
2. Use domain-based instead
3. Use hybrid approach
```

## Tools

### configure_development_standards.py

Configure development standards interactively or with defaults:

```bash
# Create with defaults for Python
python3 tools/configure_development_standards.py /path/to/system --language python --use-defaults

# Show Python defaults
python3 tools/configure_development_standards.py /path/to/system --language python --show-defaults

# Validate existing configuration
python3 tools/configure_development_standards.py /path/to/system --validate
```

### generate_python_project.py

Generate Python project structure based on standards:

```bash
# Generate service with auto-detected standards
python3 tools/generate_python_project.py /path/to/system --service user_service

# Dry run to see what would be generated
python3 tools/generate_python_project.py /path/to/system --service api_gateway --dry-run
```

**Generated Structure**:
```
services/{service_name}/
├── pyproject.toml          # Based on dependency_manager setting
├── src/
│   └── {service_name}/
│       ├── __init__.py
│       ├── main.py         # Based on web_framework setting
│       └── py.typed
├── tests/
│   ├── __init__.py
│   └── test_main.py        # Based on testing_framework setting
├── README.md
└── .ruff.toml              # If linting=ruff
```

## Workflow Integration

### When Standards Are Used

| Workflow Step | Uses Standards For |
|---------------|-------------------|
| S-03-A07 | Initial configuration |
| D-01-A04.5 | Interface contract strategy |
| D-01-A04.6 | Python project generation |
| FA-07 | Service organization strategy |

### Fallback Behavior

If `development_standards.json` doesn't exist when needed:
1. D-01-A04.5 uses `protocol_di` as default
2. D-01-A04.6 creates pyproject.toml with hatchling defaults
3. FA-07 prompts user for service organization (no default)

## File Format

```json
{
  "schema_version": "1.0.0",
  "created": "2025-11-23T10:00:00Z",
  "primary_language": {
    "language": "python",
    "version": "3.11+"
  },
  "language_standards": {
    "python": {
      "interface_strategy": {
        "value": "protocol_di",
        "user_customized": false
      },
      "dependency_manager": {
        "value": "hatchling",
        "user_customized": false
      },
      "lock_file_generation": {
        "value": true,
        "user_customized": false
      }
      // ... additional settings
    }
  },
  "service_organization": {
    "strategy": {
      "value": "workflow_based",
      "user_customized": false
    },
    "analysis_results": {
      "coordination_complexity": "high",
      "workflow_span": "cross_domain",
      "operation_types": "workflow_heavy"
    }
  }
}
```

## Migration from v3.18.0

**No migration required**. If `development_standards.json` doesn't exist:
- D-01-A04.5 falls back to previous behavior (prompts user)
- New systems will have standards configured during S-03-A07

## Related Documentation

- `docs/ARCHITECTURAL_PATTERNS_PROTOCOLS_DI.md` - Protocol + DI patterns
- `docs/changes/CHANGE_PROPOSAL_20251123_DEVELOPMENT_STANDARDS.md` - Full change proposal
- `templates/development_standards_template.json` - Template schema
