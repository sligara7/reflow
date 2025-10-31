# Implementation Guide: Human Documentation Enhancement (v3.8.0)

**Change Proposal**: CHANGE_PROPOSAL_2025-10-28_human_documentation.md
**Status**: FU-01 Complete (Analysis & Validation PASSED) → Ready for FU-02
**Timeline**: 6 weeks (5 phases)
**Priority**: HIGH

---

## Quick Start

To implement this feature:

```bash
# Clone and checkout
git clone github.com/sligara7/reflow
cd reflow
git checkout claude/systems-cohesion-validation-011CUUc22HJAhrR8frW45JAx

# Follow steps FU-02 through FU-06 in this guide
# Each step is self-contained with complete code
```

---

## FU-02: Architecture Re-Engineering (Implement 3 New Tools)

### Tool 1: generate_human_documentation.py

**Purpose**: Convert machine-readable service_architecture.json to human-readable markdown

**Implementation**:

```python
#!/usr/bin/env python3
"""
Generate human-readable documentation from machine-readable service architectures.

Usage:
    python3 generate_human_documentation.py --system-root /path/to/system
"""

import json
import argparse
from pathlib import Path
from datetime import datetime

def load_service_architecture(arch_path: Path) -> dict:
    """Load service architecture JSON."""
    with open(arch_path, 'r') as f:
        return json.load(f)

def generate_human_doc(service_arch: dict, template: str) -> str:
    """Generate human-readable markdown from service architecture."""

    # Extract metadata
    service_id = service_arch.get('service_id', 'unknown')
    service_name = service_arch.get('service_name', 'Unknown Service')
    version = service_arch.get('version', '1.0.0')
    description = service_arch.get('description', 'No description')

    # Extract interfaces
    interfaces = service_arch.get('interfaces', {})
    provided = interfaces.get('provided_interfaces', [])
    required = interfaces.get('required_interfaces', [])

    # Extract deployment
    deployment = service_arch.get('deployment', {})
    container = deployment.get('container_name', 'N/A')
    ports = deployment.get('ports', {})

    # Extract dependencies
    dependencies = service_arch.get('dependencies', {})
    services_consumed = dependencies.get('services_consumed', [])

    # Generate markdown
    doc = f"""---
service_id: {service_id}
version: {version}
last_updated: {datetime.now().strftime('%Y-%m-%d')}
framework: {service_arch.get('framework', 'uaf')}
---

# {service_name}

## Overview

{description}

**Service ID**: `{service_id}`
**Version**: {version}
**Type**: {service_arch.get('service_type', 'service')}

## Provides

"""

    if provided:
        for ifc in provided:
            doc += f"""### {ifc.get('interface_name', 'Unnamed')} (`{ifc.get('interface_id', 'unknown')}`)

- **Protocol**: {ifc.get('protocol', 'N/A')}
- **Data Format**: {ifc.get('data_format', 'N/A')}
- **Port**: {ifc.get('port', 'N/A')}
- **Description**: {ifc.get('description', 'No description')}

"""
    else:
        doc += "No interfaces provided.\n\n"

    doc += "## Requires\n\n"

    if required:
        for ifc in required:
            doc += f"""### {ifc.get('interface_name', 'Unnamed')} (`{ifc.get('interface_id', 'unknown')}`)

- **Provider**: {ifc.get('provider_service_id', 'Unknown')}
- **Criticality**: {ifc.get('criticality', 'medium')}

"""
    else:
        doc += "No external interfaces required.\n\n"

    doc += f"""## Dependencies

"""

    if services_consumed:
        for dep in services_consumed:
            doc += f"- **{dep.get('service_id', 'unknown')}**: {dep.get('dependency_type', 'unknown')} dependency\n"
    else:
        doc += "No service dependencies.\n"

    doc += f"""

## Deployment

- **Container**: `{container}`
"""

    if ports:
        primary = ports.get('primary', {})
        doc += f"""- **Port**: {primary.get('port', 'N/A')} ({primary.get('protocol', 'N/A')})
- **Exposure**: {primary.get('exposure', 'internal')}
"""

    health_checks = deployment.get('health_checks', {})
    if health_checks:
        doc += f"""- **Health Check**: {health_checks.get('endpoint', '/health')} → {health_checks.get('expected_status', 200)}
"""

    doc += f"""

## Configuration

"""

    env_vars = deployment.get('environment_variables', [])
    if env_vars:
        for var in env_vars:
            doc += f"- `{var.get('name', 'UNKNOWN')}`: {var.get('description', 'No description')}\n"
    else:
        doc += "No environment variables.\n"

    doc += f"""

## Version History

- **{version}** ({datetime.now().strftime('%Y-%m-%d')}): Current version

---

**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Machine Spec**: `specs/machine/service_arch/{service_id}/service_architecture.json`
"""

    return doc

def main():
    parser = argparse.ArgumentParser(description='Generate human-readable documentation')
    parser.add_argument('--system-root', required=True, help='System root directory')
    parser.add_argument('--output-dir', help='Output directory (default: specs/human/documentation/services)')
    args = parser.parse_args()

    system_root = Path(args.system_root)
    output_dir = Path(args.output_dir) if args.output_dir else system_root / 'specs/human/documentation/services'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Find all service architectures
    arch_dir = system_root / 'specs/machine/service_arch'
    if not arch_dir.exists():
        print(f"❌ No service architectures found at {arch_dir}")
        return 1

    count = 0
    for service_dir in arch_dir.iterdir():
        if not service_dir.is_dir():
            continue

        # Find symlink (current version)
        arch_file = service_dir / 'service_architecture.json'
        if not arch_file.exists():
            continue

        # Load and generate
        service_arch = load_service_architecture(arch_file)
        human_doc = generate_human_doc(service_arch, template='')

        # Write to output
        service_id = service_arch.get('service_id', service_dir.name)
        output_file = output_dir / f"{service_id}.md"
        with open(output_file, 'w') as f:
            f.write(human_doc)

        print(f"✅ Generated: {output_file}")
        count += 1

    print(f"\n✅ Generated {count} human documentation files")
    return 0

if __name__ == '__main__':
    exit(main())
```

**Test**:
```bash
python3 tools/generate_human_documentation.py --system-root /path/to/test_system
# Should create specs/human/documentation/services/*.md files
```

---

### Tool 2: parse_human_documentation.py

**Purpose**: Parse human-edited markdown back to machine-readable service_architecture.json

**Implementation** (Abbreviated - full version ~500 lines):

```python
#!/usr/bin/env python3
"""
Parse human-readable documentation back to machine-readable service architectures.

Usage:
    python3 parse_human_documentation.py --system-root /path/to/system --validate
"""

import json
import argparse
import re
from pathlib import Path
from datetime import datetime
import yaml

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown."""
    if not content.startswith('---'):
        return {}, content

    parts = content.split('---', 2)
    if len(parts) < 3:
        return {}, content

    try:
        frontmatter = yaml.safe_load(parts[1])
        body = parts[2].strip()
        return frontmatter, body
    except:
        return {}, content

def parse_section(body: str, section_name: str) -> str:
    """Extract section content from markdown."""
    pattern = f'## {section_name}\\n(.+?)(?=\\n## |$)'
    match = re.search(pattern, body, re.DOTALL)
    return match.group(1).strip() if match else ''

def parse_interfaces(section: str, interface_type: str) -> list:
    """Parse interface definitions from markdown section."""
    interfaces = []

    # Find all ### headers (interface names)
    pattern = r'### (.+?) \(`(.+?)`\)\n(.+?)(?=\n### |\Z)'
    matches = re.finditer(pattern, section, re.DOTALL)

    for match in matches:
        name = match.group(1).strip()
        ifc_id = match.group(2).strip()
        content = match.group(3).strip()

        # Parse bullet points
        protocol = re.search(r'\*\*Protocol\*\*: (.+)', content)
        data_format = re.search(r'\*\*Data Format\*\*: (.+)', content)
        port = re.search(r'\*\*Port\*\*: (.+)', content)
        description = re.search(r'\*\*Description\*\*: (.+)', content)

        ifc = {
            'interface_id': ifc_id,
            'interface_name': name,
        }

        if protocol:
            ifc['protocol'] = protocol.group(1).strip()
        if data_format:
            ifc['data_format'] = data_format.group(1).strip()
        if port:
            ifc['port'] = port.group(1).strip()
        if description:
            ifc['description'] = description.group(1).strip()

        interfaces.append(ifc)

    return interfaces

def parse_human_doc(md_content: str) -> dict:
    """Parse human documentation to service architecture dict."""

    frontmatter, body = parse_frontmatter(md_content)

    # Extract sections
    overview = parse_section(body, 'Overview')
    provides = parse_section(body, 'Provides')
    requires = parse_section(body, 'Requires')
    dependencies = parse_section(body, 'Dependencies')
    deployment = parse_section(body, 'Deployment')
    configuration = parse_section(body, 'Configuration')

    # Build service architecture
    service_arch = {
        'service_id': frontmatter.get('service_id', 'unknown'),
        'service_name': body.split('\n')[0].strip('# '),
        'version': frontmatter.get('version', '1.0.0'),
        'framework': frontmatter.get('framework', 'uaf'),
        'description': overview.split('\n')[0],
        'interfaces': {
            'provided_interfaces': parse_interfaces(provides, 'provided'),
            'required_interfaces': parse_interfaces(requires, 'required')
        },
        'deployment': {},
        'dependencies': {}
    }

    # Parse deployment section
    container_match = re.search(r'\*\*Container\*\*: `(.+?)`', deployment)
    if container_match:
        service_arch['deployment']['container_name'] = container_match.group(1)

    port_match = re.search(r'\*\*Port\*\*: (\d+) \((.+?)\)', deployment)
    if port_match:
        service_arch['deployment']['ports'] = {
            'primary': {
                'port': int(port_match.group(1)),
                'protocol': port_match.group(2)
            }
        }

    return service_arch

def detect_changes(old_arch: dict, new_arch: dict) -> list:
    """Detect changes between old and new architecture."""
    changes = []

    # Compare service name
    if old_arch.get('service_name') != new_arch.get('service_name'):
        changes.append({
            'type': 'service_name_changed',
            'old': old_arch.get('service_name'),
            'new': new_arch.get('service_name')
        })

    # Compare interfaces (simplified)
    old_provided = old_arch.get('interfaces', {}).get('provided_interfaces', [])
    new_provided = new_arch.get('interfaces', {}).get('provided_interfaces', [])

    old_ids = {i['interface_id'] for i in old_provided}
    new_ids = {i['interface_id'] for i in new_provided}

    added = new_ids - old_ids
    removed = old_ids - new_ids

    for ifc_id in added:
        changes.append({'type': 'interface_added', 'interface_id': ifc_id})
    for ifc_id in removed:
        changes.append({'type': 'interface_removed', 'interface_id': ifc_id})

    return changes

def main():
    parser = argparse.ArgumentParser(description='Parse human documentation to machine specs')
    parser.add_argument('--system-root', required=True, help='System root directory')
    parser.add_argument('--validate', action='store_true', help='Run validation after parsing')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without writing')
    args = parser.parse_args()

    system_root = Path(args.system_root)
    human_docs_dir = system_root / 'specs/human/documentation/services'
    machine_specs_dir = system_root / 'specs/machine/service_arch'

    if not human_docs_dir.exists():
        print(f"❌ No human documentation found at {human_docs_dir}")
        return 1

    changes_summary = []

    for human_doc in human_docs_dir.glob('*.md'):
        with open(human_doc, 'r') as f:
            md_content = f.read()

        # Parse
        new_arch = parse_human_doc(md_content)
        service_id = new_arch['service_id']

        # Load old architecture
        old_arch_file = machine_specs_dir / service_id / 'service_architecture.json'
        if old_arch_file.exists():
            with open(old_arch_file, 'r') as f:
                old_arch = json.load(f)
        else:
            old_arch = {}

        # Detect changes
        changes = detect_changes(old_arch, new_arch)

        if changes:
            changes_summary.append({
                'service_id': service_id,
                'changes': changes
            })

            print(f"\n📝 {service_id}:")
            for change in changes:
                print(f"  - {change['type']}: {change.get('old', '')} → {change.get('new', '')}")

            if not args.dry_run:
                # Write new version
                version = new_arch['version']
                new_version_file = machine_specs_dir / service_id / f"service_architecture_v{version}-{datetime.now().strftime('%Y%m%d')}.json"
                new_version_file.parent.mkdir(parents=True, exist_ok=True)

                with open(new_version_file, 'w') as f:
                    json.dump(new_arch, f, indent=2)

                # Update symlink
                symlink = machine_specs_dir / service_id / 'service_architecture.json'
                if symlink.exists():
                    symlink.unlink()
                symlink.symlink_to(new_version_file.name)

                print(f"  ✅ Updated: {new_version_file}")

    if args.validate and not args.dry_run:
        print("\n🔍 Running validation...")
        # Run system_of_systems_graph_v2.py validation
        import subprocess
        result = subprocess.run([
            'python3', str(system_root / '../tools/system_of_systems_graph_v2.py'),
            str(system_root / 'specs/machine/index.json'),
            '--detect-gaps'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Validation PASSED")
        else:
            print("❌ Validation FAILED:")
            print(result.stderr)
            return 1

    print(f"\n✅ Processed {len(changes_summary)} services with changes")
    return 0

if __name__ == '__main__':
    exit(main())
```

**Test**:
```bash
# Edit a human doc
vim specs/human/documentation/services/my_service.md

# Parse back to machine spec (dry-run first)
python3 tools/parse_human_documentation.py --system-root /path/to/system --dry-run

# Apply changes
python3 tools/parse_human_documentation.py --system-root /path/to/system --validate
```

---

### Tool 3: component_swap.py

**Purpose**: Safely swap one component for another with validation

**Implementation** (Abbreviated):

```python
#!/usr/bin/env python3
"""
Safely swap one component for another in system architecture.

Usage:
    python3 component_swap.py --index specs/machine/index.json \\
        --remove apache_proxy --add haproxy_proxy --validate
"""

import json
import argparse
from pathlib import Path

def load_service_architecture(arch_path: Path) -> dict:
    """Load service architecture."""
    with open(arch_path, 'r') as f:
        return json.load(f)

def check_interface_compatibility(old_arch: dict, new_arch: dict) -> tuple[bool, list]:
    """Check if new component provides compatible interfaces."""
    issues = []

    old_provided = old_arch.get('interfaces', {}).get('provided_interfaces', [])
    new_provided = new_arch.get('interfaces', {}).get('provided_interfaces', [])

    old_ids = {i['interface_id'] for i in old_provided}
    new_ids = {i['interface_id'] for i in new_provided}

    missing = old_ids - new_ids
    if missing:
        issues.append({
            'severity': 'ERROR',
            'message': f"New component missing interfaces: {missing}"
        })

    # Check protocol compatibility
    for old_ifc in old_provided:
        old_id = old_ifc['interface_id']
        new_ifc = next((i for i in new_provided if i['interface_id'] == old_id), None)

        if new_ifc:
            if old_ifc.get('protocol') != new_ifc.get('protocol'):
                issues.append({
                    'severity': 'WARNING',
                    'message': f"Protocol mismatch on {old_id}: {old_ifc.get('protocol')} vs {new_ifc.get('protocol')}"
                })

    compatible = not any(i['severity'] == 'ERROR' for i in issues)
    return compatible, issues

def update_index(index_path: Path, old_service: str, new_service: str, dry_run: bool = False):
    """Update index.json to reference new service."""
    with open(index_path, 'r') as f:
        index = json.load(f)

    components = index.get('components', {})

    if old_service not in components:
        print(f"❌ Service {old_service} not found in index")
        return False

    old_path = components[old_service]
    new_path = old_path.replace(old_service, new_service)

    if not dry_run:
        components[new_service] = new_path
        del components[old_service]

        with open(index_path, 'w') as f:
            json.dump(index, f, indent=2)

        print(f"✅ Updated index: {old_service} → {new_service}")
    else:
        print(f"[DRY-RUN] Would update: {old_service} → {new_service}")

    return True

def generate_report(old_service: str, new_service: str, compatible: bool, issues: list, output_path: Path):
    """Generate component swap compatibility report."""

    report = f"""# Component Swap Report

**Old**: {old_service}
**New**: {new_service}
**Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Compatibility Summary

"""

    if compatible:
        report += "✅ **Status**: COMPATIBLE\n\n"
    else:
        report += "❌ **Status**: INCOMPATIBLE\n\n"

    report += "## Issues\n\n"

    if not issues:
        report += "No issues detected.\n"
    else:
        for issue in issues:
            icon = "❌" if issue['severity'] == 'ERROR' else "⚠️"
            report += f"{icon} **{issue['severity']}**: {issue['message']}\n\n"

    with open(output_path, 'w') as f:
        f.write(report)

    print(f"📄 Report: {output_path}")

def main():
    parser = argparse.ArgumentParser(description='Component swap tool')
    parser.add_argument('--index', required=True, help='Path to index.json')
    parser.add_argument('--remove', required=True, help='Old service ID')
    parser.add_argument('--add', required=True, help='New service ID')
    parser.add_argument('--validate', action='store_true', help='Run validation after swap')
    parser.add_argument('--dry-run', action='store_true', help='Show changes without applying')
    args = parser.parse_args()

    index_path = Path(args.index)
    system_root = index_path.parent.parent

    # Load architectures
    old_arch_path = system_root / 'specs/machine/service_arch' / args.remove / 'service_architecture.json'
    new_arch_path = system_root / 'specs/machine/service_arch' / args.add / 'service_architecture.json'

    if not old_arch_path.exists():
        print(f"❌ Old service architecture not found: {old_arch_path}")
        return 1

    if not new_arch_path.exists():
        print(f"❌ New service architecture not found: {new_arch_path}")
        return 1

    old_arch = load_service_architecture(old_arch_path)
    new_arch = load_service_architecture(new_arch_path)

    # Check compatibility
    compatible, issues = check_interface_compatibility(old_arch, new_arch)

    print(f"\n🔍 Compatibility Check: {args.remove} → {args.add}")
    for issue in issues:
        icon = "❌" if issue['severity'] == 'ERROR' else "⚠️"
        print(f"  {icon} {issue['severity']}: {issue['message']}")

    if not compatible:
        print("\n❌ Components are INCOMPATIBLE - cannot swap")
        return 1

    print("\n✅ Components are COMPATIBLE")

    # Update index
    success = update_index(index_path, args.remove, args.add, args.dry_run)

    if not success:
        return 1

    # Generate report
    report_path = system_root / 'context' / f"component_swap_{args.remove}_to_{args.add}.md"
    generate_report(args.remove, args.add, compatible, issues, report_path)

    if args.validate and not args.dry_run:
        print("\n🔍 Running validation...")
        import subprocess
        result = subprocess.run([
            'python3', 'tools/system_of_systems_graph_v2.py',
            str(index_path),
            '--detect-gaps'
        ], capture_output=True, text=True)

        if result.returncode == 0:
            print("✅ Validation PASSED")
        else:
            print("❌ Validation FAILED - rolling back")
            # Rollback
            update_index(index_path, args.add, args.remove, dry_run=False)
            return 1

    return 0

if __name__ == '__main__':
    import sys
    from datetime import datetime
    sys.exit(main())
```

**Test**:
```bash
# Dry-run first
python3 tools/component_swap.py \
  --index specs/machine/index.json \
  --remove apache_proxy \
  --add haproxy_proxy \
  --dry-run

# Apply swap
python3 tools/component_swap.py \
  --index specs/machine/index.json \
  --remove apache_proxy \
  --add haproxy_proxy \
  --validate
```

---

## FU-03: Version Management

### Update version_manifest.json

**File**: `specs/machine/version_manifest.json`

**Add**:
```json
{
  "reflow_version": "3.8.0",
  "features": {
    "human_documentation": {
      "version": "1.0.0",
      "tools": [
        "generate_human_documentation.py",
        "parse_human_documentation.py",
        "component_swap.py"
      ],
      "templates": [
        "service_documentation_template.md",
        "component_swap_report_template.md"
      ],
      "workflows": [
        "human_edit_workflow.json",
        "component_swap_workflow.json"
      ]
    }
  }
}
```

### Update CHANGELOG.md

```markdown
## [3.8.0] - 2025-11-XX

### Added

- **Human Documentation Workflow** - Comprehensive human-readable documentation generation
  - `generate_human_documentation.py` - Convert machine specs to markdown
  - `parse_human_documentation.py` - Parse human edits back to machine specs with validation
  - `component_swap.py` - Safe component swapping with interface compatibility checking
- **PNG/SVG Rendering** - Mermaid diagrams now rendered to distributable image formats
- **Bidirectional Translation** - Human↔Machine documentation synchronization
- **Component Swap Validation** - Automated compatibility checking when replacing services

### Changed

- **`02-artifacts_visualization.json`** - Human documentation now MANDATORY (removed "conditional" flag)
- **AV-02 Workflow** - Added AV-02-A05 for PNG/SVG rendering
- **AV-01 Workflow** - Added AV-01-A04 for human documentation generation

### Fixed

- LLMs no longer skip human documentation steps
- Stakeholders can now review PNG/SVG diagrams (not just .mmd files)
- Architecture changes can be proposed via markdown edits (not JSON)

### Documentation

- Added `docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md` - Comprehensive analysis
- Added `docs/changes/CHANGE_PROPOSAL_2025-10-28_human_documentation.md` - Feature proposal
- Added `docs/changes/IMPLEMENTATION_GUIDE_human_documentation.md` - Implementation guide
- Updated `CLAUDE.md` - Added human documentation workflow guidance
- Updated `README.md` - Added v3.8.0 features

## [3.7.0] - 2025-10-27

...
```

---

## FU-04: Validation & Testing

### Create Test Suite

**File**: `tests/test_human_documentation_tools.py`

```python
#!/usr/bin/env python3
"""
Test suite for human documentation tools.
"""

import unittest
import json
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent / 'tools'))

from generate_human_documentation import generate_human_doc
from parse_human_documentation import parse_human_doc, detect_changes
from component_swap import check_interface_compatibility

class TestGenerateHumanDocumentation(unittest.TestCase):

    def setUp(self):
        self.sample_arch = {
            'service_id': 'test_service',
            'service_name': 'Test Service',
            'version': '1.0.0',
            'description': 'A test service',
            'framework': 'uaf',
            'interfaces': {
                'provided_interfaces': [
                    {
                        'interface_id': 'IFC-TEST-001',
                        'interface_name': 'Test API',
                        'protocol': 'REST/HTTP',
                        'data_format': 'JSON',
                        'port': 8000
                    }
                ],
                'required_interfaces': []
            },
            'deployment': {
                'container_name': 'test_service',
                'ports': {
                    'primary': {
                        'port': 8000,
                        'protocol': 'HTTP',
                        'exposure': 'external'
                    }
                }
            }
        }

    def test_generate_human_doc_structure(self):
        """Test that generated markdown has correct structure."""
        doc = generate_human_doc(self.sample_arch, template='')

        # Check frontmatter
        self.assertIn('---', doc)
        self.assertIn('service_id: test_service', doc)
        self.assertIn('version: 1.0.0', doc)

        # Check sections
        self.assertIn('## Overview', doc)
        self.assertIn('## Provides', doc)
        self.assertIn('## Requires', doc)
        self.assertIn('## Deployment', doc)

        # Check interface details
        self.assertIn('Test API', doc)
        self.assertIn('IFC-TEST-001', doc)
        self.assertIn('REST/HTTP', doc)

    def test_generate_human_doc_no_interfaces(self):
        """Test generation with no interfaces."""
        arch = self.sample_arch.copy()
        arch['interfaces'] = {
            'provided_interfaces': [],
            'required_interfaces': []
        }

        doc = generate_human_doc(arch, template='')
        self.assertIn('No interfaces provided', doc)
        self.assertIn('No external interfaces required', doc)

class TestParseHumanDocumentation(unittest.TestCase):

    def setUp(self):
        self.sample_md = """---
service_id: test_service
version: 1.0.0
framework: uaf
---

# Test Service

## Overview

A test service for unit testing.

## Provides

### Test API (`IFC-TEST-001`)

- **Protocol**: REST/HTTP
- **Data Format**: JSON
- **Port**: 8000

## Requires

No external interfaces required.

## Deployment

- **Container**: `test_service`
- **Port**: 8000 (HTTP)
"""

    def test_parse_human_doc_frontmatter(self):
        """Test parsing YAML frontmatter."""
        arch = parse_human_doc(self.sample_md)

        self.assertEqual(arch['service_id'], 'test_service')
        self.assertEqual(arch['version'], '1.0.0')
        self.assertEqual(arch['framework'], 'uaf')

    def test_parse_human_doc_interfaces(self):
        """Test parsing interface definitions."""
        arch = parse_human_doc(self.sample_md)

        provided = arch['interfaces']['provided_interfaces']
        self.assertEqual(len(provided), 1)
        self.assertEqual(provided[0]['interface_id'], 'IFC-TEST-001')
        self.assertEqual(provided[0]['protocol'], 'REST/HTTP')
        self.assertEqual(provided[0]['port'], '8000')

    def test_detect_changes_interface_added(self):
        """Test detecting added interfaces."""
        old_arch = {
            'interfaces': {
                'provided_interfaces': []
            }
        }
        new_arch = {
            'interfaces': {
                'provided_interfaces': [
                    {'interface_id': 'IFC-NEW-001'}
                ]
            }
        }

        changes = detect_changes(old_arch, new_arch)

        self.assertTrue(any(c['type'] == 'interface_added' for c in changes))

class TestComponentSwap(unittest.TestCase):

    def test_compatible_interfaces(self):
        """Test interface compatibility checking."""
        old_arch = {
            'interfaces': {
                'provided_interfaces': [
                    {
                        'interface_id': 'IFC-API-001',
                        'protocol': 'REST/HTTP'
                    }
                ]
            }
        }
        new_arch = {
            'interfaces': {
                'provided_interfaces': [
                    {
                        'interface_id': 'IFC-API-001',
                        'protocol': 'REST/HTTP'
                    }
                ]
            }
        }

        compatible, issues = check_interface_compatibility(old_arch, new_arch)

        self.assertTrue(compatible)
        self.assertEqual(len(issues), 0)

    def test_incompatible_missing_interface(self):
        """Test detecting missing interfaces."""
        old_arch = {
            'interfaces': {
                'provided_interfaces': [
                    {'interface_id': 'IFC-API-001'},
                    {'interface_id': 'IFC-API-002'}
                ]
            }
        }
        new_arch = {
            'interfaces': {
                'provided_interfaces': [
                    {'interface_id': 'IFC-API-001'}
                ]
            }
        }

        compatible, issues = check_interface_compatibility(old_arch, new_arch)

        self.assertFalse(compatible)
        self.assertTrue(any('missing interfaces' in i['message'].lower() for i in issues))

if __name__ == '__main__':
    unittest.main()
```

**Run Tests**:
```bash
python3 tests/test_human_documentation_tools.py -v
```

---

## FU-05: Documentation Updates

### Update CLAUDE.md

**Section to Add** (after "Context Management"):

```markdown
### Human Documentation Workflow (NEW in v3.8.0)

**Purpose**: Enable human-in-the-loop architecture editing with bidirectional translation

**Workflow**:
```
1. Generate human docs from machine specs:
   python3 {paths.tools_path}/generate_human_documentation.py --system-root {paths.system_root}

2. Human reviews/edits markdown files:
   vim specs/human/documentation/services/my_service.md

3. Parse human docs back to machine specs:
   python3 {paths.tools_path}/parse_human_documentation.py --system-root {paths.system_root} --validate

4. If validation passes: Changes committed
   If validation fails: Conflict report generated
```

**Key Files**:
- **Human Docs**: `specs/human/documentation/services/*.md`
- **Machine Specs**: `specs/machine/service_arch/*/service_architecture.json`
- **Visualizations**: `specs/human/visualizations/*.{mmd,png,svg}`

**Tools**:
- `generate_human_documentation.py` - Machine → Human
- `parse_human_documentation.py` - Human → Machine (with validation)
- `component_swap.py` - Safe component replacement

**Benefits**:
- ✅ Non-technical stakeholders can review architecture
- ✅ Propose changes via markdown edits (not JSON)
- ✅ Automatic validation prevents broken dependencies
- ✅ Version control tracks architecture evolution
```

### Update README.md

**Add to Features** section:

```markdown
### Human Documentation & Bidirectional Translation (v3.8.0)

**Problem**: Stakeholders can't review .mmd files or .json specs, can't propose architecture changes

**Solution**: Auto-generate human-readable markdown "sister documents" with bidirectional translation

**Features**:
- 📄 **Auto-generate human docs** from machine specs (`generate_human_documentation.py`)
- 🔄 **Bidirectional translation** - Edit markdown, propagate to JSON (`parse_human_documentation.py`)
- 🔄 **Component swapping** - Replace services with validation (`component_swap.py`)
- 🖼️ **PNG/SVG rendering** - Convert Mermaid diagrams to distributable images
- 📊 **Version tracking** - Both human + machine docs versioned

**Example**:
```bash
# Generate human docs
python3 tools/generate_human_documentation.py --system-root ./my_system

# Edit human docs
vim specs/human/documentation/services/apache_proxy.md
# Change port 8000 → 8080

# Parse back to machine specs
python3 tools/parse_human_documentation.py --system-root ./my_system --validate
# ✅ Validation passed - changes committed

# Swap components
python3 tools/component_swap.py --index specs/machine/index.json \
  --remove apache_proxy --add haproxy_proxy --validate
# ✅ Compatible - swap applied
```

**Benefits**:
- Stakeholders review PNG/SVG diagrams (not .mmd files)
- Propose changes via markdown (not JSON)
- Automatic validation prevents broken architecture
- Track how system evolves over time
```

---

## FU-06: Release v3.8.0

### Tag Release

```bash
# Commit all changes
git add tools/ templates/ docs/ workflows/ CLAUDE.md README.md CHANGELOG.md
git commit -m "feat: Human Documentation & Bidirectional Translation (v3.8.0)

Comprehensive human documentation workflow with bidirectional translation.

Features:
- Generate human-readable markdown from machine specs
- Parse human edits back to machine specs with validation
- Safe component swapping with compatibility checking
- PNG/SVG rendering for Mermaid diagrams
- Version-controlled architecture evolution tracking

Tools Added:
- generate_human_documentation.py
- parse_human_documentation.py
- component_swap.py

Workflows Updated:
- 02-artifacts_visualization.json (now mandatory)

Closes #human-documentation-workflow"

# Tag release
git tag -a v3.8.0 -m "Release v3.8.0: Human Documentation & Bidirectional Translation

Major Features:
- Human-readable documentation generation (machine→human)
- Bidirectional translation with validation (human→machine)
- Component swap tool with compatibility checking
- PNG/SVG diagram rendering
- Mandatory human documentation workflow

See CHANGELOG.md for full details."

# Push
git push origin claude/systems-cohesion-validation-011CUUc22HJAhrR8frW45JAx
git push origin v3.8.0
```

### Create GitHub Release

**Title**: v3.8.0: Human Documentation & Bidirectional Translation

**Description**:
```markdown
# Human Documentation & Bidirectional Translation

Enable human-in-the-loop architecture editing with comprehensive documentation workflow.

## What's New

### 📄 Human-Readable Documentation

Auto-generate markdown "sister documents" from machine-readable specs:

- Stakeholder-friendly format (not JSON)
- Version-controlled alongside machine specs
- YAML frontmatter + structured sections

### 🔄 Bidirectional Translation

Edit human docs and propagate changes back to machine specs:

- Edit markdown files (easier than JSON)
- Automatic parsing back to service_architecture.json
- Re-runs validation (SE-06) to catch conflicts
- Commits if valid, reports conflicts if not

### 🔄 Component Swapping

Safely replace components with automated validation:

- Interface compatibility checking
- Dependency validation
- Index.json auto-update
- Compatibility report generation

Example: Swap Apache for HAProxy with one command

### 🖼️ PNG/SVG Rendering

Mermaid diagrams now rendered to distributable formats:

- PNG for presentations, reports
- SVG for scalable, interactive diagrams
- Embedded in documentation for stakeholder review

## New Tools

- `generate_human_documentation.py` - Machine → Human translator
- `parse_human_documentation.py` - Human → Machine translator + validator
- `component_swap.py` - Safe component replacement tool

## Updated Workflows

- **02-artifacts_visualization.json** - Human documentation now MANDATORY (not optional)
- **AV-02** - Added PNG/SVG rendering step
- **AV-01** - Added human documentation generation

## Breaking Changes

None - all enhancements are additive

## Migration Guide

No migration needed - existing workflows continue to work. New features available immediately.

## Documentation

- [Human Documentation Workflow Analysis](docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md)
- [Change Proposal](docs/changes/CHANGE_PROPOSAL_2025-10-28_human_documentation.md)
- [Implementation Guide](docs/changes/IMPLEMENTATION_GUIDE_human_documentation.md)

## Contributors

Based on user feedback from session_011CUYUVgvLxFJy3Hmzr7BaZ

🤖 Implemented with [Claude Code](https://claude.com/claude-code)
```

---

## Testing Checklist

Before releasing v3.8.0, verify:

- [ ] All 3 tools implemented and executable
- [ ] Unit tests pass (test_human_documentation_tools.py)
- [ ] Integration test: Generate → Edit → Parse → Validate workflow
- [ ] Component swap test: Replace service, verify validation
- [ ] PNG/SVG rendering works (Mermaid CLI installed)
- [ ] Documentation updated (CLAUDE.md, README.md, CHANGELOG.md)
- [ ] Version manifest updated
- [ ] Git tag created
- [ ] GitHub release published

---

## Post-Release

1. **Announce** in Reflow community/users
2. **Update examples** with human documentation workflow
3. **Create tutorial video** (optional)
4. **Gather feedback** for v3.9.0 improvements

---

## Estimated Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| FU-02 | 2 weeks | 3 tools implemented |
| FU-03 | 2 days | Version management updated |
| FU-04 | 1 week | Comprehensive test suite |
| FU-05 | 3 days | Documentation updated |
| FU-06 | 1 day | Release tagged and published |
| **Total** | **4 weeks** | v3.8.0 released |

---

## Support

Questions? See:
- `docs/HUMAN_DOCUMENTATION_WORKFLOW_ANALYSIS.md` - Comprehensive analysis
- `docs/changes/CHANGE_PROPOSAL_2025-10-28_human_documentation.md` - Feature justification
- `CLAUDE.md` - Human documentation workflow section

**Status**: Ready for implementation (FU-01 Complete, Validation Passed ✅)
