#!/usr/bin/env python3
"""
Development Workflow Bootstrap Tool
Creates and initializes development tracking files for service development workflow.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import argparse

# Adjust paths for reflow directory structure
REFLOW_ROOT = Path(__file__).parent.parent
TEMPLATES_PATH = REFLOW_ROOT / "templates"


def load_template(template_name):
    """Load a template file from the templates directory."""
    template_path = TEMPLATES_PATH / template_name
    if not template_path.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    if template_path.suffix == ".json":
        with open(template_path) as f:
            return json.load(f)
    else:
        with open(template_path) as f:
            return f.read()


def bootstrap_development_context(system_name, system_path):
    """Bootstrap development context for a system."""
    system_dir = Path(system_path)
    system_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().isoformat()
    created_files = []

    print(f"🔧 Bootstrapping development context for system: {system_name}")
    print(f"📁 System directory: {system_dir}")

    # Check for build_ready_index.json
    build_ready_path = system_dir / "build_ready_index.json"
    if not build_ready_path.exists():
        print(f"⚠️  Warning: build_ready_index.json not found at {build_ready_path}")
        print("   This file is required for development workflow entry")

    # Create dev_progress_tracker.json
    try:
        dev_tracker_template = load_template("dev_progress_tracker_template.json")
        dev_tracker_template["system_name"] = system_name
        dev_tracker_template["started_timestamp"] = timestamp
        dev_tracker_template["last_updated"] = timestamp

        dev_tracker_path = system_dir / "dev_progress_tracker.json"
        with open(dev_tracker_path, "w") as f:
            json.dump(dev_tracker_template, f, indent=2)
        created_files.append(dev_tracker_path)
        print(f"✅ Created: {dev_tracker_path}")
    except Exception as e:
        print(f"❌ Failed to create dev_progress_tracker.json: {e}")

    # Create dev_current_focus.md
    try:
        dev_focus_template = load_template("dev_current_focus_template.md")
        dev_focus_content = dev_focus_template.replace(
            "REPLACE_WITH_SYSTEM_NAME", system_name
        )
        dev_focus_content = dev_focus_content.replace(
            "YYYY-MM-DD HH:MM:SS", datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        dev_focus_content = dev_focus_content.replace("CURRENT_STAGE_ID", "D1")
        dev_focus_content = dev_focus_content.replace(
            "STAGE_NAME", "Initialization & Environment Bootstrap"
        )
        dev_focus_content = dev_focus_content.replace("CURRENT_SERVICE_ID", "TBD")
        dev_focus_content = dev_focus_content.replace(
            "DESCRIPTION_OF_NEXT_ACTION",
            "Parse build_ready_index.json and enumerate dependency layers",
        )
        dev_focus_content = dev_focus_content.replace(
            "DETAILED_DESCRIPTION_OF_CURRENT_TASK",
            "Establish reproducible development environment per service dependency groups",
        )

        dev_focus_path = system_dir / "dev_current_focus.md"
        with open(dev_focus_path, "w") as f:
            f.write(dev_focus_content)
        created_files.append(dev_focus_path)
        print(f"✅ Created: {dev_focus_path}")
    except Exception as e:
        print(f"❌ Failed to create dev_current_focus.md: {e}")

    # Create dev_working_memory.json
    try:
        dev_memory_template = load_template("dev_working_memory_template.json")
        dev_memory_template["system_name"] = system_name
        dev_memory_template["last_refresh_timestamp"] = timestamp
        dev_memory_template["next_action"] = (
            "Parse build_ready_index.json to enumerate dependency layers"
        )
        dev_memory_template["snapshot_management"][
            "last_snapshot_timestamp"
        ] = timestamp
        dev_memory_template["development_metrics"]["stage_start_time"] = timestamp

        dev_memory_path = system_dir / "dev_working_memory.json"
        with open(dev_memory_path, "w") as f:
            json.dump(dev_memory_template, f, indent=2)
        created_files.append(dev_memory_path)
        print(f"✅ Created: {dev_memory_path}")
    except Exception as e:
        print(f"❌ Failed to create dev_working_memory.json: {e}")

    # Create dev_process_log.md
    try:
        log_content = f"""# Development Process Log

**System:** {system_name}
**Started:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Bootstrap Entry
- Development context initialized
- Tracking files created
- Ready for Stage D1: Initialization & Environment Bootstrap

## Process Log
<!-- Log entries will be added here as development progresses -->

---
*This log tracks the development process for {system_name}. Each stage transition, quality gate, and significant decision should be recorded here.*
"""

        dev_log_path = system_dir / "dev_process_log.md"
        with open(dev_log_path, "w") as f:
            f.write(log_content)
        created_files.append(dev_log_path)
        print(f"✅ Created: {dev_log_path}")
    except Exception as e:
        print(f"❌ Failed to create dev_process_log.md: {e}")

    # Create dev_context_checkpoint.md
    try:
        checkpoint_content = f"""# Context Checkpoint

**System:** {system_name}
**Timestamp:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Stage:** D1 - Initialization & Environment Bootstrap

## Active Service
TBD (will be determined from build_ready_index.json)

## Stage & Subtasks Remaining
- [ ] D1.1: Parse build_ready_index.json to enumerate dependency layers
- [ ] D1.2: Create dev_progress_tracker.json with all services initial status=not_started
- [ ] D1.3: Initialize per-service dev_current_focus.md with first implementation target
- [ ] D1.4: Validate required runtimes, toolchains, and lint/test frameworks
- [ ] D1.5: Record environment baseline hashes/versions to dev_process_log.md
- [ ] D1.6: Create SYSTEM_MISSION_STATEMENT.md capturing the fundamental 'why' of the system
- [ ] D1.7: Create USER_SCENARIOS.md with realistic user stories and expected outcomes
- [ ] D1.8: Create SUCCESS_CRITERIA.md defining measurable mission success indicators

## Recently Completed Actions
- Bootstrap development context initialized
- Development tracking files created

## Blocking Issues / Risks
None identified at bootstrap

## Evidence Artifacts Added
- dev_progress_tracker.json
- dev_current_focus.md
- dev_working_memory.json
- dev_process_log.md
- dev_context_checkpoint.md (this file)
"""

        checkpoint_path = system_dir / "dev_context_checkpoint.md"
        with open(checkpoint_path, "w") as f:
            f.write(checkpoint_content)
        created_files.append(checkpoint_path)
        print(f"✅ Created: {checkpoint_path}")
    except Exception as e:
        print(f"❌ Failed to create dev_context_checkpoint.md: {e}")

    # Summary
    print(f"\n🎉 Bootstrap complete!")
    print(f"Created {len(created_files)} development tracking files:")
    for file_path in created_files:
        print(f"  - {file_path.name}")

    print(f"\n📋 Next steps:")
    print(f"1. Ensure build_ready_index.json exists in {system_dir}")
    print(f"2. Review and update dev_current_focus.md")
    print(f"3. Begin Stage D1: Initialization & Environment Bootstrap")
    print(f"4. Use development workflow for guided implementation")

    return created_files


def main():
    parser = argparse.ArgumentParser(
        description="Bootstrap development context for service development workflow"
    )
    parser.add_argument("system_name", help="Name of the system being developed")
    parser.add_argument(
        "--system-path",
        default=None,
        help="Path to system directory (default: systems/<system_name>)",
    )
    parser.add_argument(
        "--force", action="store_true", help="Overwrite existing files if they exist"
    )

    args = parser.parse_args()

    if args.system_path is None:
        # Default to systems/<system_name> relative to current directory
        args.system_path = f"systems/{args.system_name}"

    system_path = Path(args.system_path)

    # Check if files already exist
    existing_files = []
    tracking_files = [
        "dev_progress_tracker.json",
        "dev_current_focus.md",
        "dev_working_memory.json",
        "dev_process_log.md",
        "dev_context_checkpoint.md",
    ]

    for file_name in tracking_files:
        file_path = system_path / file_name
        if file_path.exists():
            existing_files.append(file_name)

    if existing_files and not args.force:
        print(f"❌ Error: The following files already exist in {system_path}:")
        for file_name in existing_files:
            print(f"  - {file_name}")
        print(f"\nUse --force to overwrite existing files")
        sys.exit(1)

    try:
        created_files = bootstrap_development_context(args.system_name, system_path)
        print(f"\n✅ Development context bootstrap successful!")
    except Exception as e:
        print(f"❌ Bootstrap failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
