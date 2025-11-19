# Architectural Patterns: Protocols, Dependency Injection, and Service Organization

**Version**: 1.0.0
**Date**: 2025-11-19
**Applies to**: Reflow v3.18.0+

## Executive Summary

This document establishes architectural patterns for modern, flexible service architectures:

1. **Protocol-based interfaces** - Define service contracts using Protocols instead of Abstract Base Classes
2. **Dependency injection** - Wire services together at runtime for flexibility and testability
3. **Service organization strategies** - Choose between workflow-based or domain-based decomposition
4. **Wide inheritance over deep hierarchies** - Compose services from behavior mixins

These patterns address:
- **Flexibility**: Different implementations per facility/environment without code changes
- **Testability**: Easy mocking and contract testing
- **Maintainability**: Clear dependencies, single responsibility
- **Metaclass conflicts**: Avoid ABC metaclass issues with framework infrastructure

## Table of Contents

- [1. Protocol-Based Interfaces](#1-protocol-based-interfaces)
- [2. Dependency Injection](#2-dependency-injection)
- [3. Service Organization Strategies](#3-service-organization-strategies)
- [4. Wide Inheritance Pattern](#4-wide-inheritance-pattern)
- [5. Integration with Reflow](#5-integration-with-reflow)
- [6. Migration from ABCs](#6-migration-from-abcs)

---

## 1. Protocol-Based Interfaces

### Why Protocols Over ABCs?

**Problem with Abstract Base Classes**:
- Consume the metaclass slot (Python allows only one metaclass per class)
- Frameworks (FastAPI, SQLAlchemy, Pydantic, EPICS/Ophyd) often use metaclasses
- Force inheritance coupling (all implementations must inherit from ABC)

**Protocol Solution**:
- Structural typing - no inheritance required
- No metaclass conflicts
- Multiple implementations without common base class
- Runtime checkable with `@runtime_checkable`

### Example: Service Interface

**BAD (Abstract Base Class)**:
```python
from abc import ABC, abstractmethod

class ExecutionServiceBase(ABC):  # Uses ABCMeta metaclass
    @abstractmethod
    async def submit_plan(self, plan_name: str, params: dict) -> str:
        pass

    @abstractmethod
    def is_device_available(self, device: str) -> bool:
        pass

# Problem: Can't use another metaclass
# Problem: All implementations MUST inherit from ExecutionServiceBase
```

**GOOD (Protocol)**:
```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class CanExecutePlans(Protocol):
    """Interface: anything that can execute plans"""

    def submit_plan(self, plan_name: str, params: dict) -> str:
        """Submit a plan for execution"""
        ...

    def is_device_available(self, device: str) -> bool:
        """Check if device is available for use"""
        ...

# Implementation 1: No inheritance required
class QueueServerExecutor:
    def submit_plan(self, plan_name: str, params: dict) -> str:
        return self._qserver.item_add(...)

    def is_device_available(self, device: str) -> bool:
        return device not in self._devices_in_use

# Implementation 2: Different facility, same Protocol
class BlueAPIExecutor:
    def submit_plan(self, plan_name: str, params: dict) -> str:
        return blueapi.submit_task(...)

    def is_device_available(self, device: str) -> bool:
        return self._check_device_state(device)

# Both satisfy CanExecutePlans Protocol - no common inheritance needed
assert isinstance(QueueServerExecutor(), CanExecutePlans)
assert isinstance(BlueAPIExecutor(), CanExecutePlans)
```

### Protocol Naming Conventions

**Use capability-based names**:
- `CanExecutePlans` - "Can do X"
- `ProvidesDeviceRegistry` - "Provides Y"
- `HandlesAuthentication` - "Handles Z"
- `SupportsMonitoring` - "Supports W"

**NOT implementation-based names**:
- ❌ `ExecutionService` (too specific)
- ❌ `IExecutionService` (C# convention, not Pythonic)
- ❌ `ExecutionServiceInterface` (verbose)

### When to Use Protocols

**Use Protocols for**:
- Service-to-service interfaces
- Pluggable implementations (different facilities, test mocks)
- External integrations (database, message queue, external APIs)

**Don't use Protocols for**:
- Data classes (use dataclasses, Pydantic models)
- Domain entities (use regular classes)
- Simple value objects

---

## 2. Dependency Injection

### Core Concept

**Services declare WHAT they need, not HOW to get it**.

Dependencies are "injected" at startup, providing "directions" for service communication.

### Example: Service Dependencies

**Service declares dependencies via Protocol type hints**:
```python
class DirectCommandService:
    """Service for direct device commanding"""

    def __init__(self,
                 executor: CanExecutePlans,           # WHAT: Something that executes plans
                 registry: ProvidesDeviceRegistry,    # WHAT: Something that knows devices
                 auth: HandlesAuthentication):        # WHAT: Something that authenticates
        self._executor = executor
        self._registry = registry
        self._auth = auth

    async def command_device(self, user: User, device: str, value: Any) -> Status:
        # Use injected dependencies - don't know or care what they are
        self._auth.require_permission(user, "command_devices")

        device_info = self._registry.get_device_metadata(device)

        # Coordination check via injected executor
        if not self._executor.is_device_available(device):
            raise DeviceBusyError(f"Device {device} in use by plan")

        return await self._send_command(device, value)
```

**Startup code provides concrete implementations**:
```python
def build_services(config: Config) -> Services:
    """Dependency injection - wire services together"""

    # Build concrete implementations
    registry = YAMLDeviceRegistry(config.registry_path)

    auth = OAuth2AuthProvider(
        issuer=config.auth.issuer,
        audience=config.auth.audience
    )

    executor = QueueServerExecutor(
        host=config.qserver.host,
        registry=registry  # Inject registry into executor
    )

    commander = DirectCommandService(
        executor=executor,  # Inject "directions" to executor
        registry=registry,  # Inject "directions" to registry
        auth=auth           # Inject "directions" to auth
    )

    return Services(
        executor=executor,
        commander=commander,
        registry=registry,
        auth=auth
    )
```

### Benefits of Dependency Injection

#### 1. Different Implementations per Context

**Production**:
```python
def build_production_services(config):
    executor = QueueServerExecutor(...)
    auth = OAuth2AuthProvider(...)
    commander = DirectCommandService(executor=executor, auth=auth, ...)
    return Services(...)
```

**Testing**:
```python
def build_test_services():
    executor = MockExecutor()  # Mock implementation
    auth = AlwaysAllowAuth()   # Permissive auth for tests
    commander = DirectCommandService(executor=executor, auth=auth, ...)
    return Services(...)
```

**Diamond Light Source**:
```python
def build_diamond_services(config):
    executor = BlueAPIExecutor(...)  # Different implementation
    auth = DiamondAuthProvider(...)  # Diamond-specific auth
    commander = DirectCommandService(executor=executor, auth=auth, ...)  # Same code!
    return Services(...)
```

#### 2. Clear Dependency Graph

Constructor signatures reveal the service architecture:
```python
class ExecutionService:
    def __init__(self, registry: ProvidesDeviceRegistry): ...
    # Depends on: Registry

class CommandService:
    def __init__(self,
                 executor: CanExecutePlans,
                 registry: ProvidesDeviceRegistry,
                 auth: HandlesAuthentication): ...
    # Depends on: Executor, Registry, Auth

class MonitoringService:
    def __init__(self, registry: ProvidesDeviceRegistry): ...
    # Depends on: Registry
```

Dependencies are explicit and type-checkable.

#### 3. Integration with FastAPI

FastAPI provides built-in DI that integrates naturally:
```python
# dependencies.py
from fastapi import Depends

class ServiceContainer:
    def __init__(self, config: Config):
        self._services = build_services(config)

    def get_executor(self) -> CanExecutePlans:
        return self._services.executor

    def get_commander(self) -> DirectCommandService:
        return self._services.commander

container = ServiceContainer(load_config())

def get_executor() -> CanExecutePlans:
    return container.get_executor()

def get_commander() -> DirectCommandService:
    return container.get_commander()

# routes.py
@app.post("/plans/submit")
async def submit_plan(
    plan_name: str,
    params: dict,
    executor: CanExecutePlans = Depends(get_executor),  # FastAPI DI
    user: User = Depends(get_current_user)
):
    plan_id = executor.submit_plan(plan_name, params)
    return {"plan_id": plan_id}
```

---

## 3. Service Organization Strategies

### The "Right Coordinates" Problem

**Choosing between domain-based and workflow-based service organization is like choosing between Cartesian and polar coordinates** - the right choice depends on what you're trying to make easy.

### Strategy 1: Domain-Based Organization (Traditional)

**Group services by logical domain/capability**.

**Example**:
- UserService (user management domain)
- ProductService (product catalog domain)
- OrderService (order processing domain)
- PaymentService (payment processing domain)

**When to use**:
- Clear domain boundaries with independent lifecycles
- Domain experts aligned with services
- Conway's Law - org structure matches domains
- CRUD operations dominate

**Pros**:
- Aligns with business domains
- Clear ownership boundaries
- Easy to understand for domain experts

**Cons**:
- Cross-cutting workflows span multiple services (distributed transactions, coordination overhead)
- Coordination logic becomes distributed state management

### Strategy 2: Workflow-Based Organization (Modern)

**Group services by user workflows/operations**.

**Example** (Bluesky remote access):
- ExperimentExecutionService (workflow: submit plan → coordinate devices → execute → release)
- DeviceMonitoringService (workflow: subscribe → stream updates)
- DirectControlService (workflow: check coordination → command device)
- ConfigurationService (shared: device registry, plan discovery)

**When to use**:
- Complex coordination requirements between operations
- Common workflows that span multiple domains
- Need to minimize distributed state management
- Operational efficiency matters (reduce network hops)

**Pros**:
- Coordination logic is local (not distributed)
- Common workflows self-contained in one service
- Fewer service-to-service calls for common operations

**Cons**:
- May duplicate some domain logic across services
- Less obvious domain boundaries

### Choosing the Right Strategy

**Ask these questions**:

1. **Do you have complex coordination requirements?**
   - Yes → Workflow-based (coordination becomes local state)
   - No → Domain-based is fine

2. **Do common user operations span multiple domains?**
   - Yes → Workflow-based (keep workflows self-contained)
   - No → Domain-based aligns naturally

3. **Is your organization structured by domain or by workflow?**
   - Domain → Domain-based (Conway's Law)
   - Workflow/product teams → Workflow-based

4. **What makes up 80% of your operations?**
   - CRUD operations → Domain-based
   - Complex multi-step workflows → Workflow-based

### Hybrid Approach

**You can combine both strategies**:
- Workflow services for complex coordination (e.g., ExperimentExecutionService)
- Domain services for shared capabilities (e.g., UserManagementService, DeviceRegistryService)

**Example**:
```
Workflow Services (coordinate complex operations):
├── ExperimentExecutionService (coordinates: devices, plans, queue, execution)
├── BatchProcessingService (coordinates: data ingestion, validation, processing)

Domain Services (provide shared capabilities):
├── UserManagementService (domain: users, roles, permissions)
├── DeviceRegistryService (domain: device catalog, metadata)
├── DataAccessService (domain: stored data, analytics)
```

---

## 4. Wide Inheritance Pattern

### The Problem with Deep Hierarchies

**BAD (Deep hierarchy)**:
```python
class Service:
    pass

class NetworkService(Service):
    async def start(self): ...

class AuthenticatedNetworkService(NetworkService):
    def check_auth(self): ...

class LoggedAuthenticatedNetworkService(AuthenticatedNetworkService):
    def log(self, msg): ...

class MyService(LoggedAuthenticatedNetworkService):
    # Finally get to actual functionality 4 levels deep
    def do_work(self): ...
```

Each level adds one abstract requirement - creates fragile, inflexible hierarchies.

### Solution: Wide Composition with Mixins

**GOOD (Wide composition)**:
```python
# Define reusable behavior mixins
class HasLifecycle:
    """Mixin: start/stop behavior"""
    async def start(self):
        self._started = True
        await self._on_start()

    async def stop(self):
        await self._on_stop()
        self._started = False

    async def _on_start(self):
        """Override for startup logic"""
        pass

    async def _on_stop(self):
        """Override for cleanup"""
        pass

class HasLogging:
    """Mixin: structured logging behavior"""
    def _get_logger(self):
        return logging.getLogger(self.__class__.__name__)

    def log_info(self, msg: str, **context):
        self._get_logger().info(msg, extra=context)

    def log_error(self, msg: str, **context):
        self._get_logger().error(msg, extra=context)

class RequiresAuth:
    """Mixin: authentication checking behavior"""
    def __init__(self, auth_provider: HandlesAuthentication):
        self._auth = auth_provider

    def require_permission(self, user: User, action: str):
        if not self._auth.has_permission(user, action):
            raise PermissionDenied(f"{user} cannot {action}")

class TracksMetrics:
    """Mixin: prometheus metrics behavior"""
    def __init__(self):
        self._request_counter = Counter(f"{self.__class__.__name__}_requests")
        self._error_counter = Counter(f"{self.__class__.__name__}_errors")

    def _record_request(self):
        self._request_counter.inc()

    def _record_error(self):
        self._error_counter.inc()

# Compose services from mixins
class ExecutionService(
    HasLifecycle,      # Gets start/stop machinery
    HasLogging,        # Gets log_info/log_error
    RequiresAuth,      # Gets require_permission
    TracksMetrics,     # Gets _record_request/_record_error
):
    """
    Four parents, each provides concrete behavior.
    No deep hierarchy, no abstract methods to implement.
    Depth: 1 (not 4!)
    """

    def __init__(self,
                 registry: ProvidesDeviceRegistry,
                 auth_provider: HandlesAuthentication):
        RequiresAuth.__init__(self, auth_provider)
        TracksMetrics.__init__(self)

        self._registry = registry

    async def _on_start(self):
        """Override HasLifecycle hook"""
        self.log_info("Starting execution service")

    def submit_plan(self, user: User, plan_name: str, params: dict) -> str:
        # Use inherited behaviors naturally
        self._record_request()
        self.require_permission(user, "execute_plans")

        self.log_info("Submitting plan", plan=plan_name)
        return self._do_submit(plan_name, params)
```

### Inheritance Tree Comparison

**Wide (Recommended)**:
```
ExecutionService (depth: 1)
  ├─ HasLifecycle (concrete behavior)
  ├─ HasLogging (concrete behavior)
  ├─ RequiresAuth (concrete behavior)
  └─ TracksMetrics (concrete behavior)

CommandService (depth: 1)
  ├─ HasLifecycle (concrete behavior)
  ├─ HasLogging (concrete behavior)
  ├─ RequiresAuth (concrete behavior)
  └─ TracksMetrics (concrete behavior)
```

**Deep (Avoid)**:
```
Service
  └─ NetworkService
      └─ AuthenticatedNetworkService
          └─ LoggedAuthenticatedNetworkService
              └─ ExecutionService (depth: 5)
```

### When to Use Depth vs Width

**Use depth (specialized "is-a" relationships)**:
- Natural type hierarchies (Motor → EpicsMotor → BeamlineMotor)
- Progressive specialization where each level adds meaningful domain concepts

**Use width (composed capabilities)**:
- Cross-cutting concerns (logging, auth, metrics, lifecycle)
- Independent behaviors that don't have "is-a" relationships
- Service implementations that assemble multiple capabilities

---

## 5. Integration with Reflow

### Updated Development Workflow

**Step D-01-A04.5: Generate Interface Contracts**

Reflow will offer a CHOICE during development setup:

```
CHOICE: Interface Contract Generation Strategy

1. Protocol-based with Dependency Injection (RECOMMENDED)
   - Generate Protocol definitions from ICDs
   - Generate dependency injection setup code
   - Generate behavior mixin templates
   - Best for: Multi-facility, high testability, framework conflicts

2. Abstract Base Classes (ABC)
   - Generate ABC interfaces from ICDs
   - Traditional inheritance-based contracts
   - Best for: Simple systems, single facility, no framework conflicts

3. Skip interface generation
   - Manual interface implementation
   - Best for: Very simple systems, custom patterns
```

### Generated Artifacts

**Option 1: Protocol-based + DI** (generates):
```
services/common/protocols/
  ├── can_execute_plans.py              # Protocol definition
  ├── provides_device_registry.py       # Protocol definition
  └── handles_authentication.py         # Protocol definition

services/common/mixins/
  ├── has_lifecycle.py                  # Behavior mixin
  ├── has_logging.py                    # Behavior mixin
  ├── requires_auth.py                  # Behavior mixin
  └── tracks_metrics.py                 # Behavior mixin

services/common/di/
  ├── container.py                      # DI container
  └── dependencies.py                   # FastAPI dependencies

services/{service}/
  ├── service.py                        # Service implementation
  └── tests/
      └── test_service.py               # Tests with mocks
```

**Option 2: ABC-based** (generates):
```
services/{consumer}/interfaces/
  └── {provider}_interface.py           # ABC interface
```

### Service Organization Choice

**Step SE-02-A01.5: Service Decomposition Strategy**

Before allocating functions to services, LLM asks:

```
CHOICE: Service Organization Strategy

Based on your system's characteristics, how should services be organized?

1. Domain-Based Organization
   - Services organized by business domain/capability
   - Example: UserService, ProductService, OrderService
   - Best for: Clear domain boundaries, CRUD-heavy, aligned with org structure

2. Workflow-Based Organization
   - Services organized by user workflows/operations
   - Example: CheckoutWorkflowService, InventoryManagementService
   - Best for: Complex coordination, multi-step workflows, operational efficiency

3. Hybrid (Domain + Workflow)
   - Workflow services for complex coordination
   - Domain services for shared capabilities
   - Best for: Complex systems with both workflows and domains

Analysis of your system:
- Coordination complexity: [LOW/MEDIUM/HIGH]
- Workflow span: [SINGLE_DOMAIN/CROSS_DOMAIN]
- Common operations: [CRUD/WORKFLOWS]

Recommended: [Strategy] based on [reasoning]

Please select: [1/2/3]
```

---

## 6. Migration from ABCs

### For Existing Systems Using ABCs

**You don't need to migrate immediately**. ABCs and Protocols can coexist.

**If you want to migrate**:

1. **Add Protocol alongside ABC**:
   ```python
   # Old ABC (keep for backward compatibility)
   class ExecutionServiceBase(ABC):
       @abstractmethod
       def submit_plan(self, plan_name: str, params: dict) -> str:
           pass

   # New Protocol (preferred for new code)
   @runtime_checkable
   class CanExecutePlans(Protocol):
       def submit_plan(self, plan_name: str, params: dict) -> str: ...

   # Implementation satisfies both
   class ExecutionService(ExecutionServiceBase):  # Still inherits ABC
       def submit_plan(self, plan_name: str, params: dict) -> str:
           return self._do_submit(plan_name, params)

   # Type hint uses Protocol (not ABC)
   def use_executor(executor: CanExecutePlans):  # Not ExecutionServiceBase
       executor.submit_plan("my_plan", {})
   ```

2. **Gradually replace ABC type hints with Protocol type hints**:
   ```python
   # Old
   def old_function(executor: ExecutionServiceBase): ...

   # New
   def new_function(executor: CanExecutePlans): ...
   ```

3. **Eventually remove ABC inheritance** (once all type hints updated):
   ```python
   # Remove ABC inheritance
   class ExecutionService:  # No longer inherits from ExecutionServiceBase
       def submit_plan(self, plan_name: str, params: dict) -> str:
           return self._do_submit(plan_name, params)

   # Still satisfies Protocol
   assert isinstance(ExecutionService(), CanExecutePlans)
   ```

### For New Systems

**Prefer Protocols + DI from the start**.

Choose ABCs only if:
- Very simple system (single implementation)
- No framework metaclass conflicts
- No multi-facility deployment requirements

---

## Best Practices Summary

### Protocols
✅ **DO**:
- Use capability-based names (`CanExecutePlans`, `ProvidesRegistry`)
- Apply `@runtime_checkable` for isinstance checks
- Use for service-to-service interfaces
- Document expected behavior in docstrings

❌ **DON'T**:
- Use implementation names (`ExecutionService`)
- Use for data classes (use dataclasses instead)
- Over-apply (not everything needs a Protocol)

### Dependency Injection
✅ **DO**:
- Declare dependencies in `__init__` with Protocol type hints
- Wire services in startup code (not in service code)
- Use FastAPI's Depends for HTTP endpoints
- Create different containers for prod/test/dev

❌ **DON'T**:
- Create dependencies inside services (breaks DI)
- Use global singletons (use DI container instead)
- Mix DI and service locator patterns

### Service Organization
✅ **DO**:
- Analyze your system's coordination complexity first
- Choose domain-based for CRUD-heavy, clear domains
- Choose workflow-based for complex coordination
- Consider hybrid for large, complex systems
- Document your choice and reasoning

❌ **DON'T**:
- Default to domain-based without analysis
- Mix strategies within the same service (pick one)
- Ignore Conway's Law (org structure affects design)

### Wide Inheritance
✅ **DO**:
- Create behavior mixins for cross-cutting concerns
- Keep inheritance depth to 1-2 levels
- Provide complete, reusable behavior in mixins
- Document mixin dependencies (init requirements)

❌ **DON'T**:
- Create deep hierarchies (>3 levels)
- Put abstract methods in mixins (provide concrete behavior)
- Use mixins for domain concepts (use composition instead)

---

## References

- **Python Protocols**: [PEP 544](https://peps.python.org/pep-0544/)
- **Dependency Injection**: [Python Dependency Injector](https://python-dependency-injector.ets-labs.org/)
- **FastAPI Dependencies**: [FastAPI Dependency Injection](https://fastapi.tiangolo.com/tutorial/dependencies/)
- **Wide Inheritance**: [Composition over Inheritance](https://en.wikipedia.org/wiki/Composition_over_inheritance)

---

## Revision History

- **2025-11-19**: Initial version 1.0.0 - Protocols, DI, Service Organization, Wide Inheritance patterns
