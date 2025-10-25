#!/usr/bin/env python3
"""
Workflow Files Validator

Validates workflow JSON files for:
- JSON syntax correctness
- Required fields presence
- Step ID uniqueness
- Valid step references (next_step points to existing step)
- Valid tool references (tools_used point to existing tools)
- Valid template references (templates_used point to existing templates)

Usage:
    python3 validate_workflow_files.py /path/to/reflow/workflows/
    python3 validate_workflow_files.py /path/to/reflow/workflows/01-systems_engineering.json
"""

import os
import json
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set

class WorkflowValidator:
    def __init__(self, reflow_root: str):
        self.reflow_root = Path(reflow_root)
        self.workflows_dir = self.reflow_root / "workflows"
        self.tools_dir = self.reflow_root / "tools"
        self.templates_dir = self.reflow_root / "templates"
        self.errors = []
        self.warnings = []

    def validate_all_workflows(self) -> bool:
        """Validate all workflow JSON files in workflows directory."""
        print(f"Validating workflows in: {self.workflows_dir}")
        print("=" * 70)

        workflow_files = list(self.workflows_dir.glob("*.json"))
        if not workflow_files:
            print(f"ERROR: No workflow files found in {self.workflows_dir}")
            return False

        all_valid = True
        for workflow_file in sorted(workflow_files):
            print(f"\n📄 Validating: {workflow_file.name}")
            if not self.validate_workflow_file(workflow_file):
                all_valid = False

        return all_valid

    def validate_workflow_file(self, file_path: Path) -> bool:
        """Validate a single workflow JSON file."""
        file_errors = []
        file_warnings = []

        # Check 1: JSON syntax
        try:
            with open(file_path) as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"  ✗ JSON SYNTAX ERROR: {e.msg} at line {e.lineno}, col {e.colno}"
            file_errors.append(error_msg)
            print(error_msg)
            return False
        except Exception as e:
            error_msg = f"  ✗ FILE ERROR: {e}"
            file_errors.append(error_msg)
            print(error_msg)
            return False

        print("  ✓ JSON syntax valid")

        # Check 2: Required top-level fields
        required_fields = ["workflow_metadata", "workflow_steps", "completion"]
        missing_fields = [f for f in required_fields if f not in data]
        if missing_fields:
            for field in missing_fields:
                error_msg = f"  ✗ Missing required field: {field}"
                file_errors.append(error_msg)
                print(error_msg)
        else:
            print("  ✓ Required top-level fields present")

        # Check 3: workflow_metadata required fields
        if "workflow_metadata" in data:
            metadata_required = ["workflow_id", "name", "version", "description"]
            metadata_missing = [f for f in metadata_required if f not in data["workflow_metadata"]]
            if metadata_missing:
                for field in metadata_missing:
                    error_msg = f"  ✗ Missing workflow_metadata field: {field}"
                    file_errors.append(error_msg)
                    print(error_msg)
            else:
                print("  ✓ workflow_metadata fields valid")

        # Check 4: Step ID uniqueness
        if "workflow_steps" in data and isinstance(data["workflow_steps"], list):
            step_ids = [step.get("step_id") for step in data["workflow_steps"] if "step_id" in step]
            duplicates = {sid for sid in step_ids if step_ids.count(sid) > 1}
            if duplicates:
                for sid in duplicates:
                    error_msg = f"  ✗ Duplicate step_id: {sid}"
                    file_errors.append(error_msg)
                    print(error_msg)
            else:
                print(f"  ✓ Step IDs unique ({len(step_ids)} steps)")

            # Check 5: Valid next_step references
            valid_step_ids = set(step_ids)
            for step in data["workflow_steps"]:
                next_step = step.get("next_step")
                if next_step and next_step != "complete" and next_step not in valid_step_ids:
                    error_msg = f"  ✗ Invalid next_step reference: {step.get('step_id')} → {next_step} (step does not exist)"
                    file_errors.append(error_msg)
                    print(error_msg)

            if not file_errors:  # Only print this if no next_step errors
                print("  ✓ Step references valid")

            # Check 6: Valid tool references
            for step in data["workflow_steps"]:
                tools_used = step.get("tools_used", [])
                for tool in tools_used:
                    tool_path = self.tools_dir / tool
                    if not tool_path.exists():
                        warning_msg = f"  ⚠ Tool not found: {tool} (referenced by {step.get('step_id')})"
                        file_warnings.append(warning_msg)
                        print(warning_msg)

            # Check 7: Valid template references
            for step in data["workflow_steps"]:
                templates_used = step.get("templates_used", [])
                for template in templates_used:
                    template_path = self.templates_dir / template
                    if not template_path.exists():
                        warning_msg = f"  ⚠ Template not found: {template} (referenced by {step.get('step_id')})"
                        file_warnings.append(warning_msg)
                        print(warning_msg)

            # Check 8: Required step fields
            for step in data["workflow_steps"]:
                step_required = ["step_id", "name", "description", "phase"]
                step_missing = [f for f in step_required if f not in step]
                if step_missing:
                    for field in step_missing:
                        warning_msg = f"  ⚠ Step {step.get('step_id', 'UNKNOWN')} missing field: {field}"
                        file_warnings.append(warning_msg)
                        print(warning_msg)

        # Summary
        has_errors = len(file_errors) > 0
        if not has_errors and len(file_warnings) == 0:
            print(f"  ✅ {file_path.name} is VALID")
        elif not has_errors:
            print(f"  ✅ {file_path.name} is valid (with {len(file_warnings)} warnings)")
        else:
            print(f"  ❌ {file_path.name} is INVALID ({len(file_errors)} errors, {len(file_warnings)} warnings)")

        self.errors.extend(file_errors)
        self.warnings.extend(file_warnings)

        return not has_errors

    def print_summary(self):
        """Print validation summary."""
        print("\n" + "=" * 70)
        print("VALIDATION SUMMARY")
        print("=" * 70)
        print(f"Total Errors: {len(self.errors)}")
        print(f"Total Warnings: {len(self.warnings)}")

        if len(self.errors) == 0 and len(self.warnings) == 0:
            print("\n✅ All workflow files are valid!")
            return True
        elif len(self.errors) == 0:
            print(f"\n✅ All workflow files are valid (with {len(self.warnings)} warnings)")
            return True
        else:
            print(f"\n❌ Workflow files have {len(self.errors)} errors")
            return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 validate_workflow_files.py <workflow_file_or_directory>")
        print("\nExamples:")
        print("  python3 validate_workflow_files.py /path/to/reflow/workflows/")
        print("  python3 validate_workflow_files.py /path/to/reflow/workflows/01-systems_engineering.json")
        sys.exit(1)

    target = Path(sys.argv[1])

    # Determine reflow_root
    if target.is_dir() and target.name == "workflows":
        reflow_root = target.parent
    elif target.is_file() and target.parent.name == "workflows":
        reflow_root = target.parent.parent
    else:
        # Assume target is within reflow, walk up to find reflow root
        current = target
        while current != current.parent:
            if (current / "workflows").exists() and (current / "tools").exists():
                reflow_root = current
                break
            current = current.parent
        else:
            print(f"ERROR: Could not determine reflow_root from {target}")
            print("Make sure you're running this from within a reflow directory structure")
            sys.exit(1)

    validator = WorkflowValidator(reflow_root)

    # Validate
    if target.is_dir():
        valid = validator.validate_all_workflows()
    elif target.is_file():
        valid = validator.validate_workflow_file(target)
    else:
        print(f"ERROR: {target} is not a file or directory")
        sys.exit(1)

    # Summary
    success = validator.print_summary()

    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
