# Test Case 02: Unmet Dependency

## Purpose

Validate that `system_of_systems_graph_v2.py` detects **unmet dependencies** - interfaces required by a service but provided by no service.

## Scenario

**System**: Payment processing platform with 2 services:
- `payment_service` - Processes payments, requires Billing API (MISSING)
- `notification_service` - Sends notifications (independent)

**Flaw**: `payment_service` requires the Billing API (`IFC-BILL-001`) from `billing_service`, but **billing_service doesn't exist**.

## Expected Detection

**Tool**: `python3 tools/system_of_systems_graph_v2.py specs/machine/service_arch_index.json --detect-gaps`

**Expected Output**:
```json
{
  "knowledge_gaps": {
    "unmet_dependencies": [
      {
        "interface_id": "IFC-BILL-001",
        "interface_name": "Billing API",
        "requester": "payment_service",
        "severity": "error"
      }
    ]
  }
}
```

## Why This Is a Problem

1. **Runtime Failure**: `payment_service` will fail when trying to call non-existent billing_service
2. **Incomplete System**: Missing critical component for core functionality
3. **Deployment Blocker**: Cannot deploy system as-is

## How to Fix

**Create billing_service**:
```json
{
  "service_id": "billing_service",
  "interfaces": {
    "provided": [{
      "interface_id": "IFC-BILL-001",
      "interface_name": "Billing API"
    }]
  }
}
```

## Pass Criteria

- Detect exactly 1 unmet dependency
- Interface ID: `IFC-BILL-001`
- Requester: `payment_service`
- Severity: error
