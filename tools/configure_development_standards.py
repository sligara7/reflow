#!/usr/bin/env python3
"""
Configure Development Standards Tool

Creates and manages development_standards.json for a system, establishing
language-specific defaults with user preference overrides.

Usage:
    python3 configure_development_standards.py <system_root> [options]

Options:
    --language <lang>       Primary language (python, typescript, rust, go, java)
    --use-defaults          Accept all defaults without prompting
    --customize <setting>   Customize a specific setting (can be repeated)
    --show-defaults         Show defaults for a language and exit
    --validate              Validate existing development_standards.json
    --reflow-root <path>    Path to Reflow root (for template)

Examples:
    # Create with defaults for Python
    python3 configure_development_standards.py /path/to/system --language python --use-defaults

    # Show Python defaults
    python3 configure_development_standards.py /path/to/system --language python --show-defaults

    # Validate existing configuration
    python3 configure_development_standards.py /path/to/system --validate

Created: 2025-11-23
Version: 1.0.0
Reflow Version: 3.20.0
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# Default standards by language - extracted from template for quick access
PYTHON_DEFAULTS = {
    "interface_strategy": {
        "value": "protocol_di",
        "options": ["protocol_di", "abc", "manual"],
        "default": "protocol_di",
        "rationale": "Protocol + DI provides structural typing, no metaclass conflicts, and easy testing via dependency injection"
    },
    "dependency_manager": {
        "value": "hatchling",
        "options": ["hatchling", "poetry", "uv", "setuptools", "pip_requirements"],
        "default": "hatchling",
        "rationale": "Hatchling is PEP 517/518/621 compliant, fast, and requires minimal configuration"
    },
    "lock_file_generation": {
        "value": True,
        "options": [True, False],
        "default": True,
        "lock_tool_by_manager": {
            "hatchling": "pip-tools (pip-compile)",
            "poetry": "poetry.lock (built-in)",
            "uv": "uv.lock (built-in)",
            "setuptools": "pip-tools (pip-compile)",
            "pip_requirements": "pip-tools (pip-compile)"
        },
        "rationale": "Lock files ensure reproducible builds across environments"
    },
    "project_config": {
        "value": "pyproject_toml",
        "options": ["pyproject_toml", "setup_py", "setup_cfg"],
        "default": "pyproject_toml",
        "rationale": "pyproject.toml is the modern Python standard (PEP 518/621)"
    },
    "testing_framework": {
        "value": "pytest",
        "options": ["pytest", "unittest", "nose2"],
        "default": "pytest",
        "rationale": "pytest is the de facto standard with excellent ecosystem support"
    },
    "linting": {
        "value": "ruff",
        "options": ["ruff", "flake8_black", "pylint", "none"],
        "default": "ruff",
        "rationale": "ruff replaces flake8, black, isort with a single fast tool"
    },
    "type_checking": {
        "value": "mypy",
        "options": ["mypy", "pyright", "none"],
        "default": "mypy",
        "rationale": "mypy is the standard, pyright is faster but less ecosystem support"
    },
    "web_framework": {
        "value": "fastapi",
        "options": ["fastapi", "flask", "django", "litestar", "none"],
        "default": "fastapi",
        "rationale": "FastAPI is async-native with automatic OpenAPI docs and excellent typing support"
    },
    "orm": {
        "value": "sqlalchemy",
        "options": ["sqlalchemy", "sqlmodel", "tortoise", "raw_sql", "none"],
        "default": "sqlalchemy",
        "rationale": "SQLAlchemy 2.0 is the industry standard with excellent typing support"
    },
    "configuration": {
        "value": "pydantic_settings",
        "options": ["pydantic_settings", "python_dotenv", "dynaconf", "none"],
        "default": "pydantic_settings",
        "rationale": "Pydantic Settings provides type-safe configuration with validation"
    },
    "logging": {
        "value": "structlog",
        "options": ["structlog", "stdlib_logging", "loguru"],
        "default": "structlog",
        "rationale": "structlog provides structured JSON logs ideal for observability"
    },
    "http_client": {
        "value": "httpx",
        "options": ["httpx", "requests", "aiohttp"],
        "default": "httpx",
        "rationale": "httpx is async-native with an API similar to requests"
    }
}

TYPESCRIPT_DEFAULTS = {
    "interface_strategy": {
        "value": "typescript_interfaces",
        "options": ["typescript_interfaces", "manual"],
        "default": "typescript_interfaces",
        "rationale": "TypeScript interfaces are the native structural typing mechanism"
    },
    "package_manager": {
        "value": "pnpm",
        "options": ["pnpm", "npm", "yarn", "bun"],
        "default": "pnpm",
        "rationale": "pnpm is fast, disk-efficient, and strict about dependencies"
    },
    "lock_file_generation": {
        "value": True,
        "options": [True, False],
        "default": True,
        "rationale": "Lock files ensure reproducible builds"
    },
    "testing_framework": {
        "value": "vitest",
        "options": ["vitest", "jest", "mocha"],
        "default": "vitest",
        "rationale": "vitest is fast, ESM-native, and compatible with Vite projects"
    },
    "linting": {
        "value": "eslint_prettier",
        "options": ["eslint_prettier", "biome", "none"],
        "default": "eslint_prettier",
        "rationale": "ESLint + Prettier is the established standard for TypeScript"
    },
    "web_framework": {
        "value": "none",
        "options": ["nextjs", "express", "fastify", "hono", "none"],
        "default": "none",
        "rationale": "Depends on use case - frontend vs backend vs full-stack"
    }
}

RUST_DEFAULTS = {
    "interface_strategy": {
        "value": "traits",
        "options": ["traits"],
        "default": "traits",
        "rationale": "Rust traits are the only interface mechanism"
    },
    "build_system": {
        "value": "cargo",
        "options": ["cargo"],
        "default": "cargo",
        "rationale": "Cargo is the standard build system for Rust"
    },
    "lock_file_generation": {
        "value": True,
        "options": [True, False],
        "default": True,
        "rationale": "Cargo.lock ensures reproducible builds"
    },
    "testing_framework": {
        "value": "builtin",
        "options": ["builtin"],
        "default": "builtin",
        "rationale": "Rust has built-in testing support"
    },
    "web_framework": {
        "value": "none",
        "options": ["axum", "actix_web", "rocket", "none"],
        "default": "none",
        "rationale": "Depends on use case"
    }
}

GO_DEFAULTS = {
    "interface_strategy": {
        "value": "interfaces",
        "options": ["interfaces"],
        "default": "interfaces",
        "rationale": "Go interfaces are implicit and the only interface mechanism"
    },
    "module_system": {
        "value": "go_mod",
        "options": ["go_mod"],
        "default": "go_mod",
        "rationale": "Go modules are the standard dependency system"
    },
    "lock_file_generation": {
        "value": True,
        "options": [True, False],
        "default": True,
        "rationale": "go.sum ensures reproducible builds"
    },
    "testing_framework": {
        "value": "builtin",
        "options": ["builtin", "testify"],
        "default": "builtin",
        "rationale": "Go has built-in testing support"
    },
    "web_framework": {
        "value": "none",
        "options": ["gin", "echo", "fiber", "chi", "none"],
        "default": "none",
        "rationale": "Depends on use case"
    }
}

JAVA_DEFAULTS = {
    "interface_strategy": {
        "value": "interfaces",
        "options": ["interfaces", "abstract_classes"],
        "default": "interfaces",
        "rationale": "Java interfaces provide clean contracts without implementation coupling"
    },
    "build_system": {
        "value": "gradle",
        "options": ["gradle", "maven"],
        "default": "gradle",
        "rationale": "Gradle is more flexible and faster than Maven"
    },
    "lock_file_generation": {
        "value": True,
        "options": [True, False],
        "default": True,
        "rationale": "Lock files ensure reproducible builds"
    },
    "testing_framework": {
        "value": "junit5",
        "options": ["junit5", "junit4", "testng"],
        "default": "junit5",
        "rationale": "JUnit 5 is the modern standard with better extension model"
    },
    "web_framework": {
        "value": "none",
        "options": ["spring_boot", "quarkus", "micronaut", "none"],
        "default": "none",
        "rationale": "Depends on use case"
    }
}

LANGUAGE_DEFAULTS = {
    "python": PYTHON_DEFAULTS,
    "typescript": TYPESCRIPT_DEFAULTS,
    "rust": RUST_DEFAULTS,
    "go": GO_DEFAULTS,
    "java": JAVA_DEFAULTS
}

CROSS_CUTTING_DEFAULTS = {
    "containerization": {
        "value": "docker",
        "options": ["docker", "podman", "none"],
        "default": "docker",
        "rationale": "Docker is the industry standard for containerization"
    },
    "ci_cd": {
        "value": "github_actions",
        "options": ["github_actions", "gitlab_ci", "jenkins", "none"],
        "default": "github_actions",
        "rationale": "GitHub Actions integrates well with GitHub-hosted repositories"
    },
    "api_documentation": {
        "value": "openapi",
        "options": ["openapi", "graphql_schema", "none"],
        "default": "openapi",
        "rationale": "OpenAPI is the standard for REST API documentation"
    }
}


def get_language_defaults(language: str) -> dict[str, Any]:
    """Get default settings for a language."""
    if language not in LANGUAGE_DEFAULTS:
        raise ValueError(f"Unknown language: {language}. Supported: {list(LANGUAGE_DEFAULTS.keys())}")
    return LANGUAGE_DEFAULTS[language]


def show_defaults(language: str) -> None:
    """Display defaults for a language."""
    defaults = get_language_defaults(language)

    print(f"\n{'='*60}")
    print(f"Development Standards Defaults for {language.upper()}")
    print(f"{'='*60}\n")

    for setting, config in defaults.items():
        print(f"{setting}:")
        print(f"  Default: {config['default']}")
        print(f"  Options: {config['options']}")
        print(f"  Rationale: {config['rationale']}")
        print()

    print(f"\n{'='*60}")
    print("Cross-Cutting Defaults")
    print(f"{'='*60}\n")

    for setting, config in CROSS_CUTTING_DEFAULTS.items():
        print(f"{setting}:")
        print(f"  Default: {config['default']}")
        print(f"  Options: {config['options']}")
        print(f"  Rationale: {config['rationale']}")
        print()


def create_development_standards(
    system_root: str,
    primary_language: str,
    language_version: str = "3.11+",
    selection_rationale: str = "Primary development language",
    secondary_languages: Optional[list[str]] = None,
    customizations: Optional[dict[str, Any]] = None,
    user_notes: str = ""
) -> dict[str, Any]:
    """
    Create a development_standards.json structure.

    Args:
        system_root: Path to system root
        primary_language: Primary programming language
        language_version: Version constraint for primary language
        selection_rationale: Why this language was chosen
        secondary_languages: Additional languages used
        customizations: Dict of setting overrides
        user_notes: User notes about the configuration

    Returns:
        Complete development_standards.json structure
    """
    now = datetime.now().isoformat()
    customizations = customizations or {}
    secondary_languages = secondary_languages or []

    # Build language standards section
    language_standards = {}

    # Add primary language
    primary_defaults = get_language_defaults(primary_language)
    language_standards[primary_language] = {}

    for setting, config in primary_defaults.items():
        setting_config = config.copy()

        # Apply customization if provided
        custom_key = f"{primary_language}.{setting}"
        if custom_key in customizations:
            setting_config["value"] = customizations[custom_key]
            setting_config["user_customized"] = True
        else:
            setting_config["user_customized"] = False

        language_standards[primary_language][setting] = setting_config

    # Add secondary languages
    for lang in secondary_languages:
        if lang in LANGUAGE_DEFAULTS:
            lang_defaults = get_language_defaults(lang)
            language_standards[lang] = {}

            for setting, config in lang_defaults.items():
                setting_config = config.copy()
                custom_key = f"{lang}.{setting}"
                if custom_key in customizations:
                    setting_config["value"] = customizations[custom_key]
                    setting_config["user_customized"] = True
                else:
                    setting_config["user_customized"] = False

                language_standards[lang][setting] = setting_config

    # Build cross-cutting section
    cross_cutting = {}
    for setting, config in CROSS_CUTTING_DEFAULTS.items():
        setting_config = config.copy()
        custom_key = f"cross_cutting.{setting}"
        if custom_key in customizations:
            setting_config["value"] = customizations[custom_key]
            setting_config["user_customized"] = True
        else:
            setting_config["user_customized"] = False
        cross_cutting[setting] = setting_config

    # Build service organization section (initially null, set during FA-07/SE-01)
    service_organization = {
        "strategy": {
            "value": None,
            "options": ["workflow_based", "domain_based", "hybrid"],
            "default": None,
            "user_customized": False,
            "rationale": None,
            "note": "Set during functional allocation (FA-07 or SE-01) based on LLM analysis"
        },
        "analysis_results": {
            "coordination_complexity": None,
            "workflow_span": None,
            "operation_types": None,
            "recommendation": None,
            "recommendation_rationale": None
        },
        "allocation_details": {
            "workflow_services": [],
            "domain_services": [],
            "shared_services": []
        }
    }

    # Build complete structure
    standards = {
        "schema_version": "1.0.0",
        "created": now,
        "last_modified": now,
        "llm_prompted": True,

        "primary_language": {
            "language": primary_language,
            "version": language_version,
            "selection_rationale": selection_rationale
        },

        "secondary_languages": secondary_languages,

        "language_standards": language_standards,
        "cross_cutting": cross_cutting,
        "service_organization": service_organization,
        "user_notes": user_notes
    }

    return standards


def save_development_standards(system_root: str, standards: dict[str, Any]) -> str:
    """
    Save development standards to the system's specs directory.

    Args:
        system_root: Path to system root
        standards: Development standards dictionary

    Returns:
        Path to saved file
    """
    # Create directory if needed
    dev_dir = Path(system_root) / "specs" / "development"
    dev_dir.mkdir(parents=True, exist_ok=True)

    output_path = dev_dir / "development_standards.json"

    with open(output_path, "w") as f:
        json.dump(standards, f, indent=2)

    return str(output_path)


def load_development_standards(system_root: str) -> Optional[dict[str, Any]]:
    """
    Load existing development standards if they exist.

    Args:
        system_root: Path to system root

    Returns:
        Standards dictionary or None if not found
    """
    standards_path = Path(system_root) / "specs" / "development" / "development_standards.json"

    if not standards_path.exists():
        return None

    with open(standards_path) as f:
        return json.load(f)


def validate_development_standards(system_root: str) -> tuple[bool, list[str]]:
    """
    Validate existing development standards file.

    Args:
        system_root: Path to system root

    Returns:
        Tuple of (is_valid, list of issues)
    """
    issues = []

    standards = load_development_standards(system_root)
    if standards is None:
        return False, ["development_standards.json not found"]

    # Check required fields
    required_fields = ["schema_version", "primary_language", "language_standards"]
    for field in required_fields:
        if field not in standards:
            issues.append(f"Missing required field: {field}")

    # Check primary language
    if "primary_language" in standards:
        lang = standards["primary_language"].get("language")
        if lang and lang not in LANGUAGE_DEFAULTS:
            issues.append(f"Unknown primary language: {lang}")

    # Check language standards have valid values
    if "language_standards" in standards:
        for lang, settings in standards["language_standards"].items():
            if lang not in LANGUAGE_DEFAULTS:
                issues.append(f"Unknown language in standards: {lang}")
                continue

            defaults = LANGUAGE_DEFAULTS[lang]
            for setting, config in settings.items():
                if setting not in defaults:
                    issues.append(f"Unknown setting for {lang}: {setting}")
                elif "value" in config and config["value"] not in config.get("options", []):
                    # Skip validation for boolean options
                    if not isinstance(config["value"], bool):
                        issues.append(f"Invalid value for {lang}.{setting}: {config['value']}")

    return len(issues) == 0, issues


def format_for_llm_prompt(language: str) -> str:
    """
    Format defaults as a prompt for LLM to present to user.

    Args:
        language: Programming language

    Returns:
        Formatted string for LLM to use in conversation
    """
    defaults = get_language_defaults(language)

    lines = [
        f"For **{language.upper()}**, the recommended development standards are:",
        ""
    ]

    for setting, config in defaults.items():
        setting_name = setting.replace("_", " ").title()
        lines.append(f"- **{setting_name}**: `{config['default']}`")
        lines.append(f"  - {config['rationale']}")
        lines.append(f"  - Alternatives: {', '.join(str(o) for o in config['options'] if o != config['default'])}")
        lines.append("")

    lines.extend([
        "Would you like to:",
        "1. **Accept these defaults** (recommended)",
        "2. **Customize one or more settings**",
        "3. **Skip** (will use defaults when needed)"
    ])

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Configure development standards for a system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument("system_root", help="Path to system root directory")
    parser.add_argument("--language", "-l", help="Primary language",
                       choices=list(LANGUAGE_DEFAULTS.keys()))
    parser.add_argument("--version", "-v", help="Language version constraint", default="3.11+")
    parser.add_argument("--use-defaults", action="store_true",
                       help="Accept all defaults without prompting")
    parser.add_argument("--show-defaults", action="store_true",
                       help="Show defaults for language and exit")
    parser.add_argument("--validate", action="store_true",
                       help="Validate existing development_standards.json")
    parser.add_argument("--format-prompt", action="store_true",
                       help="Output formatted prompt for LLM use")
    parser.add_argument("--reflow-root", help="Path to Reflow root (for template)")
    parser.add_argument("--secondary-languages", "-s", nargs="+",
                       help="Secondary languages used in project")
    parser.add_argument("--notes", help="User notes about configuration")

    args = parser.parse_args()

    # Validate mode
    if args.validate:
        is_valid, issues = validate_development_standards(args.system_root)
        if is_valid:
            print("VALID: development_standards.json is valid")
            return 0
        else:
            print("INVALID: development_standards.json has issues:")
            for issue in issues:
                print(f"  - {issue}")
            return 1

    # Show defaults mode
    if args.show_defaults:
        if not args.language:
            print("ERROR: --language required with --show-defaults")
            return 1
        show_defaults(args.language)
        return 0

    # Format prompt mode
    if args.format_prompt:
        if not args.language:
            print("ERROR: --language required with --format-prompt")
            return 1
        print(format_for_llm_prompt(args.language))
        return 0

    # Create mode
    if not args.language:
        print("ERROR: --language required to create development standards")
        return 1

    # Check if standards already exist
    existing = load_development_standards(args.system_root)
    if existing:
        print(f"WARNING: development_standards.json already exists at {args.system_root}")
        print("Use --validate to check, or delete to recreate")
        return 1

    # Create standards
    standards = create_development_standards(
        system_root=args.system_root,
        primary_language=args.language,
        language_version=args.version,
        selection_rationale="Primary development language",
        secondary_languages=args.secondary_languages,
        user_notes=args.notes or ""
    )

    # Save
    output_path = save_development_standards(args.system_root, standards)

    print(f"SUCCESS: Created development standards at {output_path}")
    print(f"\nPrimary Language: {args.language}")
    print(f"Interface Strategy: {standards['language_standards'][args.language]['interface_strategy']['value']}")
    print(f"Dependency Manager: {standards['language_standards'][args.language].get('dependency_manager', {}).get('value', 'N/A')}")
    print(f"Lock Files: {standards['language_standards'][args.language].get('lock_file_generation', {}).get('value', 'N/A')}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
