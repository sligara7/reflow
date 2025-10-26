#!/usr/bin/env python3
"""
Unit tests for system_of_systems_graph_v2.py

Tests core functionality of the flagship graph generation tool.
"""

import pytest
import json
from pathlib import Path
import sys

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from system_of_systems_graph_v2 import (
    load_framework_config,
    load_framework_registry,
    load_component_index,
    adapt_component_to_universal,
    match_dependency_to_component,
)

import networkx as nx


class TestFrameworkConfig:
    """Tests for loading framework configuration."""

    def test_load_framework_config_default_when_no_working_memory(self, tmp_path):
        """Test that default framework config is returned when no working_memory.json exists."""
        # Create empty system root
        system_root = tmp_path / "system"
        system_root.mkdir()

        framework = load_framework_config(system_root)

        # Should return default (UAF) framework
        assert 'framework_id' in framework
        # May return default values

    def test_load_framework_config_from_working_memory(self, tmp_path):
        """Test loading framework config from working_memory.json."""
        system_root = tmp_path / "system"
        system_root.mkdir()

        # Create working_memory.json with framework config
        context_dir = system_root / "context"
        context_dir.mkdir()
        wm_path = context_dir / "working_memory.json"

        wm_data = {
            "architectural_framework": "systems_biology",
            "framework_configuration": {
                "framework_id": "systems_biology",
                "framework_name": "Systems Biology Framework"
            }
        }
        wm_path.write_text(json.dumps(wm_data))

        framework = load_framework_config(system_root)

        assert framework['framework_id'] == 'systems_biology'


class TestFrameworkRegistryLoading:
    """Tests for loading framework registry from definitions."""

    def test_load_framework_registry_uaf(self):
        """Test successful loading of UAF framework from registry."""
        # This test requires the actual framework_registry.json to exist
        definitions_path = Path(__file__).parent.parent.parent / "definitions" / "framework_registry.json"

        if not definitions_path.exists():
            pytest.skip("framework_registry.json not found in definitions/")

        schema = load_framework_registry("uaf")

        assert 'name' in schema
        assert 'node_type' in schema or 'node_schema' in schema
        assert schema is not None

    def test_load_framework_registry_missing_framework(self):
        """Test that missing framework raises ValueError."""
        # When framework not found in registry, should raise ValueError
        with pytest.raises(ValueError, match="Framework 'nonexistent_framework_xyz' not found"):
            load_framework_registry("nonexistent_framework_xyz")


class TestComponentIndexLoading:
    """Tests for loading component index."""

    def test_load_component_index_structured_format(self, tmp_path):
        """Test loading structured index with components key."""
        index_path = tmp_path / "index.json"
        index_data = {
            "metadata": {"version": "1.0"},
            "components": {
                "service1": "path/to/service1.json",
                "service2": "path/to/service2.json"
            }
        }
        index_path.write_text(json.dumps(index_data))

        components = load_component_index(index_path)

        assert len(components) == 2
        assert "service1" in components
        assert components["service1"] == "path/to/service1.json"

    def test_load_component_index_flat_format(self, tmp_path):
        """Test loading flat index format (legacy)."""
        index_path = tmp_path / "index.json"
        index_data = {
            "service1": "path/to/service1.json",
            "service2": "path/to/service2.json"
        }
        index_path.write_text(json.dumps(index_data))

        components = load_component_index(index_path)

        assert len(components) == 2
        assert "service1" in components

    def test_load_component_index_empty(self, tmp_path):
        """Test loading empty index."""
        index_path = tmp_path / "index.json"
        index_data = {"components": {}}
        index_path.write_text(json.dumps(index_data))

        components = load_component_index(index_path)

        assert len(components) == 0


class TestUniversalSchemaAdaptation:
    """Tests for adapting components to universal schema."""

    @pytest.fixture
    def uaf_schema(self):
        """Mock UAF framework schema (matches actual framework_registry.json structure)."""
        return {
            "node_schema": {
                "id_field": "service_id",
                "name_field": "service_name",
                "type_field": "classification",
                "functions_field": "functions",
                "interfaces_field": "interfaces",
                "dependencies_field": "dependencies"
            },
            "edge_schema": {
                "id_field": "name",
                "type_field": "interface_type",
                "direction_field": "direction",
                "protocol_field": "protocol",
                "connects_to_field": "connected_services"
            }
        }

    def test_adapt_uaf_component_to_universal(self, uaf_schema):
        """Test adapting UAF component to universal schema."""
        uaf_component = {
            "service_name": "auth_service",
            "service_id": "auth",
            "classification": "core_service",
            "functions": ["authenticate", "authorize"],
            "interfaces": [
                {
                    "name": "user_api",
                    "direction": "provided",
                    "connected_services": ["user_service"]
                }
            ]
        }

        universal_node = adapt_component_to_universal(uaf_component, uaf_schema)

        assert universal_node['node_id'] == "auth"
        assert universal_node['node_name'] == "auth_service"
        assert universal_node['node_type'] == "core_service"
        assert universal_node['functions'] == ["authenticate", "authorize"]
        assert len(universal_node['interfaces']) == 1
        assert universal_node['raw'] == uaf_component  # Preserves original data

    def test_adapt_component_missing_required_fields(self, uaf_schema):
        """Test that adapting component with missing required fields raises ValueError."""
        incomplete_component = {
            "service_name": "test_service"
            # Missing service_id (required field)
        }

        # Function should raise ValueError when required field is missing
        with pytest.raises(ValueError, match="Missing required field 'service_id'"):
            adapt_component_to_universal(incomplete_component, uaf_schema)

    def test_adapt_component_with_no_edges(self, uaf_schema):
        """Test adapting component with no interfaces/edges."""
        component = {
            "service_name": "isolated_service",
            "service_id": "isolated",
            "classification": "utility"
        }

        universal_node = adapt_component_to_universal(component, uaf_schema)

        assert universal_node['node_id'] == "isolated"
        assert universal_node['node_name'] == "isolated_service"
        assert len(universal_node['interfaces']) == 0  # No interfaces provided
        assert universal_node['raw'] == component


class TestErrorHandling:
    """Tests for error handling in various scenarios."""

    def test_load_component_index_invalid_json(self, tmp_path):
        """Test handling of invalid JSON in index file."""
        index_path = tmp_path / "index.json"
        index_path.write_text("{invalid json}")

        # Should raise JSONValidationError from json_utils
        from json_utils import JSONValidationError
        with pytest.raises(JSONValidationError):
            load_component_index(index_path)

    def test_load_component_index_malformed_json(self, tmp_path):
        """Test handling of malformed JSON in component index."""
        index_path = tmp_path / "index.json"
        index_path.write_text("{invalid json}")

        from json_utils import JSONValidationError
        with pytest.raises(JSONValidationError):
            load_component_index(str(index_path))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
