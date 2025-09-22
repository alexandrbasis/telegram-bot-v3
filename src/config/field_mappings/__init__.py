"""
Field mapping configurations for multi-table Airtable integration.

This package provides mapping utilities for different Airtable tables,
enabling proper field name translation and validation.
"""

from .bible_readers import BibleReadersFieldMapping
from .roe import ROEFieldMapping

__all__ = ["BibleReadersFieldMapping", "ROEFieldMapping"]