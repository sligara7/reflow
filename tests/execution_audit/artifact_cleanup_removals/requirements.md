# Artifact Cleanup & Removal Test

**Test ID**: TC-003
**Purpose**: Validate that Agent B correctly identifies and cleans up obsolete artifacts when functions/services are removed during refactoring
**Version**: 1.0.0
**Category**: Development Phase Testing (Artifact Cleanup)
**Complexity**: Medium
**Validates**: v3.18.1 D-06.5-A02.5 (Identify Obsolete Artifacts) and D-06.5-A03.5 (Remove Obsolete Artifacts)

---

## Test Objective

**Primary Goal**: Validate that when functions are removed during refactoring (redundant, superseded by external service), Agent B:
1. **Detects removals** using D-06.5-A02.5 (designed > as-built)
2. **Classifies root causes** (redundant_functionality, superseded_by_external, etc.)
3. **Cleans up architecture** (removes from functional_architecture.json, service_architecture.json)
4. **Cleans up contracts** (removes from SERVICE_CONTRACT.json)
5. **Cleans up tests** (deletes or updates test files)
6. **Cleans up deployment** (updates docker-compose.yml, provides cleanup commands)
7. **Documents removals** in version history with rationale

**Why This Matters**: Obsolete artifacts cause CRITICAL real-world problems:
- Tests fail referencing removed methods/endpoints
- Documentation lies about system capabilities
- Architecture files list non-existent functions
- **Old container images run obsolete code** (user's pain point)
- Build scripts try to build removed services
- Service contracts list removed functions

---

## Test Scenario

### Phase 1: Architecture Design (Baseline)

**Workflow**: 00a-basic_setup → 01d-functional_analysis → 01c-top_down_design → 02-artifacts_visualization

**Initial System**: E-commerce Payment Service

**Designed Architecture**:
- **Functions** (6):
  1. ProcessPayment
  2. **ValidatePaymentCard** (will be removed - redundant)
  3. GetPaymentStatus
  4. **CalculateTax** (will be removed - external service)
  5. RefundPayment
  6. SendPaymentConfirmation

- **Service Architecture** (1 service):
  1. **PaymentService**: All 6 functions

- **Interfaces**:
  1. PaymentService → TaxService (tax_calculation) - will be removed

**Expected**: Agent B completes design phase, generates:
- `specs/functional/functional_architecture_v1.0.0.json` (6 functions)
- `specs/machine/service_arch/PaymentService/service_architecture_v1.0.0.json` (6 functions)
- `specs/machine/interface_registry_v1.0.0.json` (1 interface)

---

### Phase 2: Service Implementation (No Drift Yet)

**Workflow**: 03a-development_implementation (D-01 through D-05)

**Implementation**: Agent B implements services per design

**Expected**: Agent B:
- Implements PaymentService with all 6 functions
- Generates service contract (D-02-A05) with 6 functions
- Creates tests for all 6 functions
- No deviations from architecture

---

### Phase 3: Refactoring & Removal of Obsolete Functions (Drift Introduced)

**Workflow**: 03b-development_validation (D-06 start)

**Refactoring Changes** (simulated real-world refactoring):

1. **Refactoring #1**: Remove ValidatePaymentCard
   - **Reason**: Redundant - Stripe API validates cards automatically
   - **Root Cause**: redundant_functionality
   - **Action**: Remove function from PaymentService implementation
   - **Affected**:
     - Remove `validate_payment_card()` method from src/payment_service.py
     - Tests: tests/test_payment_service.py::test_validate_payment_card
     - Docs: docs/PAYMENT_PROCESSING.md (references card validation)

2. **Refactoring #2**: Remove CalculateTax
   - **Reason**: Using external Avalara Tax API instead
   - **Root Cause**: superseded_by_external
   - **Action**: Remove function, remove tax_calculation interface
   - **Affected**:
     - Remove `calculate_tax()` method from src/payment_service.py
     - Remove tax_calculation interface from interface_registry.json
     - Tests: tests/test_payment_service.py::test_calculate_tax
     - Docs: docs/TAX_CALCULATION.md
     - Docker: Remove TaxService from docker-compose.yml (no longer needed)

**Result**: **DRIFT CREATED (Removals)**
- Implementation: 4 functions (ProcessPayment, GetPaymentStatus, RefundPayment, SendPaymentConfirmation)
- Architecture: 6 functions (includes ValidatePaymentCard, CalculateTax)
- **Drift Type**: Architecture > Implementation (obsolete artifacts in architecture)

---

### Phase 4: Architecture Drift Detection (D-06)

**Workflow**: D-06 (Compare as-built vs designed architecture)

**Expected Agent B Behavior**:
1. Run `compare_architectures.py` to compare designed vs implemented
2. Calculate similarity score
3. **DETECT**: Similarity < 0.95 (drift due to removals)
4. **REPORT**: Drift detected with specifics:
   - 2 functions removed (ValidatePaymentCard, CalculateTax)
   - 1 interface removed (tax_calculation)
   - Architecture has MORE than implementation (obsolete entries)
5. **TRIGGER**: D-06.5 Architecture Synchronization Loop

**Validation Criteria**:
- ✅ Agent B runs comparison tool
- ✅ Agent B calculates similarity correctly
- ✅ Agent B identifies similarity < threshold
- ✅ Agent B recognizes REMOVALS (not just additions)
- ✅ Agent B triggers D-06.5 (doesn't just proceed to D-07)

---

### Phase 5: Obsolete Artifact Identification (D-06.5-A02.5)

**Workflow**: D-06.5-A02.5 (NEW in v3.18.1)

**Expected Agent B Behavior**:

**Step 1**: Identify removed functions
- Compare designed functional_architecture.json vs as-built
- Find: ValidatePaymentCard, CalculateTax in design but NOT in implementation

**Step 2**: Identify removed interfaces
- Compare designed interface_registry.json vs as-built
- Find: tax_calculation interface in design but NOT in implementation

**Step 3**: Classify removal root causes
- ValidatePaymentCard: **redundant_functionality** (Stripe validates)
- CalculateTax: **superseded_by_external** (Avalara Tax API)

**Step 4**: Identify affected artifacts
Search for references to removed functions:
- Tests:
  - tests/test_payment_service.py::test_validate_payment_card
  - tests/test_payment_service.py::test_calculate_tax
- Documentation:
  - docs/PAYMENT_PROCESSING.md (references card validation)
  - docs/TAX_CALCULATION.md (entire doc about tax)
- Service contracts:
  - services/PaymentService/SERVICE_CONTRACT.json (lists both functions)
- Deployment:
  - docker-compose.yml (TaxService no longer needed)

**Output**: `context/obsolete_artifacts_analysis.json`

**Validation Criteria**:
- ✅ Agent B identifies 2 removed functions
- ✅ Agent B identifies 1 removed interface
- ✅ Agent B classifies root causes correctly
- ✅ Agent B searches for references in tests, docs, contracts, deployment configs
- ✅ Agent B generates obsolete_artifacts_analysis.json

---

### Phase 6: Obsolete Artifact Cleanup (D-06.5-A03.5)

**Workflow**: D-06.5-A03.5 (NEW in v3.18.1)

**Expected Agent B Behavior**:

**P0 Cleanup (Critical - BLOCKING)**:
1. **Architecture files**:
   - Remove ValidatePaymentCard from functional_architecture.json
   - Remove CalculateTax from functional_architecture.json
   - Remove ValidatePaymentCard from PaymentService/service_architecture.json
   - Remove CalculateTax from PaymentService/service_architecture.json
   - Remove tax_calculation from interface_registry.json

2. **Service contracts**:
   - Update PaymentService/SERVICE_CONTRACT.json to remove ValidatePaymentCard, CalculateTax
   - Update contracted_functions list (6 → 4 functions)
   - Update LLM warnings (function count changed)

3. **Interface contracts**:
   - Delete specs/machine/interfaces/tax_calculation_icd.json (interface removed)

**P1 Cleanup (High Priority - Should Complete)**:
1. **Tests**:
   - Delete or comment out tests/test_payment_service.py::test_validate_payment_card
   - Delete or comment out tests/test_payment_service.py::test_calculate_tax
   - Update any integration tests that reference removed functions

2. **Docker Compose**:
   - Remove TaxService from docker-compose.yml (no longer needed since using Avalara)
   - Remove TaxService volume mounts
   - Remove TaxService environment variables

3. **Container images**:
   - Document docker cleanup commands:
     ```bash
     docker-compose down
     docker rmi tax_service:latest
     docker-compose build --no-cache payment_service
     docker-compose up -d
     ```

**P2 Cleanup (Documentation)**:
1. **Markdown docs**:
   - Update docs/PAYMENT_PROCESSING.md (remove card validation section)
   - Delete docs/TAX_CALCULATION.md (entire feature removed)
   - Update README.md if it references removed features

**Output**: `context/obsolete_artifacts_cleanup_report.json`

**Validation Criteria**:
- ✅ Agent B removes obsolete functions from architecture files
- ✅ Agent B updates service contracts
- ✅ Agent B deletes obsolete ICD files
- ✅ Agent B deletes or updates test files
- ✅ Agent B updates docker-compose.yml
- ✅ Agent B provides docker cleanup commands
- ✅ Agent B updates documentation
- ✅ Agent B generates cleanup report

---

### Phase 7: Architecture Versioning (D-06.5-A04)

**Workflow**: D-06.5-A04 (Enhanced to document removals)

**Expected Agent B Behavior**:

**Version Architectures**:
- Create functional_architecture_v1.1.0.json (4 functions, down from 6)
- Create PaymentService/service_architecture_v1.1.0.json (4 functions)
- Create interface_registry_v1.1.0.json (0 interfaces, down from 1)

**Version History** (documents REMOVALS):
```json
{
  "version": "1.1.0",
  "previous_version": "1.0.0",
  "date": "2025-11-19",
  "change_type": "minor",
  "changes": [
    {
      "type": "removal",
      "function_id": "F-002",
      "function_name": "ValidatePaymentCard",
      "service": "PaymentService",
      "rationale": "Redundant - Stripe API validates cards automatically",
      "root_cause": "redundant_functionality",
      "affected_artifacts": {
        "tests": ["tests/test_payment_service.py::test_validate_payment_card"],
        "docs": ["docs/PAYMENT_PROCESSING.md"],
        "contracts": ["services/PaymentService/SERVICE_CONTRACT.json"]
      }
    },
    {
      "type": "removal",
      "function_id": "F-004",
      "function_name": "CalculateTax",
      "service": "PaymentService",
      "rationale": "Superseded - Now using Avalara Tax API for tax calculations",
      "root_cause": "superseded_by_external",
      "affected_artifacts": {
        "tests": ["tests/test_payment_service.py::test_calculate_tax"],
        "docs": ["docs/TAX_CALCULATION.md"],
        "contracts": ["services/PaymentService/SERVICE_CONTRACT.json"],
        "interfaces": ["tax_calculation"],
        "deployment": ["docker-compose.yml (TaxService removed)"]
      }
    }
  ]
}
```

**Validation Criteria**:
- ✅ Agent B uses version_architecture.py (or manual with complete docs)
- ✅ Version history includes REMOVAL entries (not just additions)
- ✅ Each removal has rationale and root cause
- ✅ Affected artifacts documented for each removal
- ✅ Semantic versioning correct (1.0.0 → 1.1.0)

---

### Phase 8: Re-Validation & Final Verification (D-06.5-A07)

**Workflow**: D-06.5-A07 (Verify Architecture Synchronization)

**Expected Agent B Behavior**:
1. Re-generate as-built architecture from current implementation
2. Compare as-built to updated as-designed architecture
3. Calculate new similarity score
4. **VERIFY**: Similarity >= 0.95 (architecture now clean)

**Expected Similarity**:
- Before cleanup: ~0.70 (2 obsolete functions out of 6 = 33% drift)
- After cleanup: 1.00 (100% - architecture matches implementation exactly)

**Validation Criteria**:
- ✅ Agent B re-validates similarity
- ✅ Final similarity >= 0.95
- ✅ No obsolete artifacts remaining in architecture
- ✅ Agent B proceeds only after synchronization

---

### Phase 9: Final Quality Gate (D-Post-A02)

**Workflow**: D-Post-A02 (Final Architecture Synchronization Verification)

**Expected Agent B Behavior**:
1. Run final architecture synchronization check
2. **VERIFY**: Architecture synchronized (similarity >= 0.95)
3. **VERIFY**: Version history documents removals
4. **VERIFY**: Cleanup report exists
5. **PASS**: Quality gate allows deployment

**Validation Criteria**:
- ✅ Final similarity >= 0.95
- ✅ Version history complete (includes removals)
- ✅ Cleanup report exists
- ✅ All obsolete artifacts cleaned up
- ✅ D-Post-A02 gate passes

---

## Success Metrics

### Primary Metrics (P0 - Must Pass)

1. **Removal Detection**:
   - ✅ Agent B detects 2 removed functions at D-06.5-A02.5
   - ✅ Agent B detects 1 removed interface
   - ✅ Agent B classifies root causes correctly

2. **Architecture Cleanup**:
   - ✅ Removed functions deleted from functional_architecture.json
   - ✅ Removed functions deleted from service_architecture.json
   - ✅ Removed interface deleted from interface_registry.json

3. **Contract Cleanup**:
   - ✅ SERVICE_CONTRACT.json updated (6 → 4 functions)
   - ✅ Obsolete ICD deleted (tax_calculation_icd.json)

4. **Test Cleanup**:
   - ✅ Test files deleted or updated (2 tests removed)

5. **Deployment Cleanup**:
   - ✅ docker-compose.yml updated (TaxService removed)
   - ✅ Docker cleanup commands provided

6. **Versioning with Removals**:
   - ✅ Version history documents removals (not just additions)
   - ✅ Each removal has rationale and root cause
   - ✅ Affected artifacts documented

7. **Final Synchronization**:
   - ✅ Final similarity >= 0.95 (ideally 1.00)
   - ✅ D-Post-A02 gate passes

### Secondary Metrics (P1 - Should Pass)

8. **Cleanup Report Quality**:
   - ✅ Comprehensive cleanup report generated
   - ✅ Docker cleanup commands included
   - ✅ Manual review items documented (if any)

9. **Documentation Cleanup**:
   - ✅ Documentation updated (removed sections)
   - ✅ README updated if applicable

10. **Time Efficiency**:
    - ✅ Cleanup completed in < 20 minutes
    - ✅ No manual intervention required for P0/P1 cleanup

### Failure Modes (What Agent B Should NOT Do)

❌ **Skip removal detection** - Only detects additions, ignores that architecture > implementation
❌ **Manual updates without D-06.5-A02.5/A03.5** - Manually edits architecture without cleanup workflow
❌ **Incomplete cleanup** - Cleans architecture but forgets tests/contracts/deployment configs
❌ **No rationale for removals** - Removes from architecture without documenting WHY
❌ **Ignore docker cleanup** - Doesn't update docker-compose.yml or provide cleanup commands
❌ **No version history for removals** - Version history only shows additions, not removals

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
  ↓ (implement all 6 functions)
  ↓
03b-development_validation (D-06 to D-07)
  ↓ (refactor - remove 2 functions)
  ↓
D-06: As-built comparison
  ↓ (detect drift - architecture > implementation)
  ↓
D-06.5: Architecture Synchronization Loop ⭐ FOCUS
  ↓ D-06.5-A01: Analyze drift
  ↓ D-06.5-A02: Root cause classification (additions)
  ↓ D-06.5-A02.5: Identify obsolete artifacts ⭐ NEW
  ↓    - Detect 2 removed functions
  ↓    - Detect 1 removed interface
  ↓    - Classify removal root causes
  ↓    - Search for references
  ↓ D-06.5-A03: Architecture update decision
  ↓ D-06.5-A03.5: Remove obsolete artifacts ⭐ NEW
  ↓    - P0: Clean architecture, contracts, ICDs
  ↓    - P1: Clean tests, docker configs
  ↓    - P2: Clean docs
  ↓ D-06.5-A04: Version architectures (with removal rationale)
  ↓ D-06.5-A05: Re-validate architecture
  ↓ D-06.5-A06: Regenerate artifacts
  ↓ D-06.5-A07: Verify synchronization (similarity >= 0.95)
  ↓
D-07: Integration testing
  ↓
D-Post-A02: Final sync verification ⭐ GATE
  ↓ (verify cleanup complete, similarity >= 0.95)
  ↓
PASS ✅
```

---

## Test Deliverables

### Agent B Should Generate:

**Phase 1**: Initial Architecture
- specs/functional/functional_architecture_v1.0.0.json (6 functions)
- specs/machine/service_arch/PaymentService/service_architecture_v1.0.0.json (6 functions)
- specs/machine/interface_registry_v1.0.0.json (1 interface)

**Phase 2**: Implementation & Contracts
- services/PaymentService/src/payment_service.py (6 functions)
- services/PaymentService/SERVICE_CONTRACT.json (v1.0.0 - 6 functions)
- tests/test_payment_service.py (6 test functions)

**Phase 3**: Refactored Implementation
- services/PaymentService/src/payment_service.py (4 functions - 2 removed)

**Phase 4**: Drift Detection
- D-06 comparison report (similarity < 0.95, 2 removals detected)

**Phase 5**: Obsolete Artifact Analysis
- context/obsolete_artifacts_analysis.json (2 functions, 1 interface identified as obsolete)

**Phase 6**: Cleanup
- Updated architecture files (v1.1.0 - 4 functions)
- Updated SERVICE_CONTRACT.json (v1.1.0 - 4 functions)
- Deleted tax_calculation_icd.json
- Updated docker-compose.yml
- context/obsolete_artifacts_cleanup_report.json

**Phase 7**: Versioning
- specs/functional/version_history.json (documents removals with rationale)

**Phase 9**: Final Verification
- D-Post-A02 report (gate PASS, similarity >= 0.95)

---

## Expected Duration

- **Phase 1** (Architecture Design): 30 minutes
- **Phase 2** (Implementation): 20 minutes
- **Phase 3** (Refactoring): 10 minutes
- **Phase 4** (Drift Detection): 5 minutes
- **Phase 5** (Obsolete Artifact ID): 10 minutes ⭐ **NEW**
- **Phase 6** (Cleanup): 15 minutes ⭐ **NEW**
- **Phase 7** (Versioning): 10 minutes
- **Phase 8** (Re-Validation): 5 minutes
- **Phase 9** (Final Gate): 5 minutes

**Total**: 110 minutes

---

## Pass/Fail Criteria

### PASS ✅

- All P0 success metrics met
- Agent B correctly detected removals (not just additions)
- Agent B executed D-06.5-A02.5 (identify obsolete artifacts)
- Agent B executed D-06.5-A03.5 (remove obsolete artifacts)
- Architecture cleaned up (no obsolete entries)
- Contracts cleaned up
- Tests cleaned up
- Docker configs cleaned up
- Cleanup report generated with docker commands
- Version history documents removals with rationale
- Similarity >= 0.95 achieved

### FAIL ❌

- Agent B only detected additions, ignored removals
- Agent B skipped D-06.5-A02.5 or D-06.5-A03.5
- Architecture still has obsolete entries
- Contracts not updated
- Tests not cleaned up
- Docker configs not updated
- No cleanup report
- Version history doesn't document removals
- Similarity < 0.95 at completion

---

## Notes for Agent A (Observer)

**What to Look For**:
1. Does Agent B detect REMOVALS (not just additions)?
2. Does Agent B execute D-06.5-A02.5 and D-06.5-A03.5?
3. Does Agent B clean up ALL affected artifacts (architecture, contracts, tests, docker)?
4. Does Agent B provide docker cleanup commands? (USER PAIN POINT)
5. Does Agent B document removals in version history with WHY?

**Common Failure Patterns**:
- Agent only looks for additions, misses removals entirely
- Agent cleans architecture but forgets contracts/tests
- Agent doesn't update docker-compose.yml (USER PAIN POINT: old images running)
- Agent doesn't provide docker cleanup commands
- Version history only shows additions, not removals

**This test validates the REMOVAL side of architecture synchronization** - completing the story started in TC-002 (additions/modifications).

---

**Test Case Created**: 2025-11-19
**Version**: 1.0.0
**Purpose**: Validate Artifact Cleanup for Removals (v3.18.1 D-06.5-A02.5 & A03.5)
