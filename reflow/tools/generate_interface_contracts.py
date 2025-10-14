#!/usr/bin/env python3
"""
Generate Interface Contract Documents (ICDs) from service architecture files.

This tool analyzes service_architecture.json files and generates detailed
interface contracts for each interface between components, enabling
independent development with guaranteed integration success.

Usage:
    python3 generate_interface_contracts.py /path/to/systems/<system_name>/
    
Output:
    Creates /systems/<system_name>/interfaces/<interface_id>.json for each interface
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Set
from datetime import datetime

class InterfaceContractGenerator:
    def __init__(self, system_path: str):
        self.system_path = Path(system_path)
        self.index_file = self.system_path / "index.json"
        self.interfaces_dir = self.system_path / "interfaces"
        self.template_path = Path(__file__).parent.parent / "templates" / "interface_contract_template.json"
        
        # Load template
        with open(self.template_path, 'r') as f:
            self.template = json.load(f)
            
        # Create interfaces directory
        self.interfaces_dir.mkdir(exist_ok=True)
        
        self.components = {}
        self.interfaces_generated = []
        self.interfaces_map = {}  # interface_id -> contract
        
    def load_components(self):
        """Load all component specifications from index"""
        if not self.index_file.exists():
            print(f"Error: Index file not found at {self.index_file}")
            sys.exit(1)
            
        with open(self.index_file, 'r') as f:
            index = json.load(f)
            
        for component_id, component_path in index.get('components', {}).items():
            if not os.path.isabs(component_path):
                component_path = self.system_path / component_path
            else:
                component_path = Path(component_path)
                
            if component_path.exists():
                try:
                    with open(component_path, 'r') as f:
                        self.components[component_id] = json.load(f)
                except json.JSONDecodeError as e:
                    print(f"Warning: Could not parse {component_path}: {e}")
            else:
                print(f"Warning: Component file not found: {component_path}")
                
        print(f"Loaded {len(self.components)} components")
        
    def extract_interfaces(self):
        """Extract all interfaces from component specifications"""
        interface_pairs = []
        
        for component_id, spec in self.components.items():
            # Get dependencies (consumers)
            dependencies = spec.get('dependencies', [])
            if isinstance(dependencies, dict):
                dependencies = dependencies.get('required_services', [])
            if isinstance(dependencies, list) and dependencies and isinstance(dependencies[0], dict):
                dependencies = [d.get('service_name', d) for d in dependencies]
                
            # Extract interfaces from spec
            interfaces = spec.get('interfaces', [])
            
            # Handle different interface formats
            if isinstance(interfaces, dict):
                # Format: {"provided": [...], "required": [...]}
                for provided in interfaces.get('provided', []):
                    for dep_id in dependencies:
                        if dep_id in self.components:
                            interface_pairs.append({
                                'provider': component_id,
                                'consumer': dep_id,
                                'interface_def': provided,
                                'direction': 'provided'
                            })
                            
                for required in interfaces.get('required', []):
                    target = required.get('service', required.get('target_service'))
                    if target and target in self.components:
                        interface_pairs.append({
                            'provider': target,
                            'consumer': component_id,
                            'interface_def': required,
                            'direction': 'required'
                        })
            elif isinstance(interfaces, list):
                # Format: list of interface objects
                for iface in interfaces:
                    for dep_id in dependencies:
                        if dep_id in self.components:
                            interface_pairs.append({
                                'provider': component_id,
                                'consumer': dep_id,
                                'interface_def': iface,
                                'direction': 'unknown'
                            })
                            
        print(f"Extracted {len(interface_pairs)} interface pairs")
        return interface_pairs
        
    def generate_interface_contract(self, provider: str, consumer: str, interface_def: Dict) -> Dict:
        """Generate a complete interface contract from interface definition"""
        
        # Create interface ID
        interface_name = interface_def.get('name', 'unnamed_interface')
        interface_id = f"{provider}_to_{consumer}_{interface_name}"
        
        # Determine interaction type
        comm_pattern = interface_def.get('communication_pattern', 
                                        interface_def.get('type', 'synchronous'))
        interaction_map = {
            'synchronous': 'synchronous',
            'asynchronous': 'asynchronous',
            'bidirectional': 'bidirectional',
            'pubsub': 'broadcast',
            'rest': 'synchronous',
            'websocket': 'bidirectional',
            'grpc': 'synchronous'
        }
        interaction_type = interaction_map.get(comm_pattern, 'synchronous')
        
        # Determine format from interface type
        iface_type = interface_def.get('interface_type', interface_def.get('protocol', 'json'))
        format_map = {
            'http_endpoint': 'json',
            'message': 'json',
            'pubsub': 'json',
            'grpc': 'protobuf',
            'rest': 'json',
            'HTTPS': 'json',
            'AMQP': 'json',
            'WSS': 'json'
        }
        format_type = format_map.get(iface_type, 'json')
        
        # Build contract
        contract = {
            "template_version": "1.0",
            "interface_id": interface_id,
            "provider_component": provider,
            "consumer_component": consumer,
            "interaction_type": interaction_type,
            "domain_type": "software",  # Default, could be inferred from system
            "contract": {
                "input_specification": {
                    "format": format_type,
                    "schema": interface_def.get('request_schema', interface_def.get('message_format', {})),
                    "constraints": self._extract_constraints(interface_def),
                    "examples": self._generate_examples(interface_def, 'input'),
                    "validation_rules": []
                },
                "output_specification": {
                    "format": format_type,
                    "schema": interface_def.get('response_schema', {}),
                    "success_criteria": "Response matches schema and contains expected fields",
                    "examples": self._generate_examples(interface_def, 'output'),
                    "validation_rules": []
                },
                "error_handling": {
                    "error_conditions": self._extract_error_conditions(interface_def),
                    "error_responses": [],
                    "retry_policy": {
                        "applicable": "yes" if interaction_type == "asynchronous" else "no",
                        "max_retries": 3,
                        "backoff_strategy": "exponential"
                    },
                    "fallback_behavior": "Log error and return error response to consumer"
                },
                "timing_constraints": {
                    "max_latency": interface_def.get('max_latency', 'none'),
                    "throughput_requirements": interface_def.get('throughput', 'none'),
                    "synchronization_requirements": "depends_on_interaction_type"
                },
                "state_requirements": {
                    "stateful": interface_def.get('stateful', False),
                    "state_description": interface_def.get('state_description', 'none'),
                    "state_persistence": "none"
                }
            },
            "integration_tests": {
                "test_scenarios": self._generate_test_scenarios(interface_def),
                "contract_verification": {
                    "provider_verification": f"Provider must implement interface matching {interface_id} specification",
                    "consumer_verification": f"Consumer must call interface according to {interface_id} specification",
                    "integration_verification": "Run integration test scenarios to verify end-to-end interaction"
                },
                "mock_specifications": {
                    "provider_mock": f"Mock {provider} that returns responses matching output_specification",
                    "consumer_mock": f"Mock {consumer} that sends requests matching input_specification"
                }
            },
            "dependencies": {
                "depends_on_interfaces": [],
                "environmental_dependencies": self._extract_env_dependencies(interface_def)
            },
            "metadata": {
                "version": f"1.0+{datetime.now().strftime('%Y-%m-%d')}",
                "last_updated": datetime.now().strftime('%Y-%m-%d'),
                "status": "draft",
                "backwards_compatible": True,
                "breaking_changes": [],
                "rationale": interface_def.get('description', f"Interface between {provider} and {consumer}"),
                "alternatives_considered": []
            }
        }
        
        return contract
        
    def _extract_constraints(self, interface_def: Dict) -> List[str]:
        """Extract constraints from interface definition"""
        constraints = []
        
        if interface_def.get('auth_required'):
            constraints.append("Authentication required")
        if 'rate_limit' in interface_def:
            constraints.append(f"Rate limit: {interface_def['rate_limit']}")
        if 'path' in interface_def:
            constraints.append(f"HTTP path: {interface_def['path']}")
        if 'method' in interface_def:
            constraints.append(f"HTTP method: {interface_def['method']}")
            
        return constraints
        
    def _extract_error_conditions(self, interface_def: Dict) -> List[Dict]:
        """Extract error conditions from interface definition"""
        return [
            {
                "error_id": "INVALID_INPUT",
                "condition": "Input does not match schema",
                "severity": "high"
            },
            {
                "error_id": "AUTH_FAILED",
                "condition": "Authentication failed",
                "severity": "critical"
            },
            {
                "error_id": "SERVICE_UNAVAILABLE",
                "condition": "Provider service is unavailable",
                "severity": "critical"
            }
        ]
        
    def _generate_examples(self, interface_def: Dict, io_type: str) -> List[Dict]:
        """Generate example inputs/outputs"""
        examples = []
        
        if io_type == 'input':
            schema = interface_def.get('request_schema', interface_def.get('message_format', {}))
            if schema:
                examples.append({
                    "example_id": "example_input_1",
                    "description": "Example request",
                    "value": self._generate_example_from_schema(schema)
                })
        else:
            schema = interface_def.get('response_schema', {})
            if schema:
                examples.append({
                    "example_id": "example_output_1",
                    "description": "Example response",
                    "value": self._generate_example_from_schema(schema),
                    "corresponding_input": "example_input_1"
                })
                
        return examples
        
    def _generate_example_from_schema(self, schema: Dict) -> Any:
        """Generate example data from schema"""
        if isinstance(schema, dict) and 'schema' in schema:
            schema = schema['schema']
            
        if isinstance(schema, dict):
            example = {}
            for key, value_type in schema.items():
                if value_type == 'string':
                    example[key] = f"example_{key}"
                elif value_type == 'integer' or value_type == 'number':
                    example[key] = 0
                elif value_type == 'boolean':
                    example[key] = True
                elif value_type == 'array':
                    example[key] = []
                elif value_type == 'object':
                    example[key] = {}
                else:
                    example[key] = f"example_{key}"
            return example
        return {}
        
    def _generate_test_scenarios(self, interface_def: Dict) -> List[Dict]:
        """Generate test scenarios for interface"""
        return [
            {
                "scenario_id": "happy_path",
                "description": "Successful interface interaction",
                "input": self._generate_example_from_schema(
                    interface_def.get('request_schema', interface_def.get('message_format', {}))
                ),
                "expected_output": self._generate_example_from_schema(
                    interface_def.get('response_schema', {})
                ),
                "success_criteria": "Output matches expected_output schema",
                "execution_steps": [
                    "Setup: Initialize provider and consumer",
                    "Execute: Consumer calls interface with test input",
                    "Verify: Check output matches expected schema and values"
                ]
            },
            {
                "scenario_id": "invalid_input",
                "description": "Test invalid input handling",
                "input": {},
                "expected_error": "INVALID_INPUT",
                "success_criteria": "Provider returns appropriate error response"
            }
        ]
        
    def _extract_env_dependencies(self, interface_def: Dict) -> List[str]:
        """Extract environmental dependencies"""
        deps = []
        
        protocol = interface_def.get('protocol', interface_def.get('interface_type', ''))
        if 'HTTPS' in protocol or 'http' in protocol.lower():
            deps.append("network_connectivity")
        if 'AMQP' in protocol:
            deps.append("message_broker_available")
        if interface_def.get('auth_required'):
            deps.append("authentication_service_available")
            
        return deps
        
    def generate_all_contracts(self):
        """Generate all interface contracts"""
        interface_pairs = self.extract_interfaces()
        
        for pair in interface_pairs:
            contract = self.generate_interface_contract(
                pair['provider'],
                pair['consumer'],
                pair['interface_def']
            )
            
            interface_id = contract['interface_id']
            contract_path = self.interfaces_dir / f"{interface_id}.json"
            
            with open(contract_path, 'w') as f:
                json.dump(contract, f, indent=2)
                
            self.interfaces_generated.append(interface_id)
            self.interfaces_map[interface_id] = contract
            
        print(f"\nGenerated {len(self.interfaces_generated)} interface contracts")
        print(f"Saved to: {self.interfaces_dir}/")
        
    def generate_summary(self):
        """Generate summary of interface contracts"""
        summary = {
            "system_path": str(self.system_path),
            "generation_date": datetime.now().isoformat(),
            "total_interfaces": len(self.interfaces_generated),
            "interfaces": []
        }
        
        for interface_id, contract in self.interfaces_map.items():
            summary['interfaces'].append({
                "interface_id": interface_id,
                "provider": contract['provider_component'],
                "consumer": contract['consumer_component'],
                "interaction_type": contract['interaction_type'],
                "status": contract['metadata']['status']
            })
            
        summary_path = self.interfaces_dir / "interfaces_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
            
        print(f"Summary saved to: {summary_path}")
        
def main():
    if len(sys.argv) != 2:
        print("Usage: python3 generate_interface_contracts.py /path/to/systems/<system_name>/")
        sys.exit(1)
        
    system_path = sys.argv[1]
    
    print("=" * 80)
    print("Interface Contract Generator")
    print("=" * 80)
    print(f"System path: {system_path}\n")
    
    generator = InterfaceContractGenerator(system_path)
    generator.load_components()
    generator.generate_all_contracts()
    generator.generate_summary()
    
    print("\n" + "=" * 80)
    print("Interface contract generation complete!")
    print("=" * 80)
    
if __name__ == "__main__":
    main()
