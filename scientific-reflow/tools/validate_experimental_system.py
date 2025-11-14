#!/usr/bin/env python3
"""
Experimental System Validation Tool for Scientific Reflow

Analyzes experimental_system_architecture.json files to:
1. Verify Systems A-F are present
2. Check System F configuration (pass-through vs active)
3. Identify knowledge gaps (System D PARTIALLY_KNOWN properties)
4. Generate system-of-systems graph structure
5. Validate interaction chains (A→B→D→E→F→Observable)

This is a simplified tool for validation testing of the Systems A-F architecture.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any

def load_experimental_system(filepath: str) -> Dict[str, Any]:
    """Load experimental system architecture JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def identify_systems(data: Dict[str, Any]) -> Dict[str, List[Dict]]:
    """Identify and categorize components by system category (A-F)."""
    systems = {
        'A': [],  # Source
        'B': [],  # Manipulation
        'C': [],  # Environment
        'D': [],  # Sample
        'E': [],  # Detection
        'F': []   # Analysis
    }

    for component in data.get('experimental_components', []):
        category = component.get('system_category', '')
        if 'system_a' in category:
            systems['A'].append(component)
        elif 'system_b' in category:
            systems['B'].append(component)
        elif 'system_c' in category:
            systems['C'].append(component)
        elif 'system_d' in category:
            systems['D'].append(component)
        elif 'system_e' in category:
            systems['E'].append(component)
        elif 'system_f' in category:
            systems['F'].append(component)

    return systems

def analyze_system_f(systems: Dict[str, List[Dict]]) -> Dict[str, Any]:
    """Analyze System F configuration."""
    if not systems['F']:
        return {
            'present': False,
            'error': 'System F is missing! All beamlines should have System F (pass-through or active).'
        }

    system_f = systems['F'][0]  # Assuming single System F
    processing_config = system_f.get('processing_config', {})
    processing_type = processing_config.get('processing_type', 'unknown')

    return {
        'present': True,
        'component_id': system_f.get('component_id'),
        'component_name': system_f.get('component_name'),
        'processing_type': processing_type,
        'is_pass_through': processing_type == 'pass_through',
        'is_active': processing_type != 'pass_through',
        'configuration': processing_config
    }

def identify_knowledge_gaps(systems: Dict[str, List[Dict]]) -> List[Dict[str, Any]]:
    """Identify knowledge gaps in System D (sample)."""
    gaps = []

    for component in systems['D']:
        knowledge_state = component.get('knowledge_state', 'UNKNOWN')

        if knowledge_state == 'PARTIALLY_KNOWN':
            properties = component.get('physical_properties', {})
            unknown_props = []

            for key, value in properties.items():
                if isinstance(value, str) and ('UNKNOWN' in value or 'unknown' in value):
                    unknown_props.append(key)
                elif key.startswith('_comment_unknown'):
                    # Find the actual unknown properties mentioned in comment
                    continue

            gaps.append({
                'component_id': component.get('component_id'),
                'component_name': component.get('component_name'),
                'knowledge_state': knowledge_state,
                'unknown_properties': unknown_props,
                'gap_closure_goal': component.get('gap_closure_goal', 'Not specified')
            })

    return gaps

def analyze_interaction_chain(data: Dict[str, Any]) -> Dict[str, Any]:
    """Analyze the interaction chain from A through F."""
    interactions = data.get('physical_interactions', [])

    # Build interaction graph
    interaction_map = {}
    for interaction in interactions:
        from_comp = interaction.get('from_component')
        to_comp = interaction.get('to_component')
        if from_comp not in interaction_map:
            interaction_map[from_comp] = []
        interaction_map[from_comp].append(to_comp)

    # Expected chain: Source (A) → Manipulation (B) → Sample (D) ← Environment (C)
    # Sample (D) → Detection (E) → Analysis (F)

    return {
        'total_interactions': len(interactions),
        'interaction_map': interaction_map,
        'critical_d_to_e': any(
            i.get('from_component', '').endswith('sample') or 'sample' in i.get('from_component', '')
            for i in interactions if i.get('critical_for_gap_closure', False)
        ),
        'has_e_to_f': any(
            'detection' in i.get('interaction_type', '') and 'analysis' in i.get('interaction_type', '')
            for i in interactions
        )
    }

def generate_validation_report(filepath: str) -> Dict[str, Any]:
    """Generate comprehensive validation report."""
    data = load_experimental_system(filepath)
    systems = identify_systems(data)
    system_f_analysis = analyze_system_f(systems)
    gaps = identify_knowledge_gaps(systems)
    interaction_analysis = analyze_interaction_chain(data)

    # System counts
    system_counts = {letter: len(comps) for letter, comps in systems.items()}

    # Validation checks
    all_systems_present = all(count > 0 for count in system_counts.values())
    system_f_correct = system_f_analysis.get('present', False)

    validation_status = {
        'all_systems_present': all_systems_present,
        'system_f_present': system_f_correct,
        'knowledge_gaps_identified': len(gaps) > 0,
        'critical_interactions_present': interaction_analysis['critical_d_to_e']
    }

    overall_valid = all(validation_status.values())

    return {
        'metadata': data.get('metadata', {}),
        'system_counts': system_counts,
        'systems_present': list(systems.keys()),
        'system_f_analysis': system_f_analysis,
        'knowledge_gaps': gaps,
        'interaction_analysis': interaction_analysis,
        'validation_status': validation_status,
        'overall_valid': overall_valid,
        'validation_message': 'PASS - Systems A-F architecture valid' if overall_valid else 'FAIL - Architecture issues detected'
    }

def print_report(report: Dict[str, Any]):
    """Print validation report in human-readable format."""
    print("\n" + "="*70)
    print("EXPERIMENTAL SYSTEM VALIDATION REPORT")
    print("="*70)

    metadata = report['metadata']
    print(f"\nValidation Case: {metadata.get('validation_case_name', 'Unknown')}")
    print(f"Beamline: {metadata.get('beamline', 'Unknown')}")
    print(f"Technique: {metadata.get('technique', 'Unknown')}")

    print("\n" + "-"*70)
    print("SYSTEMS INVENTORY")
    print("-"*70)

    for system, count in report['system_counts'].items():
        status = "✓" if count > 0 else "✗"
        print(f"  System {system}: {count} component(s) {status}")

    print("\n" + "-"*70)
    print("SYSTEM F ANALYSIS")
    print("-"*70)

    sys_f = report['system_f_analysis']
    if sys_f.get('present'):
        print(f"  ✓ System F Present")
        print(f"  Component: {sys_f.get('component_name')}")
        print(f"  Processing Type: {sys_f.get('processing_type')}")
        if sys_f.get('is_pass_through'):
            print(f"  Mode: PASS-THROUGH (identity transformation)")
        else:
            print(f"  Mode: ACTIVE PROCESSING")
    else:
        print(f"  ✗ System F Missing")
        print(f"  Error: {sys_f.get('error')}")

    print("\n" + "-"*70)
    print("KNOWLEDGE GAPS (System D)")
    print("-"*70)

    gaps = report['knowledge_gaps']
    if gaps:
        for gap in gaps:
            print(f"\n  Component: {gap['component_name']}")
            print(f"  Knowledge State: {gap['knowledge_state']}")
            print(f"  Gap Closure Goal: {gap['gap_closure_goal']}")
            if gap['unknown_properties']:
                print(f"  Unknown Properties: {', '.join(gap['unknown_properties'][:3])}")
    else:
        print("  No gaps detected (unexpected - System D should have PARTIALLY_KNOWN properties)")

    print("\n" + "-"*70)
    print("INTERACTION ANALYSIS")
    print("-"*70)

    inter = report['interaction_analysis']
    print(f"  Total Interactions: {inter['total_interactions']}")
    print(f"  Critical D→E Interaction: {'✓' if inter['critical_d_to_e'] else '✗'}")
    print(f"  E→F Interaction: {'✓' if inter['has_e_to_f'] else '✗'}")

    print("\n" + "-"*70)
    print("VALIDATION STATUS")
    print("-"*70)

    status = report['validation_status']
    for check, passed in status.items():
        symbol = "✓" if passed else "✗"
        check_name = check.replace('_', ' ').title()
        print(f"  {symbol} {check_name}")

    print("\n" + "="*70)
    print(f"OVERALL: {report['validation_message']}")
    print("="*70 + "\n")

def main():
    if len(sys.argv) < 2:
        print("Usage: python validate_experimental_system.py <experimental_system_architecture.json>")
        print("\nExample:")
        print("  python validate_experimental_system.py specs/machine/experimental_systems/experimental_system_architecture.json")
        sys.exit(1)

    filepath = sys.argv[1]

    if not Path(filepath).exists():
        print(f"Error: File not found: {filepath}")
        sys.exit(1)

    # Generate and print report
    report = generate_validation_report(filepath)
    print_report(report)

    # Save report to JSON
    output_dir = Path(filepath).parent.parent / "validation_reports"
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / f"validation_report_{Path(filepath).stem}.json"
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"Detailed report saved to: {output_file}\n")

    # Exit code
    sys.exit(0 if report['overall_valid'] else 1)

if __name__ == "__main__":
    main()
