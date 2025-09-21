"""
Unit tests for BibleReaders data model.

Tests cover:
- Field validation and types
- Required vs optional fields
- Relationship field handling
- Data serialization
"""

from datetime import date
from typing import List, Optional

import pytest
from pydantic import ValidationError

from src.models.bible_readers import BibleReader


class TestBibleReaderModel:
    """Test suite for BibleReader Pydantic model."""

    def test_create_bible_reader_with_required_fields(self):
        """Test creating a BibleReader with only required fields."""
        reader = BibleReader(
            id="rec123",
            where="Morning Session"
        )

        assert reader.id == "rec123"
        assert reader.where == "Morning Session"
        assert reader.participants == []  # Default empty list
        assert reader.when is None
        assert reader.bible is None

    def test_create_bible_reader_with_all_fields(self):
        """Test creating a BibleReader with all fields."""
        test_date = date(2025, 1, 20)
        participants = ["recPart1", "recPart2"]

        reader = BibleReader(
            id="rec123",
            where="Morning Session",
            participants=participants,
            when=test_date,
            bible="John 3:16"
        )

        assert reader.id == "rec123"
        assert reader.where == "Morning Session"
        assert reader.participants == participants
        assert reader.when == test_date
        assert reader.bible == "John 3:16"

    def test_participants_field_is_list(self):
        """Test that participants field accepts list of record IDs."""
        reader = BibleReader(
            id="rec123",
            where="Evening Session",
            participants=["recA", "recB", "recC"]
        )

        assert isinstance(reader.participants, list)
        assert len(reader.participants) == 3
        assert "recA" in reader.participants

    def test_when_field_date_parsing(self):
        """Test that when field correctly parses date strings."""
        reader = BibleReader(
            id="rec123",
            where="Afternoon Session",
            when="2025-01-20"
        )

        assert isinstance(reader.when, date)
        assert reader.when.year == 2025
        assert reader.when.month == 1
        assert reader.when.day == 20

    def test_missing_required_fields_raises_error(self):
        """Test that missing required fields raise validation errors."""
        with pytest.raises(ValidationError) as exc_info:
            BibleReader(id="rec123")  # Missing 'where' field

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(e["loc"] == ("where",) for e in errors)

    def test_invalid_date_format_raises_error(self):
        """Test that invalid date format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BibleReader(
                id="rec123",
                where="Session",
                when="invalid-date"
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("when",) for e in errors)

    def test_model_dict_serialization(self):
        """Test model serialization to dictionary."""
        reader = BibleReader(
            id="rec123",
            where="Morning Session",
            participants=["recP1"],
            when=date(2025, 1, 20),
            bible="Psalm 23"
        )

        # Test raw Python data (no serialization)
        data = reader.model_dump(mode="python")
        assert data["id"] == "rec123"
        assert data["where"] == "Morning Session"
        assert data["participants"] == ["recP1"]
        assert data["when"] == date(2025, 1, 20)
        assert data["bible"] == "Psalm 23"

        # Test JSON-compatible serialization
        json_data = reader.model_dump(mode="json")
        assert json_data["when"] == "2025-01-20"

    def test_model_dict_exclude_none(self):
        """Test model serialization excludes None values."""
        reader = BibleReader(
            id="rec123",
            where="Session"
        )

        data = reader.model_dump(exclude_none=True)

        assert "id" in data
        assert "where" in data
        assert "when" not in data  # None values excluded
        assert "bible" not in data  # None values excluded

    def test_from_airtable_record(self):
        """Test creating model from Airtable record format."""
        airtable_record = {
            "id": "recABC123",
            "fields": {
                "Where": "Morning Devotion",
                "Participants": ["recP1", "recP2"],
                "When": "2025-01-20",
                "Bible": "Genesis 1:1"
            }
        }

        reader = BibleReader.from_airtable_record(airtable_record)

        assert reader.id == "recABC123"
        assert reader.where == "Morning Devotion"
        assert reader.participants == ["recP1", "recP2"]
        assert reader.when == date(2025, 1, 20)
        assert reader.bible == "Genesis 1:1"

    def test_to_airtable_fields(self):
        """Test converting model to Airtable fields format."""
        reader = BibleReader(
            id="rec123",
            where="Evening Session",
            participants=["recP1"],
            when=date(2025, 1, 20),
            bible="Romans 8:28"
        )

        fields = reader.to_airtable_fields()

        assert fields["Where"] == "Evening Session"
        assert fields["Participants"] == ["recP1"]
        assert fields["When"] == "2025-01-20"
        assert fields["Bible"] == "Romans 8:28"

    def test_empty_participants_list_default(self):
        """Test that participants defaults to empty list."""
        reader = BibleReader(
            id="rec123",
            where="Session"
        )

        assert reader.participants == []
        assert isinstance(reader.participants, list)