#!/usr/bin/env python3
"""
Inject workflow files into target system with path adjustments for embedded operation.

This tool copies all workflow JSON files from reflow source to target system's 
context/workflows/ directory, updating internal paths to use embedded locations.

Usage:
    python3 inject_workflows.py <reflow_root> <target_workflows_dir>
    
Example:
    python3 inject_workflows.py /home/user/reflow /home/user/my_system/context/workflows
"""

import os
import sys
import json
import re
import shutil
from pathlib import Path
import argparse

def update_workflow_paths(content, path_mappings):
    """Update paths in workflow content using provided mappings."""
    updated_content = content
    
    for old_path, new_path in path_mappings.items():
        # Update JSON string values that contain paths
        pattern = r'"([^"]*?)' + re.escape(old_path) + r'([^"]*?)"'
        replacement = r'"\1' + new_path + r'\2"'
        updated_content = re.sub(pattern, replacement, updated_content)
        
        # Update standalone path references
        updated_content = updated_content.replace(old_path, new_path)
    
    return updated_content

def validate_json_syntax(content, filename):
    """Validate that modified content is still valid JSON."""
    try:
        json.loads(content)
        return True, None
    except json.JSONDecodeError as e:
        return False, f"JSON syntax error in {filename}: {e}"

def inject_decision_flow(reflow_root, target_workflows_dir):
    """Inject decision_flow.json with path adjustments."""
    reflow_path = Path(reflow_root)
    target_path = Path(target_workflows_dir)
    
    decision_flow_source = reflow_path / 'decision_flow.json'
    decision_flow_target = target_path / 'decision_flow.json'
    
    if not decision_flow_source.exists():
        print(f"⚠️  decision_flow.json not found in {reflow_root}")
        return True, ["decision_flow.json not found in source"]
    
    print("🔄 Injecting decision_flow.json...")
    
    # Read source content
    with open(decision_flow_source, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Define path mappings for embedded operation
    path_mappings = {
        './tools/': './context/tools/',
        './templates/': './context/templates/',
        './definitions/': './context/definitions/',
        './workflows/': './context/workflows/',
        # Handle relative imports in tools
        '../tools/': './context/tools/',
        '../templates/': './context/templates/',
        '../definitions/': './context/definitions/'
    }
    
    # Update paths
    updated_content = update_workflow_paths(content, path_mappings)
    
    # Validate JSON syntax
    is_valid, error = validate_json_syntax(updated_content, 'decision_flow.json')
    if not is_valid:
        print(f"❌ {error}")
        return False, [error]
    
    # Write to target
    with open(decision_flow_target, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print("  ✅ decision_flow.json injected with path updates")
    return True, []

def inject_workflow_directory(reflow_root, target_workflows_dir, workflow_subdir):
    """Inject a specific workflow subdirectory (e.g., architecture/, development/)."""
    reflow_path = Path(reflow_root)
    target_path = Path(target_workflows_dir)
    
    source_dir = reflow_path / 'workflows' / workflow_subdir
    target_dir = target_path / workflow_subdir
    
    if not source_dir.exists():
        print(f"  ℹ️  {workflow_subdir}/ not found, skipping")
        return True, [f"{workflow_subdir}/ not found in source workflows"]
    
    print(f"🔄 Injecting {workflow_subdir}/ workflows...")
    
    # Create target directory
    target_dir.mkdir(parents=True, exist_ok=True)
    
    # Process each JSON file
    issues = []
    processed_count = 0
    
    for json_file in source_dir.glob('*.json'):
        print(f"  📄 Processing {json_file.name}...")
        
        # Read source content
        with open(json_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Define path mappings
        path_mappings = {
            './tools/': './context/tools/',
            './templates/': './context/templates/',
            './definitions/': './context/definitions/',
            './workflows/': './context/workflows/',
            '../tools/': './context/tools/',
            '../templates/': './context/templates/',
            '../definitions/': './context/definitions/',
            '../../tools/': './context/tools/',
            '../../templates/': './context/templates/',
            '../../definitions/': './context/definitions/'
        }
        
        # Update paths
        updated_content = update_workflow_paths(content, path_mappings)
        
        # Validate JSON syntax
        is_valid, error = validate_json_syntax(updated_content, json_file.name)
        if not is_valid:
            print(f"    ❌ {error}")
            issues.append(error)
            continue
        
        # Write to target
        target_file = target_dir / json_file.name
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        
        processed_count += 1
        print(f"    ✅ {json_file.name}")
    
    print(f"  ✅ {workflow_subdir}/: {processed_count} files processed")
    return len(issues) == 0, issues

def inject_inject_flow(reflow_root, target_workflows_dir):
    """Inject inject_flow.json for reference."""
    reflow_path = Path(reflow_root)
    target_path = Path(target_workflows_dir)
    
    inject_flow_source = reflow_path / 'inject_flow.json'
    inject_flow_target = target_path / 'inject_flow.json'
    
    if not inject_flow_source.exists():
        print("  ℹ️  inject_flow.json not found, skipping")
        return True, ["inject_flow.json not found in source"]
    
    print("🔄 Injecting inject_flow.json...")
    
    # Simple copy - inject_flow.json doesn't need path adjustments
    # since it's a reference document
    shutil.copy2(inject_flow_source, inject_flow_target)
    
    print("  ✅ inject_flow.json copied")
    return True, []

def create_embedded_workflow_index(target_workflows_dir):
    """Create an index of available workflows in the embedded environment."""
    target_path = Path(target_workflows_dir)
    
    print("🔄 Creating workflow index...")
    
    # Scan for all workflow files
    workflows = {
        "main_workflows": [],
        "architecture_workflows": [],
        "development_workflows": [],
        "feature_update_workflows": [],
        "other_workflows": []
    }
    
    # Main workflow files (in root)
    for json_file in target_path.glob('*.json'):
        workflows["main_workflows"].append({
            "name": json_file.name,
            "path": f"./{json_file.name}",
            "description": f"Main workflow: {json_file.stem}"
        })
    
    # Subdirectory workflows
    subdirs = {
        "architecture": "architecture_workflows",
        "development": "development_workflows", 
        "feature_update": "feature_update_workflows"
    }
    
    for subdir, key in subdirs.items():
        subdir_path = target_path / subdir
        if subdir_path.exists():
            for json_file in subdir_path.glob('*.json'):
                workflows[key].append({
                    "name": json_file.name,
                    "path": f"./{subdir}/{json_file.name}",
                    "description": f"{subdir.title()} workflow: {json_file.stem}"
                })
    
    # Other subdirectories
    for item in target_path.iterdir():
        if item.is_dir() and item.name not in subdirs:
            for json_file in item.glob('*.json'):
                workflows["other_workflows"].append({
                    "name": json_file.name,
                    "path": f"./{item.name}/{json_file.name}",
                    "description": f"{item.name.title()} workflow: {json_file.stem}"
                })
    
    # Create index file
    index_data = {
        "embedded_workflows_index": {
            "description": "Index of all available workflows in embedded reflow environment",
            "created": "auto-generated during injection",
            "usage": "Use paths relative to context/workflows/ directory",
            "total_workflows": sum(len(workflows[key]) for key in workflows)
        },
        "workflows": workflows
    }
    
    index_file = target_path / 'workflows_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2)
    
    total_count = index_data["embedded_workflows_index"]["total_workflows"]
    print(f"  ✅ Workflow index created ({total_count} workflows)")
    
    return True, []

def generate_injection_report(target_workflows_dir, results):
    """Generate a report of the injection process."""
    target_path = Path(target_workflows_dir)
    
    print(f"\n📋 WORKFLOW INJECTION REPORT")
    print(f"🎯 Target Directory: {target_workflows_dir}")
    
    success_count = sum(1 for success, _ in results if success)
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count} operations")
    
    # Collect all issues
    all_issues = []
    for success, issues in results:
        all_issues.extend(issues)
    
    if all_issues:
        print(f"\n⚠️  ISSUES ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    # List injected files
    injected_files = []
    for item in target_path.rglob('*.json'):
        rel_path = item.relative_to(target_path)
        injected_files.append(str(rel_path))
    
    if injected_files:
        print(f"\n📁 INJECTED FILES ({len(injected_files)}):")
        for file_path in sorted(injected_files):
            print(f"   📄 {file_path}")
    
    return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description='Inject workflow files with embedded path adjustments')
    parser.add_argument('reflow_root', help='Path to reflow source directory')
    parser.add_argument('target_workflows_dir', help='Path to target workflows directory (context/workflows)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    reflow_root = Path(args.reflow_root).resolve()
    target_workflows_dir = Path(args.target_workflows_dir).resolve()
    
    # Validate inputs
    if not reflow_root.exists():
        print(f"❌ Reflow root does not exist: {reflow_root}")
        sys.exit(1)
    
    if not (reflow_root / 'decision_flow.json').exists():
        print(f"❌ Not a valid reflow directory (missing decision_flow.json): {reflow_root}")
        sys.exit(1)
    
    print(f"🚀 Reflow Workflow Injection")
    print(f"📂 Source: {reflow_root}")
    print(f"🎯 Target: {target_workflows_dir}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        return
    
    # Create target directory
    target_workflows_dir.mkdir(parents=True, exist_ok=True)
    
    # Execute injection operations
    operations = [
        ("decision_flow.json", lambda: inject_decision_flow(reflow_root, target_workflows_dir)),
        ("architecture workflows", lambda: inject_workflow_directory(reflow_root, target_workflows_dir, 'architecture')),
        ("development workflows", lambda: inject_workflow_directory(reflow_root, target_workflows_dir, 'development')),
        ("feature_update workflows", lambda: inject_workflow_directory(reflow_root, target_workflows_dir, 'feature_update')),
        ("inject_flow.json", lambda: inject_inject_flow(reflow_root, target_workflows_dir)),
        ("workflow index", lambda: create_embedded_workflow_index(target_workflows_dir))
    ]
    
    results = []
    for operation_name, operation_func in operations:
        print(f"\n🔄 {operation_name}...")
        success, issues = operation_func()
        results.append((success, issues))
        
        if not success:
            print(f"❌ Failed: {operation_name}")
            for issue in issues:
                print(f"   • {issue}")
    
    # Generate final report
    overall_success = generate_injection_report(target_workflows_dir, results)
    
    if overall_success:
        print(f"\n🎉 Workflow injection completed successfully!")
        print(f"📖 Check: {target_workflows_dir}/workflows_index.json")
    else:
        print(f"\n⚠️  Workflow injection completed with issues")
        sys.exit(1)

if __name__ == "__main__":
    main()