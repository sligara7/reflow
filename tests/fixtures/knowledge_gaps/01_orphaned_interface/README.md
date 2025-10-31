# Test Case 01: Orphaned Interface

## Purpose

Validate that `system_of_systems_graph_v2.py` detects **orphaned interfaces** - interfaces provided by a service but required by no other service.

## Scenario

**System**: Simple e-commerce platform with 3 services:
- `user_service` - Manages users, provides User Management API
- `product_service` - Manages products, provides Product Catalog API (ORPHANED)
- `order_service` - Manages orders, requires User Management API

**Flaw**: `product_service` provides the Product Catalog API (`IFC-PROD-001`), but **no service requires it**. The `order_service` should logically need product data to create orders, but it doesn't declare this dependency.

## Expected Detection

**Tool**: `python3 tools/system_of_systems_graph_v2.py specs/machine/service_arch_index.json --detect-gaps`

**Expected Output**:
```json
{
  "knowledge_gaps": {
    "orphaned_interfaces": [
      {
        "interface_id": "IFC-PROD-001",
        "interface_name": "Product Catalog API",
        "provider": "product_service",
        "severity": "warning"
      }
    ]
  },
  "knowledge_gaps_summary": {
    "total_gaps": 1,
    "by_type": {
      "orphaned_interfaces": 1
    }
  }
}
```

## Why This Is a Problem

1. **Unused Service**: `product_service` is deployed but never called - wasted resources
2. **Incomplete Architecture**: Orders without products suggests missing dependency
3. **Maintenance Burden**: Orphaned code accumulates technical debt

## How to Fix

**Option 1**: Add dependency to `order_service`:
```json
{
  "required": [
    {
      "interface_id": "IFC-PROD-001",
      "target_service": "product_service"
    }
  ]
}
```

**Option 2**: Remove `product_service` if truly not needed

## Pass Criteria

- Detect exactly 1 orphaned interface
- Interface ID: `IFC-PROD-001`
- Provider: `product_service`
- No other gap types detected
