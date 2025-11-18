#!/usr/bin/env python3
"""
Architecture Versioning Tool

Purpose: Version architecture changes with rationale, timestamp, and linkage to triggering events.
This tool supports iterative architecture synchronization by tracking WHY and WHEN architecture changed.

Usage:
    python3 version_architecture.py \\
        --system-root /path/to/system \\
        --change-type "performance_optimization" \\
        --rationale "Operational testing revealed 45s latency, redesigned for async" \\
        --similarity-score 0.62 \\
        --changed-files "service_architecture.json,functional_architecture.json" \\
        --triggered-by "TO-05 operational testing failure" \\
        [--test-evidence "specs/machine/ote_artifacts.json"]

Version: 1.0.0
Created: 2025-11-18
Part of: Reflow v3.15.0 - Architecture Synchronization Loop feature
"""

import argparse
import json
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Any

# Semantic versioning constants
MAJOR = 0
MINOR = 1
PATCH = 2


def load_json(file_path: Path) -> Dict[str, Any]:
    """Load JSON file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(file_path: Path, data: Dict[str, Any], indent: int = 2) -> None:
    """Save JSON file with proper formatting."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=indent, ensure_ascii=False)
        f.write('\n')


def parse_version(version_str: str) -> tuple:
    """Parse semantic version string 'v1.2.3' into (1, 2, 3)."""
    if version_str.startswith('v'):
        version_str = version_str[1:]
    parts = version_str.split('.')
    return tuple(int(p) for p in parts)


def format_version(version_tuple: tuple) -> str:
    """Format version tuple (1, 2, 3) into 'v1.2.3'."""
    return f"v{version_tuple[0]}.{version_tuple[1]}.{version_tuple[2]}"


def increment_version(current_version: str, change_type: str, breaking_changes: bool) -> str:
    """
    Increment semantic version based on change type.

    Rules:
    - Breaking changes (interface changes, service removal): increment MAJOR
    - Non-breaking additions (new endpoints, new services): increment MINOR
    - Internal changes (performance, refactoring): increment PATCH
    """
    major, minor, patch = parse_version(current_version)

    if breaking_changes:
        # Breaking change - increment major
        return format_version((major + 1, 0, 0))
    elif change_type in ['requirements_creep', 'security_hardening']:
        # Likely adds new functionality - increment minor
        return format_version((major, minor + 1, 0))
    else:
        # Internal optimization or fix - increment patch
        return format_version((major, minor, patch + 1))


def get_or_create_version_history(system_root: Path, system_name: str) -> tuple:
    """
    Get existing version history or create new one.

    Returns: (version_history_dict, version_history_path)
    """
    version_history_path = system_root / "specs" / "machine" / "architecture_version_history.json"

    if version_history_path.exists():
        version_history = load_json(version_history_path)
    else:
        # Create new version history
        version_history = {
            "system_name": system_name,
            "version_history": [],
            "current_version": "v0.0.0",
            "total_versions": 0
        }

    return version_history, version_history_path


def identify_changed_files(system_root: Path, changed_files_str: str) -> List[str]:
    """
    Identify which architecture files changed.

    Args:
        system_root: System root directory
        changed_files_str: Comma-separated list of changed files (can be relative or just names)

    Returns: List of full relative paths from system_root
    """
    changed_files = []
    specs_machine = system_root / "specs" / "machine"

    for file_name in changed_files_str.split(','):
        file_name = file_name.strip()

        # Try to find the file
        if '/' in file_name:
            # Relative path provided
            file_path = system_root / file_name
        else:
            # Just filename - search common locations
            search_paths = [
                specs_machine / file_name,
                specs_machine / "service_arch" / file_name,
                specs_machine / "functional" / file_name,
                specs_machine / "interfaces" / file_name,
                specs_machine / "graphs" / file_name
            ]

            file_path = None
            for search_path in search_paths:
                if search_path.exists():
                    file_path = search_path
                    break

            if file_path is None:
                print(f"WARNING: Could not find file {file_name}, skipping")
                continue

        if file_path.exists():
            # Store as relative path from system_root
            rel_path = file_path.relative_to(system_root)
            changed_files.append(str(rel_path))
        else:
            print(f"WARNING: File does not exist: {file_path}")

    return changed_files


def detect_breaking_changes(changed_files: List[str]) -> bool:
    """
    Detect if changes are breaking based on which files changed.

    Breaking changes:
    - Changes to interface contracts (*_icd.json)
    - Changes to interface_registry.json (interface additions/removals)
    - Service removals (would need deeper analysis, assume non-breaking for now)

    Returns: True if breaking changes detected
    """
    for file_path in changed_files:
        if '_icd.json' in file_path or 'interface_registry.json' in file_path:
            # Interface contract changes are potentially breaking
            # Note: This is conservative - some ICD changes are non-breaking (additions)
            # Future enhancement: Analyze actual ICD diff
            return True

    return False


def create_versioned_copies(system_root: Path, changed_files: List[str], new_version: str) -> None:
    """
    Create versioned copies of changed architecture files.

    Pattern: service_architecture.json → service_architecture_v1.2.3.json
    """
    for file_path_str in changed_files:
        file_path = system_root / file_path_str

        if not file_path.exists():
            print(f"WARNING: Cannot version file (does not exist): {file_path}")
            continue

        # Generate versioned filename
        file_stem = file_path.stem  # 'service_architecture'
        file_suffix = file_path.suffix  # '.json'
        versioned_name = f"{file_stem}_{new_version}{file_suffix}"
        versioned_path = file_path.parent / versioned_name

        # Copy to versioned file
        shutil.copy2(file_path, versioned_path)
        print(f"✓ Created versioned copy: {versioned_path.relative_to(system_root)}")


def update_symlinks(system_root: Path, changed_files: List[str], new_version: str) -> None:
    """
    Update symlinks to point to latest versioned files.

    Pattern: service_architecture.json → service_architecture_v1.2.3.json (latest)

    Note: On Windows, this creates a copy instead of symlink if symlinks not supported.
    """
    for file_path_str in changed_files:
        file_path = system_root / file_path_str

        if not file_path.exists():
            continue

        file_stem = file_path.stem
        file_suffix = file_path.suffix
        versioned_name = f"{file_stem}_{new_version}{file_suffix}"
        versioned_path = file_path.parent / versioned_name

        # Remove existing symlink/file (will recreate)
        # Note: Current files become versioned copies, no need to delete

        # Create symlink (or copy on Windows)
        try:
            # Check if symlinks are supported
            if hasattr(os, 'symlink'):
                # Create relative symlink
                if file_path.is_symlink():
                    file_path.unlink()
                else:
                    # First time versioning - original file becomes v{new_version}
                    # This was already done in create_versioned_copies
                    pass

                # Symlink: service_architecture.json → service_architecture_v1.2.3.json
                os.symlink(versioned_name, file_path)
                print(f"✓ Updated symlink: {file_path.name} → {versioned_name}")
            else:
                # Windows fallback - copy instead of symlink
                if file_path != versioned_path:
                    shutil.copy2(versioned_path, file_path)
                print(f"✓ Updated copy (no symlink support): {file_path.name}")
        except OSError as e:
            print(f"WARNING: Could not create symlink for {file_path.name}: {e}")
            print(f"         Falling back to copy")
            if file_path != versioned_path:
                shutil.copy2(versioned_path, file_path)


def add_version_entry(
    version_history: Dict[str, Any],
    new_version: str,
    change_type: str,
    rationale: str,
    similarity_score_before: Optional[float],
    similarity_score_after: Optional[float],
    changed_files: List[str],
    triggered_by: str,
    test_evidence: Optional[str],
    breaking_changes: bool
) -> Dict[str, Any]:
    """Add new version entry to version history."""

    entry = {
        "version": new_version,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "change_type": change_type,
        "rationale": rationale,
        "similarity_score_before": similarity_score_before,
        "similarity_score_after": similarity_score_after,
        "changed_files": changed_files,
        "triggered_by": triggered_by,
        "test_evidence": test_evidence,
        "breaking_changes": breaking_changes,
        "migration_notes": None  # User can manually add migration notes if needed
    }

    version_history["version_history"].append(entry)
    version_history["current_version"] = new_version
    version_history["total_versions"] = len(version_history["version_history"])

    return version_history


def main():
    parser = argparse.ArgumentParser(
        description="Version architecture changes with rationale and traceability",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Version architecture after performance optimization
  python3 version_architecture.py \\
      --system-root /path/to/system \\
      --change-type performance_optimization \\
      --rationale "Redesigned for async processing due to 45s latency" \\
      --similarity-score 0.62 \\
      --changed-files "service_architecture.json,functional_architecture.json" \\
      --triggered-by "TO-05 operational testing failure"

  # Version architecture after requirements change
  python3 version_architecture.py \\
      --system-root /path/to/system \\
      --change-type requirements_creep \\
      --rationale "Added authentication requirements discovered during testing" \\
      --changed-files "service_architecture.json,interface_registry.json" \\
      --triggered-by "TO-05-A05.6 Architecture Update Loop"
        """
    )

    parser.add_argument(
        '--system-root',
        type=str,
        required=True,
        help='Path to system root directory'
    )

    parser.add_argument(
        '--change-type',
        type=str,
        required=True,
        choices=[
            'initial_design',
            'requirements_creep',
            'performance_optimization',
            'technical_constraints',
            'security_hardening',
            'operational_reality',
            'developer_mistake_fix'
        ],
        help='Type of change that triggered architecture update'
    )

    parser.add_argument(
        '--rationale',
        type=str,
        required=True,
        help='Human-readable explanation of why architecture changed'
    )

    parser.add_argument(
        '--similarity-score',
        type=float,
        required=False,
        help='Similarity score before architecture update (from D-06 or TO-06 delta report)'
    )

    parser.add_argument(
        '--similarity-score-after',
        type=float,
        required=False,
        help='Similarity score after architecture update (optional, can be calculated later)'
    )

    parser.add_argument(
        '--changed-files',
        type=str,
        required=True,
        help='Comma-separated list of changed architecture files (e.g., "service_architecture.json,functional_architecture.json")'
    )

    parser.add_argument(
        '--triggered-by',
        type=str,
        required=True,
        help='Workflow step or event that triggered this architecture update (e.g., "D-06.5", "TO-05-A05.6")'
    )

    parser.add_argument(
        '--test-evidence',
        type=str,
        required=False,
        help='Path to test results or evidence that triggered change (e.g., "specs/machine/ote_artifacts.json")'
    )

    parser.add_argument(
        '--breaking-changes',
        action='store_true',
        help='Explicitly mark as breaking changes (increments major version)'
    )

    parser.add_argument(
        '--system-name',
        type=str,
        required=False,
        help='System name (only needed for first versioning, otherwise read from version history)'
    )

    args = parser.parse_args()

    # Validate system root
    system_root = Path(args.system_root).resolve()
    if not system_root.exists():
        print(f"ERROR: System root does not exist: {system_root}")
        return 1

    # Ensure specs/machine directory exists
    specs_machine = system_root / "specs" / "machine"
    if not specs_machine.exists():
        print(f"ERROR: specs/machine directory does not exist: {specs_machine}")
        print(f"       Run setup workflow (00a-basic_setup.json) first")
        return 1

    # Get or create version history
    system_name = args.system_name or "System"
    version_history, version_history_path = get_or_create_version_history(system_root, system_name)

    # If version history exists, use system name from history
    if version_history["version_history"]:
        system_name = version_history["system_name"]

    # Get current version
    current_version = version_history["current_version"]

    # Identify changed files
    changed_files = identify_changed_files(system_root, args.changed_files)
    if not changed_files:
        print("ERROR: No valid changed files found")
        return 1

    # Detect breaking changes
    breaking_changes = args.breaking_changes or detect_breaking_changes(changed_files)

    # Increment version
    new_version = increment_version(current_version, args.change_type, breaking_changes)

    print(f"\n{'='*80}")
    print(f"Architecture Versioning Tool")
    print(f"{'='*80}")
    print(f"System: {system_name}")
    print(f"Current Version: {current_version}")
    print(f"New Version: {new_version}")
    print(f"Change Type: {args.change_type}")
    print(f"Breaking Changes: {'Yes' if breaking_changes else 'No'}")
    print(f"Similarity Score (before): {args.similarity_score if args.similarity_score else 'N/A'}")
    print(f"Triggered By: {args.triggered_by}")
    print(f"{'='*80}\n")

    # Create versioned copies
    print("Creating versioned architecture files...")
    create_versioned_copies(system_root, changed_files, new_version)

    # Update symlinks
    print("\nUpdating symlinks to latest version...")
    update_symlinks(system_root, changed_files, new_version)

    # Add version entry
    print("\nUpdating version history...")
    version_history = add_version_entry(
        version_history=version_history,
        new_version=new_version,
        change_type=args.change_type,
        rationale=args.rationale,
        similarity_score_before=args.similarity_score,
        similarity_score_after=args.similarity_score_after,
        changed_files=changed_files,
        triggered_by=args.triggered_by,
        test_evidence=args.test_evidence,
        breaking_changes=breaking_changes
    )

    # Save version history
    save_json(version_history_path, version_history)
    print(f"✓ Updated version history: {version_history_path.relative_to(system_root)}")

    # Print summary
    print(f"\n{'='*80}")
    print(f"✓ Architecture Versioning Complete")
    print(f"{'='*80}")
    print(f"New Version: {new_version}")
    print(f"Total Versions: {version_history['total_versions']}")
    print(f"Rationale: {args.rationale}")
    print(f"\nVersioned Files:")
    for file_path in changed_files:
        print(f"  - {file_path}")
    print(f"\nVersion History: {version_history_path.relative_to(system_root)}")
    print(f"{'='*80}\n")

    return 0


if __name__ == '__main__':
    exit(main())
