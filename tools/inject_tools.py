#!/usr/bin/env python3
"""
Inject Python tools into target system with embedded mode modifications.

This tool copies all Python tools from reflow source to target system's 
context/tools/ directory, modifying them to work in embedded mode with
automatic path detection and adjustment.

Usage:
    python3 inject_tools.py <reflow_tools_dir> <target_tools_dir>
    
Example:
    python3 inject_tools.py /home/user/reflow/tools /home/user/my_system/context/tools
"""

import os
import sys
import shutil
import ast
import re
from pathlib import Path
import argparse

# Tools to exclude from injection (they're injection-specific)
EXCLUDED_TOOLS = {
    'execute_injection_flow.py',
    'validate_injection_readiness.py', 
    'inject_workflows.py',
    'inject_tools.py',
    'create_embedded_scripts.py'
}

def add_embedded_mode_detection(tool_content, tool_name):
    """Add embedded mode detection capability to tool code."""
    
    # Find import section and add embedded mode detection
    embedded_detection = '''
# Embedded mode detection (auto-added during injection)
def _detect_embedded_mode():
    """Detect if running in embedded mode and return appropriate paths."""
    script_path = Path(__file__).resolve()
    
    # Check if we're in context/tools/ (embedded mode)
    if script_path.parent.name == 'tools' and script_path.parent.parent.name == 'context':
        # We're embedded: context/tools/script.py
        system_root = script_path.parent.parent.parent  # Go up to system root
        context_root = script_path.parent.parent  # context/
        
        return {
            'embedded': True,
            'system_root': system_root,
            'context_root': context_root,
            'tools_path': context_root / 'tools',
            'templates_path': context_root / 'templates',
            'workflows_path': context_root / 'workflows',
            'definitions_path': context_root / 'definitions',
            'tracking_path': context_root / 'tracking'
        }
    else:
        # Standard reflow mode
        reflow_root = script_path.parent.parent  # Assume tools/ is in reflow root
        return {
            'embedded': False,
            'reflow_root': reflow_root,
            'tools_path': reflow_root / 'tools',
            'templates_path': reflow_root / 'templates',
            'workflows_path': reflow_root / 'workflows',
            'definitions_path': reflow_root / 'definitions'
        }

# Get mode configuration
_MODE_CONFIG = _detect_embedded_mode()
'''
    
    # Insert after imports but before main code
    lines = tool_content.split('\n')
    insert_position = 0
    
    # Find the end of imports/docstring
    in_docstring = False
    docstring_quotes = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle docstrings
        if not in_docstring and (stripped.startswith('"""') or stripped.startswith("'''")):
            in_docstring = True
            docstring_quotes = stripped[:3]
            if stripped.count(docstring_quotes) >= 2:  # Single line docstring
                in_docstring = False
                insert_position = i + 1
            continue
        elif in_docstring and docstring_quotes in line:
            in_docstring = False
            insert_position = i + 1
            continue
        elif in_docstring:
            continue
        
        # Skip imports
        if (stripped.startswith('import ') or 
            stripped.startswith('from ') or 
            stripped.startswith('#') or 
            stripped == ''):
            insert_position = i + 1
            continue
        else:
            break
    
    # Insert embedded mode detection
    lines.insert(insert_position, embedded_detection)
    
    return '\n'.join(lines)

def update_path_references(tool_content, tool_name):
    """Update hardcoded path references to use embedded mode detection."""
    
    # Common path patterns to update
    path_updates = [
        # Relative path references
        (r'\.\/tools\/', '_MODE_CONFIG["tools_path"] / '),
        (r'\.\/templates\/', '_MODE_CONFIG["templates_path"] / '),
        (r'\.\/definitions\/', '_MODE_CONFIG["definitions_path"] / '),
        (r'\.\/workflows\/', '_MODE_CONFIG["workflows_path"] / '),
        
        # Parent directory references  
        (r'\.\.\/(tools|templates|definitions|workflows)\/', r'_MODE_CONFIG["\1_path"] / '),
        (r'\.\./\.\.\/(tools|templates|definitions|workflows)\/', r'_MODE_CONFIG["\1_path"] / '),
        
        # Script directory detection patterns
        (r'Path\(__file__\)\.resolve\(\)\.parent\.parent', '_MODE_CONFIG.get("reflow_root", _MODE_CONFIG.get("context_root").parent)'),
        (r'Path\(__file__\)\.parent\.parent', '_MODE_CONFIG.get("reflow_root", _MODE_CONFIG.get("context_root").parent)')
    ]
    
    updated_content = tool_content
    
    for pattern, replacement in path_updates:
        updated_content = re.sub(pattern, replacement, updated_content)
    
    return updated_content

def add_system_path_detection(tool_content, tool_name):
    """Add automatic system path detection for embedded mode."""
    
    system_path_helper = '''
def _get_system_path(provided_path=None):
    """Get system path, handling both embedded and standard modes."""
    if provided_path:
        return Path(provided_path).resolve()
    
    if _MODE_CONFIG['embedded']:
        # In embedded mode, system is parent of context/
        return _MODE_CONFIG['system_root']
    else:
        # In standard mode, assume current directory or provided path
        return Path.cwd()
'''
    
    # Insert after embedded mode detection
    lines = tool_content.split('\n')
    
    # Find where to insert (after _MODE_CONFIG line)
    insert_position = len(lines)
    for i, line in enumerate(lines):
        if '_MODE_CONFIG = _detect_embedded_mode()' in line:
            insert_position = i + 1
            break
    
    lines.insert(insert_position, system_path_helper)
    
    return '\n'.join(lines)

def update_argument_parsing(tool_content, tool_name):
    """Update argument parsing to handle embedded mode system path defaults."""
    
    # Look for common system path argument patterns
    patterns = [
        (r"parser\.add_argument\(['\"]([^'\"]*system[^'\"]*)['\"]([^)]*)\)", 
         r'parser.add_argument("\1", default=str(_get_system_path()) if _MODE_CONFIG["embedded"] else None\2)')
    ]
    
    updated_content = tool_content
    
    for pattern, replacement in patterns:
        updated_content = re.sub(pattern, replacement, updated_content, flags=re.IGNORECASE)
    
    return updated_content

def inject_single_tool(source_file, target_file):
    """Inject a single tool file with embedded mode modifications."""
    
    tool_name = source_file.name
    
    print(f"  📄 Processing {tool_name}...")
    
    # Read source content
    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"    ❌ Failed to read {tool_name}: {e}")
        return False, f"Failed to read {tool_name}: {e}"
    
    # Apply modifications for embedded mode
    try:
        # Add Path import if not present
        if 'from pathlib import Path' not in content and 'import pathlib' not in content:
            lines = content.split('\n')
            # Find import section
            import_pos = 0
            for i, line in enumerate(lines):
                if line.startswith('import ') or line.startswith('from '):
                    import_pos = i + 1
            lines.insert(import_pos, 'from pathlib import Path')
            content = '\n'.join(lines)
        
        # Apply embedded mode modifications
        content = add_embedded_mode_detection(content, tool_name)
        content = update_path_references(content, tool_name)
        content = add_system_path_detection(content, tool_name)
        content = update_argument_parsing(content, tool_name)
        
        # Validate Python syntax
        try:
            ast.parse(content)
        except SyntaxError as e:
            print(f"    ⚠️  Syntax issue in modified {tool_name}: {e}")
            print("    📝 Falling back to simple copy...")
            # Fall back to simple copy if modifications break syntax
            with open(source_file, 'r', encoding='utf-8') as f:
                content = f.read()
        
    except Exception as e:
        print(f"    ⚠️  Failed to modify {tool_name}: {e}")
        print("    📝 Falling back to simple copy...")
        # Fall back to original content
        with open(source_file, 'r', encoding='utf-8') as f:
            content = f.read()
    
    # Write to target
    try:
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Preserve executable permissions
        if source_file.stat().st_mode & 0o111:  # If source is executable
            target_file.chmod(target_file.stat().st_mode | 0o755)
        
        print(f"    ✅ {tool_name}")
        return True, None
        
    except Exception as e:
        print(f"    ❌ Failed to write {tool_name}: {e}")
        return False, f"Failed to write {tool_name}: {e}"

def create_embedded_tools_index(target_tools_dir):
    """Create an index of available tools in the embedded environment."""
    target_path = Path(target_tools_dir)
    
    print("🔄 Creating tools index...")
    
    # Scan for all Python tools
    tools = []
    for py_file in target_path.glob('*.py'):
        if py_file.name.startswith('_'):
            continue  # Skip private/helper files
        
        # Try to extract docstring/description
        description = f"Python tool: {py_file.stem}"
        try:
            with open(py_file, 'r', encoding='utf-8') as f:
                content = f.read()
                # Look for module docstring
                if '"""' in content:
                    start = content.find('"""') + 3
                    end = content.find('"""', start)
                    if end > start:
                        docstring = content[start:end].strip()
                        # Take first line as description
                        first_line = docstring.split('\n')[0].strip()
                        if first_line and len(first_line) < 100:
                            description = first_line
        except:
            pass  # Use default description
        
        tools.append({
            "name": py_file.name,
            "path": f"./{py_file.name}",
            "description": description,
            "embedded_mode_ready": True
        })
    
    # Create index file
    index_data = {
        "embedded_tools_index": {
            "description": "Index of all available tools in embedded reflow environment",
            "created": "auto-generated during injection",
            "usage": "All tools automatically detect embedded mode and adjust paths",
            "total_tools": len(tools),
            "embedded_features": [
                "Automatic embedded mode detection",
                "Dynamic path resolution",
                "System path auto-detection",
                "Compatible with both embedded and standard modes"
            ]
        },
        "tools": tools
    }
    
    index_file = target_path / 'tools_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        import json
        json.dump(index_data, f, indent=2)
    
    print(f"  ✅ Tools index created ({len(tools)} tools)")
    
    return True, []

def generate_injection_report(target_tools_dir, results):
    """Generate a report of the injection process."""
    target_path = Path(target_tools_dir)
    
    print(f"\n📋 TOOLS INJECTION REPORT")
    print(f"🎯 Target Directory: {target_tools_dir}")
    
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
    
    # List injected tools
    injected_tools = []
    for py_file in target_path.glob('*.py'):
        injected_tools.append(py_file.name)
    
    if injected_tools:
        print(f"\n📁 INJECTED TOOLS ({len(injected_tools)}):")
        for tool_name in sorted(injected_tools):
            print(f"   🐍 {tool_name}")
    
    return success_count == total_count

def main():
    parser = argparse.ArgumentParser(description='Inject Python tools with embedded mode modifications')
    parser.add_argument('source_tools_dir', help='Path to source tools directory')
    parser.add_argument('target_tools_dir', help='Path to target tools directory (context/tools)')
    parser.add_argument('--dry-run', action='store_true', help='Show what would be done without executing')
    parser.add_argument('--simple-copy', action='store_true', help='Simple copy without modifications (fallback mode)')
    parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
    
    args = parser.parse_args()
    
    source_tools_dir = Path(args.source_tools_dir).resolve()
    target_tools_dir = Path(args.target_tools_dir).resolve()
    
    # Validate inputs
    if not source_tools_dir.exists():
        print(f"❌ Source tools directory does not exist: {source_tools_dir}")
        sys.exit(1)
    
    if not source_tools_dir.is_dir():
        print(f"❌ Source tools path is not a directory: {source_tools_dir}")
        sys.exit(1)
    
    print(f"🚀 Reflow Tools Injection")
    print(f"📂 Source: {source_tools_dir}")
    print(f"🎯 Target: {target_tools_dir}")
    
    if args.simple_copy:
        print("📝 Simple copy mode (no embedded modifications)")
    
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made")
        
        # Show what would be processed
        python_files = list(source_tools_dir.glob('*.py'))
        included_files = [f for f in python_files if f.name not in EXCLUDED_TOOLS]
        excluded_files = [f for f in python_files if f.name in EXCLUDED_TOOLS]
        
        print(f"\n📊 Would process {len(included_files)} tools:")
        for f in included_files:
            print(f"   🐍 {f.name}")
        
        if excluded_files:
            print(f"\n⏭️  Would exclude {len(excluded_files)} injection-specific tools:")
            for f in excluded_files:
                print(f"   ⚠️  {f.name}")
        
        return
    
    # Create target directory
    target_tools_dir.mkdir(parents=True, exist_ok=True)
    
    # Process all Python files
    python_files = list(source_tools_dir.glob('*.py'))
    results = []
    
    for py_file in python_files:
        if py_file.name in EXCLUDED_TOOLS:
            print(f"⏭️  Skipping injection-specific tool: {py_file.name}")
            continue
        
        target_file = target_tools_dir / py_file.name
        
        if args.simple_copy:
            # Simple copy without modifications
            try:
                shutil.copy2(py_file, target_file)
                print(f"  ✅ {py_file.name} (simple copy)")
                results.append((True, None))
            except Exception as e:
                print(f"  ❌ {py_file.name}: {e}")
                results.append((False, f"{py_file.name}: {e}"))
        else:
            # Inject with embedded mode modifications
            success, error = inject_single_tool(py_file, target_file)
            results.append((success, error))
    
    # Create tools index
    if not args.simple_copy:
        index_success, index_issues = create_embedded_tools_index(target_tools_dir)
        results.append((index_success, index_issues[0] if index_issues else None))
    
    # Generate final report
    overall_success = generate_injection_report(target_tools_dir, results)
    
    if overall_success:
        print(f"\n🎉 Tools injection completed successfully!")
        if not args.simple_copy:
            print(f"📖 Check: {target_tools_dir}/tools_index.json")
            print(f"🔧 All tools now support embedded mode with automatic path detection")
    else:
        print(f"\n⚠️  Tools injection completed with issues")
        sys.exit(1)

if __name__ == "__main__":
    main()