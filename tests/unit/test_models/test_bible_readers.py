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
            where="Morning Session"
        )

        assert reader.record_id is None  # Optional field
        assert reader.where == "Morning Session"
        assert reader.participants == []  # Default empty list
        assert reader.churches is None
        assert reader.room_numbers is None
        assert reader.when is None
        assert reader.bible is None

    def test_create_bible_reader_with_all_fields(self):
        """Test creating a BibleReader with all fields."""
        test_date = date(2025, 1, 20)
        participants = ["recPart1", "recPart2"]
        churches = ["Church A", "Church B"]
        room_numbers = [101, "102A"]

        reader = BibleReader(
            record_id="rec123",
            where="Morning Session",
            participants=participants,
            churches=churches,
            room_numbers=room_numbers,
            when=test_date,
            bible="John 3:16"
        )

        assert reader.record_id == "rec123"
        assert reader.where == "Morning Session"
        assert reader.participants == participants
        assert reader.churches == churches
        assert reader.room_numbers == room_numbers
        assert reader.when == test_date
        assert reader.bible == "John 3:16"

    def test_participants_field_is_list(self):
        """Test that participants field accepts list of record IDs."""
        reader = BibleReader(
            where="Evening Session",
            participants=["recA", "recB", "recC"]
        )

        assert isinstance(reader.participants, list)
        assert len(reader.participants) == 3
        assert "recA" in reader.participants

    def test_when_field_date_parsing(self):
        """Test that when field correctly parses date strings."""
        reader = BibleReader(
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
            BibleReader()  # Missing 'where' field

        errors = exc_info.value.errors()
        assert len(errors) > 0
        assert any(e["loc"] == ("where",) for e in errors)

    def test_invalid_date_format_raises_error(self):
        """Test that invalid date format raises validation error."""
        with pytest.raises(ValidationError) as exc_info:
            BibleReader(
                where="Session",
                when="invalid-date"
            )

        errors = exc_info.value.errors()
        assert any(e["loc"] == ("when",) for e in errors)

    def test_model_dict_serialization(self):
        """Test model serialization to dictionary."""
        reader = BibleReader(
            record_id="rec123",
            where="Morning Session",
            participants=["recP1"],
            churches=["Church A"],
            room_numbers=[101],
            when=date(2025, 1, 20),
            bible="Psalm 23"
        )

        # Test raw Python data (no serialization)
        data = reader.model_dump(mode="python")
        assert data["record_id"] == "rec123"
        assert data["where"] == "Morning Session"
        assert data["participants"] == ["recP1"]
        assert data["churches"] == ["Church A"]
        assert data["room_numbers"] == [101]
        assert data["when"] == date(2025, 1, 20)
        assert data["bible"] == "Psalm 23"

        # Test JSON-compatible serialization
        json_data = reader.model_dump(mode="json")
        assert json_data["when"] == "2025-01-20"

    def test_model_dict_exclude_none(self):
        """Test model serialization excludes None values."""
        reader = BibleReader(
            where="Session"
        )

        data = reader.model_dump(exclude_none=True)

        assert "where" in data
        assert "record_id" not in data  # None values excluded
        assert "churches" not in data  # None values excluded
        assert "room_numbers" not in data  # None values excluded
        assert "when" not in data  # None values excluded
        assert "bible" not in data  # None values excluded

    def test_from_airtable_record(self):
        """Test creating model from Airtable record format."""
        airtable_record = {
            "id": "recABC123",
            "fields": {
                "Where": "Morning Devotion",
                "Participants": ["recP1", "recP2"],
                "Church": ["Church A", "Church B"],
                "RoomNumber": [101, "102A"],
                "When": "2025-01-20",
                "Bible": "Genesis 1:1"
            }
        }

        reader = BibleReader.from_airtable_record(airtable_record)

        assert reader.record_id == "recABC123"
        assert reader.where == "Morning Devotion"
        assert reader.participants == ["recP1", "recP2"]
        assert reader.churches == ["Church A", "Church B"]
        assert reader.room_numbers == [101, "102A"]
        assert reader.when == date(2025, 1, 20)
        assert reader.bible == "Genesis 1:1"

    def test_to_airtable_fields(self):
        """Test converting model to Airtable fields format."""
        reader = BibleReader(
            record_id="rec123",
            where="Evening Session",
            participants=["recP1"],
            churches=["Church A"],  # Lookup fields
            room_numbers=[101],      # Should not appear in output
            when=date(2025, 1, 20),
            bible="Romans 8:28"
        )

        fields = reader.to_airtable_fields()

        assert fields["Where"] == "Evening Session"
        assert fields["Participants"] == ["recP1"]
        assert fields["When"] == "2025-01-20"
        assert fields["Bible"] == "Romans 8:28"
        # Lookup fields should not be in output (read-only)
        assert "Church" not in fields
        assert "RoomNumber" not in fields

    def test_empty_participants_list_default(self):
        """Test that participants defaults to empty list."""
        reader = BibleReader(
            where="Session"
        )

        assert reader.participants == []
        assert isinstance(reader.participants, list)

    def test_lookup_fields_are_optional(self):
        """Test that lookup fields (churches, room_numbers) are optional."""
        reader = BibleReader(
            where="Session",
            participants=["recP1"]
        )

        assert reader.churches is None
        assert reader.room_numbers is None

    def test_create_without_record_id(self):
        """Test creating a BibleReader without record_id (for new records)."""
        reader = BibleReader(
            where="New Session",
            participants=["recP1"],
            bible="Matthew 5:1-12"
        )

        assert reader.record_id is None
        assert reader.where == "New Session"
        assert reader.participants == ["recP1"]
        assert reader.bible == "Matthew 5:1-12"