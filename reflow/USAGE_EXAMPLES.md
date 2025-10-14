# Reflow Usage Examples

## Example 1: New System Architecture

### Starting Point
You have a new system concept that needs to be architected from scratch.

### Decision Flow Process

1. **Entry Decision (D0)**: "Is this a new concept/system or a change to an existing one?"
   - Answer: **new**
   - Action: Routes to `entry_points.new_concept_or_system`

2. **Prerequisites Check**:
   ```bash
   # Automated validation runs
   python3 ./tools/validate_architecture.py --check-prerequisites
   ```
   - ✅ All tools present in `./tools/`
   - ✅ All templates present in `./templates/`
   - ✅ All definitions present in `./definitions/`
   - ⚠️ Python dependencies need installation

3. **Initial Context Setup**:
   ```bash
   # Creates working directory
   mkdir -p /path/to/systems/<system_name>/
   
   # Initializes tracking files from templates
   cp ./templates/working_memory_template.json systems/<system_name>/working_memory.json
   cp ./templates/current_focus_template.md systems/<system_name>/current_focus.md
   cp ./templates/step_progress_tracker_template.json systems/<system_name>/step_progress_tracker.json
   ```

4. **Route to Architecture**:
   - Goes to `architecture/Arch-01-SetupAndContext.json`
   - Full rigorous architecture workflow begins

## Example 2: Existing System Ready for Development

### Starting Point
Architecture workflow completed, ready to start development.

### Decision Flow Process

1. **Architecture Completion Check (D1)**: "Has architecture workflow been completed?"
   - Evidence required:
     - ✅ `systems/<system_name>/build_ready_index.json` exists
     - ✅ `ARCHITECTURE_CONTEXT_SUMMARY.md` exists
     - ✅ `interfaces/*` ICDs exist
     - ✅ `index.json` with 'components' key exists

2. **Validation Pipeline**:
   ```bash
   # Template validation
   python3 ./tools/validate_architecture.py systems/<system_name>
   # Result: ✅ All service architectures pass template validation
   
   # Graph validation  
   python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-issues
   # Result: ✅ No critical architectural issues detected
   
   # Interface contracts check
   ls systems/<system_name>/interfaces/*.json
   # Result: ✅ All interfaces have complete ICDs
   ```

3. **Quality Gate Validation**:
   - ✅ Architecture completion gate passed
   - ✅ All handoff artifacts present
   - ✅ Operational mission artifacts exist

4. **Route to Development**:
   - Goes to `development/Dev-01-InitBootstrap.json`
   - Development workflow begins with confidence

## Example 3: Feature Update During Development

### Starting Point
During development, a cross-service interface change is needed.

### Decision Flow Process

1. **Development Change Check (D2)**: "Is a cross-service/contract change required?"
   - Signals detected:
     - 🔴 New interface needed
     - 🔴 Breaking API change required

2. **Impact Analysis**:
   ```bash
   # Analyze current interfaces
   python3 ./tools/system_of_systems_graph.py systems/<system_name>/index.json --analyze-dependencies
   
   # Check interface registry
   cat systems/<system_name>/interface_registry.json
   ```

3. **Update Process**:
   - Update affected `service_architecture.json` files
   - Regenerate `interface_registry.json`
   - Update ICDs
   - Re-validate architecture

4. **Re-validation**:
   ```bash
   # Validate changes
   python3 ./tools/validate_architecture.py systems/<system_name>
   python3 ./tools/generate_interface_contracts.py systems/<system_name>
   ```

5. **Route to Feature Update**:
   - Goes to `feature_update/FU-02-ArchReengineering.json`
   - Handles architecture changes systematically

## Context Management Examples

### Automatic Context Refresh
```bash
# After 4 operations or 12 minutes, context refresh triggers
# Automatically:
# 1. Saves current state
# 2. Reloads definitions and templates  
# 3. Confirms current position
# 4. Resumes with refreshed context
```

### Degradation Detection
```bash
# System detects degradation signals:
# - Working in wrong directory
# - Forgetting current step
# - Using wrong template format
# Triggers immediate context refresh and correction
```

### Progress Tracking
```bash
# Current focus always shows:
cat systems/<system_name>/current_focus.md
```
```markdown
# Current Focus

**System Name:** my_system
**Current Step:** 2 - Service Decomposition
**Current Substep:** 2.3 - Create service architectures
**Last Updated:** 2025-10-14 15:30:00

## Current Task
Creating service_architecture.json for authentication_service

## Next Action
Apply template validation and continue with next service

## Progress Summary
- **Services Created:** 3/8
- **Interfaces Deduced:** 12 total
- **Validation Status:** PENDING
- **Critical Issues:** None
```

## Quality Gate Examples

### Architecture Completion Gate
```bash
# Required before development handoff:
✅ build_ready_index.json - Complete technical specs
✅ SYSTEM_MISSION_STATEMENT.md - Why system exists
✅ USER_SCENARIOS.md - Concrete user workflows  
✅ SUCCESS_CRITERIA.md - Measurable success metrics
✅ All validation tools pass
✅ All interfaces have ICDs
```

### Validation Tools Pass
```bash
# Template validation
python3 ./tools/validate_architecture.py systems/my_system
# Output: ✅ All 8 service architectures pass validation

# Graph validation
python3 ./tools/system_of_systems_graph.py systems/my_system/index.json --analyze-issues
# Output: ✅ No critical issues, 2 recommendations

# Interface validation  
python3 ./tools/generate_interface_contracts.py systems/my_system
# Output: ✅ Generated 12 complete ICDs
```

This enhanced decision flow provides the same rigor as the original architecture workflow while offering better modularity, clearer decision points, and comprehensive validation at every step.