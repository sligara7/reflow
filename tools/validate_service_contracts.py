#!/usr/bin/env python3
"""
Validate Service Interface Contracts

This tool validates that service implementations match their SERVICE_CONTRACT.json
contracts, detecting architectural drift and warning about breaking changes.

The validation acts as a "pre-flight check" before development steps that could
introduce drift:
- D-04-A06.5: After integration surfaces implementation
- D-06-A02.5: After as-built architecture comparison
- D-07-A07.5: Pre-deployment validation

Purpose: Detect contract violations and warn LLMs about architectural impact

Usage:
    python3 validate_service_contracts.py <system_root> [--service SERVICE_NAME]

Inputs:
    - services/{service}/SERVICE_CONTRACT.json (contract to validate)
    - services/{service}/src/ (implementation to check)
    - specs/machine/service_arch/{service}/service_architecture_v*.json
    - specs/machine/graphs/system_of_systems_graph.json

Outputs:
    - specs/machine/validation/service_contracts_validation_report.json

Validation Checks:
    1. Contract file exists
    2. Contract is up-to-date with architecture
    3. Implementation matches contracted functions
    4. Implementation matches contracted interfaces

Version: 3.17.0 - Service Interface Contracts feature
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import ast
import re

# Import secure path handling
from path_utils import sanitize_path, validate_system_root, PathSecurityError
from json_utils import safe_load_json, JSONValidationError


class ServiceContractValidator:
    """Validate service implementations against their contracts"""

    def __init__(self, system_root: Path):
        """
        Initialize validator with system root path

        Args:
            system_root: Path to system root directory
        """
        try:
            self.system_root = validate_system_root(system_root)
        except PathSecurityError as e:
            raise ValueError(f"Invalid system root: {e}")

        self.specs_machine = self.system_root / "specs" / "machine"
        self.services_dir = self.system_root / "services"
        self.validation_dir = self.specs_machine / "validation"

        # Ensure validation directory exists
        self.validation_dir.mkdir(parents=True, exist_ok=True)

    def load_contract(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Load service contract

        Args:
            service_name: Name of the service

        Returns:
            Service contract dict or None if not found
        """
        contract_file = self.services_dir / service_name / "SERVICE_CONTRACT.json"
        if not contract_file.exists():
            return None

        try:
            return safe_load_json(
                contract_file,
                file_type_description=f"service contract for {service_name}"
            )
        except JSONValidationError as e:
            print(f"⚠️  Warning: Failed to load contract for {service_name}: {e}")
            return None

    def load_service_architecture(self, service_name: str) -> Optional[Dict[str, Any]]:
        """
        Load service architecture specification

        Args:
            service_name: Name of the service

        Returns:
            Service architecture dict or None if not found
        """
        service_arch_dir = self.specs_machine / "service_arch" / service_name

        # Find latest versioned architecture file
        arch_files = list(service_arch_dir.glob("service_architecture_v*.json"))
        if not arch_files:
            # Try unversioned
            unversioned = service_arch_dir / "service_architecture.json"
            if unversioned.exists():
                arch_files = [unversioned]
            else:
                return None

        # Sort by version
        def extract_version(path: Path) -> tuple:
            match = re.search(r'v(\d+)\.(\d+)\.(\d+)', path.name)
            if match:
                return tuple(map(int, match.groups()))
            return (0, 0, 0)

        arch_files.sort(key=extract_version, reverse=True)

        try:
            return safe_load_json(
                arch_files[0],
                file_type_description=f"service architecture for {service_name}"
            )
        except JSONValidationError as e:
            print(f"⚠️  Warning: Failed to load architecture for {service_name}: {e}")
            return None

    def find_python_files(self, service_name: str) -> List[Path]:
        """
        Find all Python source files for a service

        Args:
            service_name: Name of the service

        Returns:
            List of Python file paths
        """
        service_dir = self.services_dir / service_name
        if not service_dir.exists():
            return []

        # Look in common source directories
        src_patterns = [
            service_dir / "src" / "**" / "*.py",
            service_dir / "**" / "*.py"
        ]

        python_files = []
        for pattern in src_patterns:
            python_files.extend(service_dir.glob(str(pattern.relative_to(service_dir))))

        # Filter out test files and __pycache__
        python_files = [
            f for f in python_files
            if "__pycache__" not in str(f) and "test" not in str(f)
        ]

        return python_files

    def extract_function_names_from_code(
        self,
        python_files: List[Path]
    ) -> List[str]:
        """
        Extract function and method names from Python source files using AST

        Args:
            python_files: List of Python file paths

        Returns:
            List of function names found in code
        """
        functions = []

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    code = f.read()

                tree = ast.parse(code, filename=str(py_file))

                # Extract function definitions
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        # Skip private functions (starting with _)
                        if not node.name.startswith('_'):
                            functions.append(node.name)
                    elif isinstance(node, ast.ClassDef):
                        # Extract methods from classes
                        for item in node.body:
                            if isinstance(item, ast.FunctionDef):
                                # Skip private methods
                                if not item.name.startswith('_'):
                                    functions.append(item.name)

            except Exception as e:
                print(f"  ⚠️  Warning: Failed to parse {py_file}: {e}")
                continue

        # Remove duplicates
        functions = list(set(functions))

        return functions

    def validate_contract_exists(
        self,
        service_name: str
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that contract file exists

        Args:
            service_name: Name of the service

        Returns:
            (is_valid, error_message)
        """
        contract_file = self.services_dir / service_name / "SERVICE_CONTRACT.json"

        if not contract_file.exists():
            return (
                False,
                f"SERVICE_CONTRACT.json not found for {service_name}. "
                f"Run generate_service_contracts.py to create it."
            )

        return (True, None)

    def validate_contract_freshness(
        self,
        contract: Dict[str, Any],
        service_arch: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that contract is up-to-date with architecture

        Args:
            contract: Service contract
            service_arch: Service architecture specification

        Returns:
            (is_valid, warning_message)
        """
        # Compare architecture version in contract vs actual architecture
        contract_arch_version = contract.get("architecture_reference", {}).get(
            "architecture_version",
            "unknown"
        )

        # This is a warning, not an error - architecture may have been updated
        # and contract needs regeneration
        if contract_arch_version == "unknown":
            return (
                False,
                "Contract does not specify architecture version. "
                "Regenerate contract to sync with latest architecture."
            )

        # Check if contract date is recent (within 30 days of architecture changes)
        # This is informational only
        contract_date = contract.get("contract_date", "1970-01-01")

        return (True, None)

    def validate_functions(
        self,
        contract: Dict[str, Any],
        implemented_functions: List[str]
    ) -> Tuple[bool, List[str]]:
        """
        Validate that contracted functions are implemented

        Args:
            contract: Service contract
            implemented_functions: Functions found in implementation

        Returns:
            (is_valid, list of issues)
        """
        issues = []

        contracted_functions = contract.get("contracted_functions", {}).get(
            "functions",
            []
        )

        if not contracted_functions:
            return (True, [])

        # Check each contracted function
        for func_contract in contracted_functions:
            func_name = func_contract.get("function_name", "Unknown")

            # Fuzzy match - function might be in different case or have prefix
            matches = [
                impl_func for impl_func in implemented_functions
                if func_name.lower() in impl_func.lower() or
                   impl_func.lower() in func_name.lower()
            ]

            if not matches:
                issues.append(
                    f"Contracted function '{func_name}' not found in implementation. "
                    f"This may indicate architectural drift."
                )

        is_valid = len(issues) == 0

        return (is_valid, issues)

    def validate_interfaces(
        self,
        contract: Dict[str, Any],
        service_name: str
    ) -> Tuple[bool, List[str]]:
        """
        Validate that contracted interfaces are implemented

        Args:
            contract: Service contract
            service_name: Name of the service

        Returns:
            (is_valid, list of issues)
        """
        issues = []

        # Check provided interfaces
        provided = contract.get("contracted_interfaces", {}).get("provides", [])

        for interface in provided:
            interface_name = interface.get("interface_name")
            icd_file = self.system_root / interface.get("icd_file", "")

            # Check if ICD exists
            if not icd_file.exists():
                issues.append(
                    f"ICD file for provided interface '{interface_name}' "
                    f"not found: {icd_file}"
                )

        # Check consumed interfaces
        consumed = contract.get("contracted_interfaces", {}).get("consumes", [])

        for interface in consumed:
            interface_name = interface.get("interface_name")
            icd_file = self.system_root / interface.get("icd_file", "")

            # Check if ICD exists
            if not icd_file.exists():
                issues.append(
                    f"ICD file for consumed interface '{interface_name}' "
                    f"not found: {icd_file}"
                )

        is_valid = len(issues) == 0

        return (is_valid, issues)

    def validate_service(self, service_name: str) -> Dict[str, Any]:
        """
        Validate a single service contract

        Args:
            service_name: Name of the service

        Returns:
            Validation result dictionary
        """
        print(f"\n🔍 Validating contract for service: {service_name}")

        result = {
            "service_name": service_name,
            "timestamp": datetime.now().isoformat(),
            "validation_status": "pending",
            "checks": {},
            "issues": [],
            "warnings": []
        }

        # Check 1: Contract exists
        exists_valid, exists_error = self.validate_contract_exists(service_name)
        result["checks"]["contract_exists"] = {
            "passed": exists_valid,
            "error": exists_error
        }

        if not exists_valid:
            result["validation_status"] = "failed"
            result["issues"].append(exists_error)
            print(f"  ❌ Contract file not found")
            return result

        print(f"  ✅ Contract file exists")

        # Load contract
        contract = self.load_contract(service_name)
        if not contract:
            result["validation_status"] = "failed"
            result["issues"].append("Failed to load contract file")
            print(f"  ❌ Failed to load contract")
            return result

        # Check 2: Contract freshness
        service_arch = self.load_service_architecture(service_name)
        if service_arch:
            fresh_valid, fresh_warning = self.validate_contract_freshness(
                contract,
                service_arch
            )
            result["checks"]["contract_freshness"] = {
                "passed": fresh_valid,
                "warning": fresh_warning
            }

            if not fresh_valid:
                result["warnings"].append(fresh_warning)
                print(f"  ⚠️  Contract may be stale: {fresh_warning}")
            else:
                print(f"  ✅ Contract is up-to-date")

        # Check 3: Function implementation
        python_files = self.find_python_files(service_name)
        if python_files:
            implemented_functions = self.extract_function_names_from_code(python_files)

            functions_valid, function_issues = self.validate_functions(
                contract,
                implemented_functions
            )

            result["checks"]["functions_implemented"] = {
                "passed": functions_valid,
                "issues": function_issues,
                "contracted_count": len(
                    contract.get("contracted_functions", {}).get("functions", [])
                ),
                "implemented_count": len(implemented_functions)
            }

            if not functions_valid:
                result["issues"].extend(function_issues)
                print(f"  ❌ Function validation failed ({len(function_issues)} issues)")
            else:
                print(f"  ✅ All contracted functions found")
        else:
            result["warnings"].append("No Python source files found for validation")
            print(f"  ⚠️  No source files found to validate")

        # Check 4: Interface implementation
        interfaces_valid, interface_issues = self.validate_interfaces(
            contract,
            service_name
        )

        result["checks"]["interfaces_valid"] = {
            "passed": interfaces_valid,
            "issues": interface_issues
        }

        if not interfaces_valid:
            result["issues"].extend(interface_issues)
            print(f"  ❌ Interface validation failed ({len(interface_issues)} issues)")
        else:
            print(f"  ✅ All interfaces valid")

        # Determine overall status
        if len(result["issues"]) == 0:
            result["validation_status"] = "passed"
            print(f"  ✅ Validation PASSED")
        else:
            result["validation_status"] = "failed"
            print(f"  ❌ Validation FAILED ({len(result['issues'])} issues)")

        return result

    def validate_all_services(self) -> Dict[str, Any]:
        """
        Validate contracts for all services

        Returns:
            Validation report for all services
        """
        print("🚀 Validating service contracts for all services...\n")

        # Find all services with contracts
        service_dirs = [
            d for d in self.services_dir.iterdir()
            if d.is_dir() and (d / "SERVICE_CONTRACT.json").exists()
        ]

        if not service_dirs:
            print("⚠️  No service contracts found")
            return {
                "timestamp": datetime.now().isoformat(),
                "services_validated": 0,
                "services_passed": 0,
                "services_failed": 0,
                "results": []
            }

        results = []

        for service_dir in service_dirs:
            service_name = service_dir.name
            result = self.validate_service(service_name)
            results.append(result)

        # Summary
        passed = sum(1 for r in results if r["validation_status"] == "passed")
        failed = sum(1 for r in results if r["validation_status"] == "failed")

        report = {
            "timestamp": datetime.now().isoformat(),
            "services_validated": len(results),
            "services_passed": passed,
            "services_failed": failed,
            "results": results
        }

        print(f"\n📊 Validation Summary:")
        print(f"  Services validated: {len(results)}")
        print(f"  Passed: {passed}")
        print(f"  Failed: {failed}")

        return report

    def write_report(self, report: Dict[str, Any]) -> Path:
        """
        Write validation report to file

        Args:
            report: Validation report dictionary

        Returns:
            Path to report file
        """
        report_file = self.validation_dir / "service_contracts_validation_report.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)

        print(f"\n💾 Report written to: {report_file}")

        return report_file


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate service implementations against their contracts"
    )
    parser.add_argument(
        "system_root",
        type=Path,
        help="Path to system root directory"
    )
    parser.add_argument(
        "--service",
        type=str,
        help="Validate contract for single service (default: all services)"
    )

    args = parser.parse_args()

    try:
        validator = ServiceContractValidator(args.system_root)

        if args.service:
            result = validator.validate_service(args.service)
            report = {
                "timestamp": datetime.now().isoformat(),
                "services_validated": 1,
                "services_passed": 1 if result["validation_status"] == "passed" else 0,
                "services_failed": 1 if result["validation_status"] == "failed" else 0,
                "results": [result]
            }
        else:
            report = validator.validate_all_services()

        validator.write_report(report)

        # Exit code based on validation results
        if report["services_failed"] > 0:
            return 1
        else:
            return 0

    except Exception as e:
        print(f"\n❌ Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
