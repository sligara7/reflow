# Workflow Fix: SE-02 Structure Enforcement (v3.14.2)

**Date**: 2025-11-13
**Issue**: LLMs creating service architectures with incorrect structure, causing tool failures at SE-06
**Fix**: Enhanced SE-02-A01 with explicit structure requirements, examples, and validation enforcement

## Problem Statement

User reported:
> "I'm still getting errors in using the tools properly... Need to fix the workflows so that at the beginning of a workflow, it knows how to build the appropriate objects so that the tool can be used properly. This shouldn't be found out when the tool is run."

### Root Cause

LLMs were creating service architecture files with **incorrect structure**:
- ❌ **Incorrect**: `service_id` and `service_name` nested inside `service_metadata` object
- ✅ **Correct**: `service_id` and `service_name` at TOP LEVEL of JSON

**Impact**:
- Files created in SE-02 appeared valid to LLMs
- Errors only discovered at SE-06 when `system_of_systems_graph_v2.py` ran
- Forced return to SE-02 to reformat → reformatting loops → workflow never completed

### Why This Happened

1. **Template was correct** (`service_id` at top level on line 16)
2. **Schema was correct** (required `service_id` at top level)
3. **Tool was correct** (expected `data.get('service_id')`)
4. **BUT workflow wasn't prescriptive enough** - LLMs weren't following template exactly

## Solution

Enhanced `workflow_steps/systems_engineering/SE-02-ServiceArchitecture.json` with:

### 1. New Section: `MANDATORY_STRUCTURE_REQUIREMENTS_READ_FIRST`

Added **before** all other content with:
- **TOP_LEVEL_FIELDS_REQUIREMENT**: Explicit rule about service_id placement
- **✅ CORRECT_STRUCTURE_EXAMPLE**: Full JSON showing exactly what to create
- **❌ INCORRECT_STRUCTURE_DO_NOT_USE**: Full JSON showing what NOT to create (the common mistake)
- **PRE_CREATION_CHECKLIST**: 5-point checklist LLMs must review before creating files

### 2. Enhanced `execution_steps_WITH_VALIDATION`

- Step 0: ⚠️ FIRST - read structure requirements
- Step 1: Reference exact line number in template (line 16)
- Steps b-d: ✅ VERIFY checks for service_id, interfaces, components
- Step e: 🚨 IMMEDIATELY validate (BLOCKING emphasis)
- Step h: Double-check with grep command
- Step i: DO NOT batch creation - validate each file immediately

### 3. Expanded `llm_agent_guidance`

New section: **`🚨_CRITICAL_STRUCTURE_REMINDERS_PREVENT_REFORMATTING_LOOPS`**
- Lists #1 mistake with ⚠️ emoji
- Shows correct vs incorrect with ✅ and ❌ emojis
- Provides verification commands
- References checklist

New subsection: **`prevention_workflow`**
- **before_creating_any_files**: 4-step pre-flight checklist
- **while_creating_files**: Per-file validation workflow
- **if_you_see_format_errors_at_SE-06**: Recovery instructions

### 4. Updated `common_mistakes`

- Moved "nesting service_id" to **#1 position** with 🚨 emoji
- Added reference to INCORRECT_STRUCTURE_DO_NOT_USE example
- Added "not validating immediately" to mistakes list

## Files Changed

- `workflow_steps/systems_engineering/SE-02-ServiceArchitecture.json`

## Validation

Tested on existing xrpl4 project:
```bash
python3 /home/ajs7/project/reflow/tools/system_of_systems_graph_v2.py \
  /home/ajs7/project/xrpl4/specs/machine/index.json
```

**Result**: ✓ Graph generation complete! (8 nodes, 0 edges)
- No structure errors
- Service architectures correctly formatted with `service_id` at top level

## Expected Impact

1. **LLMs will see structure requirements BEFORE creating files** (not after)
2. **Explicit examples prevent guessing** - LLMs know exactly what structure to create
3. **Immediate validation catches errors** - no more discovering issues 4 steps later
4. **Reformatting loops eliminated** - workflows complete SE-06 without going back to SE-02

## Lessons Learned

### What Worked in Original Design
- ✅ Template had correct structure
- ✅ Schema validated correct structure
- ✅ Tool expected correct structure
- ✅ Workflow referenced template

### What Was Missing
- ❌ No explicit CORRECT vs INCORRECT examples
- ❌ Structure requirements buried deep in workflow
- ❌ No pre-flight checklist
- ❌ Validation not prominent enough (optional-seeming)
- ❌ No grep verification command

### Design Principle Derived

**"Show, Don't Tell" for LLM Workflows**:
- Don't just say "follow the template" → Show exact JSON structure
- Don't just say "interfaces is array" → Show correct `[ {...} ]` vs incorrect `{ provided: ... }`
- Don't just say "validate after creation" → Make validation BLOCKING with 🚨 emoji
- Don't just warn about mistakes → Show exact mistake structure with ❌ symbol

## Future Applications

This pattern should be applied to other workflow steps that create structured files:
- FA-02: Functional architecture creation
- SE-03: System architecture validation
- D-01: Development environment setup

## Version

- **Reflow Version**: v3.14.2 (unreleased)
- **Compatible With**: v3.0+ workflows
- **Backward Compatible**: Yes - only adds guidance, doesn't change file formats

## References

- Original Issue: User report 2025-11-13
- Related: `docs/RELEASE_NOTES_v3.14.0.md` (forward-looking templates)
- Template: `templates/service_architecture_template.json`
- Schema: `templates/schemas/service_architecture_schema.json`
- Tool: `tools/system_of_systems_graph_v2.py`
