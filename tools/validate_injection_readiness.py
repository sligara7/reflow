#!/usr/bin/env python3
"""
Validate that a target system is ready for reflow injection.

This tool checks if a developed system has the proper structure and prerequisites
for embedding a complete reflow environment within its context/ folder.

Usage:
    python3 validate_injection_readiness.py <target_system_path>
    
Example:
    python3 validate_injection_readiness.py /home/user/my_developed_system
"""

import os
import sys
import json
from pathlib import Path
import argparse

def check_directory_structure(target_path):
    """Check if target has required reflow directory structure."""
    target = Path(target_path)
    
    print("🔍 Checking directory structure...")
    
    required_dirs = {
        'context': 'LLM agent tracking files',
        'specs': 'System specifications', 
        'services': 'Implementation code',
        'docs': 'System documentation'
    }
    
    issues = []
    for dir_name, description in required_dirs.items():
        dir_path = target / dir_name
        if dir_path.exists():
            print(f"  ✅ {dir_name}/ - {description}")
        else:
            print(f"  ❌ {dir_name}/ - {description} (MISSING)")
            issues.append(f"Missing {dir_name}/ directory")
    
    return len(issues) == 0, issues

def check_context_contents(target_path):
    """Check existing context directory contents."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    print("\n🔍 Checking context/ directory contents...")
    
    if not context_dir.exists():
        print("  ❌ No context/ directory found")
        return False, ["No context/ directory - system may not be reflow-developed"]
    
    # Look for typical reflow context files
    expected_files = [
        'working_memory.json',
        'current_focus.md', 
        'step_progress_tracker.json',
        'process_log.md'
    ]
    
    found_files = []
    for expected in expected_files:
        if (context_dir / expected).exists():
            found_files.append(expected)
            print(f"  ✅ {expected}")
        else:
            print(f"  ⚠️  {expected} (not found)")
    
    if len(found_files) >= 2:
        print(f"  ✅ Context appears to be from reflow workflow ({len(found_files)}/{len(expected_files)} expected files)")
        return True, []
    else:
        return True, [f"Context directory exists but may not be from reflow workflow (only {len(found_files)} expected files found)"]

def check_system_completeness(target_path):
    """Check if system appears to be reasonably developed."""
    target = Path(target_path)
    
    print("\n🔍 Checking system development completeness...")
    
    issues = []
    
    # Check specs directory
    specs_dir = target / 'specs'
    if specs_dir.exists():
        machine_dir = specs_dir / 'machine'
        if machine_dir.exists():
            index_file = machine_dir / 'index.json'
            if index_file.exists():
                print("  ✅ specs/machine/index.json found")
            else:
                print("  ⚠️  specs/machine/index.json not found")
                issues.append("Missing specs/machine/index.json - system may not be architecturally complete")
        else:
            print("  ⚠️  specs/machine/ directory not found")
            issues.append("Missing specs/machine/ directory")
    
    # Check services directory
    services_dir = target / 'services'
    if services_dir.exists():
        service_items = [item for item in services_dir.iterdir() if item.is_dir() or item.name.endswith('.json')]
        if service_items:
            print(f"  ✅ services/ contains {len(service_items)} items")
        else:
            print("  ⚠️  services/ directory is empty")
            issues.append("services/ directory is empty - system may not be developed yet")
    
    # Check docs directory
    docs_dir = target / 'docs'
    if docs_dir.exists():
        doc_files = [f for f in docs_dir.glob('*.md') if f.is_file()]
        if doc_files:
            print(f"  ✅ docs/ contains {len(doc_files)} markdown files")
        else:
            print("  ⚠️  docs/ directory has no markdown files")
            issues.append("docs/ directory has no markdown files")
    
    return len(issues) == 0, issues

def check_for_conflicts(target_path):
    """Check for potential conflicts with injection."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    print("\n🔍 Checking for potential injection conflicts...")
    
    issues = []
    
    if not context_dir.exists():
        return True, []
    
    # Check for existing embedded structure
    embedded_indicators = ['workflows', 'tools', 'templates', 'definitions', 'bin', 'config']
    found_embedded = []
    
    for indicator in embedded_indicators:
        if (context_dir / indicator).exists():
            found_embedded.append(indicator)
    
    if found_embedded:
        print(f"  ⚠️  Found existing embedded directories: {', '.join(found_embedded)}")
        issues.append(f"Context already contains embedded directories: {', '.join(found_embedded)}")
        print("     This suggests reflow may have already been injected")
    else:
        print("  ✅ No existing embedded reflow directories found")
    
    # Check for git repository
    if (target / '.git').exists():
        print("  ✅ Target is a git repository")
        
        # Check if there are uncommitted changes
        try:
            import subprocess
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                  cwd=target, capture_output=True, text=True)
            if result.returncode == 0:
                if result.stdout.strip():
                    print("  ⚠️  Git repository has uncommitted changes")
                    issues.append("Uncommitted changes in git repository - recommend committing before injection")
                else:
                    print("  ✅ Git repository is clean")
            else:
                print("  ⚠️  Could not check git status")
        except:
            print("  ⚠️  Could not check git status")
    else:
        print("  ⚠️  Target is not a git repository")
        issues.append("Target is not a git repository - recommend initializing git first")
    
    return len(issues) == 0, issues

def check_space_requirements(target_path):
    """Check if there's enough disk space for injection."""
    target = Path(target_path)
    
    print("\n🔍 Checking disk space requirements...")
    
    # Get reflow root to estimate size
    script_path = Path(__file__).resolve()
    reflow_root = script_path.parent.parent
    
    # Estimate size of reflow components to be injected
    total_size = 0
    for component in ['tools', 'templates', 'definitions', 'workflows']:
        component_path = reflow_root / component
        if component_path.exists():
            for file_path in component_path.rglob('*'):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
    
    # Add decision_flow.json
    decision_flow = reflow_root / 'decision_flow.json'
    if decision_flow.exists():
        total_size += decision_flow.stat().st_size
    
    # Get available disk space
    try:
        stat = os.statvfs(target)
        available_space = stat.f_bavail * stat.f_frsize
        
        size_mb = total_size / (1024 * 1024)
        available_mb = available_space / (1024 * 1024)
        
        print(f"  📦 Estimated injection size: {size_mb:.1f} MB")
        print(f"  💾 Available disk space: {available_mb:.1f} MB")
        
        if available_space > total_size * 10:  # 10x safety margin
            print("  ✅ Sufficient disk space available")
            return True, []
        else:
            return False, [f"May not have sufficient disk space (need ~{size_mb:.1f} MB)"]
            
    except Exception as e:
        print(f"  ⚠️  Could not check disk space: {e}")
        return True, ["Could not verify disk space"]

def generate_readiness_report(target_path, all_checks):
    """Generate a comprehensive readiness report."""
    target = Path(target_path)
    
    print(f"\n📋 INJECTION READINESS REPORT")
    print(f"🎯 Target System: {target_path}")
    print(f"📅 Check Date: {Path(__file__).stat().st_mtime}")
    
    passed_checks = sum(1 for passed, _ in all_checks if passed)
    total_checks = len(all_checks)
    
    print(f"✅ Passed: {passed_checks}/{total_checks} checks")
    
    # Collect all issues
    all_issues = []
    for passed, issues in all_checks:
        all_issues.extend(issues)
    
    if all_issues:
        print(f"\n⚠️  ISSUES FOUND ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    # Overall recommendation
    critical_failures = sum(1 for passed, _ in all_checks if not passed)
    
    if critical_failures == 0 and len(all_issues) <= 2:
        print(f"\n🎉 RECOMMENDATION: READY FOR INJECTION")
        print("   System appears suitable for reflow injection")
        return True
    elif critical_failures == 0:
        print(f"\n⚠️  RECOMMENDATION: READY WITH CAUTION")
        print("   System can be injected but address warnings if possible")
        return True
    else:
        print(f"\n❌ RECOMMENDATION: NOT READY")
        print("   Please address critical issues before attempting injection")
        return False

def main():
    parser = argparse.ArgumentParser(description='Validate system readiness for reflow injection')
    parser.add_argument('target_system', help='Path to target system for injection')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    parser.add_argument('--json', action='store_true', help='Output results as JSON')
    
    args = parser.parse_args()
    target_path = Path(args.target_system).resolve()
    
    if not target_path.exists():
        print(f"❌ Target system does not exist: {target_path}")
        sys.exit(1)
    
    if not target_path.is_dir():
        print(f"❌ Target system is not a directory: {target_path}")
        sys.exit(1)
    
    print(f"🚀 Reflow Injection Readiness Check")
    print(f"🎯 Target: {target_path}")
    
    # Run all checks
    checks = [
        ("Directory Structure", check_directory_structure(target_path)),
        ("Context Contents", check_context_contents(target_path)),
        ("System Completeness", check_system_completeness(target_path)),
        ("Conflict Detection", check_for_conflicts(target_path)),
        ("Disk Space", check_space_requirements(target_path))
    ]
    
    if args.json:
        # Output JSON format
        results = {
            "target_system": str(target_path),
            "timestamp": Path(__file__).stat().st_mtime,
            "checks": {}
        }
        
        for check_name, (passed, issues) in checks:
            results["checks"][check_name.lower().replace(" ", "_")] = {
                "passed": passed,
                "issues": issues
            }
        
        # Overall result
        critical_failures = sum(1 for _, (passed, _) in checks if not passed)
        all_issues = []
        for _, (_, issues) in checks:
            all_issues.extend(issues)
        
        if critical_failures == 0 and len(all_issues) <= 2:
            results["recommendation"] = "READY"
        elif critical_failures == 0:
            results["recommendation"] = "READY_WITH_CAUTION"
        else:
            results["recommendation"] = "NOT_READY"
        
        print(json.dumps(results, indent=2))
    else:
        # Generate human-readable report
        ready = generate_readiness_report(target_path, [result for _, result in checks])
        
        if ready:
            sys.exit(0)
        else:
            sys.exit(1)

if __name__ == "__main__":
    main()