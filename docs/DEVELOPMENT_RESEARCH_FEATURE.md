# Development Best Practices Research Feature

**Date Added**: 2025-10-24
**Workflow**: 03-development.json
**Step**: D-01-A00 (NEW - optional research step)

---

## Overview

Added an optional research step at the beginning of D-01 (Development Environment Setup) to help LLM agents discover and apply current industry best practices before setting up development tooling.

## Motivation

When building services, development practices evolve rapidly:
- **Dependency management**: poetry/hatchling have replaced requirements.txt as Python best practice
- **Testing**: New frameworks emerge with better features
- **Security**: New scanning tools and standards
- **CI/CD**: Platform capabilities change frequently

Without research, LLM agents default to older patterns from training data, missing modern improvements.

## How It Works

### Step D-01-A00: Optional Research

**When**: First action in D-01, before any development setup
**User Decision**: Optional - user is asked if they want research
**Time Budget**: 5-10 minutes total (quick search, top results)

### If User Chooses "Yes"

LLM agent performs quick research in 8 categories:

1. **Dependency Management**
   - Query: "{language} dependency management best practices 2025"
   - Finds: poetry vs hatchling vs pdm for Python, pnpm vs yarn for JS, etc.

2. **Container Best Practices**
   - Multi-stage builds, security scanning, layer optimization, base images

3. **CI/CD Tooling**
   - GitHub Actions vs GitLab CI, automated testing, deployment strategies

4. **Observability Frameworks**
   - Logging (structured logging), metrics (Prometheus), tracing (OpenTelemetry)

5. **Security Standards**
   - Dependency scanning, secrets management, code security, OWASP

6. **Testing Frameworks**
   - Unit testing, integration testing, mocking, coverage tools

7. **Linting and Formatting**
   - Modern linters (ruff for Python, ESLint for JS), formatters, type checkers

8. **Build Systems**
   - Build automation, artifact packaging, version management

### Research Output

Results saved to: `context/development_tooling_research_{date}.md`

Uses template: `templates/development_research_output_template.md`

Format includes:
- Summary of current best practices for each category
- Tool comparisons with pros/cons
- Recommendations for this specific project
- Sources with links (prioritizing 2024-2025 content)

### If User Chooses "No"

Research skipped, workflow proceeds directly to D-01-A01 (language selection).

Default tooling choices from workflow used (now includes modern best practices as defaults).

---

## Integration with Rest of D-01

### D-01-A04 Enhancement

The dependency management step (D-01-A04) was updated to:

1. **Check for research results**: `context/development_tooling_research_*.md`
2. **Use research recommendations** if available
3. **Fall back to modern defaults** if no research:
   - Python: Prefer poetry/hatchling over requirements.txt
   - JavaScript: Suggest pnpm or yarn over npm
   - Java: Gradle with version catalogs
   - Go: Standard go modules

**Example** - Python dependency management:
```
If research exists:
  → Read dependency_management_recommendation section
  → Use recommended tool (e.g., poetry)
  
If no research:
  → Use modern_best_practices defaults
  → Prefer poetry/hatchling (modern) over requirements.txt (traditional)
```

---

## Usage Example

### Scenario: Building Python Microservices

**Without research** (old behavior):
```
D-01-A04: Initialize dependency management
  → Creates requirements.txt
  → Uses pip for installation
  → No lock file, manual dependency resolution
```

**With research** (new behavior):
```
D-01-A00: User chooses "Yes - Research best practices"
  → LLM searches "Python dependency management best practices 2025"
  → Finds: poetry and hatchling are current standards
  → Documents in context/development_tooling_research_2025-10-24.md
  
D-01-A04: Initialize dependency management
  → Reads research results
  → Creates pyproject.toml with poetry
  → Sets up lock file (poetry.lock)
  → Better dependency resolution and reproducibility
```

**Modern tooling benefits**:
- ✅ Dependency lock file (poetry.lock)
- ✅ Automatic dependency resolution
- ✅ Standardized project structure
- ✅ Better development workflow (poetry add, poetry install)
- ✅ Integrated build system

---

## When to Use Research

### Recommended "Yes" Scenarios

1. **New tech stack**: Building services in unfamiliar language/framework
2. **Greenfield project**: Starting fresh without legacy constraints
3. **Learning mode**: Want to discover modern practices
4. **Long-lived project**: Worth 10 minutes to get tooling right

### Reasonable "No" Scenarios

1. **Known stack**: Already familiar with modern tooling for this language
2. **Time-constrained**: Need to move quickly, will research manually later
3. **Legacy migration**: Must match existing project tooling
4. **Experimental**: Quick prototype, tooling doesn't matter yet

---

## Research Quality Guidelines

### Search Strategy

- **Recency bias**: Prioritize 2024-2025 sources (practices change fast)
- **Authoritative sources**: Official docs, reputable tech blogs, Stack Overflow trends
- **Quick scan**: Top 3-5 results per category (not exhaustive research)
- **Actionable focus**: Look for "best practices", "recommended", "industry standard"

### Time Management

- **Per category**: 1-2 minutes max
- **Total budget**: 5-10 minutes
- **Quick synthesis**: Bullet points, not essays
- **Decision-ready**: Clear recommendation + rationale

---

## Files Modified

1. **`/home/ajs7/project/reflow/workflows/03-development.json`**
   - Added D-01-A00 (optional research step)
   - Updated D-01-A04 to use research results
   - Added modern tooling defaults

2. **`/home/ajs7/project/reflow/templates/development_research_output_template.md`**
   - NEW template for research output format
   - Structured sections for each research category
   - Example Python configuration

---

## Future Enhancements

Potential improvements to this feature:

1. **Cached research**: Store research results per language/framework to avoid re-searching
2. **Research updates**: Prompt to refresh research every 6-12 months
3. **Team preferences**: Save org-specific tooling choices
4. **Automated tooling setup**: Scripts to configure chosen tools (e.g., poetry init)
5. **Architecture-level research**: Move high-level architecture pattern research to SE-02

---

## Example Research Output

Here's what the research output looks like for a Python service:

```markdown
# Development Tooling Research

**Date**: 2025-10-24
**Language**: Python
**Research Duration**: 8 minutes

## Recommendations for This Project

| Category | Tool | Rationale |
|----------|------|-----------|
| Dependency Mgmt | poetry | Lock files, better dependency resolution, modern standard |
| Testing | pytest | Most popular, rich plugin ecosystem, async support |
| Linting | ruff | 10-100x faster than alternatives, replaces 5+ tools |
| Formatting | ruff | Same tool as linting, opinionated, fast |
| Type Checking | mypy | Standard, excellent IDE integration |
| Observability | OpenTelemetry | Vendor-neutral, unified logging/metrics/tracing |
| Security | safety + bandit | Dependency scanning + code security |
| CI/CD | GitHub Actions | Built-in, free for public repos, great ecosystem |

### Implementation Notes

- Use pyproject.toml instead of requirements.txt
- Configure ruff in pyproject.toml (replaces black, isort, flake8, pylint)
- Set up pre-commit hooks for ruff + mypy
- Target Python 3.12+ for performance improvements
```

---

## Summary

**Problem**: LLM agents use outdated tooling patterns from training data

**Solution**: Optional research step in D-01 to discover current best practices

**Result**: Services use modern, industry-standard tooling

**Impact**: Better developer experience, better tooling, more maintainable projects

**Time Cost**: 5-10 minutes (optional, user-controlled)

**Value**: Modern tooling choices without requiring human to research each tool category

---

**End of Documentation**
