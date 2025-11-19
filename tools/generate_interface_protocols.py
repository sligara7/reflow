#!/usr/bin/env python3
"""
Generate Protocol-Based Interface Contracts with Dependency Injection

This tool generates Protocol-based interfaces, behavior mixins, and DI container
setup from system_of_systems_graph.json and ICD files.

Key Differences from ABC Generation:
- Uses Python Protocols (structural typing, no metaclass conflicts)
- Generates dependency injection container and FastAPI dependencies
- Creates reusable behavior mixins (HasLifecycle, HasLogging, etc.)
- Supports multiple implementations without inheritance coupling

Supported Languages:
- Python: Protocol with @runtime_checkable
- TypeScript: Interface declarations (future)
- Rust: Trait definitions (future)
- Other languages: Extensible template system

Usage:
    python3 generate_interface_protocols.py /path/to/system_root/

Inputs:
    - specs/machine/graphs/system_of_systems_graph.json (edges = interfaces)
    - specs/machine/development_language_configuration.json (language per service)
    - specs/machine/interfaces/*_icd.json (detailed interface specs)

Outputs:
    - services/common/protocols/*.py (Protocol definitions)
    - services/common/mixins/*.py (Behavior mixins)
    - services/common/di/container.py (DI container)
    - services/common/di/dependencies.py (FastAPI dependencies if applicable)

Version: 3.18.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
import re

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class ProtocolGenerator:
    """Generate Protocol-based interfaces and DI infrastructure"""

    # Type mapping: JSON Schema → Python types
    PYTHON_TYPE_MAPPINGS = {
        'string': 'str',
        'integer': 'int',
        'number': 'float',
        'boolean': 'bool',
        'array': 'List',
        'object': 'Dict[str, Any]',
        'null': 'None'
    }

    def __init__(self, system_root: str):
        """
        Initialize Protocol generator

        Args:
            system_root: Path to system root directory

        Raises:
            PathSecurityError: If system_root is invalid
        """
        self.system_root = validate_system_root(system_root)
        self.graph_data: Optional[Dict] = None
        self.lang_config: Optional[Dict] = None
        self.icds: Dict[str, Dict] = {}
        self.protocols_generated: List[str] = []
        self.mixins_generated: List[str] = []

    def load_inputs(self):
        """Load system_of_systems_graph.json, language config, and ICDs"""
        print("Loading input files...")

        # Load system of systems graph
        graph_path = self.system_root / "specs" / "machine" / "graphs" / "system_of_systems_graph.json"
        if not graph_path.exists():
            print(f"⚠️  Graph file not found: {graph_path}")
            print("   Protocol generation requires system_of_systems_graph.json")
            sys.exit(1)

        self.graph_data = safe_load_json(graph_path)
        print(f"✅ Loaded graph with {len(self.graph_data.get('nodes', []))} nodes, {len(self.graph_data.get('edges', []))} edges")

        # Load language configuration
        lang_config_path = self.system_root / "specs" / "machine" / "development_language_configuration.json"
        if lang_config_path.exists():
            self.lang_config = safe_load_json(lang_config_path)
            print(f"✅ Loaded language configuration")
        else:
            print("ℹ️  No language configuration found - defaulting to Python")
            self.lang_config = {"default_language": "Python"}

        # Load ICDs
        icd_dir = self.system_root / "specs" / "machine" / "interfaces"
        if icd_dir.exists():
            for icd_file in icd_dir.glob("*_icd.json"):
                interface_name = icd_file.stem.replace("_icd", "")
                self.icds[interface_name] = safe_load_json(icd_file)
            print(f"✅ Loaded {len(self.icds)} ICD files")
        else:
            print("⚠️  No ICD directory found - will generate basic Protocols")

    def _to_snake_case(self, text: str) -> str:
        """Convert text to snake_case"""
        # Insert underscore before capitals
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', text)
        # Insert underscore before capitals that follow lowercase
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1).lower()

    def _to_protocol_name(self, service_name: str, verb: str = "Provides") -> str:
        """
        Convert service name to Protocol name

        Examples:
            UserService -> ProvidesUserManagement
            ExecutionService -> CanExecutePlans
            DeviceRegistry -> ProvidesDeviceRegistry
        """
        # Remove "Service" suffix if present
        base_name = service_name.replace("Service", "").replace("_service", "")

        # Determine verb based on service type
        if "registry" in service_name.lower() or "config" in service_name.lower():
            verb = "Provides"
        elif "executor" in service_name.lower() or "runner" in service_name.lower():
            verb = "Can"
        elif "monitor" in service_name.lower() or "observer" in service_name.lower():
            verb = "Supports"
        elif "auth" in service_name.lower():
            verb = "Handles"
        else:
            verb = "Provides"

        # Construct protocol name
        if verb == "Can":
            # CanExecutePlans, CanProcessData
            action = base_name.replace("Executor", "Execute").replace("Runner", "Run")
            return f"Can{action}"
        else:
            # ProvidesUserManagement, HandlesAuthentication
            return f"{verb}{base_name}"

    def _map_json_type_to_python(self, json_type: str, items_type: Optional[str] = None) -> str:
        """
        Map JSON schema type to Python type hint

        Args:
            json_type: JSON schema type (string, integer, array, etc.)
            items_type: For arrays, the type of items

        Returns:
            Python type hint string
        """
        base_type = self.PYTHON_TYPE_MAPPINGS.get(json_type, 'Any')

        if json_type == 'array' and items_type:
            item_type = self.PYTHON_TYPE_MAPPINGS.get(items_type, 'Any')
            return f'List[{item_type}]'

        return base_type

    def generate_protocols(self):
        """Generate Protocol definitions for all service interfaces"""
        print("\n📋 Generating Protocol definitions...")

        # Create output directory
        protocols_dir = self.system_root / "services" / "common" / "protocols"
        protocols_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = protocols_dir / "__init__.py"
        init_file.write_text('"""Protocol definitions for service interfaces"""\n')

        # Generate Protocol for each unique provider in graph edges
        providers = set()
        for edge in self.graph_data.get('edges', []):
            providers.add(edge['source'])

        for provider in sorted(providers):
            self._generate_protocol_for_provider(provider, protocols_dir)

        print(f"✅ Generated {len(self.protocols_generated)} Protocol files")

    def _generate_protocol_for_provider(self, provider: str, output_dir: Path):
        """
        Generate a Protocol definition for a provider service

        Args:
            provider: Service name that provides an interface
            output_dir: Directory to write Protocol file
        """
        protocol_name = self._to_protocol_name(provider)
        protocol_file = output_dir / f"{self._to_snake_case(protocol_name)}.py"

        # Find all interfaces provided by this service
        interfaces = []
        for edge in self.graph_data.get('edges', []):
            if edge['source'] == provider:
                interface_id = edge.get('interface_id', edge.get('label', 'unknown'))
                interfaces.append(interface_id)

        # Collect methods from ICDs
        methods = []
        for interface_id in interfaces:
            icd = self.icds.get(interface_id, {})
            if 'operations' in icd:
                for op in icd['operations']:
                    methods.append(self._generate_method_signature(op))
            elif 'endpoints' in icd:  # REST API style
                for endpoint in icd['endpoints']:
                    methods.append(self._generate_method_from_endpoint(endpoint))

        # If no methods found, generate placeholder
        if not methods:
            methods.append(self._generate_placeholder_method(provider))

        # Generate Protocol file
        content = self._render_protocol_template(
            protocol_name=protocol_name,
            provider=provider,
            methods=methods,
            interfaces=interfaces
        )

        protocol_file.write_text(content)
        self.protocols_generated.append(protocol_name)
        print(f"  ✅ {protocol_name} -> {protocol_file.name}")

    def _generate_method_signature(self, operation: Dict) -> Dict[str, str]:
        """
        Generate method signature from ICD operation

        Args:
            operation: Operation dict from ICD

        Returns:
            Dict with method_name, params, return_type, docstring
        """
        method_name = operation.get('name', 'unknown_operation')

        # Build parameters
        params = []
        for param in operation.get('inputs', []):
            param_name = param.get('name', 'param')
            param_type = self._map_json_type_to_python(
                param.get('type', 'string'),
                param.get('items_type')
            )
            optional = not param.get('required', False)
            if optional:
                params.append(f"{param_name}: Optional[{param_type}] = None")
            else:
                params.append(f"{param_name}: {param_type}")

        # Return type
        return_type = 'Any'
        if 'output' in operation:
            return_type = self._map_json_type_to_python(
                operation['output'].get('type', 'object'),
                operation['output'].get('items_type')
            )

        # Docstring
        docstring = operation.get('description', f'{method_name} operation')

        # Add parameter documentation
        param_docs = []
        for param in operation.get('inputs', []):
            param_docs.append(f"        {param.get('name', 'param')}: {param.get('description', 'No description')}")

        if param_docs:
            docstring += "\n\n    Args:\n" + "\n".join(param_docs)

        # Add return documentation
        if 'output' in operation and 'description' in operation['output']:
            docstring += f"\n\n    Returns:\n        {operation['output']['description']}"

        # Add error documentation
        if 'errors' in operation:
            error_docs = [f"        {err.get('name', 'Error')}: {err.get('description', 'No description')}" for err in operation['errors']]
            if error_docs:
                docstring += "\n\n    Raises:\n" + "\n".join(error_docs)

        return {
            'method_name': method_name,
            'params': ', '.join(params),
            'return_type': return_type,
            'docstring': docstring
        }

    def _generate_method_from_endpoint(self, endpoint: Dict) -> Dict[str, str]:
        """Generate method signature from REST endpoint"""
        path = endpoint.get('path', '/unknown')
        method = endpoint.get('method', 'GET')

        # Convert path to method name: /users/{id} -> get_user
        method_name = self._to_snake_case(path.replace('/{', '_by_').replace('{', '').replace('}', ''))
        method_name = f"{method.lower()}{method_name}"

        return {
            'method_name': method_name,
            'params': '*args, **kwargs',
            'return_type': 'Any',
            'docstring': f"{method} {path}\n\n    {endpoint.get('description', 'No description')}"
        }

    def _generate_placeholder_method(self, provider: str) -> Dict[str, str]:
        """Generate placeholder method when no ICD found"""
        return {
            'method_name': 'placeholder_operation',
            'params': '',
            'return_type': 'Any',
            'docstring': f"""
    Placeholder operation for {provider}

    TODO: Implement actual operations based on service requirements.
    This is a placeholder because no ICD file was found for this service.
    """
        }

    def _render_protocol_template(self, protocol_name: str, provider: str, methods: List[Dict], interfaces: List[str]) -> str:
        """
        Render Protocol template

        Args:
            protocol_name: Name of the Protocol class
            provider: Provider service name
            methods: List of method signature dicts
            interfaces: List of interface IDs

        Returns:
            Rendered Python Protocol code
        """
        # Build method definitions
        method_defs = []
        for method in methods:
            method_def = f'''
    def {method['method_name']}(self{", " + method['params'] if method['params'] else ""}) -> {method['return_type']}:
        """
        {method['docstring']}
        """
        ...
'''
            method_defs.append(method_def)

        # Render template
        return f'''"""
Protocol: {protocol_name}

Provider: {provider}
Interfaces: {", ".join(interfaces) if interfaces else "No ICDs found"}

Generated from: system_of_systems_graph.json
Generated on: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""

from typing import Protocol, runtime_checkable, Any, Optional, List, Dict


@runtime_checkable
class {protocol_name}(Protocol):
    """
    Interface: {protocol_name}

    Provider services implement this interface to expose {provider} capabilities.
    Consumer services depend on this interface (not concrete implementations).

    This enables:
    - Multiple implementations without inheritance coupling
    - Easy testing with mock implementations
    - Different implementations per facility/environment
    - No metaclass conflicts with frameworks
    """
{''.join(method_defs)}
'''

    def generate_behavior_mixins(self):
        """Generate reusable behavior mixin classes"""
        print("\n🔧 Generating behavior mixins...")

        mixins_dir = self.system_root / "services" / "common" / "mixins"
        mixins_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = mixins_dir / "__init__.py"
        init_file.write_text('"""Reusable behavior mixins for services"""\n')

        # Generate standard mixins
        self._generate_has_lifecycle_mixin(mixins_dir)
        self._generate_has_logging_mixin(mixins_dir)
        self._generate_requires_auth_mixin(mixins_dir)
        self._generate_tracks_metrics_mixin(mixins_dir)

        print(f"✅ Generated {len(self.mixins_generated)} behavior mixins")

    def _generate_has_lifecycle_mixin(self, output_dir: Path):
        """Generate HasLifecycle mixin"""
        content = '''"""HasLifecycle mixin - Provides start/stop lifecycle management"""

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
    - is_started property to check service state

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
            self._get_logger().warning(f"{self.__class__.__name__} already started")
            return

        self._get_logger().info(f"Starting {self.__class__.__name__}")

        self._started = True
        await self._on_start()

        self._get_logger().info(f"{self.__class__.__name__} started successfully")

    async def stop(self):
        """Stop the service gracefully"""
        if not self._started:
            self._get_logger().warning(f"{self.__class__.__name__} not started")
            return

        self._get_logger().info(f"Stopping {self.__class__.__name__}")

        await self._on_stop()
        self._started = False

        self._get_logger().info(f"{self.__class__.__name__} stopped")

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

    def _get_logger(self) -> logging.Logger:
        """Get logger (handles lazy initialization)"""
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger
'''
        mixin_file = output_dir / "has_lifecycle.py"
        mixin_file.write_text(content)
        self.mixins_generated.append("HasLifecycle")
        print(f"  ✅ HasLifecycle -> has_lifecycle.py")

    def _generate_has_logging_mixin(self, output_dir: Path):
        """Generate HasLogging mixin"""
        content = '''"""HasLogging mixin - Provides structured logging capabilities"""

import logging
from typing import Any, Optional


class HasLogging:
    """
    Mixin: Provides structured logging capabilities

    Services that inherit from this mixin get:
    - log_info(), log_warning(), log_error(), log_debug() methods
    - Automatic logger naming based on class name
    - Context parameter support for structured logging

    Usage:
        class MyService(HasLogging, OtherMixins):
            def do_work(self, user_id: str):
                self.log_info("Starting work", user_id=user_id, operation="do_work")
                try:
                    result = self._process()
                    self.log_info("Work completed", result=result)
                except Exception as e:
                    self.log_error("Work failed", error=str(e), user_id=user_id)
    """

    def __init__(self):
        self._logger: Optional[logging.Logger] = None

    def _get_logger(self) -> logging.Logger:
        """Get logger (handles lazy initialization)"""
        if self._logger is None:
            self._logger = logging.getLogger(self.__class__.__name__)
        return self._logger

    def log_info(self, msg: str, **context: Any):
        """Log info message with structured context"""
        self._get_logger().info(msg, extra=context)

    def log_warning(self, msg: str, **context: Any):
        """Log warning message with structured context"""
        self._get_logger().warning(msg, extra=context)

    def log_error(self, msg: str, **context: Any):
        """Log error message with structured context"""
        self._get_logger().error(msg, extra=context)

    def log_debug(self, msg: str, **context: Any):
        """Log debug message with structured context"""
        self._get_logger().debug(msg, extra=context)
'''
        mixin_file = output_dir / "has_logging.py"
        mixin_file.write_text(content)
        self.mixins_generated.append("HasLogging")
        print(f"  ✅ HasLogging -> has_logging.py")

    def _generate_requires_auth_mixin(self, output_dir: Path):
        """Generate RequiresAuth mixin"""
        content = '''"""RequiresAuth mixin - Provides authentication/authorization checking"""

from typing import Protocol, runtime_checkable, Any


@runtime_checkable
class HandlesAuthentication(Protocol):
    """
    Protocol: Authentication provider interface

    Authentication providers must implement these methods.
    """

    def has_permission(self, user: Any, action: str) -> bool:
        """Check if user has permission to perform action"""
        ...


class RequiresAuth:
    """
    Mixin: Provides authentication/authorization checking

    Services that inherit from this mixin get:
    - require_permission() method to check and enforce permissions
    - check_permission() method to check permissions without raising

    Requires:
        - auth_provider: HandlesAuthentication instance injected via constructor

    Usage:
        class MyService(RequiresAuth, OtherMixins):
            def __init__(self, auth_provider: HandlesAuthentication):
                self._auth = auth_provider

            def sensitive_operation(self, user: User):
                self.require_permission(user, "perform_sensitive_op")
                # ... do sensitive work ...
    """

    def __init__(self, auth_provider: HandlesAuthentication):
        self._auth = auth_provider

    def require_permission(self, user: Any, action: str):
        """
        Require user to have permission, raise exception if not

        Args:
            user: User object (must have permissions)
            action: Action name (e.g., "execute_plans", "command_devices")

        Raises:
            PermissionDenied: If user lacks permission
        """
        if not self.check_permission(user, action):
            raise PermissionDenied(f"User {user} lacks permission: {action}")

    def check_permission(self, user: Any, action: str) -> bool:
        """
        Check if user has permission (non-raising)

        Args:
            user: User object
            action: Action name

        Returns:
            True if user has permission, False otherwise
        """
        return self._auth.has_permission(user, action)


class PermissionDenied(Exception):
    """Raised when user lacks required permission"""
    pass
'''
        mixin_file = output_dir / "requires_auth.py"
        mixin_file.write_text(content)
        self.mixins_generated.append("RequiresAuth")
        print(f"  ✅ RequiresAuth -> requires_auth.py")

    def _generate_tracks_metrics_mixin(self, output_dir: Path):
        """Generate TracksMetrics mixin"""
        content = '''"""TracksMetrics mixin - Provides Prometheus metrics tracking"""

try:
    from prometheus_client import Counter, Histogram, Gauge
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("⚠️  prometheus_client not installed - metrics tracking will be no-ops")


class TracksMetrics:
    """
    Mixin: Provides Prometheus metrics tracking

    Services that inherit from this mixin get:
    - _record_request() method to increment request counter
    - _record_error() method to increment error counter
    - _record_duration() method to record operation duration

    Requires:
        - pip install prometheus-client (optional, gracefully degrades)

    Usage:
        class MyService(TracksMetrics, OtherMixins):
            def do_work(self):
                self._record_request()
                try:
                    result = self._process()
                    return result
                except Exception as e:
                    self._record_error()
                    raise
    """

    def __init__(self):
        service_name = self.__class__.__name__
        if PROMETHEUS_AVAILABLE:
            self._request_counter = Counter(
                f"{service_name}_requests_total",
                f"Total requests to {service_name}"
            )
            self._error_counter = Counter(
                f"{service_name}_errors_total",
                f"Total errors in {service_name}"
            )
            self._duration_histogram = Histogram(
                f"{service_name}_duration_seconds",
                f"Operation duration in {service_name}"
            )
        else:
            self._request_counter = None
            self._error_counter = None
            self._duration_histogram = None

    def _record_request(self):
        """Increment request counter"""
        if self._request_counter:
            self._request_counter.inc()

    def _record_error(self):
        """Increment error counter"""
        if self._error_counter:
            self._error_counter.inc()

    def _record_duration(self, duration_seconds: float):
        """Record operation duration"""
        if self._duration_histogram:
            self._duration_histogram.observe(duration_seconds)
'''
        mixin_file = output_dir / "tracks_metrics.py"
        mixin_file.write_text(content)
        self.mixins_generated.append("TracksMetrics")
        print(f"  ✅ TracksMetrics -> tracks_metrics.py")

    def generate_di_container(self):
        """Generate dependency injection container"""
        print("\n🔌 Generating DI container...")

        di_dir = self.system_root / "services" / "common" / "di"
        di_dir.mkdir(parents=True, exist_ok=True)

        # Create __init__.py
        init_file = di_dir / "__init__.py"
        init_file.write_text('"""Dependency injection infrastructure"""\n')

        self._generate_container_template(di_dir)
        self._generate_fastapi_dependencies(di_dir)

        print("✅ Generated DI infrastructure")

    def _generate_container_template(self, output_dir: Path):
        """Generate DI container template"""
        # Collect all Protocol names
        protocol_imports = []
        for protocol_name in self.protocols_generated:
            module_name = self._to_snake_case(protocol_name)
            protocol_imports.append(f"from ..protocols.{module_name} import {protocol_name}")

        protocol_imports_str = "\n".join(protocol_imports) if protocol_imports else "# No protocols generated"

        content = f'''"""
Dependency Injection Container

Wires services together by providing concrete implementations
for Protocol-based interfaces.

This is a TEMPLATE - you need to:
1. Import your service implementations
2. Update _build_services() to instantiate your services
3. Add getter methods for each service

Usage:
    # Startup
    config = load_config()
    container = ServiceContainer(config)
    await container.start_all()

    # Access services
    executor = container.get_executor()
    registry = container.get_registry()
"""

from typing import Dict, Any, Optional
{protocol_imports_str}


class ServiceContainer:
    """
    Dependency Injection Container

    Manages service lifecycle and provides access to service instances.
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize container with configuration

        Args:
            config: Configuration dictionary (loaded from config file)
        """
        self._config = config
        self._services: Dict[str, Any] = {{}}
        self._build_services()

    def _build_services(self):
        """
        Build and wire services based on configuration

        TODO: Update this method to instantiate your actual service implementations.

        Example:
            # Import implementations
            from services.execution.queueserver_executor import QueueServerExecutor
            from services.registry.yaml_registry import YAMLDeviceRegistry

            # Build services with dependencies injected
            registry = YAMLDeviceRegistry(self._config["registry_path"])

            executor = QueueServerExecutor(
                config=self._config["executor"],
                registry=registry  # Inject dependency
            )

            self._services = {{
                "executor": executor,
                "registry": registry
            }}
        """
        # TEMPLATE - Replace with your service instantiation
        print("⚠️  ServiceContainer._build_services() is a template - update with your services")
        self._services = {{}}

    async def start_all(self):
        """Start all services in dependency order"""
        print("Starting all services...")
        for name, service in self._services.items():
            if hasattr(service, "start"):
                await service.start()
                print(f"  ✅ Started {{name}}")

    async def stop_all(self):
        """Stop all services in reverse dependency order"""
        print("Stopping all services...")
        for name, service in reversed(list(self._services.items())):
            if hasattr(service, "stop"):
                await service.stop()
                print(f"  ✅ Stopped {{name}}")

    # TODO: Add getter methods for your services
    # Example:
    # def get_executor(self) -> CanExecutePlans:
    #     return self._services["executor"]
    #
    # def get_registry(self) -> ProvidesDeviceRegistry:
    #     return self._services["registry"]
'''
        container_file = output_dir / "container.py"
        container_file.write_text(content)
        print("  ✅ ServiceContainer -> container.py (TEMPLATE)")

    def _generate_fastapi_dependencies(self, output_dir: Path):
        """Generate FastAPI dependency injection helpers"""
        content = '''"""
FastAPI Dependency Injection Helpers

Provides FastAPI-compatible dependency functions for injecting services into endpoints.

Requires:
    - pip install fastapi

Usage:
    from fastapi import FastAPI, Depends
    from services.common.di.dependencies import get_executor

    app = FastAPI()

    @app.post("/plans/submit")
    async def submit_plan(
        plan_name: str,
        executor: CanExecutePlans = Depends(get_executor)
    ):
        plan_id = executor.submit_plan(plan_name, {})
        return {"plan_id": plan_id}
"""

try:
    from fastapi import Depends
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False
    print("ℹ️  FastAPI not installed - dependency functions are templates only")

from typing import Optional
from .container import ServiceContainer


# Global container instance (initialized at startup)
_container: Optional[ServiceContainer] = None


def initialize_container(config: dict):
    """
    Initialize the global service container

    Call this during application startup (e.g., FastAPI startup event).

    Args:
        config: Configuration dictionary
    """
    global _container
    _container = ServiceContainer(config)


async def startup_services():
    """
    Start all services in the container

    Call this during application startup event.
    """
    if _container is None:
        raise RuntimeError("Container not initialized - call initialize_container() first")
    await _container.start_all()


async def shutdown_services():
    """
    Stop all services in the container

    Call this during application shutdown event.
    """
    if _container:
        await _container.stop_all()


# TODO: Add dependency functions for your services
# Example:
# def get_executor() -> CanExecutePlans:
#     """Get executor service for FastAPI dependency injection"""
#     if _container is None:
#         raise RuntimeError("Container not initialized")
#     return _container.get_executor()
#
# def get_registry() -> ProvidesDeviceRegistry:
#     """Get registry service for FastAPI dependency injection"""
#     if _container is None:
#         raise RuntimeError("Container not initialized")
#     return _container.get_registry()
'''
        deps_file = output_dir / "dependencies.py"
        deps_file.write_text(content)
        print("  ✅ FastAPI dependencies -> dependencies.py (TEMPLATE)")

    def generate_summary(self):
        """Generate summary report"""
        print("\n" + "=" * 60)
        print("PROTOCOL GENERATION SUMMARY")
        print("=" * 60)

        print(f"\n📋 Protocols Generated: {len(self.protocols_generated)}")
        for protocol in self.protocols_generated:
            print(f"  - {protocol}")

        print(f"\n🔧 Behavior Mixins Generated: {len(self.mixins_generated)}")
        for mixin in self.mixins_generated:
            print(f"  - {mixin}")

        print(f"\n🔌 DI Infrastructure:")
        print(f"  - ServiceContainer (template)")
        print(f"  - FastAPI dependencies (template)")

        print(f"\n📁 Output Structure:")
        print(f"  services/common/protocols/  ({len(self.protocols_generated)} files)")
        print(f"  services/common/mixins/     ({len(self.mixins_generated)} files)")
        print(f"  services/common/di/         (2 files)")

        print(f"\n⚠️  NEXT STEPS:")
        print(f"  1. Review generated Protocols in services/common/protocols/")
        print(f"  2. Update services/common/di/container.py with your service implementations")
        print(f"  3. Add getter methods to container for each service")
        print(f"  4. Update services/common/di/dependencies.py with FastAPI dependency functions")
        print(f"  5. Implement services using generated Protocols and mixins")

        print("\n✅ Protocol generation complete!")

    def run(self):
        """Run the Protocol generation process"""
        try:
            self.load_inputs()
            self.generate_protocols()
            self.generate_behavior_mixins()
            self.generate_di_container()
            self.generate_summary()
        except Exception as e:
            print(f"\n❌ Error during Protocol generation: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_interface_protocols.py /path/to/system_root/")
        sys.exit(1)

    system_root = sys.argv[1]
    generator = ProtocolGenerator(system_root)
    generator.run()


if __name__ == "__main__":
    main()
