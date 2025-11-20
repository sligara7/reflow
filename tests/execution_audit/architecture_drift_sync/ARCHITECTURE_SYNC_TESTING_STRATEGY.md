# Architecture Synchronization Testing Strategy

**Version**: 1.0.0
**Created**: 2025-11-19
**Purpose**: Comprehensive strategy for testing Reflow's architecture drift detection and synchronization capabilities

---

## Executive Summary

Architecture drift is a **CRITICAL real-world problem** where implementations diverge from designed architectures during development and testing. This causes:
- Stale documentation
- Misalignment between design and implementation
- Integration failures
- Maintenance nightmares
- Loss of architectural intent

**TC-002 (architecture_drift_sync)** validates that Reflow prevents and resolves architecture drift through a **two-layer defense**:
1. **Proactive Prevention**: Service Interface Contracts (v3.17.0) warn LLMs BEFORE making breaking changes
2. **Reactive Synchronization**: D-06.5 Architecture Synchronization Loop (v3.15.0) detects and resolves drift AFTER it occurs

---

## The Architecture Drift Problem

### Real-World Scenario

**Phase 1: Architecture Design**
- Architect designs e-commerce system: 5 functions, 2 services, 1 interface
- Documentation created: `functional_architecture.json`, `service_architecture.json`, `interface_registry.json`

**Phase 2: Development**
- Developer implements services per design
- All good so far ✅

**Phase 3: Testing & Reality Strikes**
- Integration tests reveal gaps:
  - Order cancellation doesn't refund payment (missing RefundPayment function)
  - Order status doesn't include payment info (missing interface)
  - Concurrent orders cause race conditions (missing ValidateOrderUniqueness function)

**Phase 4: Quick Fixes (THE PROBLEM)**
- Developer adds 3 new functions + 1 new interface to make tests pass
- **Architecture documents NOT updated** (too busy, forgot, manual process, etc.)
- Implementation now has 8 functions (was 5), 2 interfaces (was 1)
- **DRIFT**: Architecture documents lie about reality

**Phase 5: Consequences**
- New developer onboards using stale architecture docs → confusion
- Integration with other services fails → unexpected dependencies
- Deployment issues → architecture doesn't match running system
- Technical debt accumulates → "the code is the documentation"

---

## Reflow's Two-Layer Defense

### Layer 1: Proactive Prevention (Service Contracts - v3.17.0)

**Mechanism**: Embedded architectural "hooks" in each service directory

**File**: `services/{service_name}/SERVICE_CONTRACT.json`

**Structure**:
```json
{
  "service_name": "OrderService",
  "contracted_functions": {
    "functions": ["CreateOrder", "GetOrderStatus", "CancelOrder"],
    "warning": "⚠️ WARNING: This service has 3 contracted functions. DO NOT modify without updating functional_architecture.json"
  },
  "contracted_interfaces": {
    "provides": [],
    "consumes": ["payment_processing"],
    "warning": "⚠️ WARNING: Interface changes are BREAKING changes. Affects PaymentService (1 consumer)."
  },
  "architecture_source_of_truth": "../specs/machine/service_arch/OrderService/service_architecture.json",
  "llm_warnings": {
    "before_modifying_functions": "⚠️ Before adding/removing/renaming functions, UPDATE functional_architecture.json",
    "before_modifying_interfaces": "⚠️ Before changing interfaces, VERIFY impact on consumer services and UPDATE interface_registry.json"
  }
}
```

**How It Works**:
1. Contracts generated at **D-02-A05** (after domain model implementation)
2. LLM sees contract when modifying service code
3. Explicit warnings alert LLM to architectural impact
4. LLM should update architecture BEFORE making breaking changes

**Validation Points**:
- D-04-A06.5: Validate contracts after integration surfaces
- D-06-A02.5: Validate contracts against as-built architecture
- D-06.5-A04.5: Regenerate contracts when architecture changes
- D-07-A07.5: Final pre-deployment contract validation

**Strength**: **Proactive** - prevents drift before it happens
**Weakness**: Relies on LLM compliance (can be ignored)

---

### Layer 2: Reactive Synchronization (D-06.5 Loop - v3.15.0)

**Mechanism**: Systematic iterative loop that detects drift and updates architecture

**Trigger**: D-06 as-built comparison shows similarity < 0.95

**Workflow Steps**:
```
D-06: As-Built Comparison
  ↓ Run compare_architectures.py
  ↓ Calculate similarity score
  ↓ IF similarity < 0.95 → TRIGGER D-06.5

D-06.5: Architecture Synchronization Loop
  ↓
  D-06.5-A01: Classify Root Causes
    - operational_reality: Discovered during testing
    - requirements_creep: Incomplete initial requirements
    - technical_constraints: Performance, security, concurrency issues
    - performance_optimization: Scale/latency improvements
    - security_hardening: Threat model changes
    - developer_mistake: Implementation errors

  D-06.5-A02: Update Functional Architecture
    - Add new functions
    - Update dependencies
    - Update flows

  D-06.5-A03: Update Service Architecture
    - Allocate new functions to services
    - Add new interfaces
    - Update interface_registry.json

  D-06.5-A04: Version Architectures
    - Use version_architecture.py tool (NOT manual)
    - Semantic versioning (1.0.0 → 1.1.0)
    - Document root causes in version_history.json
    - Include rationale for WHY changes were made

  D-06.5-A04.5: Regenerate Service Contracts
    - Update SERVICE_CONTRACT.json for affected services
    - Reflect new functions/interfaces in contracts

  D-06.5-A05: Re-Validate Similarity
    - Run comparison again
    - Calculate new similarity score
    - IF similarity >= 0.95 → EXIT loop

  D-06.5-A06: Iterate If Needed
    - IF similarity < 0.95 → GOTO D-06.5-A02
    - ELSE → PROCEED to D-07
```

**Enforcement Gates**:
- **D-06.5 Entry**: MANDATORY when similarity < 0.7, RECOMMENDED when < 0.95
- **D-Post-A02**: BLOCKING gate - requires similarity >= 0.95 before deployment

**Strength**: **Automatic detection** - catches drift even if LLM ignores contracts
**Weakness**: Reactive - drift already happened (but gets fixed)

---

## TC-002: Testing Strategy

### Test Scenario Design

**Objective**: Validate BOTH layers work together

**Approach**: Controlled drift injection through realistic test failures

**6-Phase Test**:

1. **Phase 1: Baseline Architecture**
   - Design simple e-commerce system
   - 5 functions, 2 services, 1 interface
   - Architecture documents created (v1.0.0)

2. **Phase 2: Clean Implementation**
   - Implement services per design
   - Generate service contracts (D-02-A05)
   - No drift yet

3. **Phase 3: Drift Injection**
   - Run integration tests
   - Inject 3 test failures (test_failures.json):
     - TEST-001: Order cancellation doesn't refund payment
     - TEST-002: Order status missing payment info
     - TEST-003: Concurrent orders cause race conditions
   - Agent B implements fixes (adds 3 functions + 1 interface)
   - **DRIFT CREATED**: Implementation ≠ Architecture

4. **Phase 4: Drift Detection**
   - Agent B runs D-06 as-built comparison
   - **CRITICAL CHECKPOINT**: Does Agent B detect similarity < 0.95?
   - **CRITICAL CHECKPOINT**: Does Agent B trigger D-06.5 (or skip to D-07)?

5. **Phase 5: Synchronization Loop**
   - Agent B executes D-06.5 workflow
   - Classifies root causes (3 changes)
   - Updates functional architecture (v1.1.0)
   - Updates service architectures (OrderService, PaymentService)
   - Uses version_architecture.py (not manual)
   - **CRITICAL CHECKPOINT**: Regenerates service contracts (D-06.5-A04.5)
   - Re-validates similarity
   - Iterates until similarity >= 0.95

6. **Phase 6: Final Validation**
   - Agent B runs D-Post-A02 gate
   - Verifies similarity >= 0.95
   - **PASS** → Architecture synchronized

---

## Validation Checkpoints (Agent A's Job)

### 10 Critical Checkpoints

**Checkpoint 1: Drift Detection (D-06)**
- ✅ Did Agent B run comparison at D-06?
- ✅ Did Agent B calculate similarity correctly?
- ✅ Did Agent B identify similarity < 0.95?
- ❌ Did Agent B skip to D-07 without detecting drift?

**Checkpoint 2: Synchronization Triggered**
- ✅ Did Agent B trigger D-06.5 workflow?
- ✅ Was it automatic or did Agent B need prompting?
- ❌ Did Agent B skip D-06.5 entirely?

**Checkpoint 3: Root Cause Classification**
- ✅ Did Agent B classify all 3 drift changes?
- ✅ Were categories appropriate?
- ✅ Was rationale specific (not generic)?

**Checkpoint 4: Functional Architecture Updated**
- ✅ Was functional_architecture.json updated to v1.1.0?
- ✅ Were all 3 new functions added?
- ✅ Were dependencies updated?

**Checkpoint 5: Service Architecture Updated**
- ✅ Were both service architectures updated (OrderService, PaymentService)?
- ✅ Were new functions allocated correctly?
- ✅ Was interface_registry.json updated?
- ✅ Are versions consistent across files?

**Checkpoint 6: Versioning Applied**
- ✅ Was version_architecture.py tool used?
- ✅ Is version history complete?
- ✅ Are root causes documented?
- ✅ Is semantic versioning correct (1.0.0 → 1.1.0)?
- ❌ Was versioning manual (without tool)?

**Checkpoint 7: Re-Validation & Iteration**
- ✅ Did Agent B re-calculate similarity?
- ✅ What was final similarity score?
- ✅ How many iterations?
- ✅ Did Agent B proceed only after >= 0.95?

**Checkpoint 8: Final Quality Gate**
- ✅ Was D-Post-A02 gate executed?
- ✅ Did gate pass?
- ✅ Is architecture fully synchronized?

**Checkpoint 9: Service Contracts Generated** (NEW)
- ✅ Were contracts generated at D-02-A05?
- ✅ Are contracts in services/*/SERVICE_CONTRACT.json?
- ✅ Do contracts reflect initial architecture?

**Checkpoint 10: Service Contracts Validated** (NEW)
- ✅ Were contracts validated at D-04-A06.5, D-06-A02.5?
- ✅ Were contracts regenerated at D-06.5-A04.5?
- ✅ Do contracts reflect updated architecture (v1.1.0)?
- ✅ Were LLM warnings present and visible?
- ❌ Did Agent B modify functions/interfaces without seeing contract warnings?

---

## Success Criteria

### Must Pass (P0) - Test FAILS if any missing

- [x] Drift detected at D-06 (similarity < 0.95)
- [x] D-06.5 synchronization loop triggered
- [x] All 3 new functions added to functional architecture
- [x] All affected services updated (OrderService, PaymentService)
- [x] New interface added (payment_status_query)
- [x] version_architecture.py tool used (not manual)
- [x] Root causes classified for all changes
- [x] Similarity re-validated after updates
- [x] Final similarity >= 0.95
- [x] D-Post-A02 gate passed
- [x] **Service contracts generated at D-02-A05** (NEW)
- [x] **Service contracts regenerated at D-06.5-A04.5** (NEW)
- [x] **Contract validation steps executed** (NEW)

### Should Pass (P1) - Test PASSES but with warnings

- [x] Root cause categories appropriate and specific
- [x] Version history comprehensive and clear
- [x] Iterations <= 2 (efficient synchronization)
- [x] Time to complete sync <= 30 minutes
- [x] All documentation traces test failure → fix → architecture update
- [x] **LLM warnings present in contracts** (NEW)
- [x] **Contracts reflect updated functions/interfaces** (NEW)

### Nice to Have (P2) - Not required for PASS

- [ ] Automated detection (no manual prompting needed)
- [ ] Proactive architecture updates during fix implementation
- [ ] Clear sign-offs and approvals in version history
- [ ] **Agent B explicitly mentions contract warnings when making changes** (NEW)

---

## Failure Modes

### Critical Failures (Test FAILS)

❌ **Agent B skips D-06 drift detection entirely**
- Root Cause: Workflow step not executed
- Impact: Drift never detected, stale architecture persists

❌ **Agent B detects drift but proceeds to D-07 without sync**
- Root Cause: Workflow compliance failure
- Impact: Known drift not resolved, gate bypass

❌ **Agent B updates architecture manually without D-06.5 workflow**
- Root Cause: Ad-hoc fix instead of systematic process
- Impact: Missing versioning, no root cause documentation

❌ **Agent B doesn't use version_architecture.py tool**
- Root Cause: Manual versioning instead of tool
- Impact: Inconsistent versioning, missing history

❌ **Final similarity < 0.95 but gate passes anyway**
- Root Cause: Gate validation failure
- Impact: Deployment with unsynchronized architecture

❌ **Service contracts not generated at D-02-A05** (NEW)
- Root Cause: Workflow step skipped
- Impact: No proactive drift prevention

❌ **Service contracts not regenerated at D-06.5-A04.5** (NEW)
- Root Cause: Workflow step skipped
- Impact: Contracts stale, don't reflect updated architecture

---

### Warning Failures (Test PASSES but with warnings)

⚠️ **Agent B needs manual prompting to trigger D-06.5**
- Indicates: Workflow clarity issue, LLM doesn't auto-trigger
- Fix: Improve workflow instructions

⚠️ **Iterations > 2 (inefficient synchronization)**
- Indicates: First-pass updates incomplete
- Fix: Improve D-06.5-A02/A03 instructions

⚠️ **Root causes generic or missing**
- Indicates: Classification quality issue
- Fix: Provide better examples in workflow

⚠️ **Time > 30 minutes to complete sync**
- Indicates: Workflow inefficiency
- Fix: Optimize tool invocations

⚠️ **LLM warnings not visible in contracts** (NEW)
- Indicates: Contract generation quality issue
- Fix: Improve generate_service_contracts.py output

---

## Agent A Observation Guidelines

### What to Look For

**Proactive Layer (Contracts)**:
1. **Contract Generation**: Were contracts created at D-02-A05?
2. **Contract Content**: Do contracts list correct functions and interfaces?
3. **LLM Warnings**: Are warnings explicit and actionable?
4. **Contract Validation**: Were contracts validated at checkpoints (D-04-A06.5, D-06-A02.5)?
5. **Contract Updates**: Were contracts regenerated when architecture changed (D-06.5-A04.5)?
6. **LLM Awareness**: Did Agent B acknowledge contract warnings when making changes?

**Reactive Layer (D-06.5 Loop)**:
1. **Drift Detection**: Does Agent B even CHECK for drift?
2. **Tool Usage**: Does Agent B use RIGHT tools (version_architecture.py vs manual)?
3. **Iteration**: Does Agent B ITERATE (or assume first update is good enough)?
4. **Documentation**: Does Agent B DOCUMENT WHY (root causes, not just WHAT)?
5. **Consistency**: Are all architecture files updated together (functional, service, interface)?
6. **Versioning**: Is semantic versioning applied correctly?

### Common Issues to Report

**High Priority**:
- Agent skips D-06 comparison entirely
- Agent detects drift but proceeds to D-07 anyway
- Agent manually updates architecture without workflow
- Agent doesn't re-validate after updates
- Agent doesn't classify root causes
- **Agent doesn't generate service contracts** (NEW)
- **Agent modifies functions/interfaces without updating contracts** (NEW)

**Medium Priority**:
- Agent needs prompting to trigger D-06.5
- Iterations > 2 (inefficient)
- Root causes too generic
- Version history incomplete
- **Contracts missing LLM warnings** (NEW)

**Low Priority**:
- Time > 30 minutes (performance issue)
- Manual workarounds needed
- Documentation clarity issues

---

## Integration with GAN Testing Framework

### Workflow 97 Integration

**How TC-002 Fits**:
1. **97-GAN-inspired-test.json** orchestrates test execution
2. **Agent B** (Generator) executes TC-002 workflow blind to expected outputs
3. **Agent A** (Discriminator) observes Agent B, validates against VALIDATION_CRITERIA.md
4. **Automated Validation**: Agent A uses validation logic to check 10 checkpoints
5. **Meta-Analysis**: Agent A generates comprehensive report on Agent B's performance
6. **Fix Triggering**: If P0 issues found → Auto-trigger 98-reflow_feature_update.json

**Benchmarking**:
- **Baseline Run**: First execution establishes baseline metrics
- **Subsequent Runs**: Compare to baseline to detect regressions/improvements
- **Metrics Tracked**:
  - Drift detection rate (% of times Agent B detects drift)
  - Synchronization success rate (% of times similarity reaches >= 0.95)
  - Iterations required (average)
  - Time to synchronize (minutes)
  - Contract generation rate (% of times contracts generated)
  - Contract validation rate (% of checkpoints executed)

---

## Expected Deliverables

### Agent B Should Generate

**Phase 1: Initial Architecture**
- `specs/functional/functional_architecture_v1.0.0.json`
- `specs/machine/service_arch/OrderService/service_architecture_v1.0.0.json`
- `specs/machine/service_arch/PaymentService/service_architecture_v1.0.0.json`
- `specs/machine/interface_registry_v1.0.0.json`
- `specs/functional/version_history.json` (v1.0.0 entry)

**Phase 2: Service Contracts**
- `services/OrderService/SERVICE_CONTRACT.json` (3 functions, 1 consumed interface)
- `services/PaymentService/SERVICE_CONTRACT.json` (2 functions, 1 provided interface)

**Phase 3: Test Results**
- Test failure reports (3 failures)
- Fixed implementation with new functions/interfaces

**Phase 4: Drift Detection**
- D-06 comparison report (similarity < 0.95)
- List of specific differences

**Phase 5: Synchronization**
- `specs/functional/functional_architecture_v1.1.0.json` (8 functions)
- `specs/machine/service_arch/OrderService/service_architecture_v1.1.0.json` (4 functions)
- `specs/machine/service_arch/PaymentService/service_architecture_v1.1.0.json` (4 functions)
- `specs/machine/interface_registry_v1.1.0.json` (2 interfaces)
- `specs/functional/version_history.json` (v1.1.0 entry with root causes)
- Root cause analysis document
- D-06.5 revalidation report (similarity >= 0.95)

**Phase 5.5: Updated Contracts**
- `services/OrderService/SERVICE_CONTRACT.json` (4 functions, 2 consumed interfaces)
- `services/PaymentService/SERVICE_CONTRACT.json` (4 functions, 2 provided interfaces)

**Phase 6: Final Validation**
- D-Post-A02 report (gate PASS, similarity >= 0.95)

### Agent A Should Analyze

**Checkpoint Results**:
- Did Agent B pass/fail each of 10 checkpoints?
- What was similarity score before/after sync?
- How many iterations required?
- Time to complete synchronization?

**Contract Assessment**:
- Were contracts generated at correct workflow steps?
- Do contracts accurately reflect architecture?
- Are LLM warnings present and clear?
- Did Agent B acknowledge warnings when making changes?

**Quality Assessment**:
- Root cause classification quality (Good/Fair/Poor)
- Versioning completeness (Complete/Partial/Missing)
- Tool usage correctness (Correct/Incorrect)

**Deviations**:
- List any workflow deviations
- List any tool misuse
- List any quality issues

**Recommendations**:
- P0 issues requiring immediate fix
- P1 issues for next sprint
- P2 polish items

---

## Extensibility

### Future Test Scenarios

**TC-003: Multiple Drift Cycles**
- Drift → Sync → More Drift → Sync Again
- Tests resilience of D-06.5 loop to repeated drift

**TC-004: Breaking Changes**
- Drift includes interface breaking changes
- Tests contract validation detects breaking changes
- Tests dependency impact analysis

**TC-005: Cross-Service Drift**
- Changes affecting multiple services simultaneously
- Tests consistency of synchronized updates

**TC-006: Operational Drift**
- Drift during operational testing (TO-05)
- Tests TO-05-A05.5/A05.6 operational sync loop

**TC-007: Performance-Driven Drift**
- Architecture changes due to performance optimization
- Tests root cause classification accuracy

**TC-008: Security-Driven Drift**
- Architecture changes due to threat model updates
- Tests security hardening rationale documentation

---

## Conclusion

**TC-002 (architecture_drift_sync)** is a **CRITICAL benchmark test** because:

1. **Validates Real Problem**: Architecture drift is #1 cause of stale documentation
2. **Tests Two Layers**: Proactive (contracts) + Reactive (D-06.5) = comprehensive defense
3. **Realistic Scenario**: Test failures causing drift mirrors real-world development
4. **Systematic Validation**: 10 checkpoints ensure thorough evaluation
5. **Continuous Improvement**: Benchmarking tracks Reflow quality over time
6. **Extensible**: Foundation for additional drift scenarios

**Expected Impact**:
- Prevent stale architecture docs (saves 2-4 hours per service)
- Catch drift early (proactive contracts)
- Resolve drift systematically (reactive D-06.5 loop)
- Maintain architectural intent over project lifecycle
- Enable confident onboarding (docs always current)

**This test is the guardian of architectural truth.** ✅

---

**Document Version**: 1.0.0
**Created**: 2025-11-19
**Next Review**: After first TC-002 execution
