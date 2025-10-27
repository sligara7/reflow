#!/usr/bin/env python3
"""
Dependency Validation Tool

Validates that all code imports exist in requirements.txt/pyproject.toml.
Prevents "missing dependency" issues during Docker builds and runtime.

Usage:
    python3 validate_dependencies.py --system-root /path/to/system --service service_name
    python3 validate_dependencies.py --system-root /path/to/system --all-services

Part of Reflow v3.6.0 - Early Testing Integration feature (D-06.5-A01)
Prevents Category 1 issues: Dependencies not matching code (5 issues from operational testing)
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
import re


class DependencyValidator:
    """Validates that code imports match declared dependencies."""

    # Standard library modules (don't need to be in requirements.txt)
    STDLIB_MODULES = {
        'abc', 'argparse', 'ast', 'asyncio', 'base64', 'collections', 'copy',
        'csv', 'datetime', 'decimal', 'email', 'enum', 'functools', 'hashlib',
        'http', 'io', 'itertools', 'json', 'logging', 'math', 'os', 'pathlib',
        're', 'secrets', 'shutil', 'signal', 'socket', 'ssl', 'string', 'subprocess',
        'sys', 'tempfile', 'threading', 'time', 'traceback', 'typing', 'unittest',
        'urllib', 'uuid', 'warnings', 'weakref', 'xml'
    }

    # Import name to package name mappings (when they differ)
    IMPORT_TO_PACKAGE = {
        'PIL': 'Pillow',
        'cv2': 'opencv-python',
        'yaml': 'PyYAML',
        'dotenv': 'python-dotenv',
        'jwt': 'PyJWT',
        'dateutil': 'python-dateutil',
        'psycopg2': 'psycopg2-binary',
        'sklearn': 'scikit-learn',
        'bs4': 'beautifulsoup4'
    }

    def __init__(self, system_root: Path):
        self.system_root = Path(system_root)
        self.services_dir = self.system_root / "services"
        self.issues = []

    def validate_service(self, service_name: str) -> Dict:
        """Validate dependencies for a single service."""
        service_dir = self.services_dir / service_name

        if not service_dir.exists():
            return {
                "service": service_name,
                "status": "error",
                "error": f"Service directory not found: {service_dir}"
            }

        print(f"\nValidating dependencies for service: {service_name}")

        # Step 1: Extract imports from code
        src_dir = service_dir / "src"
        if not src_dir.exists():
            return {
                "service": service_name,
                "status": "error",
                "error": f"Source directory not found: {src_dir}"
            }

        imported_modules = self._extract_imports_from_code(src_dir)
        print(f"  Found {len(imported_modules)} imported modules in code")

        # Step 2: Read declared dependencies
        declared_packages = self._read_declared_dependencies(service_dir)
        if declared_packages is None:
            return {
                "service": service_name,
                "status": "error",
                "error": "No requirements.txt or pyproject.toml found"
            }

        print(f"  Found {len(declared_packages)} declared packages")

        # Step 3: Compare and find missing dependencies
        missing_deps = self._find_missing_dependencies(
            imported_modules, declared_packages
        )

        # Step 4: Check for common issues
        version_warnings = self._check_version_patterns(service_dir)

        # Build result
        result = {
            "service": service_name,
            "status": "pass" if not missing_deps else "fail",
            "imported_modules_count": len(imported_modules),
            "declared_packages_count": len(declared_packages),
            "missing_dependencies": missing_deps,
            "version_warnings": version_warnings
        }

        if missing_deps:
            print(f"  ❌ FAIL: {len(missing_deps)} missing dependencies")
            for dep in missing_deps:
                print(f"    - {dep['package']} (imported in {dep['example_file']})")
        else:
            print(f"  ✅ PASS: All imports found in dependencies")

        return result

    def _extract_imports_from_code(self, src_dir: Path) -> Set[str]:
        """Extract all import statements from Python files using AST."""
        imported_modules = set()

        # Find all Python files
        python_files = list(src_dir.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                for node in ast.walk(tree):
                    # Handle: import X
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            module_name = alias.name.split('.')[0]
                            imported_modules.add(module_name)

                    # Handle: from X import Y
                    elif isinstance(node, ast.ImportFrom):
                        if node.module:
                            module_name = node.module.split('.')[0]
                            imported_modules.add(module_name)

            except SyntaxError as e:
                print(f"  Warning: Syntax error in {py_file}: {e}")
            except Exception as e:
                print(f"  Warning: Could not parse {py_file}: {e}")

        # Filter out standard library modules
        external_modules = {
            mod for mod in imported_modules
            if mod not in self.STDLIB_MODULES
        }

        return external_modules

    def _read_declared_dependencies(self, service_dir: Path) -> Set[str]:
        """Read dependencies from requirements.txt or pyproject.toml."""
        # Try requirements.txt first
        req_file = service_dir / "requirements.txt"
        if req_file.exists():
            return self._parse_requirements_txt(req_file)

        # Try pyproject.toml
        pyproject_file = service_dir / "pyproject.toml"
        if pyproject_file.exists():
            return self._parse_pyproject_toml(pyproject_file)

        return None

    def _parse_requirements_txt(self, req_file: Path) -> Set[str]:
        """Parse requirements.txt and extract package names."""
        packages = set()

        with open(req_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Extract package name (before ==, >=, <=, etc.)
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)', line)
                if match:
                    package_name = match.group(1).lower()
                    packages.add(package_name)

        return packages

    def _parse_pyproject_toml(self, pyproject_file: Path) -> Set[str]:
        """Parse pyproject.toml and extract package names."""
        packages = set()

        try:
            import tomli
        except ImportError:
            # Fallback: simple regex parsing (not perfect but works for basic cases)
            with open(pyproject_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Find dependencies section
                in_deps = False
                for line in content.split('\n'):
                    if 'dependencies' in line and '=' in line:
                        in_deps = True
                        continue

                    if in_deps:
                        if line.strip().startswith(']'):
                            break

                        # Extract package name from "package>=version" format
                        match = re.search(r'"([a-zA-Z0-9_\-\.]+)', line)
                        if match:
                            package_name = match.group(1).lower()
                            packages.add(package_name)

            return packages

        # Use tomli if available
        with open(pyproject_file, 'rb') as f:
            data = tomli.load(f)

        # Try different locations in pyproject.toml
        if 'project' in data and 'dependencies' in data['project']:
            for dep in data['project']['dependencies']:
                match = re.match(r'^([a-zA-Z0-9_\-\.]+)', dep)
                if match:
                    package_name = match.group(1).lower()
                    packages.add(package_name)

        return packages

    def _find_missing_dependencies(
        self,
        imported_modules: Set[str],
        declared_packages: Set[str]
    ) -> List[Dict]:
        """Find imported modules not in declared packages."""
        missing = []

        for module in sorted(imported_modules):
            # Convert import name to package name if needed
            package_name = self.IMPORT_TO_PACKAGE.get(module, module).lower()

            # Check if package is declared
            if package_name not in declared_packages:
                # Try with hyphens/underscores variations
                package_hyphen = package_name.replace('_', '-')
                package_underscore = package_name.replace('-', '_')

                if (package_hyphen not in declared_packages and
                    package_underscore not in declared_packages):

                    # Find example file where this module is imported
                    example_file = self._find_import_location(module)

                    missing.append({
                        "module": module,
                        "package": package_name,
                        "example_file": example_file,
                        "suggestion": f"Add '{package_name}' to requirements.txt"
                    })

        return missing

    def _find_import_location(self, module: str) -> str:
        """Find a file where this module is imported (for error reporting)."""
        # This is a simplified version - we could cache this during extraction
        return f"(search codebase for 'import {module}')"

    def _check_version_patterns(self, service_dir: Path) -> List[str]:
        """Check for common version-related issues."""
        warnings = []

        req_file = service_dir / "requirements.txt"
        if not req_file.exists():
            return warnings

        with open(req_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Check for unpinned versions (no version specified)
        unpinned = re.findall(r'^([a-zA-Z0-9_\-\.]+)\s*$', content, re.MULTILINE)
        if unpinned:
            warnings.append(
                f"Unpinned versions found: {', '.join(unpinned[:3])}... "
                f"(consider pinning versions for reproducible builds)"
            )

        # Check for very loose constraints (>=)
        loose = re.findall(r'([a-zA-Z0-9_\-\.]+)>=', content)
        if len(loose) > 5:
            warnings.append(
                f"{len(loose)} packages with >= constraints "
                f"(consider using == for deterministic builds)"
            )

        return warnings

    def validate_all_services(self) -> Dict:
        """Validate dependencies for all services."""
        if not self.services_dir.exists():
            return {
                "status": "error",
                "error": f"Services directory not found: {self.services_dir}"
            }

        # Find all service directories
        services = [
            d.name for d in self.services_dir.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        ]

        if not services:
            return {
                "status": "error",
                "error": "No services found"
            }

        print(f"Found {len(services)} services: {', '.join(services)}")

        results = []
        for service in services:
            result = self.validate_service(service)
            results.append(result)

        # Overall status
        failed_services = [r for r in results if r.get('status') == 'fail']
        overall_status = 'fail' if failed_services else 'pass'

        return {
            "status": overall_status,
            "services_validated": len(services),
            "services_passed": len(services) - len(failed_services),
            "services_failed": len(failed_services),
            "results": results
        }


def main():
    parser = argparse.ArgumentParser(
        description="Validate that code imports match declared dependencies"
    )
    parser.add_argument(
        '--system-root',
        required=True,
        help='Path to system root directory'
    )
    parser.add_argument(
        '--service',
        help='Validate specific service'
    )
    parser.add_argument(
        '--all-services',
        action='store_true',
        help='Validate all services'
    )
    parser.add_argument(
        '--output',
        help='Output JSON report to file'
    )

    args = parser.parse_args()

    validator = DependencyValidator(args.system_root)

    # Validate
    if args.service:
        result = validator.validate_service(args.service)
    elif args.all_services:
        result = validator.validate_all_services()
    else:
        print("Error: Must specify --service or --all-services")
        sys.exit(1)

    # Output result
    if args.output:
        output_file = Path(args.output)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nValidation report written to: {output_file}")

    # Print summary
    print("\n" + "="*60)
    print("DEPENDENCY VALIDATION SUMMARY")
    print("="*60)

    if result['status'] == 'pass':
        print("✅ PASS: All dependencies validated successfully")
        sys.exit(0)
    elif result['status'] == 'fail':
        print("❌ FAIL: Missing dependencies found")
        print("\nAction required:")
        print("  1. Add missing packages to requirements.txt or pyproject.toml")
        print("  2. Re-run validation to confirm fixes")
        sys.exit(1)
    else:
        print(f"⚠️  ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
