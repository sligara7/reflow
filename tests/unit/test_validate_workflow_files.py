"""
Unit tests for validate_workflow_files.py

This is a SAMPLE test demonstrating testing infrastructure.
Full test coverage (80% target) is future work.
"""

import json
import pytest
from pathlib import Path
import sys
import os

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from validate_workflow_files import WorkflowValidator


class TestWorkflowValidator:
    """Test suite for WorkflowValidator class"""

    def test_validator_initialization(self):
        """Test that validator can be initialized"""
        validator = WorkflowValidator()
        assert validator is not None

    def test_valid_json_detection(self, tmp_path):
        """Test that validator accepts valid JSON"""
        # Create a valid workflow file
        workflow_file = tmp_path / "valid_workflow.json"
        valid_workflow = {
            "workflow_metadata": {
                "workflow_id": "test",
                "name": "Test Workflow",
                "version": "1.0.0"
            },
            "workflow_steps": []
        }
        workflow_file.write_text(json.dumps(valid_workflow, indent=2))

        validator = WorkflowValidator()
        result = validator.validate_workflow_file(workflow_file)

        # Should return True for valid workflow
        assert result is True

    def test_invalid_json_detection(self, tmp_path):
        """Test that validator rejects invalid JSON"""
        # Create an invalid JSON file
        workflow_file = tmp_path / "invalid_workflow.json"
        workflow_file.write_text("{invalid json content")

        validator = WorkflowValidator()
        result = validator.validate_workflow_file(workflow_file)

        # Should return False for invalid JSON
        assert result is False

    def test_missing_required_fields(self, tmp_path):
        """Test that validator detects missing required fields"""
        # Create workflow missing required field
        workflow_file = tmp_path / "incomplete_workflow.json"
        incomplete_workflow = {
            "workflow_metadata": {
                "workflow_id": "test"
                # Missing: name, version
            }
        }
        workflow_file.write_text(json.dumps(incomplete_workflow, indent=2))

        validator = WorkflowValidator()
        result = validator.validate_workflow_file(workflow_file)

        # Should detect missing fields
        assert result is False


# Integration test example
class TestWorkflowValidationIntegration:
    """Integration tests using real workflow files"""

    def test_real_workflows_validate(self):
        """Test that actual Reflow workflows validate correctly"""
        workflows_dir = Path(__file__).parent.parent.parent / "workflows"

        if not workflows_dir.exists():
            pytest.skip("Workflows directory not found")

        validator = WorkflowValidator()

        # Test all real workflow files
        workflow_files = list(workflows_dir.glob("*.json"))
        assert len(workflow_files) > 0, "No workflow files found"

        results = {}
        for workflow_file in workflow_files:
            result = validator.validate_workflow_file(workflow_file)
            results[workflow_file.name] = result

        # All workflows should validate
        # (Note: May have warnings, but should be valid)
        # This test may need adjustment based on actual validator behavior
        assert all(results.values()), f"Some workflows failed: {results}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
