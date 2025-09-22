"""
Unit tests for ROE data model.

Tests cover:
- Field validation and types
- Required vs optional fields
- Relationship field handling
- Data serialization
"""

from typing import List, Optional

import pytest
from pydantic import ValidationError

from src.models.roe import ROE


class TestROEModel:
    """Test suite for ROE Pydantic model."""

    def test_create_roe_with_required_fields(self):
        """Test creating a ROE with only required fields."""
        roe = ROE(roe_topic="Prayer and Meditation")

        assert roe.record_id is None  # Optional field
        assert roe.roe_topic == "Prayer and Meditation"
        assert roe.roista == []  # Default empty list
        assert roe.assistant == []  # Default empty list
        # Check lookup fields are None
        assert roe.roista_church is None
        assert roe.roista_department is None
        assert roe.roista_room is None
        assert roe.roista_notes is None
        assert roe.assistant_church is None
        assert roe.assistant_department is None
        assert roe.assistant_room is None

    def test_create_roe_with_all_fields(self):
        """Test creating a ROE with all fields."""
        roista = ["recRoista1"]
        assistant = ["recAssistant1"]
        roista_churches = ["Church A"]
        roista_depts = ["ROE"]
        roista_rooms = [101]
        roista_notes = ["Team leader"]
        assistant_churches = ["Church B"]
        assistant_depts = ["Chapel"]
        assistant_rooms = ["202A"]

        roe = ROE(
            record_id="rec123",
            roe_topic="Discipleship",
            roista=roista,
            roista_church=roista_churches,
            roista_department=roista_depts,
            roista_room=roista_rooms,
            roista_notes=roista_notes,
            assistant=assistant,
            assistant_church=assistant_churches,
            assistant_department=assistant_depts,
            assistant_room=assistant_rooms,
        )

        assert roe.record_id == "rec123"
        assert roe.roe_topic == "Discipleship"
        assert roe.roista == roista
        assert roe.roista_church == roista_churches
        assert roe.roista_department == roista_depts
        assert roe.roista_room == roista_rooms
        assert roe.roista_notes == roista_notes
        assert roe.assistant == assistant
        assert roe.assistant_church == assistant_churches
        assert roe.assistant_department == assistant_depts
        assert roe.assistant_room == assistant_rooms

    def test_roista_field_is_list(self):
        """Test that roista field accepts list of record IDs."""
        roe = ROE(roe_topic="Christian Living", roista=["recA", "recB"])

        assert isinstance(roe.roista, list)
        assert len(roe.roista) == 2
        assert "recA" in roe.roista

    def test_assistant_field_is_list(self):
        """Test that assistant field accepts list of record IDs."""
        roe = ROE(roe_topic="Grace", assistant=["recC", "recD", "recE"])

        assert isinstance(roe.assistant, list)
        assert len(roe.assistant) == 3
        assert "recE" in roe.assistant

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ROE()  # Missing 'roe_topic' field

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(e["loc"] == ("roe_topic",) for e in errors)

    def test_model_dict_serialization(self):
        """Test model serialization to dictionary."""
        roe = ROE(
            record_id="rec123",
            roe_topic="Faith and Trust",
            roista=["recR1"],
            roista_church=["Church A"],
            assistant=["recA1"],
            assistant_church=["Church B"],
        )

        data = roe.model_dump(mode="python")

        assert data["record_id"] == "rec123"
        assert data["roe_topic"] == "Faith and Trust"
        assert data["roista"] == ["recR1"]
        assert data["roista_church"] == ["Church A"]
        assert data["assistant"] == ["recA1"]
        assert data["assistant_church"] == ["Church B"]

    def test_model_dict_exclude_none(self):
        """Test model serialization excludes None values."""
        roe = ROE(roe_topic="Love and Forgiveness")

        data = roe.model_dump(exclude_none=True)

        assert "roe_topic" in data
        # Empty lists should still be included (not None)
        assert "roista" in data
        assert "assistant" in data
        # None values should be excluded
        assert "record_id" not in data
        assert "roista_church" not in data
        assert "assistant_church" not in data

    def test_from_airtable_record(self):
        """Test creating model from Airtable record format."""
        airtable_record = {
            "id": "recABC123",
            "fields": {
                "RoeTopic": "Surrender and Commitment",
                "Roista": ["recR1", "recR2"],
                "RoistaChurch": ["Church A", "Church B"],
                "RoistaDepartment": ["ROE", "Chapel"],
                "RoistaRoom": [101, 102],
                "RoistaNotes": ["Leader", "Assistant"],
                "Assistant": ["recA1"],
                "AssistantChuch": ["Church C"],  # Note typo in Airtable
                "AssistantDepartment": ["Kitchen"],
                "AssistantRoom": ["201"],
            },
        }

        roe = ROE.from_airtable_record(airtable_record)

        assert roe.record_id == "recABC123"
        assert roe.roe_topic == "Surrender and Commitment"
        assert roe.roista == ["recR1", "recR2"]
        assert roe.roista_church == ["Church A", "Church B"]
        assert roe.roista_department == ["ROE", "Chapel"]
        assert roe.roista_room == [101, 102]
        assert roe.roista_notes == ["Leader", "Assistant"]
        assert roe.assistant == ["recA1"]
        assert roe.assistant_church == ["Church C"]
        assert roe.assistant_department == ["Kitchen"]
        assert roe.assistant_room == ["201"]

    def test_to_airtable_fields(self):
        """Test converting model to Airtable fields format."""
        roe = ROE(
            record_id="rec123",
            roe_topic="Joy and Celebration",
            roista=["recR1"],
            roista_church=["Church A"],  # Lookup fields
            assistant=["recA1", "recA2"],
            assistant_church=["Church B", "Church C"],  # Should not appear in output
        )

        fields = roe.to_airtable_fields()

        assert fields["RoeTopic"] == "Joy and Celebration"
        assert fields["Roista"] == ["recR1"]
        assert fields["Assistant"] == ["recA1", "recA2"]
        # Lookup fields should not be in output (read-only)
        assert "RoistaChurch" not in fields
        assert "AssistantChuch" not in fields

    def test_empty_relationship_lists_default(self):
        """Test that relationship fields default to empty lists."""
        roe = ROE(roe_topic="Service")

        assert roe.roista == []
        assert roe.assistant == []
        assert isinstance(roe.roista, list)
        assert isinstance(roe.assistant, list)

    def test_single_roista_multiple_assistants(self):
        """Test ROE can have one roista but multiple assistants."""
        roe = ROE(
            roe_topic="Leadership",
            roista=["recMainRoista"],
            assistant=["recA1", "recA2", "recA3"],
        )

        assert len(roe.roista) == 1
        assert len(roe.assistant) == 3

    def test_from_airtable_with_empty_fields(self):
        """Test creating from Airtable record with missing optional fields."""
        airtable_record = {
            "id": "recXYZ",
            "fields": {
                "RoeTopic": "Hope"
                # No Roista or Assistant fields
            },
        }

        roe = ROE.from_airtable_record(airtable_record)

        assert roe.record_id == "recXYZ"
        assert roe.roe_topic == "Hope"
        assert roe.roista == []
        assert roe.assistant == []
        # Lookup fields should be None
        assert roe.roista_church is None
        assert roe.assistant_department is None

    def test_lookup_fields_are_optional(self):
        """Test that all lookup fields are optional."""
        roe = ROE(roe_topic="Fellowship", roista=["recR1"])

        assert roe.roista_church is None
        assert roe.roista_department is None
        assert roe.roista_room is None
        assert roe.roista_notes is None
        assert roe.assistant_church is None
        assert roe.assistant_department is None
        assert roe.assistant_room is None

    def test_create_without_record_id(self):
        """Test creating a ROE without record_id (for new records)."""
        roe = ROE(roe_topic="New Topic", roista=["recR1"], assistant=["recA1"])

        assert roe.record_id is None
        assert roe.roe_topic == "New Topic"
        assert roe.roista == ["recR1"]
        assert roe.assistant == ["recA1"]
