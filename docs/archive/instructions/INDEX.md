# Reflow Modular Instructions System

## Overview

This directory contains focused instruction modules that replace the large, monolithic workflow files. Each module is <300 lines and addresses specific aspects of reflow workflows.

## Problem Addressed

The original approach had three critical issues:
1. **Context Overload** - 1600+ line files overwhelmed LLM agents
2. **Repository Clutter** - No enforcement of clean directory structure 
3. **Instruction Non-Adherence** - Critical rules got buried and forgotten

## Solution: Modular Instructions

Instead of reading massive files, agents load small, focused modules as needed.

## Module Reference

### 🚨 Critical Modules (Load Before Every Operation)

#### `1-behavioral-rules.json` (167 lines)
**When to Load**: Before EVERY workflow operation
**Purpose**: Non-negotiable behavioral rules that prevent common violations
**Key Rules**:
- NEVER generate reports/summaries
- Strict workflow adherence without deviation  
- Directory structure enforcement (4-folder structure only)
- System isolation (prevent cross-contamination)
- Pre/post operation validation requirements

**Load Command**: "Load instructions/1-behavioral-rules.json"

#### `2-file-locations.json` (177 lines)  
**When to Load**: When agent shows confusion about file locations
**Purpose**: Definitive reference for where ALL files belong
**Key Information**:
- Tracking files ALWAYS in `<system>/context/`
- Working directory requirements (must cd to system root)
- Embedded vs standard reflow file locations
- Quick diagnosis for "file not found" errors

**Load Command**: "Load instructions/2-file-locations.json"

### 🛠️ Operational Modules (Load As Needed)

#### `3-system-isolation.json` (Future)
**When to Load**: Multi-system environments, cross-contamination risks
**Purpose**: Prevent mixing files between different systems

#### `4-context-refresh.json` (Future)  
**When to Load**: After 4+ operations, degradation signals detected
**Purpose**: When/how to refresh context without losing workflow state

#### `5-tool-reference.json` (Future)
**When to Load**: Before using reflow tools
**Purpose**: Complete tool documentation and usage patterns

#### `6-workflow-decisions.json` (Future)
**When to Load**: At decision points (D0-D4 in workflows)  
**Purpose**: Decision trees for routing between workflow phases

#### `7-quality-gates.json` (Future)
**When to Load**: Before handoffs between workflow phases
**Purpose**: Validation checkpoints and requirements

## Usage Patterns

### For ANY Workflow Operation
```
ALWAYS LOAD:
1. instructions/1-behavioral-rules.json (mandatory rules)
2. instructions/2-file-locations.json (if file location confusion)
```

### For Architecture Workflow  
```
LOAD: 1-behavioral-rules.json
LOAD: 2-file-locations.json  
IF needed: 5-tool-reference.json (for architecture tools)
IF needed: 7-quality-gates.json (for validation checkpoints)
```

### For Development Workflow
```
LOAD: 1-behavioral-rules.json
LOAD: 2-file-locations.json
IF needed: 6-workflow-decisions.json (for D3 decision logic)
IF needed: 5-tool-reference.json (for development tools)
```

### For Injection Workflow (inject_flow.json)
```  
LOAD: 1-behavioral-rules.json (includes injection-specific rules)
LOAD: 2-file-locations.json (includes injection file locations)
```

## Loading Instructions for LLM Agents

### Quick Load (Emergency)
If agent is violating rules or lost context:
```
"Load instructions/1-behavioral-rules.json immediately"
```

### Standard Load (Beginning of workflow)
```
"Load instructions/1-behavioral-rules.json and 2-file-locations.json before starting workflow"
```

### Comprehensive Load (Complex operation)
```
"Load instruction modules: 1-behavioral-rules, 2-file-locations, and 5-tool-reference"
```

## Benefits

✅ **Context Management**: Each module fits easily in LLM context window
✅ **Focused Rules**: Agent can reference specific rule types by name  
✅ **Reduced Forgetting**: Critical rules in dedicated, easily referenced files
✅ **Stackable Context**: Multiple modules can be loaded together
✅ **Maintainable**: Update individual modules without affecting others

## Enforcement Tools

### Directory Structure Validation
```bash
python3 tools/validate_directory_structure.py <system_path>
python3 tools/validate_directory_structure.py <system_path> --auto-clean
```

### Behavioral Rules Enforcement (Future)
```bash  
python3 tools/validate_behavioral_compliance.py <system_path>
```

## Integration with Existing Workflows

### decision_flow.json Integration
The main `decision_flow.json` file now references these modules instead of containing all rules inline:

```json
{
  "pre_operation_validation": {
    "required_modules": [
      "instructions/1-behavioral-rules.json",
      "instructions/2-file-locations.json"  
    ]
  }
}
```

### inject_flow.json Integration  
The `inject_flow.json` workflow similarly references these modules for behavioral consistency:

```json
{
  "injection_behavioral_rules": {
    "load_modules": [
      "instructions/1-behavioral-rules.json",
      "instructions/2-file-locations.json"
    ]
  }
}
```

## Migration Strategy

### Phase 1: ✅ Completed
- Created modular instruction files
- Built directory validation tool  
- This INDEX.md documentation

### Phase 2: In Progress
- Integrate module loading into main workflows
- Update existing decision_flow.json to reference modules
- Update inject_flow.json to reference modules

### Phase 3: Future
- Create remaining modules (3-7)  
- Build behavioral compliance validator
- Full workflow testing and refinement

## Success Metrics

- ✅ Reduced agent rule violations (no more "NEVER generate reports" violations)
- ✅ Clean system directories (4-folder structure maintained)
- ✅ Faster workflow execution (less context reloading needed)
- ✅ Better rule adherence (focused, accessible rule modules)

## Emergency Procedures

### If Agent Violates Rules
```
"STOP. Load instructions/1-behavioral-rules.json immediately and review NEVER_GENERATE_REPORTS section"
```

### If Agent Can't Find Files
```
"Load instructions/2-file-locations.json and follow QUICK_DIAGNOSIS procedure"
```

### If Directory Gets Cluttered  
```bash
python3 tools/validate_directory_structure.py <system_path> --auto-clean
```

---

## Quick Reference Card

**Before ANY Operation**: Load `1-behavioral-rules.json`
**If File Confusion**: Load `2-file-locations.json`  
**Directory Cleanup**: Run `validate_directory_structure.py --auto-clean`
**Emergency Stop**: "Load 1-behavioral-rules.json immediately"

This modular system transforms workflow instruction delivery from overwhelming monoliths to focused, actionable guidance.