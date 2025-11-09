# Workflow Fix: Make system_of_systems_graph_v2.py Execution Mandatory and Unmissable

**Date**: 2025-11-08
**Version**: Reflow v3.14.0 (proposed)
**Priority**: CRITICAL
**Impact**: Prevents architecture validation from being accidentally skipped

## Problem Statement

The `system_of_systems_graph_v2.py` tool is **THE FLAGSHIP VALIDATION TOOL** for Reflow, but it can be accidentally skipped by LLM agents because:

1. **Inconsistent emphasis** across workflows (SE-06 is good, FA-05 and BU-06 are weak)
2. **No verification** that the tool actually executed (workflows describe it but don't check)
3. **Ambiguous language** ("generate graph" sounds optional, not mandatory validation)
4. **Missing explicit warnings** to LLM agents that this step is CRITICAL and BLOCKING
5. **Workflow chain is long** (SE-01 → SE-02 → SE-03 → SE-04 → SE-05 → SE-06) - LLMs stop early

**User Report**: "This concerns me because this tool should not be skipped - the workflow should make this clear, so need to adjust the workflow so that this is not just skipped over"

### Actual Failure Scenario (Reported by User)

1. **Functional Architecture (FA-05)**: LLM **PURPOSEFULLY SKIPPED** the tool
   - FA-05 is only 88 lines (vs SE-06's 834 lines)
   - Contains word "optional" on line 16 (`--analyze-context (optional - AI workflows only)`)
   - LLM interpreted entire step as optional analysis

2. **Systems Engineering (After SE-01)**: LLM completed service allocation, user had to ASK if tool was run
   - LLM completed SE-01 (service decomposition/allocation)
   - Workflow chain: SE-01 → SE-02 (10 actions!) → SE-03 → SE-04 → SE-05 → SE-06
   - LLM either (a) never reached SE-06, or (b) reached SE-06 but didn't emphasize its criticality
   - User had to explicitly ask: "Have you run the system_of_systems_graph_v2.py tool?"

**Root Cause**: FA-05 is catastrophically weak (easily skippable) + SE-06 is 5 steps away from SE-01 (LLMs lose track)

## Proposed Solution

### 1. Standardize Tool Invocation Pattern (ALL Workflows)

**Before** (ambiguous, skippable):
```json
{
  "action_id": "XX-XX-A0X",
  "action_name": "Generate System Graph",
  "description": "Generate system_of_systems_graph.json with analysis",
  "tool": "system_of_systems_graph_v2.py"
}
```

**After** (mandatory, unmissable):
```json
{
  "action_id": "XX-XX-A0X",
  "action_name": "CRITICAL: VALIDATE ARCHITECTURE VIA GRAPH ANALYSIS",
  "description": "⚠️ MANDATORY BLOCKING STEP ⚠️ - Validate architecture by generating system graph with comprehensive NetworkX analysis, knowledge gap detection, and architectural issue validation. DO NOT SKIP THIS STEP.",
  "tool": "system_of_systems_graph_v2.py",
  "criticality": "CRITICAL",
  "blocking": true,
  "skippable": false,

  "llm_agent_pre_flight_checklist": {
    "STOP_BEFORE_PROCEEDING": "⚠️ YOU MUST COMPLETE THIS CHECKLIST BEFORE PROCEEDING ⚠️",
    "checks": [
      "[ ] I have read the tool command pattern for my framework",
      "[ ] I have selected framework-appropriate NetworkX analyses",
      "[ ] I have constructed the full command with all flags",
      "[ ] I am about to EXECUTE system_of_systems_graph_v2.py NOW",
      "[ ] I will READ the tool output carefully after execution",
      "[ ] I will VERIFY the output files exist after execution",
      "[ ] I will ANALYZE the results (centrality, gaps, issues) after execution"
    ],
    "if_you_skip_this": "The architecture is INVALID. You will miss critical issues (circular deps, orphaned services, async/sync mismatches, security violations, knowledge gaps). These issues will cause RUNTIME FAILURES in production."
  },

  "post_execution_verification": {
    "MANDATORY_CHECKS": "⚠️ VERIFY THESE FILES EXIST AFTER RUNNING TOOL ⚠️",
    "required_files": [
      "specs/machine/graphs/system_of_systems_graph.json (OR specs/functional/graphs/functional_architecture_graph.json for functional mode)",
      "specs/machine/architecture_issues.json (OR specs/functional/functional_architecture_issues.json)"
    ],
    "required_file_contents": {
      "system_of_systems_graph.json": ["nodes array (not empty)", "edges array", "networkx_analysis section", "framework_info section"],
      "architecture_issues.json": ["issues array (may be empty if clean)", "severity classifications"]
    },
    "verification_command": "ls -lh specs/machine/graphs/system_of_systems_graph.json && wc -l specs/machine/graphs/system_of_systems_graph.json",
    "failure_action": "If files missing or empty: Tool did NOT execute successfully. Re-run tool with verbose output to diagnose."
  }
}
```

### 2. Add Explicit Blocking Quality Gate

**Add to ALL workflows** (SE-06, FA-05, BU-06, feature_update, meta_analysis):

```json
{
  "quality_gate": {
    "gate_id": "G-XX-XX-GRAPH",
    "gate_name": "Architecture Graph Validation Gate",
    "blocking": true,
    "enforcement": "BLOCKING - MUST pass before proceeding to next step",

    "pre_gate_warning": "⚠️ CRITICAL BLOCKING GATE ⚠️ - You MUST have executed system_of_systems_graph_v2.py before this gate. If you skipped it, GO BACK and run it now.",

    "checks": [
      {
        "check_id": "GRAPH-01",
        "description": "system_of_systems_graph.json (or functional_architecture_graph.json) exists",
        "validation": "File exists at expected path",
        "severity": "CRITICAL - BLOCKING",
        "on_fail": "STOP. Run system_of_systems_graph_v2.py immediately."
      },
      {
        "check_id": "GRAPH-02",
        "description": "Graph file is not empty and has valid structure",
        "validation": "File size > 1KB, contains 'nodes' and 'edges' arrays, has 'networkx_analysis' section",
        "severity": "CRITICAL - BLOCKING",
        "on_fail": "STOP. Graph file incomplete. Re-run system_of_systems_graph_v2.py with verbose output."
      },
      {
        "check_id": "GRAPH-03",
        "description": "architecture_issues.json (or functional_architecture_issues.json) exists",
        "validation": "File exists at expected path",
        "severity": "CRITICAL - BLOCKING",
        "on_fail": "STOP. Run system_of_systems_graph_v2.py with --analyze-issues flag."
      },
      {
        "check_id": "GRAPH-04",
        "description": "No CRITICAL severity architectural issues remain unresolved",
        "validation": "architecture_issues.json has zero issues with severity='CRITICAL'",
        "severity": "CRITICAL - BLOCKING",
        "on_fail": "STOP. Fix CRITICAL issues in architecture files, then re-run system_of_systems_graph_v2.py."
      },
      {
        "check_id": "GRAPH-05",
        "description": "NetworkX analysis results present",
        "validation": "system_of_systems_graph.json contains networkx_analysis section with analysis results",
        "severity": "HIGH - BLOCKING",
        "on_fail": "STOP. Re-run system_of_systems_graph_v2.py with appropriate analysis flags (--centrality --community etc)."
      }
    ],

    "gate_decision": "pass|fail",
    "on_pass": "Proceed to next step",
    "on_fail": "BLOCK PROGRESSION. Cannot proceed until all checks pass. Fix issues and re-run validations.",

    "llm_agent_gate_execution": {
      "step_1": "READ this entire quality_gate section carefully",
      "step_2": "For each check, VERIFY the condition manually (ls files, check file contents)",
      "step_3": "If ANY check fails: STOP immediately, fix the issue, re-run tool",
      "step_4": "If ALL checks pass: Document gate passed in working_memory.json, proceed to next step",
      "step_5": "Update working_memory.json -> quality_gates_passed array with this gate_id"
    }
  }
}
```

### 3. Enhance LLM Agent Instructions (ALL Workflows)

Add to top of every action that uses `system_of_systems_graph_v2.py`:

```json
{
  "llm_agent_critical_warnings": [
    "⚠️⚠️⚠️ CRITICAL - DO NOT SKIP THIS STEP ⚠️⚠️⚠️",
    "",
    "This is NOT optional graph generation. This is MANDATORY ARCHITECTURE VALIDATION.",
    "",
    "If you skip this tool:",
    "  ❌ You will miss circular dependencies (runtime deadlocks)",
    "  ❌ You will miss orphaned services (deployment failures)",
    "  ❌ You will miss async/sync mismatches (performance degradation)",
    "  ❌ You will miss security boundary violations (security breaches)",
    "  ❌ You will miss interface mismatches (integration failures)",
    "  ❌ You will miss knowledge gaps (missing components)",
    "",
    "These issues cause PRODUCTION FAILURES that are 10-100x more expensive to fix after deployment.",
    "",
    "EXECUTION CHECKLIST (complete BEFORE proceeding):",
    "  1. ✓ Select framework-appropriate analyses (see analysis_selection_guidance)",
    "  2. ✓ Construct full command with all flags",
    "  3. ✓ EXECUTE system_of_systems_graph_v2.py NOW",
    "  4. ✓ READ the tool output (don't just glance - ANALYZE results)",
    "  5. ✓ VERIFY output files exist (system_of_systems_graph.json, architecture_issues.json)",
    "  6. ✓ CHECK for CRITICAL issues in architecture_issues.json",
    "  7. ✓ FIX any CRITICAL issues, re-run tool until clean",
    "  8. ✓ UPDATE working_memory.json with analysis results",
    "",
    "DO NOT proceed to next step until ALL 8 checklist items are ✓ complete."
  ]
}
```

### 4. Add Tool Execution Verification (New Helper Script)

Create `tools/verify_graph_tool_execution.py`:

```python
#!/usr/bin/env python3
"""
Verify that system_of_systems_graph_v2.py actually executed successfully.

This is a BLOCKING validation script that workflows should call AFTER
the graph tool to ensure it actually ran (not just described running it).

Usage:
    python3 verify_graph_tool_execution.py /path/to/system_root [--functional-mode]

Exit codes:
    0: Success - tool executed, files valid
    1: Failure - tool did not execute or files invalid
"""

import sys
import json
from pathlib import Path

def verify_graph_execution(system_root: Path, functional_mode: bool = False) -> bool:
    """Verify system_of_systems_graph_v2.py executed successfully."""

    # Determine expected paths
    if functional_mode:
        graph_path = system_root / "specs/functional/graphs/functional_architecture_graph.json"
        issues_path = system_root / "specs/functional/functional_architecture_issues.json"
    else:
        graph_path = system_root / "specs/machine/graphs/system_of_systems_graph.json"
        issues_path = system_root / "specs/machine/architecture_issues.json"

    checks_passed = []
    checks_failed = []

    # Check 1: Graph file exists
    if not graph_path.exists():
        checks_failed.append(f"❌ CRITICAL: {graph_path} does NOT exist - tool did not execute")
        return False
    checks_passed.append(f"✓ Graph file exists: {graph_path}")

    # Check 2: Graph file not empty
    if graph_path.stat().st_size < 100:
        checks_failed.append(f"❌ CRITICAL: {graph_path} is empty or too small - tool execution failed")
        return False
    checks_passed.append(f"✓ Graph file has content ({graph_path.stat().st_size} bytes)")

    # Check 3: Graph file is valid JSON
    try:
        with open(graph_path) as f:
            graph_data = json.load(f)
    except json.JSONDecodeError as e:
        checks_failed.append(f"❌ CRITICAL: {graph_path} is not valid JSON - {e}")
        return False
    checks_passed.append("✓ Graph file is valid JSON")

    # Check 4: Graph has required sections
    required_sections = ["nodes", "edges", "framework_info"]
    for section in required_sections:
        if section not in graph_data:
            checks_failed.append(f"❌ CRITICAL: Graph missing required section '{section}'")
            return False
    checks_passed.append(f"✓ Graph has required sections: {required_sections}")

    # Check 5: Graph has nodes and edges
    if not graph_data.get("nodes"):
        checks_failed.append("❌ CRITICAL: Graph has zero nodes - architecture is empty")
        return False
    if not graph_data.get("edges"):
        checks_failed.append("⚠️  WARNING: Graph has zero edges - architecture has no connections")
    checks_passed.append(f"✓ Graph has {len(graph_data['nodes'])} nodes and {len(graph_data.get('edges', []))} edges")

    # Check 6: NetworkX analysis results present
    if "networkx_analysis" not in graph_data:
        checks_failed.append("⚠️  WARNING: No NetworkX analysis results - tool may not have run with analysis flags")
    else:
        checks_passed.append("✓ NetworkX analysis results present")

    # Check 7: Issues file exists
    if not issues_path.exists():
        checks_failed.append(f"⚠️  WARNING: {issues_path} does NOT exist - gap detection may not have run")
    else:
        checks_passed.append(f"✓ Issues file exists: {issues_path}")

        # Check 8: Issues file is valid JSON
        try:
            with open(issues_path) as f:
                issues_data = json.load(f)

            # Check 9: No CRITICAL issues
            critical_issues = [i for i in issues_data.get("issues", []) if i.get("severity") == "CRITICAL"]
            if critical_issues:
                checks_failed.append(f"❌ CRITICAL: {len(critical_issues)} CRITICAL architectural issues detected - MUST FIX before proceeding")
                for issue in critical_issues[:3]:  # Show first 3
                    checks_failed.append(f"   - {issue.get('type')}: {issue.get('description')}")
                return False
            checks_passed.append("✓ No CRITICAL architectural issues")

        except json.JSONDecodeError:
            checks_failed.append(f"⚠️  WARNING: {issues_path} is not valid JSON")

    # Print results
    print("\n" + "="*80)
    print("GRAPH TOOL EXECUTION VERIFICATION")
    print("="*80)
    print("\nPASSED CHECKS:")
    for check in checks_passed:
        print(f"  {check}")

    if checks_failed:
        print("\nFAILED CHECKS:")
        for check in checks_failed:
            print(f"  {check}")
        print("\n" + "="*80)
        print("❌ VERIFICATION FAILED - system_of_systems_graph_v2.py did NOT execute successfully")
        print("="*80)
        return False

    print("\n" + "="*80)
    print("✓ VERIFICATION PASSED - system_of_systems_graph_v2.py executed successfully")
    print("="*80)
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 verify_graph_tool_execution.py /path/to/system_root [--functional-mode]")
        sys.exit(1)

    system_root = Path(sys.argv[1])
    functional_mode = "--functional-mode" in sys.argv

    success = verify_graph_execution(system_root, functional_mode)
    sys.exit(0 if success else 1)
```

### 5. Add Workflow Chain Reminder to SE-01 (CRITICAL FIX)

**Problem**: LLMs complete SE-01 (service allocation) and think they're done, never reaching SE-06 (5 steps away)

**Solution**: Add prominent reminder to SE-01 that SE-06 is MANDATORY:

```json
{
  "step_id": "SE-01",
  "name": "System Analysis & Service Decomposition",

  "llm_agent_workflow_chain_reminder": {
    "IMPORTANT": "⚠️ SE-01 is just the BEGINNING of the systems engineering workflow ⚠️",
    "full_workflow_chain": [
      "SE-01: Service Decomposition (YOU ARE HERE)",
      "SE-02: Service Architecture (10 actions)",
      "SE-03: Constraints & Template Validation",
      "SE-04: Deployment Architecture Reconciliation",
      "SE-05: Consistency & Specification Verification",
      "SE-06: Graph Generation ← CRITICAL VALIDATION TOOL RUNS HERE (MANDATORY)"
    ],
    "do_not_stop_early": "You MUST complete ALL steps SE-01 through SE-06. Stopping at SE-01 means you have NOT validated the architecture.",
    "se_06_is_mandatory": "SE-06 runs system_of_systems_graph_v2.py which validates your architecture for circular dependencies, orphaned services, async/sync mismatches, security violations, and knowledge gaps. This is NOT optional.",
    "typical_time": "SE-01 (30 min) → SE-02 (2-3 hours) → SE-03 (20 min) → SE-04 (30 min) → SE-05 (20 min) → SE-06 (30 min) = 4-5 hours total",
    "if_you_skip_se_06": "Your architecture is INVALID. Critical issues will cause production failures."
  }
}
```

**Add this to**:
- `workflow_steps/systems_engineering/SE-01-AnalysisAndDecomposition.json`
- At the END of the step (after all actions, before next_step)

### 6. Update Workflow Files

**Files to update** (Priority order):

1. **CRITICAL** - `workflow_steps/functional_analysis/FA-05-TechnicalAnalysis.json` ❌
   - Currently: 88 lines, contains "optional", easily skippable
   - Target: 800+ lines like SE-06, unmissable warnings, blocking gate
   - Impact: HIGHEST (user reported purposeful skip here)

2. **HIGH** - `workflow_steps/systems_engineering/SE-01-AnalysisAndDecomposition.json` ⚠️
   - Add workflow chain reminder (see section 5 above)
   - Prevent LLMs from stopping early

3. **MEDIUM** - `workflow_steps/systems_engineering/SE-06-GraphGeneration.json` ✓
   - Already good (834 lines), but add explicit blocking gate with file verification
   - Add pre-flight checklist

4. **MEDIUM** - `workflow_steps/bottom_up_integration/BU-06-ValidationVerification.json` ⚠️
   - Currently moderate, needs enhancement with explicit warnings

5. **LOW** - `workflows/feature_update.json`
   - Check if it references graph tool properly, add warnings if needed

6. **LOW** - `workflows/99-meta_analysis.json`
   - Check if it references graph tool properly, add warnings if needed

**Changes for each**:
- Add `llm_agent_critical_warnings` section (see template above)
- Add `llm_agent_pre_flight_checklist` (see template above)
- Add `post_execution_verification` with file checks (see template above)
- Add explicit BLOCKING quality gate with 5 checks (see template above)
- Add verification script call: `python3 {reflow_root}/tools/verify_graph_tool_execution.py {system_root}`

### 6. Update CLAUDE.md Documentation

Add new section to CLAUDE.md:

```markdown
## ⚠️ CRITICAL: The Graph Tool is NOT Optional

**Tool**: `system_of_systems_graph_v2.py`
**Status**: MANDATORY - NEVER skip this tool
**Why**: This is THE validation tool for architecture quality

### What This Tool Does

NOT just graph generation - this tool:
- ✅ Validates architecture completeness (no missing components)
- ✅ Detects circular dependencies (runtime deadlocks)
- ✅ Finds orphaned services (deployment failures)
- ✅ Identifies async/sync mismatches (performance issues)
- ✅ Discovers security boundary violations (security breaches)
- ✅ Checks interface consistency (integration failures)
- ✅ Analyzes with 25+ NetworkX algorithms (centrality, community, cycles, flow, etc.)

### Cost of Skipping

If you skip this tool, you WILL have production failures:
- **Circular dependencies** → Runtime deadlocks, services can't start
- **Orphaned services** → Deployed but never called, wasted resources
- **Async/sync mismatches** → Event loop blocked, 10x performance degradation
- **Security violations** → Public services bypass auth, data breaches
- **Interface mismatches** → Services can't communicate, integration failures

**Fix cost**: 10-100x more expensive after deployment vs. catching during architecture phase

### When To Run

**Every time** you:
- Complete service architecture (SE-06)
- Complete functional architecture (FA-05)
- Complete bottom-up integration (BU-06)
- Update features (feature_update workflow)
- Analyze Reflow itself (meta_analysis workflow)

### How To Know You Ran It

**After running**, these files MUST exist:
- `specs/machine/graphs/system_of_systems_graph.json` (OR `specs/functional/graphs/functional_architecture_graph.json`)
- `specs/machine/architecture_issues.json` (OR `specs/functional/functional_architecture_issues.json`)

**Verification command**:
```bash
python3 {reflow_root}/tools/verify_graph_tool_execution.py {system_root}
# Exit code 0 = success, 1 = failure
```

### If You Accidentally Skipped

**STOP. Go back. Run it now.**

You cannot proceed to next workflow without running this tool. The architecture is invalid.
```

## Implementation Plan (Priority Order)

**Phase 1: Critical Fixes** (Cannot ship without these)
1. ✅ Create this documentation (`WORKFLOW_FIX_MANDATORY_GRAPH_TOOL.md`)
2. ⬜ **CRITICAL** - Overhaul FA-05-TechnicalAnalysis.json
   - Expand from 88 lines to 800+ lines
   - Remove ALL instances of "optional"
   - Add unmissable warnings, blocking gate, pre-flight checklist
   - Add post-execution verification
   - Make it match SE-06's level of detail
3. ⬜ **HIGH** - Add workflow chain reminder to SE-01-AnalysisAndDecomposition.json
   - Prevent LLMs from stopping after SE-01
   - Remind about mandatory SE-06 completion
4. ⬜ Create verification script (`tools/verify_graph_tool_execution.py`)
   - Automated file existence and validity checks
   - Called after every graph tool execution

**Phase 2: Important Enhancements** (Should have)
5. ⬜ **MEDIUM** - Enhance SE-06-GraphGeneration.json
   - Add explicit blocking quality gate with file verification
   - Add pre-flight checklist
   - Call verification script
6. ⬜ **MEDIUM** - Update BU-06-ValidationVerification.json
   - Add explicit warnings, blocking gate
   - Call verification script
7. ⬜ Update CLAUDE.md with "CRITICAL: The Graph Tool is NOT Optional" section

**Phase 3: Nice to Have** (Polish)
8. ⬜ **LOW** - Check and update workflows/feature_update.json
9. ⬜ **LOW** - Check and update workflows/99-meta_analysis.json
10. ⬜ Test with sample workflow execution (both FA and SE paths)
11. ⬜ Commit changes with comprehensive message

**Estimated Time**:
- Phase 1 (Critical): 2-3 hours
- Phase 2 (Important): 1-2 hours
- Phase 3 (Polish): 1 hour
- **Total: 4-6 hours**

## Expected Outcomes

After these changes:
- ✅ LLM agents **cannot miss** the graph tool - warnings are unmissable
- ✅ Workflows **block** if tool not executed - explicit verification checks
- ✅ Language is **unambiguous** - "CRITICAL VALIDATION" not "generate graph"
- ✅ **Consistent** across all workflows - same emphasis everywhere
- ✅ **Verifiable** - automated script confirms execution
- ✅ **Educational** - LLMs understand WHY this is critical (cost of skipping)

## Risk Mitigation

**Risk**: Too many warnings might cause "warning fatigue"
**Mitigation**: Only use ⚠️  symbols for truly CRITICAL steps (this qualifies)

**Risk**: Verification script might false positive/negative
**Mitigation**: Test thoroughly with various scenarios (empty files, partial execution, full success)

**Risk**: Breaking changes to existing workflows
**Mitigation**: Enhancements are backward-compatible (add checks, don't remove steps)

## Success Criteria

1. ✅ LLM agent runs workflow and **automatically** executes graph tool (without user prompting)
2. ✅ Workflow **blocks** if graph tool not executed (verification catches it)
3. ✅ LLM agent **understands** why tool is critical (reads warnings, doesn't skip)
4. ✅ User feedback: "This is much clearer now - LLM didn't skip the tool"

## Version

Target: **Reflow v3.14.0**
Priority: **CRITICAL**
Estimated effort: **2-4 hours**
