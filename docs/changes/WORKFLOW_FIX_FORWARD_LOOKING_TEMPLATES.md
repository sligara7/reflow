# Workflow Fix: Forward-Looking Templates - Architecture Format Preparation

**Date**: 2025-11-08
**Version**: Reflow v3.14.0 (proposed)
**Priority**: CRITICAL
**Impact**: Prevents LLMs from creating improperly formatted architectures that block tool execution

## Problem Statement (User-Reported Root Cause)

**User**: "The reason sometimes it skips is that when it develops the architectures, it doesn't develop them properly - so when it gets to the steps where it is supposed to run the tools, it says it has to go back and reformat. Going into the workflows, it should have a good idea (or template) of what needs to be done prior to getting to the tool usage step"

### The Actual Failure Pattern

```
SE-02: Create service_architecture.json files
  → LLM creates architectures WITHOUT knowing exact format SE-06 needs
  → Missing sections: interfaces format, edge weights, proper component structure
  ↓
SE-03, SE-04, SE-05: Various steps
  ↓
SE-06: Run system_of_systems_graph_v2.py
  → LLM reads SE-06, discovers: "Tool needs 'interfaces' array with specific structure"
  → LLM realizes: "I created interfaces wrong in SE-02"
  → LLM: "I have to go back and reformat the architecture files"
  → Goes back to SE-02, reformats
  → **NEVER RETURNS to SE-06** (lost in reformatting, thinks it's "done")
  → User has to ask: "Did you run the graph tool?"
```

**Same problem in Functional Architecture**:
```
FA-02: Create functional_architecture.json
  → LLM creates it without knowing FA-05 tool requirements
  ↓
FA-05: Run system_of_systems_graph_v2.py --functional-mode
  → Discovers format issues
  → Goes back to reformat
  → Never returns to FA-05
```

## Root Cause Analysis

### Problem 1: Templates Don't Show Downstream Requirements

**SE-02-A01** (line 36) says:
```json
"required_sections": [
  "metadata (name, version, description)",
  "operational_view (capabilities, activities, services)",
  "system_view (components, interfaces, data_models)",
  ...
]
```

BUT it doesn't say:
- **WHY** these sections are required (SE-06 tool needs them)
- **WHAT FORMAT** interfaces must be in (array? object? what fields?)
- **WHAT HAPPENS** if missing (tool fails, have to reformat, lose progress)

### Problem 2: No Forward Reference to Tool Requirements

**SE-02** has only 4 mentions of SE-06 (lines 76, 151, 328, 692, 700):
- All are buried deep in the file
- None are in the PRIMARY action (SE-02-A01) where architectures are created
- None say "Create architecture in THIS EXACT FORMAT for SE-06 tool"

### Problem 3: No Immediate Validation

**Current flow**:
```
SE-02: Create architectures
  ↓ (no validation)
SE-03, SE-04, SE-05: Other stuff
  ↓ (4 steps later!)
SE-06: Discover format issues
```

**Should be**:
```
SE-02: Create architectures
  ↓ (IMMEDIATE validation)
SE-02-VALIDATE: Check format is correct for SE-06
  → If wrong: Fix NOW (don't wait 4 steps)
  → If right: Proceed to SE-03
```

### Problem 4: Templates vs. Tool Expectations Mismatch

**What template shows**:
```json
{
  "interfaces": {
    "provided": [...],
    "consumed": [...]
  }
}
```

**What tool expects** (from `system_of_systems_graph_v2.py` line 572):
```python
interfaces = node_data.get('interfaces', [])  # Expects ARRAY, not object!
```

**Result**: LLM follows template → creates object → tool fails → reformat loop

## Proposed Solution: Forward-Looking Templates

### Core Principle

**"Create architectures RIGHT THE FIRST TIME by knowing downstream tool requirements UPFRONT"**

Every architecture creation step (SE-02, FA-02, BU-05) must:
1. **State WHY** each section is required ("SE-06 graph tool needs this")
2. **Show EXACT format** the tool expects (array vs object, required fields)
3. **Validate IMMEDIATELY** after creation (don't wait for tool step)
4. **Reference tool documentation** explicitly ("See SE-06-A02 for tool requirements")

### Solution 1: Add "Required for Tool" Sections to Architecture Steps

**Update SE-02-A01** (Create service_architecture.json):

```json
{
  "action_id": "SE-02-A01",
  "description": "Create service_architecture.json with ALL sections required for SE-06 graph tool validation",

  "⚠️ CRITICAL_FORMAT_REQUIREMENTS": {
    "purpose": "These format requirements ensure SE-06 graph tool (system_of_systems_graph_v2.py) can read your architecture WITHOUT needing to go back and reformat",
    "if_format_wrong": "You will reach SE-06, discover format issues, have to return here to reformat, and may never complete SE-06",

    "required_for_se_06_graph_tool": {
      "tool": "system_of_systems_graph_v2.py",
      "tool_step": "SE-06-A02",
      "input_expectations": {
        "interfaces": {
          "format": "ARRAY (not object)",
          "structure": [
            {
              "interface_id": "string",
              "interface_name": "string",
              "type": "provided | consumed | internal",
              "protocol": "REST | gRPC | message_queue | database | file_system",
              "description": "string"
            }
          ],
          "tool_code_reference": "system_of_systems_graph_v2.py line 572: interfaces = node_data.get('interfaces', [])",
          "common_mistake": "Creating interfaces as object with 'provided'/'consumed' keys → Tool expects flat array",
          "correct_example": {
            "interfaces": [
              {"interface_id": "user_api", "type": "provided", "protocol": "REST"},
              {"interface_id": "database", "type": "consumed", "protocol": "database"}
            ]
          },
          "incorrect_example": {
            "interfaces": {
              "provided": ["user_api"],
              "consumed": ["database"]
            }
          }
        },

        "components": {
          "format": "ARRAY with specific fields for graph node creation",
          "required_fields": ["component_id", "component_name", "component_type"],
          "tool_code_reference": "system_of_systems_graph_v2.py line 150-152: Validates node_id and node_name exist",
          "purpose": "Tool creates graph nodes from components - missing fields cause crashes"
        },

        "dependencies": {
          "format": "ARRAY showing service-to-service dependencies",
          "structure": [
            {
              "service_id": "string",
              "interface_id": "string",
              "dependency_type": "required | optional"
            }
          ],
          "tool_code_reference": "Used to create graph edges between services",
          "purpose": "Tool creates edges from dependencies - missing this means orphaned nodes"
        },

        "edge_weights": {
          "condition": "REQUIRED if framework uses flow analysis (decision_flow, ecological)",
          "check": "Read working_memory.json -> framework_analysis.recommended_analyses contains 'flow'",
          "format": "weight field on each dependency/transition",
          "tool_code_reference": "Flow analysis requires edge weights - will fail with 'No capacity attribute' if missing",
          "when_to_add": "NOW in SE-02, not later in SE-06 (too late)"
        }
      }
    }
  },

  "immediate_validation_after_creation": {
    "validation_id": "SE-02-A01-VALIDATE",
    "run_immediately": "After creating each service_architecture.json file",
    "checks": [
      {
        "check": "interfaces field is ARRAY (not object)",
        "validation": "isinstance(data['interfaces'], list)",
        "on_fail": "FIX NOW: Convert interfaces object to array (see correct_example above)"
      },
      {
        "check": "All components have component_id and component_name",
        "validation": "for comp in data['components']: assert 'component_id' in comp and 'component_name' in comp",
        "on_fail": "FIX NOW: Add missing component_id or component_name fields"
      },
      {
        "check": "dependencies array exists if service has external dependencies",
        "validation": "'dependencies' in data if service consumes external interfaces",
        "on_fail": "FIX NOW: Add dependencies array showing which services this depends on"
      },
      {
        "check": "Edge weights present if framework requires them",
        "validation": "If flow analysis: all dependencies have 'weight' field",
        "on_fail": "FIX NOW: Add weight field to each dependency (see SE-02-A02B for guidance)"
      }
    ],
    "success_criteria": "ALL checks pass before proceeding to next service or next step",
    "tool_to_use": "Python json.load() + manual checks OR create validate_service_architecture_format.py helper"
  },

  "template_enhancements": {
    "update_template": "service_architecture_template.json",
    "add_comments": "Include EXTENSIVE inline comments explaining EACH field's purpose and format requirements",
    "show_examples": "Include 2-3 complete examples (simple service, complex service, service with edge weights)",
    "reference_tool_requirements": "Comment at top: 'This format is REQUIRED for SE-06 graph tool - DO NOT deviate from structure'"
  }
}
```

**Update FA-02** (Create functional_architecture.json):

```json
{
  "action_id": "FA-02-A02",
  "description": "Create functional_architecture.json with ALL sections required for FA-05 technical analysis tool",

  "⚠️ CRITICAL_FORMAT_REQUIREMENTS": {
    "purpose": "These format requirements ensure FA-05 analysis tool (system_of_systems_graph_v2.py --functional-mode) can read your functional architecture WITHOUT needing to go back and reformat",
    "if_format_wrong": "You will reach FA-05, discover format issues, have to return here to reformat, and may never complete FA-05",

    "required_for_fa_05_tool": {
      "tool": "system_of_systems_graph_v2.py --functional-mode",
      "tool_step": "FA-05",
      "input_expectations": {
        "functions": {
          "format": "ARRAY of function definitions",
          "required_fields": ["function_id", "function_name", "inputs", "outputs"],
          "structure": [
            {
              "function_id": "F-001",
              "function_name": "Validate User Input",
              "inputs": ["user_input"],
              "outputs": ["validation_result"],
              "description": "What this function does"
            }
          ],
          "purpose": "Tool creates graph nodes from functions - missing fields cause crashes"
        },

        "dependencies": {
          "format": "ARRAY showing function-to-function dependencies (who calls whom)",
          "structure": [
            {
              "source_function": "F-001",
              "target_function": "F-002",
              "data_flow": "validation_result"
            }
          ],
          "purpose": "Tool creates edges from dependencies - missing this means unreachable functions"
        }
      }
    }
  }
}
```

### Solution 2: Create Immediate Format Validation Tool

Create `tools/validate_architecture_format.py`:

```python
#!/usr/bin/env python3
"""
Validate architecture file format IMMEDIATELY after creation.

This prevents the "create wrong → discover at tool step → go back to reformat → never return" loop.

Usage:
    # After creating service_architecture.json in SE-02
    python3 validate_architecture_format.py /path/to/service_architecture.json --mode service

    # After creating functional_architecture.json in FA-02
    python3 validate_architecture_format.py /path/to/functional_architecture.json --mode functional

Exit codes:
    0: Format is correct for graph tool
    1: Format has issues that will break graph tool
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple

def validate_service_architecture_format(arch_path: Path) -> Tuple[bool, List[str]]:
    """Validate service_architecture.json format for SE-06 graph tool."""

    with open(arch_path) as f:
        data = json.load(f)

    errors = []
    warnings = []

    # Check 1: interfaces must be ARRAY (not object)
    if 'interfaces' in data:
        if not isinstance(data['interfaces'], list):
            errors.append(f"❌ CRITICAL: 'interfaces' must be ARRAY, not {type(data['interfaces']).__name__}")
            errors.append(f"   Tool expects: data.get('interfaces', []) → array")
            errors.append(f"   You have: object with keys {list(data['interfaces'].keys())}")
            errors.append(f"   FIX: Convert to array format (see SE-02-A01 correct_example)")

    # Check 2: components must have required fields
    if 'components' in data:
        for i, comp in enumerate(data['components']):
            if 'component_id' not in comp:
                errors.append(f"❌ CRITICAL: Component {i} missing 'component_id' (required for graph nodes)")
            if 'component_name' not in comp:
                errors.append(f"❌ CRITICAL: Component {i} missing 'component_name' (required for graph nodes)")

    # Check 3: dependencies should exist if service consumes interfaces
    consumed_interfaces = [iface for iface in data.get('interfaces', []) if iface.get('type') == 'consumed']
    if consumed_interfaces and 'dependencies' not in data:
        warnings.append(f"⚠️  WARNING: Service has {len(consumed_interfaces)} consumed interfaces but no 'dependencies' array")
        warnings.append(f"   This may cause orphaned service detection")

    # Check 4: edge weights if framework requires flow analysis
    # (Would need to check working_memory.json for framework)

    # Print results
    if errors:
        print("\n" + "="*80)
        print("❌ ARCHITECTURE FORMAT VALIDATION FAILED")
        print("="*80)
        print(f"\nFile: {arch_path}")
        print(f"\n{len(errors)} CRITICAL ERRORS (will break SE-06 graph tool):")
        for error in errors:
            print(f"  {error}")

        if warnings:
            print(f"\n{len(warnings)} WARNINGS:")
            for warning in warnings:
                print(f"  {warning}")

        print("\n" + "="*80)
        print("⚠️  DO NOT PROCEED TO SE-06 - FIX THESE ERRORS NOW")
        print("="*80)
        return False, errors

    print(f"\n✓ Architecture format is CORRECT for SE-06 graph tool: {arch_path}")
    if warnings:
        print(f"\n{len(warnings)} warnings (non-blocking):")
        for warning in warnings:
            print(f"  {warning}")

    return True, []

def validate_functional_architecture_format(arch_path: Path) -> Tuple[bool, List[str]]:
    """Validate functional_architecture.json format for FA-05 tool."""

    with open(arch_path) as f:
        data = json.load(f)

    errors = []

    # Check 1: functions array exists with required fields
    if 'functions' not in data:
        errors.append("❌ CRITICAL: Missing 'functions' array (required for FA-05 graph tool)")
    else:
        for i, func in enumerate(data['functions']):
            if 'function_id' not in func:
                errors.append(f"❌ CRITICAL: Function {i} missing 'function_id'")
            if 'function_name' not in func:
                errors.append(f"❌ CRITICAL: Function {i} missing 'function_name'")

    # Check 2: dependencies array exists
    if 'dependencies' not in data:
        errors.append("❌ CRITICAL: Missing 'dependencies' array (required for FA-05 to create graph edges)")

    if errors:
        print("\n❌ FUNCTIONAL ARCHITECTURE FORMAT VALIDATION FAILED")
        for error in errors:
            print(f"  {error}")
        print("\n⚠️  DO NOT PROCEED TO FA-05 - FIX THESE ERRORS NOW")
        return False, errors

    print(f"✓ Functional architecture format is CORRECT for FA-05 tool: {arch_path}")
    return True, []

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python3 validate_architecture_format.py <file_path> --mode <service|functional>")
        sys.exit(1)

    arch_path = Path(sys.argv[1])
    mode = sys.argv[3] if len(sys.argv) >= 4 else "service"

    if mode == "service":
        success, errors = validate_service_architecture_format(arch_path)
    elif mode == "functional":
        success, errors = validate_functional_architecture_format(arch_path)
    else:
        print(f"Unknown mode: {mode}")
        sys.exit(1)

    sys.exit(0 if success else 1)
```

### Solution 3: Add Validation Calls to Workflow Steps

**Update SE-02-A01** - Add immediate validation after architecture creation:

```json
{
  "action_id": "SE-02-A01",
  "execution_steps": [
    "1. Read service_architecture_template.json",
    "2. Create service_architecture_v1.0.0-{date}.json for this service",
    "3. ⚠️ IMMEDIATELY validate format:",
    "   python3 {reflow_root}/tools/validate_architecture_format.py specs/machine/service_arch/{service}/service_architecture_v1.0.0-{date}.json --mode service",
    "4. If validation FAILS: FIX format NOW before creating symlink",
    "5. If validation PASSES: Create symlink service_architecture.json",
    "6. Repeat for next service"
  ],

  "llm_agent_instructions": [
    "⚠️ CRITICAL: After creating EACH service_architecture.json, you MUST validate format immediately",
    "Run: python3 {reflow_root}/tools/validate_architecture_format.py <path> --mode service",
    "If validation fails: FIX the errors NOW (don't defer to SE-06)",
    "Common fix: interfaces must be ARRAY not object - see correct_example in this action",
    "DO NOT proceed to next service or next step until validation passes"
  ]
}
```

**Update FA-02** - Add immediate validation:

```json
{
  "action_id": "FA-02-A02",
  "execution_steps": [
    "1. Create functional_architecture.json",
    "2. ⚠️ IMMEDIATELY validate format:",
    "   python3 {reflow_root}/tools/validate_architecture_format.py specs/functional/functional_architecture.json --mode functional",
    "3. If validation FAILS: FIX format NOW",
    "4. If validation PASSES: Proceed to FA-02-A03"
  ]
}
```

### Solution 4: Enhanced Templates with Tool Requirements

**Update `templates/service_architecture_template.json`**:

```json
{
  "// CRITICAL FORMAT NOTICE": "This format is REQUIRED for SE-06 graph tool (system_of_systems_graph_v2.py). DO NOT deviate from structure or tool will fail.",
  "// Tool Expectations": "interfaces = ARRAY (not object), components = ARRAY with component_id/component_name, dependencies = ARRAY",
  "// Validation": "After creating this file, run: python3 tools/validate_architecture_format.py <this_file> --mode service",

  "metadata": {
    "service_name": "example_service",
    "...": "..."
  },

  "interfaces": [
    {
      "// NOTE": "This must be an ARRAY, not an object with 'provided'/'consumed' keys",
      "// Tool Code": "system_of_systems_graph_v2.py line 572: interfaces = node_data.get('interfaces', [])",
      "interface_id": "example_api",
      "interface_name": "Example REST API",
      "type": "provided",
      "protocol": "REST",
      "description": "External REST API for clients"
    },
    {
      "interface_id": "database_connection",
      "type": "consumed",
      "protocol": "database",
      "description": "PostgreSQL database connection"
    }
  ],

  "components": [
    {
      "// NOTE": "component_id and component_name are REQUIRED for graph node creation",
      "// Tool Code": "system_of_systems_graph_v2.py line 150-152: validates these fields exist",
      "component_id": "comp_001",
      "component_name": "API Handler",
      "...": "..."
    }
  ],

  "dependencies": [
    {
      "// NOTE": "This array creates graph edges between services",
      "service_id": "database_service",
      "interface_id": "database_connection",
      "dependency_type": "required"
    }
  ]
}
```

## Implementation Plan

**Phase 1: Immediate Validation** (Highest priority - prevents reformatting loops)
1. ✅ Create this documentation
2. ⬜ Create `tools/validate_architecture_format.py` (format validation tool)
3. ⬜ Update SE-02-A01: Add "CRITICAL_FORMAT_REQUIREMENTS" section with SE-06 tool expectations
4. ⬜ Update SE-02-A01: Add immediate validation call after architecture creation
5. ⬜ Update FA-02: Add "CRITICAL_FORMAT_REQUIREMENTS" section with FA-05 tool expectations
6. ⬜ Update FA-02: Add immediate validation call

**Phase 2: Template Enhancements** (Important - shows correct format upfront)
7. ⬜ Update `templates/service_architecture_template.json` with inline tool requirement comments
8. ⬜ Update `templates/functional_architecture_template.json` with inline tool requirement comments
9. ⬜ Add 2-3 complete examples to each template (simple, complex, with edge weights)

**Phase 3: Documentation** (Nice to have)
10. ⬜ Update CLAUDE.md: Add "Architecture Format Requirements" section
11. ⬜ Test with actual workflow execution (both SE and FA paths)
12. ⬜ Commit changes

**Estimated Time**: 3-5 hours

## Expected Outcomes

After these changes:
- ✅ LLMs create architectures in **correct format the FIRST time**
- ✅ Format validated **IMMEDIATELY** (not 4-5 steps later)
- ✅ NO MORE "go back and reformat" loops
- ✅ Tool steps become **SIMPLE**: Just run the tool (no format discovery)
- ✅ Templates **show exact format** tool expects (array vs object, required fields)
- ✅ LLMs **understand WHY** format matters (for downstream tools, not arbitrary rules)

## Success Criteria

1. ✅ LLM reads SE-02-A01, sees tool requirements, creates correct format first time
2. ✅ Validation script catches format errors immediately after creation
3. ✅ LLM reaches SE-06, runs tool successfully without going back to reformat
4. ✅ Same for FA-02 → FA-05 path
5. ✅ User feedback: "LLM didn't have to go back and reformat - it worked first try"

## Relationship to Other Fixes

This fix is **complementary** to the "Make Tool Unmissable" fix (`WORKFLOW_FIX_MANDATORY_GRAPH_TOOL.md`):

- **This fix**: Ensures architectures are formatted correctly BEFORE reaching tool step
- **Other fix**: Ensures tool step has unmissable warnings and blocking gates

**Both are needed**:
- Without this: LLM creates wrong format → goes back to reformat → loses track
- Without other: LLM creates right format → but still skips tool (no emphasis)
- With both: LLM creates right format → reaches tool step → sees unmissable warnings → runs tool successfully ✅
