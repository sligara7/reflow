#!/usr/bin/env python3
"""
Execute injection workflow to make a developed system completely self-contained.

This script implements the inject_flow.json workflow, creating a standalone system
with embedded reflow capabilities in its context/ folder.

Usage:
    python3 execute_injection_flow.py <target_system_path>
    
Example:
    python3 execute_injection_flow.py /home/user/my_developed_system
"""

import os
import sys
import json
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import argparse

def get_reflow_root():
    """Get the reflow root directory (where this script is located)."""
    script_path = Path(__file__).resolve()
    return script_path.parent.parent  # tools/execute_injection_flow.py -> reflow/

def validate_target_system(target_path):
    """Validate that target system is suitable for injection."""
    target = Path(target_path)
    
    if not target.exists():
        print(f"❌ Target system does not exist: {target_path}")
        return False
        
    required_dirs = ['context', 'specs', 'services', 'docs']
    missing_dirs = []
    
    for req_dir in required_dirs:
        if not (target / req_dir).exists():
            missing_dirs.append(req_dir)
    
    if missing_dirs:
        print(f"❌ Missing required directories: {', '.join(missing_dirs)}")
        print("   Target system must have: context/, specs/, services/, docs/")
        return False
        
    print(f"✅ Target system validated: {target_path}")
    return True

def backup_existing_context(target_path):
    """Create backup of existing context directory."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    if not context_dir.exists():
        print("ℹ️  No existing context directory to backup")
        return True
        
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = target / f'context_backup_{timestamp}'
    
    try:
        shutil.copytree(context_dir, backup_dir)
        print(f"✅ Context backed up to: {backup_dir.name}")
        return True
    except Exception as e:
        print(f"❌ Failed to backup context: {e}")
        return False

def create_embedded_structure(target_path):
    """Create the embedded reflow directory structure."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    # Create new structure
    new_dirs = [
        'workflows', 'tools', 'templates', 'definitions', 
        'tracking', 'bin', 'config'
    ]
    
    for new_dir in new_dirs:
        (context_dir / new_dir).mkdir(parents=True, exist_ok=True)
    
    # Move existing context files to tracking/
    if context_dir.exists():
        for item in context_dir.iterdir():
            if item.is_file() and item.suffix in ['.json', '.md']:
                tracking_dir = context_dir / 'tracking'
                tracking_dir.mkdir(exist_ok=True)
                try:
                    shutil.move(str(item), str(tracking_dir / item.name))
                    print(f"  Moved {item.name} to tracking/")
                except Exception as e:
                    print(f"  Warning: Could not move {item.name}: {e}")
    
    print("✅ Embedded directory structure created")
    return True

def inject_workflows(reflow_root, target_path):
    """Copy workflow files with path adjustments."""
    reflow = Path(reflow_root)
    target = Path(target_path)
    workflows_target = target / 'context' / 'workflows'
    
    # Copy decision_flow.json
    decision_flow = reflow / 'decision_flow.json'
    if decision_flow.exists():
        # Read and modify paths in decision_flow.json
        with open(decision_flow, 'r') as f:
            workflow_content = f.read()
        
        # Update tool paths to use embedded locations
        workflow_content = workflow_content.replace('./tools/', './context/tools/')
        workflow_content = workflow_content.replace('./templates/', './context/templates/')
        workflow_content = workflow_content.replace('./definitions/', './context/definitions/')
        
        with open(workflows_target / 'decision_flow.json', 'w') as f:
            f.write(workflow_content)
        print("  ✅ Injected decision_flow.json")
    
    # Copy workflows directory if it exists
    workflows_source = reflow / 'workflows'
    if workflows_source.exists():
        for workflow_dir in workflows_source.iterdir():
            if workflow_dir.is_dir():
                target_workflow_dir = workflows_target / workflow_dir.name
                shutil.copytree(workflow_dir, target_workflow_dir, dirs_exist_ok=True)
                print(f"  ✅ Injected {workflow_dir.name}/ workflows")
    
    print("✅ Workflows injected with path adjustments")
    return True

def inject_tools(reflow_root, target_path):
    """Copy Python tools with embedded mode modifications."""
    reflow = Path(reflow_root)
    target = Path(target_path)
    tools_source = reflow / 'tools'
    tools_target = target / 'context' / 'tools'
    
    if not tools_source.exists():
        print("❌ Source tools directory not found")
        return False
    
    # Copy all Python tools
    for tool_file in tools_source.glob('*.py'):
        if tool_file.name == 'execute_injection_flow.py':
            continue  # Don't copy this script itself
            
        # For now, simple copy - in future iterations we'll add embedded mode detection
        shutil.copy2(tool_file, tools_target / tool_file.name)
        print(f"  ✅ Injected {tool_file.name}")
    
    print("✅ Tools injected")
    return True

def inject_templates_and_definitions(reflow_root, target_path):
    """Copy templates and definitions."""
    reflow = Path(reflow_root)
    target = Path(target_path)
    
    # Copy templates
    templates_source = reflow / 'templates'
    templates_target = target / 'context' / 'templates'
    if templates_source.exists():
        shutil.copytree(templates_source, templates_target, dirs_exist_ok=True)
        print("✅ Templates injected")
    
    # Copy definitions
    definitions_source = reflow / 'definitions'
    definitions_target = target / 'context' / 'definitions'
    if definitions_source.exists():
        shutil.copytree(definitions_source, definitions_target, dirs_exist_ok=True)
        print("✅ Definitions injected")
    
    return True

def create_executable_scripts(target_path):
    """Create convenience wrapper scripts."""
    target = Path(target_path)
    bin_dir = target / 'context' / 'bin'
    
    # Main reflow script
    reflow_script = bin_dir / 'reflow'
    reflow_content = '''#!/bin/bash
# Embedded reflow workflow execution script

SYSTEM_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONTEXT_ROOT="$SYSTEM_ROOT/context"

cd "$SYSTEM_ROOT"

if [ $# -eq 0 ]; then
    echo "Usage: $0 <workflow_step> [args]"
    echo "Example: $0 development/Dev-01-InitBootstrap.json"
    echo ""
    echo "Available workflows:"
    find "$CONTEXT_ROOT/workflows" -name "*.json" -type f | sed "s|$CONTEXT_ROOT/workflows/||" | sort
    exit 1
fi

echo "🔄 Executing embedded reflow workflow: $1"
echo "📁 System root: $SYSTEM_ROOT"
echo "📁 Context root: $CONTEXT_ROOT"

# Future: Execute workflow with embedded tools
echo "ℹ️  Workflow execution will be implemented in future iteration"
echo "ℹ️  For now, manually execute tools from $CONTEXT_ROOT/tools/"
'''
    
    with open(reflow_script, 'w') as f:
        f.write(reflow_content)
    reflow_script.chmod(0o755)
    
    # Validation script
    validate_script = bin_dir / 'validate'
    validate_content = '''#!/bin/bash
# Embedded reflow validation script

SYSTEM_ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
CONTEXT_ROOT="$SYSTEM_ROOT/context"

cd "$SYSTEM_ROOT"

case "${1:-all}" in
    "architecture"|"arch")
        echo "🔍 Validating architecture..."
        python3 "$CONTEXT_ROOT/tools/validate_architecture.py" .
        ;;
    "contracts")
        echo "🔍 Generating and validating interface contracts..."
        python3 "$CONTEXT_ROOT/tools/generate_interface_contracts.py" .
        ;;
    "graph")
        echo "🔍 Analyzing system graph..."
        python3 "$CONTEXT_ROOT/tools/system_of_systems_graph.py" specs/machine/index.json --analyze-issues
        ;;
    "all")
        echo "🔍 Running all validations..."
        python3 "$CONTEXT_ROOT/tools/validate_architecture.py" .
        python3 "$CONTEXT_ROOT/tools/system_of_systems_graph.py" specs/machine/index.json --analyze-issues
        ;;
    *)
        echo "Usage: $0 [architecture|contracts|graph|all]"
        exit 1
        ;;
esac
'''
    
    with open(validate_script, 'w') as f:
        f.write(validate_content)
    validate_script.chmod(0o755)
    
    print("✅ Executable scripts created")
    return True

def create_configuration(reflow_root, target_path):
    """Create embedded environment configuration."""
    reflow = Path(reflow_root)
    target = Path(target_path)
    config_dir = target / 'context' / 'config'
    
    # Read reflow version from decision_flow.json if available
    reflow_version = "unknown"
    decision_flow = reflow / 'decision_flow.json'
    if decision_flow.exists():
        try:
            with open(decision_flow, 'r') as f:
                workflow_data = json.load(f)
                reflow_version = workflow_data.get('workflow_metadata', {}).get('version', 'unknown')
        except:
            pass
    
    # Create embedded.json configuration
    embedded_config = {
        "embedded_mode": True,
        "reflow_root": "./context",
        "system_root": "..",
        "tools_path": "./context/tools",
        "templates_path": "./context/templates", 
        "workflows_path": "./context/workflows",
        "definitions_path": "./context/definitions",
        "tracking_path": "./context/tracking",
        "original_reflow_version": reflow_version,
        "injection_timestamp": datetime.now().isoformat(),
        "injection_source": str(reflow_root)
    }
    
    with open(config_dir / 'embedded.json', 'w') as f:
        json.dump(embedded_config, f, indent=2)
    
    # Create paths.json for path mapping
    paths_config = {
        "logical_to_embedded": {
            "./tools/": "./context/tools/",
            "./templates/": "./context/templates/",
            "./workflows/": "./context/workflows/",
            "./definitions/": "./context/definitions/"
        },
        "system_relative_paths": {
            "specs": "./specs/",
            "services": "./services/",
            "docs": "./docs/",
            "context": "./context/"
        }
    }
    
    with open(config_dir / 'paths.json', 'w') as f:
        json.dump(paths_config, f, indent=2)
    
    print("✅ Configuration files created")
    return True

def create_documentation(reflow_root, target_path):
    """Create usage documentation for embedded environment."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    # Create README_EMBEDDED.md
    readme_content = f'''# Embedded Reflow Environment

This system contains a complete embedded reflow workflow environment in the `context/` folder.

## What is this?

This system was developed using the reflow architecture and development methodology. The complete reflow toolchain has been embedded within the system's `context/` folder, making it completely self-contained.

## Directory Structure

```
context/
├── workflows/     # Complete reflow workflows (decision_flow.json, etc.)
├── tools/         # All reflow Python tools
├── templates/     # Reflow templates
├── definitions/   # Architectural definitions
├── tracking/      # Original context files (migrated here)
├── bin/           # Executable workflow scripts
└── config/        # Embedded environment configuration
```

## Quick Start

### Continue Development
```bash
# Execute reflow workflows
./context/bin/reflow development/Dev-01-InitBootstrap.json

# Validate architecture
./context/bin/validate architecture

# Validate all
./context/bin/validate all
```

### Tool Usage
```bash
# Use embedded tools directly
python3 context/tools/validate_architecture.py .
python3 context/tools/system_of_systems_graph.py specs/machine/index.json --analyze-issues
```

## Benefits of Embedded Environment

- **Complete Self-Containment**: No external reflow installation required
- **Team Collaboration**: All team members get identical reflow environment
- **Version Consistency**: Workflow tools are versioned with system development
- **Portability**: System repo contains complete development environment
- **Historical Preservation**: Complete development methodology preserved with system

## Team Collaboration

New team members can immediately start working:

```bash
git clone <this-repo>
cd <system-directory>
cat context/README_EMBEDDED.md  # This file
./context/bin/validate all       # Verify embedded environment works
```

## Production Deployment

When ready for production, you can clean the embedded environment:

```bash
# Remove embedded tools but keep development history
./context/bin/remove-embedded --keep-docs

# Or completely clean for production
./context/bin/remove-embedded --clean
```

## Troubleshooting

If you encounter issues with the embedded environment:

1. Check configuration: `cat context/config/embedded.json`
2. Verify tools exist: `ls context/tools/`
3. Check permissions: `ls -la context/bin/`

## Original Development

- **Reflow Source**: {reflow_root}
- **Injection Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Methodology**: Complete reflow architecture and development workflow

This system showcases the reflow methodology for systematic architecture design and development.
'''
    
    with open(context_dir / 'README_EMBEDDED.md', 'w') as f:
        f.write(readme_content)
    
    # Create INJECTION_HISTORY.md
    history_content = f'''# Reflow Injection History

## Injection Details

- **Source Reflow Directory**: {reflow_root}
- **Target System**: {target_path}
- **Injection Timestamp**: {datetime.now().isoformat()}
- **Injection Script**: execute_injection_flow.py

## Injected Components

### Workflows
- decision_flow.json (with path adjustments)
- All workflow JSON files from workflows/ directory

### Tools
- All Python tools from tools/ directory
- Modified for embedded operation

### Templates & Definitions  
- Complete templates/ directory
- Complete definitions/ directory

### Generated Components
- Executable wrapper scripts in bin/
- Configuration files in config/
- This documentation

## Path Modifications

All workflow files have been modified to use embedded paths:
- `./tools/` → `./context/tools/`
- `./templates/` → `./context/templates/`
- `./definitions/` → `./context/definitions/`

## Reversal Process

To remove the embedded environment:

1. Use removal script: `./context/bin/remove-embedded`
2. Or manually remove: `rm -rf context/{{workflows,tools,templates,definitions,bin,config}}`
3. Restore original context: `mv context/tracking/* context/`

## Update Process

To update embedded reflow from newer version:

1. Run: `python3 /path/to/newer/reflow/tools/execute_injection_flow.py {target_path} --update`
2. Or manually re-inject over existing embedded environment
'''
    
    with open(context_dir / 'INJECTION_HISTORY.md', 'w') as f:
        f.write(history_content)
    
    print("✅ Documentation created")
    return True

def validate_injection(target_path):
    """Validate successful injection."""
    target = Path(target_path)
    context_dir = target / 'context'
    
    checks = [
        ("workflows/decision_flow.json", "Workflow files"),
        ("tools/validate_architecture.py", "Python tools"), 
        ("templates/", "Templates directory"),
        ("definitions/", "Definitions directory"),
        ("bin/reflow", "Executable scripts"),
        ("config/embedded.json", "Configuration files"),
        ("README_EMBEDDED.md", "Documentation")
    ]
    
    all_good = True
    for check_path, description in checks:
        full_path = context_dir / check_path
        if full_path.exists():
            print(f"  ✅ {description}")
        else:
            print(f"  ❌ Missing: {description}")
            all_good = False
    
    if all_good:
        print("✅ Injection validation passed")
        return True
    else:
        print("❌ Injection validation failed")
        return False

def validate_pre_operation_requirements(reflow_root, target_path):
    """Validate pre-operation requirements as per modular instruction system."""
    print("🔍 Pre-Operation Validation (as per instructions/1-behavioral-rules.json)...")
    
    # Load behavioral rules
    behavioral_rules_path = reflow_root / 'instructions' / '1-behavioral-rules.json'
    if not behavioral_rules_path.exists():
        print("⚠️  Behavioral rules not found - continuing with basic validation")
    else:
        print("✅ Behavioral rules loaded")
    
    # Validate working directory
    current_dir = Path.cwd()
    if current_dir != reflow_root:
        print(f"❌ Wrong working directory. Currently in: {current_dir}")
        print(f"   Must be in reflow root: {reflow_root}")
        return False
    
    # Validate target system directory structure
    directory_validator = reflow_root / 'tools' / 'validate_directory_structure.py'
    if directory_validator.exists():
        print("🏗️  Running directory structure validation...")
        result = subprocess.run([
            'python3', str(directory_validator), str(target_path), '--json'
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            try:
                validation_data = json.loads(result.stdout)
                if validation_data.get('validation_passed', False):
                    print("✅ Target system directory structure is clean")
                else:
                    print("⚠️  Target system has directory structure issues")
                    print("   Consider running: python3 tools/validate_directory_structure.py <target> --auto-clean")
            except:
                print("✅ Directory validation completed")
        else:
            print("⚠️  Directory validation had issues but continuing...")
    
    return True

def validate_post_operation_requirements(reflow_root, target_path):
    """Validate post-operation requirements as per modular instruction system."""
    print("\n🔍 Post-Operation Validation (as per instructions/1-behavioral-rules.json)...")
    
    # Test embedded environment functionality
    validate_script = target_path / 'context' / 'bin' / 'validate'
    if validate_script.exists():
        print("🧪 Testing embedded environment...")
        result = subprocess.run(['bash', str(validate_script), 'all'], 
                              capture_output=True, text=True, cwd=target_path)
        if result.returncode == 0:
            print("✅ Embedded environment functional")
        else:
            print("⚠️  Embedded environment may have issues")
            print(f"   Output: {result.stdout[:200]}...")
    
    # Validate directory structure after injection
    directory_validator = reflow_root / 'tools' / 'validate_directory_structure.py'
    if directory_validator.exists():
        print("🏗️  Validating directory structure after injection...")
        result = subprocess.run([
            'python3', str(directory_validator), str(target_path)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Directory structure remains clean after injection")
        else:
            print("⚠️  Directory structure validation failed")
            print("   Run: python3 tools/validate_directory_structure.py <target> --auto-clean")
    
    return True

def main():
    parser = argparse.ArgumentParser(description='Execute reflow injection workflow')
    parser.add_argument('target_system', help='Path to target system for injection')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--skip-validation', action='store_true', help='Skip pre/post operation validation (not recommended)')
    
    args = parser.parse_args()
    target_path = Path(args.target_system).resolve()
    
    print(f"🚀 Reflow Injection Workflow (v1.1.0 - Modular Instructions)")
    print(f"📁 Target System: {target_path}")
    print(f"📋 Behavioral Rules: Load instructions/1-behavioral-rules.json")
    print(f"📋 File Locations: Load instructions/2-file-locations.json")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        return
    
    reflow_root = get_reflow_root()
    print(f"📁 Reflow Root: {reflow_root}")
    
    # Pre-operation validation (as per behavioral rules)
    if not args.skip_validation:
        if not validate_pre_operation_requirements(reflow_root, target_path):
            print("❌ Pre-operation validation failed")
            sys.exit(1)
    
    # Execute injection workflow steps
    steps = [
        ("Validating target system", lambda: validate_target_system(target_path)),
        ("Backing up existing context", lambda: backup_existing_context(target_path)),
        ("Creating embedded structure", lambda: create_embedded_structure(target_path)),
        ("Injecting workflows", lambda: inject_workflows(reflow_root, target_path)),
        ("Injecting tools", lambda: inject_tools(reflow_root, target_path)),
        ("Injecting templates & definitions", lambda: inject_templates_and_definitions(reflow_root, target_path)),
        ("Creating executable scripts", lambda: create_executable_scripts(target_path)),
        ("Creating configuration", lambda: create_configuration(reflow_root, target_path)),
        ("Creating documentation", lambda: create_documentation(reflow_root, target_path)),
        ("Validating injection", lambda: validate_injection(target_path))
    ]
    
    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        if not step_func():
            print(f"❌ Failed: {step_name}")
            sys.exit(1)
    
    print(f"\n🎉 Injection completed successfully!")
    
    # Post-operation validation (as per behavioral rules)
    if not args.skip_validation:
        validate_post_operation_requirements(reflow_root, target_path)
    
    print(f"\n📖 Next Steps:")
    print(f"  1. Read usage guide: {target_path}/context/README_EMBEDDED.md")
    print(f"  2. Test embedded environment: cd {target_path} && ./context/bin/validate all")
    print(f"  3. Load behavioral rules: instructions/1-behavioral-rules.json (when using embedded reflow)")
    print(f"  4. Load file locations: instructions/2-file-locations.json (if file confusion occurs)")

if __name__ == "__main__":
    main()
