#!/usr/bin/env python3

import json
import sys
from pathlib import Path
from datetime import datetime
import networkx as nx
from typing import Dict, List, Set, Tuple

class ArchitectureValidator:
    def __init__(self, system_path: Path):
        self.system_path = Path(system_path)
        self.working_memory = self.load_working_memory()
        self.validation_results = {
            "timestamp": datetime.now().isoformat(),
            "system": self.system_path.name,
            "checks": {},
            "issues": []
        }

    def load_working_memory(self) -> dict:
        memory_file = self.system_path / "working_memory.json"
        if memory_file.exists():
            with open(memory_file) as f:
                return json.load(f)
        return {}

    def load_service_files(self) -> Dict[str, dict]:
        services = {}
        for service_file in self.system_path.rglob("service_architecture.json"):
            with open(service_file) as f:
                services[service_file.parent.name] = json.load(f)
        return services

    def validate_interface_consistency(self) -> List[dict]:
        """Check interface consistency across services"""
        issues = []
        services = self.load_service_files()
        interface_registry = self.load_interface_registry()

        for service_name, service in services.items():
            for interface in service.get("interfaces", []):
                # Check interface exists in registry
                if service_name not in interface_registry["interfaces"]:
                    issues.append({
                        "type": "interface_missing",
                        "service": service_name,
                        "interface": interface["name"],
                        "severity": "high"
                    })
                    continue

                reg_interface = interface_registry["interfaces"][service_name].get(interface["name"])
                if not reg_interface:
                    issues.append({
                        "type": "interface_not_registered",
                        "service": service_name,
                        "interface": interface["name"],
                        "severity": "medium"
                    })
                    continue

                # Check interface details match
                for field in ["path", "method", "auth_required"]:
                    if interface.get(field) != reg_interface.get(field):
                        issues.append({
                            "type": "interface_mismatch",
                            "service": service_name,
                            "interface": interface["name"],
                            "field": field,
                            "severity": "high"
                        })

        return issues

    def validate_resource_isolation(self) -> List[dict]:
        """Check resource isolation between services"""
        issues = []
        services = self.load_service_files()
        shared_resources = set()

        # Collect shared resources
        for service in services.values():
            for relationship in service.get("service_resource_relationships", []):
                resource = (relationship["resource_type"], relationship["resource_performer"])
                if resource in shared_resources:
                    issues.append({
                        "type": "shared_resource",
                        "resource": resource[0],
                        "performer": resource[1],
                        "severity": "medium"
                    })
                shared_resources.add(resource)

        return issues

    def validate_dependency_cycles(self) -> List[dict]:
        """Check for circular dependencies"""
        issues = []
        services = self.load_service_files()
        
        # Build dependency graph
        G = nx.DiGraph()
        for service_name, service in services.items():
            G.add_node(service_name)
            for dep in service.get("dependencies", []):
                G.add_edge(service_name, dep)

        # Find cycles
        try:
            cycles = list(nx.simple_cycles(G))
            for cycle in cycles:
                issues.append({
                    "type": "circular_dependency",
                    "cycle": cycle,
                    "severity": "high"
                })
        except Exception as e:
            issues.append({
                "type": "graph_analysis_error",
                "error": str(e),
                "severity": "high"
            })

        return issues

    def load_interface_registry(self) -> dict:
        registry_file = self.system_path / "interface_registry.json"
        if registry_file.exists():
            with open(registry_file) as f:
                return json.load(f)
        return {"interfaces": {}}

    def validate_directory_structure(self) -> List[dict]:
        """Check for empty or incomplete system directories"""
        issues = []
        
        # Find all directories
        for dir_path in self.system_path.rglob('*'):
            if dir_path.is_dir():
                # Skip certain utility directories
                if any(x in str(dir_path) for x in ['__pycache__', '.git', 'interfaces']):
                    continue
                    
                # Check if directory is empty
                if not any(dir_path.iterdir()):
                    issues.append({
                        "type": "empty_directory",
                        "path": str(dir_path),
                        "severity": "high",
                        "description": "Directory exists but contains no files"
                    })
                    continue
                    
                # Check if this is a direct child directory of the system directory (potential service)
                # and doesn't have service_architecture.json
                if (dir_path.parent == self.system_path and 
                    not (dir_path / 'service_architecture.json').exists()):
                    # Only flag if directory contains files but no service_architecture.json
                    if any(f.is_file() for f in dir_path.iterdir()):
                        issues.append({
                            "type": "missing_architecture",
                            "path": str(dir_path),
                            "severity": "high",
                            "description": "System directory missing service_architecture.json"
                        })
        
        return issues

    def run_all_validations(self) -> dict:
        """Run all validation checks"""
        # Directory structure validation
        directory_issues = self.validate_directory_structure()
        self.validation_results["checks"]["directory_structure"] = {
            "status": "fail" if directory_issues else "pass",
            "issues": directory_issues
        }
        # Interface consistency
        interface_issues = self.validate_interface_consistency()
        self.validation_results["checks"]["interface_consistency"] = {
            "status": "fail" if interface_issues else "pass",
            "issues": interface_issues
        }

        # Resource isolation
        resource_issues = self.validate_resource_isolation()
        self.validation_results["checks"]["resource_isolation"] = {
            "status": "fail" if resource_issues else "pass",
            "issues": resource_issues
        }

        # Dependency cycles
        dependency_issues = self.validate_dependency_cycles()
        self.validation_results["checks"]["dependency_cycles"] = {
            "status": "fail" if dependency_issues else "pass",
            "issues": dependency_issues
        }

        # Combine all issues
        self.validation_results["issues"] = interface_issues + resource_issues + dependency_issues

        return self.validation_results

    def update_working_memory(self):
        """Update working memory with validation results"""
        if not self.working_memory:
            return

        self.working_memory["validation_state"] = {
            "interface_consistency": {
                "last_checked": datetime.now().isoformat(),
                "status": self.validation_results["checks"]["interface_consistency"]["status"],
                "issues": self.validation_results["checks"]["interface_consistency"]["issues"]
            },
            "resource_isolation": {
                "last_checked": datetime.now().isoformat(),
                "status": self.validation_results["checks"]["resource_isolation"]["status"],
                "issues": self.validation_results["checks"]["resource_isolation"]["issues"]
            },
            "dependency_cycles": {
                "last_checked": datetime.now().isoformat(),
                "status": self.validation_results["checks"]["dependency_cycles"]["status"],
                "issues": self.validation_results["checks"]["dependency_cycles"]["issues"]
            }
        }

        with open(self.system_path / "working_memory.json", "w") as f:
            json.dump(self.working_memory, f, indent=2)

def main():
    if len(sys.argv) != 2:
        print("Usage: validate_architecture.py <system_path>")
        sys.exit(1)

    system_path = Path(sys.argv[1])
    if not system_path.exists():
        print(f"Error: System path {system_path} does not exist")
        sys.exit(1)

    validator = ArchitectureValidator(system_path)
    results = validator.run_all_validations()
    validator.update_working_memory()

    # Output results
    print(json.dumps(results, indent=2))

    # Exit with status code
    sys.exit(1 if results["issues"] else 0)

if __name__ == "__main__":
    main()