# Change Proposal: Service Interface Contracts (Embedded Architectural Hooks)

**Date**: 2025-11-19
**Version**: 3.17.0
**Status**: Proposed
**Author**: Reflow Development Team
**Issue**: Proactive drift prevention through embedded service contracts

## Executive Summary

This proposal introduces **Service Interface Contracts** - minimal JSON manifests embedded within each service that act as "architectural hooks" to warn LLMs before making breaking changes to functions or interfaces.

**Problem**: Current architecture synchronization (v3.15.0) detects drift **after it happens**. LLMs can unknowingly modify service functions or interfaces without realizing the downstream impact on dependent services.

**Solution**: Embed a `SERVICE_CONTRACT.json` file in each service's root directory that declares:
- Contracted functions (WHAT the service must implement)
- Contracted interfaces (WHO the service talks to)
- Reference to authoritative architecture (WHERE source of truth lives)
- Warning messages for LLMs (WHY changes require architecture updates)

**Impact**: **Proactive** drift prevention - warns LLMs **BEFORE** changes, not AFTER.

## Background

### Existing Drift Detection Mechanisms

Reflow already has robust drift detection:

1. **Python ABC Contracts** (v3.10.0) - `generate_interface_abc.py`
   - **What**: Language-native interfaces (Python ABC, TypeScript, Rust traits)
   - **When**: Compile-time/runtime type checking
   - **Limitation**: Only validates **type signatures**, not architectural contracts

2. **ICD Verification** (existing) - `verify_component_contract.py`
   - **What**: Validates implementations match Interface Contract Documents
   - **When**: D-04-A06 (integration surfaces), D-07-A07 (pre-deployment)
   - **Limitation**: Only validates **API contracts**, not function completeness

3. **Architecture Synchronization Loop** (v3.15.0) - `version_architecture.py`
   - **What**: Detects drift between as-designed and as-built architecture
   - **When**: D-06 (as-built generation) and D-06.5 (synchronization loop)
   - **Limitation**: **Reactive** - detects drift after implementation is complete

### The Gap: Proactive Prevention

**Missing**: A mechanism to **warn LLMs at the moment they consider making changes** that would violate the architectural contract.

**Example Scenario**:
1. LLM is asked to "add a new endpoint to UserService"
2. LLM implements the endpoint without checking architecture
3. Endpoint duplicates functionality already in AuthService (architectural violation)
4. Drift detected later during D-06, requiring rework

**What We Need**: A **visible, machine-readable contract** that LLMs can read **before** making changes.

## Proposal

### Core Concept

Embed a `SERVICE_CONTRACT.json` file at the root of each service directory that serves as an **architectural contract** between the service implementation and the system architecture.

**File Location**: `services/{service_name}/SERVICE_CONTRACT.json`

**Why Root Directory?**: Maximum visibility - first file LLMs see when examining a service.

### Contract Structure

```json
{
  "service_name": "UserService",
  "contract_version": "1.0.0",
  "contract_date": "2025-11-19",

  "architecture_reference": {
    "service_architecture_file": "specs/machine/service_arch/UserService/service_architecture_v1.0.0.json",
    "graph_node_id": "UserService",
    "graph_file": "specs/machine/graphs/system_of_systems_graph.json",
    "last_architecture_sync": "2025-11-19",
    "architecture_version": "1.0.0"
  },

  "contracted_functions": {
    "functions": [
      {
        "function_id": "F-01",
        "function_name": "CreateUser",
        "description": "Create new user account",
        "source": "Derived from service_architecture.json → components → functions"
      },
      {
        "function_id": "F-02",
        "function_name": "AuthenticateUser",
        "description": "Authenticate user credentials",
        "source": "Derived from service_architecture.json → components → functions"
      }
    ],
    "function_count": 2,
    "warning": "DO NOT add, remove, or substantially modify these functions without updating the functional architecture and regenerating the system of systems graph."
  },

  "contracted_interfaces": {
    "provides": [
      {
        "interface_name": "UserManagementAPI",
        "icd_file": "specs/machine/interfaces/UserManagementAPI_icd.json",
        "consumers": ["WebUI", "AdminService"],
        "breaking_change_impact": "Modifying this interface affects 2 consumer services"
      }
    ],
    "consumes": [
      {
        "interface_name": "EmailNotificationAPI",
        "provider_service": "NotificationService",
        "icd_file": "specs/machine/interfaces/EmailNotificationAPI_icd.json"
      }
    ],
    "provides_count": 1,
    "consumes_count": 1,
    "warning": "DO NOT modify provided interfaces without updating ICDs. All interface changes require re-running systems engineering workflows."
  },

  "llm_warnings": {
    "before_modifying_functions": "⚠️  WARNING: This service has 2 contracted functions. Adding, removing, or substantially changing function behavior requires updating the functional architecture. Run workflow 01d-functional_analysis or 01b/01c to update architecture first.",
    "before_modifying_interfaces": "⚠️  WARNING: This service provides 1 interfaces consumed by 2 services. Interface changes are BREAKING changes. Update ICDs, notify consumers, and re-run systems engineering workflows before making changes.",
    "before_adding_dependencies": "⚠️  WARNING: Adding new service dependencies changes the system architecture. Update the system of systems graph and interface registry before adding imports or API clients.",
    "drift_detection": "If you see differences between this contract and the actual implementation, run D-06 (As-Built Architecture Generation) and D-06.5 (Architecture Synchronization Loop) to reconcile."
  },

  "validation_status": {
    "last_validated": "2025-11-19",
    "validation_tool": "tools/validate_service_contracts.py",
    "validation_result": "passed",
    "deviations_detected": false,
    "deviations": []
  }
}
```

### New Tools

#### 1. `generate_service_contracts.py`

**Purpose**: Generate `SERVICE_CONTRACT.json` files from architecture specifications

**Inputs**:
- `specs/machine/service_arch/{service}/service_architecture_v*.json`
- `specs/machine/graphs/system_of_systems_graph.json`
- `specs/machine/interface_registry.json`

**Outputs**:
- `services/{service}/SERVICE_CONTRACT.json` (for each service)

**Usage**:
```bash
# Generate contracts for all services
python3 tools/generate_service_contracts.py /path/to/system

# Generate contract for single service
python3 tools/generate_service_contracts.py /path/to/system --service UserService
```

**When to Run**:
- **D-02-A05** (new action): After domain model implementation, before integration surfaces
- **D-06.5-A04.5** (new action): When architecture changes during synchronization loop

#### 2. `validate_service_contracts.py`

**Purpose**: Validate implementations match their contracts

**Inputs**:
- `services/{service}/SERVICE_CONTRACT.json`
- `services/{service}/src/` (implementation code)
- `specs/machine/service_arch/{service}/service_architecture_v*.json`

**Outputs**:
- `specs/machine/validation/service_contracts_validation_report.json`

**Validation Checks**:
1. Contract file exists
2. Contract is up-to-date with architecture version
3. Contracted functions are implemented
4. Contracted interfaces have valid ICDs

**Usage**:
```bash
# Validate all services
python3 tools/validate_service_contracts.py /path/to/system

# Validate single service
python3 tools/validate_service_contracts.py /path/to/system --service UserService
```

**When to Run**:
- **D-04-A06.5** (new action): After integration surfaces implementation
- **D-06-A02.5** (new action): After as-built architecture comparison
- **D-07-A07.5** (new action): Pre-deployment validation

### Workflow Integration

#### 1. Generation Point: D-02-A05 (NEW)

**Step**: D-02 Core & Domain Model Realization
**Action ID**: D-02-A05
**Description**: Generate service interface contracts
**When**: After domain model implementation (D-02-A04), before integration surfaces (D-04)

**Rationale**: Generate contracts early (after domain logic, before interfaces) so they're available to warn LLMs during integration surface implementation.

**Workflow Update**:
```json
{
  "action_id": "D-02-A05",
  "description": "Generate service interface contracts",
  "tool": "generate_service_contracts.py",
  "command_pattern": "python3 {reflow_root}/tools/generate_service_contracts.py {system_root} --service {service_name}",
  "purpose": "Embed architectural contract within service to prevent LLM drift",
  "outputs": ["services/{service_name}/SERVICE_CONTRACT.json"],
  "new_in_version": "v3.17.0 - Service Interface Contracts feature"
}
```

#### 2. Validation Points

##### D-04-A06.5 (NEW) - After Integration Surfaces

**When**: After D-04-A06 (verify_component_contract.py), before D-04-A07 (integration tests)

**Purpose**: Validate that integration surfaces (APIs, clients) match contracted interfaces

**Workflow Update**:
```json
{
  "action_id": "D-04-A06.5",
  "description": "Validate service contracts after integration implementation",
  "tool": "validate_service_contracts.py",
  "command_pattern": "python3 {reflow_root}/tools/validate_service_contracts.py {system_root} --service {service_name}",
  "purpose": "Detect contract violations introduced during integration surfaces implementation",
  "blocking": false,
  "enforcement": "STRONGLY RECOMMENDED to fix violations before proceeding"
}
```

##### D-06-A02.5 (NEW) - After As-Built Comparison

**When**: After D-06-A02 (compare as-built to as-designed), before D-06-A03 (review delta)

**Purpose**: Validate contracts against as-built architecture

**Workflow Update**:
```json
{
  "action_id": "D-06-A02.5",
  "description": "Validate service contracts against as-built architecture",
  "tool": "validate_service_contracts.py",
  "command_pattern": "python3 {reflow_root}/tools/validate_service_contracts.py {system_root}",
  "purpose": "Detect contract drift revealed by as-built architecture analysis",
  "outputs": ["specs/machine/validation/service_contracts_validation_report.json"]
}
```

##### D-07-A07.5 (NEW) - Pre-Deployment Validation

**When**: After D-07-A07 (verify_component_contract.py --strict), before D-Post

**Purpose**: Final validation that contracts are satisfied before operational testing

**Workflow Update**:
```json
{
  "action_id": "D-07-A07.5",
  "description": "Final service contract validation before deployment",
  "tool": "validate_service_contracts.py",
  "command_pattern": "python3 {reflow_root}/tools/validate_service_contracts.py {system_root}",
  "purpose": "Final pre-deployment check that all contracts are satisfied",
  "blocking": true,
  "enforcement": "Must pass before proceeding to operational testing"
}
```

#### 3. Update Point: D-06.5-A04.5 (NEW)

**Step**: D-06.5 Architecture Synchronization & Versioning Loop
**Action ID**: D-06.5-A04.5
**Description**: Regenerate service contracts when architecture changes
**When**: After D-06.5-A04 (version_architecture.py), before D-06.5-A05 (re-validate)

**Rationale**: When architecture changes, contracts must be regenerated to reflect new reality.

**Workflow Update**:
```json
{
  "action_id": "D-06.5-A04.5",
  "description": "Regenerate service contracts after architecture update",
  "tool": "generate_service_contracts.py",
  "command_pattern": "python3 {reflow_root}/tools/generate_service_contracts.py {system_root}",
  "purpose": "Update embedded contracts to match updated architecture",
  "when": "After architecture versioning (D-06.5-A04), before re-validation (D-06.5-A05)"
}
```

### Template

**New Template**: `templates/service_contract_template.json`

Contains metadata structure and placeholder values for contract generation.

## Benefits

### 1. Proactive Drift Prevention

**Before**: LLM makes change → Drift detected in D-06 → Rework required
**After**: LLM reads contract → Sees warning → Updates architecture first → No drift

**Time Saved**: 2-4 hours per service (average drift reconciliation time)

### 2. LLM-Friendly Documentation

**What Makes It LLM-Friendly**:
- **Highly visible**: Root directory, named `SERVICE_CONTRACT.json`
- **Machine-readable**: JSON format, easy to parse
- **Explicit warnings**: `llm_warnings` section with context-specific messages
- **Actionable**: Points to exact workflows to run (`01d-functional_analysis`, `01b`, `01c`)

**Example LLM Interaction**:
```
User: "Add a new endpoint to UserService"

LLM: *Reads SERVICE_CONTRACT.json*
LLM: "I see UserService has 2 contracted functions and provides 1 interface
      consumed by 2 services. Before adding an endpoint, I should:
      1. Check if this function is already contracted
      2. Update functional architecture (workflow 01d or 01b/01c)
      3. Regenerate system graph
      4. Regenerate this contract

      Would you like me to do this, or just add the endpoint directly?"
```

### 3. Complements Existing Tools

**Does NOT Replace**:
- Python ABC contracts (type-level validation)
- ICD verification (API contract compliance)
- Architecture synchronization (post-facto drift detection)

**Adds**: **Intent-level validation** - "Should I be making this change at all?"

### 4. Minimal Overhead

**Contract Size**: ~2-5KB per service (minimal)
**Generation Time**: <1 second per service
**Validation Time**: 5-10 seconds per service (AST parsing)

**Total Overhead**: 1-2 minutes for 8-service system

## Risks & Mitigation

### Risk 1: Contract Staleness

**Risk**: Contracts become out-of-sync with architecture as changes occur

**Mitigation**:
- Automatic regeneration in D-06.5 (architecture synchronization loop)
- Validation checks contract freshness against architecture version
- Warning messages prompt LLMs to regenerate if stale

### Risk 2: False Positives in Validation

**Risk**: Fuzzy function matching may miss implementations

**Mitigation**:
- Fuzzy matching (case-insensitive, partial match)
- Validation is non-blocking by default (warnings, not errors)
- Manual review of validation reports

### Risk 3: LLMs Ignoring Warnings

**Risk**: LLMs may not read contracts before making changes

**Mitigation**:
- Highly visible location (root directory)
- Explicit instructions in CLAUDE.md to check contracts
- Validation gates catch violations even if warnings ignored

## Implementation Plan

### Phase 1: Core Implementation (Current)

- [x] Create `service_contract_template.json`
- [x] Create `generate_service_contracts.py` tool
- [x] Create `validate_service_contracts.py` tool
- [ ] Update workflows via `98-reflow_feature_update.json`:
  - [ ] Add D-02-A05 (generate contracts)
  - [ ] Add D-04-A06.5 (validate after integration)
  - [ ] Add D-06-A02.5 (validate after as-built)
  - [ ] Add D-06.5-A04.5 (regenerate on architecture update)
  - [ ] Add D-07-A07.5 (final pre-deployment validation)
- [ ] Update CLAUDE.md documentation

### Phase 2: Testing (Future)

- [ ] Add test case to `tests/test_systems/` for contract validation
- [ ] Test contract generation on microservices_basic test system
- [ ] Validate contract validation catches known drift scenarios

### Phase 3: Documentation (Future)

- [ ] Create `docs/SERVICE_CONTRACTS_GUIDE.md`
- [ ] Add examples to `templates/examples/`
- [ ] Update `docs/TOOL_USAGE_SUMMARY.md`

## Backwards Compatibility

**Fully Backwards Compatible**:
- Contracts are **additive** - no existing functionality removed
- Validation is **non-blocking** by default (warnings only)
- Services without contracts continue to work normally
- No changes to existing architecture files required

**Migration Path**:
- Existing systems: Run `generate_service_contracts.py` to create contracts
- New systems: Contracts generated automatically in D-02-A05

## Success Metrics

1. **Drift Reduction**: Measure architectural drift incidents (similarity < 0.95) in D-06
   - **Target**: 30% reduction in drift incidents

2. **LLM Awareness**: Measure how often LLMs mention contracts in responses
   - **Target**: 70% of service modification requests mention contract check

3. **Time Savings**: Measure time spent in D-06.5 architecture reconciliation
   - **Target**: 25% reduction in reconciliation time

4. **Adoption**: Measure contract generation in new projects
   - **Target**: 90% of new systems generate contracts in D-02

## Alternatives Considered

### Alternative 1: Embed Warnings in README.md

**Why Rejected**: Unstructured, not machine-readable, easy to overlook

### Alternative 2: Require Contract Approval Before Implementation

**Why Rejected**: Too heavyweight, slows down development

### Alternative 3: Runtime Contract Enforcement

**Why Rejected**: Out of scope - this is architecture validation, not runtime validation

## Conclusion

Service Interface Contracts provide a lightweight, LLM-friendly mechanism for **proactive** architectural drift prevention. By embedding contracts directly in service directories, we create visible "hooks" that warn LLMs before they make breaking changes.

**Key Value Proposition**: **Prevent drift before it happens, not after.**

## References

- **v3.10.0**: Language-Native Interface Contracts (`generate_interface_abc.py`)
- **v3.15.0**: Architecture Synchronization Loop (`version_architecture.py`)
- **v3.16.0**: Testing Framework (GAN-inspired validation)
- **CLAUDE.md**: LLM agent guide

---

**Approval**: Pending
**Implementation**: In Progress
**Version**: 3.17.0
