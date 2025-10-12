#!/usr/bin/env python3
"""Natural language runner for service development workflow.

Functions:
  - Parse a natural language command (or explicit flags) to identify:
      * system name
      * service name (optional: operate on single service)
      * starting stage (default D1)
  - Ensure bootstrap has been performed (run bootstrap script if needed)
  - Load workflow spec (service_development_workflow.json)
  - Present next actionable steps with context refresh rules
  - Optionally execute 'dry-run' scaffolding actions (placeholder for future automation)

Usage:
  python3 tools/run_development_workflow.py "execute this process on system alpha"
  python3 tools/run_development_workflow.py --system alpha --stage D3 --service portfolio

NOTE: This script currently emits an action plan; it does not create code artifacts beyond bootstrap.
"""
import re
import json
import subprocess
import shlex
import sys
from pathlib import Path
import argparse
import datetime as dt

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW_FILE = ROOT / 'service_development_workflow.json'
BOOTSTRAP = ROOT / 'tools' / 'bootstrap_development_context.py'
SYSTEMS = ROOT / 'systems'

STAGE_ORDER = [f"D{i}" for i in range(1,13)] + ["POST", "continuous"]

NL_SYSTEM_PAT = re.compile(r"system\s+([A-Za-z0-9_-]+)")
NL_SERVICE_PAT = re.compile(r"service\s+([A-Za-z0-9_-]+)")
NL_STAGE_PAT = re.compile(r"stage\s+(D\d{1,2}|POST)", re.IGNORECASE)

class WorkflowError(Exception):
    pass

def parse_args():
    ap = argparse.ArgumentParser(description='Run development workflow (natural language or flags).')
    ap.add_argument('command', nargs='*', help='Natural language command')
    ap.add_argument('--system', help='Explicit system name')
    ap.add_argument('--service', help='Specific service to focus')
    ap.add_argument('--stage', help='Starting stage (D1..D12, POST)')
    ap.add_argument('--force-bootstrap', action='store_true', help='Force re-bootstrap context files')
    ap.add_argument('--dry-run', action='store_true', help='Do not modify files (except bootstrap)')
    return ap.parse_args()

def infer_from_nl(command: str):
    system = None
    service = None
    stage = None
    if m := NL_SYSTEM_PAT.search(command):
        system = m.group(1)
    if m := NL_SERVICE_PAT.search(command):
        service = m.group(1)
    if m := NL_STAGE_PAT.search(command):
        stage = m.group(1).upper()
    # Common phrases
    if 'execute this process on ' in command and not system:
        # try last token
        tail = command.strip().split()[-1]
        system = tail
    return system, service, stage

def load_workflow():
    if not WORKFLOW_FILE.exists():
        raise WorkflowError('Workflow spec not found')
    return json.loads(WORKFLOW_FILE.read_text())

def ensure_bootstrap(system: str, force: bool):
    system_dir = SYSTEMS / system
    if not system_dir.exists():
        raise WorkflowError(f'System directory {system_dir} not found')
    needed = [
        'dev_working_memory.json',
        'dev_progress_tracker.json',
        'dev_current_focus.md'
    ]
    missing = [n for n in needed if not (system_dir / n).exists()]
    if missing or force:
        cmd = [sys.executable, str(BOOTSTRAP), system]
        if force:
            cmd.append('--force')
        print(f"[bootstrap] Running: {' '.join(shlex.quote(c) for c in cmd)}")
        subprocess.run(cmd, check=True)
        print('[bootstrap] Completed')
    else:
        print('[bootstrap] Existing context detected; skipping (use --force-bootstrap to override)')


def compute_stage_plan(workflow: dict, start_stage: str, service: str | None):
    stages = workflow['development_stages']
    index = next((i for i,s in enumerate(stages) if s['stage_id'] == start_stage), None)
    if index is None:
        raise WorkflowError(f'Stage {start_stage} not found')
    return stages[index:]


def summarize_actions(stages, service: str | None):
    plan_lines = []
    for st in stages:
        sid = st['stage_id']
        plan_lines.append(f"Stage {sid} - {st['name']}: {st['description']}")
        for act in st.get('actions', []):
            scope = f"[service={service}]" if service else "[all services]"
            plan_lines.append(f"  - {sid}:{act['id']} {scope} -> {act['description']}")
        exit_crit = '; '.join(st.get('exit_criteria', []))
        if exit_crit:
            plan_lines.append(f"    Exit Criteria: {exit_crit}")
        if 'quality_gate' in st:
            plan_lines.append(f"    Quality Gate: {st['quality_gate']}")
        plan_lines.append("")
    return '\n'.join(plan_lines)


def update_focus(system: str, stage: str, next_action: str, service: str | None):
    path = SYSTEMS / system / 'dev_current_focus.md'
    ts = dt.datetime.utcnow().isoformat() + 'Z'
    lines = [
        f"# Development Current Focus",
        f"Updated: {ts}",
        "",
        "## IMMEDIATE NEXT ACTION",
        next_action,
        "",
        "## ACTIVE CONTEXT",
        f"- System: {system}",
        f"- Stage: {stage}",
        f"- Service: {service or 'ALL'}",
        "",
        "## NOTES",
        "Proceed per service_development_workflow.json; trigger context refresh after 6 ops or stage boundary.",
        ""
    ]
    path.write_text('\n'.join(lines))
    print(f"[focus] Updated {path}")


def main():
    args = parse_args()
    command_text = ' '.join(args.command) if args.command else ''
    system, service, stage = args.system, args.service, args.stage
    if command_text:
        si, sv, st = infer_from_nl(command_text)
        system = system or si
        service = service or sv
        stage = stage or st
    if not system:
        print('ERROR: Could not determine system name. Use --system <name>.')
        sys.exit(1)
    stage = stage or 'D1'
    try:
        workflow = load_workflow()
        ensure_bootstrap(system, args.force_bootstrap)
        stages = compute_stage_plan(workflow, stage, service)
        plan = summarize_actions(stages, service)
        # Pick first actionable step description
        first_action = 'Review stage actions' if not stages or not stages[0].get('actions') else stages[0]['actions'][0]['description']
        update_focus(system, stage, first_action, service)
        print('\n=== ACTION PLAN (dry-run)' if args.dry_run else '\n=== ACTION PLAN')
        print(plan)
        if args.dry_run:
            print('Dry-run mode: no further execution.')
        else:
            print('Execution mode currently limited to bootstrap + focus update (future automation TODO).')
    except WorkflowError as e:
        print(f'ERROR: {e}')
        sys.exit(1)

if __name__ == '__main__':
    main()
