#!/usr/bin/env python3
"""
Generate human-readable documentation from functional architecture.

Converts functional_architecture.json to stakeholder-friendly markdown documentation
organized by functional flows, functions, and cross-references.

Usage:
    python3 generate_functional_documentation.py --system-root /path/to/system
    python3 generate_functional_documentation.py --system-root /path/to/system --output-file /custom/path.md
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
import sys


def load_functional_architecture(arch_path: Path) -> dict:
    """Load functional architecture JSON."""
    with open(arch_path, 'r') as f:
        return json.load(f)


def generate_overview_section(metadata: dict) -> str:
    """Generate overview section from document metadata."""
    system_name = metadata.get('system_name', 'Unknown System')
    version = metadata.get('version', '1.0.0')
    purpose = metadata.get('purpose', 'No purpose defined')
    framework = metadata.get('framework', 'Unknown')
    created = metadata.get('created', 'Unknown')
    last_updated = metadata.get('last_updated', 'Unknown')

    doc = f"""---
document_type: functional_architecture
system_name: {system_name}
version: {version}
framework: {framework}
last_updated: {last_updated}
---

# Functional Architecture: {system_name}

**Version**: {version}
**Framework**: {framework}
**Created**: {created}
**Last Updated**: {last_updated}

## Purpose

{purpose}

"""

    # Add source documents if available
    source_docs = metadata.get('source_documents', [])
    if source_docs:
        doc += "## Source Documents\n\n"
        for src in source_docs:
            doc += f"- `{src}`\n"
        doc += "\n"

    return doc


def generate_flows_section(flows: list) -> str:
    """Generate functional flows section."""
    if not flows:
        return "## Functional Flows\n\n*No functional flows defined.*\n\n"

    doc = "## Functional Flows\n\n"
    doc += f"This system implements {len(flows)} primary functional flows:\n\n"

    for flow in flows:
        flow_id = flow.get('flow_id', 'UNKNOWN')
        flow_name = flow.get('flow_name', 'Unnamed Flow')
        description = flow.get('description', 'No description')
        entry_point = flow.get('entry_point', 'N/A')
        exit_points = flow.get('exit_points', [])
        typical_path = flow.get('typical_path', [])
        requirements = flow.get('implements_requirements', [])
        context_consumption = flow.get('estimated_context_consumption', 'Unknown')

        doc += f"### {flow_name} (`{flow_id}`)\n\n"
        doc += f"{description}\n\n"
        doc += f"- **Entry Point**: `{entry_point}`\n"
        doc += f"- **Exit Points**: {', '.join(f'`{ep}`' for ep in exit_points) if exit_points else 'N/A'}\n"
        doc += f"- **Implements Requirements**: {', '.join(requirements) if requirements else 'None specified'}\n"
        doc += f"- **Estimated Context Consumption**: {context_consumption}\n"

        if typical_path:
            doc += f"- **Typical Path**: {' → '.join(f'`{step}`' for step in typical_path)}\n"

        # Add note if exists
        note = flow.get('note')
        if note:
            doc += f"\n*Note: {note}*\n"

        doc += "\n"

    return doc


def generate_functions_section(functions: list, flows: list) -> str:
    """Generate functions section organized by flow."""
    if not functions:
        return "## Functions\n\n*No functions defined.*\n\n"

    doc = "## Functions\n\n"
    doc += f"This system implements {len(functions)} functions:\n\n"

    # Create flow-to-functions mapping
    flow_functions = {}
    for flow in flows:
        flow_id = flow.get('flow_id')
        flow_name = flow.get('flow_name', flow_id)
        typical_path = flow.get('typical_path', [])
        if typical_path:
            flow_functions[flow_id] = {
                'name': flow_name,
                'functions': [f for f in functions if f.get('function_id') in typical_path]
            }

    # Add functions not in any flow
    all_flow_function_ids = set()
    for flow_data in flow_functions.values():
        all_flow_function_ids.update(f.get('function_id') for f in flow_data['functions'])

    orphan_functions = [f for f in functions if f.get('function_id') not in all_flow_function_ids]

    # Document functions by flow
    for flow_id, flow_data in flow_functions.items():
        doc += f"### Functions in {flow_data['name']}\n\n"

        for func in flow_data['functions']:
            doc += generate_function_detail(func)

    # Document orphan functions if any
    if orphan_functions:
        doc += "### Other Functions\n\n"
        for func in orphan_functions:
            doc += generate_function_detail(func)

    return doc


def generate_function_detail(func: dict) -> str:
    """Generate detailed documentation for a single function."""
    func_id = func.get('function_id', 'UNKNOWN')
    func_name = func.get('function_name', 'Unnamed Function')
    func_type = func.get('function_type', 'unknown')
    description = func.get('description', 'No description')
    inputs = func.get('inputs', [])
    outputs = func.get('outputs', [])
    context_consumption = func.get('context_consumption', 'Unknown')
    exec_time = func.get('execution_time_seconds', 'Unknown')
    requirements = func.get('implements_requirements', [])
    error_handling = func.get('error_handling', 'Not specified')

    doc = f"#### {func_name} (`{func_id}`)\n\n"
    doc += f"**Type**: {func_type}  \n"
    doc += f"**Description**: {description}\n\n"

    # Inputs
    doc += "**Inputs**:\n"
    if inputs:
        for inp in inputs:
            doc += f"- `{inp}`\n"
    else:
        doc += "- *None*\n"
    doc += "\n"

    # Outputs
    doc += "**Outputs**:\n"
    if outputs:
        for out in outputs:
            doc += f"- `{out}`\n"
    else:
        doc += "- *None*\n"
    doc += "\n"

    # Performance metrics
    doc += f"**Performance**:\n"
    doc += f"- Context Consumption: {context_consumption} tokens\n"
    doc += f"- Execution Time: {exec_time}s\n\n"

    # Requirements
    if requirements:
        doc += f"**Implements Requirements**: {', '.join(requirements)}\n\n"

    # Error handling
    doc += f"**Error Handling**: {error_handling}\n\n"

    # Note if exists
    note = func.get('note')
    if note:
        doc += f"*Note: {note}*\n\n"

    return doc


def generate_summary_section(arch: dict) -> str:
    """Generate summary statistics section."""
    flows = arch.get('functional_flows', [])
    functions = arch.get('functions', [])

    # Calculate total context consumption
    total_context = sum(f.get('context_consumption', 0) for f in functions)

    # Count function types
    function_types = {}
    for func in functions:
        func_type = func.get('function_type', 'unknown')
        function_types[func_type] = function_types.get(func_type, 0) + 1

    doc = "## Summary\n\n"
    doc += f"- **Total Flows**: {len(flows)}\n"
    doc += f"- **Total Functions**: {len(functions)}\n"
    doc += f"- **Total Context Consumption**: {total_context:,} tokens\n\n"

    if function_types:
        doc += "**Functions by Type**:\n"
        for func_type, count in sorted(function_types.items()):
            doc += f"- {func_type}: {count}\n"
        doc += "\n"

    return doc


def generate_functional_doc(arch: dict) -> str:
    """Generate complete human-readable functional architecture documentation."""
    metadata = arch.get('document_metadata', {})
    flows = arch.get('functional_flows', [])
    functions = arch.get('functions', [])

    # Build complete document
    doc = generate_overview_section(metadata)
    doc += generate_summary_section(arch)
    doc += generate_flows_section(flows)
    doc += generate_functions_section(functions, flows)

    # Footer
    doc += "---\n\n"
    doc += f"**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  \n"
    doc += f"**Source**: `specs/functional/functional_architecture.json`  \n"
    doc += f"**Tool**: `generate_functional_documentation.py` (v3.14.6)\n"

    return doc


def main():
    parser = argparse.ArgumentParser(
        description='Generate human-readable documentation from functional architecture',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate functional architecture documentation
  python3 generate_functional_documentation.py --system-root /path/to/system

  # Custom output file
  python3 generate_functional_documentation.py --system-root /path/to/system --output-file /custom/path.md
        """
    )
    parser.add_argument('--system-root', required=True, help='System root directory')
    parser.add_argument('--output-file', help='Output markdown file (default: specs/human/FUNCTIONAL_ARCHITECTURE.md)')
    parser.add_argument('--verbose', action='store_true', help='Verbose output')
    args = parser.parse_args()

    system_root = Path(args.system_root)
    if not system_root.exists():
        print(f"❌ System root does not exist: {system_root}")
        return 1

    # Find functional architecture
    functional_arch_path = system_root / 'specs/functional/functional_architecture.json'
    if not functional_arch_path.exists():
        print(f"❌ Functional architecture not found at {functional_arch_path}")
        return 1

    # Determine output file
    if args.output_file:
        output_file = Path(args.output_file)
    else:
        output_file = system_root / 'specs/human/FUNCTIONAL_ARCHITECTURE.md'

    output_file.parent.mkdir(parents=True, exist_ok=True)

    if args.verbose:
        print(f"System Root: {system_root}")
        print(f"Input: {functional_arch_path}")
        print(f"Output: {output_file}")

    try:
        # Load and generate
        arch = load_functional_architecture(functional_arch_path)
        doc = generate_functional_doc(arch)

        # Write output
        with open(output_file, 'w') as f:
            f.write(doc)

        print(f"✅ Generated: {output_file.relative_to(system_root)}")

        # Show statistics
        flows = arch.get('functional_flows', [])
        functions = arch.get('functions', [])
        print(f"📊 {len(flows)} flows, {len(functions)} functions")

        return 0

    except Exception as e:
        print(f"❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
