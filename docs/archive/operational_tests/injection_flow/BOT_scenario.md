# Basic Operational Test (BOT) - Injection Flow

## Test Scenario: Standalone System Creation and Handoff

### Objective
Take the existing `dnd_reflow` system, inject complete reflow capabilities into it, export to a new repository, and verify a recipient can use it without any external reflow installation.

### Test Requirements
Use the `inject_flow.json` workflow to:
1. **Inject** complete reflow toolchain into `dnd_reflow` system's context folder
2. **Export** the system to a new GitHub repository 
3. **Verify** a fresh user can clone and use the embedded reflow environment
4. **Validate** all reflow functionality works in standalone mode

### Success Criteria

✅ **Injection Phase Complete**:
- `inject_flow.json` workflow executes without manual fixes
- All reflow tools, templates, workflows embedded in `dnd_reflow/context/`
- Original context files safely migrated to `context/tracking/`
- Embedded scripts (`context/bin/reflow`, `context/bin/validate`) functional

✅ **Export Phase Complete**:
- System exported to new GitHub repository successfully
- Repository contains complete embedded reflow environment
- No external reflow dependencies in exported system
- Documentation clear for recipients

✅ **Standalone Verification Complete**:
- Fresh clone works in environment without reflow installation
- Embedded workflows execute correctly (`./context/bin/reflow`)
- Embedded tools functional (`./context/bin/validate all`)
- New user can continue development using embedded environment

✅ **User Experience**:
- Process completed using only `inject_flow.json` documentation
- No manual fixes or workarounds required
- Clear path from injection to standalone repository

### Failure Criteria

❌ **Injection Failures**:
- Injection process fails or requires manual intervention
- Embedded tools don't work in target system
- Original system functionality broken by injection
- Context files corrupted or lost during injection

❌ **Export Failures**:
- Export to GitHub fails or incomplete
- Exported system missing critical embedded components
- External reflow dependencies still present
- Documentation unclear or missing

❌ **Standalone Failures**:
- Fresh clone doesn't work without external reflow
- Embedded environment non-functional
- New user cannot use embedded tools/workflows
- Critical functionality missing from embedded environment

### Test Execution Steps

#### Phase 1: Pre-Injection Setup (30 minutes expected)
1. **Verify dnd_reflow status**: Ensure it's in a clean, working state
2. **Document baseline**: Record current dnd_reflow structure and functionality
3. **Prepare clean test environment**: Fresh directory/workspace for testing

**Expected Evidence**:
- dnd_reflow system documented and verified functional
- Clean workspace prepared for injection testing

#### Phase 2: Injection Execution (1-2 hours expected)
1. **Load behavioral rules**: Follow `instructions/1-behavioral-rules.json`
2. **Execute injection**: Run `python3 tools/execute_injection_flow.py <dnd_reflow_path>`
3. **Validate injection**: Verify all components embedded correctly
4. **Test embedded environment**: Run `./context/bin/validate all` in target system

**Expected Evidence**:
- Injection completes without errors
- `dnd_reflow/context/` contains complete reflow environment:
  - `context/workflows/` (decision_flow.json + all workflow files)
  - `context/tools/` (all Python tools with embedded mode detection)
  - `context/templates/` (all reflow templates)
  - `context/definitions/` (architectural definitions)
  - `context/tracking/` (original context files migrated here)
  - `context/bin/` (executable wrapper scripts)
  - `context/config/` (embedded configuration)
- Embedded validation passes: `./context/bin/validate all` succeeds

#### Phase 3: Export and Repository Creation (1 hour expected)
1. **Export system**: Push injected system to new GitHub repository
2. **Verify export completeness**: Check all embedded components included
3. **Test repository**: Clone fresh copy to verify completeness
4. **Document for recipients**: Ensure clear usage instructions

**Expected Evidence**:
- New GitHub repository created with injected system
- Repository contains complete embedded reflow environment
- Fresh clone includes all necessary components
- `context/README_EMBEDDED.md` provides clear instructions

#### Phase 4: Standalone Verification (2-3 hours expected)
1. **Fresh environment setup**: New machine/container without reflow installed
2. **Clone and test**: Clone repository and test embedded environment
3. **Workflow execution**: Execute embedded reflow workflows
4. **Development continuation**: Verify ability to continue system development

**Expected Evidence**:
- System clones and works without external reflow installation
- `./context/bin/reflow` lists and can access embedded workflows
- `./context/bin/validate all` runs successfully using embedded tools
- `./context/bin/setup-dev` provides working development environment
- Can continue development using embedded reflow capabilities

### Documentation Requirements

Document every step, including:
- **Injection process**: Every step, time taken, issues encountered
- **Embedded functionality**: What works, what doesn't, performance impact
- **Export process**: GitHub integration, repository completeness
- **Standalone verification**: Fresh user experience, pain points
- **Overall assessment**: Success/failure with detailed reasoning

### Pass/Fail Decision

**PASS**: Complete standalone system with embedded reflow that works identically to external reflow installation, achieved through `inject_flow.json` workflow without manual intervention.

**FAIL**: Injection fails, exported system missing functionality, or recipient requires external reflow installation.

### Current System Assessment

**inject_flow.json Status**: Claims to create standalone systems but never tested with actual system handoff to verify independence from external reflow.

**dnd_reflow Target**: Existing system claiming "production ready" - perfect test subject for injection and standalone verification.

### Test Execution Plan

**Test Date**: TBD
**Primary Tester**: User (ajs7)
**Secondary Verification**: External user without reflow installation
**Status**: Ready to execute

### Success Measurement

This BOT will definitively answer:
- Does `inject_flow.json` actually create standalone systems?
- Can recipients use injected systems without external reflow?
- Is the injection process reliable and user-friendly?
- Do embedded environments provide full reflow functionality?

**Only after this BOT passes should inject_flow.json claim to create "standalone" or "self-contained" systems.**