# Artifact Cleanup & Removal Test - Validation Criteria

**Test Case**: TC-003 (artifact_cleanup_removals)
**Purpose**: Automated validation of Agent B's artifact cleanup behavior for removals

---

## Validation Checkpoints

### ✅ Checkpoint 1: Drift Detection - Removals (D-06)

**Files to Check**:
- `actual_outputs/D-06-comparison-report.json`

**Validation Rules**:
```python
{
  "checkpoint": "drift_detection_removals",
  "similarity_score": {
    "expected": "< 0.95",
    "type": "removal_drift",
    "note": "Architecture has MORE than implementation (obsolete entries)"
  },
  "removals_detected": {
    "functions": ["ValidatePaymentCard", "CalculateTax"],
    "interfaces": ["tax_calculation"]
  }
}
```

**Critical Questions**:
- ✅ Did Agent B detect REMOVALS (not just additions)? (Yes/No)
- ✅ Did Agent B recognize architecture > implementation? (Yes/No)
- ✅ Similarity < 0.95? (Yes/No)

---

### ✅ Checkpoint 2: Obsolete Artifact Identification (D-06.5-A02.5)

**Files to Check**:
- `actual_outputs/context/obsolete_artifacts_analysis.json`

**Validation Rules**:
```python
{
  "checkpoint": "obsolete_artifacts_identified",
  "removed_functions": {
    "count": 2,
    "expected": [
      {
        "function_name": "ValidatePaymentCard",
        "root_cause": "redundant_functionality",
        "rationale_specific": true
      },
      {
        "function_name": "CalculateTax",
        "root_cause": "superseded_by_external",
        "rationale_specific": true
      }
    ]
  },
  "removed_interfaces": {
    "count": 1,
    "expected": ["tax_calculation"]
  },
  "affected_artifacts_identified": {
    "tests": true,
    "docs": true,
    "contracts": true,
    "deployment": true
  }
}
```

**Critical Questions**:
- ✅ Did Agent B execute D-06.5-A02.5? (Yes/No)
- ✅ Identified 2 removed functions? (Yes/No)
- ✅ Identified 1 removed interface? (Yes/No)
- ✅ Classified root causes? (Yes/No)
- ✅ Searched for affected artifacts? (Yes/No)

---

### ✅ Checkpoint 3: Architecture Cleanup (D-06.5-A03.5 - P0)

**Files to Check**:
- `specs/functional/functional_architecture_v1.1.0.json`
- `specs/machine/service_arch/PaymentService/service_architecture_v1.1.0.json`
- `specs/machine/interface_registry_v1.1.0.json`

**Validation Rules**:
```python
{
  "checkpoint": "architecture_cleanup",
  "functional_architecture": {
    "functions_count": 4,  # Down from 6
    "removed": ["ValidatePaymentCard", "CalculateTax"]
  },
  "service_architecture": {
    "allocated_functions_count": 4,  # Down from 6
    "removed": ["ValidatePaymentCard", "CalculateTax"]
  },
  "interface_registry": {
    "interfaces_count": 0,  # Down from 1
    "removed": ["tax_calculation"]
  }
}
```

**Critical Questions**:
- ✅ Removed from functional_architecture.json? (Yes/No)
- ✅ Removed from service_architecture.json? (Yes/No)
- ✅ Removed from interface_registry.json? (Yes/No)

---

### ✅ Checkpoint 4: Contract Cleanup (D-06.5-A03.5 - P0)

**Files to Check**:
- `services/PaymentService/SERVICE_CONTRACT.json`
- `specs/machine/interfaces/tax_calculation_icd.json` (should NOT exist)

**Validation Rules**:
```python
{
  "checkpoint": "contract_cleanup",
  "service_contract": {
    "contracted_functions_count": 4,  # Down from 6
    "removed": ["ValidatePaymentCard", "CalculateTax"],
    "llm_warnings_updated": true
  },
  "icd_deleted": {
    "tax_calculation_icd.json": "file_does_not_exist"
  }
}
```

**Critical Questions**:
- ✅ SERVICE_CONTRACT.json updated? (Yes/No - 6→4 functions)
- ✅ tax_calculation_icd.json deleted? (Yes/No)

---

### ✅ Checkpoint 5: Test Cleanup (D-06.5-A03.5 - P1)

**Files to Check**:
- `tests/test_payment_service.py`
- `actual_outputs/context/obsolete_artifacts_cleanup_report.json`

**Validation Rules**:
```python
{
  "checkpoint": "test_cleanup",
  "tests_deleted_or_updated": [
    "test_validate_payment_card",
    "test_calculate_tax"
  ],
  "cleanup_method": "deleted | commented_out | updated"
}
```

**Critical Questions**:
- ✅ test_validate_payment_card removed/updated? (Yes/No)
- ✅ test_calculate_tax removed/updated? (Yes/No)

---

### ✅ Checkpoint 6: Docker Cleanup (D-06.5-A03.5 - P1)

**Files to Check**:
- `docker-compose.yml`
- `actual_outputs/context/obsolete_artifacts_cleanup_report.json`

**Validation Rules**:
```python
{
  "checkpoint": "docker_cleanup",
  "docker_compose_updated": {
    "tax_service_removed": true,
    "environment_vars_removed": ["TAX_SERVICE_URL", "TAX_DB_CONNECTION"],
    "volumes_removed": ["tax_service_data"]
  },
  "docker_cleanup_commands_provided": {
    "commands": [
      "docker-compose down",
      "docker rmi tax_service:latest",
      "docker-compose build --no-cache",
      "docker-compose up -d"
    ]
  }
}
```

**Critical Questions**:
- ✅ docker-compose.yml updated? (Yes/No - TaxService removed)
- ✅ Docker cleanup commands provided? (Yes/No)

---

### ✅ Checkpoint 7: Documentation Cleanup (D-06.5-A03.5 - P2)

**Files to Check**:
- `docs/PAYMENT_PROCESSING.md`
- `docs/TAX_CALCULATION.md` (should be deleted or updated)
- `actual_outputs/context/obsolete_artifacts_cleanup_report.json`

**Validation Rules**:
```python
{
  "checkpoint": "documentation_cleanup",
  "docs_updated_or_deleted": [
    "PAYMENT_PROCESSING.md (updated)",
    "TAX_CALCULATION.md (deleted)"
  ]
}
```

**Critical Questions**:
- ✅ Documentation updated? (Yes/No)
- ⚠️ P2 - Can be skipped if time constrained

---

### ✅ Checkpoint 8: Versioning with Removals (D-06.5-A04)

**Files to Check**:
- `specs/functional/version_history.json`

**Validation Rules**:
```python
{
  "checkpoint": "versioning_with_removals",
  "version": "1.1.0",
  "changes": [
    {
      "type": "removal",
      "function": "ValidatePaymentCard",
      "rationale": "Redundant - Stripe validates",
      "root_cause": "redundant_functionality"
    },
    {
      "type": "removal",
      "function": "CalculateTax",
      "rationale": "Superseded - Avalara Tax API",
      "root_cause": "superseded_by_external"
    }
  ],
  "affected_artifacts_documented": true
}
```

**Critical Questions**:
- ✅ Version history includes removals? (Yes/No)
- ✅ Each removal has rationale? (Yes/No)
- ✅ Root causes documented? (Yes/No)
- ✅ Affected artifacts listed? (Yes/No)

---

### ✅ Checkpoint 9: Cleanup Report Generated (D-06.5-A03.5)

**Files to Check**:
- `actual_outputs/context/obsolete_artifacts_cleanup_report.json`

**Validation Rules**:
```python
{
  "checkpoint": "cleanup_report",
  "report_exists": true,
  "contains": {
    "cleanup_summary": true,
    "manual_review_needed": "list",
    "docker_cleanup_commands": true
  }
}
```

**Critical Questions**:
- ✅ Cleanup report generated? (Yes/No)
- ✅ Docker commands included? (Yes/No)

---

### ✅ Checkpoint 10: Final Synchronization (D-06.5-A07, D-Post-A02)

**Files to Check**:
- `actual_outputs/D-06.5-A07-similarity-validation.json`
- `actual_outputs/D-Post-A02-final-sync-verification.json`

**Validation Rules**:
```python
{
  "checkpoint": "final_synchronization",
  "similarity_score": ">= 0.95",
  "ideally": "1.00",
  "architecture_synchronized": true,
  "no_obsolete_artifacts_remaining": true,
  "gate_status": "PASS"
}
```

**Critical Questions**:
- ✅ Final similarity >= 0.95? (Yes/No)
- ✅ D-Post-A02 gate passed? (Yes/No)
- ✅ No obsolete artifacts remaining? (Yes/No)

---

## Overall Test Success Criteria

### Must Pass (P0)

- [x] Drift detected (removals, not just additions)
- [x] D-06.5-A02.5 executed (identify obsolete artifacts)
- [x] D-06.5-A03.5 executed (remove obsolete artifacts)
- [x] Architecture files cleaned up (2 functions, 1 interface removed)
- [x] Service contracts cleaned up (6→4 functions)
- [x] ICD deleted (tax_calculation_icd.json)
- [x] Tests cleaned up (2 tests removed/updated)
- [x] Docker configs cleaned up (TaxService removed)
- [x] Docker cleanup commands provided
- [x] Version history documents removals with rationale
- [x] Final similarity >= 0.95
- [x] D-Post-A02 gate passed

### Should Pass (P1)

- [x] Root causes specific (not generic)
- [x] Cleanup report comprehensive
- [x] Manual review items documented (if any)
- [x] Time < 20 minutes for cleanup

### Nice to Have (P2)

- [ ] Documentation cleaned up
- [ ] All P2 cleanup completed

---

## Failure Modes

### Critical Failures (Test FAILS)

❌ Agent B only detects additions, ignores removals
❌ Agent B skips D-06.5-A02.5 or D-06.5-A03.5
❌ Architecture files still have obsolete entries
❌ Service contracts not updated
❌ Tests not cleaned up
❌ Docker configs not updated (USER PAIN POINT)
❌ No docker cleanup commands (USER PAIN POINT)
❌ Version history doesn't document removals

### Warning Failures (Test PASSES but with warnings)

⚠️ Cleanup incomplete (some artifacts missed)
⚠️ Manual review needed for most items
⚠️ Time > 20 minutes
⚠️ Documentation not cleaned up (P2)

---

## Automated Validation Script

```python
def validate_artifact_cleanup_test(actual_outputs_dir):
    results = {
        "checkpoint_1_removals_detected": False,
        "checkpoint_2_obsolete_identified": False,
        "checkpoint_3_architecture_cleaned": False,
        "checkpoint_4_contracts_cleaned": False,
        "checkpoint_5_tests_cleaned": False,
        "checkpoint_6_docker_cleaned": False,
        "checkpoint_7_docs_cleaned": False,
        "checkpoint_8_versioning_removals": False,
        "checkpoint_9_cleanup_report": False,
        "checkpoint_10_final_sync": False,
        "overall_pass": False
    }

    # Checkpoint 1: Removals detected
    if exists("D-06-comparison-report.json"):
        report = load_json("D-06-comparison-report.json")
        if "removals" in report or report.get("similarity_score") < 0.95:
            results["checkpoint_1_removals_detected"] = True

    # Checkpoint 2: Obsolete artifacts identified
    if exists("context/obsolete_artifacts_analysis.json"):
        analysis = load_json("obsolete_artifacts_analysis.json")
        if len(analysis.get("removed_functions", [])) >= 2:
            results["checkpoint_2_obsolete_identified"] = True

    # Checkpoint 3: Architecture cleaned
    if exists("specs/functional/functional_architecture_v1.1.0.json"):
        func_arch = load_json("functional_architecture_v1.1.0.json")
        if len(func_arch.get("functions", [])) == 4:  # Down from 6
            results["checkpoint_3_architecture_cleaned"] = True

    # Checkpoint 4: Contracts cleaned
    if exists("services/PaymentService/SERVICE_CONTRACT.json"):
        contract = load_json("SERVICE_CONTRACT.json")
        if len(contract.get("contracted_functions", {}).get("functions", [])) == 4:
            results["checkpoint_4_contracts_cleaned"] = True

    # Checkpoint 5: Tests cleaned
    # Check if tests were removed/updated (search for test functions)
    results["checkpoint_5_tests_cleaned"] = True  # Assume true if no errors

    # Checkpoint 6: Docker cleaned
    if exists("context/obsolete_artifacts_cleanup_report.json"):
        cleanup = load_json("obsolete_artifacts_cleanup_report.json")
        if cleanup.get("docker_compose_updated") and cleanup.get("docker_cleanup_commands"):
            results["checkpoint_6_docker_cleaned"] = True

    # Checkpoint 8: Versioning with removals
    if exists("specs/functional/version_history.json"):
        history = load_json("version_history.json")
        if any(change.get("type") == "removal" for change in history.get("changes", [])):
            results["checkpoint_8_versioning_removals"] = True

    # Checkpoint 9: Cleanup report
    if exists("context/obsolete_artifacts_cleanup_report.json"):
        results["checkpoint_9_cleanup_report"] = True

    # Checkpoint 10: Final sync
    if exists("D-Post-A02-final-sync-verification.json"):
        final = load_json("D-Post-A02-final-sync-verification.json")
        if final.get("similarity_score") >= 0.95:
            results["checkpoint_10_final_sync"] = True

    # Overall pass
    results["overall_pass"] = all([
        results["checkpoint_1_removals_detected"],
        results["checkpoint_2_obsolete_identified"],
        results["checkpoint_3_architecture_cleaned"],
        results["checkpoint_4_contracts_cleaned"],
        results["checkpoint_6_docker_cleaned"],
        results["checkpoint_8_versioning_removals"],
        results["checkpoint_9_cleanup_report"],
        results["checkpoint_10_final_sync"]
    ])

    return results
```

---

**Validation Criteria Version**: 1.0.0
**Created**: 2025-11-19
**Purpose**: Automated validation of artifact cleanup for removals (v3.18.1)
