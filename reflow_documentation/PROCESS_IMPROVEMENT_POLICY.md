# Process Improvement Collection and Implementation Policy

## Overview

The reflow system includes a sophisticated process improvement mechanism that distinguishes between system-specific improvements (which can be implemented immediately) and generic workflow improvements (which are collected for later review).

## Two Types of Process Improvements

### 🔧 System-Specific Improvements
**Scope**: Apply only to the current system being developed
**Action**: Prompt user for immediate implementation
**Location**: Document in `systems/<system_name>/process_log.md`

**Examples**:
- Add missing interface to specific service
- Correct component dependency in current system
- Fix validation error in current service_architecture.json
- Improve specific component's resource allocation

**Workflow**:
1. **IDENTIFY**: Is this improvement specific to current system?
2. **PROMPT**: "Would you like to implement this improvement now: [description]? (y/n)"
3. **IF YES**: Implement immediately and document in process_log.md
4. **IF NO**: Log as deferred improvement in process_log.md
5. **CONTINUE**: Resume workflow execution

### 📋 Generic Workflow Improvements
**Scope**: Apply to the workflow, templates, tools, or process itself
**Action**: Collect to inbox.jsonl for later review and implementation
**Location**: `./process_improvements/inbox/inbox.jsonl`

**Examples**:
- Add validation step to workflow
- Improve template format
- Enhance tool functionality
- Update shared policies

## Classification Decision Tree

### Questions to Ask:
1. Does this improvement apply only to the current system being developed?
2. Does this improvement involve changing decision_flow.json, templates, or tools?
3. Does this improvement affect how future systems would be developed?

### Routing Logic:
- **Current system only** → System-specific → Prompt for immediate implementation
- **Affects workflow or tools** → Generic → Collect to inbox.jsonl
- **Affects future systems** → Generic → Collect to inbox.jsonl

## System-Specific Implementation Format

### Documentation Location
```
systems/<system_name>/process_log.md
```

### Format Example
```markdown
## Process Improvement - 2025-10-14T10:30:00Z
**Improvement**: Add auth_requirement to coordinator service
**Status**: Implemented
**Rationale**: Satisfies security validation requirements
**Files Modified**: specs/machine/service_arch/coordinator/service_architecture.json
```

### Required Fields
- `timestamp`
- `improvement_description`
- `implementation_status` (implemented|deferred|rejected)
- `rationale_for_status`
- `files_modified` (if implemented)

## Generic Workflow Improvements Format

### ✅ CORRECT: Use JSONL Format
- **File**: `./process_improvements/inbox/inbox.jsonl`
- **Format**: One JSON object per line (JSONL)
- **Template**: Follow `./process_improvements/template.json` structure

### Required Fields
```json
{
  "timestamp": "2025-10-14T10:30:00Z",
  "workflow_area": "architecture|development|feature_update|decision_flow|shared_policies",
  "sub_id": "A2.S2.4",
  "category": "context_management|iteration|artifact_routing|validation|tooling|docs|usability|automation",
  "suggestion": "Generic, system-agnostic improvement proposal",
  "rationale": "Why this improves the process",
  "evidence_refs": ["repo-relative/path1", "repo-relative/path2"],
  "impact": "low|medium|high",
  "status": "proposed"
}
```

## User Interaction for System-Specific Improvements

### Prompt Format
```
🔧 PROCESS IMPROVEMENT IDENTIFIED:
[improvement_description]

This improvement is specific to the current system 'system_name' and can be implemented immediately.

Would you like to implement this now? (y/n)

If yes, I will make the necessary changes and continue the workflow.
If no, I will document it for later implementation.
```

### Timeout Behavior
- If no response in 30 seconds, document as deferred and continue workflow

## Collection Triggers

Process improvements should be collected:
- `on_refresh_complete`
- `on_step_exit`
- `after_validation_failure_resolved`
- `at_workflow_completion`
- `when_discovering_process_inefficiency`
- `when_identifying_system_specific_optimization`

## Critical Rules

### For System-Specific Improvements:
1. **CLASSIFY first**: Determine if improvement is system-specific
2. **PROMPT user**: Always ask before implementing
3. **DOCUMENT**: Log in systems/<system_name>/process_log.md
4. **NO automatic implementation**: User confirmation required

### For Generic Improvements:
1. **Generic Only**: Must be system-agnostic with no system/service names
2. **Repo-Relative Paths**: Use only repo-relative paths in evidence_refs
3. **No Secrets**: Never include secrets, tokens, or sensitive information
4. **JSONL Format**: Always append to inbox.jsonl as proper JSON objects
5. **Template Compliance**: Follow the template.json structure exactly

### Invalid Approaches ❌
- Creating `PROCESS_IMPROVEMENTS.md` files in system directories
- Implementing system-specific changes without user confirmation
- Putting system-specific improvements in generic inbox.jsonl
- Including system-specific names in generic improvements
- Using absolute paths in evidence_refs
- Writing improvements as markdown instead of proper format

## Integration with Decision Flow

The enhanced decision_flow.json now includes:
- **Classification decision tree** for routing improvements appropriately
- **User prompting mechanism** for system-specific improvements
- **Dual-track documentation** (process_log.md vs inbox.jsonl)
- **Enhanced degradation signals** for incorrect classification
- **Timeout handling** for user interaction

This ensures all process improvements are handled appropriately - immediate implementation for system-specific optimizations, and systematic collection for workflow enhancements.