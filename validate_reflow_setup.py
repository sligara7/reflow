#!/usr/bin/env python3
"""
Reflow Setup Validation Script
Validates that all required components are present for the stand-alone reflow system.
"""

import json
import sys
from pathlib import Path

def validate_reflow_setup():
    """Validate that reflow directory has all required components."""
    reflow_root = Path(__file__).parent
    issues = []
    
    # Check required directories
    required_dirs = ['tools', 'templates', 'definitions', 'architecture', 'development', 'feature_update']
    for dir_name in required_dirs:
        dir_path = reflow_root / dir_name
        if not dir_path.exists():
            issues.append(f"Missing required directory: {dir_name}")
        elif not dir_path.is_dir():
            issues.append(f"Path exists but is not a directory: {dir_name}")
    
    # Check required tools
    required_tools = [
        'validate_architecture.py',
        'system_of_systems_graph.py', 
        'generate_interface_contracts.py',
        'analyze_features.py',
        'bootstrap_development_context.py',
        'verify_component_contract.py'
    ]
    tools_dir = reflow_root / 'tools'
    for tool in required_tools:
        tool_path = tools_dir / tool
        if not tool_path.exists():
            issues.append(f"Missing required tool: tools/{tool}")
        elif not tool_path.is_file():
            issues.append(f"Tool path exists but is not a file: tools/{tool}")
    
    # Check required templates
    required_templates = [
        'service_architecture_template.json',
        'index_template.json',
        'interface_registry_template.json',
        'interface_registry_enhanced_template.json',
        'working_memory_template.json',
        'current_focus_template.md',
        'step_progress_tracker_template.json',
        'dev_progress_tracker_template.json',
        'dev_current_focus_template.md',
        'dev_working_memory_template.json',
        'interface_contract_complete_template.json',
        'component_specification_complete_template.json'
    ]
    templates_dir = reflow_root / 'templates'
    for template in required_templates:
        template_path = templates_dir / template
        if not template_path.exists():
            issues.append(f"Missing required template: templates/{template}")
        elif not template_path.is_file():
            issues.append(f"Template path exists but is not a file: templates/{template}")
    
    # Check required definitions
    definitions_file = reflow_root / 'definitions' / 'architectural_definitions.json'
    if not definitions_file.exists():
        issues.append("Missing required definitions: definitions/architectural_definitions.json")
    elif not definitions_file.is_file():
        issues.append("Definitions path exists but is not a file: definitions/architectural_definitions.json")
    
    # Check main decision flow
    decision_flow = reflow_root / 'decision_flow.json'
    if not decision_flow.exists():
        issues.append("Missing main decision flow: decision_flow.json")
    elif not decision_flow.is_file():
        issues.append("Decision flow path exists but is not a file: decision_flow.json")
    else:
        # Validate decision flow JSON
        try:
            with open(decision_flow) as f:
                flow_data = json.load(f)
            
            # Check for required sections
            required_sections = ['workflow_metadata', 'prerequisites', 'context_management', 'entry_points', 'quality_gates']
            for section in required_sections:
                if section not in flow_data:
                    issues.append(f"Missing required section in decision_flow.json: {section}")
        except json.JSONDecodeError as e:
            issues.append(f"Invalid JSON in decision_flow.json: {e}")
    
    # Check Python dependencies (optional warnings)
    warnings = []
    try:
        import networkx
    except ImportError:
        warnings.append("Python dependency missing: networkx (required for graph analysis)")
    
    try:
        import matplotlib
    except ImportError:
        warnings.append("Python dependency missing: matplotlib (required for visualizations)")
    
    # Report results
    if issues:
        print("❌ Reflow setup validation FAILED")
        print(f"Found {len(issues)} issues:")
        for issue in issues:
            print(f"  - {issue}")
        return False
    else:
        print("✅ Reflow setup validation PASSED")
        print("All required components are present.")
        
        if warnings:
            print(f"\n⚠️  {len(warnings)} warnings:")
            for warning in warnings:
                print(f"  - {warning}")
        
        return True

if __name__ == "__main__":
    success = validate_reflow_setup()
    sys.exit(0 if success else 1)