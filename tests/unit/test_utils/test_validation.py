"""
Unit tests for validation utilities.

Tests validation helpers for room/floor input handling and error cases.
"""

import pytest

from src.utils.validation import (ValidationResult, validate_floor,
                                  validate_room_number)


class TestRoomNumberValidation:
    """Test room number validation functionality."""

    def test_validate_room_number_valid_numeric(self):
        """Test validation of valid numeric room numbers."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("205")

        assert result.is_valid is True
        assert result.value == "205"
        assert result.error_message is None

    def test_validate_room_number_valid_alphanumeric(self):
        """Test validation of valid alphanumeric room numbers."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("G01")

        assert result.is_valid is True
        assert result.value == "G01"
        assert result.error_message is None

    def test_validate_room_number_empty_string(self):
        """Test validation fails for empty string."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("")

        assert result.is_valid is False
        assert result.value is None
        assert "Room number must be provided" in result.error_message

    def test_validate_room_number_none(self):
        """Test validation fails for None input."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number(None)

        assert result.is_valid is False
        assert result.value is None
        assert "Room number must be provided" in result.error_message

    def test_validate_room_number_whitespace_only(self):
        """Test validation fails for whitespace-only input."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("   ")

        assert result.is_valid is False
        assert result.value is None
        assert "Room number must be provided" in result.error_message

    def test_validate_room_number_too_long(self):
        """Test validation fails for excessively long room numbers."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("A" * 21)  # 21 characters

        assert result.is_valid is False
        assert result.value is None
        assert "Room number too long" in result.error_message

    def test_validate_room_number_strips_whitespace(self):
        """Test validation strips leading/trailing whitespace."""
        # This test should FAIL - function doesn't exist yet
        result = validate_room_number("  205  ")

        assert result.is_valid is True
        assert result.value == "205"
        assert result.error_message is None


class TestFloorValidation:
    """Test floor validation functionality."""

    def test_validate_floor_valid_integer(self):
        """Test validation of valid integer floor."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor(2)

        assert result.is_valid is True
        assert result.value == 2
        assert result.error_message is None

    def test_validate_floor_valid_string_numeric(self):
        """Test validation of valid numeric string floor."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("3")

        assert result.is_valid is True
        assert result.value == "3"
        assert result.error_message is None

    def test_validate_floor_valid_string_alpha(self):
        """Test validation of valid alphabetic floor (e.g., 'Ground')."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("Ground")

        assert result.is_valid is True
        assert result.value == "Ground"
        assert result.error_message is None

    def test_validate_floor_negative_integer(self):
        """Test validation allows negative floors (basements)."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor(-1)

        assert result.is_valid is True
        assert result.value == -1
        assert result.error_message is None

    def test_validate_floor_zero(self):
        """Test validation allows zero floor."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor(0)

        assert result.is_valid is True
        assert result.value == 0
        assert result.error_message is None

    def test_validate_floor_none(self):
        """Test validation fails for None input."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor(None)

        assert result.is_valid is False
        assert result.value is None
        assert "Floor must be provided" in result.error_message

    def test_validate_floor_empty_string(self):
        """Test validation fails for empty string."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("")

        assert result.is_valid is False
        assert result.value is None
        assert "Floor must be provided" in result.error_message

    def test_validate_floor_whitespace_only(self):
        """Test validation fails for whitespace-only string."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("   ")

        assert result.is_valid is False
        assert result.value is None
        assert "Floor must be provided" in result.error_message

    def test_validate_floor_too_long_string(self):
        """Test validation fails for excessively long floor strings."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("A" * 21)  # 21 characters

        assert result.is_valid is False
        assert result.value is None
        assert "Floor identifier too long" in result.error_message

    def test_validate_floor_strips_whitespace(self):
        """Test validation strips leading/trailing whitespace from strings."""
        # This test should FAIL - function doesn't exist yet
        result = validate_floor("  Ground  ")

        assert result.is_valid is True
        assert result.value == "Ground"
        assert result.error_message is None


class TestValidationResult:
    """Test ValidationResult dataclass."""

    def test_validation_result_creation(self):
        """Test creating ValidationResult instances."""
        # This test should FAIL - class doesn't exist yet
        result = ValidationResult(True, "test", None)

        assert result.is_valid is True
        assert result.value == "test"
        assert result.error_message is None

    def test_validation_result_invalid(self):
        """Test creating invalid ValidationResult."""
        # This test should FAIL - class doesn't exist yet
        result = ValidationResult(False, None, "Error message")

        assert result.is_valid is False
        assert result.value is None
        assert result.error_message == "Error message"
