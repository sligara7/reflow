# Workflow Driver Updates Needed for New Structure

## Overview

The `workflow_driver.py` needs to be updated to support the new multi-workflow structure. This document outlines the required changes.

## Current Limitations

### 1. **Hardcoded System Path**
```python
# Current (line 65):
self.system_path = self.reflow_root / "systems" / system_name

# Problem: Assumes systems are in reflow/systems/ directory
# Solution: Accept system path as argument or discover from working_memory.json
```

**Required Change**:
```python
def __init__(self, system_path_or_name):
    self.reflow_root = Path(__file__).parent

    # If argument is a path, use it directly
    if Path(system_path_or_name).exists():
        self.system_path = Path(system_path_or_name).resolve()
        self.system_name = self.system_path.name
    else:
        # Fallback to old behavior (backward compatibility)
        self.system_name = system_path_or_name
        self.system_path = self.reflow_root / "systems" / system_name
```

---

### 2. **Uses Old Index File**
```python
# Current (line 66):
self.workflows_index = self.load_workflows_index()

# Problem: Loads workflows_index.json instead of workflows_master_index.json
```

**Required Change**:
```python
def load_workflows_master_index(self):
    """Load workflows_master_index.json"""
    index_path = self.reflow_root / "workflows_master_index.json"
    if not index_path.exists():
        # Fallback to old file for backward compatibility
        index_path = self.reflow_root / "workflows_index.json"
        if not index_path.exists():
            print_error(f"No workflow index found")
            sys.exit(1)
    with open(index_path) as f:
        return json.load(f)
```

---

### 3. **No Workflow Tracking**
```python
# Current: Tracks current step, but not current workflow
# Problem: Can't manage transitions between workflows

# Required: Track current workflow in working_memory.json
```

**Required Changes in `working_memory.json` schema**:
```json
{
  "current_workflow": "01-systems_engineering",
  "current_step": "SE-02",
  "current_substep": "SE-02-A01",
  "workflow_history": [
    {"workflow": "00-setup", "completed": "2025-10-24T10:00:00Z"},
    {"workflow": "01-systems_engineering", "status": "in_progress"}
  ],
  "paths": {
    "reflow_root": "/home/user/dev/reflow",
    "system_root": "/home/user/projects/my_system",
    "workflow_steps_path": "/home/user/dev/reflow/workflow_steps",
    "tools_path": "/home/user/dev/reflow/tools",
    "templates_path": "/home/user/dev/reflow/templates"
  }
}
```

**Required Methods**:
```python
def get_current_workflow(self):
    """Get the current workflow from working_memory.json"""
    return self.working_memory.get('current_workflow', '00-setup')

def load_current_workflow_config(self):
    """Load the current workflow JSON file"""
    current_workflow = self.get_current_workflow()
    workflow_file = self.reflow_root / "workflows" / f"{current_workflow}.json"
    if not workflow_file.exists():
        print_error(f"Workflow file not found: {workflow_file}")
        sys.exit(1)
    with open(workflow_file) as f:
        return json.load(f)

def transition_to_next_workflow(self):
    """Transition to the next workflow"""
    workflow_config = self.load_current_workflow_config()
    next_workflow = workflow_config.get('completion', {}).get('next_workflow')

    if not next_workflow:
        print_success("No next workflow - this was the final workflow!")
        return

    # Update working memory
    self.working_memory['current_workflow'] = next_workflow
    self.working_memory['workflow_history'].append({
        'workflow': workflow_config['workflow_metadata']['workflow_id'],
        'completed': datetime.now().isoformat() + 'Z'
    })

    # Load next workflow and set first step
    next_config = self.load_workflow_config(next_workflow)
    first_step = next_config['workflow_steps'][0]['step_id']
    self.working_memory['current_step'] = first_step
    self.working_memory['current_substep'] = ''

    self.save_working_memory()
    print_success(f"Transitioned to workflow: {next_workflow}")
```

---

### 4. **Step File Loading**
```python
# Current (lines 127-157):
def get_current_step_file(self):
    # Uses old directory structure (architecture/, development/, feature_update/)

# Problem: Needs to use new workflow_steps/ directory
```

**Required Change**:
```python
def get_current_step_file(self):
    """Get the current step JSON file path"""
    current_workflow = self.get_current_workflow()
    current_step = self.working_memory.get('current_step', '')

    # Get workflow config to find steps directory
    workflow_config = self.load_current_workflow_config()
    steps_directory = workflow_config['workflow_steps'][0].get('step_file', '').split('/')[0]

    # Look for step file in workflow_steps/{workflow_type}/
    step_pattern = f"workflow_steps/{steps_directory}/*{current_step}*.json"
    matches = list(self.reflow_root.glob(step_pattern))

    if matches:
        return matches[0]

    # Fallback: check old structure for backward compatibility
    old_patterns = [
        f"architecture/*{current_step}*.json",
        f"development/*{current_step}*.json",
        f"feature_update/*{current_step}*.json"
    ]

    for pattern in old_patterns:
        matches = list(self.reflow_root.glob(pattern))
        if matches:
            print_warning(f"Using deprecated step file location: {matches[0]}")
            return matches[0]

    return None
```

---

### 5. **Missing Commands**

**New commands needed**:
```bash
# List all workflows
python3 workflow_driver.py <system> --list-workflows

# Show current workflow
python3 workflow_driver.py <system> --current-workflow

# Specify workflow explicitly
python3 workflow_driver.py <system> --workflow 01-systems_engineering

# Transition to next workflow
python3 workflow_driver.py <system> --next-workflow

# Show workflow progress (which workflows completed)
python3 workflow_driver.py <system> --workflow-status
```

**Required Argument Parser Updates**:
```python
def setup_argument_parser():
    parser = argparse.ArgumentParser(
        description='Reflow Workflow Driver',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    # Show current state
    python3 workflow_driver.py /path/to/system

    # List all workflows
    python3 workflow_driver.py /path/to/system --list-workflows

    # Show current workflow
    python3 workflow_driver.py /path/to/system --current-workflow

    # Transition to next workflow
    python3 workflow_driver.py /path/to/system --next-workflow

    # Set workflow explicitly
    python3 workflow_driver.py /path/to/system --workflow 01-systems_engineering

    # Other commands (existing)
    python3 workflow_driver.py /path/to/system --next
    python3 workflow_driver.py /path/to/system --validate
    python3 workflow_driver.py /path/to/system --refresh
        """
    )

    parser.add_argument('system', help='System name or path')
    parser.add_argument('--list-workflows', action='store_true',
                       help='List all available workflows')
    parser.add_argument('--current-workflow', action='store_true',
                       help='Show current workflow')
    parser.add_argument('--next-workflow', action='store_true',
                       help='Transition to next workflow')
    parser.add_argument('--workflow', metavar='ID',
                       help='Set current workflow (e.g., 01-systems_engineering)')
    parser.add_argument('--workflow-status', action='store_true',
                       help='Show workflow completion status')

    # Existing arguments
    parser.add_argument('--next', action='store_true',
                       help='Advance to next step')
    parser.add_argument('--validate', action='store_true',
                       help='Run validation gate')
    parser.add_argument('--refresh', action='store_true',
                       help='Force context refresh')
    parser.add_argument('--mark-done', metavar='ID',
                       help='Mark action as complete')
    parser.add_argument('--status', action='store_true',
                       help='Show overall status')
    parser.add_argument('--init', action='store_true',
                       help='Initialize new system')

    return parser
```

---

## Implementation Priority

### Priority 1 (Critical for New Structure)
1. ✅ Accept system path as argument (not just name)
2. ✅ Load `workflows_master_index.json`
3. ✅ Track current workflow in `working_memory.json`
4. ✅ `--next-workflow` command
5. ✅ Load step files from `workflow_steps/`

### Priority 2 (Nice to Have)
1. ✅ `--list-workflows` command
2. ✅ `--current-workflow` command
3. ✅ `--workflow-status` command
4. ✅ `--workflow <id>` command (set workflow explicitly)
5. ✅ Workflow progress visualization

### Priority 3 (Enhancement)
1. ✅ Automatic workflow transition detection
2. ✅ Workflow dependency validation
3. ✅ Conditional workflow handling (e.g., skip artifacts if architecture-only)
4. ✅ Workflow completion celebration output

---

## Backward Compatibility

To maintain backward compatibility:

1. **Check for both index files**: Try `workflows_master_index.json` first, fallback to `workflows_index.json`
2. **Support both path formats**: Accept both system path and system name
3. **Check both step directories**: Try `workflow_steps/` first, fallback to old directories
4. **Graceful degradation**: If new fields missing in `working_memory.json`, use defaults

```python
def ensure_backward_compatibility(self):
    """Ensure working memory has all required fields for new structure"""
    if 'current_workflow' not in self.working_memory:
        # Infer workflow from current step
        current_step = self.working_memory.get('current_step', '')
        if current_step.startswith('Arch-'):
            self.working_memory['current_workflow'] = '01-systems_engineering'
        elif current_step.startswith('Dev-'):
            self.working_memory['current_workflow'] = '03-development'
        elif current_step.startswith('FU-'):
            self.working_memory['current_workflow'] = 'feature_update'
        else:
            self.working_memory['current_workflow'] = '00-setup'

    if 'workflow_history' not in self.working_memory:
        self.working_memory['workflow_history'] = []

    if 'paths' not in self.working_memory:
        self.working_memory['paths'] = {
            'reflow_root': str(self.reflow_root),
            'system_root': str(self.system_path)
        }

    self.save_working_memory()
```

---

## Testing Plan

1. **Test with new systems**:
   - Start fresh system with 00-setup workflow
   - Progress through all workflows
   - Verify transitions work correctly

2. **Test with old systems**:
   - Load system using old structure
   - Verify backward compatibility
   - Test migration path

3. **Test edge cases**:
   - System path vs system name
   - Missing workflow files
   - Corrupted working_memory.json
   - Workflow without next_workflow (end of chain)

---

## Example Updated Commands

```bash
# Old way (still supported)
python3 workflow_driver.py my_system --status

# New way (recommended)
python3 workflow_driver.py /home/user/projects/my_system --workflow-status

# New workflow commands
python3 workflow_driver.py /home/user/projects/my_system --current-workflow
python3 workflow_driver.py /home/user/projects/my_system --next-workflow
python3 workflow_driver.py /home/user/projects/my_system --list-workflows

# Set workflow explicitly
python3 workflow_driver.py /home/user/projects/my_system --workflow 02-artifacts_visualization
```

---

## Summary

The `workflow_driver.py` needs significant updates to support the new multi-workflow structure. The key changes are:

1. Accept system paths (not just names)
2. Use `workflows_master_index.json`
3. Track current workflow
4. Support workflow transitions
5. Load steps from `workflow_steps/`
6. Add new commands for workflow management
7. Maintain backward compatibility

**Estimated Effort**: 4-6 hours of development + 2-3 hours of testing

**Impact**: High (core functionality)

**Risk**: Medium (with proper backward compatibility testing)

---

## Next Actions

1. Create `workflow_driver_v2.py` with new functionality
2. Test thoroughly with sample systems
3. Update documentation
4. Deprecate old `workflow_driver.py` gradually
5. Update all user guides and tutorials

OR

1. Update existing `workflow_driver.py` in-place
2. Add comprehensive tests
3. Update documentation
4. Announce breaking changes (if any)
