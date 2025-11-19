#!/usr/bin/env python3
"""
Generate Interface Registry from Service Architectures

Automatically creates interface_registry.json by extracting all interfaces
from service_architecture.json files. Ensures field values match exactly
to prevent validation errors.

Usage:
    python3 generate_interface_registry.py /path/to/system_root/

Inputs:
    - specs/machine/service_arch/*/service_architecture.json (all services)
    - specs/machine/index.json (optional - for service catalog)

Outputs:
    - specs/machine/interface_registry.json

Version: 3.18.1
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import defaultdict

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class InterfaceRegistryGenerator:
    """Generate interface registry from service architecture files"""

    def __init__(self, system_root: str):
        """
        Initialize generator

        Args:
            system_root: Path to system root directory

        Raises:
            PathSecurityError: If system_root is invalid
        """
        self.system_root = validate_system_root(system_root)
        self.service_architectures: Dict[str, Dict] = {}
        self.interfaces: Dict[str, Dict[str, Dict]] = defaultdict(dict)
        self.internal_only_services: Dict[str, Dict] = {}

    def load_service_architectures(self):
        """Load all service architecture files"""
        print("Loading service architecture files...")

        service_arch_dir = self.system_root / "specs" / "machine" / "service_arch"
        if not service_arch_dir.exists():
            print(f"❌ Service architecture directory not found: {service_arch_dir}")
            sys.exit(1)

        # Find all service architecture files (prefer symlinks, fallback to versioned)
        service_dirs = [d for d in service_arch_dir.iterdir() if d.is_dir()]

        for service_dir in sorted(service_dirs):
            service_id = service_dir.name

            # Try symlink first, then latest versioned file
            arch_file = service_dir / "service_architecture.json"
            if not arch_file.exists():
                # Find latest versioned file
                versioned_files = sorted(service_dir.glob("service_architecture_v*.json"))
                if versioned_files:
                    arch_file = versioned_files[-1]  # Latest version
                else:
                    print(f"  ⚠️  No architecture file found for {service_id}")
                    continue

            try:
                arch_data = safe_load_json(arch_file)
                self.service_architectures[service_id] = arch_data
                print(f"  ✅ Loaded {service_id}")
            except Exception as e:
                print(f"  ❌ Error loading {service_id}: {e}")

        print(f"\n✅ Loaded {len(self.service_architectures)} service architectures")

    def extract_interfaces(self):
        """Extract all interfaces from service architectures"""
        print("\n📋 Extracting interfaces...")

        interface_count = 0

        for service_id, arch_data in self.service_architectures.items():
            # Check if service is internal-only
            deployment = arch_data.get('deployment', {})
            if deployment.get('internal_only', False):
                self.internal_only_services[service_id] = {
                    'internal_only': True,
                    'justification': deployment.get('internal_only_justification', 'Internal service'),
                    'security_boundary': deployment.get('security_boundary', 'internal_network')
                }

            # Extract interfaces array
            interfaces = arch_data.get('interfaces', [])

            if not isinstance(interfaces, list):
                print(f"  ⚠️  {service_id}: 'interfaces' is not an array, skipping")
                continue

            for iface in interfaces:
                if not isinstance(iface, dict):
                    continue

                # Extract interface details
                interface_name = iface.get('interface_id') or iface.get('name') or iface.get('interface_name', 'unnamed')

                # Build interface entry matching template structure
                interface_entry = {
                    'interface_type': iface.get('interface_type', iface.get('type', 'service_dependency')),
                    'communication_pattern': iface.get('communication_pattern', iface.get('pattern', 'synchronous')),
                    'auth_required': iface.get('auth_required', iface.get('authentication_required', False))
                }

                # Optional fields
                if 'path' in iface:
                    interface_entry['path'] = iface['path']
                if 'method' in iface:
                    interface_entry['method'] = iface['method']
                if 'protocol' in iface:
                    interface_entry['protocol'] = iface['protocol']
                if 'description' in iface:
                    interface_entry['description'] = iface['description']

                # Async details
                if iface.get('communication_pattern') == 'asynchronous' or iface.get('pattern') == 'asynchronous':
                    async_details = {}
                    if 'message_broker' in iface:
                        async_details['message_broker'] = iface['message_broker']
                    if 'exchange_name' in iface:
                        async_details['exchange_name'] = iface['exchange_name']
                    if 'routing_key' in iface:
                        async_details['routing_key'] = iface['routing_key']
                    if 'message_format' in iface:
                        async_details['message_format'] = iface['message_format']

                    if async_details:
                        interface_entry['async_details'] = async_details

                # Add to registry
                self.interfaces[service_id][interface_name] = interface_entry
                interface_count += 1

        print(f"  ✅ Extracted {interface_count} interfaces from {len(self.service_architectures)} services")

    def generate_registry(self) -> Dict:
        """Generate complete interface registry"""
        print("\n🔧 Generating interface registry...")

        # Get system name from first service architecture or working memory
        system_name = "Unknown System"
        if self.service_architectures:
            first_arch = next(iter(self.service_architectures.values()))
            system_name = first_arch.get('system_name', 'Unknown System')

        # Try to get from working memory
        working_memory_path = self.system_root / "context" / "working_memory.json"
        if working_memory_path.exists():
            try:
                wm = safe_load_json(working_memory_path)
                system_name = wm.get('system_name', system_name)
            except:
                pass

        registry = {
            "registry_version": "1.1",
            "system_name": system_name,
            "creation_date": datetime.now().strftime("%Y-%m-%d"),
            "generated_by": "generate_interface_registry.py (automated)",
            "interfaces": dict(self.interfaces)  # Convert defaultdict to regular dict
        }

        # Add internal_only_services if any
        if self.internal_only_services:
            registry["internal_only_services"] = {
                "description": "Services marked as internal-only to suppress irrelevant auth warnings",
                "services": self.internal_only_services
            }

        # Add schema management
        registry["schema_management"] = {
            "schema_version": "1.0",
            "validation_rules": [
                "All message interfaces must specify message_format",
                "Async interfaces must specify message_broker",
                "Internal-only services must have justification"
            ]
        }

        return registry

    def save_registry(self, registry: Dict):
        """Save registry to file"""
        output_path = self.system_root / "specs" / "machine" / "interface_registry.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(registry, f, indent=2)

        print(f"\n✅ Interface registry saved to: {output_path}")

    def print_summary(self, registry: Dict):
        """Print generation summary"""
        print("\n" + "=" * 70)
        print("INTERFACE REGISTRY GENERATION SUMMARY")
        print("=" * 70)

        print(f"\n📊 Statistics:")
        print(f"  Services: {len(registry['interfaces'])}")
        total_interfaces = sum(len(interfaces) for interfaces in registry['interfaces'].values())
        print(f"  Total Interfaces: {total_interfaces}")

        if registry.get('internal_only_services'):
            print(f"  Internal-Only Services: {len(registry['internal_only_services']['services'])}")

        print(f"\n📁 Output:")
        print(f"  specs/machine/interface_registry.json")

        print(f"\n⚠️  NEXT STEPS:")
        print(f"  1. Review generated registry for correctness")
        print(f"  2. Run validation: python3 tools/validate_architecture.py {self.system_root}")
        print(f"  3. Fix any interface_mismatch errors by updating service_architecture.json files")
        print(f"  4. Re-generate registry if service architectures change")

        print("\n✅ Interface registry generation complete!")

    def run(self):
        """Run the generation process"""
        try:
            self.load_service_architectures()
            self.extract_interfaces()
            registry = self.generate_registry()
            self.save_registry(registry)
            self.print_summary(registry)
        except Exception as e:
            print(f"\n❌ Error during registry generation: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)


def main():
    """Main entry point"""
    if len(sys.argv) != 2:
        print("Usage: python3 generate_interface_registry.py /path/to/system_root/")
        print("\nGenerates interface_registry.json from service_architecture.json files")
        sys.exit(1)

    system_root = sys.argv[1]
    generator = InterfaceRegistryGenerator(system_root)
    generator.run()


if __name__ == "__main__":
    main()
