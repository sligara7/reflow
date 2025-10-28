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
            },
            'dependencies': {
                'services_consumed': []
            }
        }

    def test_generate_human_doc_structure(self):
        """Test that generated markdown has correct structure."""
        doc = generate_human_doc(self.sample_arch)

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

        doc = generate_human_doc(arch)
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
        # Port is parsed as string from markdown
        self.assertEqual(int(provided[0]['port']), 8000)

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

    def test_detect_changes_version_changed(self):
        """Test detecting version changes."""
        old_arch = {'version': '1.0.0'}
        new_arch = {'version': '1.1.0'}

        changes = detect_changes(old_arch, new_arch)

        self.assertTrue(any(c['type'] == 'version_changed' for c in changes))


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
        # Should have no ERROR-level issues
        errors = [i for i in issues if i['severity'] == 'ERROR']
        self.assertEqual(len(errors), 0)

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

    def test_protocol_mismatch_warning(self):
        """Test protocol mismatch generates warning."""
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
                        'protocol': 'gRPC'
                    }
                ]
            }
        }

        compatible, issues = check_interface_compatibility(old_arch, new_arch)

        # Should be compatible (WARNING not ERROR)
        self.assertTrue(compatible)
        # Should have warning about protocol mismatch
        self.assertTrue(any(i['severity'] == 'WARNING' for i in issues))


if __name__ == '__main__':
    unittest.main()
