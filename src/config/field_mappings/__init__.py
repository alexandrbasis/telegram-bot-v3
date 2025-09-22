"""
Field mapping configurations for multi-table Airtable integration.

This package provides mapping utilities for different Airtable tables,
enabling proper field name translation and validation.
"""

from .bible_readers import BibleReadersFieldMapping
from .roe import ROEFieldMapping

# Re-export the original AirtableFieldMapping for backward compatibility
# Import from the parent level to avoid circular import
import sys
from pathlib import Path

# Add parent directory to path temporarily to import field_mappings.py
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
field_mappings_file = parent_dir / "field_mappings.py"

if field_mappings_file.exists():
    # Use importlib to load the module dynamically
    import importlib.util
    spec = importlib.util.spec_from_file_location("field_mappings_module", field_mappings_file)
    field_mappings_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(field_mappings_module)

    # Extract AirtableFieldMapping class
    AirtableFieldMapping = field_mappings_module.AirtableFieldMapping
else:
    # Fallback if file doesn't exist
    AirtableFieldMapping = None

__all__ = ["BibleReadersFieldMapping", "ROEFieldMapping", "AirtableFieldMapping"]