#!/usr/bin/env python3
"""
Generate Language-Native Interface Contracts (ABC, Traits, etc.)

This tool generates strongly-typed interface contracts using language-specific
constructs (Python ABC abstract classes, TypeScript interfaces, Rust traits,
C++ abstract classes) from system_of_systems_graph.json and ICD files.

Provides compile-time/runtime interface enforcement between services,
complementing the existing JSON-based Interface Contract Documents.

Supported Languages:
- Python: ABC (Abstract Base Classes) with @abstractmethod
- TypeScript: Interface declarations
- Rust: Trait definitions
- C++: Abstract base classes with pure virtual functions
- Java: Interface declarations
- Go: Interface types

Usage:
    python3 generate_interface_abc.py /path/to/system_root/

Inputs:
    - specs/machine/graphs/system_of_systems_graph.json (edges = interfaces)
    - specs/machine/development_language_configuration.json (language per service)
    - specs/machine/interfaces/*_icd.json (detailed interface specs)

Outputs:
    - services/{consumer_service}/interfaces/{provider}_interface.{ext}
    - One interface file per service dependency

Version: 3.10.0
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from datetime import datetime

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class InterfaceABCGenerator:
    """Generate language-native interface contracts from graph and ICDs"""

    # Type mapping: JSON Schema → Language Types
    TYPE_MAPPINGS = {
        'python': {
            'string': 'str',
            'integer': 'int',
            'number': 'float',
            'boolean': 'bool',
            'array': 'List',
            'object': 'Dict[str, Any]',
            'null': 'None'
        },
        'typescript': {
            'string': 'string',
            'integer': 'number',
            'number': 'number',
            'boolean': 'boolean',
            'array': 'Array',
            'object': 'Record<string, any>',
            'null': 'null'
        },
        'rust': {
            'string': 'String',
            'integer': 'i64',
            'number': 'f64',
            'boolean': 'bool',
            'array': 'Vec',
            'object': 'HashMap<String, serde_json::Value>',
            'null': 'Option'
        },
        'cpp': {
            'string': 'std::string',
            'integer': 'int64_t',
            'number': 'double',
            'boolean': 'bool',
            'array': 'std::vector',
            'object': 'std::map<std::string, json>',
            'null': 'nullptr'
        },
        'java': {
            'string': 'String',
            'integer': 'Long',
            'number': 'Double',
            'boolean': 'Boolean',
            'array': 'List',
            'object': 'Map<String, Object>',
            'null': 'null'
        },
        'go': {
            'string': 'string',
            'integer': 'int64',
            'number': 'float64',
            'boolean': 'bool',
            'array': '[]',
            'object': 'map[string]interface{}',
            'null': 'nil'
        }
    }

    FILE_EXTENSIONS = {
        'python': '.py',
        'typescript': '.ts',
        'rust': '.rs',
        'cpp': '.hpp',
        'java': '.java',
        'go': '.go'
    }

    def __init__(self, system_path: Path):
        """Initialize generator with validated system path"""
        self.system_path = system_path

        # Security: Sanitize all file paths
        try:
            self.graph_file = sanitize_path(
                "specs/machine/graphs/system_of_systems_graph.json",
                self.system_path,
                must_exist=False  # Don't require - will auto-generate if missing
            )
            self.lang_config_file = sanitize_path(
                "specs/machine/development_language_configuration.json",
                self.system_path,
                must_exist=False  # May not exist yet
            )
            self.interfaces_dir = sanitize_path(
                "specs/machine/interfaces",
                self.system_path,
                must_exist=False
            )
        except PathSecurityError as e:
            print(f"ERROR: Path security violation: {e}", file=sys.stderr)
            sys.exit(1)

        # Auto-generate graph if missing
        if not self.graph_file.exists():
            print(f"\n⚠️  System graph not found: {self.graph_file}")
            print(f"📊 Auto-generating system graph...")
            self._auto_generate_graph()

            if not self.graph_file.exists():
                print(f"\n❌ ERROR: Failed to auto-generate system graph.", file=sys.stderr)
                print(f"Please run manually:", file=sys.stderr)
                print(f"  python3 system_of_systems_graph_v2.py {self.system_path}", file=sys.stderr)
                sys.exit(1)
            else:
                print(f"✅ System graph generated successfully")

        self.graph_data = None
        self.lang_config = None
        self.generated_count = 0
        self.skipped_count = 0
        self.errors = []

    def _auto_generate_graph(self):
        """Auto-generate system graph using system_of_systems_graph_v2.py"""
        import subprocess

        # Find system_of_systems_graph_v2.py in the same directory as this tool
        tools_dir = Path(__file__).parent
        graph_tool = tools_dir / "system_of_systems_graph_v2.py"

        if not graph_tool.exists():
            print(f"⚠️  Graph generation tool not found: {graph_tool}", file=sys.stderr)
            return

        try:
            # Run system_of_systems_graph_v2.py with system root
            # Use index.json as input (standard service mode)
            index_file = self.system_path / "specs" / "machine" / "index.json"

            if index_file.exists():
                print(f"Running: python3 {graph_tool} {index_file}")
                result = subprocess.run(
                    ["python3", str(graph_tool), str(index_file)],
                    capture_output=True,
                    text=True,
                    timeout=60
                )

                if result.returncode != 0:
                    print(f"⚠️  Graph generation failed:", file=sys.stderr)
                    print(result.stderr, file=sys.stderr)
                else:
                    print(result.stdout)
            else:
                print(f"⚠️  Index file not found: {index_file}", file=sys.stderr)
                print(f"Cannot auto-generate graph without index.json", file=sys.stderr)

        except subprocess.TimeoutExpired:
            print(f"⚠️  Graph generation timed out (> 60s)", file=sys.stderr)
        except Exception as e:
            print(f"⚠️  Graph generation error: {e}", file=sys.stderr)

    def load_data(self):
        """Load system graph and language configuration"""
        print("Loading system data...")

        # Load system graph
        self.graph_data = safe_load_json(
            self.graph_file,
            file_type_description="system of systems graph"
        )

        # Load language configuration (optional - may not exist yet)
        if self.lang_config_file.exists():
            self.lang_config = safe_load_json(
                self.lang_config_file,
                file_type_description="language configuration"
            )
        else:
            print("Warning: Language configuration not found. Using default (Python).")
            self.lang_config = {"primary_languages": {}}

        print(f"✅ Loaded graph with {len(self.graph_data.get('graph', {}).get('links', []))} interfaces")

    def get_service_language(self, service_name: str) -> str:
        """Get the development language for a service"""
        if not self.lang_config:
            return 'python'  # Default

        # Check service-specific configuration
        service_config = self.lang_config.get('service_specific_configurations', {}).get(service_name, {})
        if 'language' in service_config:
            return service_config['language'].lower()

        # Check primary language
        primary = self.lang_config.get('primary_languages', {})
        if isinstance(primary, dict):
            for key, value in primary.items():
                if isinstance(value, dict) and 'language' in value:
                    return value['language'].lower()

        return 'python'  # Default fallback

    def map_json_type_to_language(self, json_type: str, language: str, is_array: bool = False) -> str:
        """Map JSON schema type to language-specific type"""
        lang = language.lower()
        type_map = self.TYPE_MAPPINGS.get(lang, self.TYPE_MAPPINGS['python'])

        base_type = type_map.get(json_type, 'Any' if lang == 'python' else 'any')

        if is_array and lang == 'python':
            return f"List[{base_type}]"
        elif is_array and lang == 'typescript':
            return f"{base_type}[]"
        elif is_array and lang == 'rust':
            return f"Vec<{base_type}>"
        elif is_array and lang in ['cpp', 'java', 'go']:
            return f"{type_map['array']}<{base_type}>"

        return base_type

    def extract_method_signature(self, icd: Dict, language: str) -> List[Dict]:
        """Extract method signatures from ICD"""
        methods = []

        # Get interface name/ID
        interface_id = icd.get('interface_id', 'unknown')

        # Extract input/output specifications
        contract = icd.get('contract', {})
        input_spec = contract.get('input_specification', {})
        output_spec = contract.get('output_specification', {})

        # Try to infer method name from interface_id
        # Format: provider_to_consumer_method_name
        parts = interface_id.split('_')
        if len(parts) >= 4:
            method_name = '_'.join(parts[3:])  # Everything after consumer
        else:
            method_name = 'execute'  # Default

        # Build method signature
        method = {
            'name': method_name,
            'description': icd.get('metadata', {}).get('rationale', f"Interface method for {interface_id}"),
            'params': [],
            'returns': 'None',
            'raises': []
        }

        # Extract parameters from input schema
        input_schema = input_spec.get('schema', {})
        if isinstance(input_schema, dict):
            for param_name, param_type in input_schema.items():
                lang_type = self.map_json_type_to_language(param_type, language)
                method['params'].append({
                    'name': param_name,
                    'type': lang_type,
                    'description': f"{param_name} parameter"
                })

        # Extract return type from output schema
        output_schema = output_spec.get('schema', {})
        if output_schema:
            method['returns'] = self.map_json_type_to_language('object', language)

        # Extract error conditions
        error_handling = contract.get('error_handling', {})
        for error in error_handling.get('error_conditions', []):
            method['raises'].append({
                'error_type': error.get('error_id', 'Error'),
                'description': error.get('condition', '')
            })

        methods.append(method)
        return methods

    def generate_python_abc(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate Python ABC interface"""
        class_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '"""',
            f'Interface contract for {provider}',
            f'Provider: {provider}',
            f'Consumer: {consumer}',
            'Generated by: Reflow generate_interface_abc.py',
            f'Generated: {datetime.now().strftime("%Y-%m-%d")}',
            '"""',
            '',
            'from abc import ABC, abstractmethod',
            'from typing import Dict, List, Any, Optional',
            '',
            '',
            f'class {class_name}(ABC):',
            f'    """Interface for {provider} service"""',
            ''
        ]

        for method in methods:
            # Method signature
            params_str = ', '.join([
                f"{p['name']}: {p['type']}" for p in method['params']
            ])
            return_type = method['returns'] or 'None'

            lines.append(f"    @abstractmethod")
            lines.append(f"    def {method['name']}(self{', ' + params_str if params_str else ''}) -> {return_type}:")

            # Docstring
            lines.append(f'        """')
            lines.append(f"        {method['description']}")
            lines.append('')

            if method['params']:
                lines.append('        Args:')
                for param in method['params']:
                    lines.append(f"            {param['name']}: {param['description']}")
                lines.append('')

            if method['returns'] and method['returns'] != 'None':
                lines.append('        Returns:')
                lines.append(f"            {method['returns']}")
                lines.append('')

            if method['raises']:
                lines.append('        Raises:')
                for error in method['raises']:
                    lines.append(f"            {error['error_type']}: {error['description']}")
                lines.append('')

            lines.append('        """')
            lines.append('        pass')
            lines.append('')

        return '\n'.join(lines)

    def generate_typescript_interface(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate TypeScript interface"""
        interface_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '/**',
            f' * Interface contract for {provider}',
            f' * Provider: {provider}',
            f' * Consumer: {consumer}',
            ' * Generated by: Reflow generate_interface_abc.py',
            f' * Generated: {datetime.now().strftime("%Y-%m-%d")}',
            ' */',
            '',
            f'export interface {interface_name} {{',
        ]

        for method in methods:
            params_str = ', '.join([
                f"{p['name']}: {p['type']}" for p in method['params']
            ])
            return_type = method['returns'] or 'void'

            lines.append('  /**')
            lines.append(f"   * {method['description']}")
            for param in method['params']:
                lines.append(f"   * @param {param['name']} - {param['description']}")
            if return_type != 'void':
                lines.append(f'   * @returns Promise<{return_type}>')
            lines.append('   */')
            lines.append(f"  {method['name']}({params_str}): Promise<{return_type}>;")
            lines.append('')

        lines.append('}')
        return '\n'.join(lines)

    def generate_rust_trait(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate Rust trait"""
        trait_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '//! Interface contract for ' + provider,
            '//! Provider: ' + provider,
            '//! Consumer: ' + consumer,
            '//! Generated by: Reflow generate_interface_abc.py',
            '//! Generated: ' + datetime.now().strftime("%Y-%m-%d"),
            '',
            'use async_trait::async_trait;',
            'use std::collections::HashMap;',
            '',
            '#[async_trait]',
            f'pub trait {trait_name} {{',
        ]

        for method in methods:
            params_str = ', '.join([
                f"{p['name']}: {p['type']}" for p in method['params']
            ])
            return_type = method['returns'] or '()'

            lines.append(f'    /// {method["description"]}')
            for param in method['params']:
                lines.append(f"    /// * `{param['name']}` - {param['description']}")

            lines.append(f"    async fn {method['name']}(&self{', ' + params_str if params_str else ''}) -> Result<{return_type}, ServiceError>;")
            lines.append('')

        lines.append('}')
        return '\n'.join(lines)

    def generate_cpp_class(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate C++ abstract base class"""
        class_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '/**',
            f' * Interface contract for {provider}',
            f' * Provider: {provider}',
            f' * Consumer: {consumer}',
            ' * Generated by: Reflow generate_interface_abc.py',
            f' * Generated: {datetime.now().strftime("%Y-%m-%d")}',
            ' */',
            '',
            '#pragma once',
            '',
            '#include <string>',
            '#include <vector>',
            '#include <map>',
            '',
            f'class {class_name} {{',
            'public:',
            f'    virtual ~{class_name}() = default;',
            ''
        ]

        for method in methods:
            params_str = ', '.join([
                f"{p['type']} {p['name']}" for p in method['params']
            ])
            return_type = method['returns'] or 'void'

            lines.append(f'    /**')
            lines.append(f"     * {method['description']}")
            lines.append(f'     */')
            lines.append(f"    virtual {return_type} {method['name']}({params_str}) = 0;")
            lines.append('')

        lines.append('};')
        return '\n'.join(lines)

    def generate_java_interface(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate Java interface"""
        interface_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '/**',
            f' * Interface contract for {provider}',
            f' * Provider: {provider}',
            f' * Consumer: {consumer}',
            ' * Generated by: Reflow generate_interface_abc.py',
            f' * Generated: {datetime.now().strftime("%Y-%m-%d")}',
            ' */',
            '',
            'import java.util.*;',
            '',
            f'public interface {interface_name} {{',
        ]

        for method in methods:
            params_str = ', '.join([
                f"{p['type']} {p['name']}" for p in method['params']
            ])
            return_type = method['returns'] or 'void'

            lines.append(f'    /**')
            lines.append(f"     * {method['description']}")
            for param in method['params']:
                lines.append(f"     * @param {param['name']} {param['description']}")
            lines.append(f'     */')
            lines.append(f"    {return_type} {method['name']}({params_str});")
            lines.append('')

        lines.append('}')
        return '\n'.join(lines)

    def generate_go_interface(self, provider: str, consumer: str, methods: List[Dict]) -> str:
        """Generate Go interface"""
        interface_name = f"{self._to_pascal_case(provider)}Interface"

        lines = [
            '// Interface contract for ' + provider,
            '// Provider: ' + provider,
            '// Consumer: ' + consumer,
            '// Generated by: Reflow generate_interface_abc.py',
            '// Generated: ' + datetime.now().strftime("%Y-%m-%d"),
            '',
            'package interfaces',
            '',
            f'type {interface_name} interface {{',
        ]

        for method in methods:
            params_str = ', '.join([
                f"{p['name']} {p['type']}" for p in method['params']
            ])
            return_type = method['returns'] or ''

            lines.append(f'    // {method["description"]}')
            if return_type:
                lines.append(f"    {self._to_pascal_case(method['name'])}({params_str}) ({return_type}, error)")
            else:
                lines.append(f"    {self._to_pascal_case(method['name'])}({params_str}) error")
            lines.append('')

        lines.append('}')
        return '\n'.join(lines)

    def _to_pascal_case(self, snake_str: str) -> str:
        """Convert snake_case to PascalCase"""
        return ''.join(word.capitalize() for word in snake_str.split('_'))

    def generate_interfaces(self):
        """Generate all interface contracts"""
        print("\nGenerating language-native interface contracts...")

        # Get edges from graph (edges = interfaces)
        edges = self.graph_data.get('graph', {}).get('links', [])

        if not edges:
            print("⚠️  No interfaces found in system graph")
            return

        for edge in edges:
            provider = edge.get('source')
            consumer = edge.get('target')
            interface_id = edge.get('interface_id', f"{provider}_to_{consumer}")

            if not provider or not consumer:
                self.errors.append(f"Invalid edge: {edge}")
                continue

            # Get consumer's language
            language = self.get_service_language(consumer)

            # Try to load ICD file
            icd_file = self.interfaces_dir / f"{interface_id}.json"
            if not icd_file.exists():
                # Try alternate naming
                icd_file = self.interfaces_dir / f"{interface_id}_icd.json"

            if not icd_file.exists():
                print(f"⚠️  No ICD found for {interface_id}, generating basic interface")
                icd = self._create_basic_icd(provider, consumer, interface_id)
            else:
                icd = safe_load_json(icd_file, file_type_description="ICD")

            # Extract method signatures
            methods = self.extract_method_signature(icd, language)

            # Generate interface code
            try:
                code = self._generate_for_language(provider, consumer, methods, language)

                if not code:
                    self.skipped_count += 1
                    print(f"⏭️  Skipped {interface_id} (unsupported language: {language})")
                    continue

                # Write interface file
                self._write_interface_file(consumer, provider, language, code)
                self.generated_count += 1
                print(f"✅ Generated {language} interface: {provider} → {consumer}")

            except Exception as e:
                self.errors.append(f"Error generating {interface_id}: {e}")
                print(f"❌ Error: {interface_id}: {e}")

    def _generate_for_language(self, provider: str, consumer: str, methods: List[Dict], language: str) -> Optional[str]:
        """Generate interface for specific language"""
        generators = {
            'python': self.generate_python_abc,
            'typescript': self.generate_typescript_interface,
            'rust': self.generate_rust_trait,
            'cpp': self.generate_cpp_class,
            'c++': self.generate_cpp_class,
            'java': self.generate_java_interface,
            'go': self.generate_go_interface
        }

        generator = generators.get(language.lower())
        if not generator:
            return None

        return generator(provider, consumer, methods)

    def _write_interface_file(self, consumer: str, provider: str, language: str, code: str):
        """Write interface file to service directory"""
        # Create service interfaces directory
        service_dir = self.system_path / 'services' / consumer / 'interfaces'
        service_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename
        extension = self.FILE_EXTENSIONS.get(language.lower(), '.txt')
        filename = f"{provider}_interface{extension}"
        filepath = service_dir / filename

        with open(filepath, 'w') as f:
            f.write(code)

    def _create_basic_icd(self, provider: str, consumer: str, interface_id: str) -> Dict:
        """Create basic ICD when none exists"""
        return {
            'interface_id': interface_id,
            'provider_component': provider,
            'consumer_component': consumer,
            'contract': {
                'input_specification': {'schema': {}},
                'output_specification': {'schema': {}},
                'error_handling': {'error_conditions': []}
            },
            'metadata': {
                'rationale': f"Basic interface between {provider} and {consumer}"
            }
        }

    def generate_summary(self):
        """Generate summary report"""
        print("\n" + "=" * 80)
        print("Interface ABC Generation Summary")
        print("=" * 80)
        print(f"✅ Generated: {self.generated_count} interface files")
        print(f"⏭️  Skipped: {self.skipped_count} (unsupported languages)")
        print(f"❌ Errors: {len(self.errors)}")

        if self.errors:
            print("\nErrors:")
            for error in self.errors:
                print(f"  - {error}")

        print("\n📁 Interface files created in: services/{consumer}/interfaces/")
        print("\n💡 Usage:")
        print("  - Provider services: Implement the interface (class MyService(ProviderInterface))")
        print("  - Consumer services: Import the interface for type hints")
        print("  - Tests: Mock using the interface for contract testing")
        print("=" * 80)


def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_interface_abc.py /path/to/system_root/")
        sys.exit(1)

    # Security: Validate system path
    try:
        system_path = validate_system_root(sys.argv[1])
    except PathSecurityError as e:
        print(f"ERROR: Path security violation: {e}", file=sys.stderr)
        sys.exit(1)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)

    print("=" * 80)
    print("Interface ABC Generator (v3.10.0)")
    print("=" * 80)
    print(f"System path: {system_path}\n")

    generator = InterfaceABCGenerator(system_path)
    generator.load_data()
    generator.generate_interfaces()
    generator.generate_summary()


if __name__ == "__main__":
    main()
