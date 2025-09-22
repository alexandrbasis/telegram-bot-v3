"""
Test cases for AirtableBibleReadersRepository.

This module tests the Airtable-specific implementation of BibleReadersRepository,
ensuring proper mapping between BibleReader domain objects and Airtable records.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.data.airtable.airtable_bible_readers_repo import AirtableBibleReadersRepository
from src.data.airtable.airtable_client import AirtableAPIError
from src.data.repositories.participant_repository import (
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from src.models.bible_readers import BibleReader


class TestAirtableBibleReadersRepository:
    """Test cases for AirtableBibleReadersRepository."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_client):
        """Create repository instance with mock client."""
        return AirtableBibleReadersRepository(mock_client)

    @pytest.fixture
    def sample_bible_reader(self):
        """Create a sample BibleReader for testing."""
        return BibleReader(
            record_id=None,  # For creation
            where="Morning Chapel",
            participants=["recParticipant1", "recParticipant2"],
            when=date(2025, 2, 15),
            bible="John 3:16",
        )

    @pytest.fixture
    def sample_airtable_record(self):
        """Create a sample Airtable record."""
        return {
            "id": "recBibleReader123",
            "fields": {
                "Where": "Morning Chapel",
                "Participants": ["recParticipant1", "recParticipant2"],
                "When": "2025-02-15",
                "Bible": "John 3:16",
                "Church": ["Grace Church"],
                "RoomNumber": [101, 102],
            },
        }

    async def test_create_success(
        self, repository, mock_client, sample_bible_reader, sample_airtable_record
    ):
        """Test successful BibleReader creation."""
        mock_client.create_record.return_value = sample_airtable_record

        result = await repository.create(sample_bible_reader)

        assert result.record_id == "recBibleReader123"
        assert result.where == "Morning Chapel"
        assert result.participants == ["recParticipant1", "recParticipant2"]
        assert result.when == date(2025, 2, 15)
        assert result.bible == "John 3:16"

        # Verify client was called with correct fields
        mock_client.create_record.assert_called_once()
        call_args = mock_client.create_record.call_args[0][0]
        assert call_args["Where"] == "Morning Chapel"
        assert call_args["Participants"] == ["recParticipant1", "recParticipant2"]

    async def test_create_with_existing_id_fails(self, repository, sample_bible_reader):
        """Test creation fails when BibleReader already has record_id."""
        sample_bible_reader.record_id = "recExisting123"

        with pytest.raises(
            ValidationError, match="Cannot create bible_reader with existing record_id"
        ):
            await repository.create(sample_bible_reader)

    async def test_create_airtable_error(
        self, repository, mock_client, sample_bible_reader
    ):
        """Test creation handles Airtable API errors."""
        mock_client.create_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to create BibleReader"):
            await repository.create(sample_bible_reader)

    async def test_get_by_id_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful retrieval by ID."""
        mock_client.get_record.return_value = sample_airtable_record

        result = await repository.get_by_id("recBibleReader123")

        assert result is not None
        assert result.record_id == "recBibleReader123"
        assert result.where == "Morning Chapel"
        mock_client.get_record.assert_called_once_with("recBibleReader123")

    async def test_get_by_id_not_found(self, repository, mock_client):
        """Test get_by_id returns None when record not found."""
        mock_client.get_record.return_value = None

        result = await repository.get_by_id("nonexistent")

        assert result is None

    async def test_get_by_id_airtable_not_found_error(self, repository, mock_client):
        """Test get_by_id handles NOT_FOUND API errors."""
        mock_client.get_record.side_effect = AirtableAPIError("NOT_FOUND")

        result = await repository.get_by_id("nonexistent")

        assert result is None

    async def test_get_by_id_other_airtable_error(self, repository, mock_client):
        """Test get_by_id handles other Airtable API errors."""
        mock_client.get_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to get BibleReader"):
            await repository.get_by_id("recBibleReader123")

    async def test_get_by_where_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful retrieval by where field."""
        mock_client.list_records.return_value = [sample_airtable_record]

        result = await repository.get_by_where("Morning Chapel")

        assert result is not None
        assert result.where == "Morning Chapel"
        mock_client.list_records.assert_called_once_with(
            formula="{Where} = 'Morning Chapel'", max_records=1
        )

    async def test_get_by_where_not_found(self, repository, mock_client):
        """Test get_by_where returns None when not found."""
        mock_client.list_records.return_value = []

        result = await repository.get_by_where("Nonexistent Location")

        assert result is None

    async def test_get_by_where_airtable_error(self, repository, mock_client):
        """Test get_by_where handles Airtable API errors."""
        mock_client.list_records.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to search BibleReader"):
            await repository.get_by_where("Morning Chapel")

    async def test_update_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful BibleReader update."""
        bible_reader = BibleReader(
            record_id="recBibleReader123",
            where="Evening Service",
            participants=["recParticipant3"],
            when=date(2025, 3, 1),
            bible="Psalm 23",
        )

        updated_record = {
            **sample_airtable_record,
            "fields": {
                **sample_airtable_record["fields"],
                "Where": "Evening Service",
                "Bible": "Psalm 23",
            },
        }
        mock_client.update_record.return_value = updated_record

        result = await repository.update(bible_reader)

        assert result.where == "Evening Service"
        assert result.bible == "Psalm 23"
        mock_client.update_record.assert_called_once()

    async def test_update_without_id_fails(self, repository, sample_bible_reader):
        """Test update fails when BibleReader has no record_id."""
        with pytest.raises(
            ValidationError, match="Cannot update bible_reader without record_id"
        ):
            await repository.update(sample_bible_reader)

    async def test_update_not_found_error(self, repository, mock_client):
        """Test update handles NOT_FOUND errors."""
        bible_reader = BibleReader(
            record_id="nonexistent", where="Test", participants=[]
        )
        mock_client.update_record.side_effect = AirtableAPIError("NOT_FOUND")

        with pytest.raises(
            NotFoundError, match="BibleReader with id nonexistent not found"
        ):
            await repository.update(bible_reader)

    async def test_update_other_airtable_error(self, repository, mock_client):
        """Test update handles other Airtable API errors."""
        bible_reader = BibleReader(
            record_id="recBibleReader123", where="Test", participants=[]
        )
        mock_client.update_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to update BibleReader"):
            await repository.update(bible_reader)

    async def test_delete_success(self, repository, mock_client):
        """Test successful BibleReader deletion."""
        mock_client.delete_record.return_value = True

        result = await repository.delete("recBibleReader123")

        assert result is True
        mock_client.delete_record.assert_called_once_with("recBibleReader123")

    async def test_delete_not_found(self, repository, mock_client):
        """Test delete returns False when record not found."""
        mock_client.delete_record.side_effect = AirtableAPIError("NOT_FOUND")

        result = await repository.delete("nonexistent")

        assert result is False

    async def test_delete_other_airtable_error(self, repository, mock_client):
        """Test delete handles other Airtable API errors."""
        mock_client.delete_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to delete BibleReader"):
            await repository.delete("recBibleReader123")

    async def test_list_all_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful listing of all BibleReaders."""
        mock_client.list_records.return_value = [sample_airtable_record]

        result = await repository.list_all()

        assert len(result) == 1
        assert result[0].record_id == "recBibleReader123"
        assert result[0].where == "Morning Chapel"

    async def test_list_all_empty(self, repository, mock_client):
        """Test list_all returns empty list when no records."""
        mock_client.list_records.return_value = []

        result = await repository.list_all()

        assert result == []

    async def test_list_all_with_invalid_record(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test list_all skips invalid records and logs warning."""
        valid_record = sample_airtable_record
        # Create a record that will cause BibleReader.from_airtable_record to fail
        invalid_record = {
            "id": "recInvalid",
            "fields": {"When": "invalid-date-format"},
        }  # Invalid date format

        mock_client.list_records.return_value = [valid_record, invalid_record]

        result = await repository.list_all()

        assert len(result) == 1  # Only valid record included
        assert result[0].record_id == "recBibleReader123"

    async def test_list_all_airtable_error(self, repository, mock_client):
        """Test list_all handles Airtable API errors."""
        mock_client.list_records.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to list BibleReaders"):
            await repository.list_all()

    async def test_get_by_participant_id_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful retrieval by participant ID."""
        mock_client.list_records.return_value = [sample_airtable_record]

        result = await repository.get_by_participant_id("recParticipant1")

        assert len(result) == 1
        assert result[0].record_id == "recBibleReader123"

        # Verify formula construction
        mock_client.list_records.assert_called_once()
        call_args = mock_client.list_records.call_args
        formula = call_args.kwargs["formula"]
        assert "FIND('recParticipant1'" in formula
        assert "Participants" in formula

    async def test_get_by_participant_id_not_found(self, repository, mock_client):
        """Test get_by_participant_id returns empty list when not found."""
        mock_client.list_records.return_value = []

        result = await repository.get_by_participant_id("nonexistent")

        assert result == []

    async def test_get_by_participant_id_airtable_error(self, repository, mock_client):
        """Test get_by_participant_id handles Airtable API errors."""
        mock_client.list_records.side_effect = AirtableAPIError("API Error")

        with pytest.raises(
            RepositoryError, match="Failed to search BibleReaders by participant"
        ):
            await repository.get_by_participant_id("recParticipant1")

    async def test_repository_uses_correct_field_mapping(self, repository):
        """Test repository uses BibleReadersFieldMapping."""
        assert repository.field_mapping is not None
        # Test a few key mappings
        assert repository.field_mapping.python_to_airtable_field("where") == "Where"
        assert (
            repository.field_mapping.python_to_airtable_field("participants")
            == "Participants"
        )
