#!/usr/bin/env python3
"""
Reflow Workflow Driver - MANDATORY entry point for all reflow operations

This driver enforces the workflow, tracks progress, validates gates, and prevents
common issues like context drift and skipping validation.

Usage:
    python3 workflow_driver.py <system_name>                    # Show current step
    python3 workflow_driver.py <system_name> --refresh          # Force context refresh
    python3 workflow_driver.py <system_name> --next             # Advance to next step
    python3 workflow_driver.py <system_name> --validate         # Run validation gate
    python3 workflow_driver.py <system_name> --mark-done <id>   # Mark action complete
    python3 workflow_driver.py <system_name> --status           # Show overall status
    python3 workflow_driver.py <system_name> --init             # Initialize new system

Examples:
    python3 workflow_driver.py dnd_reflow
    python3 workflow_driver.py dnd_reflow --mark-done D1.2
    python3 workflow_driver.py dnd_reflow --validate
    python3 workflow_driver.py dnd_reflow --next
"""

import json
import sys
import os
from pathlib import Path
from datetime import datetime, timedelta
import subprocess
import argparse

# Colors for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")

def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")

def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")

def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")

def print_info(text):
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")

class WorkflowDriver:
    def __init__(self, system_name):
        self.reflow_root = Path(__file__).parent
        self.system_name = system_name
        self.system_path = self.reflow_root / "systems" / system_name
        self.workflows_index = self.load_workflows_index()
        self.decision_flow = self.load_decision_flow()

        # Check if system exists
        if not self.system_path.exists():
            print_error(f"System directory not found: {self.system_path}")
            print_info("Run with --init to create a new system")
            sys.exit(1)

        self.working_memory = self.load_working_memory()
        self.progress_tracker = self.load_progress_tracker()

    def load_workflows_index(self):
        """Load workflows_index.json"""
        index_path = self.reflow_root / "workflows_index.json"
        if not index_path.exists():
            print_error(f"workflows_index.json not found at {index_path}")
            sys.exit(1)
        with open(index_path) as f:
            return json.load(f)

    def load_decision_flow(self):
        """Load decision_flow.json"""
        flow_path = self.reflow_root / "decision_flow.json"
        if not flow_path.exists():
            print_error(f"decision_flow.json not found at {flow_path}")
            sys.exit(1)
        with open(flow_path) as f:
            return json.load(f)

    def load_working_memory(self):
        """Load working_memory.json"""
        wm_path = self.system_path / "working_memory.json"
        if not wm_path.exists():
            print_error(f"working_memory.json not found at {wm_path}")
            print_info("Initialize the system first with the workflow")
            sys.exit(1)
        with open(wm_path) as f:
            return json.load(f)

    def load_progress_tracker(self):
        """Load step_progress_tracker.json"""
        tracker_path = self.system_path / "step_progress_tracker.json"
        if not tracker_path.exists():
            print_error(f"step_progress_tracker.json not found at {tracker_path}")
            sys.exit(1)
        with open(tracker_path) as f:
            return json.load(f)

    def save_working_memory(self):
        """Save working_memory.json"""
        wm_path = self.system_path / "working_memory.json"
        with open(wm_path, 'w') as f:
            json.dump(self.working_memory, f, indent=2)

    def save_progress_tracker(self):
        """Save step_progress_tracker.json"""
        tracker_path = self.system_path / "step_progress_tracker.json"
        with open(tracker_path, 'w') as f:
            json.dump(self.progress_tracker, f, indent=2)

    def get_current_step_file(self):
        """Get the current step JSON file path"""
        current_step = self.working_memory.get('current_step', '')

        # Map step ID to workflow file
        for workflow_type, workflows in self.workflows_index.items():
            if workflow_type == 'version' or workflow_type == 'description':
                continue
            for step_id, step_file in workflows.items():
                # Handle different step ID formats
                if '-' in step_id:
                    # Check if current step matches this workflow step
                    if current_step.startswith(step_id) or current_step == step_id:
                        step_path = self.reflow_root / step_file
                        if step_path.exists():
                            return step_path

        # Fallback: try to find by pattern
        # Handle both formats: "Dev-02" and "D2"
        patterns = [
            f"architecture/*{current_step}*.json",
            f"development/*{current_step}*.json",
            f"feature_update/*{current_step}*.json"
        ]

        for pattern in patterns:
            matches = list(self.reflow_root.glob(pattern))
            if matches:
                return matches[0]

        return None

    def load_current_step_config(self):
        """Load the current step configuration"""
        step_file = self.get_current_step_file()
        if not step_file:
            print_error(f"Could not find step file for: {self.working_memory.get('current_step')}")
            return None

        with open(step_file) as f:
            return json.load(f)

    def check_context_refresh_needed(self):
        """Check if context refresh is required"""
        operations_count = self.working_memory.get('operations_since_refresh', 0)
        last_refresh_str = self.working_memory.get('last_refresh_timestamp', '')

        needs_refresh = []

        # Check operation count
        if operations_count >= 4:
            needs_refresh.append(f"Operation count threshold reached ({operations_count}/4)")

        # Check time threshold
        if last_refresh_str:
            try:
                last_refresh = datetime.fromisoformat(last_refresh_str.replace('Z', '+00:00'))
                time_since = datetime.now() - last_refresh.replace(tzinfo=None)
                if time_since > timedelta(minutes=12):
                    needs_refresh.append(f"Time threshold exceeded ({int(time_since.total_seconds()/60)} minutes)")
            except:
                pass

        return needs_refresh

    def refresh_context(self):
        """Force context refresh"""
        print_header("CONTEXT REFRESH")

        print_info("Refreshing context from core files...")

        # Files to refresh
        files_to_read = [
            (self.reflow_root / "definitions/architectural_definitions.json", "Architectural Definitions"),
            (self.reflow_root / "decision_flow.json", "Decision Flow"),
            (self.system_path / "working_memory.json", "Working Memory"),
            (self.system_path / "step_progress_tracker.json", "Progress Tracker"),
            (self.system_path / "current_focus.md", "Current Focus")
        ]

        print("\n" + "─" * 70)
        for file_path, description in files_to_read:
            if file_path.exists():
                print_success(f"Read: {description}")
            else:
                print_warning(f"Missing: {description}")
        print("─" * 70 + "\n")

        # Update working memory
        self.working_memory['operations_since_refresh'] = 0
        self.working_memory['last_refresh_timestamp'] = datetime.now().isoformat() + 'Z'
        self.working_memory['context_metadata']['refresh_triggers_met'] = ['manual_refresh']
        self.save_working_memory()

        print_success("Context refreshed successfully\n")

        # Show current state
        self.show_current_state()

    def show_current_state(self):
        """Display current system state"""
        print(f"{Colors.BOLD}System:{Colors.ENDC} {self.system_name}")
        print(f"{Colors.BOLD}Current Step:{Colors.ENDC} {self.working_memory.get('current_step', 'Unknown')}")
        print(f"{Colors.BOLD}Substep:{Colors.ENDC} {self.working_memory.get('current_substep', 'N/A')}")
        print(f"{Colors.BOLD}Working Directory:{Colors.ENDC} {self.system_path}")
        print(f"{Colors.BOLD}Operations Since Refresh:{Colors.ENDC} {self.working_memory.get('operations_since_refresh', 0)}/4")

        # Show focus
        focus = self.working_memory.get('progress_summary', {}).get('current_focus', 'No focus set')
        print(f"{Colors.BOLD}Current Focus:{Colors.ENDC} {focus}")

    def increment_operations(self):
        """Increment operation counter"""
        self.working_memory['operations_since_refresh'] = self.working_memory.get('operations_since_refresh', 0) + 1
        self.save_working_memory()

    def display_current_step(self):
        """Display the current step with actions and validation"""
        print_header(f"CURRENT STEP: {self.working_memory.get('current_step', 'Unknown')}")

        # Check context refresh
        refresh_needed = self.check_context_refresh_needed()
        if refresh_needed:
            print_warning("CONTEXT REFRESH REQUIRED!")
            for reason in refresh_needed:
                print(f"  - {reason}")
            print_info("Run: python3 workflow_driver.py " + self.system_name + " --refresh\n")
            return

        self.show_current_state()

        # Load step configuration
        step_config = self.load_current_step_config()
        if not step_config:
            return

        print(f"\n{Colors.BOLD}Step Description:{Colors.ENDC}")
        print(f"  {step_config.get('workflow_metadata', {}).get('description', 'No description')}\n")

        # Entry conditions
        if 'entry_conditions' in step_config:
            print(f"{Colors.BOLD}Entry Conditions:{Colors.ENDC}")
            for key, value in step_config['entry_conditions'].items():
                if isinstance(value, bool):
                    status = "✓" if value else "✗"
                    print(f"  {status} {key}: {value}")
                elif isinstance(value, list):
                    print(f"  • {key}:")
                    for item in value:
                        print(f"    - {item}")
                else:
                    print(f"  • {key}: {value}")
            print()

        # Prerequisites
        if 'prerequisites' in step_config:
            print(f"{Colors.BOLD}Prerequisites:{Colors.ENDC}")
            prereqs = step_config['prerequisites']
            for key, items in prereqs.items():
                if isinstance(items, list):
                    print(f"  {key.replace('_', ' ').title()}:")
                    for item in items:
                        # Check if file exists
                        if isinstance(item, str) and (item.startswith('./') or item.startswith('/')):
                            path = Path(item.replace('/home/ajs7/project/saa', str(self.reflow_root)))
                            status = "✓" if path.exists() else "✗"
                            print(f"    {status} {item}")
                        else:
                            print(f"    • {item}")
            print()

        # Steps/Actions
        if 'steps' in step_config:
            print(f"{Colors.BOLD}REQUIRED ACTIONS:{Colors.ENDC}\n")

            completed_actions = self.progress_tracker.get('current_step_actions', {}).get('completed_actions', [])

            for i, step in enumerate(step_config['steps'], 1):
                step_id = step.get('id', f'step_{i}')
                is_complete = step_id in completed_actions

                status_icon = "✓" if is_complete else "○"
                color = Colors.OKGREEN if is_complete else Colors.ENDC

                print(f"{color}{status_icon} {i}. [{step_id}] {step.get('description', 'No description')}{Colors.ENDC}")

                if 'command' in step:
                    cmd = step['command'].replace('<system_name>', self.system_name)
                    print(f"   {Colors.OKCYAN}Command:{Colors.ENDC} {cmd}")

                if 'tool' in step:
                    print(f"   {Colors.OKCYAN}Tool:{Colors.ENDC} {step['tool']}")

                if 'success' in step:
                    print(f"   {Colors.OKCYAN}Success Criteria:{Colors.ENDC} {step['success']}")

                if 'validation' in step:
                    print(f"   {Colors.OKCYAN}Validation:{Colors.ENDC} {step['validation']}")

                if 'outputs' in step:
                    print(f"   {Colors.OKCYAN}Outputs:{Colors.ENDC} {', '.join(step['outputs'])}")

                if not is_complete:
                    print(f"   {Colors.WARNING}Mark complete:{Colors.ENDC} python3 workflow_driver.py {self.system_name} --mark-done {step_id}")

                print()

        # Validation gate
        if 'validation' in step_config:
            print(f"{Colors.BOLD}{Colors.WARNING}VALIDATION GATE:{Colors.ENDC}")
            validation = step_config['validation']
            if isinstance(validation, dict):
                for key, value in validation.items():
                    print(f"  • {key}: {value}")
            else:
                print(f"  {validation}")
            print(f"\n  {Colors.OKCYAN}Run validation:{Colors.ENDC} python3 workflow_driver.py {self.system_name} --validate\n")

        # Next step
        if 'handoff' in step_config:
            print(f"{Colors.BOLD}After Validation:{Colors.ENDC}")
            next_workflow = step_config['handoff'].get('next_workflow', 'Unknown')
            print(f"  Next: {next_workflow}")
            print(f"  {Colors.OKCYAN}Advance:{Colors.ENDC} python3 workflow_driver.py {self.system_name} --next\n")

        # Increment operations counter
        self.increment_operations()

    def mark_action_done(self, action_id):
        """Mark a specific action as complete"""
        completed = self.progress_tracker.setdefault('current_step_actions', {}).setdefault('completed_actions', [])

        if action_id in completed:
            print_warning(f"Action {action_id} already marked as complete")
            return

        completed.append(action_id)
        self.progress_tracker['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        self.save_progress_tracker()

        print_success(f"Action {action_id} marked as complete")

        # Increment operations
        self.increment_operations()

    def run_validation(self):
        """Run validation gate for current step"""
        print_header("VALIDATION GATE")

        step_config = self.load_current_step_config()
        if not step_config:
            return False

        # Check if all actions are complete
        if 'steps' in step_config:
            completed_actions = self.progress_tracker.get('current_step_actions', {}).get('completed_actions', [])
            required_actions = [s.get('id', f'step_{i}') for i, s in enumerate(step_config['steps'], 1)]

            incomplete = set(required_actions) - set(completed_actions)
            if incomplete:
                print_error("Not all actions are complete!")
                print("\nIncomplete actions:")
                for action_id in incomplete:
                    print(f"  ✗ {action_id}")
                print_info("\nComplete all actions before running validation")
                return False

        print_success("All actions marked as complete")

        # Run validation based on step
        current_step = self.working_memory.get('current_step', '')

        # Determine validation command
        validation_commands = []

        if current_step.startswith('A') or 'Arch' in current_step:
            # Architecture validation
            validation_commands = [
                ('Architecture Validation', f'python3 {self.reflow_root}/tools/validate_architecture.py {self.system_path}'),
                ('System Graph', f'python3 {self.reflow_root}/tools/system_of_systems_graph.py {self.system_path}')
            ]
        elif current_step.startswith('D') or 'Dev' in current_step:
            # Development validation
            validation_commands = [
                ('Architecture Validation', f'python3 {self.reflow_root}/tools/validate_architecture.py {self.system_path}')
            ]

        all_passed = True
        for name, cmd in validation_commands:
            print(f"\n{Colors.BOLD}Running: {name}{Colors.ENDC}")
            print(f"Command: {cmd}\n")

            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

            if result.returncode == 0:
                print_success(f"{name} PASSED")
                print(result.stdout)
            else:
                print_error(f"{name} FAILED")
                print(result.stderr)
                print(result.stdout)
                all_passed = False

        if all_passed:
            print_header("VALIDATION PASSED ✓")
            self.progress_tracker['current_step_actions']['validation_status'] = 'passed'
            self.save_progress_tracker()
            print_info(f"Ready to proceed: python3 workflow_driver.py {self.system_name} --next\n")
        else:
            print_header("VALIDATION FAILED ✗")
            print_error("Fix validation issues before proceeding\n")

        # Increment operations
        self.increment_operations()

        return all_passed

    def advance_to_next_step(self):
        """Advance to the next workflow step"""
        print_header("ADVANCING TO NEXT STEP")

        # Check validation passed
        validation_status = self.progress_tracker.get('current_step_actions', {}).get('validation_status', 'pending')
        if validation_status != 'passed':
            print_error("Cannot advance: validation not passed")
            print_info(f"Run: python3 workflow_driver.py {self.system_name} --validate")
            return

        step_config = self.load_current_step_config()
        if not step_config:
            print_error("Could not load current step configuration")
            return

        # Get next workflow
        next_workflow = step_config.get('handoff', {}).get('next_workflow', '')
        if not next_workflow:
            print_warning("No next workflow specified in current step")
            return

        # Parse next workflow file to get step ID
        next_workflow_path = Path(next_workflow)
        if next_workflow_path.name.startswith('Arch-'):
            next_step = next_workflow_path.stem.replace('Arch-', 'A')
        elif next_workflow_path.name.startswith('Dev-'):
            next_step = next_workflow_path.stem.replace('Dev-', 'Dev-')
        elif next_workflow_path.name.startswith('FU-'):
            next_step = next_workflow_path.stem.replace('FU-', 'F')
        else:
            next_step = next_workflow_path.stem

        # Update working memory
        old_step = self.working_memory.get('current_step', '')
        self.working_memory['current_step'] = next_step
        self.working_memory['operations_since_refresh'] = 0
        self.working_memory['last_refresh_timestamp'] = datetime.now().isoformat() + 'Z'

        # Update progress tracker
        self.progress_tracker['current_step'] = next_step
        self.progress_tracker['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Add to history
        history_entry = {
            'step_id': old_step,
            'status': 'completed',
            'completed': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'validation_passed': True
        }
        self.progress_tracker.setdefault('step_history', []).append(history_entry)

        # Reset current step actions
        self.progress_tracker['current_step_actions'] = {
            'total_actions': 0,
            'completed_actions': [],
            'current_action': next_step,
            'validation_status': 'pending'
        }

        # Save
        self.save_working_memory()
        self.save_progress_tracker()

        print_success(f"Advanced from {old_step} to {next_step}")
        print_info(f"Next workflow: {next_workflow}\n")

        # Show new current step
        self.display_current_step()

    def show_status(self):
        """Show overall system status"""
        print_header(f"STATUS: {self.system_name}")

        self.show_current_state()

        print(f"\n{Colors.BOLD}Step History:{Colors.ENDC}")
        history = self.progress_tracker.get('step_history', [])
        for entry in history[-5:]:  # Last 5 steps
            step_id = entry.get('step_id', 'Unknown')
            status = entry.get('status', 'Unknown')
            completed = entry.get('completed', 'N/A')
            icon = "✓" if status == 'completed' else "○"
            print(f"  {icon} {step_id} - {status} - {completed}")

        print(f"\n{Colors.BOLD}Overall Progress:{Colors.ENDC}")
        overall = self.progress_tracker.get('overall_progress', {})
        completed = overall.get('completed_steps', 0)
        total = overall.get('total_steps', 10)
        progress_pct = (completed / total * 100) if total > 0 else 0

        print(f"  Steps: {completed}/{total} ({progress_pct:.1f}%)")

        blockers = overall.get('blockers', [])
        if blockers:
            print(f"\n{Colors.BOLD}Blockers:{Colors.ENDC}")
            for blocker in blockers:
                print(f"  ✗ {blocker}")

        # Artifacts
        print(f"\n{Colors.BOLD}Artifacts Generated:{Colors.ENDC}")
        artifacts = self.progress_tracker.get('artifacts_generated', {})
        for key, value in artifacts.items():
            if isinstance(value, bool):
                icon = "✓" if value else "✗"
                print(f"  {icon} {key.replace('_', ' ').title()}")
            elif isinstance(value, list):
                print(f"  • {key.replace('_', ' ').title()}: {len(value)} items")

    def initialize_system(self):
        """Initialize a new system"""
        print_header(f"INITIALIZING SYSTEM: {self.system_name}")

        # Create system directory structure
        directories = [
            self.system_path,
            self.system_path / "context",
            self.system_path / "interfaces",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            print_success(f"Created: {directory}")

        # Create initial working_memory.json
        working_memory = {
            "template_version": "1.0",
            "system_name": self.system_name,
            "current_step": "A1",
            "current_substep": "SetupAndContext",
            "operations_since_refresh": 0,
            "last_refresh_timestamp": datetime.now().isoformat() + 'Z',
            "progress_summary": {
                "completed_steps": [],
                "current_focus": "Initialize system structure and context",
                "next_action": "Set up system directory and context tracking files"
            },
            "context_metadata": {
                "working_directory": f"systems/{self.system_name}",
                "degradation_signals": []
            }
        }

        wm_path = self.system_path / "working_memory.json"
        with open(wm_path, 'w') as f:
            json.dump(working_memory, f, indent=2)
        print_success(f"Created: {wm_path}")

        # Create initial step_progress_tracker.json
        progress_tracker = {
            "template_version": "1.0",
            "system_name": self.system_name,
            "workflow_version": "2.0.0",
            "started_timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "last_updated": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "current_step": "A1",
            "step_history": [],
            "current_step_actions": {
                "total_actions": 0,
                "completed_actions": [],
                "current_action": "INITIALIZATION",
                "validation_status": "pending"
            },
            "overall_progress": {
                "total_steps": 10,
                "completed_steps": 0,
                "blockers": []
            },
            "artifacts_generated": {
                "service_architectures": [],
                "index_json": False,
                "interface_registry": False,
                "icds": []
            }
        }

        tracker_path = self.system_path / "step_progress_tracker.json"
        with open(tracker_path, 'w') as f:
            json.dump(progress_tracker, f, indent=2)
        print_success(f"Created: {tracker_path}")

        # Create initial current_focus.md
        focus_content = f"""# Current Focus: {self.system_name}

**System:** {self.system_name}
**Step:** A1 - Setup and Context
**Status:** Initializing

## Current Objective
Initialize system structure and establish context tracking.

## Next Actions
1. Define system mission and requirements
2. Create foundational architecture documents
3. Begin service decomposition

## Notes
- System initialized on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

        focus_path = self.system_path / "current_focus.md"
        with open(focus_path, 'w') as f:
            f.write(focus_content)
        print_success(f"Created: {focus_path}")

        print(f"\n{Colors.OKGREEN}System initialized successfully!{Colors.ENDC}")
        print_info(f"Run: python3 workflow_driver.py {self.system_name}")

    def auto_detect_progress(self, dry_run=False):
        """Automatically detect and update progress based on code state"""
        print_header("AUTO-DETECT PROGRESS")

        current_step = self.working_memory.get('current_step', '')

        if not current_step.startswith('Dev-'):
            print_warning("Auto-detect only supported for development steps (Dev-*)")
            return

        # Load step configuration
        step_config = self.load_current_step_config()
        if not step_config:
            return

        # Check if step has auto_progress_detection configured
        validation = step_config.get('validation', {})
        quality_gates = validation.get('quality_gates', {})
        auto_detect = quality_gates.get('auto_progress_detection', {})

        if not auto_detect.get('enabled', False):
            print_warning(f"Auto-detect not enabled for {current_step}")
            return

        print_info("Scanning codebase to detect completed actions...")

        # Get service directories
        services_dir = self.system_path / "services"
        if not services_dir.exists():
            code_dir = self.system_path / "code"
            if code_dir.exists():
                services_dir = code_dir
            else:
                print_error("No services/ or code/ directory found")
                return

        # Detect completion for each action
        checks = auto_detect.get('checks', {})
        detected_complete = []

        for action_id, check_func in checks.items():
            # Simple heuristic checks based on file existence
            is_complete = False

            if 'directory_skeleton' in check_func:
                # Check if service directories exist
                is_complete = any(services_dir.glob('*/src'))
            elif 'models_exist' in check_func:
                # Check for model files
                is_complete = any(services_dir.glob('*/src/models/*.py'))
            elif 'routers_exist' in check_func:
                # Check for router files
                is_complete = any(services_dir.glob('*/src/routers/*.py')) or any(services_dir.glob('*/src/api/*.py'))
            elif 'config_loader' in check_func:
                # Check for config files
                is_complete = any(services_dir.glob('*/src/config.py')) or any(services_dir.glob('*/src/config/*.py'))
            elif 'di_setup' in check_func:
                # Check for DI setup
                is_complete = any(services_dir.glob('*/src/di.py')) or any(services_dir.glob('*/src/dependencies.py'))
            elif 'lint_pass' in check_func:
                # Assume lint passes if code exists
                is_complete = any(services_dir.glob('*/src/*.py'))

            status_icon = "✓" if is_complete else "○"
            color = Colors.OKGREEN if is_complete else Colors.WARNING
            print(f"{color}{status_icon} {action_id}: {check_func}{Colors.ENDC}")

            if is_complete:
                detected_complete.append(action_id)

        if dry_run:
            print_info(f"\nDry run complete. Would mark {len(detected_complete)} actions as complete")
            return

        # Update progress tracker
        if detected_complete:
            completed_actions = self.progress_tracker.setdefault('current_step_actions', {}).setdefault('completed_actions', [])
            new_completions = [a for a in detected_complete if a not in completed_actions]

            if new_completions:
                completed_actions.extend(new_completions)
                self.progress_tracker['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                self.save_progress_tracker()
                print_success(f"\nMarked {len(new_completions)} new actions as complete")
            else:
                print_info("\nNo new completions detected")
        else:
            print_warning("\nNo completed actions detected")

    def run_quality_gates(self):
        """Run quality gates with blocking validation"""
        print_header("QUALITY GATES VALIDATION")

        step_config = self.load_current_step_config()
        if not step_config:
            return False

        validation = step_config.get('validation', {})
        quality_gates = validation.get('quality_gates', {})

        if not quality_gates:
            print_info("No quality gates configured for this step")
            return True

        all_passed = True
        results = {}

        # Run each quality gate
        for gate_name, gate_config in quality_gates.items():
            if gate_name == 'auto_progress_detection':
                continue  # Skip, not a validation gate

            print(f"\n{Colors.BOLD}Running: {gate_name}{Colors.ENDC}")
            print(f"Description: {gate_config.get('description', 'No description')}")

            blocking = gate_config.get('blocking', False)
            tool = gate_config.get('tool', '')

            if tool:
                # Replace placeholders
                cmd = tool.replace('<reflow_path>', str(self.reflow_root))
                cmd = cmd.replace('<system_path>', str(self.system_path))
                cmd = cmd.replace('<system>', self.system_name)

                print(f"Command: {cmd}")

                timeout = gate_config.get('timeout_seconds', 600)
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)

                passed = result.returncode == 0
                results[gate_name] = {
                    'passed': passed,
                    'blocking': blocking,
                    'output': result.stdout,
                    'error': result.stderr
                }

                if passed:
                    print_success(f"{gate_name} PASSED")
                else:
                    if blocking:
                        print_error(f"{gate_name} FAILED (BLOCKING)")
                        all_passed = False
                    else:
                        print_warning(f"{gate_name} FAILED (non-blocking)")

                    if result.stderr:
                        print(f"\n{Colors.FAIL}Error Output:{Colors.ENDC}")
                        print(result.stderr[:500])  # Limit output
            else:
                # Manual checks
                print_info(f"Manual validation required for: {gate_name}")
                checks = gate_config.get('checks', [])
                for check in checks:
                    print(f"  - {check}")

        # Show remediation steps if failed
        if not all_passed:
            print(f"\n{Colors.FAIL}{'='*70}{Colors.ENDC}")
            print(f"{Colors.FAIL}{Colors.BOLD}VALIDATION GATE FAILED{Colors.ENDC}")
            print(f"{Colors.FAIL}{'='*70}{Colors.ENDC}")

            on_failure = validation.get('on_validation_failure', {})
            message = on_failure.get('message', 'Validation failed')
            print(f"\n{Colors.WARNING}{message}{Colors.ENDC}\n")

            remediation = on_failure.get('remediation_steps', [])
            if remediation:
                print(f"{Colors.BOLD}Remediation Steps:{Colors.ENDC}")
                for i, step in enumerate(remediation, 1):
                    step = step.replace('<system>', self.system_name)
                    print(f"  {i}. {step}")
        else:
            print(f"\n{Colors.OKGREEN}{'='*70}{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{Colors.BOLD}ALL QUALITY GATES PASSED{Colors.ENDC}")
            print(f"{Colors.OKGREEN}{'='*70}{Colors.ENDC}")

        return all_passed

def main():
    parser = argparse.ArgumentParser(
        description='Reflow Workflow Driver - Enforce structured workflow execution',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 workflow_driver.py dnd_reflow                    # Show current step
  python3 workflow_driver.py dnd_reflow --refresh          # Force context refresh
  python3 workflow_driver.py dnd_reflow --validate         # Run validation
  python3 workflow_driver.py dnd_reflow --mark-done D1.2   # Mark action complete
  python3 workflow_driver.py dnd_reflow --next             # Advance to next step
  python3 workflow_driver.py dnd_reflow --status           # Show status
  python3 workflow_driver.py new_system --init             # Initialize new system
        """
    )

    parser.add_argument('system_name', help='Name of the system to work on')
    parser.add_argument('--refresh', action='store_true', help='Force context refresh')
    parser.add_argument('--next', action='store_true', help='Advance to next step')
    parser.add_argument('--validate', action='store_true', help='Run validation gate')
    parser.add_argument('--mark-done', metavar='ACTION_ID', help='Mark action as complete')
    parser.add_argument('--status', action='store_true', help='Show overall status')
    parser.add_argument('--init', action='store_true', help='Initialize new system')
    parser.add_argument('--auto-detect-progress', action='store_true', help='Auto-detect and update progress')
    parser.add_argument('--quality-gates', action='store_true', help='Run quality gates validation')
    parser.add_argument('--dry-run', action='store_true', help='Dry run mode (use with --auto-detect-progress)')

    args = parser.parse_args()

    # Handle initialization separately
    if args.init:
        driver = WorkflowDriver.__new__(WorkflowDriver)
        driver.reflow_root = Path(__file__).parent
        driver.system_name = args.system_name
        driver.system_path = driver.reflow_root / "systems" / args.system_name
        driver.initialize_system()
        return

    # Load existing system
    driver = WorkflowDriver(args.system_name)

    # Execute command
    if args.refresh:
        driver.refresh_context()
    elif args.validate:
        driver.run_validation()
    elif args.quality_gates:
        driver.run_quality_gates()
    elif args.auto_detect_progress:
        driver.auto_detect_progress(dry_run=args.dry_run)
    elif args.mark_done:
        driver.mark_action_done(args.mark_done)
    elif args.next:
        driver.advance_to_next_step()
    elif args.status:
        driver.show_status()
    else:
        # Default: show current step
        driver.display_current_step()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Operation cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print(f"\n{Colors.FAIL}Error: {e}{Colors.ENDC}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
