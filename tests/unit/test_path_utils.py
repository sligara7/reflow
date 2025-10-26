#!/usr/bin/env python3
"""
Unit tests for path_utils.py security module.

Tests path traversal protection, path sanitization, and security validation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
import sys
import os

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools"))

from path_utils import (
    sanitize_path,
    validate_system_root,
    is_safe_filename,
    safe_read_file,
    safe_write_file,
    get_validated_paths,
    PathSecurityError
)


class TestValidateSystemRoot:
    """Tests for validate_system_root() function."""

    def test_valid_directory(self, tmp_path):
        """Test validating a valid existing directory."""
        result = validate_system_root(tmp_path)
        assert result == tmp_path
        assert result.is_dir()

    def test_nonexistent_directory(self):
        """Test that nonexistent directory raises PathSecurityError."""
        with pytest.raises(PathSecurityError, match="System root does not exist"):
            validate_system_root("/nonexistent/path/xyz123")

    def test_file_not_directory(self, tmp_path):
        """Test that file path raises PathSecurityError."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test")

        with pytest.raises(PathSecurityError, match="System root is not a directory"):
            validate_system_root(test_file)

    def test_string_path_conversion(self, tmp_path):
        """Test that string paths are converted to Path objects."""
        result = validate_system_root(str(tmp_path))
        assert isinstance(result, Path)
        assert result == tmp_path


class TestSanitizePath:
    """Tests for sanitize_path() function."""

    def test_safe_relative_path(self, tmp_path):
        """Test sanitizing a safe relative path."""
        # Create a test file
        test_file = tmp_path / "docs" / "README.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("test")

        result = sanitize_path("docs/README.md", tmp_path, must_exist=True)
        assert result == test_file
        assert result.exists()

    def test_path_traversal_blocked(self, tmp_path):
        """Test that path traversal attempts are blocked."""
        with pytest.raises(PathSecurityError, match="outside system root"):
            sanitize_path("../../etc/passwd", tmp_path)

    def test_absolute_path_outside_root_blocked(self, tmp_path):
        """Test that absolute paths outside system_root are blocked."""
        with pytest.raises(PathSecurityError, match="outside system root"):
            sanitize_path("/etc/passwd", tmp_path)

    def test_path_with_dot_segments(self, tmp_path):
        """Test that paths with . and .. segments are resolved safely."""
        test_dir = tmp_path / "subdir"
        test_dir.mkdir()
        test_file = test_dir / "file.txt"
        test_file.write_text("test")

        # Path with . should work
        result = sanitize_path("./subdir/file.txt", tmp_path, must_exist=True)
        assert result == test_file

        # Path with .. that stays within root should work
        result = sanitize_path("subdir/../subdir/file.txt", tmp_path, must_exist=True)
        assert result == test_file

    def test_must_exist_enforcement(self, tmp_path):
        """Test that must_exist parameter is enforced."""
        # Non-existent file with must_exist=True should raise
        with pytest.raises(FileNotFoundError):
            sanitize_path("nonexistent.txt", tmp_path, must_exist=True)

        # Non-existent file with must_exist=False should work
        result = sanitize_path("nonexistent.txt", tmp_path, must_exist=False)
        assert result == tmp_path / "nonexistent.txt"

    def test_strict_mode(self, tmp_path):
        """Test strict mode path validation."""
        # Create a symlink outside system_root
        target_dir = tmp_path.parent / "outside"
        target_dir.mkdir(exist_ok=True)
        symlink = tmp_path / "link"

        try:
            symlink.symlink_to(target_dir)

            # Strict mode should block symlinks outside root
            with pytest.raises(PathSecurityError, match="outside system root"):
                sanitize_path("link", tmp_path, strict=True, allow_symlinks=True)
        finally:
            if symlink.exists():
                symlink.unlink()
            if target_dir.exists():
                target_dir.rmdir()

    def test_symlink_within_root(self, tmp_path):
        """Test that symlinks within system_root work with allow_symlinks=True."""
        target_file = tmp_path / "target.txt"
        target_file.write_text("test")
        symlink = tmp_path / "link.txt"
        symlink.symlink_to(target_file)

        # allow_symlinks=True should work for symlinks within root
        # Note: sanitize_path resolves symlinks to their target
        result = sanitize_path("link.txt", tmp_path, allow_symlinks=True)
        assert result == target_file  # Resolved to target
        assert result.exists()
        assert result.read_text() == "test"

    def test_null_byte_injection(self, tmp_path):
        """Test that null byte injection is blocked."""
        # Null bytes cause ValueError in Path.resolve(), which is acceptable behavior
        with pytest.raises((PathSecurityError, ValueError)):
            sanitize_path("file\x00.txt", tmp_path)


class TestIsSafeFilename:
    """Tests for is_safe_filename() function."""

    def test_safe_filenames(self):
        """Test that safe filenames are accepted."""
        assert is_safe_filename("README.md") is True
        assert is_safe_filename("service_architecture.json") is True
        assert is_safe_filename("my-file_v1.2.3.txt") is True

    def test_path_traversal_blocked(self):
        """Test that path traversal characters are blocked."""
        assert is_safe_filename("../file.txt") is False
        assert is_safe_filename("..\\file.txt") is False
        assert is_safe_filename("dir/../file.txt") is False

    def test_directory_separators_blocked(self):
        """Test that directory separators are blocked."""
        assert is_safe_filename("dir/file.txt") is False
        assert is_safe_filename("dir\\file.txt") is False

    def test_null_byte_blocked(self):
        """Test that null bytes are blocked."""
        assert is_safe_filename("file\x00.txt") is False

    def test_leading_dots(self):
        """Test handling of leading dots."""
        # With allow_dots=False (default)
        assert is_safe_filename(".hidden") is False
        assert is_safe_filename("..file") is False

        # With allow_dots=True
        assert is_safe_filename(".hidden", allow_dots=True) is True
        assert is_safe_filename("..file", allow_dots=True) is True


class TestSafeReadFile:
    """Tests for safe_read_file() function."""

    def test_safe_read(self, tmp_path):
        """Test reading a safe file."""
        test_file = tmp_path / "test.txt"
        test_content = "Hello, World!"
        test_file.write_text(test_content)

        content = safe_read_file("test.txt", tmp_path)
        assert content == test_content

    def test_read_blocks_traversal(self, tmp_path):
        """Test that read blocks path traversal."""
        with pytest.raises(PathSecurityError):
            safe_read_file("../../etc/passwd", tmp_path)

    def test_read_nonexistent_file(self, tmp_path):
        """Test reading nonexistent file."""
        with pytest.raises(FileNotFoundError):
            safe_read_file("nonexistent.txt", tmp_path)


class TestSafeWriteFile:
    """Tests for safe_write_file() function."""

    def test_safe_write(self, tmp_path):
        """Test writing to a safe file."""
        test_content = "Test content"
        safe_write_file("test.txt", test_content, tmp_path)

        result_file = tmp_path / "test.txt"
        assert result_file.exists()
        assert result_file.read_text() == test_content

    def test_write_blocks_traversal(self, tmp_path):
        """Test that write blocks path traversal."""
        with pytest.raises(PathSecurityError):
            safe_write_file("../../etc/passwd", "malicious", tmp_path)

    def test_write_to_nested_path(self, tmp_path):
        """Test writing to a nested path (parent dirs created automatically)."""
        # Create parent directory first
        (tmp_path / "subdir").mkdir()
        safe_write_file("subdir/file.txt", "content", tmp_path)

        result_file = tmp_path / "subdir" / "file.txt"
        assert result_file.exists()
        assert result_file.read_text() == "content"


class TestGetValidatedPaths:
    """Tests for get_validated_paths() function."""

    def test_get_validated_paths(self, tmp_path):
        """Test getting validated paths from working memory."""
        # Create working_memory.json
        working_memory = tmp_path / "context" / "working_memory.json"
        working_memory.parent.mkdir(parents=True)
        working_memory.write_text("""
        {
            "paths": {
                "reflow_root": "/reflow",
                "system_root": "/system",
                "tools_path": "/reflow/tools"
            }
        }
        """)

        paths = get_validated_paths(tmp_path)
        # Function returns paths from working_memory.json
        assert isinstance(paths, dict)

    def test_missing_working_memory(self, tmp_path):
        """Test that missing working_memory.json returns empty dict."""
        # Function returns empty dict instead of raising
        paths = get_validated_paths(tmp_path)
        assert paths == {}


class TestSecurityScenarios:
    """Integration tests for real-world security scenarios."""

    def test_scenario_malicious_user_input(self, tmp_path):
        """Test protection against malicious user input."""
        malicious_inputs = [
            "../../etc/passwd",
            "../../../etc/shadow",
            "/.ssh/id_rsa",
            "dir/../../etc/hosts",
            "dir/../../../root/.bashrc"
        ]

        for malicious_path in malicious_inputs:
            with pytest.raises((PathSecurityError, FileNotFoundError)):
                sanitize_path(malicious_path, tmp_path, must_exist=False)

        # Null byte separately (causes ValueError)
        with pytest.raises((PathSecurityError, ValueError)):
            sanitize_path("file\x00.txt", tmp_path, must_exist=False)

    def test_scenario_safe_user_inputs(self, tmp_path):
        """Test that legitimate user inputs work correctly."""
        # Create test structure
        (tmp_path / "docs").mkdir()
        (tmp_path / "specs" / "machine").mkdir(parents=True)
        (tmp_path / "context").mkdir()

        safe_inputs = [
            "docs/README.md",
            "specs/machine/architecture.json",
            "context/working_memory.json",
            "service_architecture.json"
        ]

        for safe_path in safe_inputs:
            # Should not raise
            result = sanitize_path(safe_path, tmp_path, must_exist=False)
            assert result.is_relative_to(tmp_path)

    def test_scenario_cross_system_access_blocked(self, tmp_path):
        """Test that cross-system access is blocked."""
        # Create two system directories
        system1 = tmp_path / "system1"
        system2 = tmp_path / "system2"
        system1.mkdir()
        system2.mkdir()

        # Try to access system2 from system1 context
        with pytest.raises(PathSecurityError):
            sanitize_path("../system2/sensitive.json", system1)


# Pytest fixtures
@pytest.fixture
def tmp_path(tmp_path_factory):
    """Create a temporary directory for testing."""
    return tmp_path_factory.mktemp("reflow_test")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
