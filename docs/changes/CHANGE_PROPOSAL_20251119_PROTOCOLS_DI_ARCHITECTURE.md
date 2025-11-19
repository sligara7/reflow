# Change Proposal: Protocol-Based Interfaces, Dependency Injection, and Service Organization Strategies

**Date**: 2025-11-19
**Proposal ID**: CP-2025-11-19-001
**Feature**: Protocol-based interfaces + Dependency Injection + Service Organization Strategies
**Priority**: High
**Workflow Version**: 3.17.0 → 3.18.0

## Executive Summary

Add **Protocol-based interfaces with dependency injection** as the **recommended default** for service architectures, while maintaining ABC support for backward compatibility. Introduce **service organization strategy choice** (domain-based vs workflow-based) during architecture design. Provide **behavior mixin templates** for wide inheritance patterns.

This modernizes Reflow's architectural patterns to support:
- Multi-facility deployments with different implementations
- Framework integration without metaclass conflicts
- Better testability through dependency injection
- Flexible service organization aligned with system characteristics

## Business Justification

### Current State

Reflow v3.10.0 introduced ABC interface generation (`generate_interface_abc.py`), but ABCs have limitations:

1. **Metaclass Conflicts**: ABCs consume the metaclass slot, conflicting with:
   - FastAPI dependency injection metaclasses
   - SQLAlchemy ORM metaclasses
   - Pydantic model metaclasses
   - Domain-specific framework metaclasses (EPICS/Ophyd, scientific computing)

2. **Inheritance Coupling**: All implementations must inherit from ABC, preventing:
   - Multiple implementations without common base class
   - Clean separation of interface and implementation
   - Third-party implementations that don't know about your ABC

3. **Single Service Organization**: Reflow currently defaults to domain-based service organization, but complex coordination requirements often benefit from workflow-based organization

### Proposed Solution

1. **Protocol-based Interfaces** (Python Protocols, TypeScript interfaces, Rust traits)
   - Structural typing - no inheritance required
   - No metaclass conflicts
   - Multiple implementations without coupling

2. **Dependency Injection**
   - Services declare WHAT they need (via Protocol type hints)
   - Startup code provides concrete implementations
   - Easy swapping of implementations (prod/test/facility-specific)

3. **Service Organization Strategy Choice**
   - Domain-based (traditional) - group by business domain
   - Workflow-based (modern) - group by user workflows
   - Hybrid - combine both strategies
   - LLM analyzes system and recommends strategy

4. **Wide Inheritance with Behavior Mixins**
   - Reusable behavior components (HasLifecycle, HasLogging, RequiresAuth, TracksMetrics)
   - Shallow hierarchies (depth = 1) instead of deep chains
   - Compose services from multiple mixins

### Impact

**Time Savings**: 5-10 days per system
- Multi-facility: Different implementations without code changes (3-5 days)
- Testing: Easy mocking with Protocol implementations (1-2 days)
- Coordination: Workflow-based organization reduces distributed state complexity (2-3 days)

**Quality Improvement**:
- No metaclass conflicts with frameworks
- Clear dependency graphs (explicit in constructors)
- Better testability (inject mocks)
- Flexible service organization (choose based on system characteristics)

## Feature Description

### 1. New Tool: `generate_interface_protocols.py`

**Purpose**: Generate Protocol-based interfaces + DI setup from system_of_systems_graph.json

**Inputs**:
- `specs/machine/graphs/system_of_systems_graph.json` (edges = interfaces)
- `specs/machine/development_language_configuration.json` (language per service)
- `specs/machine/interfaces/{interface}_icd.json` (detailed interface specs)

**Outputs**:
```
services/common/
  ├── protocols/
  │   ├── can_execute_plans.py              # Protocol definition
  │   ├── provides_device_registry.py       # Protocol definition
  │   └── handles_authentication.py         # Protocol definition
  ├── mixins/
  │   ├── has_lifecycle.py                  # Behavior mixin
  │   ├── has_logging.py                    # Behavior mixin
  │   ├── requires_auth.py                  # Behavior mixin
  │   └── tracks_metrics.py                 # Behavior mixin
  └── di/
      ├── container.py                      # DI container
      └── dependencies.py                   # FastAPI dependencies (if using FastAPI)
```

**Example Output (Protocol)**:
```python
# services/common/protocols/can_execute_plans.py
from typing import Protocol, runtime_checkable

@runtime_checkable
class CanExecutePlans(Protocol):
    """
    Interface: Anything that can execute plans

    Provider services implement this interface to expose plan execution capabilities.
    Consumer services depend on this interface (not concrete implementations).

    Generated from: system_of_systems_graph.json
    ICDs: execution_api_icd.json
    """

    def submit_plan(self, plan_name: str, params: dict) -> str:
        """
        Submit a plan for execution

        Args:
            plan_name: Name of the plan to execute (required)
            params: Plan parameters as key-value pairs

        Returns:
            Plan execution ID (UUID string)

        Raises:
            PlanNotFoundException: If plan_name not found
            ValidationError: If params invalid for plan
            DeviceUnavailableError: If required devices busy
        """
        ...

    def is_device_available(self, device: str) -> bool:
        """
        Check if device is available for use

        Args:
            device: Device name to check

        Returns:
            True if device available, False if in use
        """
        ...
```

**Example Output (Behavior Mixin)**:
```python
# services/common/mixins/has_lifecycle.py
import asyncio
import logging
from typing import Optional

class HasLifecycle:
    """
    Mixin: Provides start/stop lifecycle management

    Services that inherit from this mixin get:
    - start() method to initialize the service
    - stop() method to gracefully shutdown
    - _on_start() hook for custom startup logic
    - _on_stop() hook for custom cleanup logic

    Usage:
        class MyService(HasLifecycle, OtherMixins):
            async def _on_start(self):
                # Custom startup logic
                await self._connect_to_database()

            async def _on_stop(self):
                # Custom cleanup logic
                await self._close_connections()
    """

    def __init__(self):
        self._started: bool = False
        self._logger: Optional[logging.Logger] = None

    async def start(self):
        """Start the service"""
        if self._started:
            return

        self._logger = logging.getLogger(self.__class__.__name__)
        self._logger.info(f"Starting {self.__class__.__name__}")

        self._started = True
        await self._on_start()

        self._logger.info(f"{self.__class__.__name__} started successfully")

    async def stop(self):
        """Stop the service gracefully"""
        if not self._started:
            return

        self._logger.info(f"Stopping {self.__class__.__name__}")

        await self._on_stop()
        self._started = False

        self._logger.info(f"{self.__class__.__name__} stopped")

    async def _on_start(self):
        """
        Override this method for custom startup logic

        Called by start() after basic initialization.
        """
        pass

    async def _on_stop(self):
        """
        Override this method for custom cleanup logic

        Called by stop() before final shutdown.
        """
        pass

    @property
    def is_started(self) -> bool:
        """Check if service is started"""
        return self._started
```

**Example Output (DI Container)**:
```python
# services/common/di/container.py
from typing import Dict, Any
from ..protocols.can_execute_plans import CanExecutePlans
from ..protocols.provides_device_registry import ProvidesDeviceRegistry
from ..protocols.handles_authentication import HandlesAuthentication

class ServiceContainer:
    """
    Dependency Injection Container

    Wires services together by providing concrete implementations
    for Protocol-based interfaces.

    Usage:
        # Startup
        config = load_config()
        container = ServiceContainer(config)
        await container.start_all()

        # Access services
        executor = container.get_executor()
        registry = container.get_registry()
    """

    def __init__(self, config: Dict[str, Any]):
        self._config = config
        self._services: Dict[str, Any] = {}
        self._build_services()

    def _build_services(self):
        """Build and wire services based on configuration"""
        # Import implementations based on config
        # This allows different implementations per environment

        if self._config.get("executor_type") == "queueserver":
            from services.execution.queueserver_executor import QueueServerExecutor
            executor_class = QueueServerExecutor
        elif self._config.get("executor_type") == "blueapi":
            from services.execution.blueapi_executor import BlueAPIExecutor
            executor_class = BlueAPIExecutor
        else:
            raise ValueError(f"Unknown executor_type: {self._config.get('executor_type')}")

        # Build services with dependencies injected
        registry = YAMLDeviceRegistry(self._config["registry_path"])

        auth = OAuth2AuthProvider(
            issuer=self._config["auth"]["issuer"],
            audience=self._config["auth"]["audience"]
        )

        executor = executor_class(
            config=self._config["executor"],
            registry=registry,
            auth=auth
        )

        self._services = {
            "executor": executor,
            "registry": registry,
            "auth": auth
        }

    async def start_all(self):
        """Start all services in dependency order"""
        # Start in order: registry → auth → executor
        for service in self._services.values():
            if hasattr(service, "start"):
                await service.start()

    async def stop_all(self):
        """Stop all services in reverse dependency order"""
        # Stop in reverse order
        for service in reversed(list(self._services.values())):
            if hasattr(service, "stop"):
                await service.stop()

    def get_executor(self) -> CanExecutePlans:
        """Get executor service"""
        return self._services["executor"]

    def get_registry(self) -> ProvidesDeviceRegistry:
        """Get registry service"""
        return self._services["registry"]

    def get_auth(self) -> HandlesAuthentication:
        """Get auth service"""
        return self._services["auth"]
```

### 2. Service Organization Strategy Choice

**New Action: SE-02-A01.5 - Service Decomposition Strategy**

Before allocating functions to services (SE-02-A02), LLM analyzes system and asks user to choose:

```
ANALYSIS: Service Organization Strategy

Based on your system's characteristics:

1. Coordination Complexity: HIGH
   - Found 3 functions with coordination requirements (device locking, queue management, state synchronization)
   - Distributed state management would be required with domain-based organization

2. Workflow Span: CROSS_DOMAIN
   - Primary workflows span 2-3 domains (device management + plan execution + monitoring)
   - Common operations require coordination across multiple services

3. Common Operations: WORKFLOWS (80% workflows, 20% CRUD)
   - Most user operations are multi-step workflows, not simple CRUD

RECOMMENDATION: Workflow-Based Organization
- Group services by user workflows to keep coordination logic local
- Reduces distributed state management complexity
- Makes common operations self-contained

CHOICE: Service Organization Strategy

1. Domain-Based Organization
   Services: UserManagementService, DeviceManagementService, PlanExecutionService, MonitoringService
   Pros: Clear domain boundaries, aligns with business domains
   Cons: Coordination logic becomes distributed, more service-to-service calls

2. Workflow-Based Organization ⭐ RECOMMENDED
   Services: ExperimentExecutionService (workflow: submit→coordinate→execute→release),
            DeviceMonitoringService (workflow: subscribe→stream),
            DirectControlService (workflow: check→command),
            ConfigurationService (shared: registry, plans)
   Pros: Coordination is local, workflows self-contained
   Cons: May duplicate some domain logic

3. Hybrid (Domain + Workflow)
   Workflow Services: ExperimentExecutionService, BatchProcessingService
   Domain Services: UserManagementService, DeviceRegistryService
   Pros: Best of both strategies
   Cons: More complex to design initially

Please select [1/2/3]:
```

**Storage**: Choice stored in `specs/machine/service_organization_strategy.json`

### 3. Updated Workflow Action: D-01-A04.5

**New workflow action** with CHOICE:

```json
{
  "action_id": "D-01-A04.5",
  "description": "Generate interface contracts (CHOICE: Protocol-based or ABC-based)",
  "user_prompt": {
    "ask": "Which interface contract strategy would you like to use?",
    "options": [
      "Protocol-based with Dependency Injection (RECOMMENDED) - Modern, flexible, no metaclass conflicts",
      "Abstract Base Classes (ABC) - Traditional, inheritance-based",
      "Skip interface generation - Manual implementation"
    ],
    "default": "Protocol-based with Dependency Injection",
    "recommendation": "Protocol-based is recommended for multi-facility, framework integration, and high testability"
  },
  "if_protocol_based": {
    "tool": "generate_interface_protocols.py",
    "command": "python3 {reflow_root}/tools/generate_interface_protocols.py {system_root}",
    "outputs": [
      "services/common/protocols/*.py",
      "services/common/mixins/*.py",
      "services/common/di/container.py",
      "services/common/di/dependencies.py"
    ]
  },
  "if_abc_based": {
    "tool": "generate_interface_abc.py",
    "command": "python3 {reflow_root}/tools/generate_interface_abc.py {system_root}",
    "outputs": [
      "services/{consumer}/interfaces/{provider}_interface.{ext}"
    ]
  }
}
```

## Impact Analysis

### Affected Components

1. **Workflows** (2 files modified):
   - `workflows/01c-top_down_design.json` - Add SE-02-A01.5 (service organization strategy choice)
   - `workflow_steps/development/D-01-InitBootstrap.json` - Update D-01-A04.5 (interface contract choice)

2. **Tools** (2 new tools):
   - `tools/generate_interface_protocols.py` (NEW) - Protocol + DI generation
   - `tools/analyze_service_organization.py` (NEW) - Analyze system for organization recommendation

3. **Templates** (12 new templates):
   - `templates/protocol_template.py` (NEW)
   - `templates/mixins/has_lifecycle_template.py` (NEW)
   - `templates/mixins/has_logging_template.py` (NEW)
   - `templates/mixins/requires_auth_template.py` (NEW)
   - `templates/mixins/tracks_metrics_template.py` (NEW)
   - `templates/di_container_template.py` (NEW)
   - `templates/di_dependencies_fastapi_template.py` (NEW)
   - `templates/service_organization_strategy_template.json` (NEW)
   - TypeScript, Rust, C++, Java, Go protocol templates (5 NEW)

4. **Documentation** (4 files):
   - `docs/ARCHITECTURAL_PATTERNS_PROTOCOLS_DI.md` (NEW) - 300+ line architectural guide
   - `CLAUDE.md` - Add Protocol + DI guidance, service organization strategies
   - `docs/TOOL_USAGE_SUMMARY.md` - Add new tool documentation
   - `docs/RELEASE_NOTES_v3.18.0.md` (NEW) - Feature release notes

5. **Dependencies**:
   - No new Python dependencies (uses stdlib `typing.Protocol`)
   - Generated code uses language-native constructs (no external dependencies)

### Breaking Changes

**NONE** - This is a purely additive feature with backward compatibility.

- Existing ABC-based systems continue to work
- New systems can choose Protocol-based or ABC-based
- Both can coexist in the same system

### Data Model Changes

**New files**:
- `specs/machine/service_organization_strategy.json` - Stores chosen strategy and rationale

**No changes to existing schemas**.

## Implementation Considerations

### Design Principles

1. **Choice, not mandate**: Users choose Protocol-based or ABC-based (Protocol recommended)
2. **Framework-agnostic**: Works with UAF, Systems Biology, all frameworks
3. **Language-agnostic**: Protocol equivalents in TypeScript (interfaces), Rust (traits), etc.
4. **Migration path**: ABCs can gradually adopt Protocols without breaking changes
5. **Best practices**: Provide comprehensive guidance document

### Algorithm for Service Organization Analysis

```python
# Pseudocode for analyze_service_organization.py

1. Load functional_architecture.json (functions and flows)
2. Load service_architecture.json (if exists - for brownfield)

3. Analyze coordination complexity:
   - Count functions with coordination keywords (lock, coordinate, synchronize, queue)
   - Analyze functional flows for distributed state requirements
   - Score: LOW (<2 coordination points), MEDIUM (2-5), HIGH (>5)

4. Analyze workflow span:
   - Map functional flows to domains
   - Count flows that span multiple domains
   - Score: SINGLE_DOMAIN (<30% cross-domain), CROSS_DOMAIN (>30%)

5. Analyze operation types:
   - Count CRUD operations (Create, Read, Update, Delete patterns)
   - Count workflow operations (multi-step, coordination-heavy)
   - Ratio: CRUD_HEAVY (>60% CRUD), WORKFLOW_HEAVY (>60% workflows), BALANCED

6. Generate recommendation:
   - HIGH coordination + CROSS_DOMAIN + WORKFLOW_HEAVY → Workflow-based
   - LOW coordination + SINGLE_DOMAIN + CRUD_HEAVY → Domain-based
   - MEDIUM + CROSS_DOMAIN + BALANCED → Hybrid

7. Present analysis + recommendation to user for choice
```

### Testing Strategy

1. **Unit tests**: Test Protocol generation, DI container, mixin behaviors
2. **Integration tests**: Generate Protocols for sample system, verify type checking
3. **Multi-language validation**:
   - Python: mypy type checking
   - TypeScript: tsc compilation
   - Rust: rustc compilation
4. **Migration test**: Convert ABC-based system to Protocol-based, verify behavior unchanged

## Alternatives Considered

### Alternative 1: Keep ABC-only

**Rejected** - Metaclass conflicts are real problem for framework integration (FastAPI, SQLAlchemy, Pydantic, domain frameworks).

### Alternative 2: Protocol-only (remove ABC support)

**Rejected** - Breaking change for existing systems. Better to support both and recommend Protocols.

### Alternative 3: Automatic service organization (no choice)

**Rejected** - Different systems have different needs. Analysis + human choice is better than pure automation.

## Success Criteria

1. ✅ Tool generates syntactically valid Protocol files for all 6 languages
2. ✅ Generated Protocols pass language-specific type checking (mypy, tsc, rustc, etc.)
3. ✅ Generated DI container successfully wires services together
4. ✅ Generated mixins provide reusable behavior without conflicts
5. ✅ Service organization analysis correctly identifies system characteristics
6. ✅ LLM presents clear recommendation with rationale
7. ✅ Migration path documented for ABC → Protocol transition
8. ✅ Documentation comprehensive (patterns guide, examples, best practices)

## Rollout Plan

### Phase 1: Core Protocol + DI (v3.18.0)
- Implement `generate_interface_protocols.py` for Python
- Create behavior mixin templates
- Create DI container template
- Update D-01-A04.5 workflow action with choice
- Add ARCHITECTURAL_PATTERNS_PROTOCOLS_DI.md documentation
- Release as v3.18.0

### Phase 2: Service Organization Strategy (v3.18.0)
- Implement `analyze_service_organization.py`
- Add SE-02-A01.5 workflow action
- Update CLAUDE.md with service organization guidance
- Include in v3.18.0 release

### Phase 3: Multi-language Support (v3.18.1+)
- Add TypeScript, Rust, C++, Java, Go Protocol generation
- Language-specific DI patterns
- Release as v3.18.1

## Migration Guide

### For Existing ABC-based Systems

**No migration required** - ABCs continue to work.

**Optional migration** (to gain benefits of Protocols + DI):

1. **Step 1: Add Protocols alongside ABCs**
   ```python
   # Keep existing ABC
   class ExecutionServiceBase(ABC):
       @abstractmethod
       def submit_plan(self, plan_name: str, params: dict) -> str:
           pass

   # Add Protocol
   @runtime_checkable
   class CanExecutePlans(Protocol):
       def submit_plan(self, plan_name: str, params: dict) -> str: ...

   # Implementation satisfies both
   class ExecutionService(ExecutionServiceBase):
       def submit_plan(self, plan_name: str, params: dict) -> str:
           return self._do_submit(plan_name, params)

   assert isinstance(ExecutionService(), CanExecutePlans)  # True
   ```

2. **Step 2: Update type hints to use Protocols**
   ```python
   # Old
   def use_executor(executor: ExecutionServiceBase): ...

   # New
   def use_executor(executor: CanExecutePlans): ...
   ```

3. **Step 3: Remove ABC inheritance** (once all type hints updated)
   ```python
   # No longer inherit from ABC
   class ExecutionService:
       def submit_plan(self, plan_name: str, params: dict) -> str:
           return self._do_submit(plan_name, params)

   # Still satisfies Protocol
   assert isinstance(ExecutionService(), CanExecutePlans)  # True
   ```

### For New Systems

**Recommended**: Choose "Protocol-based with Dependency Injection" during D-01-A04.5.

**If using domain-based organization**: Still use Protocols + DI for flexibility.

**If using workflow-based organization**: Protocols + DI are essential for coordination.

## Questions & Risks

### Questions

1. ✅ Should Protocol generation replace ABC generation? **Answer: No, offer both as choice**
2. ✅ Should service organization be automatic or user choice? **Answer: Analysis + recommendation + user choice**
3. ⚠️ How to handle Protocol versioning? **Answer: Version with ICD version (future enhancement)**

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Learning curve for Protocols | Medium | Low | Comprehensive documentation, examples, migration guide |
| DI adds complexity | Low | Medium | DI is opt-in, templates provide working examples |
| Service organization choice paralysis | Low | Low | Clear analysis + recommendation reduces uncertainty |
| Protocol drift (ICD updated, Protocol not regenerated) | Medium | High | Add validation tool (future enhancement) |

## Timeline

- **Day 1-2**: Implement `generate_interface_protocols.py` (Python) + templates (12 hours)
- **Day 3**: Implement `analyze_service_organization.py` + SE-02-A01.5 (6 hours)
- **Day 4**: Update workflows (D-01-A04.5), documentation (8 hours)
- **Day 5**: Testing, examples, migration guide (6 hours)
- **Total**: ~32 hours (4-5 days)

## Approval

This change proposal requires approval before implementation per FU-01 gate.

**Change Type**: ⭐ **Feature Addition** (non-breaking)
**Version Impact**: Minor version bump (3.17.0 → 3.18.0)

---

**Prepared by**: Claude (LLM Agent) based on Bluesky remote access architecture analysis
**Date**: 2025-11-19
**Status**: PENDING APPROVAL
