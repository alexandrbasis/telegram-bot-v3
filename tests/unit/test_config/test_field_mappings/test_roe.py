"""
Test cases for ROE field mapping configuration.

This module tests the field mapping functionality for the ROE table,
ensuring proper translation between Python model fields and Airtable fields.
"""

import pytest

from src.config.field_mappings.roe import ROEFieldMapping


class TestROEFieldMapping:
    """Test cases for ROEFieldMapping class."""

    def test_airtable_field_ids_exist(self):
        """Test that all required Airtable field IDs are defined."""
        expected_fields = {
            "RoeTopic",
            "Roista",
            "Assistant",
            "Prayer",
            "RoeDate",
            "RoeTiming",
            "RoeDuration",
            "RoistaChurch",
            "RoistaDepartment",
            "RoistaRoom",
            "RoistaNotes",
            "AssistantChuch",  # Note: preserves Airtable typo
            "AssistantDepartment",
            "AssistantRoom",
            "id",
        }

        actual_fields = set(ROEFieldMapping.AIRTABLE_FIELD_IDS.keys())
        assert actual_fields == expected_fields

        # Verify field IDs are non-empty strings
        for field_name, field_id in ROEFieldMapping.AIRTABLE_FIELD_IDS.items():
            assert isinstance(field_id, str)
            assert len(field_id) > 0

    def test_python_to_airtable_mapping(self):
        """Test Python to Airtable field name mapping."""
        expected_mappings = {
            "roe_topic": "RoeTopic",
            "roista": "Roista",
            "assistant": "Assistant",
            "prayer": "Prayer",
            "roe_date": "RoeDate",
            "roe_timing": "RoeTiming",
            "roe_duration": "RoeDuration",
            "roista_church": "RoistaChurch",
            "roista_department": "RoistaDepartment",
            "roista_room": "RoistaRoom",
            "roista_notes": "RoistaNotes",
            "assistant_church": "AssistantChuch",
            "assistant_department": "AssistantDepartment",
            "assistant_room": "AssistantRoom",
            "record_id": "id",
        }

        assert ROEFieldMapping.PYTHON_TO_AIRTABLE == expected_mappings

    def test_airtable_to_python_mapping(self):
        """Test Airtable to Python field name mapping (reverse mapping)."""
        expected_mappings = {
            "RoeTopic": "roe_topic",
            "Roista": "roista",
            "Assistant": "assistant",
            "Prayer": "prayer",
            "RoeDate": "roe_date",
            "RoeTiming": "roe_timing",
            "RoeDuration": "roe_duration",
            "RoistaChurch": "roista_church",
            "RoistaDepartment": "roista_department",
            "RoistaRoom": "roista_room",
            "RoistaNotes": "roista_notes",
            "AssistantChuch": "assistant_church",
            "AssistantDepartment": "assistant_department",
            "AssistantRoom": "assistant_room",
            "id": "record_id",
        }

        assert ROEFieldMapping.AIRTABLE_TO_PYTHON == expected_mappings

    def test_get_airtable_field_id_success(self):
        """Test successful retrieval of Airtable field ID."""
        field_id = ROEFieldMapping.get_airtable_field_id("RoeTopic")
        assert field_id == "fldSniGvfWpmkpc1r"

    def test_get_airtable_field_id_failure(self):
        """Test KeyError when field name not found."""
        with pytest.raises(KeyError):
            ROEFieldMapping.get_airtable_field_id("NonexistentField")

    def test_python_to_airtable_field_success(self):
        """Test successful conversion from Python to Airtable field name."""
        airtable_field = ROEFieldMapping.python_to_airtable_field("roe_topic")
        assert airtable_field == "RoeTopic"

    def test_python_to_airtable_field_failure(self):
        """Test KeyError when Python field name not found."""
        with pytest.raises(KeyError):
            ROEFieldMapping.python_to_airtable_field("nonexistent_field")

    def test_airtable_to_python_field_success(self):
        """Test successful conversion from Airtable to Python field name."""
        python_field = ROEFieldMapping.airtable_to_python_field("RoeTopic")
        assert python_field == "roe_topic"

    def test_airtable_to_python_field_failure(self):
        """Test KeyError when Airtable field name not found."""
        with pytest.raises(KeyError):
            ROEFieldMapping.airtable_to_python_field("NonexistentField")

    def test_get_writable_fields(self):
        """Test that writable fields exclude lookup and ID fields."""
        writable_fields = ROEFieldMapping.get_writable_fields()

        expected_writable = {
            "roe_topic": "RoeTopic",
            "roista": "Roista",
            "assistant": "Assistant",
            "prayer": "Prayer",
            "roe_date": "RoeDate",
            "roe_timing": "RoeTiming",
            "roe_duration": "RoeDuration",
        }

        assert writable_fields == expected_writable

        # Ensure read-only fields are excluded
        excluded_fields = {
            "roista_church", "roista_department", "roista_room", "roista_notes",
            "assistant_church", "assistant_department", "assistant_room", "record_id"
        }
        for field in excluded_fields:
            assert field not in writable_fields

    def test_get_presenter_relationship_fields(self):
        """Test retrieval of presenter and assistant relationship fields."""
        relationship_fields = ROEFieldMapping.get_presenter_relationship_fields()

        expected_fields = {
            "roista": "Roista",
            "assistant": "Assistant",
            "prayer": "Prayer",
        }

        assert relationship_fields == expected_fields

    def test_get_scheduling_fields(self):
        """Test retrieval of scheduling and timing fields."""
        scheduling_fields = ROEFieldMapping.get_scheduling_fields()

        expected_fields = {
            "roe_date": "RoeDate",
            "roe_timing": "RoeTiming",
            "roe_duration": "RoeDuration",
        }

        assert scheduling_fields == expected_fields

    def test_validate_presenter_relationships_with_roista(self):
        """Test validation passes when ROE has a roista."""
        roe_data = {
            "roe_topic": "Test Topic",
            "roista": ["recROISTA123"],
            "assistant": [],
        }

        assert ROEFieldMapping.validate_presenter_relationships(roe_data) is True

    def test_validate_presenter_relationships_with_assistant(self):
        """Test validation passes when ROE has an assistant."""
        roe_data = {
            "roe_topic": "Test Topic",
            "roista": [],
            "assistant": ["recASSIST123"],
        }

        assert ROEFieldMapping.validate_presenter_relationships(roe_data) is True

    def test_validate_presenter_relationships_with_both(self):
        """Test validation passes when ROE has both roista and assistant."""
        roe_data = {
            "roe_topic": "Test Topic",
            "roista": ["recROISTA123"],
            "assistant": ["recASSIST123"],
        }

        assert ROEFieldMapping.validate_presenter_relationships(roe_data) is True

    def test_validate_presenter_relationships_with_neither(self):
        """Test validation fails when ROE has neither roista nor assistant."""
        roe_data = {
            "roe_topic": "Test Topic",
            "roista": [],
            "assistant": [],
        }

        assert ROEFieldMapping.validate_presenter_relationships(roe_data) is False

    def test_validate_presenter_relationships_missing_fields(self):
        """Test validation fails when required fields are missing."""
        roe_data = {
            "roe_topic": "Test Topic",
        }

        assert ROEFieldMapping.validate_presenter_relationships(roe_data) is False

    def test_format_duration_for_airtable(self):
        """Test duration formatting for Airtable compatibility."""
        # Test various durations
        assert ROEFieldMapping.format_duration_for_airtable(30) == "0:30"
        assert ROEFieldMapping.format_duration_for_airtable(60) == "1:00"
        assert ROEFieldMapping.format_duration_for_airtable(90) == "1:30"
        assert ROEFieldMapping.format_duration_for_airtable(125) == "2:05"

    def test_field_mapping_completeness(self):
        """Test that field mappings are bidirectionally complete."""
        # Every Python field should map to an Airtable field
        for python_field in ROEFieldMapping.PYTHON_TO_AIRTABLE:
            airtable_field = ROEFieldMapping.PYTHON_TO_AIRTABLE[python_field]
            assert airtable_field in ROEFieldMapping.AIRTABLE_FIELD_IDS

        # Every Airtable field in the mapping should have a reverse mapping
        for airtable_field in ROEFieldMapping.PYTHON_TO_AIRTABLE.values():
            assert airtable_field in ROEFieldMapping.AIRTABLE_TO_PYTHON

    def test_primary_field_mapping(self):
        """Test that primary field (RoeTopic) is properly mapped."""
        # Primary field should be in all mappings
        assert "RoeTopic" in ROEFieldMapping.AIRTABLE_FIELD_IDS
        assert "roe_topic" in ROEFieldMapping.PYTHON_TO_AIRTABLE
        assert ROEFieldMapping.PYTHON_TO_AIRTABLE["roe_topic"] == "RoeTopic"
        assert ROEFieldMapping.get_airtable_field_id("RoeTopic") == "fldSniGvfWpmkpc1r"

    def test_relationship_fields_mapping(self):
        """Test that relationship fields are properly mapped."""
        # Main relationship fields
        assert "Roista" in ROEFieldMapping.AIRTABLE_FIELD_IDS
        assert "roista" in ROEFieldMapping.PYTHON_TO_AIRTABLE
        assert ROEFieldMapping.get_airtable_field_id("Roista") == "fldLWsfnGvJ26GwMI"

        assert "Assistant" in ROEFieldMapping.AIRTABLE_FIELD_IDS
        assert "assistant" in ROEFieldMapping.PYTHON_TO_AIRTABLE
        assert ROEFieldMapping.get_airtable_field_id("Assistant") == "fldtTUTsJy6oCg1sE"

    def test_airtable_typo_preservation(self):
        """Test that Airtable field name typo is preserved for compatibility."""
        # AssistantChuch (not Church) should be preserved
        assert "AssistantChuch" in ROEFieldMapping.AIRTABLE_FIELD_IDS
        assert ROEFieldMapping.PYTHON_TO_AIRTABLE["assistant_church"] == "AssistantChuch"