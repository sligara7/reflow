# Context Refresh - Quick Reference Guide

## When to Refresh (Manual Procedure Until Automation Restored)

### Trigger 1: After ~5 Major Operations

**Count these operations**:
- ✅ Creating or modifying files
- ✅ Running validation tools
- ✅ Generating artifacts
- ✅ Complex analysis or transformations

**Don't count these**:
- ❌ Reading tracking files
- ❌ Updating working_memory.json or step_progress_tracker.json
- ❌ Reading workflow or template files

**Example count**:
1. Create service_architecture.json (count = 1)
2. Run validate_architecture.py (count = 2)
3. Create fixed_service_architecture.json (count = 3)
4. Run system_of_systems_graph.py (count = 4)
5. Create interface_registry.json (count = 5) ← **REFRESH NOW**

---

### Trigger 2: Degradation Signals Detected

**Immediate refresh if you notice**:
- ⚠️ Asking about system name (it's in working_memory.json!)
- ⚠️ Forgetting current step or workflow
- ⚠️ Using wrong template format
- ⚠️ Working in wrong system directory
- ⚠️ Creating files in wrong location
- ⚠️ pwd doesn't match system_name
- ⚠️ Referencing files from other systems
- ⚠️ Generating summaries or reports unexpectedly

**If ANY of these occur → STOP and REFRESH immediately**

---

## Context Refresh Procedure

### Step-by-Step

```bash
# 1. PAUSE - Stop all operations
# (Don't create/modify any more files until refresh complete)

# 2. VERIFY PWD - Confirm correct system directory
pwd
# Should show: /absolute/path/to/your/system
# If wrong → cd /correct/path/to/system

# 3. SAVE STATE - Update tracking files
# Edit context/working_memory.json:
# - Update current_step if changed
# - Set operations_since_refresh = 0
# - Set last_refresh_timestamp = current timestamp
# - Add to context_metadata.refresh_triggers_met

# Edit context/step_progress_tracker.json:
# - Mark any completed actions
# - Update progress percentages

# 4. RELOAD CORE FILES - Re-read critical reflow files
cat {reflow_root}/definitions/architectural_definitions.json
cat {reflow_root}/workflows/{current_workflow}.json
cat {reflow_root}/templates/{relevant_templates}

# 5. RELOAD CONTEXT FILES - Re-read system context
cat context/current_focus.md          # (or dev_current_focus.md if development)
cat context/step_progress_tracker.json  # (or dev_progress_tracker.json)
cat context/working_memory.json

# 6. VERIFY ALIGNMENT - Check everything matches
# Confirm:
# - System name: [your system name]
# - Current workflow: [e.g., 01-systems_engineering]
# - Current step: [e.g., SE-02]
# - Next action: [what you plan to do next]

# 7. FINAL CHECKS
# ✓ pwd is correct system directory
# ✓ operations_since_refresh = 0
# ✓ Next action aligns with workflow step
# ✓ Not about to generate a report or summary

# 8. RESUME - Continue with confirmed action
```

---

## Quick Checklist Format

Copy this checklist and use it for each refresh:

```
CONTEXT REFRESH CHECKLIST
========================

□ PAUSE: Stopped all operations
□ VERIFY PWD: pwd = /path/to/system ✓
□ SAVE STATE:
  □ Updated working_memory.json
  □ Set operations_since_refresh = 0
  □ Set last_refresh_timestamp
  □ Updated step_progress_tracker.json
□ RELOAD CORE:
  □ Read architectural_definitions.json
  □ Read current workflow file
  □ Read relevant templates
□ RELOAD CONTEXT:
  □ Read current_focus.md
  □ Read step_progress_tracker.json
  □ Read working_memory.json
□ VERIFY:
  □ System name: ___________
  □ Current workflow: ___________
  □ Current step: ___________
  □ Next action: ___________
□ FINAL CHECKS:
  □ pwd correct
  □ operations_since_refresh = 0
  □ Action aligns with workflow
  □ Not generating report
□ RESUME
```

---

## working_memory.json Example

**Before refresh** (operations_since_refresh = 5):
```json
{
  "system_name": "my_system",
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "operations_since_refresh": 5,
  "last_refresh_timestamp": "2025-10-24T10:00:00Z",
  "context_metadata": {
    "refresh_triggers_met": []
  },
  "paths": {
    "reflow_root": "/home/user/dev/reflow",
    "system_root": "/home/user/projects/my_system"
  }
}
```

**After refresh** (reset counter):
```json
{
  "system_name": "my_system",
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "operations_since_refresh": 0,
  "last_refresh_timestamp": "2025-10-24T11:30:00Z",
  "context_metadata": {
    "refresh_triggers_met": ["operation_count_5", "manual_refresh"]
  },
  "paths": {
    "reflow_root": "/home/user/dev/reflow",
    "system_root": "/home/user/projects/my_system"
  }
}
```

---

## Common Degradation Scenarios & Recovery

### Scenario 1: "What system am I working on?"

**Signal**: You're asking about the system name

**Recovery**:
```bash
# Read working_memory.json - system name is there!
cat context/working_memory.json | grep system_name

# If file not found, check pwd
pwd

# Verify you're in the right directory
ls context/  # Should show working_memory.json

# If in wrong directory:
cd /correct/path/to/system
cat context/working_memory.json
```

**Root cause**: Context exhaustion - you forgot what you already knew

**Prevention**: Refresh every 5 operations

---

### Scenario 2: "Where should I create this file?"

**Signal**: Uncertain about file location

**Recovery**:
```bash
# Read current_focus.md - it should tell you
cat context/current_focus.md

# Check workflow instructions
cat {reflow_root}/workflows/{current_workflow}.json

# Verify paths from working_memory.json
cat context/working_memory.json | grep -A 5 "paths"

# All system files go in {system_root}
# All reflow files read from {reflow_root}
```

**Root cause**: Lost track of directory structure

**Prevention**: Execute context refresh

---

### Scenario 3: Working in Wrong Directory

**Signal**: Creating files in wrong system or in reflow directory

**Recovery**:
```bash
# STOP IMMEDIATELY - don't create more files

# Check where you are
pwd

# Where should you be?
cat context/working_memory.json | grep system_root

# Navigate to correct location
cd /path/from/working_memory.json

# Verify
pwd
ls context/  # Should see working_memory.json, current_focus.md, etc.

# Document the error
echo "$(date): Wrong directory error - was in $(pwd), should be in {system_root}" >> context/process_log.md

# Execute full context refresh
# (follow refresh procedure above)
```

**Root cause**: Severe context drift - working in entirely wrong location

**Prevention**: ALWAYS verify pwd before operations

---

## Tips for Preventing Context Issues

### 1. Keep a Physical Checklist
Print this guide and check off items manually - helps you remember

### 2. Set a Timer
After 4-5 operations, your phone/timer reminds you to refresh

### 3. Use Visible Reminders
Put sticky notes on your monitor:
- "Count operations!"
- "Refresh at 5!"
- "Check pwd!"

### 4. Batch Related Operations
Group related work to minimize context window usage:
- Good: Create all service_architecture.json files, then validate all
- Bad: Create one, validate, create another, validate (uses more context)

### 5. Reference Files by Path
Instead of copying large file contents into context:
- ❌ Bad: "Here's the full service_architecture.json: {...2000 lines...}"
- ✅ Good: "See service_architecture.json at specs/machine/service_arch/auth/service_architecture.json"

### 6. Document as You Go
Keep `context/process_log.md` updated with:
- What you did
- What worked
- What didn't work
- Issues encountered

This helps reconstruct context after refresh.

---

## Future: Automated Context Refresh

**When implemented** (see CONTEXT_MANAGEMENT_ADDENDUM.md):
- ✅ Automatic operations counting
- ✅ Auto-trigger refresh at threshold
- ✅ Automatic degradation detection
- ✅ Built-in refresh sequence
- ✅ workflow_driver.py integration

**Commands will be**:
```bash
# Auto-refresh when threshold reached
workflow_driver.py <system> --auto-refresh

# Force refresh manually
workflow_driver.py <system> --refresh

# Check degradation signals
workflow_driver.py <system> --check-degradation
```

**Until then**: Use this manual procedure

---

## Questions?

- **"How do I know which operation count I'm on?"**
  Check `operations_since_refresh` in `context/working_memory.json`

- **"Can I skip the refresh?"**
  Not recommended - context drift causes errors and wasted time

- **"What if I forget to refresh?"**
  Watch for degradation signals - if you notice any, refresh immediately

- **"Do I need to refresh between workflows?"**
  Yes! Transitioning to a new workflow is a good time to refresh

- **"How long does a refresh take?"**
  2-3 minutes - much faster than debugging context drift issues!

---

## See Also

- **CONTEXT_MANAGEMENT_ADDENDUM.md** - Full analysis of missing features
- **NEW_STRUCTURE_README.md** - Overview of new workflow structure
- **workflow_driver.py** - Will eventually automate this

---

*Quick guide for interim manual context management*
*Until automated features are restored*
*Last updated: 2025-10-24*
