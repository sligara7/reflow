# Workflow Step Test: Port Management - UAF

## Workflow Step

**SE-02-A04**: Port Assignment and Registry Creation

## Framework

**UAF 1.2** (IT systems)

## Purpose

Validate that SE-02-A04 **executes** for UAF framework and creates `port_registry.json`.

## Conditional Logic

**Condition**: `framework_registry['uaf']['deployment_characteristics']['port_management_applicable'] == true`

**Action**: If true, execute SE-02-A04 (assign ports, create port_registry.json)

## Scenario

**System**: Simple UAF IT system with 2 services:
- `api_service` (application) → port 8000
- `database` (PostgreSQL) → port 5432

## Expected Behavior

**Step SE-02-A04 should**:
1. Check `port_management_applicable` → TRUE for UAF
2. Assign ports based on service type
   - Application services: 8000-8099 range
   - Database services: standard ports (5432 for PostgreSQL)
3. Create `specs/machine/port_registry.json` with:
   ```json
   {
     "ports": [
       {"service_id": "api_service", "primary_port": 8000},
       {"service_id": "database", "primary_port": 5432}
     ]
   }
   ```
4. Update each `service_architecture.json` with assigned port
5. Validate no port conflicts

## Pass Criteria

- `port_registry.json` **exists** in `specs/machine/`
- Contains entries for both services
- No duplicate port assignments
- Ports match service type ranges

## Related Tests

- `port_management_biology` - Same workflow, different framework → SE-02-A04 skipped
