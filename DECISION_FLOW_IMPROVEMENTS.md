# Decision Flow Workflow Improvements

## Problem Statement

The current `decision_flow.json` workflow has three key limitations:

### 1. **Context Overload for LLM Agents**
- **Issue**: The file is ~1600 lines with multiple levels of nested instructions
- **Effect**: LLM agents repeatedly forget instructions and require reminders
- **Root Cause**: Instructions are not chunked into focused, referenceable modules
- **Impact**: Token wastage, repeated context reloads, user frustration

### 2. **Repository Clutter**
- **Issue**: Agents create intermediate reports, summaries, and artifacts in system directories
- **Effect**: System directories become cluttered with non-essential files
- **Current State**: No enforcement of the 4-folder structure (context, specs, services, docs)
- **Target State**: ONLY these 4 folders should exist at system root level

### 3. **Instruction Non-Adherence**
- **Issue**: Agents violate "NEVER_GENERATE_REPORTS" rule repeatedly
- **Effect**: User has to monitor every interaction and remind agent
- **Root Cause**: Rule is buried in ~1600 line document; not easily accessible

---

## Solution Architecture

### Phase 1: Modularize Instructions into Focused Chunks

Instead of one massive `decision_flow.json`, create focused instruction modules:

```
reflow/instructions/
├── 1-behavioral-rules.json          # NEVER generate reports, mandatory adherence, etc.
├── 2-file-locations.json            # CRITICAL_FILE_LOCATIONS section only
├── 3-system-isolation.json          # pwd verification, cross-contamination prevention
├── 4-context-refresh.json           # When/how to refresh context
├── 5-tool-reference.json            # All tool documentation
├── 6-workflow-decisions.json        # Decision trees (D0-D4)
├── 7-quality-gates.json             # Validation checkpoints
└── README.md                        # Index explaining when each module is needed
```

**Benefits:**
- Each module <300 lines (fits easily in context)
- Agent can reference specific module by name
- Modules stack together for comprehensive context
- Easy to update individual sections without affecting others

### Phase 2: Enforce Directory Structure with Validation

Create automated validation to prevent clutter:

```json
{
  "artifact_management": {
    "allowed_root_folders": ["context", "specs", "services", "docs"],
    "validation_rules": {
      "check_root_artifacts": {
        "description": "No files/folders allowed in system root except the 4 main folders",
        "prohibited_patterns": [
          "*.md (except README.md if system root readme is needed)",
          "*.json (except build_ready_index.json in services/)",
          "*.txt",
          "*_summary*",
          "*_report*",
          "*.backup",
          "*.tmp"
        ],
        "tool": "./tools/validate_directory_structure.py",
        "when_to_run": [
          "Before each workflow step",
          "After context refresh",
          "At quality gates"
        ]
      },
      "cleanup_procedure": {
        "description": "Automatic cleanup of prohibited artifacts",
        "steps": [
          "1. Identify all files/folders not in allowed_root_folders",
          "2. Generate cleanup report listing files to remove",
          "3. Prompt user for confirmation",
          "4. Remove prohibited artifacts",
          "5. Document cleanup in context/process_log.md"
        ],
        "automation": "python3 tools/cleanup_system_directory.py <system_path> --auto-clean"
      }
    }
  }
}
```

### Phase 3: Make Behavioral Rules Non-Negotiable

Create a "Rules Injection" system:

```
reflow/
├── instructions/
│   └── 1-behavioral-rules.json      # All MUST-DO rules
└── tools/
    └── enforce_behavioral_rules.py  # Pre-execution validation
```

**How it works:**
1. Before EVERY workflow operation, agent reads `1-behavioral-rules.json`
2. Tool validates agent is NOT about to:
   - Generate reports
   - Create files outside allowed folders
   - Work in wrong directory
   - Cross-contaminate systems
3. If validation fails, workflow stops with clear error

---

## Implementation Plan

### Step 1: Create Modular Instruction Files (1-2 hours)

Create `/home/ajs7/project/reflow/instructions/` directory with:
- `1-behavioral-rules.json` - Extracted from CRITICAL_BEHAVIORAL_RULES section
- `2-file-locations.json` - Extracted from CRITICAL_FILE_LOCATIONS section  
- `3-system-isolation.json` - Extracted from system_isolation section
- `4-context-refresh.json` - Refresh triggers, sequences, degradation signals
- `5-tool-reference.json` - tool_reference section (with better organization)
- `6-workflow-decisions.json` - decisions section (D0-D4)
- `7-quality-gates.json` - quality_gates and handoff_requirements
- `INDEX.md` - Documentation of when/how to use each module

### Step 2: Create Directory Validation Tool (1-2 hours)

Implement:
```python
# tools/validate_directory_structure.py
- Check only 4 root folders exist
- Identify prohibited artifacts
- Generate cleanup report
- Optional auto-cleanup mode
```

### Step 3: Create Behavioral Rules Enforcer (1-2 hours)

Implement:
```python
# tools/enforce_behavioral_rules.py
- Load 1-behavioral-rules.json
- Pre-operation validation checklist
- Block operations that violate rules
- Log rule violations
```

### Step 4: Update decision_flow.json (2-3 hours)

Modify main file to:
- Reduce size to <500 lines (just decision tree structure)
- Reference modular instruction files
- Include "instruction module stacking" guide
- Add mandatory pre-operation checklist referencing modules

---

## Chunking Strategy: Instruction Module Composition

When agent needs comprehensive context, it loads modules in this order:

```
# For ANY workflow operation:
LOAD: 1-behavioral-rules.json       # What NOT to do (non-negotiable)
LOAD: 2-file-locations.json         # Where files must be
LOAD: 3-system-isolation.json       # pwd verification

# For specific operations:
IF architecture_workflow:
  LOAD: 6-workflow-decisions.json   # Which decision path to follow
  LOAD: 5-tool-reference.json       # Tools for this phase
  LOAD: 7-quality-gates.json        # When to validate

IF development_workflow:
  LOAD: 6-workflow-decisions.json   # D3 decision logic
  LOAD: 5-tool-reference.json       # Dev-specific tools
  LOAD: 7-quality-gates.json        # Dev quality gates
```

**Result**: 
- Each load is 100-200 lines (fits in local context)
- Agent can reference modules by name: "Load 1-behavioral-rules"
- No need to re-read massive file
- Rules are compartmentalized and maintainable

---

## Expected Improvements

### Before (Current State)
- decision_flow.json: ~1600 lines
- Agent repeatedly forgets "NEVER generate reports"
- User has to re-explain rules frequently
- System directories accumulate clutter
- No automated enforcement

### After (Proposed State)
- Main decision_flow.json: ~300 lines (lightweight reference)
- Instruction modules: 7 focused files (~150-250 lines each)
- Behavioral rules enforced BEFORE execution
- Directory validation prevents clutter
- Agent can reference specific modules when needed
- Clear separation between "mandatory behavior" and "optional guidance"

---

## Integration Points

### 1. Pre-Operation Hook (NEW)
```json
{
  "pre_operation_checklist": {
    "description": "MUST run before every workflow operation",
    "steps": [
      "1. Load instructions/1-behavioral-rules.json",
      "2. Verify pwd is correct system directory (from 3-system-isolation.json)",
      "3. Verify NOT about to generate report (from 1-behavioral-rules.json)",
      "4. Verify operation aligns with current step (from step_progress_tracker.json)",
      "5. Run directory structure validation (tools/validate_directory_structure.py)",
      "6. Proceed with operation only if all checks pass"
    ]
  }
}
```

### 2. Post-Operation Hook (NEW)
```json
{
  "post_operation_cleanup": {
    "description": "MUST run after major workflow operations",
    "steps": [
      "1. Update context/process_log.md with operation details",
      "2. Update context/step_progress_tracker.json with progress",
      "3. Run directory structure validation",
      "4. If prohibited artifacts detected, run cleanup tool",
      "5. Confirm directory is clean before continuing"
    ]
  }
}
```

### 3. Context Refresh Integration
When context refresh is triggered (operation_count >= 4):
- Load only the modules relevant to current workflow phase
- Skip redundant modules already loaded
- Update operation counter in tracking file

---

## Success Criteria

✓ Agent spontaneously avoids generating reports (rule is accessible, not buried)
✓ No need for user to remind agent repeatedly  
✓ System directories remain clean (only 4 folders)
✓ When agent goes off track, pre-operation validation catches it
✓ Agent can reference "Load module X" instead of re-reading massive file
✓ Workflow remains identical; only instruction delivery changes
✓ No performance impact; just better organization

---

## Recommendation

**Implement in this order:**
1. ✅ First: Create instruction modules + INDEX.md (don't modify decision_flow yet)
2. ✅ Second: Create validation tools (directory structure + behavioral rules enforcer)
3. ✅ Third: Test tools with existing system
4. ✅ Fourth: Modify decision_flow.json to reference modules
5. ✅ Fifth: Document module stacking approach for agents

This approach:
- Reduces risk (modules are additive, not replacing)
- Allows gradual rollout (test modules first)
- Keeps decision_flow.json as reference point during transition
- Solves all three problems systematically
