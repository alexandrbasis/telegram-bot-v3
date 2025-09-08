"""
Validation utilities for room/floor search functionality.

Provides validation functions for room numbers and floor identifiers
with comprehensive error handling and input normalization.
"""

import logging
from dataclasses import dataclass
from typing import Any, Optional, Union

logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """
    Result of a validation operation.

    Contains validation status, processed value, and error message.
    """

    is_valid: bool
    value: Optional[Any]
    error_message: Optional[str]


def validate_room_number(room_number: Any) -> ValidationResult:
    """
    Validate room number input.

    Accepts numeric and alphanumeric room identifiers, handles edge cases
    like empty strings, whitespace, and excessively long values.

    Args:
        room_number: Room number to validate (string expected)

    Returns:
        ValidationResult with validation status and processed value
    """
    # Check for None input
    if room_number is None:
        return ValidationResult(False, None, "Room number must be provided")

    # Convert to string and strip whitespace
    room_str = str(room_number).strip()

    # Check for empty or whitespace-only input
    if not room_str:
        return ValidationResult(False, None, "Room number must be provided")

    # Check length constraints (max 20 characters)
    if len(room_str) > 20:
        return ValidationResult(False, None, "Room number too long (max 20 characters)")

    # Valid room number
    logger.debug(f"Validated room number: '{room_str}'")
    return ValidationResult(True, room_str, None)


def validate_floor(floor: Any) -> ValidationResult:
    """
    Validate floor input.

    Accepts integers, numeric strings, and alphabetic identifiers like "Ground".
    Handles edge cases and normalizes input.

    Args:
        floor: Floor identifier to validate (int or string)

    Returns:
        ValidationResult with validation status and processed value
    """
    # Check for None input
    if floor is None:
        return ValidationResult(False, None, "Floor must be provided")

    # Handle integer input (including negative for basements)
    if isinstance(floor, int):
        logger.debug(f"Validated integer floor: {floor}")
        return ValidationResult(True, floor, None)

    # Handle string input
    if isinstance(floor, str):
        floor_str = floor.strip()

        # Check for empty or whitespace-only input
        if not floor_str:
            return ValidationResult(False, None, "Floor must be provided")

        # Check length constraints (max 20 characters)
        if len(floor_str) > 20:
            return ValidationResult(
                False, None, "Floor identifier too long (max 20 characters)"
            )

        # Valid floor identifier
        logger.debug(f"Validated string floor: '{floor_str}'")
        return ValidationResult(True, floor_str, None)

    # Convert other types to string and validate
    floor_str = str(floor).strip()
    if not floor_str:
        return ValidationResult(False, None, "Floor must be provided")

    if len(floor_str) > 20:
        return ValidationResult(
            False, None, "Floor identifier too long (max 20 characters)"
        )

    logger.debug(f"Validated converted floor: '{floor_str}'")
    return ValidationResult(True, floor_str, None)
