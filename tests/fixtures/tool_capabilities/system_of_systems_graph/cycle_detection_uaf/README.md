# Framework-Specific Test: Cycle Detection - UAF

## Framework

**UAF 1.2** (Unified Architecture Framework)

## Purpose

Validate that circular dependencies in UAF systems are detected with **ERROR** severity.

## Scenario

**System**: Authentication microservices with circular dependency:

```
auth_service → user_service → session_service → auth_service
```

**Circular Dependency**:
- `auth_service` requires `user_service` (to validate user exists)
- `user_service` requires `session_service` (to manage user sessions)
- `session_service` requires `auth_service` (to validate session auth)

## Why This Is Bad (UAF Context)

In UAF/IT systems, circular dependencies cause:
1. **Build Failures**: Can't determine which service to build first
2. **Deployment Issues**: Can't start services in correct order
3. **Tight Coupling**: Changes in one service cascade to others
4. **Testing Complexity**: Can't unit test services independently

**Clean Architecture Violation**: Services should depend on abstractions, not concrete implementations.

## Expected Detection

**Command**:
```bash
python3 tools/system_of_systems_graph_v2.py \
  specs/machine/service_arch_index.json \
  --framework uaf \
  --cycles \
  --output detected_output.json
```

**Expected Output**:
```json
{
  "graph_analysis": {
    "cycles": {
      "detected": true,
      "count": 1,
      "cycles": [
        ["auth_service", "user_service", "session_service", "auth_service"]
      ],
      "severity": "error",
      "interpretation": "Circular dependencies violate clean architecture",
      "recommendation": "Refactor to break cycle - consider dependency injection or event-driven architecture"
    }
  }
}
```

## Mitigation Strategies

1. **Dependency Inversion**: Introduce interface/abstraction layer
2. **Event-Driven**: Replace synchronous calls with async events
3. **Service Consolidation**: Merge tightly coupled services
4. **API Gateway Pattern**: Centralized routing breaks direct dependencies

## Pass Criteria

- Cycle detected (auth → user → session → auth)
- Severity: **ERROR** (not warning or info)
- Tool completes successfully
- Recommendation provided for remediation

## Related Tests

- `cycle_detection_biology` - Same cycle, INFO severity (feedback loops expected)
- `cycle_detection_decision_flow` - Rework loops, WARNING severity
- `dag_validation_uaf` - Validates DAG property (should fail with cycles)
