#!/usr/bin/env python3
"""
Generate Service Interface Contracts

This tool generates SERVICE_CONTRACT.json files for each service, embedding
architectural contracts that warn LLMs before making breaking changes.

The service contract acts as a "hook" that prevents architectural drift by
declaring:
- Contracted functions (WHAT the service must implement)
- Contracted interfaces (WHO the service talks to)
- Reference to system architecture (WHERE the source of truth lives)
- Warning messages for LLMs (WHY changes require architecture updates)

Purpose: Proactive drift prevention - warn LLMs BEFORE changes, not AFTER

Usage:
    python3 generate_service_contracts.py <system_root> [--service SERVICE_NAME]

Inputs:
    - specs/machine/service_arch/{service}/service_architecture_v*.json
    - specs/machine/graphs/system_of_systems_graph.json
    - specs/machine/interface_registry.json

Outputs:
    - services/{service}/SERVICE_CONTRACT.json (for each service)

Integration Points:
    - D-02-A05: Generate contracts after domain model implementation
    - D-06.5-A04.5: Regenerate contracts when architecture changes

Version: 3.17.0 - Service Interface Contracts feature
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import glob
import re

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class ServiceContractGenerator:
    """Generate service interface contracts from architecture specifications"""

    def __init__(self, system_root: Path):
        """
        Initialize generator with system root path

        Args:
            system_root: Path to system root directory
        """
        try:
            self.system_root = validate_system_root(system_root)
        except PathSecurityError as e:
            raise ValueError(f"Invalid system root: {e}")

        self.specs_machine = self.system_root / "specs" / "machine"
        self.services_dir = self.system_root / "services"
        self.templates_dir = Path(__file__).parent.parent / "templates"

        # Load template
        try:
            template_file = sanitize_path(
                "service_contract_template.json",
                self.templates_dir,
                must_exist=True
            )
            self.template = safe_load_json(
                template_file,
                file_type_description="service contract template"
            )
        except (PathSecurityError, JSONValidationError) as e:
            raise ValueError(f"Failed to load template: {e}")

    def load_system_graph(self) -> Dict[str, Any]:
        """Load system of systems graph"""
        try:
            graph_file = sanitize_path(
                "graphs/system_of_systems_graph.json",
                self.specs_machine,
                must_exist=True
            )
            return safe_load_json(graph_file, file_type_description="system graph")
        except (PathSecurityError, JSONValidationError) as e:
            raise ValueError(f"Failed to load system graph: {e}")

    def load_interface_registry(self) -> Dict[str, Any]:
        """Load interface registry"""
        try:
            registry_file = sanitize_path(
                "interface_registry.json",
                self.specs_machine,
                must_exist=False
            )
            if registry_file.exists():
                return safe_load_json(
                    registry_file,
                    file_type_description="interface registry"
                )
            else:
                return {"interfaces": []}
        except (PathSecurityError, JSONValidationError) as e:
            print(f"⚠️  Warning: Failed to load interface registry: {e}")
            return {"interfaces": []}

    def find_service_architecture(self, service_name: str) -> Optional[Path]:
        """
        Find the latest service architecture file for a service

        Args:
            service_name: Name of the service

        Returns:
            Path to service_architecture_v*.json or None if not found
        """
        service_arch_dir = self.specs_machine / "service_arch" / service_name
        if not service_arch_dir.exists():
            return None

        # Find all versioned architecture files
        arch_files = list(service_arch_dir.glob("service_architecture_v*.json"))
        if not arch_files:
            # Try unversioned file
            unversioned = service_arch_dir / "service_architecture.json"
            if unversioned.exists():
                return unversioned
            return None

        # Sort by version (extract version from filename)
        def extract_version(path: Path) -> tuple:
            match = re.search(r'v(\d+)\.(\d+)\.(\d+)', path.name)
            if match:
                return tuple(map(int, match.groups()))
            return (0, 0, 0)

        arch_files.sort(key=extract_version, reverse=True)
        return arch_files[0]

    def load_service_architecture(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Load service architecture specification

        Args:
            service_name: Name of the service

        Returns:
            Service architecture dict or None if not found
        """
        arch_file = self.find_service_architecture(service_name)
        if not arch_file:
            return None

        try:
            return safe_load_json(
                arch_file,
                file_type_description=f"service architecture for {service_name}"
            )
        except JSONValidationError as e:
            print(f"⚠️  Warning: Failed to load architecture for {service_name}: {e}")
            return None

    def extract_contracted_functions(
        self,
        service_arch: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """
        Extract contracted functions from service architecture

        Args:
            service_arch: Service architecture specification

        Returns:
            List of function contracts
        """
        functions = []

        # Extract from components
        system_view = service_arch.get("system_view", {})
        components = system_view.get("components", [])

        for component in components:
            component_functions = component.get("functions", [])
            for func in component_functions:
                functions.append({
                    "function_id": func.get("id", "unknown"),
                    "function_name": func.get("name", "Unknown"),
                    "description": func.get("description", "No description"),
                    "source": "Derived from service_architecture.json → components → functions"
                })

        return functions

    def extract_provided_interfaces(
        self,
        service_name: str,
        graph: Dict[str, Any],
        interface_registry: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract interfaces provided by this service

        Args:
            service_name: Name of the service
            graph: System of systems graph
            interface_registry: Interface registry

        Returns:
            List of provided interface contracts
        """
        provided = []

        # Find all edges where this service is the provider
        edges = graph.get("edges", [])
        for edge in edges:
            if edge.get("provider") == service_name:
                interface_name = edge.get("interface")
                consumer = edge.get("consumer")

                # Find interface in registry
                icd_file = f"specs/machine/interfaces/{interface_name}_icd.json"

                # Check if already added
                existing = next(
                    (p for p in provided if p["interface_name"] == interface_name),
                    None
                )

                if existing:
                    # Add consumer to existing interface
                    if consumer not in existing["consumers"]:
                        existing["consumers"].append(consumer)
                        existing["breaking_change_impact"] = (
                            f"Modifying this interface affects "
                            f"{len(existing['consumers'])} consumer services"
                        )
                else:
                    # Add new provided interface
                    provided.append({
                        "interface_id": interface_name,
                        "interface_name": interface_name,
                        "icd_file": icd_file,
                        "consumers": [consumer],
                        "breaking_change_impact": (
                            f"Modifying this interface affects 1 consumer service"
                        )
                    })

        return provided

    def extract_consumed_interfaces(
        self,
        service_name: str,
        graph: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Extract interfaces consumed by this service

        Args:
            service_name: Name of the service
            graph: System of systems graph

        Returns:
            List of consumed interface contracts
        """
        consumed = []

        # Find all edges where this service is the consumer
        edges = graph.get("edges", [])
        for edge in edges:
            if edge.get("consumer") == service_name:
                interface_name = edge.get("interface")
                provider = edge.get("provider")

                icd_file = f"specs/machine/interfaces/{interface_name}_icd.json"

                consumed.append({
                    "interface_id": interface_name,
                    "interface_name": interface_name,
                    "provider_service": provider,
                    "icd_file": icd_file
                })

        return consumed

    def generate_contract(self, service_name: str) -> Dict[str, Any]:
        """
        Generate service contract for a single service

        Args:
            service_name: Name of the service

        Returns:
            Service contract dictionary
        """
        print(f"\n🔨 Generating contract for service: {service_name}")

        # Load architecture
        service_arch = self.load_service_architecture(service_name)
        if not service_arch:
            raise ValueError(f"Service architecture not found for {service_name}")

        # Load graph and registry
        graph = self.load_system_graph()
        interface_registry = self.load_interface_registry()

        # Extract architecture version
        arch_file = self.find_service_architecture(service_name)
        arch_version_match = re.search(r'v(\d+\.\d+\.\d+)', arch_file.name)
        arch_version = arch_version_match.group(1) if arch_version_match else "1.0.0"

        # Extract contracted functions
        functions = self.extract_contracted_functions(service_arch)

        # Extract interfaces
        provided = self.extract_provided_interfaces(
            service_name,
            graph,
            interface_registry
        )
        consumed = self.extract_consumed_interfaces(service_name, graph)

        # Build contract
        contract = {
            "service_name": service_name,
            "contract_version": "1.0.0",
            "contract_date": datetime.now().strftime("%Y-%m-%d"),
            "architecture_reference": {
                "description": "Pointer to the authoritative system architecture that defines this service",
                "service_architecture_file": (
                    f"specs/machine/service_arch/{service_name}/"
                    f"service_architecture_v{arch_version}.json"
                ),
                "graph_node_id": service_name,
                "graph_file": "specs/machine/graphs/system_of_systems_graph.json",
                "last_architecture_sync": datetime.now().strftime("%Y-%m-%d"),
                "architecture_version": arch_version
            },
            "contracted_functions": {
                "description": "Functions this service MUST implement (from functional architecture)",
                "functions": functions,
                "function_count": len(functions),
                "warning": (
                    "DO NOT add, remove, or substantially modify these functions "
                    "without updating the functional architecture "
                    "(specs/machine/service_arch/) and regenerating the system of "
                    "systems graph. Changes to contracted functions may break "
                    "dependent services."
                )
            },
            "contracted_interfaces": {
                "description": "Interfaces this service MUST provide and consume",
                "provides": provided,
                "consumes": consumed,
                "provides_count": len(provided),
                "consumes_count": len(consumed),
                "warning": (
                    "DO NOT modify provided interfaces without updating ICDs and "
                    "notifying consumer services. DO NOT modify consumed interfaces - "
                    "contact the provider service owner instead. All interface "
                    "changes require re-running systems engineering workflows "
                    "(01b or 01c)."
                )
            },
            "llm_warnings": {
                "before_modifying_functions": (
                    f"⚠️  WARNING: This service has {len(functions)} contracted "
                    f"functions. Adding, removing, or substantially changing function "
                    f"behavior requires updating the functional architecture. Run "
                    f"workflow 01d-functional_analysis or 01b/01c to update "
                    f"architecture first, then regenerate this contract."
                ),
                "before_modifying_interfaces": (
                    f"⚠️  WARNING: This service provides {len(provided)} interfaces "
                    f"consumed by other services. Interface changes are BREAKING "
                    f"changes. Update ICDs (specs/machine/interfaces/), notify "
                    f"consumers, and re-run systems engineering workflows before "
                    f"making changes."
                ),
                "before_adding_dependencies": (
                    "⚠️  WARNING: Adding new service dependencies (consuming new "
                    "interfaces) changes the system architecture. Update the system "
                    "of systems graph and interface registry before adding imports "
                    "or API clients."
                ),
                "drift_detection": (
                    "If you see differences between this contract and the actual "
                    "implementation, run D-06 (As-Built Architecture Generation) and "
                    "D-06.5 (Architecture Synchronization Loop) to reconcile the drift."
                )
            },
            "validation_status": {
                "last_validated": "never",
                "validation_tool": "tools/validate_service_contracts.py",
                "validation_result": "pending",
                "deviations_detected": False,
                "deviations": []
            }
        }

        print(f"  ✅ Contracted functions: {len(functions)}")
        print(f"  ✅ Provides interfaces: {len(provided)}")
        print(f"  ✅ Consumes interfaces: {len(consumed)}")

        return contract

    def write_contract(self, service_name: str, contract: Dict[str, Any]) -> Path:
        """
        Write service contract to file

        Args:
            service_name: Name of the service
            contract: Service contract dictionary

        Returns:
            Path to written contract file
        """
        service_dir = self.services_dir / service_name
        if not service_dir.exists():
            service_dir.mkdir(parents=True, exist_ok=True)
            print(f"  📁 Created service directory: {service_dir}")

        contract_file = service_dir / "SERVICE_CONTRACT.json"

        with open(contract_file, 'w', encoding='utf-8') as f:
            json.dump(contract, f, indent=2, ensure_ascii=False)

        print(f"  💾 Contract written to: {contract_file}")

        return contract_file

    def generate_all_contracts(self) -> List[Path]:
        """
        Generate contracts for all services

        Returns:
            List of paths to generated contract files
        """
        print("🚀 Generating service contracts for all services...\n")

        # Load graph to find all services
        graph = self.load_system_graph()
        nodes = graph.get("nodes", [])

        if not nodes:
            print("⚠️  No services found in system graph")
            return []

        contract_files = []

        for node in nodes:
            service_name = node.get("id")
            if not service_name:
                continue

            try:
                contract = self.generate_contract(service_name)
                contract_file = self.write_contract(service_name, contract)
                contract_files.append(contract_file)
            except Exception as e:
                print(f"  ❌ Failed to generate contract: {e}")
                continue

        print(f"\n✅ Generated {len(contract_files)} service contracts")
        return contract_files

    def generate_single_contract(self, service_name: str) -> Path:
        """
        Generate contract for a single service

        Args:
            service_name: Name of the service

        Returns:
            Path to generated contract file
        """
        print(f"🚀 Generating service contract for {service_name}...\n")

        contract = self.generate_contract(service_name)
        contract_file = self.write_contract(service_name, contract)

        print(f"\n✅ Generated contract for {service_name}")
        return contract_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Generate service interface contracts from architecture specifications"
    )
    parser.add_argument(
        "system_root",
        type=Path,
        help="Path to system root directory"
    )
    parser.add_argument(
        "--service",
        type=str,
        help="Generate contract for single service (default: all services)"
    )

    args = parser.parse_args()

    try:
        generator = ServiceContractGenerator(args.system_root)

        if args.service:
            generator.generate_single_contract(args.service)
        else:
            generator.generate_all_contracts()

        return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
