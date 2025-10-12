#!/usr/bin/env python3
"""Bootstrap development context for a system post-architecture workflow.

Creates:
  - dev_working_memory.json
  - dev_progress_tracker.json
  - dev_current_focus.md
  - dev_process_log.md (if absent)
  - dev_context_checkpoint.md (initial checkpoint)

Usage:
  python3 tools/bootstrap_development_context.py <system_name>

Prerequisites:
  systems/<system_name>/build_ready_index.json must exist

Idempotent: Will not overwrite existing files unless --force passed.
"""
import sys
import json
import shutil
import datetime as dt
from pathlib import Path
import argparse

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = ROOT / 'templates'
SYSTEMS = ROOT / 'systems'

TEMPLATE_FILES = {
    'dev_working_memory.json': TEMPLATES / 'dev_working_memory_template.json',
    'dev_progress_tracker.json': TEMPLATES / 'dev_progress_tracker_template.json',
    'dev_current_focus.md': TEMPLATES / 'dev_current_focus_template.md'
}

PROCESS_LOG_HEADER = """# Development Process Log\n\nInitialized: {ts}\n\n| Timestamp | Event | Details |\n|-----------|-------|---------|\n"""

CHECKPOINT_TEMPLATE = """# Context Checkpoint (Initial)\nGenerated: {ts}\n\n## Active Service\nNone selected yet (awaiting initialization)\n\n## Stage & Subtasks Remaining\nStage: D1 - All subtasks pending\n\n## Recently Completed Actions\n- Initialization bootstrap executed\n\n## Blocking Issues / Risks\n- None\n\n## Evidence Artifacts Added\n- None\n"""

def load_build_ready(system_dir: Path):
    br = system_dir / 'build_ready_index.json'
    if not br.exists():
        raise SystemExit(f"ERROR: {br} not found. Ensure architecture workflow completion first.")
    try:
        return json.loads(br.read_text())
    except Exception as e:
        raise SystemExit(f"ERROR: Failed to parse build_ready_index.json: {e}")


def derive_services(build_ready_index: dict):
    # Expect a key that lists services; fallback heuristics.
    for key in ('services', 'service_registry', 'components'):
        if key in build_ready_index and isinstance(build_ready_index[key], list):
            return build_ready_index[key]
    # Try to derive from artifacts map
    artifacts = build_ready_index.get('artifacts', {})
    service_names = []
    for name, meta in artifacts.items():
        if isinstance(meta, dict) and meta.get('type') == 'service':
            service_names.append(name)
    return sorted(set(service_names))


def write_if_missing(target: Path, content: str, force: bool):
    if target.exists() and not force:
        return False
    target.write_text(content)
    return True


def personalize_template(raw: str, system_name: str):
    ts = dt.datetime.utcnow().isoformat() + 'Z'
    return (raw
            .replace('<REPLACE_SYSTEM_NAME>', system_name)
            .replace('<SET_AT_INIT>', ts)
            .replace('<TIMESTAMP>', ts))


def init_files(system_name: str, force: bool = False):
    system_dir = SYSTEMS / system_name
    if not system_dir.exists():
        raise SystemExit(f"ERROR: System directory {system_dir} not found")

    build_ready = load_build_ready(system_dir)
    services = derive_services(build_ready)
    if not services:
        print("WARNING: No services discovered in build_ready_index.json; progress tracker will have zero services")

    # Copy & personalize templates
    for out_name, template_path in TEMPLATE_FILES.items():
        if not template_path.exists():
            raise SystemExit(f"ERROR: Missing template {template_path}")
        raw = template_path.read_text()
        content = personalize_template(raw, system_name)
        if out_name == 'dev_progress_tracker.json':
            # Replace example service block with actual services
            tracker = json.loads(content)
            tracker['services'] = {}
            for svc in services:
                tracker['services'][svc] = {
                    'stage': 'D1',
                    'last_updated': dt.datetime.utcnow().isoformat() + 'Z',
                    'quality_gates_passed': [],
                    'blocking_issues': [],
                    'evidence_refs': []
                }
            tracker['global_status']['total_services'] = len(services)
            content = json.dumps(tracker, indent=2)
        write_if_missing(system_dir / out_name, content, force)

    # Process log
    process_log = system_dir / 'dev_process_log.md'
    if write_if_missing(process_log, PROCESS_LOG_HEADER.format(ts=dt.datetime.utcnow().isoformat() + 'Z'), force):
        print(f"Created {process_log}")

    # Initial checkpoint
    checkpoint = system_dir / 'dev_context_checkpoint.md'
    if write_if_missing(checkpoint, CHECKPOINT_TEMPLATE.format(ts=dt.datetime.utcnow().isoformat() + 'Z'), force):
        print(f"Created {checkpoint}")

    # Working memory file may need separate creation if template missing fields
    wm_path = system_dir / 'dev_working_memory.json'
    if not wm_path.exists() or force:
        wm = {
            'system_name': system_name,
            'active_service': services[0] if services else None,
            'stage': 'D1',
            'operations_since_refresh': 0,
            'last_refresh_timestamp': dt.datetime.utcnow().isoformat() + 'Z',
            'pending_quality_gates': [],
            'open_blockers': [],
            'recent_actions': [],
            'next_action': 'Bootstrap environment for first service'
        }
        wm_path.write_text(json.dumps(wm, indent=2))
        print(f"Created {wm_path}")

    print("Bootstrap complete.")


def main():
    parser = argparse.ArgumentParser(description='Initialize development context for a system.')
    parser.add_argument('system_name', help='Name of the system directory under systems/')
    parser.add_argument('--force', action='store_true', help='Overwrite existing files')
    args = parser.parse_args()
    init_files(args.system_name, args.force)

if __name__ == '__main__':
    main()
