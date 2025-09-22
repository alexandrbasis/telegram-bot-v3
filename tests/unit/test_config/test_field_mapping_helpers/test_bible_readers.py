"""
Test cases for BibleReaders field mapping configuration.

This module tests the field mapping functionality for the BibleReaders table,
ensuring proper translation between Python model fields and Airtable fields.
"""

import pytest

from src.config.field_mappings.bible_readers import BibleReadersFieldMapping


class TestBibleReadersFieldMapping:
    """Test cases for BibleReadersFieldMapping class."""

    def test_airtable_field_ids_exist(self):
        """Test that all required Airtable field IDs are defined."""
        expected_fields = {
            "Where",
            "Participants",
            "When",
            "Bible",
            "Church",
            "RoomNumber",
            "id",
        }

        actual_fields = set(BibleReadersFieldMapping.AIRTABLE_FIELD_IDS.keys())
        assert actual_fields == expected_fields

        # Verify field IDs are non-empty strings
        for field_name, field_id in BibleReadersFieldMapping.AIRTABLE_FIELD_IDS.items():
            assert isinstance(field_id, str)
            assert len(field_id) > 0

    def test_python_to_airtable_mapping(self):
        """Test Python to Airtable field name mapping."""
        expected_mappings = {
            "where": "Where",
            "participants": "Participants",
            "when": "When",
            "bible": "Bible",
            "churches": "Church",
            "room_numbers": "RoomNumber",
            "record_id": "id",
        }

        assert BibleReadersFieldMapping.PYTHON_TO_AIRTABLE == expected_mappings

    def test_airtable_to_python_mapping(self):
        """Test Airtable to Python field name mapping (reverse mapping)."""
        expected_mappings = {
            "Where": "where",
            "Participants": "participants",
            "When": "when",
            "Bible": "bible",
            "Church": "churches",
            "RoomNumber": "room_numbers",
            "id": "record_id",
        }

        assert BibleReadersFieldMapping.AIRTABLE_TO_PYTHON == expected_mappings

    def test_get_airtable_field_id_success(self):
        """Test successful retrieval of Airtable field ID."""
        field_id = BibleReadersFieldMapping.get_airtable_field_id("Where")
        assert field_id == "fldsSNHSXJBhewCxq"

    def test_get_airtable_field_id_failure(self):
        """Test KeyError when field name not found."""
        with pytest.raises(KeyError):
            BibleReadersFieldMapping.get_airtable_field_id("NonexistentField")

    def test_python_to_airtable_field_success(self):
        """Test successful conversion from Python to Airtable field name."""
        airtable_field = BibleReadersFieldMapping.python_to_airtable_field("where")
        assert airtable_field == "Where"

    def test_python_to_airtable_field_failure(self):
        """Test KeyError when Python field name not found."""
        with pytest.raises(KeyError):
            BibleReadersFieldMapping.python_to_airtable_field("nonexistent_field")

    def test_airtable_to_python_field_success(self):
        """Test successful conversion from Airtable to Python field name."""
        python_field = BibleReadersFieldMapping.airtable_to_python_field("Where")
        assert python_field == "where"

    def test_airtable_to_python_field_failure(self):
        """Test KeyError when Airtable field name not found."""
        with pytest.raises(KeyError):
            BibleReadersFieldMapping.airtable_to_python_field("NonexistentField")

    def test_get_writable_fields(self):
        """Test that writable fields exclude lookup and ID fields."""
        writable_fields = BibleReadersFieldMapping.get_writable_fields()

        expected_writable = {
            "where": "Where",
            "participants": "Participants",
            "when": "When",
            "bible": "Bible",
        }

        assert writable_fields == expected_writable

        # Ensure read-only fields are excluded
        excluded_fields = {"churches", "room_numbers", "record_id"}
        for field in excluded_fields:
            assert field not in writable_fields

    def test_format_date_for_airtable(self):
        """Test date formatting for Airtable compatibility."""
        iso_date = "2025-02-15"
        formatted_date = BibleReadersFieldMapping.format_date_for_airtable(iso_date)

        # For now, should return ISO format (can be enhanced later for locale)
        assert formatted_date == iso_date

    def test_field_mapping_completeness(self):
        """Test that field mappings are bidirectionally complete."""
        # Every Python field should map to an Airtable field
        for python_field in BibleReadersFieldMapping.PYTHON_TO_AIRTABLE:
            airtable_field = BibleReadersFieldMapping.PYTHON_TO_AIRTABLE[python_field]
            assert airtable_field in BibleReadersFieldMapping.AIRTABLE_FIELD_IDS

        # Every Airtable field in the mapping should have a reverse mapping
        for airtable_field in BibleReadersFieldMapping.PYTHON_TO_AIRTABLE.values():
            assert airtable_field in BibleReadersFieldMapping.AIRTABLE_TO_PYTHON

    def test_primary_field_mapping(self):
        """Test that primary field (Where) is properly mapped."""
        # Primary field should be in all mappings
        assert "Where" in BibleReadersFieldMapping.AIRTABLE_FIELD_IDS
        assert "where" in BibleReadersFieldMapping.PYTHON_TO_AIRTABLE
        assert BibleReadersFieldMapping.PYTHON_TO_AIRTABLE["where"] == "Where"
        assert (
            BibleReadersFieldMapping.get_airtable_field_id("Where")
            == "fldsSNHSXJBhewCxq"
        )

    def test_relationship_field_mapping(self):
        """Test that relationship field (Participants) is properly mapped."""
        # Participants field should be in all mappings
        assert "Participants" in BibleReadersFieldMapping.AIRTABLE_FIELD_IDS
        assert "participants" in BibleReadersFieldMapping.PYTHON_TO_AIRTABLE
        assert (
            BibleReadersFieldMapping.PYTHON_TO_AIRTABLE["participants"]
            == "Participants"
        )
        assert (
            BibleReadersFieldMapping.get_airtable_field_id("Participants")
            == "fldVBlRvv295QhBlX"
        )
