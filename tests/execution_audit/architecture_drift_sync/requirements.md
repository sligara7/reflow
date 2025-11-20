# Architecture Drift & Synchronization Test

**Test ID**: TC-002
**Purpose**: Validate that Agent B correctly detects architecture drift during development/testing and triggers architecture synchronization loop
**Version**: 1.0.0
**Category**: Development Phase Testing
**Complexity**: Medium

---

## Test Objective

**Primary Goal**: Validate that when services evolve during development/testing and diverge from designed architecture, Agent B:
1. **Detects drift** using similarity analysis
2. **Triggers synchronization** (D-06.5 Architecture Synchronization Loop)
3. **Updates architecture** to match implementation
4. **Versions changes** with rationale
5. **Iterates** until similarity >= 0.95

**Why This Matters**: Architecture drift is a CRITICAL problem that causes:
- Stale documentation
- Misalignment between design and implementation
- Integration failures
- Maintenance nightmares
- Loss of architectural intent

---

## Test Scenario

### Phase 1: Architecture Design (Baseline)

**Workflow**: 00a-basic_setup → 01d-functional_analysis → 01c-top_down_design → 02-artifacts_visualization

**Initial System**: Simple E-commerce Order Service

**Designed Architecture**:
- **Functions** (5):
  1. CreateOrder
  2. GetOrderStatus
  3. CancelOrder
  4. ProcessPayment
  5. SendOrderConfirmation

- **Service Architecture** (2 services):
  1. **OrderService**: CreateOrder, GetOrderStatus, CancelOrder
  2. **PaymentService**: ProcessPayment, SendOrderConfirmation

- **Interfaces**:
  1. OrderService → PaymentService (payment_processing)

**Expected**: Agent B completes design phase, generates:
- `specs/functional/functional_architecture.json`
- `specs/machine/service_arch/OrderService/service_architecture.json`
- `specs/machine/service_arch/PaymentService/service_architecture.json`
- `specs/machine/interface_registry.json`

---

### Phase 2: Service Implementation (No Drift Yet)

**Workflow**: 03a-development_implementation (D-01 through D-05)

**Implementation**: Agent B implements services per design

**Expected**: Agent B:
- Implements OrderService with CreateOrder, GetOrderStatus, CancelOrder
- Implements PaymentService with ProcessPayment, SendOrderConfirmation
- No deviations from architecture

---

### Phase 3: Testing & Discovery of Issues (Drift Introduced)

**Workflow**: 03b-development_validation (D-06 through D-07)

**Injected Test Failures** (simulated real-world issues):

1. **Test Failure #1**: Order cancellation doesn't refund payment
   - **Symptom**: CancelOrder completes but payment not refunded
   - **Root Cause**: Missing function - RefundPayment not in architecture
   - **Required Fix**: Add RefundPayment function to PaymentService

2. **Test Failure #2**: Order status doesn't include payment status
   - **Symptom**: GetOrderStatus returns incomplete information
   - **Root Cause**: Missing interface - OrderService needs to query PaymentService
   - **Required Fix**: Add new interface OrderService → PaymentService (payment_status_query)

3. **Test Failure #3**: Concurrent order creation causes race conditions
   - **Symptom**: Duplicate orders created
   - **Root Cause**: Missing function - ValidateOrderUniqueness
   - **Required Fix**: Add ValidateOrderUniqueness to OrderService

**Agent B Implements Fixes**:
- Adds RefundPayment function to PaymentService
- Adds payment_status_query interface
- Adds ValidateOrderUniqueness function to OrderService
- Updates CancelOrder to call RefundPayment

**Result**: **ARCHITECTURE DRIFT**
- Implementation now has 8 functions (was 5)
- Implementation has 2 interfaces (was 1)
- Functional flows changed (CancelOrder → RefundPayment added)

---

### Phase 4: Architecture Synchronization Detection (D-06 As-Built Comparison)

**Workflow**: D-06 (Compare as-built vs designed architecture)

**Expected Agent B Behavior**:
1. Run `compare_architectures.py` to compare designed vs implemented
2. Calculate similarity score
3. **DETECT**: Similarity < 0.95 (significant drift)
4. **REPORT**: Drift detected with specifics:
   - 3 new functions added
   - 1 new interface added
   - Multiple functional flows changed
5. **TRIGGER**: D-06.5 Architecture Synchronization Loop

**Validation Criteria**:
- ✅ Agent B runs comparison tool
- ✅ Agent B calculates similarity correctly
- ✅ Agent B identifies similarity < threshold (0.7 = MANDATORY sync, < 0.95 = RECOMMENDED)
- ✅ Agent B triggers D-06.5 (doesn't just proceed to D-07)

---

### Phase 5: Architecture Synchronization Loop (D-06.5)

**Workflow**: D-06.5 (iterative sync until architecture matches implementation)

**Expected Agent B Behavior**:

**D-06.5-A01**: Classify root causes of drift
- RefundPayment: operational_reality (discovered during testing)
- payment_status_query: requirements_creep (incomplete initial requirements)
- ValidateOrderUniqueness: technical_constraints (race condition prevention)

**D-06.5-A02**: Update functional architecture
- Add RefundPayment, ValidateOrderUniqueness functions
- Update CancelOrder dependencies to include RefundPayment
- Update GetOrderStatus dependencies to include payment status query

**D-06.5-A03**: Update service architecture
- Add RefundPayment to PaymentService
- Add ValidateOrderUniqueness to OrderService
- Add payment_status_query interface

**D-06.5-A04**: Version architectures using `version_architecture.py`
- Create functional_architecture_v1.1.0.json with rationale
- Create service_architecture_v1.1.0.json for each service
- Document WHY changes were made (root causes)

**D-06.5-A05**: Re-validate similarity
- Run comparison again
- Calculate new similarity score
- **VERIFY**: Similarity >= 0.95

**D-06.5-A06**: Iterate if needed
- IF similarity < 0.95: Return to D-06.5-A02 (iterate)
- IF similarity >= 0.95: Proceed to D-07

**Validation Criteria**:
- ✅ Agent B classifies ALL drift causes
- ✅ Agent B updates functional_architecture.json with new functions/flows
- ✅ Agent B updates service_architecture.json for affected services
- ✅ Agent B uses version_architecture.py (not manual versioning)
- ✅ Agent B includes rationale in version history
- ✅ Agent B re-validates and iterates if needed
- ✅ Agent B achieves similarity >= 0.95 before proceeding

---

### Phase 6: Final Validation (D-Post-A02)

**Workflow**: D-Post (final quality gates)

**Expected Agent B Behavior**:
1. Run final architecture synchronization check (D-Post-A02)
2. **VERIFY**: Architecture and implementation aligned (similarity >= 0.95)
3. **VERIFY**: Version history documents drift reasons
4. **PASS**: Quality gate allows deployment

**Validation Criteria**:
- ✅ Final similarity >= 0.95
- ✅ Version history exists and is complete
- ✅ All drift classified and documented
- ✅ Architecture documents are current (not stale)

---

## Success Metrics

### Primary Metrics (P0 - Must Pass)

1. **Drift Detection**:
   - ✅ Agent B runs similarity comparison at D-06
   - ✅ Agent B correctly identifies similarity < 0.95
   - ✅ Agent B does NOT skip to D-07 when drift detected

2. **Synchronization Triggered**:
   - ✅ Agent B triggers D-06.5 workflow
   - ✅ Agent B does NOT manually update architecture without workflow

3. **Architecture Updated**:
   - ✅ functional_architecture.json updated with new functions
   - ✅ service_architecture.json updated for affected services
   - ✅ interface_registry.json updated with new interfaces

4. **Versioning Applied**:
   - ✅ Uses version_architecture.py tool
   - ✅ Creates versioned files (v1.1.0)
   - ✅ Includes rationale for changes

5. **Iteration Until Sync**:
   - ✅ Re-validates similarity after updates
   - ✅ Iterates if similarity still < 0.95
   - ✅ Only proceeds when similarity >= 0.95

### Secondary Metrics (P1 - Should Pass)

6. **Root Cause Classification**:
   - ✅ Classifies each drift with correct category
   - ✅ Provides specific rationale (not generic)

7. **Quality of Documentation**:
   - ✅ Version history is comprehensive
   - ✅ Architectural decisions documented
   - ✅ Traceability from test failure → fix → architecture update

8. **Time Efficiency**:
   - ✅ Completes sync in < 30 minutes
   - ✅ Requires ≤ 2 sync iterations

### Failure Modes (What Agent B Should NOT Do)

❌ **Skip drift detection** - Proceeds to D-07 without checking similarity
❌ **Manual updates** - Updates architecture without using version_architecture.py
❌ **Incomplete sync** - Updates some files but not others (inconsistent state)
❌ **No rationale** - Versions without documenting WHY
❌ **Single iteration** - Doesn't re-validate, assumes first update is sufficient
❌ **Ignore threshold** - Proceeds with similarity < 0.95

---

## Expected Workflow Path

```
00a-basic_setup
  ↓
01d-functional_analysis
  ↓
01c-top_down_design (SE-01, SE-02)
  ↓
02-artifacts_visualization
  ↓
03a-development_implementation (D-01 to D-05)
  ↓ (implement services per architecture)
  ↓
03b-development_validation (D-06 to D-07)
  ↓
D-06: As-built comparison
  ↓ (detect drift - similarity < 0.95)
  ↓
D-06.5: Architecture Synchronization Loop ⭐ CRITICAL
  ↓ D-06.5-A01: Classify drift causes
  ↓ D-06.5-A02: Update functional architecture
  ↓ D-06.5-A03: Update service architecture
  ↓ D-06.5-A04: Version architectures
  ↓ D-06.5-A05: Re-validate similarity
  ↓ (if similarity >= 0.95) ✅
  ↓
D-07: Integration testing
  ↓
D-Post-A02: Final sync verification ⭐ GATE
  ↓ (verify similarity >= 0.95)
  ↓
PASS ✅
```

---

## Test Deliverables

### Agent B Should Generate:

1. **Initial Architecture** (Phase 1):
   - specs/functional/functional_architecture_v1.0.0.json
   - specs/machine/service_arch/*/service_architecture_v1.0.0.json
   - specs/machine/interface_registry_v1.0.0.json

2. **Implementation** (Phase 2):
   - services/OrderService/src/main.py (or equivalent)
   - services/PaymentService/src/main.py

3. **Test Results** (Phase 3):
   - Test failure reports showing the 3 issues
   - Fixed implementation with new functions/interfaces

4. **Drift Detection** (Phase 4):
   - D-06 comparison report showing similarity < 0.95
   - List of specific differences

5. **Synchronization** (Phase 5):
   - Updated functional_architecture_v1.1.0.json
   - Updated service_architecture_v1.1.0.json for affected services
   - Updated interface_registry_v1.1.0.json
   - version_history.json documenting changes
   - Root cause analysis document

6. **Final Validation** (Phase 6):
   - D-Post-A02 report showing similarity >= 0.95
   - Complete version history

### Agent A Should Analyze:

1. **Did Agent B detect drift?** (Yes/No, at what step)
2. **Did Agent B trigger D-06.5?** (Yes/No, manual or automatic)
3. **How many sync iterations?** (Count)
4. **Final similarity score?** (Number)
5. **Quality of root cause classification?** (Good/Fair/Poor)
6. **Quality of versioning?** (Complete/Partial/Missing)
7. **Time to complete sync?** (Minutes)
8. **Deviations from workflow?** (List)

---

## Injected Test Data

To simulate the test failures, provide Agent B with:

**File**: `tests/execution_audit/architecture_drift_sync/test_failures.json`

```json
{
  "test_phase": "D-06",
  "test_failures": [
    {
      "test_id": "TEST-001",
      "test_name": "test_cancel_order_refunds_payment",
      "status": "FAILED",
      "error": "AssertionError: Payment not refunded after order cancellation",
      "expected": "Payment refunded when order cancelled",
      "actual": "Order cancelled but payment remains charged",
      "root_cause": "Missing RefundPayment function in PaymentService",
      "required_fix": "Add RefundPayment function and update CancelOrder to call it"
    },
    {
      "test_id": "TEST-002",
      "test_name": "test_get_order_status_includes_payment",
      "status": "FAILED",
      "error": "AssertionError: Order status missing payment information",
      "expected": "Order status includes payment_status field",
      "actual": "Order status only includes order fields",
      "root_cause": "OrderService doesn't query PaymentService for payment status",
      "required_fix": "Add payment_status_query interface between OrderService and PaymentService"
    },
    {
      "test_id": "TEST-003",
      "test_name": "test_concurrent_order_creation",
      "status": "FAILED",
      "error": "IntegrityError: Duplicate order_id created",
      "expected": "Concurrent requests create unique orders",
      "actual": "Race condition allows duplicate orders",
      "root_cause": "No uniqueness validation before order creation",
      "required_fix": "Add ValidateOrderUniqueness function to OrderService"
    }
  ]
}
```

---

## Expected Duration

- **Phase 1** (Architecture Design): 30 minutes
- **Phase 2** (Implementation): 20 minutes
- **Phase 3** (Testing + Fixes): 20 minutes
- **Phase 4** (Drift Detection): 5 minutes
- **Phase 5** (Synchronization): 20-30 minutes ⭐ **CRITICAL PHASE**
- **Phase 6** (Final Validation): 5 minutes

**Total**: 100-110 minutes

---

## Pass/Fail Criteria

### PASS ✅

- All P0 success metrics met
- Agent B correctly detected drift
- Agent B triggered D-06.5 synchronization
- Architecture updated to match implementation
- Similarity >= 0.95 achieved
- Version history complete

### FAIL ❌

- Agent B skipped drift detection
- Agent B didn't trigger synchronization
- Architecture not updated
- Similarity < 0.95 at completion
- No versioning applied
- Agent B manually updated without workflow

---

## Notes for Agent A (Observer)

**What to Look For**:
1. Does Agent B even CHECK for drift? (Many agents skip this)
2. Does Agent B use the RIGHT tools? (version_architecture.py vs manual edits)
3. Does Agent B ITERATE? (Or assume first update is good enough)
4. Does Agent B DOCUMENT WHY? (Root causes, not just WHAT changed)

**Common Failure Patterns**:
- Agent skips D-06 comparison entirely
- Agent detects drift but proceeds to D-07 anyway
- Agent manually updates architecture without workflow
- Agent doesn't re-validate after updates
- Agent doesn't classify root causes

**This is a CRITICAL test** because architecture drift is one of the biggest real-world problems in systems engineering!

---

## Extensibility

**Future Enhancements**:
1. Add operational testing drift (TO-05-A05.5/A05.6 loop)
2. Add multiple drift iterations (drift → sync → more drift → sync again)
3. Add breaking changes (test handling of incompatible changes)
4. Add cross-service drift (changes affecting multiple services)

---

**Test Case Created**: 2025-11-19
**Version**: 1.0.0
**Purpose**: Validate Architecture Synchronization Loop (v3.15.0)
