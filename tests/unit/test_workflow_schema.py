#!/usr/bin/env python3
"""
Unit tests for workflow schema validation.

Tests JSON schema validation for Reflow workflow files.
"""

import pytest
import json
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    pytest.skip("jsonschema not installed", allow_module_level=True)


@pytest.fixture
def workflow_schema():
    """Load the workflow schema."""
    schema_path = Path(__file__).parent.parent.parent / "schemas" / "workflow_schema.json"
    with open(schema_path) as f:
        return json.load(f)


@pytest.fixture
def minimal_valid_workflow():
    """Create a minimal valid workflow for testing."""
    return {
        "workflow_metadata": {
            "workflow_id": "00-test",
            "name": "Test Workflow",
            "version": "1.0.0",
            "description": "A test workflow"
        },
        "workflow_steps": [
            {
                "step_id": "T-01",
                "name": "Test Step",
                "description": "A test step",
                "phase": "testing"
            }
        ]
    }


class TestWorkflowSchema:
    """Tests for workflow schema validation."""

    def test_schema_is_valid_json_schema(self, workflow_schema):
        """Test that the schema itself is valid JSON Schema."""
        # This will raise an exception if schema is invalid
        jsonschema.Draft7Validator.check_schema(workflow_schema)

    def test_minimal_valid_workflow_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that a minimal valid workflow passes validation."""
        # Should not raise any exception
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_missing_workflow_metadata_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that missing workflow_metadata fails validation."""
        del minimal_valid_workflow["workflow_metadata"]

        with pytest.raises(jsonschema.ValidationError, match="'workflow_metadata' is a required property"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_missing_workflow_steps_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that missing workflow_steps fails validation."""
        del minimal_valid_workflow["workflow_steps"]

        with pytest.raises(jsonschema.ValidationError, match="'workflow_steps' is a required property"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_invalid_workflow_id_pattern_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that invalid workflow_id pattern fails validation."""
        # Single digit instead of two digits
        minimal_valid_workflow["workflow_metadata"]["workflow_id"] = "1-test"

        with pytest.raises(jsonschema.ValidationError, match="does not match"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_valid_workflow_id_patterns_pass(self, workflow_schema, minimal_valid_workflow):
        """Test that various valid workflow_id patterns pass."""
        valid_ids = [
            "00-setup",
            "01-systems_engineering",
            "99-test_workflow",
            "feature_update"
        ]

        for workflow_id in valid_ids:
            minimal_valid_workflow["workflow_metadata"]["workflow_id"] = workflow_id
            # Should not raise
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_invalid_version_format_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that invalid version format fails validation."""
        minimal_valid_workflow["workflow_metadata"]["version"] = "1.0"  # Missing patch

        with pytest.raises(jsonschema.ValidationError, match="does not match"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_valid_version_formats_pass(self, workflow_schema, minimal_valid_workflow):
        """Test that various valid version formats pass."""
        valid_versions = ["1.0.0", "1.2.3", "10.20.30"]

        for version in valid_versions:
            minimal_valid_workflow["workflow_metadata"]["version"] = version
            # Should not raise
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_empty_workflow_steps_array_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that empty workflow_steps array fails validation."""
        minimal_valid_workflow["workflow_steps"] = []

        with pytest.raises(jsonschema.ValidationError, match="should be non-empty"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_step_missing_required_field_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that step missing required field fails validation."""
        # Remove required field from step
        del minimal_valid_workflow["workflow_steps"][0]["step_id"]

        with pytest.raises(jsonschema.ValidationError, match="'step_id' is a required property"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)


class TestGateValidation:
    """Tests for gate validation within workflow steps."""

    def test_gate_with_all_required_fields_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that gate with all required fields passes."""
        minimal_valid_workflow["workflow_steps"][0]["gates"] = [
            {
                "gate_id": "G-T-01",
                "name": "Test Gate",
                "checks": ["Test check 1", "Test check 2"]
            }
        ]

        # Should not raise (blocking is optional)
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_gate_with_blocking_field_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that gate with optional blocking field passes."""
        minimal_valid_workflow["workflow_steps"][0]["gates"] = [
            {
                "gate_id": "G-T-01",
                "name": "Test Gate",
                "checks": ["Test check"],
                "blocking": True
            }
        ]

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_gate_missing_gate_id_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that gate missing gate_id fails."""
        minimal_valid_workflow["workflow_steps"][0]["gates"] = [
            {
                "name": "Test Gate",
                "checks": ["Test check"]
            }
        ]

        with pytest.raises(jsonschema.ValidationError, match="'gate_id' is a required property"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_gate_with_empty_checks_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that gate with empty checks array fails."""
        minimal_valid_workflow["workflow_steps"][0]["gates"] = [
            {
                "gate_id": "G-T-01",
                "name": "Test Gate",
                "checks": []  # Empty array
            }
        ]

        with pytest.raises(jsonschema.ValidationError, match="should be non-empty"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_gate_with_enforcement_tiers_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that gate with two-tier enforcement passes."""
        minimal_valid_workflow["workflow_steps"][0]["gates"] = [
            {
                "gate_id": "G-T-01",
                "name": "Test Gate",
                "checks": ["Check 1"],
                "enforcement": {
                    "tier_1_critical": ["Critical check"],
                    "tier_2_important": ["Important check"]
                }
            }
        ]

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)


class TestActionValidation:
    """Tests for action validation within workflow steps."""

    def test_action_with_required_fields_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that action with required fields passes."""
        minimal_valid_workflow["workflow_steps"][0]["actions"] = [
            {
                "action_id": "T-01-A01",
                "description": "Test action"
            }
        ]

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_action_success_criteria_as_string_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that success_criteria as string passes."""
        minimal_valid_workflow["workflow_steps"][0]["actions"] = [
            {
                "action_id": "T-01-A01",
                "description": "Test action",
                "success_criteria": "Action completes successfully"
            }
        ]

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_action_success_criteria_as_array_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that success_criteria as array passes."""
        minimal_valid_workflow["workflow_steps"][0]["actions"] = [
            {
                "action_id": "T-01-A01",
                "description": "Test action",
                "success_criteria": [
                    "Criterion 1 met",
                    "Criterion 2 met",
                    "Criterion 3 met"
                ]
            }
        ]

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_action_missing_description_fails(self, workflow_schema, minimal_valid_workflow):
        """Test that action missing description fails."""
        minimal_valid_workflow["workflow_steps"][0]["actions"] = [
            {
                "action_id": "T-01-A01"
                # Missing description
            }
        ]

        with pytest.raises(jsonschema.ValidationError, match="'description' is a required property"):
            jsonschema.validate(minimal_valid_workflow, workflow_schema)


class TestCompletionValidation:
    """Tests for completion section validation."""

    def test_completion_with_next_workflow_string_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that completion with next_workflow as string passes."""
        minimal_valid_workflow["completion"] = {
            "next_workflow": "01-systems_engineering"
        }

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_completion_with_next_workflow_null_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that completion with next_workflow as null passes."""
        minimal_valid_workflow["completion"] = {
            "next_workflow": None
        }

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)

    def test_completion_with_outputs_required_passes(self, workflow_schema, minimal_valid_workflow):
        """Test that completion with outputs_required passes."""
        minimal_valid_workflow["completion"] = {
            "outputs_required": [
                "context/working_memory.json",
                "specs/machine/service_architecture.json"
            ]
        }

        # Should not raise
        jsonschema.validate(minimal_valid_workflow, workflow_schema)


class TestRealWorldWorkflows:
    """Tests validating actual Reflow workflow files."""

    @pytest.fixture
    def reflow_root(self):
        """Get the reflow root directory."""
        return Path(__file__).parent.parent.parent

    def test_all_workflows_validate_against_schema(self, workflow_schema, reflow_root):
        """Test that all existing workflow files validate against schema."""
        workflows_dir = reflow_root / "workflows"
        workflow_files = list(workflows_dir.glob("*.json"))

        assert len(workflow_files) == 6, f"Expected 6 workflow files, found {len(workflow_files)}"

        errors = []
        for workflow_file in sorted(workflow_files):
            try:
                with open(workflow_file) as f:
                    workflow = json.load(f)
                jsonschema.validate(workflow, workflow_schema)
            except jsonschema.ValidationError as e:
                errors.append(f"{workflow_file.name}: {e.message}")

        # All workflows should validate without errors
        assert len(errors) == 0, f"Workflow validation errors:\n" + "\n".join(errors)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
