#!/usr/bin/env python3
"""
Validate architecture file format IMMEDIATELY after creation.

This prevents the "create wrong → discover at tool step → go back to reformat → never return" loop.

Usage:
    # After creating service_architecture.json in SE-02
    python3 validate_architecture_format.py /path/to/service_architecture.json --mode service

    # After creating functional_architecture.json in FA-02
    python3 validate_architecture_format.py /path/to/functional_architecture.json --mode functional

Exit codes:
    0: Format is correct for graph tool
    1: Format has issues that will break graph tool

Version: 1.0.0 (Reflow v3.14.0)
"""

import sys
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

def validate_service_architecture_format(arch_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate service_architecture.json format for SE-06 graph tool.

    Returns:
        (success, errors, warnings)
    """

    try:
        with open(arch_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, [f"❌ CRITICAL: File not found: {arch_path}"], []
    except json.JSONDecodeError as e:
        return False, [f"❌ CRITICAL: Invalid JSON: {e}"], []

    errors = []
    warnings = []

    # Check 1: interfaces must be ARRAY (not object)
    # Tool code reference: system_of_systems_graph_v2.py line 572
    if 'interfaces' in data:
        if not isinstance(data['interfaces'], list):
            errors.append(f"❌ CRITICAL: 'interfaces' must be ARRAY, not {type(data['interfaces']).__name__}")
            errors.append(f"   Tool expects: data.get('interfaces', []) → expects array")

            # Check if it's the common mistake (object with 'provided'/'consumed' keys)
            if isinstance(data['interfaces'], dict):
                keys = list(data['interfaces'].keys())
                errors.append(f"   You have: object with keys {keys}")
                if 'provided' in keys or 'consumed' in keys:
                    errors.append(f"   Common mistake detected: interfaces as object with provided/consumed keys")
                    errors.append(f"")
                    errors.append(f"   FIX: Convert to flat array format:")
                    errors.append(f"   INCORRECT:")
                    errors.append(f'     "interfaces": {{"provided": [...], "consumed": [...]}}')
                    errors.append(f"   CORRECT:")
                    errors.append(f'     "interfaces": [')
                    errors.append(f'       {{"interface_id": "api", "type": "provided", ...}},')
                    errors.append(f'       {{"interface_id": "db", "type": "consumed", ...}}')
                    errors.append(f'     ]')
        else:
            # Validate interface array structure
            for i, iface in enumerate(data['interfaces']):
                if not isinstance(iface, dict):
                    errors.append(f"❌ CRITICAL: interfaces[{i}] must be object, not {type(iface).__name__}")
                    continue

                # Check required fields
                if 'interface_id' not in iface:
                    warnings.append(f"⚠️  WARNING: interfaces[{i}] missing 'interface_id' (recommended)")
                if 'type' not in iface:
                    warnings.append(f"⚠️  WARNING: interfaces[{i}] missing 'type' field (should be 'provided', 'consumed', or 'internal')")

    # Check 2: components must have required fields
    # Tool code reference: system_of_systems_graph_v2.py line 150-152
    if 'components' in data:
        if not isinstance(data['components'], list):
            errors.append(f"❌ CRITICAL: 'components' must be ARRAY, not {type(data['components']).__name__}")
        else:
            for i, comp in enumerate(data['components']):
                if not isinstance(comp, dict):
                    errors.append(f"❌ CRITICAL: components[{i}] must be object, not {type(comp).__name__}")
                    continue

                # component_id and component_name are REQUIRED for graph node creation
                if 'component_id' not in comp:
                    errors.append(f"❌ CRITICAL: components[{i}] missing 'component_id' (REQUIRED for graph nodes)")
                    errors.append(f"   Tool will crash: system_of_systems_graph_v2.py line 150-152 validates this exists")
                if 'component_name' not in comp:
                    errors.append(f"❌ CRITICAL: components[{i}] missing 'component_name' (REQUIRED for graph nodes)")

    # Check 3: dependencies should exist if service has consumed interfaces
    if 'interfaces' in data and isinstance(data['interfaces'], list):
        consumed_interfaces = [iface for iface in data['interfaces']
                             if isinstance(iface, dict) and iface.get('type') == 'consumed']
        if consumed_interfaces and 'dependencies' not in data:
            warnings.append(f"⚠️  WARNING: Service has {len(consumed_interfaces)} consumed interfaces but no 'dependencies' array")
            warnings.append(f"   This may cause orphaned service detection in SE-06 graph analysis")
            warnings.append(f"   Consider adding 'dependencies' array showing which services provide these interfaces")

    # Check 4: dependencies array format (if present)
    if 'dependencies' in data:
        if not isinstance(data['dependencies'], list):
            errors.append(f"❌ CRITICAL: 'dependencies' must be ARRAY, not {type(data['dependencies']).__name__}")
        else:
            for i, dep in enumerate(data['dependencies']):
                if not isinstance(dep, dict):
                    errors.append(f"❌ CRITICAL: dependencies[{i}] must be object, not {type(dep).__name__}")
                    continue

                if 'service_id' not in dep and 'target_service' not in dep:
                    warnings.append(f"⚠️  WARNING: dependencies[{i}] missing 'service_id' or 'target_service' field")

    # Check 5: Basic required sections
    required_sections = ['metadata']
    for section in required_sections:
        if section not in data:
            warnings.append(f"⚠️  WARNING: Missing recommended section '{section}'")

    # Print results
    if errors:
        print("\n" + "="*80)
        print("❌ SERVICE ARCHITECTURE FORMAT VALIDATION FAILED")
        print("="*80)
        print(f"\nFile: {arch_path}")
        print(f"\n{len(errors)} CRITICAL ERROR(S) - These will break SE-06 graph tool:")
        for error in errors:
            print(f"  {error}")

        if warnings:
            print(f"\n{len(warnings)} WARNING(S) - Non-blocking but recommended to fix:")
            for warning in warnings:
                print(f"  {warning}")

        print("\n" + "="*80)
        print("⚠️  DO NOT PROCEED TO SE-06 - FIX THESE ERRORS NOW")
        print("="*80)
        print("\nHow to fix:")
        print("  1. Edit the architecture file to fix the errors above")
        print("  2. Re-run this validation: python3 validate_architecture_format.py <file> --mode service")
        print("  3. Once validation passes, proceed to next step")
        print("="*80)
        return False, errors, warnings

    # Success
    print("\n" + "="*80)
    print(f"✓ SERVICE ARCHITECTURE FORMAT VALIDATION PASSED")
    print("="*80)
    print(f"\nFile: {arch_path}")
    print(f"Status: Format is CORRECT for SE-06 graph tool (system_of_systems_graph_v2.py)")

    if warnings:
        print(f"\n{len(warnings)} WARNING(S) - Non-blocking but recommended to address:")
        for warning in warnings:
            print(f"  {warning}")

    print("\n" + "="*80)
    print("✓ SAFE TO PROCEED to next step")
    print("="*80)

    return True, [], warnings


def validate_functional_architecture_format(arch_path: Path) -> Tuple[bool, List[str], List[str]]:
    """
    Validate functional_architecture.json format for FA-05 tool.

    Returns:
        (success, errors, warnings)
    """

    try:
        with open(arch_path) as f:
            data = json.load(f)
    except FileNotFoundError:
        return False, [f"❌ CRITICAL: File not found: {arch_path}"], []
    except json.JSONDecodeError as e:
        return False, [f"❌ CRITICAL: Invalid JSON: {e}"], []

    errors = []
    warnings = []

    # Check 1: functions array exists with required fields
    if 'functions' not in data:
        errors.append("❌ CRITICAL: Missing 'functions' array (REQUIRED for FA-05 graph tool)")
        errors.append("   Tool expects: data.get('functions', []) to create graph nodes")
    else:
        if not isinstance(data['functions'], list):
            errors.append(f"❌ CRITICAL: 'functions' must be ARRAY, not {type(data['functions']).__name__}")
        else:
            for i, func in enumerate(data['functions']):
                if not isinstance(func, dict):
                    errors.append(f"❌ CRITICAL: functions[{i}] must be object, not {type(func).__name__}")
                    continue

                # Required fields for graph nodes
                if 'function_id' not in func:
                    errors.append(f"❌ CRITICAL: functions[{i}] missing 'function_id' (REQUIRED for graph nodes)")
                if 'function_name' not in func:
                    errors.append(f"❌ CRITICAL: functions[{i}] missing 'function_name' (REQUIRED for graph nodes)")

                # Recommended fields
                if 'inputs' not in func:
                    warnings.append(f"⚠️  WARNING: functions[{i}] ({func.get('function_id', i)}) missing 'inputs' array")
                if 'outputs' not in func:
                    warnings.append(f"⚠️  WARNING: functions[{i}] ({func.get('function_id', i)}) missing 'outputs' array")

    # Check 2: dependencies array exists
    if 'dependencies' not in data and 'function_dependencies' not in data and 'edges' not in data:
        errors.append("❌ CRITICAL: Missing dependencies array (REQUIRED for FA-05 to create graph edges)")
        errors.append("   Expected one of: 'dependencies', 'function_dependencies', or 'edges'")
        errors.append("   Without this, tool cannot create connections between functions (unreachable functions)")
    else:
        # Check whichever dependency field exists
        dep_field = None
        if 'dependencies' in data:
            dep_field = 'dependencies'
        elif 'function_dependencies' in data:
            dep_field = 'function_dependencies'
        elif 'edges' in data:
            dep_field = 'edges'

        if dep_field:
            if not isinstance(data[dep_field], list):
                errors.append(f"❌ CRITICAL: '{dep_field}' must be ARRAY, not {type(data[dep_field]).__name__}")
            else:
                for i, dep in enumerate(data[dep_field]):
                    if not isinstance(dep, dict):
                        errors.append(f"❌ CRITICAL: {dep_field}[{i}] must be object, not {type(dep).__name__}")
                        continue

                    # Check for source/target fields (various naming conventions)
                    has_source = any(key in dep for key in ['source', 'source_function', 'from', 'caller'])
                    has_target = any(key in dep for key in ['target', 'target_function', 'to', 'callee'])

                    if not has_source:
                        warnings.append(f"⚠️  WARNING: {dep_field}[{i}] missing source field (expected: 'source', 'source_function', 'from', or 'caller')")
                    if not has_target:
                        warnings.append(f"⚠️  WARNING: {dep_field}[{i}] missing target field (expected: 'target', 'target_function', 'to', or 'callee')")

    # Print results
    if errors:
        print("\n" + "="*80)
        print("❌ FUNCTIONAL ARCHITECTURE FORMAT VALIDATION FAILED")
        print("="*80)
        print(f"\nFile: {arch_path}")
        print(f"\n{len(errors)} CRITICAL ERROR(S) - These will break FA-05 analysis tool:")
        for error in errors:
            print(f"  {error}")

        if warnings:
            print(f"\n{len(warnings)} WARNING(S) - Non-blocking but recommended to fix:")
            for warning in warnings:
                print(f"  {warning}")

        print("\n" + "="*80)
        print("⚠️  DO NOT PROCEED TO FA-05 - FIX THESE ERRORS NOW")
        print("="*80)
        print("\nHow to fix:")
        print("  1. Edit the functional architecture file to fix the errors above")
        print("  2. Re-run this validation: python3 validate_architecture_format.py <file> --mode functional")
        print("  3. Once validation passes, proceed to FA-03 (visualizations)")
        print("="*80)
        return False, errors, warnings

    # Success
    print("\n" + "="*80)
    print(f"✓ FUNCTIONAL ARCHITECTURE FORMAT VALIDATION PASSED")
    print("="*80)
    print(f"\nFile: {arch_path}")
    print(f"Status: Format is CORRECT for FA-05 analysis tool (system_of_systems_graph_v2.py --functional-mode)")

    if warnings:
        print(f"\n{len(warnings)} WARNING(S) - Non-blocking but recommended to address:")
        for warning in warnings:
            print(f"  {warning}")

    print("\n" + "="*80)
    print("✓ SAFE TO PROCEED to FA-03 (visualizations)")
    print("="*80)

    return True, [], warnings


def main():
    """Main entry point."""

    if len(sys.argv) < 2:
        print("Validate Architecture Format Tool v1.0.0")
        print("\nUsage:")
        print("  python3 validate_architecture_format.py <file_path> --mode <service|functional>")
        print("\nExamples:")
        print("  # Validate service architecture (for SE-06 tool)")
        print("  python3 validate_architecture_format.py specs/machine/service_arch/auth_service/service_architecture.json --mode service")
        print("\n  # Validate functional architecture (for FA-05 tool)")
        print("  python3 validate_architecture_format.py specs/functional/functional_architecture.json --mode functional")
        print("\nExit codes:")
        print("  0: Format is correct for graph tool")
        print("  1: Format has issues that will break graph tool")
        sys.exit(1)

    arch_path = Path(sys.argv[1])

    # Determine mode from arguments or file path
    mode = "service"  # default
    if "--mode" in sys.argv:
        mode_idx = sys.argv.index("--mode")
        if mode_idx + 1 < len(sys.argv):
            mode = sys.argv[mode_idx + 1]
    elif "functional_architecture" in arch_path.name:
        mode = "functional"

    # Validate
    if mode == "service":
        success, errors, warnings = validate_service_architecture_format(arch_path)
    elif mode == "functional":
        success, errors, warnings = validate_functional_architecture_format(arch_path)
    else:
        print(f"❌ Unknown mode: {mode} (expected 'service' or 'functional')")
        sys.exit(1)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
