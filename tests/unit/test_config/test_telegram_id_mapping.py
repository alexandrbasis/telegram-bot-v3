"""
Tests for Telegram ID field mapping addition.

This test ensures that the missing "Telegram ID" field is properly mapped
in the field_mappings.py configuration.
"""

import pytest

from src.config.field_mappings import AirtableFieldMapping


class TestTelegramIDMapping:
    """Test suite for Telegram ID field mapping."""

    def test_telegram_id_field_mapping_exists(self):
        """Test that Telegram ID field has proper mapping in AIRTABLE_FIELD_IDS."""
        # RED phase - this test will fail until we add the mapping

        # Test that Telegram ID field mapping exists
        field_id = AirtableFieldMapping.get_field_id("TelegramID")
        assert (
            field_id is not None
        ), "Telegram ID field mapping should exist in AIRTABLE_FIELD_IDS"

        # Verify it's a valid field ID format (starts with 'fld' and has correct length)
        assert field_id.startswith(
            "fld"
        ), f"Field ID should start with 'fld', got: {field_id}"
        assert (
            len(field_id) == 17
        ), f"Field ID should be 17 characters long, got: {len(field_id)}"

    def test_telegram_id_python_to_airtable_mapping(self):
        """Test Python field name to Airtable field name mapping for Telegram ID."""
        # RED phase - this test will fail until we add the mapping

        airtable_field = AirtableFieldMapping.get_airtable_field_name("telegram_id")
        assert (
            airtable_field == "TelegramID"
        ), f"Expected 'TelegramID', got: {airtable_field}"

    def test_telegram_id_airtable_to_python_mapping(self):
        """Test Airtable field name to Python field name mapping for Telegram ID."""
        # RED phase - this test will fail until we add the mapping

        python_field = AirtableFieldMapping.get_python_field_name("TelegramID")
        assert (
            python_field == "telegram_id"
        ), f"Expected 'telegram_id', got: {python_field}"

    def test_telegram_id_in_field_lists(self):
        """Test that Telegram ID appears in field lists."""
        # RED phase - this test will fail until we add the mapping

        airtable_fields = AirtableFieldMapping.get_all_airtable_fields()
        python_fields = AirtableFieldMapping.get_all_python_fields()

        assert (
            "TelegramID" in airtable_fields
        ), "TelegramID should be in Airtable fields list"
        assert (
            "telegram_id" in python_fields
        ), "telegram_id should be in Python fields list"

    def test_telegram_id_field_type(self):
        """Test that Telegram ID field has correct field type."""
        # RED phase - this test will fail until we add the field type mapping

        from src.config.field_mappings import FieldType

        field_type = AirtableFieldMapping.get_field_type("TelegramID")
        assert (
            field_type == FieldType.TEXT
        ), f"Telegram ID should be TEXT type, got: {field_type}"

    def test_telegram_id_bidirectional_consistency(self):
        """Test bidirectional mapping consistency for Telegram ID."""
        # RED phase - this test will fail until we add the mapping

        # Python to Airtable and back
        airtable_field = AirtableFieldMapping.get_airtable_field_name("telegram_id")
        python_field = AirtableFieldMapping.get_python_field_name(airtable_field)
        assert (
            python_field == "telegram_id"
        ), "Bidirectional mapping should be consistent"

        # Airtable to Python and back
        python_field = AirtableFieldMapping.get_python_field_name("TelegramID")
        airtable_field = AirtableFieldMapping.get_airtable_field_name(python_field)
        assert (
            airtable_field == "TelegramID"
        ), "Bidirectional mapping should be consistent"
