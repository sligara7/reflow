# Change Proposal: Pixi Integration for Reflow

**Date**: 2025-11-05
**Proposal ID**: CP-2025-11-05-001
**Feature**: Pixi Package Manager Integration (Phase 1: Reflow Itself)
**Priority**: Medium
**Workflow Version**: 3.10.0 → 3.11.0

## Executive Summary

Add **Pixi** (https://pixi.sh) as the recommended dependency manager for Reflow's own tools, providing fast, reproducible Python environments with lockfile support. This addresses the current gap where Reflow has no formal dependency management (`requirements.txt` or `pyproject.toml`).

**Phase 1 Scope:** Pixi for Reflow itself only (not user systems yet)

## Business Justification

### Current Gap

Per `specs/machine/development_language_configuration.json`:
```json
"gaps_identified": {
  "critical": [
    "No testing framework or tests (0% coverage)",
    "No requirements.txt or pyproject.toml for dependency management",  ← THIS
    "No CI/CD pipeline"
  ]
}
```

**Problem:**
- Reflow tools require Python 3.8+ and NetworkX
- No formal dependency specification
- Users must manually `pip install networkx`
- Version mismatches can cause bugs
- No reproducible environment guarantee

### Why Pixi?

**Alternatives Considered:**
1. **requirements.txt** - Simple but no lockfile, slow installs
2. **Poetry** - Popular but heavy, slower than Pixi
3. **PDM** - Good but less mature than Poetry
4. **Pixi** ✅ - Fast (Rust-based), lockfile, cross-platform, conda-forge packages

**Pixi Advantages:**
- ⚡ **Fast**: Rust-based, parallel installs, ~2-5x faster than pip/poetry
- 🔒 **Reproducible**: `pixi.lock` guarantees exact versions
- 🌍 **Cross-platform**: Linux, macOS, Windows
- 📦 **Conda-forge**: Access to 20,000+ packages (including non-Python tools)
- 🎯 **Simple**: Single `pixi.toml`, no virtual env confusion
- 🚀 **Modern**: Released 2023, actively developed by prefix.dev

### Impact

**Time Savings**: 5-10 minutes per user setup
- Before: "Install Python, install NetworkX, hope versions work"
- After: "Install Pixi, run `pixi install`, guaranteed to work"

**Quality Improvement**:
- ✅ Reproducible Reflow environment (lockfile)
- ✅ Faster CI/CD (when added later)
- ✅ Easier onboarding for contributors
- ✅ Foundation for future dev dependencies (pytest, ruff, mypy)

## Feature Description

### New Files

#### 1. `pixi.toml` (Reflow Root)

```toml
[project]
name = "reflow"
version = "3.11.0"
description = "Systems engineering and development workflow framework"
channels = ["conda-forge"]
platforms = ["linux-64", "osx-64", "osx-arm64", "win-64"]

[dependencies]
python = ">=3.8"
networkx = ">=3.0"

[feature.dev.dependencies]
# Future: Add when implementing testing/linting
# pytest = "*"
# pytest-cov = "*"
# ruff = "*"
# mypy = "*"

[tasks]
# Common Reflow commands
validate-arch = "python tools/validate_architecture.py"
generate-graph = "python tools/system_of_systems_graph_v2.py"
generate-icds = "python tools/generate_interface_contracts.py"
generate-abc = "python tools/generate_interface_abc.py"

[tasks.help]
cmd = """
echo 'Reflow v3.11.0 - Available commands:'
echo ''
echo '  pixi run validate-arch <system_path>   - Validate architecture'
echo '  pixi run generate-graph <system_path>  - Generate system graph'
echo '  pixi run generate-icds <system_path>   - Generate ICDs'
echo '  pixi run generate-abc <system_path>    - Generate ABC interfaces'
echo ''
echo 'Or run tools directly: pixi run python tools/<tool_name>.py'
"""
```

**Benefits:**
- Declares all Reflow dependencies
- Creates reproducible environment
- Provides convenient task shortcuts
- Cross-platform (Linux, macOS, Windows)

#### 2. `.gitignore` Update

Add to `.gitignore`:
```
# Pixi
.pixi/
pixi.lock
```

**Note:** Some projects commit `pixi.lock` for reproducibility. Recommendation: **Don't commit** for Reflow (a library), but **do commit** for user systems (applications).

### Workflow Integration

#### New Action: S-03-A07 in `00-setup.json`

```json
{
  "action_id": "S-03-A07",
  "description": "Install Pixi package manager (OPTIONAL but RECOMMENDED)",
  "purpose": "Set up fast, reproducible Python environment for Reflow tools",
  "optional": true,
  "recommended": "Strongly recommended for reproducible environment and faster setup",
  "user_prompt": {
    "ask": "Would you like to install Pixi for dependency management?",
    "options": [
      "Yes - Install Pixi (recommended for reproducible environment)",
      "No - I'll use pip manually"
    ],
    "default": "Yes",
    "benefits": [
      "Fast, reproducible Python environment",
      "Guaranteed compatibility with Reflow tools",
      "Easy updates via 'pixi update'",
      "Cross-platform (Linux, macOS, Windows)",
      "Foundation for future dev tools (pytest, ruff)"
    ]
  },
  "if_yes": {
    "setup_steps": [
      {
        "step": 1,
        "action": "Check if Pixi already installed",
        "command": "pixi --version",
        "on_success": "Skip to step 3",
        "on_failure": "Continue to step 2"
      },
      {
        "step": 2,
        "action": "Install Pixi",
        "linux_macos": "curl -fsSL https://pixi.sh/install.sh | bash",
        "windows": "iwr -useb https://pixi.sh/install.ps1 | iex",
        "note": "May require shell restart to update PATH"
      },
      {
        "step": 3,
        "action": "Install Reflow dependencies",
        "command": "cd {reflow_root} && pixi install",
        "creates": ".pixi/ directory with isolated environment",
        "duration": "30-60 seconds"
      },
      {
        "step": 4,
        "action": "Verify installation",
        "command": "pixi run python -c 'import networkx; print(f\"NetworkX {networkx.__version__} installed\")'",
        "success_criteria": "NetworkX version printed"
      }
    ],
    "usage": [
      "Run Reflow tools: pixi run python tools/<tool>.py",
      "Or use shortcuts: pixi run validate-arch <system_path>",
      "Update dependencies: pixi update",
      "See all tasks: pixi task list"
    ]
  },
  "if_no": {
    "action": "Skip Pixi installation, use system Python and pip",
    "fallback": "Ensure NetworkX is installed: pip install networkx>=3.0"
  },
  "reference": "See https://pixi.sh for complete Pixi documentation"
}
```

## Impact Analysis

### Affected Components

1. **Workflows** (1 file modified):
   - `workflows/00-setup.json` - Add S-03-A07 action

2. **New Files** (1 new file):
   - `pixi.toml` - Reflow dependency specification

3. **Configuration** (2 files modified):
   - `.gitignore` - Add `.pixi/` and `pixi.lock`
   - `specs/machine/development_language_configuration.json` - Update to reflect Pixi adoption

4. **Documentation** (3 files modified):
   - `docs/CLAUDE.md` - Add Pixi setup instructions
   - `README.md` - Update installation instructions
   - `docs/RELEASE_NOTES_v3.11.0.md` (NEW)

### Breaking Changes

**NONE** - This is completely optional and backward compatible.

**Fallback:** If user declines Pixi or it fails to install, workflow falls back to `pip install networkx`.

### Dependencies

- **Pixi**: Optional dependency, installed at user's discretion
- **Python**: Already required (no change)
- **NetworkX**: Already required, now formally declared in `pixi.toml`

### Interface Changes

**NONE** - All tools continue to work identically whether run via Pixi or system Python.

## Migration Guide

### For Existing Reflow Users

**No migration required!** This is purely additive.

**To adopt Pixi:**
1. Pull latest Reflow (v3.11.0)
2. Install Pixi: `curl -fsSL https://pixi.sh/install.sh | bash`
3. Run: `pixi install` in Reflow root
4. (Optional) Use `pixi run` commands for convenience

**To continue without Pixi:**
- Keep using system Python and pip as before
- No changes needed

### For New Reflow Users

**Recommended setup:**
1. Clone Reflow: `git clone https://github.com/sligara7/reflow.git`
2. Install Pixi: `curl -fsSL https://pixi.sh/install.sh | bash`
3. Setup: `cd reflow && pixi install`
4. Done! Run tools with `pixi run python tools/<tool>.py`

**Alternative (without Pixi):**
1. Clone Reflow
2. Install dependencies: `pip install networkx>=3.0`
3. Run tools with `python3 tools/<tool>.py`

## Testing Strategy

### Installation Testing

1. **Linux**: Test Pixi installation on Ubuntu 22.04, Debian, Fedora
2. **macOS**: Test on Intel and ARM (M1/M2) Macs
3. **Windows**: Test on Windows 10/11 with PowerShell

### Functionality Testing

1. Run each Reflow tool via `pixi run python tools/<tool>.py`
2. Verify tools work identically with Pixi vs system Python
3. Test `pixi.lock` reproducibility (install on two systems, verify identical)

### Fallback Testing

1. Decline Pixi installation in S-03-A07
2. Verify workflow falls back to pip
3. Verify tools still work with system Python

## Implementation Plan

### Phase 1: Core Implementation (v3.11.0) ← THIS PROPOSAL

1. Create `pixi.toml` in Reflow root
2. Update `.gitignore` to exclude `.pixi/`
3. Add S-03-A07 to `workflows/00-setup.json`
4. Update `development_language_configuration.json`
5. Update documentation (CLAUDE.md, README.md)
6. Test on Linux, macOS, Windows
7. Release v3.11.0

**Timeline**: 4-6 hours

### Phase 2: User Systems (v3.12.0) - DEFERRED

Future enhancement: Offer Pixi as option for user systems during D-01.
- Update D-01-A00 research to include Pixi
- Create `generate_dependency_manifest.py` tool
- Support pixi/poetry/pip choice

**Timeline**: TBD (not in this proposal)

## Success Criteria

1. ✅ `pixi.toml` exists in Reflow root with correct dependencies
2. ✅ `pixi install` successfully creates `.pixi/` environment
3. ✅ All Reflow tools work via `pixi run python tools/<tool>.py`
4. ✅ S-03-A07 workflow step allows user to opt-in or decline
5. ✅ Fallback to pip works if Pixi declined
6. ✅ Documentation updated with Pixi instructions
7. ✅ Tested on Linux, macOS, Windows

## Risks & Mitigation

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Pixi installation fails | Low | Medium | Fallback to pip (already in workflow) |
| User unfamiliar with Pixi | Medium | Low | Make optional, provide clear docs |
| Platform compatibility issues | Low | Medium | Test on 3 platforms before release |
| Pixi not maintained long-term | Low | High | Easy to migrate back to pip/poetry if needed |
| Confusion about when to use Pixi | Medium | Low | Clear documentation: "Reflow uses Pixi, user systems choose their own" |

## Questions for User

Before implementing:

1. **Lockfile policy:** Should we commit `pixi.lock` to git?
   - ✅ Recommended: **No** (Reflow is a library, not an application)
   - Users get latest compatible versions
   - Simpler git history

2. **Default behavior:** Should S-03-A07 be opt-in or opt-out?
   - ✅ Recommended: **Opt-in** (ask user, default to "Yes")
   - Less intrusive for users who prefer pip

3. **Pixi tasks:** Are the proposed tasks sufficient?
   - `validate-arch`, `generate-graph`, `generate-icds`, `generate-abc`, `help`
   - Should we add more?

## Approval

**Change Type**: ⭐ **Feature Addition** (non-breaking, optional)
**Version Impact**: Minor version bump (3.10.0 → 3.11.0)
**Breaking Changes**: None
**User Impact**: Positive (faster, more reliable setup)

---

**Prepared by**: Claude (LLM Agent)
**Date**: 2025-11-05
**Status**: AWAITING APPROVAL
