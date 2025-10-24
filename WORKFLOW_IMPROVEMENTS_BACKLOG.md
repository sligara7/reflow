# Workflow Improvements Backlog

This document tracks potential improvements to the reflow workflow system identified during implementation on real projects.

**Status**: PHASE 1 & 2 COMPLETED - 5 of 13 improvements implemented
**Last Updated**: 2025-10-24
**Source**: dnd_reflow system implementation

## Implementation Summary

**Completed (5/13)**:
- ✅ Automatic Progress Detection
- ✅ Validation Integration with Quality Gates
- ✅ Service-Level Progress Tracking
- ✅ Docker Compose Integration Testing
- ✅ Test Coverage Quality Gates

**Implementation Details**:
- Files Modified: decision_flow.json, Dev-02-CoreAndDomain.json, Dev-05-ObservabilityAndTesting.json, workflow_driver.py
- New Features: --auto-detect-progress, --quality-gates, --dry-run flags
- Documentation: quality_gates_and_validation section in decision_flow.json

**Remaining (8/13)**: See Phase 3 and Phase 4 below

## High Priority Improvements

### 1. Automatic Progress Detection
**Problem**: Manual marking of completed actions is error-prone and easily forgotten
**Impact**: Progress tracker becomes out of sync with actual state
**Effort**: Medium (2-3 days)
**Value**: High

**Current State**:
```bash
# Manual marking required
python3 workflow_driver.py dnd_reflow --mark-done D2.1
```

**Proposed Solution**:
```python
# tools/detect_progress.py
def detect_dev02_completion(service_path: Path) -> Dict[str, bool]:
    """
    Automatically detect which Dev-02 actions are complete by scanning code.

    Returns: Dict of action_id -> completion status
    """
    checks = {
        'D2.1': check_directory_skeleton(service_path),
        'D2.2': check_models_exist(service_path),
        'D2.3': check_routers_exist(service_path),
        'D2.4': check_config_loader(service_path),
        'D2.5': check_di_setup(service_path),
        'D2.6': check_lint_pass(service_path)
    }
    return checks

def check_models_exist(service_path: Path) -> bool:
    """Check if data models are implemented."""
    models_path = service_path / 'src/models'
    if not models_path.exists():
        return False

    # Check for Python files (not just __init__.py)
    model_files = [f for f in models_path.glob('*.py') if f.name != '__init__.py']
    return len(model_files) > 0

def check_routers_exist(service_path: Path) -> bool:
    """Check if API routers are implemented."""
    routers_path = service_path / 'src/routers'
    if not routers_path.exists():
        return False

    # Check for router files
    router_files = [f for f in routers_path.glob('*.py') if f.name != '__init__.py']
    return len(router_files) > 0

def check_fastapi_app(service_path: Path) -> bool:
    """Check if FastAPI app is initialized."""
    main_py = service_path / 'src/main.py'
    if not main_py.exists():
        return False

    content = main_py.read_text()
    return 'FastAPI' in content and 'app = FastAPI' in content
```

**Integration**:
```bash
# Auto-detect and update progress
python3 workflow_driver.py dnd_reflow --auto-detect-progress

# Show what would be detected
python3 workflow_driver.py dnd_reflow --auto-detect-progress --dry-run
```

**Benefits**:
- No manual tracking needed
- Progress always accurate
- Can detect regressions (code deleted)
- Faster workflow execution

---

### 2. Service-Level Progress Tracking
**Problem**: Single progress tracker doesn't reflect per-service development status
**Impact**: Can't tell which services are ahead/behind
**Effort**: Medium (2-3 days)
**Value**: High

**Current State**:
```json
// dev_progress_tracker.json - system-wide only
{
  "current_stage": "ARCHITECTURE_COMPLETED",
  "active_service": "Ready for development workflow"
}
```

**Proposed Solution**:
```json
// services/character_service/.progress.json
{
  "service_name": "character_service",
  "dev_stage": "Dev-04",  // Ahead of system-wide stage
  "completed_stages": ["Dev-01", "Dev-02", "Dev-03"],
  "current_actions": {
    "D4.1": "completed",
    "D4.2": "in_progress",
    "D4.3": "pending"
  },
  "validation_status": "PASSED",
  "blockers": [],
  "metrics": {
    "test_coverage": 87.5,
    "endpoints_implemented": 15,
    "endpoints_total": 18
  }
}
```

**Workflow Driver Integration**:
```bash
# Show system-wide progress
python3 workflow_driver.py dnd_reflow --status

# Show per-service progress
python3 workflow_driver.py dnd_reflow --service character_service --status

# Advance specific service
python3 workflow_driver.py dnd_reflow --service session_service --next

# Show services that are blocked
python3 workflow_driver.py dnd_reflow --show-blockers
```

**Benefits**:
- Parallel development supported
- Can have services at different stages
- Identify lagging services
- Better resource allocation

---

### 3. Validation Integration with Quality Gates
**Problem**: Validation results aren't blocking - agents can proceed with errors
**Impact**: Accumulation of technical debt, downstream failures
**Effort**: Low (1 day)
**Value**: High

**Current State**:
```bash
# Validation can fail but doesn't block advancement
python3 tools/validate_architecture.py systems/dnd_reflow
# (shows errors but workflow can continue)
```

**Proposed Solution**:
```python
# In workflow_driver.py
def enforce_validation_gate(step_id: str) -> Dict[str, Any]:
    """Run validation and BLOCK if it fails."""

    validation_result = run_validation_tools(step_id)

    if not validation_result['passed']:
        return {
            "can_proceed": False,
            "blocking": True,
            "reason": "VALIDATION_FAILED",
            "issues": validation_result['issues'],
            "fix_suggestions": generate_fix_suggestions(validation_result)
        }

    return {"can_proceed": True}
```

**Example Blocking**:
```bash
$ python3 workflow_driver.py dnd_reflow --next

✗✗✗ VALIDATION GATE FAILED ✗✗✗

Cannot proceed to next step. Fix these issues first:

INTERFACE CONSISTENCY (14 issues):
  1. session_service.create_session - interface incomplete
     Fix: Add endpoint definition, request/response schemas

  2. session_service.get_session - interface incomplete
     Fix: Add endpoint definition, request/response schemas

Run: python3 workflow_driver.py dnd_reflow --validate
to check again after fixes.
```

**Benefits**:
- Prevent proceeding with broken architecture
- Clear error messages with fix suggestions
- Force best practices
- Reduce debugging time

---

### 4. Docker Compose Integration Testing
**Problem**: No verification that services actually start and run
**Impact**: "Works on my machine" problems not caught until deployment
**Effort**: Low (1 day)
**Value**: Medium

**Current State**:
- Code written but never tested running
- Manual docker-compose testing

**Proposed Solution**:
```python
# In Dev-02 validation
def validate_services_runnable(system_path: Path) -> Dict[str, Any]:
    """
    Verify all services can start successfully.

    This is a critical validation that code isn't just written but actually works.
    """

    # Build and start services
    result = subprocess.run(
        ['docker-compose', 'up', '--build', '-d'],
        cwd=system_path,
        capture_output=True,
        timeout=300  # 5 minutes max
    )

    if result.returncode != 0:
        return {
            "passed": False,
            "reason": "Services failed to start",
            "error": result.stderr.decode()
        }

    # Check all services are running
    time.sleep(10)  # Wait for startup
    ps_result = subprocess.run(
        ['docker-compose', 'ps'],
        cwd=system_path,
        capture_output=True
    )

    # Parse output and check for "running" status
    services_status = parse_docker_ps(ps_result.stdout.decode())

    failed_services = [s for s, status in services_status.items() if status != 'running']

    if failed_services:
        # Get logs for failed services
        logs = get_service_logs(system_path, failed_services)

        return {
            "passed": False,
            "reason": f"{len(failed_services)} services failed to start",
            "failed_services": failed_services,
            "logs": logs
        }

    # Cleanup
    subprocess.run(['docker-compose', 'down'], cwd=system_path)

    return {
        "passed": True,
        "services_tested": len(services_status)
    }
```

**Integration**:
```bash
# Added to Dev-02 validation
python3 workflow_driver.py dnd_reflow --validate
# Now includes:
# - Architecture validation
# - Interface consistency
# - Docker compose build/start test ← NEW
```

**Benefits**:
- Catch import errors, dependency issues early
- Verify Docker configuration works
- Ensure services can communicate
- Confidence before deployment

---

### 5. Test Coverage Quality Gate
**Problem**: No enforcement of testing standards
**Impact**: Untested code shipped to production
**Effort**: Medium (2 days)
**Value**: High

**Current State**:
- Tests optional
- No coverage requirements
- No validation of test quality

**Proposed Solution**:
```python
# In Dev-05 validation (ObservabilityAndTesting)
def validate_test_coverage(service_path: Path) -> Dict[str, Any]:
    """
    Enforce minimum test coverage standards.

    Requirements:
    - Overall coverage >= 60%
    - Domain logic coverage >= 80%
    - All public endpoints have at least one test
    - Critical paths fully tested
    """

    # Run pytest with coverage
    result = subprocess.run(
        ['pytest', '--cov=src', '--cov-report=json'],
        cwd=service_path,
        capture_output=True
    )

    if result.returncode != 0:
        return {
            "passed": False,
            "reason": "Tests failed to run",
            "error": result.stderr.decode()
        }

    # Load coverage report
    coverage_file = service_path / 'coverage.json'
    with open(coverage_file) as f:
        coverage_data = json.load(f)

    total_coverage = coverage_data['totals']['percent_covered']

    # Check per-module coverage
    domain_modules = [k for k in coverage_data['files'].keys() if '/services/' in k]
    domain_coverage = sum(coverage_data['files'][m]['percent_covered']
                         for m in domain_modules) / len(domain_modules) if domain_modules else 0

    # Check endpoint coverage
    router_files = [k for k in coverage_data['files'].keys() if '/routers/' in k]
    uncovered_endpoints = find_uncovered_endpoints(service_path, router_files, coverage_data)

    issues = []

    if total_coverage < 60:
        issues.append({
            "severity": "ERROR",
            "message": f"Overall coverage {total_coverage:.1f}% < 60% minimum",
            "suggestion": "Add tests for untested modules"
        })

    if domain_coverage < 80:
        issues.append({
            "severity": "WARNING",
            "message": f"Domain logic coverage {domain_coverage:.1f}% < 80% target",
            "suggestion": "Focus tests on business logic"
        })

    if uncovered_endpoints:
        issues.append({
            "severity": "ERROR",
            "message": f"{len(uncovered_endpoints)} endpoints have no tests",
            "endpoints": uncovered_endpoints,
            "suggestion": "Add integration tests for all endpoints"
        })

    return {
        "passed": len([i for i in issues if i['severity'] == 'ERROR']) == 0,
        "total_coverage": total_coverage,
        "domain_coverage": domain_coverage,
        "issues": issues
    }
```

**Integration**:
```bash
$ python3 workflow_driver.py dnd_reflow --validate

Running: Test Coverage Validation
✗ Test Coverage FAILED

ERRORS:
  - Overall coverage 42.3% < 60% minimum
  - 8 endpoints have no tests:
    * POST /api/v2/characters
    * GET /api/v2/characters/{id}
    * POST /api/v2/characters/{id}/retheme
    ...

Fix these issues before proceeding to Dev-06.
```

**Benefits**:
- Enforce quality standards
- Prevent shipping untested code
- Guide developers on what to test
- Improve system reliability

---

## Medium Priority Improvements

### 6. Incremental Validation (Watch Mode)
**Problem**: Validation only runs manually at step boundaries
**Impact**: Late discovery of issues
**Effort**: Medium (2-3 days)
**Value**: Medium

**Proposed Solution**:
```bash
# Watch mode - validate on file changes
python3 workflow_driver.py dnd_reflow --watch

# Output:
Watching: /home/ajs7/project/dnd_reflow/services/**/*.py
         /home/ajs7/project/dnd_reflow/interfaces/**/*.json

[14:23:45] File changed: services/session_service/src/main.py
[14:23:45] Running validation...
[14:23:46] ✓ Architecture validation PASSED
[14:23:47] ✗ Interface consistency FAILED (1 new issue)
           - session_service.create_session endpoint added but not in registry
[14:23:47] Suggestion: Run tools/generate_interface_contracts.py to sync
```

**Benefits**:
- Real-time feedback
- Catch errors immediately
- Faster development loop
- Less context switching

---

### 7. Rollback Support
**Problem**: No way to rollback if advanced too early
**Impact**: Stuck in wrong state, manual file editing needed
**Effort**: Low (1 day)
**Value**: Medium

**Proposed Solution**:
```bash
# Rollback to previous step
python3 workflow_driver.py dnd_reflow --rollback

# Rollback to specific step
python3 workflow_driver.py dnd_reflow --rollback-to Dev-02

# Show rollback history
python3 workflow_driver.py dnd_reflow --rollback-history
```

**Implementation**:
```python
def create_checkpoint(workflow_state: WorkflowState):
    """Create checkpoint before advancing."""
    checkpoint = {
        "step": workflow_state.current_step,
        "timestamp": datetime.utcnow(),
        "files": snapshot_tracking_files(workflow_state)
    }
    save_checkpoint(checkpoint)

def rollback_to_checkpoint(checkpoint_id: str):
    """Restore state from checkpoint."""
    checkpoint = load_checkpoint(checkpoint_id)
    restore_tracking_files(checkpoint['files'])
    print(f"Rolled back to {checkpoint['step']} at {checkpoint['timestamp']}")
```

---

### 8. Multi-Service Parallel Development
**Problem**: Workflow assumes single-threaded service development
**Impact**: Can't work on multiple services simultaneously
**Effort**: High (5-7 days)
**Value**: Medium

**Proposed Solution**:
```bash
# Work on specific service
python3 workflow_driver.py dnd_reflow --service session_service --show

# Mark action complete for specific service
python3 workflow_driver.py dnd_reflow --service session_service --mark-done D2.1

# Show all services status
python3 workflow_driver.py dnd_reflow --services-matrix

# Output:
Service Progress Matrix:
┌──────────────────────┬────────┬─────────┬──────────┬─────────┐
│ Service              │ Stage  │ Actions │ Coverage │ Status  │
├──────────────────────┼────────┼─────────┼──────────┼─────────┤
│ character_service    │ Dev-04 │ 9/9     │ 87%      │ ✓       │
│ game_rules_service   │ Dev-03 │ 7/9     │ 65%      │ ⚠       │
│ session_service      │ Dev-02 │ 2/9     │ 0%       │ ○       │
│ llm_service          │ Dev-03 │ 6/9     │ 45%      │ ⚠       │
└──────────────────────┴────────┴─────────┴──────────┴─────────┘
```

---

### 9. Integration with Git Hooks
**Problem**: Can commit code that fails validation
**Impact**: Broken code in repository
**Effort**: Low (1 day)
**Value**: Medium

**Proposed Solution**:
```bash
# .git/hooks/pre-commit
#!/bin/bash

# Run validation before allowing commit
python3 workflow_driver.py $(basename $(pwd)) --validate --quiet

if [ $? -ne 0 ]; then
    echo "❌ Validation failed. Fix issues before committing."
    echo "Run: python3 workflow_driver.py $(basename $(pwd)) --validate"
    exit 1
fi

echo "✓ Validation passed"
```

---

### 10. Metrics Dashboard
**Problem**: No visibility into workflow efficiency
**Impact**: Can't improve what you don't measure
**Effort**: Medium (3-4 days)
**Value**: Low

**Proposed Solution**:
```bash
# Generate metrics report
python3 workflow_driver.py dnd_reflow --metrics

# Output:
Workflow Metrics Report - dnd_reflow
=====================================

Progress:
  Current Step: Dev-02
  Completion: 35% (9/25 total actions)
  Services: 2/9 complete (22%)

Efficiency:
  Average time per action: 2.3 hours
  Validation failure rate: 15%
  Context refreshes needed: 8
  Operations per refresh: 3.2 avg

Quality:
  Test coverage: 58% avg
  Validation pass rate: 85%
  Interface consistency: 93%

Bottlenecks:
  Slowest step: Dev-02 (8.5 hours)
  Most errors: D2.3 (interface adapters, 6 attempts)

Recommendations:
  - Add examples for D2.3 to reduce errors
  - Consider breaking Dev-02 into smaller steps
  - Automate interface contract generation
```

---

## Low Priority / Future Enhancements

### 11. LLM-Assisted Fix Suggestions
**Problem**: Error messages don't provide concrete fixes
**Effort**: High
**Value**: Low (nice-to-have)

Use LLM to analyze validation errors and suggest specific code changes.

### 12. Template Customization
**Problem**: One-size-fits-all templates
**Effort**: Medium
**Value**: Low

Allow per-system customization of step templates.

### 13. Workflow Visualization
**Problem**: Hard to see overall progress
**Effort**: Medium
**Value**: Low

Generate visual workflow diagrams showing current position.

---

## Implementation Priority

### Phase 1 (Immediate - This Week) - ✅ COMPLETED 2025-10-24
1. ✅ **IMPLEMENTED** - Automatic Progress Detection (HIGH value, MEDIUM effort)
   - Added auto-detection functionality to workflow_driver.py
   - Implemented in Dev-02-CoreAndDomain.json quality gates
   - Command: `python3 workflow_driver.py <system> --auto-detect-progress`

2. ✅ **IMPLEMENTED** - Validation Integration (HIGH value, LOW effort)
   - Added quality_gates_and_validation section to decision_flow.json
   - Integrated blocking validation gates in Dev-02 and Dev-05
   - Command: `python3 workflow_driver.py <system> --quality-gates`

### Phase 2 (Short-term - Next 2 Weeks) - ✅ COMPLETED 2025-10-24
3. ✅ **IMPLEMENTED** - Service-Level Progress Tracking (HIGH value, MEDIUM effort)
   - Added service_level_progress_tracking schema to decision_flow.json
   - File location: services/<service_name>/.progress.json
   - Supports parallel development at different stages

4. ✅ **IMPLEMENTED** - Docker Compose Integration (MEDIUM value, LOW effort)
   - Added docker_compose_integration quality gate to Dev-02
   - Validates services can start successfully in containers
   - Prevents "works on my machine" problems

5. ✅ **IMPLEMENTED** - Test Coverage Gates (HIGH value, MEDIUM effort)
   - Added test_coverage quality gate to Dev-05
   - Enforces 60% overall, 80% domain logic, 100% critical paths
   - Blocks advancement if coverage requirements not met

### Phase 3 (Medium-term - Next Month)
6. Incremental Validation (MEDIUM value, MEDIUM effort)
7. Rollback Support (MEDIUM value, LOW effort)
8. Git Hooks Integration (MEDIUM value, LOW effort)

### Phase 4 (Long-term - Future)
9. Multi-Service Parallel Development (MEDIUM value, HIGH effort)
10. Metrics Dashboard (LOW value, MEDIUM effort)

---

## Tracking

- **Total Improvements**: 13
- **High Priority**: 5
- **Medium Priority**: 5
- **Low Priority**: 3
- **Estimated Total Effort**: ~30 days
- **Estimated Total Value**: High

## Notes

These improvements were identified during actual implementation on the dnd_reflow system. They represent real pain points and opportunities for automation.

Each improvement should be:
1. Designed in detail
2. Prototyped on test system
3. Validated with real usage
4. Documented thoroughly
5. Integrated into workflow_driver.py
6. Tested across multiple systems

The goal is a workflow system that:
- ✓ Enforces best practices automatically
- ✓ Catches errors early
- ✓ Provides clear guidance
- ✓ Tracks progress accurately
- ✓ Supports parallel development
- ✓ Improves continuously
