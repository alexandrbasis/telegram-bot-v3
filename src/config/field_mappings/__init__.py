"""
Field mapping configurations for multi-table Airtable integration.

This package provides mapping utilities for different Airtable tables,
enabling proper field name translation and validation.
"""

import importlib.util

# Re-export all symbols from the original field_mappings.py for backward compatibility
# Import from the parent level to avoid circular import
from pathlib import Path

from .bible_readers import BibleReadersFieldMapping
from .roe import ROEFieldMapping

# Add parent directory to path temporarily to import field_mappings.py
current_dir = Path(__file__).parent
parent_dir = current_dir.parent
field_mappings_file = parent_dir / "field_mappings.py"

if field_mappings_file.exists():
    # Use importlib to load the module dynamically
    spec = importlib.util.spec_from_file_location(
        "field_mappings_module", field_mappings_file
    )
    if spec is not None and spec.loader is not None:
        field_mappings_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(field_mappings_module)

        # Extract all required symbols for backward compatibility
        AirtableFieldMapping = field_mappings_module.AirtableFieldMapping
        FieldType = field_mappings_module.FieldType
        SearchFieldMapping = field_mappings_module.SearchFieldMapping
        field_mapping = field_mappings_module.field_mapping
        search_mapping = field_mappings_module.search_mapping
    else:
        # Fallback if spec or loader is None
        AirtableFieldMapping = None
        FieldType = None
        SearchFieldMapping = None
        field_mapping = None
        search_mapping = None
else:
    # Fallback if file doesn't exist
    AirtableFieldMapping = None
    FieldType = None
    SearchFieldMapping = None
    field_mapping = None
    search_mapping = None

__all__ = [
    "BibleReadersFieldMapping",
    "ROEFieldMapping",
    "AirtableFieldMapping",
    "FieldType",
    "SearchFieldMapping",
    "field_mapping",
    "search_mapping",
]
