"""Utility helpers for building Airtable formulas safely."""

from enum import Enum
from typing import Any, Tuple


def escape_formula_value(value: str) -> str:
    """Escape characters in a string for safe use inside Airtable formulas."""
    return value.replace("'", "''")


def prepare_formula_value(value: Any) -> Tuple[bool, Any]:
    """Normalize formula values and indicate whether quoting is required."""
    if isinstance(value, Enum):
        value = value.value
    if isinstance(value, str):
        return True, escape_formula_value(value)
    return False, value
