#!/usr/bin/env python3
"""
Create executable wrapper scripts for embedded reflow environment.

This tool generates convenience scripts in context/bin/ that provide easy
access to embedded reflow workflows and tools with proper path resolution.

Usage:
    python3 create_embedded_scripts.py <target_bin_dir>
    
Example:
    python3 create_embedded_scripts.py /home/user/my_system/context/bin
"""

import os
import sys
from pathlib import Path
import argparse
import stat

def create_main_reflow_script(bin_dir):
    """Create the main 'reflow' workflow execution script."""
    
    script_path = Path(bin_dir) / 'reflow'
    
    script_content = '''#!/bin/bash
# Embedded Reflow Workflow Execution Script
# Auto-generated during reflow injection

set -e

# Detect paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_ROOT="$SCRIPT_DIR/.."

# Change to system root for all operations
cd "$SYSTEM_ROOT"

# Function to display usage
show_usage() {
    echo "🚀 Embedded Reflow Workflow Executor"
    echo ""
    echo "Usage: $0 <workflow_step> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 development/Dev-01-InitBootstrap.json"
    echo "  $0 architecture/Arch-01-SetupAndContext.json" 
    echo "  $0 decision_flow.json"
    echo ""
    echo "Available workflows:"
    if [ -d "$CONTEXT_ROOT/workflows" ]; then
        find "$CONTEXT_ROOT/workflows" -name "*.json" -type f | \\
            sed "s|$CONTEXT_ROOT/workflows/||" | \\
            sort | \\
            sed 's/^/  📄 /'
    else
        echo "  ❌ No workflows directory found"
    fi
    echo ""
    echo "📁 System root: $SYSTEM_ROOT"
    echo "📁 Context root: $CONTEXT_ROOT"
}

# Function to execute workflow
execute_workflow() {
    local workflow_path="$1"
    shift  # Remove workflow_path from arguments
    
    # Check if workflow file exists
    local full_workflow_path="$CONTEXT_ROOT/workflows/$workflow_path"
    if [ ! -f "$full_workflow_path" ]; then
        echo "❌ Workflow not found: $workflow_path"
        echo "📁 Looked in: $full_workflow_path"
        echo ""
        echo "Available workflows:"
        find "$CONTEXT_ROOT/workflows" -name "*.json" -type f | \\
            sed "s|$CONTEXT_ROOT/workflows/||" | \\
            sort | \\
            sed 's/^/  📄 /'
        exit 1
    fi
    
    echo "🔄 Executing embedded reflow workflow: $workflow_path"
    echo "📁 System root: $SYSTEM_ROOT"
    echo "📁 Workflow: $full_workflow_path"
    echo ""
    
    # Future enhancement: Parse and execute workflow steps
    echo "ℹ️  Workflow execution framework will be implemented in future iteration"
    echo "ℹ️  For now, this script validates paths and workflow existence"
    echo ""
    echo "📖 To manually execute workflow steps, refer to:"
    echo "   cat '$full_workflow_path'"
    echo ""
    echo "🔧 Use embedded tools directly:"
    echo "   python3 '$CONTEXT_ROOT/tools/validate_architecture.py' ."
    echo "   python3 '$CONTEXT_ROOT/tools/system_of_systems_graph.py' specs/machine/index.json"
    
    # Return success to indicate workflow was found and validated
    return 0
}

# Main script logic
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    "-h"|"--help"|"help")
        show_usage
        exit 0
        ;;
    "list"|"ls")
        echo "📋 Available workflows:"
        if [ -d "$CONTEXT_ROOT/workflows" ]; then
            find "$CONTEXT_ROOT/workflows" -name "*.json" -type f | \\
                sed "s|$CONTEXT_ROOT/workflows/||" | \\
                sort | \\
                sed 's/^/  📄 /'
        fi
        exit 0
        ;;
    *)
        execute_workflow "$@"
        ;;
esac
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"  ✅ reflow - Main workflow executor")
    return True, None

def create_validate_script(bin_dir):
    """Create the 'validate' script for running validation tools."""
    
    script_path = Path(bin_dir) / 'validate'
    
    script_content = '''#!/bin/bash
# Embedded Reflow Validation Script
# Auto-generated during reflow injection

set -e

# Detect paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_ROOT="$SCRIPT_DIR/.."

# Change to system root for all operations
cd "$SYSTEM_ROOT"

# Function to display usage
show_usage() {
    echo "🔍 Embedded Reflow Validation Tools"
    echo ""
    echo "Usage: $0 [validation_type]"
    echo ""
    echo "Validation types:"
    echo "  architecture, arch    - Validate service architectures"
    echo "  contracts            - Generate and validate interface contracts"
    echo "  graph               - Analyze system graph for issues"
    echo "  foundational        - Validate foundational document alignment"
    echo "  all                 - Run all validations (default)"
    echo ""
    echo "Examples:"
    echo "  $0 architecture"
    echo "  $0 all"
    echo ""
    echo "📁 System root: $SYSTEM_ROOT"
    echo "📁 Tools: $CONTEXT_ROOT/tools"
}

# Function to run validation
run_validation() {
    local validation_type="${1:-all}"
    
    echo "🔍 Running $validation_type validation..."
    echo "📁 Working directory: $(pwd)"
    echo ""
    
    case "$validation_type" in
        "architecture"|"arch")
            if [ -f "$CONTEXT_ROOT/tools/validate_architecture.py" ]; then
                echo "🏗️  Validating architecture..."
                python3 "$CONTEXT_ROOT/tools/validate_architecture.py" .
            else
                echo "❌ validate_architecture.py not found in embedded tools"
                exit 1
            fi
            ;;
        "contracts")
            if [ -f "$CONTEXT_ROOT/tools/generate_interface_contracts.py" ]; then
                echo "📋 Generating and validating interface contracts..."
                # Copy index.json to current directory (tool requirement)
                if [ -f "specs/machine/index.json" ]; then
                    cp specs/machine/index.json .
                    python3 "$CONTEXT_ROOT/tools/generate_interface_contracts.py" .
                    rm -f index.json  # Clean up
                else
                    echo "❌ specs/machine/index.json not found"
                    exit 1
                fi
            else
                echo "❌ generate_interface_contracts.py not found in embedded tools"
                exit 1
            fi
            ;;
        "graph")
            if [ -f "$CONTEXT_ROOT/tools/system_of_systems_graph.py" ]; then
                echo "📊 Analyzing system graph..."
                if [ -f "specs/machine/index.json" ]; then
                    python3 "$CONTEXT_ROOT/tools/system_of_systems_graph.py" specs/machine/index.json --analyze-issues
                else
                    echo "❌ specs/machine/index.json not found"
                    exit 1
                fi
            else
                echo "❌ system_of_systems_graph.py not found in embedded tools"
                exit 1
            fi
            ;;
        "foundational")
            if [ -f "$CONTEXT_ROOT/tools/validate_foundational_alignment.py" ]; then
                echo "📚 Validating foundational document alignment..."
                python3 "$CONTEXT_ROOT/tools/validate_foundational_alignment.py" .
            else
                echo "❌ validate_foundational_alignment.py not found in embedded tools"
                exit 1
            fi
            ;;
        "all")
            echo "🔍 Running all validations..."
            echo ""
            
            # Run architecture validation
            if [ -f "$CONTEXT_ROOT/tools/validate_architecture.py" ]; then
                echo "1️⃣  Architecture validation:"
                python3 "$CONTEXT_ROOT/tools/validate_architecture.py" . || true
                echo ""
            fi
            
            # Run graph analysis
            if [ -f "$CONTEXT_ROOT/tools/system_of_systems_graph.py" ] && [ -f "specs/machine/index.json" ]; then
                echo "2️⃣  System graph analysis:"
                python3 "$CONTEXT_ROOT/tools/system_of_systems_graph.py" specs/machine/index.json --analyze-issues || true
                echo ""
            fi
            
            # Run foundational alignment if tool exists
            if [ -f "$CONTEXT_ROOT/tools/validate_foundational_alignment.py" ]; then
                echo "3️⃣  Foundational alignment:"
                python3 "$CONTEXT_ROOT/tools/validate_foundational_alignment.py" . || true
                echo ""
            fi
            
            echo "✅ All validations completed"
            ;;
        *)
            echo "❌ Unknown validation type: $validation_type"
            show_usage
            exit 1
            ;;
    esac
}

# Main script logic
case "${1:-all}" in
    "-h"|"--help"|"help")
        show_usage
        exit 0
        ;;
    *)
        run_validation "$1"
        ;;
esac
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"  ✅ validate - Validation tools runner")
    return True, None

def create_setup_dev_script(bin_dir):
    """Create the 'setup-dev' script for development environment setup."""
    
    script_path = Path(bin_dir) / 'setup-dev'
    
    script_content = '''#!/bin/bash
# Embedded Reflow Development Setup Script
# Auto-generated during reflow injection

set -e

# Detect paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_ROOT="$SCRIPT_DIR/.."

# Change to system root for all operations
cd "$SYSTEM_ROOT"

echo "🚀 Embedded Reflow Development Environment Setup"
echo ""
echo "📁 System root: $SYSTEM_ROOT"
echo "📁 Context root: $CONTEXT_ROOT"
echo ""

# Function to check if file exists
check_file() {
    local file="$1"
    local description="$2"
    if [ -f "$file" ]; then
        echo "  ✅ $description"
        return 0
    else
        echo "  ❌ $description (missing: $file)"
        return 1
    fi
}

# Function to check if directory exists
check_dir() {
    local dir="$1"
    local description="$2"
    if [ -d "$dir" ]; then
        echo "  ✅ $description"
        return 0
    else
        echo "  ❌ $description (missing: $dir)"
        return 1
    fi
}

echo "🔍 Checking embedded environment..."

# Check embedded structure
check_dir "$CONTEXT_ROOT/workflows" "Embedded workflows"
check_dir "$CONTEXT_ROOT/tools" "Embedded tools"
check_dir "$CONTEXT_ROOT/templates" "Embedded templates"
check_dir "$CONTEXT_ROOT/definitions" "Embedded definitions"
check_dir "$CONTEXT_ROOT/tracking" "Tracking files"

echo ""
echo "🔍 Checking system structure..."

# Check system structure
check_dir "specs" "System specifications"
check_dir "services" "Service implementations"
check_dir "docs" "System documentation"

echo ""
echo "🔍 Checking key files..."

# Check key files
check_file "specs/machine/index.json" "System index"
check_file "docs/SYSTEM_MISSION_STATEMENT.md" "Mission statement" || true
check_file "$CONTEXT_ROOT/config/embedded.json" "Embedded configuration"

echo ""
echo "🧪 Running embedded environment tests..."

# Test embedded tools
if [ -f "$CONTEXT_ROOT/tools/validate_architecture.py" ]; then
    echo "  🧪 Testing validate_architecture.py..."
    python3 "$CONTEXT_ROOT/tools/validate_architecture.py" . --help >/dev/null 2>&1 && echo "    ✅ Tool executes correctly" || echo "    ⚠️  Tool may have issues"
fi

if [ -f "specs/machine/index.json" ] && [ -f "$CONTEXT_ROOT/tools/system_of_systems_graph.py" ]; then
    echo "  🧪 Testing system_of_systems_graph.py..."
    python3 "$CONTEXT_ROOT/tools/system_of_systems_graph.py" specs/machine/index.json --help >/dev/null 2>&1 && echo "    ✅ Tool executes correctly" || echo "    ⚠️  Tool may have issues"
fi

echo ""
echo "📖 Development environment summary:"
echo ""
echo "🔧 Available commands:"
echo "  ./context/bin/reflow <workflow>     - Execute embedded workflows"
echo "  ./context/bin/validate [type]      - Run validation tools"
echo "  python3 context/tools/<tool>.py    - Run tools directly"
echo ""
echo "📚 Documentation:"
echo "  context/README_EMBEDDED.md         - Embedded environment guide"
echo "  context/INJECTION_HISTORY.md       - Injection history"
echo ""
if [ -f "$CONTEXT_ROOT/workflows/workflows_index.json" ]; then
    echo "📋 Available workflows:"
    if command -v jq >/dev/null 2>&1; then
        jq -r '.workflows.main_workflows[]?, .workflows.architecture_workflows[]?, .workflows.development_workflows[]? | "  📄 \\(.path)"' "$CONTEXT_ROOT/workflows/workflows_index.json" 2>/dev/null || echo "  📄 See context/workflows/workflows_index.json"
    else
        echo "  📄 See context/workflows/workflows_index.json"
    fi
    echo ""
fi

echo "✅ Development environment setup check completed!"
echo ""
echo "🎯 Next steps:"
echo "  1. Review context/README_EMBEDDED.md"
echo "  2. Run: ./context/bin/validate all"
echo "  3. Continue development with: ./context/bin/reflow <workflow>"
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"  ✅ setup-dev - Development environment checker")
    return True, None

def create_tool_runner_script(bin_dir):
    """Create a generic 'tool' script for running any embedded tool."""
    
    script_path = Path(bin_dir) / 'tool'
    
    script_content = '''#!/bin/bash
# Embedded Reflow Tool Runner Script
# Auto-generated during reflow injection

set -e

# Detect paths relative to this script
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SYSTEM_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONTEXT_ROOT="$SCRIPT_DIR/.."

# Change to system root for all operations
cd "$SYSTEM_ROOT"

# Function to display usage
show_usage() {
    echo "🔧 Embedded Reflow Tool Runner"
    echo ""
    echo "Usage: $0 <tool_name> [args...]"
    echo ""
    echo "Examples:"
    echo "  $0 validate_architecture ."
    echo "  $0 system_of_systems_graph specs/machine/index.json --analyze-issues"
    echo "  $0 generate_interface_contracts ."
    echo ""
    echo "Available tools:"
    if [ -d "$CONTEXT_ROOT/tools" ]; then
        find "$CONTEXT_ROOT/tools" -name "*.py" -type f | \\
            grep -v "^_" | \\
            sed "s|$CONTEXT_ROOT/tools/||" | \\
            sed "s|\\.py$||" | \\
            sort | \\
            sed 's/^/  🐍 /'
    else
        echo "  ❌ No tools directory found"
    fi
    echo ""
    echo "📁 System root: $SYSTEM_ROOT"
    echo "📁 Tools: $CONTEXT_ROOT/tools"
}

# Function to execute tool
execute_tool() {
    local tool_name="$1"
    shift  # Remove tool_name from arguments
    
    # Add .py extension if not present
    if [[ "$tool_name" != *.py ]]; then
        tool_name="$tool_name.py"
    fi
    
    # Check if tool file exists
    local tool_path="$CONTEXT_ROOT/tools/$tool_name"
    if [ ! -f "$tool_path" ]; then
        echo "❌ Tool not found: $tool_name"
        echo "📁 Looked in: $tool_path"
        echo ""
        echo "Available tools:"
        find "$CONTEXT_ROOT/tools" -name "*.py" -type f | \\
            grep -v "^_" | \\
            sed "s|$CONTEXT_ROOT/tools/||" | \\
            sed "s|\\.py$||" | \\
            sort | \\
            sed 's/^/  🐍 /'
        exit 1
    fi
    
    echo "🔧 Running embedded tool: $tool_name"
    echo "📁 System root: $SYSTEM_ROOT"
    echo "🐍 Tool: $tool_path"
    echo ""
    
    # Execute the tool with all remaining arguments
    python3 "$tool_path" "$@"
}

# Main script logic
if [ $# -eq 0 ]; then
    show_usage
    exit 1
fi

case "$1" in
    "-h"|"--help"|"help")
        show_usage
        exit 0
        ;;
    "list"|"ls")
        echo "🔧 Available tools:"
        if [ -d "$CONTEXT_ROOT/tools" ]; then
            find "$CONTEXT_ROOT/tools" -name "*.py" -type f | \\
                grep -v "^_" | \\
                sed "s|$CONTEXT_ROOT/tools/||" | \\
                sed "s|\\.py$||" | \\
                sort | \\
                sed 's/^/  🐍 /'
        fi
        exit 0
        ;;
    *)
        execute_tool "$@"
        ;;
esac
'''
    
    with open(script_path, 'w') as f:
        f.write(script_content)
    
    # Make executable
    script_path.chmod(stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
    
    print(f"  ✅ tool - Generic tool runner")
    return True, None

def create_scripts_index(bin_dir):
    """Create an index of available scripts."""
    
    bin_path = Path(bin_dir)
    
    print("🔄 Creating scripts index...")
    
    # Scan for all executable scripts
    scripts = []
    for script_file in bin_path.iterdir():
        if script_file.is_file() and os.access(script_file, os.X_OK):
            if script_file.name in ['scripts_index.json']:
                continue  # Skip the index file itself
            
            description = f"Executable script: {script_file.name}"
            
            # Try to extract description from script comments
            try:
                with open(script_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()[:10]  # Read first 10 lines
                    for line in lines:
                        line = line.strip()
                        if line.startswith('# ') and len(line) > 3:
                            potential_desc = line[2:].strip()
                            if len(potential_desc) > 10 and len(potential_desc) < 100:
                                description = potential_desc
                                break
            except:
                pass  # Use default description
            
            scripts.append({
                "name": script_file.name,
                "path": f"./{script_file.name}",
                "description": description,
                "executable": True
            })
    
    # Create index file
    index_data = {
        "embedded_scripts_index": {
            "description": "Index of all available executable scripts in embedded reflow environment",
            "created": "auto-generated during injection",
            "usage": "Execute scripts from system root: ./context/bin/<script>",
            "total_scripts": len(scripts)
        },
        "scripts": scripts
    }
    
    index_file = bin_path / 'scripts_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(index_data, f, indent=2)
    
    print(f"  ✅ Scripts index created ({len(scripts)} scripts)")
    
    return True, []

def generate_creation_report(bin_dir, results):
    """Generate a report of the script creation process."""
    bin_path = Path(bin_dir)
    
    print(f"\n📋 SCRIPT CREATION REPORT")
    print(f"🎯 Target Directory: {bin_dir}")
    
    success_count = sum(1 for success, _ in results if success)
    total_count = len(results)
    
    print(f"✅ Successful: {success_count}/{total_count} operations")
    
    # Collect all issues
    all_issues = []
    for success, issue in results:
        if issue:
            all_issues.append(issue)
    
    if all_issues:
        print(f"\n⚠️  ISSUES ({len(all_issues)}):")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")
    
    # List created scripts
    created_scripts = []
    for script_file in bin_path.iterdir():
        if script_file.is_file() and os.access(script_file, os.X_OK):
            created_scripts.append(script_file.name)
    
    if created_scripts:
        print(f"\n📁 CREATED SCRIPTS ({len(created_scripts)}):")
        for script_name in sorted(created_scripts):
            print(f"   🔧 {script_name}")
    
    return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description='Create executable wrapper scripts for embedded reflow environment')
    parser.add_argument('target_bin_dir', help='Path to target bin directory (context/bin)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    target_bin_dir = Path(args.target_bin_dir).resolve()
    
    print(f"🚀 Reflow Embedded Scripts Creation")
    print(f"🎯 Target: {target_bin_dir}")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        print("\n📊 Would create scripts:")
        scripts = ['reflow', 'validate', 'setup-dev', 'tool', 'scripts_index.json']
        for script in scripts:
            print(f"   🔧 {script}")
        return
    
    # Create target directory
    target_bin_dir.mkdir(parents=True, exist_ok=True)
    
    # Create all scripts
    operations = [
        ("reflow script", lambda: create_main_reflow_script(target_bin_dir)),
        ("validate script", lambda: create_validate_script(target_bin_dir)),
        ("setup-dev script", lambda: create_setup_dev_script(target_bin_dir)),
        ("tool runner script", lambda: create_tool_runner_script(target_bin_dir)),
        ("scripts index", lambda: create_scripts_index(target_bin_dir))
    ]
    
    print("\n🔄 Creating scripts...")
    results = []
    
    for operation_name, operation_func in operations:
        success, error = operation_func()
        results.append((success, error))
        
        if not success:
            print(f"❌ Failed: {operation_name}")
            if error:
                print(f"   • {error}")
    
    # Generate final report
    overall_success = generate_creation_report(target_bin_dir, results)
    
    if overall_success:
        print(f"\n🎉 Embedded scripts created successfully!")
        print(f"📖 Check: {target_bin_dir}/scripts_index.json")
        print(f"🔧 All scripts are executable and ready for use")
    else:
        print(f"\n⚠️  Script creation completed with issues")
        sys.exit(1)

if __name__ == "__main__":
    main()