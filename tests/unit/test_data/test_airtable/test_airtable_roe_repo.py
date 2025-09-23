"""
Unit tests for AirtableROERepository implementation.

Tests the Airtable-specific ROE repository that handles CRUD operations
for ROE records with proper field mapping and validation.
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest

from src.data.airtable.airtable_client import AirtableAPIError
from src.data.airtable.airtable_roe_repo import AirtableROERepository
from src.data.repositories.participant_repository import (
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from src.models.roe import ROE


class TestAirtableROERepository:
    """Test suite for AirtableROERepository."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient."""
        return AsyncMock()

    @pytest.fixture
    def repository(self, mock_client):
        """Create an AirtableROERepository with mocked client."""
        return AirtableROERepository(mock_client)

    @pytest.fixture
    def sample_roe(self):
        """Create a sample ROE for testing."""
        return ROE(
            roe_topic="Test ROE Topic",
            roista=["recROISTAID1"],
            assistant=["recASSISTANT1"],
            prayer=["recPRAYER1"],
            roe_date=date(2025, 9, 22),
            roe_timing="Morning Session",
            roe_duration=45,
        )

    @pytest.fixture
    def sample_airtable_record(self):
        """Create a sample Airtable record for testing."""
        return {
            "id": "recTEST123",
            "fields": {
                "RoeTopic": "Test ROE Topic",
                "Roista": ["recROISTAID1"],
                "Assistant": ["recASSISTANT1"],
                "Prayer": ["recPRAYER1"],
                "RoeDate": "2025-09-22",
                "RoeTiming": "Morning Session",
                "RoeDuration": 45,
                "RoistaChurch": ["Test Church"],
                "RoistaDepartment": ["ROE"],
                "RoistaRoom": [101],
                "RoistaNotes": ["Test notes"],
                "AssistantChuch": ["Assistant Church"],
                "AssistantDepartment": ["Chapel"],
                "AssistantRoom": [102],
            },
        }

    # CREATE TESTS
    async def test_create_success(
        self, repository, mock_client, sample_roe, sample_airtable_record
    ):
        """Test successful ROE creation."""
        mock_client.create_record.return_value = sample_airtable_record

        result = await repository.create(sample_roe)

        assert result.record_id == "recTEST123"
        assert result.roe_topic == "Test ROE Topic"
        assert result.roista == ["recROISTAID1"]
        assert result.assistant == ["recASSISTANT1"]
        assert result.prayer == ["recPRAYER1"]
        assert result.roe_date == date(2025, 9, 22)
        assert result.roe_timing == "Morning Session"
        assert result.roe_duration == 45

        # Verify client was called with correct fields
        mock_client.create_record.assert_called_once()
        call_args = mock_client.create_record.call_args[0][0]
        assert call_args["RoeTopic"] == "Test ROE Topic"
        assert call_args["Roista"] == ["recROISTAID1"]
        assert call_args["Assistant"] == ["recASSISTANT1"]
        assert call_args["Prayer"] == ["recPRAYER1"]
        assert call_args["RoeDate"] == "2025-09-22"
        assert call_args["RoeTiming"] == "Morning Session"
        assert call_args["RoeDuration"] == 45

    async def test_create_validation_error_existing_record_id(
        self, repository, sample_roe
    ):
        """Test creation fails when ROE already has record_id."""
        sample_roe.record_id = "existing_id"

        with pytest.raises(
            ValidationError, match="Cannot create roe with existing record_id"
        ):
            await repository.create(sample_roe)

    async def test_create_validation_error_no_presenter(self, repository, mock_client):
        """Test creation fails when ROE has no presenter."""
        roe_without_presenter = ROE(
            roe_topic="Test ROE Topic",
            roista=[],
            assistant=[],
        )

        with pytest.raises(
            ValidationError, match="ROE must have at least one presenter"
        ):
            await repository.create(roe_without_presenter)

    async def test_create_airtable_api_error(self, repository, mock_client, sample_roe):
        """Test creation handles Airtable API errors."""
        mock_client.create_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to create ROE"):
            await repository.create(sample_roe)

    # GET BY ID TESTS
    async def test_get_by_id_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful ROE retrieval by ID."""
        mock_client.get_record.return_value = sample_airtable_record

        result = await repository.get_by_id("recTEST123")

        assert result is not None
        assert result.record_id == "recTEST123"
        assert result.roe_topic == "Test ROE Topic"
        assert result.prayer == ["recPRAYER1"]
        assert result.roe_date == date(2025, 9, 22)
        mock_client.get_record.assert_called_once_with("recTEST123")

    async def test_get_by_id_not_found(self, repository, mock_client):
        """Test ROE retrieval when record doesn't exist."""
        mock_client.get_record.return_value = None

        result = await repository.get_by_id("nonexistent")

        assert result is None
        mock_client.get_record.assert_called_once_with("nonexistent")

    async def test_get_by_id_airtable_not_found_error(self, repository, mock_client):
        """Test ROE retrieval handles Airtable NOT_FOUND error."""
        mock_client.get_record.side_effect = AirtableAPIError("NOT_FOUND")

        result = await repository.get_by_id("nonexistent")

        assert result is None

    async def test_get_by_id_airtable_api_error(self, repository, mock_client):
        """Test ROE retrieval handles other Airtable API errors."""
        mock_client.get_record.side_effect = AirtableAPIError("Other API Error")

        with pytest.raises(RepositoryError, match="Failed to get ROE"):
            await repository.get_by_id("recTEST123")

    # GET BY TOPIC TESTS
    async def test_get_by_topic_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful ROE retrieval by topic."""
        mock_client.list_records.return_value = {"records": [sample_airtable_record], "offset": None}

        result = await repository.get_by_topic("Test ROE Topic")

        assert result is not None
        assert result.roe_topic == "Test ROE Topic"
        mock_client.list_records.assert_called_once_with(
            formula="{RoeTopic} = 'Test ROE Topic'", max_records=1
        )

    async def test_get_by_topic_not_found(self, repository, mock_client):
        """Test ROE retrieval by topic when no matches found."""
        mock_client.list_records.return_value = {"records": [], "offset": None}

        result = await repository.get_by_topic("Nonexistent Topic")

        assert result is None

    async def test_get_by_topic_airtable_api_error(self, repository, mock_client):
        """Test ROE retrieval by topic handles Airtable API errors."""
        mock_client.list_records.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to search ROE by topic"):
            await repository.get_by_topic("Test Topic")

    # UPDATE TESTS
    async def test_update_success(
        self, repository, mock_client, sample_roe, sample_airtable_record
    ):
        """Test successful ROE update."""
        sample_roe.record_id = "recTEST123"
        sample_roe.roe_topic = "Updated ROE Topic"
        updated_record = sample_airtable_record.copy()
        updated_record["fields"]["RoeTopic"] = "Updated ROE Topic"
        mock_client.update_record.return_value = updated_record

        result = await repository.update(sample_roe)

        assert result.roe_topic == "Updated ROE Topic"
        assert result.record_id == "recTEST123"
        mock_client.update_record.assert_called_once_with(
            "recTEST123", result.to_airtable_fields()
        )

    async def test_update_validation_error_no_record_id(self, repository, sample_roe):
        """Test update fails when ROE has no record_id."""
        sample_roe.record_id = None

        with pytest.raises(
            ValidationError, match="Cannot update roe without record_id"
        ):
            await repository.update(sample_roe)

    async def test_update_validation_error_no_presenter(self, repository):
        """Test update fails when ROE has no presenter."""
        roe_without_presenter = ROE(
            record_id="recTEST123",
            roe_topic="Test ROE Topic",
            roista=[],
            assistant=[],
        )

        with pytest.raises(
            ValidationError, match="ROE must have at least one presenter"
        ):
            await repository.update(roe_without_presenter)

    async def test_update_not_found_error(self, repository, mock_client, sample_roe):
        """Test update handles record not found."""
        sample_roe.record_id = "recTEST123"
        mock_client.update_record.side_effect = AirtableAPIError("NOT_FOUND")

        with pytest.raises(NotFoundError, match="ROE with id recTEST123 not found"):
            await repository.update(sample_roe)

    async def test_update_airtable_api_error(self, repository, mock_client, sample_roe):
        """Test update handles other Airtable API errors."""
        sample_roe.record_id = "recTEST123"
        mock_client.update_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to update ROE"):
            await repository.update(sample_roe)

    # DELETE TESTS
    async def test_delete_success(self, repository, mock_client):
        """Test successful ROE deletion."""
        mock_client.delete_record.return_value = True

        result = await repository.delete("recTEST123")

        assert result is True
        mock_client.delete_record.assert_called_once_with("recTEST123")

    async def test_delete_not_found(self, repository, mock_client):
        """Test deletion when record doesn't exist."""
        mock_client.delete_record.return_value = False

        result = await repository.delete("nonexistent")

        assert result is False

    async def test_delete_airtable_api_error(self, repository, mock_client):
        """Test deletion handles Airtable API errors."""
        mock_client.delete_record.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to delete ROE"):
            await repository.delete("recTEST123")

    # LIST TESTS
    async def test_list_all_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful listing of all ROE records."""
        mock_client.list_records.return_value = {"records": [sample_airtable_record], "offset": None}

        result = await repository.list_all()

        assert len(result) == 1
        assert result[0].record_id == "recTEST123"
        assert result[0].roe_topic == "Test ROE Topic"
        mock_client.list_records.assert_called_once_with()

    async def test_list_all_empty(self, repository, mock_client):
        """Test listing when no ROE records exist."""
        mock_client.list_records.return_value = {"records": [], "offset": None}

        result = await repository.list_all()

        assert result == []

    async def test_list_all_airtable_api_error(self, repository, mock_client):
        """Test listing handles Airtable API errors."""
        mock_client.list_records.side_effect = AirtableAPIError("API Error")

        with pytest.raises(RepositoryError, match="Failed to list ROEs"):
            await repository.list_all()

    # RELATIONSHIP QUERY TESTS
    async def test_get_by_roista_id_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful ROE retrieval by roista ID."""
        mock_client.list_records.return_value = {"records": [sample_airtable_record], "offset": None}

        result = await repository.get_by_roista_id("recROISTAID1")

        assert len(result) == 1
        assert result[0].roe_topic == "Test ROE Topic"
        mock_client.list_records.assert_called_once_with(
            formula="FIND('recROISTAID1', ARRAYJOIN({Roista})) > 0"
        )

    async def test_get_by_assistant_id_success(
        self, repository, mock_client, sample_airtable_record
    ):
        """Test successful ROE retrieval by assistant ID."""
        mock_client.list_records.return_value = {"records": [sample_airtable_record], "offset": None}

        result = await repository.get_by_assistant_id("recASSISTANT1")

        assert len(result) == 1
        assert result[0].roe_topic == "Test ROE Topic"
        mock_client.list_records.assert_called_once_with(
            formula="FIND('recASSISTANT1', ARRAYJOIN({Assistant})) > 0"
        )
