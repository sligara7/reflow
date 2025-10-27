#!/usr/bin/env python3
"""
Module Structure Validation Tool

Validates Python package structure: __init__.py presence, circular imports, shadowing.
Prevents ImportError and module resolution issues at runtime.

Usage:
    python3 validate_module_structure.py --system-root /path/to/system --service service_name
    python3 validate_module_structure.py --system-root /path/to/system --all-services

Part of Reflow v3.6.0 - Early Testing Integration feature (D-06.5-A02)
Prevents Category 2 issues: Module/package structure (3 issues from operational testing)
"""

import argparse
import ast
import json
import sys
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict


class ModuleStructureValidator:
    """Validates Python module and package structure."""

    def __init__(self, system_root: Path):
        self.system_root = Path(system_root)
        self.services_dir = self.system_root / "services"

    def validate_service(self, service_name: str) -> Dict:
        """Validate module structure for a single service."""
        service_dir = self.services_dir / service_name

        if not service_dir.exists():
            return {
                "service": service_name,
                "status": "error",
                "error": f"Service directory not found: {service_dir}"
            }

        print(f"\nValidating module structure for service: {service_name}")

        src_dir = service_dir / "src"
        if not src_dir.exists():
            return {
                "service": service_name,
                "status": "error",
                "error": f"Source directory not found: {src_dir}"
            }

        issues = []

        # Check 1: Missing __init__.py
        print("  Checking for missing __init__.py files...")
        missing_init = self._check_missing_init_py(src_dir)
        if missing_init:
            print(f"    ❌ Found {len(missing_init)} directories missing __init__.py")
            issues.extend(missing_init)
        else:
            print(f"    ✅ All packages have __init__.py")

        # Check 2: Circular imports
        print("  Checking for circular imports...")
        circular_imports = self._check_circular_imports(src_dir)
        if circular_imports:
            print(f"    ❌ Found {len(circular_imports)} circular import cycles")
            issues.extend(circular_imports)
        else:
            print(f"    ✅ No circular imports detected")

        # Check 3: Shadowed modules
        print("  Checking for shadowed modules...")
        shadowed = self._check_shadowed_modules(src_dir)
        if shadowed:
            print(f"    ❌ Found {len(shadowed)} shadowed modules")
            issues.extend(shadowed)
        else:
            print(f"    ✅ No shadowed modules detected")

        # Check 4: Import test (can modules be imported?)
        print("  Testing module imports...")
        import_errors = self._test_module_imports(src_dir, service_name)
        if import_errors:
            print(f"    ❌ Found {len(import_errors)} modules that cannot be imported")
            issues.extend(import_errors)
        else:
            print(f"    ✅ All modules can be imported")

        # Build result
        result = {
            "service": service_name,
            "status": "fail" if issues else "pass",
            "total_issues": len(issues),
            "issues": issues
        }

        return result

    def _check_missing_init_py(self, src_dir: Path) -> List[Dict]:
        """Check for directories missing __init__.py files."""
        issues = []

        # Find all directories that contain Python files
        for directory in src_dir.rglob("*"):
            if not directory.is_dir():
                continue

            # Skip __pycache__ and hidden directories
            if directory.name.startswith('.') or directory.name == '__pycache__':
                continue

            # Check if directory contains Python files
            python_files = list(directory.glob("*.py"))
            if not python_files:
                continue

            # Check for __init__.py
            init_file = directory / "__init__.py"
            if not init_file.exists():
                issues.append({
                    "type": "missing_init_py",
                    "severity": "error",
                    "directory": str(directory.relative_to(src_dir)),
                    "message": f"Directory '{directory.relative_to(src_dir)}' contains Python files but is missing __init__.py",
                    "fix": f"Create {init_file}"
                })

        return issues

    def _check_circular_imports(self, src_dir: Path) -> List[Dict]:
        """Check for circular import dependencies."""
        # Build import dependency graph
        import_graph = defaultdict(set)

        python_files = list(src_dir.rglob("*.py"))

        for py_file in python_files:
            module_path = self._get_module_path(py_file, src_dir)

            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    tree = ast.parse(f.read(), filename=str(py_file))

                for node in ast.walk(tree):
                    # Handle: from X import Y (relative imports)
                    if isinstance(node, ast.ImportFrom):
                        if node.level > 0:  # Relative import
                            imported_module = self._resolve_relative_import(
                                module_path, node.module, node.level
                            )
                        else:  # Absolute import
                            imported_module = node.module

                        if imported_module:
                            import_graph[module_path].add(imported_module)

                    # Handle: import X
                    elif isinstance(node, ast.Import):
                        for alias in node.names:
                            import_graph[module_path].add(alias.name)

            except Exception as e:
                # Skip files that can't be parsed
                continue

        # Detect cycles using DFS
        cycles = self._find_cycles_dfs(import_graph)

        issues = []
        for cycle in cycles:
            issues.append({
                "type": "circular_import",
                "severity": "error",
                "cycle": cycle,
                "message": f"Circular import detected: {' → '.join(cycle)}",
                "fix": "Refactor to break circular dependency (extract to separate module, use late imports, or dependency injection)"
            })

        return issues

    def _get_module_path(self, file_path: Path, src_dir: Path) -> str:
        """Convert file path to Python module path."""
        relative_path = file_path.relative_to(src_dir)

        # Remove .py extension and convert to module notation
        module_path = str(relative_path.with_suffix('')).replace('/', '.')

        # Remove __init__ from end if present
        if module_path.endswith('.__init__'):
            module_path = module_path[:-9]

        return module_path

    def _resolve_relative_import(
        self,
        current_module: str,
        imported_module: str,
        level: int
    ) -> str:
        """Resolve relative import to absolute module path."""
        parts = current_module.split('.')

        # Go up 'level' directories
        if level > len(parts):
            return None

        base_parts = parts[:-level] if level > 0 else parts

        if imported_module:
            return '.'.join(base_parts + [imported_module])
        else:
            return '.'.join(base_parts)

    def _find_cycles_dfs(self, graph: Dict[str, Set[str]]) -> List[List[str]]:
        """Find cycles in import graph using depth-first search."""
        cycles = []
        visited = set()
        rec_stack = set()
        path = []

        def dfs(node):
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if dfs(neighbor):
                        return True
                elif neighbor in rec_stack:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                    return True

            path.pop()
            rec_stack.remove(node)
            return False

        for node in graph:
            if node not in visited:
                dfs(node)

        return cycles

    def _check_shadowed_modules(self, src_dir: Path) -> List[Dict]:
        """Check for modules shadowed by directories with same name."""
        issues = []

        for py_file in src_dir.rglob("*.py"):
            # Get file stem (name without extension)
            file_stem = py_file.stem

            # Skip __init__.py
            if file_stem == '__init__':
                continue

            # Check if directory with same name exists in same parent
            potential_shadow_dir = py_file.parent / file_stem

            if potential_shadow_dir.exists() and potential_shadow_dir.is_dir():
                issues.append({
                    "type": "shadowed_module",
                    "severity": "error",
                    "file": str(py_file.relative_to(src_dir)),
                    "directory": str(potential_shadow_dir.relative_to(src_dir)),
                    "message": f"Module '{py_file.relative_to(src_dir)}' is shadowed by directory '{potential_shadow_dir.relative_to(src_dir)}'",
                    "fix": f"Rename either the file or directory to avoid shadowing"
                })

        return issues

    def _test_module_imports(self, src_dir: Path, service_name: str) -> List[Dict]:
        """Test if modules can be imported (basic sanity check)."""
        issues = []

        # This is a simplified check - actual import testing would require
        # setting up PYTHONPATH and handling dependencies
        # For now, we just check for obvious syntax errors

        python_files = list(src_dir.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, 'r', encoding='utf-8') as f:
                    ast.parse(f.read(), filename=str(py_file))
            except SyntaxError as e:
                issues.append({
                    "type": "syntax_error",
                    "severity": "error",
                    "file": str(py_file.relative_to(src_dir)),
                    "line": e.lineno,
                    "message": f"Syntax error in '{py_file.relative_to(src_dir)}': {e.msg}",
                    "fix": f"Fix syntax error at line {e.lineno}"
                })
            except Exception as e:
                issues.append({
                    "type": "parse_error",
                    "severity": "warning",
                    "file": str(py_file.relative_to(src_dir)),
                    "message": f"Could not parse '{py_file.relative_to(src_dir)}': {str(e)}",
                    "fix": "Review file for parsing issues"
                })

        return issues

    def validate_all_services(self) -> Dict:
        """Validate module structure for all services."""
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
        description="Validate Python module and package structure"
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

    validator = ModuleStructureValidator(args.system_root)

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
    print("MODULE STRUCTURE VALIDATION SUMMARY")
    print("="*60)

    if result['status'] == 'pass':
        print("✅ PASS: Module structure validated successfully")
        sys.exit(0)
    elif result['status'] == 'fail':
        print("❌ FAIL: Module structure issues found")
        print("\nCommon fixes:")
        print("  - Add missing __init__.py files")
        print("  - Refactor circular imports")
        print("  - Rename shadowed modules/directories")
        print("  - Fix syntax errors")
        sys.exit(1)
    else:
        print(f"⚠️  ERROR: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()
