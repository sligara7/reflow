# Architecture Drift & Sync Test - Validation Criteria

**Test Case**: TC-002 (architecture_drift_sync)
**Purpose**: Automated validation of Agent B's architecture synchronization behavior

---

## Validation Checkpoints

### ✅ Checkpoint 1: Drift Detection (D-06)

**Files to Check**:
- `actual_outputs/D-06-comparison-report.json` OR similar drift detection output

**Validation Rules**:
```python
{
  "checkpoint": "drift_detection",
  "required_files": ["D-06-comparison-report.json"],
  "required_fields": {
    "similarity_score": {
      "type": "number",
      "range": [0.0, 1.0],
      "expected": "< 0.95",
      "critical": "< 0.7 triggers MANDATORY sync"
    },
    "differences_detected": {
      "type": "array",
      "min_length": 3,
      "expected_contains": [
        "RefundPayment function added",
        "payment_status_query interface added",
        "ValidateOrderUniqueness function added"
      ]
    },
    "drift_detected": {
      "type": "boolean",
      "expected": true
    }
  },
  "success_criteria": {
    "similarity_calculated": true,
    "similarity_below_threshold": true,
    "differences_identified": true,
    "agent_b_recognizes_drift": true
  }
}
```

**Agent A Analysis**:
- ✅ Did Agent B run comparison at D-06? (Yes/No)
- ✅ Did Agent B calculate similarity correctly? (Number)
- ✅ Did Agent B identify drift? (Yes/No)
- ❌ Did Agent B skip to D-07 without sync? (Failure mode)

---

### ✅ Checkpoint 2: Synchronization Triggered (D-06.5 Entry)

**Files to Check**:
- `actual_outputs/D-06.5-sync-initiated.json` OR Agent B transcript

**Validation Rules**:
```python
{
  "checkpoint": "sync_triggered",
  "evidence_required": [
    "Agent B explicitly states entering D-06.5 workflow",
    "Agent B does NOT proceed directly to D-07",
    "Agent B acknowledges similarity < threshold"
  ],
  "success_criteria": {
    "d_06_5_triggered": true,
    "automatic_not_manual": true,
    "agent_b_follows_workflow": true
  }
}
```

**Agent A Analysis**:
- ✅ Did Agent B trigger D-06.5? (Yes/No)
- ✅ Was it automatic or did Agent B need prompting? (Automatic/Manual/Prompted)
- ❌ Did Agent B skip D-06.5? (Failure mode)

---

### ✅ Checkpoint 3: Root Cause Classification (D-06.5-A01)

**Files to Check**:
- `actual_outputs/drift_root_cause_analysis.json`

**Validation Rules**:
```python
{
  "checkpoint": "root_cause_classification",
  "required_file": "drift_root_cause_analysis.json",
  "expected_classifications": [
    {
      "change": "RefundPayment function added",
      "root_cause_category": "operational_reality",
      "rationale": "Discovered during testing - business logic requirement"
    },
    {
      "change": "payment_status_query interface added",
      "root_cause_category": "requirements_creep",
      "rationale": "Incomplete initial requirements - stakeholder feedback"
    },
    {
      "change": "ValidateOrderUniqueness function added",
      "root_cause_category": "technical_constraints",
      "rationale": "Race condition prevention - concurrency handling"
    }
  ],
  "success_criteria": {
    "all_changes_classified": true,
    "categories_appropriate": true,
    "rationale_specific_not_generic": true
  }
}
```

**Agent A Analysis**:
- ✅ Did Agent B classify all 3 changes? (Count)
- ✅ Were categories appropriate? (Good/Fair/Poor)
- ✅ Was rationale specific? (Yes/No)

---

### ✅ Checkpoint 4: Functional Architecture Updated (D-06.5-A02)

**Files to Check**:
- `actual_outputs/specs/functional/functional_architecture_v1.1.0.json`

**Validation Rules**:
```python
{
  "checkpoint": "functional_architecture_updated",
  "required_file": "specs/functional/functional_architecture_v1.1.0.json",
  "expected_changes": {
    "functions_count": {
      "before": 5,
      "after": 8,  # Added RefundPayment, ValidateOrderUniqueness, GetPaymentStatus
      "delta": 3
    },
    "new_functions": [
      {
        "function_id": "F-06",
        "name": "RefundPayment",
        "dependencies": []
      },
      {
        "function_id": "F-07",
        "name": "ValidateOrderUniqueness",
        "dependencies": []
      },
      {
        "function_id": "F-08",
        "name": "GetPaymentStatus",
        "dependencies": []
      }
    ],
    "modified_functions": [
      {
        "function_id": "F-03",
        "name": "CancelOrder",
        "new_dependencies": ["F-06"]  # Now depends on RefundPayment
      },
      {
        "function_id": "F-02",
        "name": "GetOrderStatus",
        "new_dependencies": ["F-08"]  # Now depends on GetPaymentStatus
      },
      {
        "function_id": "F-01",
        "name": "CreateOrder",
        "new_dependencies": ["F-07"]  # Now depends on ValidateOrderUniqueness
      }
    ]
  },
  "success_criteria": {
    "version_incremented": "1.0.0 -> 1.1.0",
    "new_functions_added": true,
    "dependencies_updated": true,
    "flows_updated": true
  }
}
```

**Agent A Analysis**:
- ✅ Was functional_architecture.json updated? (Yes/No)
- ✅ Were all 3 new functions added? (Count)
- ✅ Were dependencies updated for affected functions? (Yes/No)
- ✅ Was version incremented correctly? (Yes/No)

---

### ✅ Checkpoint 5: Service Architecture Updated (D-06.5-A03)

**Files to Check**:
- `actual_outputs/specs/machine/service_arch/OrderService/service_architecture_v1.1.0.json`
- `actual_outputs/specs/machine/service_arch/PaymentService/service_architecture_v1.1.0.json`
- `actual_outputs/specs/machine/interface_registry_v1.1.0.json`

**Validation Rules**:
```python
{
  "checkpoint": "service_architecture_updated",
  "required_files": [
    "service_arch/OrderService/service_architecture_v1.1.0.json",
    "service_arch/PaymentService/service_architecture_v1.1.0.json",
    "interface_registry_v1.1.0.json"
  ],
  "expected_changes": {
    "OrderService": {
      "allocated_functions": {
        "before": 3,  # CreateOrder, GetOrderStatus, CancelOrder
        "after": 4,   # + ValidateOrderUniqueness
        "added": ["ValidateOrderUniqueness"]
      }
    },
    "PaymentService": {
      "allocated_functions": {
        "before": 2,  # ProcessPayment, SendOrderConfirmation
        "after": 4,   # + RefundPayment, GetPaymentStatus
        "added": ["RefundPayment", "GetPaymentStatus"]
      }
    },
    "interface_registry": {
      "interfaces_count": {
        "before": 1,  # payment_processing
        "after": 2,   # + payment_status_query
        "added": ["payment_status_query"]
      }
    }
  },
  "success_criteria": {
    "all_services_updated": true,
    "functions_correctly_allocated": true,
    "interfaces_added": true,
    "versions_consistent": true
  }
}
```

**Agent A Analysis**:
- ✅ Were both service architectures updated? (Yes/No)
- ✅ Were new functions allocated correctly? (Yes/No)
- ✅ Was interface_registry updated? (Yes/No)
- ✅ Are versions consistent across files? (Yes/No)

---

### ✅ Checkpoint 6: Versioning Applied (D-06.5-A04)

**Files to Check**:
- `actual_outputs/specs/functional/version_history.json`
- `actual_outputs/specs/machine/service_arch/*/version_history.json`

**Validation Rules**:
```python
{
  "checkpoint": "versioning_applied",
  "required_tool": "version_architecture.py",
  "required_files": [
    "specs/functional/version_history.json",
    "specs/machine/service_arch/OrderService/version_history.json",
    "specs/machine/service_arch/PaymentService/version_history.json"
  ],
  "expected_version_history": {
    "version": "1.1.0",
    "previous_version": "1.0.0",
    "date": "{CURRENT_DATE}",
    "change_type": "minor",
    "changes_summary": "Added RefundPayment, GetPaymentStatus, ValidateOrderUniqueness functions; added payment_status_query interface",
    "root_causes": [
      {
        "category": "operational_reality",
        "description": "RefundPayment - discovered during testing"
      },
      {
        "category": "requirements_creep",
        "description": "payment_status_query - incomplete initial requirements"
      },
      {
        "category": "technical_constraints",
        "description": "ValidateOrderUniqueness - race condition prevention"
      }
    ],
    "rationale": "Testing phase revealed gaps in original architecture. Implementation evolved to handle refunds, payment status queries, and concurrent order creation.",
    "approved_by": "Agent B",
    "sign_off_date": "{CURRENT_DATE}"
  },
  "success_criteria": {
    "version_architecture_tool_used": true,
    "version_history_complete": true,
    "root_causes_documented": true,
    "rationale_provided": true,
    "semantic_versioning_correct": true
  }
}
```

**Agent A Analysis**:
- ✅ Was version_architecture.py used? (Yes/No)
- ✅ Is version history complete? (Yes/No)
- ✅ Are root causes documented? (Yes/No)
- ✅ Is rationale specific and clear? (Yes/No)
- ❌ Was versioning manual (without tool)? (Failure mode)

---

### ✅ Checkpoint 7: Re-Validation & Iteration (D-06.5-A05/A06)

**Files to Check**:
- `actual_outputs/D-06.5-revalidation-report.json`

**Validation Rules**:
```python
{
  "checkpoint": "revalidation",
  "required_file": "D-06.5-revalidation-report.json",
  "expected_behavior": {
    "similarity_recalculated": true,
    "new_similarity_score": {
      "type": "number",
      "expected": ">= 0.95"
    },
    "iterations_count": {
      "type": "number",
      "expected": "1-2",
      "max_acceptable": 3
    },
    "final_status": "SYNCHRONIZED"
  },
  "success_criteria": {
    "agent_b_revalidated": true,
    "similarity_meets_threshold": true,
    "iteration_occurred": true,
    "proceeded_only_after_sync": true
  }
}
```

**Agent A Analysis**:
- ✅ Did Agent B re-calculate similarity? (Yes/No)
- ✅ What was final similarity score? (Number)
- ✅ How many iterations? (Count)
- ✅ Did Agent B proceed only after >= 0.95? (Yes/No)
- ❌ Did Agent B skip re-validation? (Failure mode)

---

### ✅ Checkpoint 8: Final Quality Gate (D-Post-A02)

**Files to Check**:
- `actual_outputs/D-Post-A02-final-sync-verification.json`

**Validation Rules**:
```python
{
  "checkpoint": "final_quality_gate",
  "required_file": "D-Post-A02-final-sync-verification.json",
  "expected_result": {
    "architecture_synchronized": true,
    "similarity_score": ">= 0.95",
    "version_history_complete": true,
    "all_drift_documented": true,
    "gate_status": "PASS"
  },
  "success_criteria": {
    "final_gate_executed": true,
    "gate_passed": true,
    "deployment_allowed": true
  }
}
```

**Agent A Analysis**:
- ✅ Was D-Post-A02 gate executed? (Yes/No)
- ✅ Did gate pass? (Yes/No)
- ✅ Is architecture fully synchronized? (Yes/No)

---

## Overall Test Success Criteria

### Must Pass (P0)

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

### Should Pass (P1)

- [x] Root cause categories appropriate and specific
- [x] Version history comprehensive and clear
- [x] Iterations <= 2 (efficient synchronization)
- [x] Time to complete sync <= 30 minutes
- [x] All documentation traces test failure → fix → architecture update

### Nice to Have (P2)

- [ ] Automated detection (no manual prompting needed)
- [ ] Proactive architecture updates during fix implementation
- [ ] Clear signoffs and approvals in version history

---

## Failure Modes to Detect

### Critical Failures (Test FAILS)

❌ Agent B skips D-06 drift detection entirely
❌ Agent B detects drift but proceeds to D-07 without sync
❌ Agent B updates architecture manually without D-06.5 workflow
❌ Agent B doesn't use version_architecture.py tool
❌ Final similarity < 0.95 but gate passes anyway

### Warning Failures (Test PASSES but with warnings)

⚠️ Agent B needs manual prompting to trigger D-06.5
⚠️ Iterations > 2 (inefficient synchronization)
⚠️ Root causes generic or missing
⚠️ Time > 30 minutes to complete sync

---

## Automated Validation Script

Agent A should use this logic:

```python
def validate_architecture_drift_test(actual_outputs_dir):
    results = {
        "checkpoint_1_drift_detected": False,
        "checkpoint_2_sync_triggered": False,
        "checkpoint_3_root_causes_classified": False,
        "checkpoint_4_functional_arch_updated": False,
        "checkpoint_5_service_arch_updated": False,
        "checkpoint_6_versioning_applied": False,
        "checkpoint_7_revalidated": False,
        "checkpoint_8_final_gate_passed": False,
        "overall_pass": False
    }

    # Checkpoint 1: Drift Detection
    if exists("D-06-comparison-report.json"):
        report = load_json("D-06-comparison-report.json")
        if report.get("similarity_score") < 0.95:
            results["checkpoint_1_drift_detected"] = True

    # Checkpoint 2: Sync Triggered
    if agent_b_transcript_contains("D-06.5") or agent_b_transcript_contains("synchronization"):
        results["checkpoint_2_sync_triggered"] = True

    # Checkpoint 3: Root Causes
    if exists("drift_root_cause_analysis.json"):
        root_causes = load_json("drift_root_cause_analysis.json")
        if len(root_causes.get("changes", [])) >= 3:
            results["checkpoint_3_root_causes_classified"] = True

    # Checkpoint 4: Functional Architecture
    if exists("specs/functional/functional_architecture_v1.1.0.json"):
        func_arch = load_json("functional_architecture_v1.1.0.json")
        if len(func_arch.get("functions", [])) >= 8:
            results["checkpoint_4_functional_arch_updated"] = True

    # Checkpoint 5: Service Architecture
    if (exists("service_arch/OrderService/service_architecture_v1.1.0.json") and
        exists("service_arch/PaymentService/service_architecture_v1.1.0.json") and
        exists("interface_registry_v1.1.0.json")):
        results["checkpoint_5_service_arch_updated"] = True

    # Checkpoint 6: Versioning
    if exists("specs/functional/version_history.json"):
        version_history = load_json("version_history.json")
        if version_history.get("version") == "1.1.0":
            results["checkpoint_6_versioning_applied"] = True

    # Checkpoint 7: Revalidation
    if exists("D-06.5-revalidation-report.json"):
        revalidation = load_json("D-06.5-revalidation-report.json")
        if revalidation.get("similarity_score") >= 0.95:
            results["checkpoint_7_revalidated"] = True

    # Checkpoint 8: Final Gate
    if exists("D-Post-A02-final-sync-verification.json"):
        final_gate = load_json("D-Post-A02-final-sync-verification.json")
        if final_gate.get("gate_status") == "PASS":
            results["checkpoint_8_final_gate_passed"] = True

    # Overall Pass
    results["overall_pass"] = all([
        results["checkpoint_1_drift_detected"],
        results["checkpoint_2_sync_triggered"],
        results["checkpoint_4_functional_arch_updated"],
        results["checkpoint_5_service_arch_updated"],
        results["checkpoint_6_versioning_applied"],
        results["checkpoint_7_revalidated"],
        results["checkpoint_8_final_gate_passed"]
    ])

    return results
```

---

**Validation Criteria Version**: 1.0.0
**Created**: 2025-11-19
**Purpose**: Automated and manual validation of architecture synchronization loop
