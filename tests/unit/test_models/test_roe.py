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
        roe = ROE(
            id="rec123",
            roe_topic="Prayer and Meditation"
        )

        assert roe.id == "rec123"
        assert roe.roe_topic == "Prayer and Meditation"
        assert roe.roista == []  # Default empty list
        assert roe.assistant == []  # Default empty list

    def test_create_roe_with_all_fields(self):
        """Test creating a ROE with all fields."""
        roista = ["recRoista1"]
        assistant = ["recAssistant1"]

        roe = ROE(
            id="rec123",
            roe_topic="Discipleship",
            roista=roista,
            assistant=assistant
        )

        assert roe.id == "rec123"
        assert roe.roe_topic == "Discipleship"
        assert roe.roista == roista
        assert roe.assistant == assistant

    def test_roista_field_is_list(self):
        """Test that roista field accepts list of record IDs."""
        roe = ROE(
            id="rec123",
            roe_topic="Christian Living",
            roista=["recA", "recB"]
        )

        assert isinstance(roe.roista, list)
        assert len(roe.roista) == 2
        assert "recA" in roe.roista

    def test_assistant_field_is_list(self):
        """Test that assistant field accepts list of record IDs."""
        roe = ROE(
            id="rec123",
            roe_topic="Grace",
            assistant=["recC", "recD", "recE"]
        )

        assert isinstance(roe.assistant, list)
        assert len(roe.assistant) == 3
        assert "recE" in roe.assistant

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            ROE(id="rec123")  # Missing 'roe_topic' field

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(e["loc"] == ("roe_topic",) for e in errors)

    def test_model_dict_serialization(self):
        """Test model serialization to dictionary."""
        roe = ROE(
            id="rec123",
            roe_topic="Faith and Trust",
            roista=["recR1"],
            assistant=["recA1"]
        )

        data = roe.model_dump(mode="python")

        assert data["id"] == "rec123"
        assert data["roe_topic"] == "Faith and Trust"
        assert data["roista"] == ["recR1"]
        assert data["assistant"] == ["recA1"]

    def test_model_dict_exclude_none(self):
        """Test model serialization excludes None values."""
        roe = ROE(
            id="rec123",
            roe_topic="Love and Forgiveness"
        )

        data = roe.model_dump(exclude_none=True)

        assert "id" in data
        assert "roe_topic" in data
        # Empty lists should still be included (not None)
        assert "roista" in data
        assert "assistant" in data

    def test_from_airtable_record(self):
        """Test creating model from Airtable record format."""
        airtable_record = {
            "id": "recABC123",
            "fields": {
                "RoeTopic": "Surrender and Commitment",
                "Roista": ["recR1", "recR2"],
                "Assistant": ["recA1"]
            }
        }

        roe = ROE.from_airtable_record(airtable_record)

        assert roe.id == "recABC123"
        assert roe.roe_topic == "Surrender and Commitment"
        assert roe.roista == ["recR1", "recR2"]
        assert roe.assistant == ["recA1"]

    def test_to_airtable_fields(self):
        """Test converting model to Airtable fields format."""
        roe = ROE(
            id="rec123",
            roe_topic="Joy and Celebration",
            roista=["recR1"],
            assistant=["recA1", "recA2"]
        )

        fields = roe.to_airtable_fields()

        assert fields["RoeTopic"] == "Joy and Celebration"
        assert fields["Roista"] == ["recR1"]
        assert fields["Assistant"] == ["recA1", "recA2"]

    def test_empty_relationship_lists_default(self):
        """Test that relationship fields default to empty lists."""
        roe = ROE(
            id="rec123",
            roe_topic="Service"
        )

        assert roe.roista == []
        assert roe.assistant == []
        assert isinstance(roe.roista, list)
        assert isinstance(roe.assistant, list)

    def test_single_roista_multiple_assistants(self):
        """Test ROE can have one roista but multiple assistants."""
        roe = ROE(
            id="rec123",
            roe_topic="Leadership",
            roista=["recMainRoista"],
            assistant=["recA1", "recA2", "recA3"]
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
            }
        }

        roe = ROE.from_airtable_record(airtable_record)

        assert roe.id == "recXYZ"
        assert roe.roe_topic == "Hope"
        assert roe.roista == []
        assert roe.assistant == []