#!/usr/bin/env python3
"""
Unit tests for json_utils.py

Tests JSON validation utilities with syntax errors, schema validation, and error messages.
"""

import pytest
import json
from pathlib import Path
import sys

# Add tools directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from json_utils import (
    safe_load_json,
    safe_load_json_with_schema_path,
    validate_required_fields,
    validate_json_type,
    JSONValidationError
)

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False


class TestSafeLoadJSON:
    """Tests for safe_load_json() function."""

    def test_load_valid_json(self, tmp_path):
        """Test loading valid JSON file."""
        json_file = tmp_path / "valid.json"
        test_data = {"key": "value", "number": 42}
        json_file.write_text(json.dumps(test_data))

        result = safe_load_json(json_file)
        assert result == test_data

    def test_file_not_found(self, tmp_path):
        """Test error when file doesn't exist."""
        nonexistent = tmp_path / "nonexistent.json"

        with pytest.raises(FileNotFoundError, match="not found"):
            safe_load_json(nonexistent, file_type_description="test file")

    def test_invalid_json_syntax(self, tmp_path):
        """Test error on invalid JSON syntax."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text('{"key": "value"')  # Missing closing brace

        with pytest.raises(JSONValidationError, match="Invalid JSON syntax"):
            safe_load_json(invalid_json)

    def test_json_syntax_error_helpful_message(self, tmp_path):
        """Test that syntax errors include helpful troubleshooting tips."""
        invalid_json = tmp_path / "invalid.json"
        invalid_json.write_text('{"key": "value",}')  # Trailing comma

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(invalid_json)

        error_msg = str(exc_info.value)
        assert "Common issues:" in error_msg
        assert "Trailing comma" in error_msg

    def test_unicode_decode_error(self, tmp_path):
        """Test error on file encoding issues."""
        binary_file = tmp_path / "binary.json"
        binary_file.write_bytes(b'\xff\xfe')  # Invalid UTF-8

        with pytest.raises(JSONValidationError, match="encoding error"):
            safe_load_json(binary_file)

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
    def test_schema_validation_pass(self, tmp_path):
        """Test successful schema validation."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"name": "test", "version": "1.0.0"}')

        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }

        result = safe_load_json(json_file, schema=schema)
        assert result["name"] == "test"

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
    def test_schema_validation_fail(self, tmp_path):
        """Test schema validation failure."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"name": "test"}')  # Missing required field

        schema = {
            "type": "object",
            "required": ["name", "version"],
            "properties": {
                "name": {"type": "string"},
                "version": {"type": "string"}
            }
        }

        with pytest.raises(JSONValidationError, match="Schema validation failed"):
            safe_load_json(json_file, schema=schema)

    @pytest.mark.skipif(not JSONSCHEMA_AVAILABLE, reason="jsonschema not installed")
    def test_schema_validation_error_path(self, tmp_path):
        """Test that schema validation errors include field path."""
        json_file = tmp_path / "data.json"
        json_file.write_text('{"metadata": {"name": 123}}')  # Wrong type

        schema = {
            "type": "object",
            "properties": {
                "metadata": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"}
                    }
                }
            }
        }

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file, schema=schema)

        error_msg = str(exc_info.value)
        assert "metadata.name" in error_msg

    def test_file_type_description_in_errors(self, tmp_path):
        """Test that file_type_description appears in error messages."""
        json_file = tmp_path / "workflow.json"
        json_file.write_text('{invalid}')

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file, file_type_description="workflow file")

        assert "workflow file" in str(exc_info.value).lower()


class TestSafeLoadJSONWithSchemaPath:
    """Tests for safe_load_json_with_schema_path() function."""

    def test_load_with_schema_file(self, tmp_path):
        """Test loading JSON with schema from file."""
        # Create schema file
        schema_file = tmp_path / "schema.json"
        schema = {
            "type": "object",
            "required": ["name"],
            "properties": {"name": {"type": "string"}}
        }
        schema_file.write_text(json.dumps(schema))

        # Create data file
        data_file = tmp_path / "data.json"
        data_file.write_text('{"name": "test"}')

        result = safe_load_json_with_schema_path(
            data_file,
            schema_path=schema_file
        )
        assert result["name"] == "test"

    def test_missing_schema_file_warning(self, tmp_path, capsys):
        """Test that missing schema file prints warning but continues."""
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "value"}')

        nonexistent_schema = tmp_path / "nonexistent_schema.json"

        result = safe_load_json_with_schema_path(
            data_file,
            schema_path=nonexistent_schema
        )

        # Should still load data
        assert result["key"] == "value"

        # Should print warning
        captured = capsys.readouterr()
        assert "Schema file not found" in captured.out

    def test_invalid_schema_file_warning(self, tmp_path, capsys):
        """Test that invalid schema file prints warning but continues."""
        # Create invalid schema file
        schema_file = tmp_path / "schema.json"
        schema_file.write_text('{invalid json}')

        # Create valid data file
        data_file = tmp_path / "data.json"
        data_file.write_text('{"key": "value"}')

        result = safe_load_json_with_schema_path(
            data_file,
            schema_path=schema_file
        )

        # Should still load data
        assert result["key"] == "value"

        # Should print warning
        captured = capsys.readouterr()
        assert "Invalid JSON in schema file" in captured.out


class TestValidateRequiredFields:
    """Tests for validate_required_fields() function."""

    def test_all_fields_present(self):
        """Test validation passes when all fields present."""
        data = {"field1": "value1", "field2": "value2", "field3": "value3"}
        required = ["field1", "field2"]

        # Should not raise
        validate_required_fields(data, required)

    def test_missing_fields(self):
        """Test validation fails when fields missing."""
        data = {"field1": "value1"}
        required = ["field1", "field2", "field3"]

        with pytest.raises(JSONValidationError, match="Missing required fields"):
            validate_required_fields(data, required)

    def test_missing_fields_lists_all_missing(self):
        """Test error message lists all missing fields."""
        data = {"field1": "value1"}
        required = ["field1", "field2", "field3"]

        with pytest.raises(JSONValidationError) as exc_info:
            validate_required_fields(data, required, file_description="test file")

        error_msg = str(exc_info.value)
        assert "field2" in error_msg
        assert "field3" in error_msg
        assert "test file" in error_msg


class TestValidateJSONType:
    """Tests for validate_json_type() function."""

    def test_correct_type_dict(self):
        """Test validation passes for correct dict type."""
        data = {"key": "value"}
        validate_json_type(data, dict)

    def test_correct_type_list(self):
        """Test validation passes for correct list type."""
        data = ["item1", "item2"]
        validate_json_type(data, list)

    def test_correct_type_string(self):
        """Test validation passes for correct string type."""
        data = "test string"
        validate_json_type(data, str)

    def test_wrong_type(self):
        """Test validation fails for wrong type."""
        data = "not a dict"

        with pytest.raises(JSONValidationError, match="Type error"):
            validate_json_type(data, dict, field_name="test_field")

    def test_type_error_message_details(self):
        """Test type error message includes expected and actual types."""
        data = 123

        with pytest.raises(JSONValidationError) as exc_info:
            validate_json_type(data, str, field_name="test_field", file_description="test file")

        error_msg = str(exc_info.value)
        assert "Expected: str" in error_msg
        assert "Got: int" in error_msg
        assert "test_field" in error_msg


class TestMalformedJSONScenarios:
    """Integration tests for various malformed JSON scenarios."""

    def test_trailing_comma_in_object(self, tmp_path):
        """Test helpful error for trailing comma in object."""
        json_file = tmp_path / "trailing_comma.json"
        json_file.write_text('{"key1": "value1", "key2": "value2",}')

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file)

        assert "Trailing comma" in str(exc_info.value)

    def test_single_quotes_instead_of_double(self, tmp_path):
        """Test error for single quotes (common mistake)."""
        json_file = tmp_path / "single_quotes.json"
        json_file.write_text("{'key': 'value'}")

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file)

        error_msg = str(exc_info.value)
        assert "Single quotes instead of double quotes" in error_msg

    def test_unquoted_keys(self, tmp_path):
        """Test error for unquoted object keys."""
        json_file = tmp_path / "unquoted.json"
        json_file.write_text('{key: "value"}')

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file)

        error_msg = str(exc_info.value)
        assert "Unquoted strings or keys" in error_msg

    def test_missing_closing_bracket(self, tmp_path):
        """Test error for missing closing bracket."""
        json_file = tmp_path / "unclosed.json"
        json_file.write_text('{"key": ["value1", "value2"')

        with pytest.raises(JSONValidationError) as exc_info:
            safe_load_json(json_file)

        error_msg = str(exc_info.value)
        assert "Missing closing bracket/brace" in error_msg


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
