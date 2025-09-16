"""
Unit tests for AirtableParticipantRepository.

Tests cover:
- All CRUD operations (create, read, update, delete)
- Search and filtering methods
- Room and floor search methods (NEW)
- Bulk operations
- Error handling and exception mapping
- Repository abstraction compliance
"""

import asyncio
from datetime import date
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.data.airtable.airtable_client import AirtableAPIError, AirtableClient
from src.data.airtable.airtable_participant_repo import (
    AirtableParticipantRepository,
    _PARTICIPANT_CACHE,
)
from src.data.repositories.participant_repository import (
    DuplicateError,
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from src.models.participant import Department, Gender, Participant, Role


@pytest.fixture
def mock_airtable_client():
    """Fixture providing a mock AirtableClient."""
    client = Mock(spec=AirtableClient)

    # Mock client config attributes needed for caching
    client.config = Mock()
    client.config.base_id = "appTestBase123456789"
    client.config.table_id = "tblTestTable12345678"
    client.config.table_name = "TestTable"

    # Default successful responses
    client.create_record = AsyncMock(
        return_value={
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "FullNameEN": "Ivan Ivanov",
                "ContactInformation": "ivan@example.com",
                "Role": "CANDIDATE",
                "Department": "Chapel",
            },
        }
    )

    client.get_record = AsyncMock(
        return_value={
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "FullNameEN": "Ivan Ivanov",
                "ContactInformation": "ivan@example.com",
                "Phone": "+1234567890",
                "Role": "CANDIDATE",
            },
        }
    )

    client.update_record = AsyncMock(
        return_value={
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Петров",
                "FullNameEN": "Ivan Petrov",
                "Email": "ivan.petrov@example.com",
                "Phone": "+1234567890",
                "Role": "CANDIDATE",
            },
        }
    )

    client.delete_record = AsyncMock(return_value=True)

    client.list_records = AsyncMock(
        return_value=[
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Иван Иванов", "Role": "CANDIDATE"},
            },
            {
                "id": "rec234567890123456",
                "fields": {"FullNameRU": "Петр Петров", "Role": "TEAM"},
            },
        ]
    )

    client.search_by_field = AsyncMock(
        return_value=[
            {
                "id": "rec123456789012345",
                "fields": {
                    "FullNameRU": "Иван Иванов",
                    "ContactInformation": "ivan@example.com",
                    "Role": "CANDIDATE",
                },
            }
        ]
    )

    client.search_by_formula = AsyncMock(
        return_value=[
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Иван Иванов", "Role": "CANDIDATE"},
            }
        ]
    )

    client.bulk_create = AsyncMock(
        return_value=[
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Участник 1", "Role": "CANDIDATE"},
            },
            {
                "id": "rec234567890123456",
                "fields": {"FullNameRU": "Участник 2", "Role": "TEAM"},
            },
        ]
    )

    client.bulk_update = AsyncMock(
        return_value=[
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Обновленный 1", "Role": "CANDIDATE"},
            }
        ]
    )

    client.test_connection = AsyncMock(return_value=True)

    return client


@pytest.fixture
def repository(mock_airtable_client):
    """Fixture providing AirtableParticipantRepository with mock client."""
    return AirtableParticipantRepository(mock_airtable_client)


@pytest.fixture
def clear_floor_cache():
    """Fixture that clears the floor cache before each test."""
    from src.data.airtable.airtable_participant_repo import _FLOOR_CACHE

    _FLOOR_CACHE.clear()
    yield
    _FLOOR_CACHE.clear()


@pytest.fixture
def sample_participant():
    """Fixture providing a sample Participant for testing."""
    return Participant(
        full_name_ru="Иван Иванов",
        full_name_en="Ivan Ivanov",
        contact_information="ivan@example.com",
        role=Role.CANDIDATE,
        department=Department.CHAPEL,
    )


@pytest.fixture
def sample_participant_with_id():
    """Fixture providing a sample Participant with record_id for testing updates."""
    return Participant(
        record_id="rec123456789012345",
        full_name_ru="Иван Иванов",
        full_name_en="Ivan Ivanov",
        contact_information="ivan@example.com",
        role=Role.CANDIDATE,
    )


class TestAirtableParticipantRepositoryInitialization:
    """Test suite for repository initialization."""

    def test_repository_initialization(self, mock_airtable_client):
        """Test repository can be initialized with AirtableClient."""
        repo = AirtableParticipantRepository(mock_airtable_client)

        assert repo.client is mock_airtable_client


class TestAirtableParticipantRepositoryCreate:
    """Test suite for create operations."""

    @pytest.mark.asyncio
    async def test_create_participant_success(
        self, repository, mock_airtable_client, sample_participant
    ):
        """Test successful participant creation."""
        # Mock find_by_contact_information to return None (no duplicate)
        with patch.object(repository, "find_by_contact_information", return_value=None):
            result = await repository.create(sample_participant)

        # Should call client.create_record with Airtable fields
        mock_airtable_client.create_record.assert_called_once()

        # Result should be a Participant with record_id
        assert isinstance(result, Participant)
        assert result.record_id == "rec123456789012345"
        assert result.full_name_ru == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_create_participant_duplicate_email(
        self, repository, mock_airtable_client, sample_participant
    ):
        """Test creation fails when participant with email already exists."""
        # Mock find_by_contact_information to return existing participant
        with patch.object(
            repository, "find_by_contact_information", return_value=sample_participant
        ):
            with pytest.raises(DuplicateError) as exc_info:
                await repository.create(sample_participant)

            assert "already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_participant_validation_error(
        self, repository, mock_airtable_client, sample_participant
    ):
        """Test creation with validation error from Airtable."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []

        # Mock Airtable API error with 422 status
        mock_airtable_client.create_record.side_effect = AirtableAPIError(
            "Validation failed", status_code=422
        )

        with pytest.raises(ValidationError) as exc_info:
            await repository.create(sample_participant)

        assert "Invalid participant data" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_participant_api_error(
        self, repository, mock_airtable_client, sample_participant
    ):
        """Test creation with general API error."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []

        mock_airtable_client.create_record.side_effect = AirtableAPIError(
            "Server error"
        )

        with pytest.raises(RepositoryError) as exc_info:
            await repository.create(sample_participant)

        assert "Failed to create participant" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_participant_unexpected_error(
        self, repository, mock_airtable_client, sample_participant
    ):
        """Test creation with unexpected error."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []

        mock_airtable_client.create_record.side_effect = RuntimeError(
            "Unexpected error"
        )

        with pytest.raises(RepositoryError) as exc_info:
            await repository.create(sample_participant)

        assert "Unexpected error creating participant" in str(exc_info.value)


class TestAirtableParticipantRepositoryRead:
    """Test suite for read operations."""

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, repository, mock_airtable_client):
        """Test successful get by ID."""
        result = await repository.get_by_id("rec123456789012345")

        mock_airtable_client.get_record.assert_called_once_with("rec123456789012345")

        assert isinstance(result, Participant)
        assert result.record_id == "rec123456789012345"
        assert result.full_name_ru == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, repository, mock_airtable_client):
        """Test get by ID when record not found."""
        mock_airtable_client.get_record.return_value = None

        result = await repository.get_by_id("nonexistent")

        assert result is None
        mock_airtable_client.get_record.assert_called_once_with("nonexistent")

    @pytest.mark.asyncio
    async def test_get_by_id_api_error(self, repository, mock_airtable_client):
        """Test get by ID with API error."""
        mock_airtable_client.get_record.side_effect = AirtableAPIError("API error")

        with pytest.raises(RepositoryError) as exc_info:
            await repository.get_by_id("rec123")

        assert "Failed to get participant" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_all_success(self, repository, mock_airtable_client):
        """Test successful list all participants."""
        result = await repository.list_all()

        mock_airtable_client.list_records.assert_called_once_with(max_records=None)

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)

    @pytest.mark.asyncio
    async def test_list_all_with_limit(self, repository, mock_airtable_client):
        """Test list all with limit."""
        await repository.list_all(limit=10)

        mock_airtable_client.list_records.assert_called_once_with(max_records=10)

    @pytest.mark.asyncio
    async def test_list_all_api_error(self, repository, mock_airtable_client):
        """Test list all with API error."""
        mock_airtable_client.list_records.side_effect = AirtableAPIError("API error")

        with pytest.raises(RepositoryError) as exc_info:
            await repository.list_all()

        assert "Failed to list participants" in str(exc_info.value)


class TestAirtableParticipantRepositoryUpdate:
    """Test suite for update operations."""

    @pytest.mark.asyncio
    async def test_update_participant_success(
        self, repository, mock_airtable_client, sample_participant_with_id
    ):
        """Test successful participant update."""
        result = await repository.update(sample_participant_with_id)

        mock_airtable_client.update_record.assert_called_once()
        call_args = mock_airtable_client.update_record.call_args
        assert call_args[0][0] == "rec123456789012345"  # record_id

        assert isinstance(result, Participant)
        assert result.record_id == "rec123456789012345"

    @pytest.mark.asyncio
    async def test_update_participant_no_record_id(
        self, repository, sample_participant
    ):
        """Test update fails without record_id."""
        with pytest.raises(ValidationError) as exc_info:
            await repository.update(sample_participant)

        assert "without record_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_participant_not_found(
        self, repository, mock_airtable_client, sample_participant_with_id
    ):
        """Test update with participant not found."""
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Not found", status_code=404
        )

        with pytest.raises(NotFoundError) as exc_info:
            await repository.update(sample_participant_with_id)

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_participant_validation_error(
        self, repository, mock_airtable_client, sample_participant_with_id
    ):
        """Test update with validation error."""
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Validation failed", status_code=422
        )

        with pytest.raises(ValidationError) as exc_info:
            await repository.update(sample_participant_with_id)

        assert "Invalid participant data" in str(exc_info.value)


class TestAirtableParticipantRepositoryDelete:
    """Test suite for delete operations."""

    @pytest.mark.asyncio
    async def test_delete_participant_success(
        self, repository, mock_airtable_client, sample_participant_with_id
    ):
        """Test successful participant deletion."""
        # Mock get_by_id to return existing participant
        with patch.object(
            repository, "get_by_id", return_value=sample_participant_with_id
        ):
            result = await repository.delete("rec123456789012345")

        mock_airtable_client.delete_record.assert_called_once_with("rec123456789012345")
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_participant_not_found(self, repository, mock_airtable_client):
        """Test delete when participant not found."""
        # Mock get_by_id to return None
        with patch.object(repository, "get_by_id", return_value=None):
            with pytest.raises(NotFoundError) as exc_info:
                await repository.delete("nonexistent")

        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_participant_api_error(self, repository, mock_airtable_client):
        """Test delete with API error."""
        mock_airtable_client.delete_record.side_effect = AirtableAPIError(
            "Not found", status_code=404
        )

        with pytest.raises(NotFoundError) as exc_info:
            await repository.delete("rec123")

        assert "not found" in str(exc_info.value)


class TestAirtableParticipantRepositorySearch:
    """Test suite for search operations."""

    @pytest.mark.asyncio
    async def test_find_by_contact_information_success(
        self, repository, mock_airtable_client
    ):
        """Test successful find by contact information."""
        result = await repository.find_by_contact_information("ivan@example.com")

        mock_airtable_client.search_by_field.assert_called_once_with(
            "ContactInformation", "ivan@example.com"
        )

        assert isinstance(result, Participant)
        assert result.contact_information == "ivan@example.com"

    @pytest.mark.asyncio
    async def test_find_by_contact_information_not_found(
        self, repository, mock_airtable_client
    ):
        """Test find by contact information when not found."""
        mock_airtable_client.search_by_field.return_value = []

        result = await repository.find_by_contact_information("notfound@example.com")

        assert result is None

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_success(self, repository, mock_airtable_client):
        """Test successful find by Telegram ID."""
        result = await repository.find_by_telegram_id(12345)

        mock_airtable_client.search_by_field.assert_called_once_with(
            "TelegramID", 12345
        )

        assert isinstance(result, Participant)

    @pytest.mark.asyncio
    async def test_search_by_name_success(self, repository, mock_airtable_client):
        """Test successful search by name pattern."""
        result = await repository.search_by_name("Иван")

        # Should call search_by_formula with proper formula
        mock_airtable_client.search_by_formula.assert_called_once()
        call_args = mock_airtable_client.search_by_formula.call_args[0][0]
        assert "SEARCH('Иван'" in call_args
        assert "FullNameRU" in call_args
        assert "FullNameEN" in call_args

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)

    @pytest.mark.asyncio
    async def test_find_by_role_success(self, repository, mock_airtable_client):
        """Test successful find by role."""
        result = await repository.find_by_role("CANDIDATE")

        mock_airtable_client.search_by_field.assert_called_once_with(
            "Role", "CANDIDATE"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)

    @pytest.mark.asyncio
    async def test_find_by_department_success(self, repository, mock_airtable_client):
        """Test successful find by department."""
        result = await repository.find_by_department("Chapel")

        mock_airtable_client.search_by_field.assert_called_once_with(
            "Department", "Chapel"
        )

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)


class TestParticipantCacheBehavior:
    """Test caching invalidation logic for participant list."""

    @pytest.mark.asyncio
    async def test_create_invalidates_participant_cache(
        self, repository, mock_airtable_client
    ):
        """Creating a participant clears the cached list used by enhanced search."""
        sample_participants = [
            Participant(record_id="recA", full_name_ru="Кэш Тест"),
        ]

        repository.list_all = AsyncMock(return_value=sample_participants)
        _PARTICIPANT_CACHE.clear()

        with patch(
            "src.data.airtable.airtable_participant_repo.SearchService"
        ) as mock_search_service:
            mock_instance = Mock()
            mock_instance.search_participants_enhanced.return_value = []
            mock_search_service.return_value = mock_instance

            await repository.search_by_name_enhanced("Тест")

        cache_key = repository._get_participant_cache_key()
        assert cache_key in _PARTICIPANT_CACHE

        new_participant = Participant(full_name_ru="Новый Участник")
        await repository.create(new_participant)

        assert cache_key not in _PARTICIPANT_CACHE


class TestAirtableParticipantRepositoryBulkOperations:
    """Test suite for bulk operations."""

    @pytest.mark.asyncio
    async def test_bulk_create_success(self, repository, mock_airtable_client):
        """Test successful bulk create."""
        participants = [
            Participant(full_name_ru="Участник 1", role=Role.CANDIDATE),
            Participant(full_name_ru="Участник 2", role=Role.TEAM),
        ]

        result = await repository.bulk_create(participants)

        mock_airtable_client.bulk_create.assert_called_once()

        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        assert all(p.record_id is not None for p in result)

    @pytest.mark.asyncio
    async def test_bulk_create_empty_list(self, repository, mock_airtable_client):
        """Test bulk create with empty list."""
        result = await repository.bulk_create([])

        assert result == []
        mock_airtable_client.bulk_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_create_validation_error(self, repository, mock_airtable_client):
        """Test bulk create with validation error."""
        mock_airtable_client.bulk_create.side_effect = AirtableAPIError(
            "Validation failed", status_code=422
        )

        participants = [Participant(full_name_ru="Test", role=Role.CANDIDATE)]

        with pytest.raises(ValidationError) as exc_info:
            await repository.bulk_create(participants)

        assert "Invalid participant data in bulk create" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_bulk_update_success(self, repository, mock_airtable_client):
        """Test successful bulk update."""
        participants = [
            Participant(
                record_id="rec123456789012345",
                full_name_ru="Обновленный 1",
                role=Role.CANDIDATE,
            )
        ]

        result = await repository.bulk_update(participants)

        mock_airtable_client.bulk_update.assert_called_once()
        call_args = mock_airtable_client.bulk_update.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["id"] == "rec123456789012345"
        assert "fields" in call_args[0]

        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)

    @pytest.mark.asyncio
    async def test_bulk_update_no_record_id(self, repository):
        """Test bulk update fails without record_id."""
        participants = [Participant(full_name_ru="Test", role=Role.CANDIDATE)]

        with pytest.raises(ValidationError) as exc_info:
            await repository.bulk_update(participants)

        assert "without record_id" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_bulk_update_empty_list(self, repository, mock_airtable_client):
        """Test bulk update with empty list."""
        result = await repository.bulk_update([])

        assert result == []
        mock_airtable_client.bulk_update.assert_not_called()


class TestAirtableParticipantRepositoryUtilities:
    """Test suite for utility operations."""

    @pytest.mark.asyncio
    async def test_count_all_success(self, repository, mock_airtable_client):
        """Test successful count all."""
        result = await repository.count_all()

        mock_airtable_client.list_records.assert_called_once()
        assert result == 2  # Based on mock data

    @pytest.mark.asyncio
    async def test_count_all_api_error(self, repository, mock_airtable_client):
        """Test count all with API error."""
        mock_airtable_client.list_records.side_effect = AirtableAPIError("API error")

        with pytest.raises(RepositoryError) as exc_info:
            await repository.count_all()

        assert "Failed to count participants" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_health_check_success(self, repository, mock_airtable_client):
        """Test successful health check."""
        result = await repository.health_check()

        mock_airtable_client.test_connection.assert_called_once()
        assert result is True

    @pytest.mark.asyncio
    async def test_health_check_failure(self, repository, mock_airtable_client):
        """Test health check failure."""
        mock_airtable_client.test_connection.return_value = False

        result = await repository.health_check()

        assert result is False

    @pytest.mark.asyncio
    async def test_health_check_api_error(self, repository, mock_airtable_client):
        """Test health check with API error."""
        mock_airtable_client.test_connection.side_effect = AirtableAPIError(
            "Connection failed"
        )

        with pytest.raises(RepositoryError) as exc_info:
            await repository.health_check()

        assert "Repository health check failed" in str(exc_info.value)


class TestAirtableParticipantRepositoryErrorHandling:
    """Test suite for comprehensive error handling scenarios."""

    @pytest.mark.asyncio
    async def test_search_api_errors_convert_to_repository_errors(
        self, repository, mock_airtable_client
    ):
        """Test that search API errors are properly converted to RepositoryError."""
        mock_airtable_client.search_by_field.side_effect = AirtableAPIError(
            "Search failed"
        )

        with pytest.raises(RepositoryError):
            await repository.find_by_contact_information("test@example.com")

        with pytest.raises(RepositoryError):
            await repository.find_by_telegram_id(12345)

        with pytest.raises(RepositoryError):
            await repository.find_by_role("CANDIDATE")

        with pytest.raises(RepositoryError):
            await repository.find_by_department("Chapel")

    @pytest.mark.asyncio
    async def test_search_formula_api_errors(self, repository, mock_airtable_client):
        """Test that search formula API errors are handled."""
        mock_airtable_client.search_by_formula.side_effect = AirtableAPIError(
            "Formula search failed"
        )

        with pytest.raises(RepositoryError):
            await repository.search_by_name("Test")

    @pytest.mark.asyncio
    async def test_invalid_records_are_skipped_in_list_operations(
        self, repository, mock_airtable_client
    ):
        """Test that invalid records are skipped and logged during list operations."""
        # Mock list_records to return some valid and some invalid records
        mock_airtable_client.list_records.return_value = [
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Valid Participant", "Role": "CANDIDATE"},
            },
            {
                "id": "rec234567890123456",
                "fields": {"Invalid": "Record"},  # Missing required fields
            },
            {
                "id": "rec345678901234567",
                "fields": {"FullNameRU": "Another Valid", "Role": "TEAM"},
            },
        ]

        with patch("src.data.airtable.airtable_participant_repo.logger") as mock_logger:
            result = await repository.list_all()

        # Should return only valid participants
        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)

        # Should log warning for invalid record
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Skipping invalid participant record" in warning_call


class TestAirtableParticipantRepositoryUpdateById:
    """Test suite for update_by_id functionality."""

    @pytest.mark.asyncio
    async def test_update_by_id_success(self, repository, mock_airtable_client):
        """Test successful update by ID with field changes."""
        field_updates = {
            "full_name_ru": "Новое Имя",
            "role": Role.TEAM,
            "payment_amount": 500,
        }

        # Mock successful update
        mock_airtable_client.update_record.return_value = {
            "id": "rec123456789012345",
            "fields": {"FullNameRU": "Новое Имя", "Role": "TEAM", "PaymentAmount": 500},
        }

        result = await repository.update_by_id("rec123456789012345", field_updates)

        assert result is True

        # Verify client was called with correct parameters
        mock_airtable_client.update_record.assert_called_once()
        call_args = mock_airtable_client.update_record.call_args
        assert call_args[0][0] == "rec123456789012345"  # record_id

        # Check that field mapping was applied
        airtable_fields = call_args[0][1]
        assert "FullNameRU" in airtable_fields
        assert "Role" in airtable_fields
        assert "PaymentAmount" in airtable_fields

    @pytest.mark.asyncio
    async def test_update_by_id_empty_record_id(self, repository, mock_airtable_client):
        """Test update with empty record ID raises ValidationError."""
        field_updates = {"full_name_ru": "Test Name"}

        with pytest.raises(ValidationError, match="Record ID cannot be empty"):
            await repository.update_by_id("", field_updates)

        # Client should not be called
        mock_airtable_client.update_record.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_by_id_no_updates(self, repository, mock_airtable_client):
        """Test update with no field updates returns True without API call."""
        result = await repository.update_by_id("rec123456789012345", {})

        assert result is True
        # Client should not be called for empty updates
        mock_airtable_client.update_record.assert_not_called()

    @pytest.mark.asyncio
    async def test_update_by_id_record_not_found(
        self, repository, mock_airtable_client
    ):
        """Test update with non-existent record raises NotFoundError."""
        field_updates = {"full_name_ru": "Test Name"}

        # Mock 404 error
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Not Found", status_code=404
        )

        with pytest.raises(NotFoundError, match="Participant rec999999 not found"):
            await repository.update_by_id("rec999999", field_updates)

    @pytest.mark.asyncio
    async def test_update_by_id_validation_error(
        self, repository, mock_airtable_client
    ):
        """Test update with invalid data raises ValidationError."""
        field_updates = {"invalid_field": "value"}

        # Mock 422 validation error
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Validation Error", status_code=422
        )

        with pytest.raises(ValidationError, match="Unknown field name: invalid_field"):
            await repository.update_by_id("rec123456789012345", field_updates)

    @pytest.mark.asyncio
    async def test_update_by_id_api_error(self, repository, mock_airtable_client):
        """Test update with API error raises RepositoryError."""
        field_updates = {"full_name_ru": "Test Name"}

        # Mock general API error (500)
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Server Error", status_code=500
        )

        with pytest.raises(RepositoryError, match="Failed to update participant"):
            await repository.update_by_id("rec123456789012345", field_updates)

    @pytest.mark.asyncio
    async def test_update_by_id_no_record_returned(
        self, repository, mock_airtable_client
    ):
        """Test update when no record is returned from API."""
        field_updates = {"full_name_ru": "Test Name"}

        # Mock client returning None
        mock_airtable_client.update_record.return_value = None

        result = await repository.update_by_id("rec123456789012345", field_updates)

        assert result is False

    @pytest.mark.asyncio
    async def test_update_by_id_unexpected_error(
        self, repository, mock_airtable_client
    ):
        """Test update with unexpected exception raises RepositoryError."""
        field_updates = {"full_name_ru": "Test Name"}

        # Mock unexpected error
        mock_airtable_client.update_record.side_effect = Exception("Unexpected error")

        with pytest.raises(
            RepositoryError, match="Unexpected error updating participant"
        ):
            await repository.update_by_id("rec123456789012345", field_updates)


class TestRoomFloorSearchMethods:
    """Test class for room and floor search methods."""

    @pytest.mark.asyncio
    async def test_find_by_room_number_success(self, repository, mock_airtable_client):
        """Test successful room search returns participants."""
        room_number = "205"
        mock_records = [
            {"id": "rec1", "fields": {"FullNameRU": "Участник 1", "RoomNumber": 205}},
            {"id": "rec2", "fields": {"FullNameRU": "Участник 2", "RoomNumber": 205}},
        ]

        mock_airtable_client.search_by_field.return_value = mock_records

        # This test should FAIL - method doesn't exist yet
        result = await repository.find_by_room_number(room_number)

        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        mock_airtable_client.search_by_field.assert_called_once_with(
            "RoomNumber", room_number
        )

    @pytest.mark.asyncio
    async def test_find_by_room_number_empty_result(
        self, repository, mock_airtable_client
    ):
        """Test room search with no participants returns empty list."""
        room_number = "999"
        mock_airtable_client.search_by_field.return_value = []

        # This test should FAIL - method doesn't exist yet
        result = await repository.find_by_room_number(room_number)

        assert result == []
        mock_airtable_client.search_by_field.assert_called_once_with(
            "RoomNumber", room_number
        )

    @pytest.mark.asyncio
    async def test_find_by_room_number_api_error(
        self, repository, mock_airtable_client
    ):
        """Test room search handles API errors."""
        room_number = "205"
        mock_airtable_client.search_by_field.side_effect = AirtableAPIError(
            "API Error", status_code=500
        )

        # This test should FAIL - method doesn't exist yet
        with pytest.raises(
            RepositoryError, match="Failed to find participants by room"
        ):
            await repository.find_by_room_number(room_number)

    @pytest.mark.asyncio
    async def test_find_by_floor_success(self, repository, mock_airtable_client):
        """Test successful floor search returns participants."""
        floor = 2
        mock_records = [
            {
                "id": "rec1",
                "fields": {"FullNameRU": "Участник 1", "Floor": 2, "RoomNumber": 201},
            },
            {
                "id": "rec2",
                "fields": {"FullNameRU": "Участник 2", "Floor": 2, "RoomNumber": 205},
            },
        ]

        mock_airtable_client.search_by_field.return_value = mock_records

        # This test should FAIL - method doesn't exist yet
        result = await repository.find_by_floor(floor)

        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        mock_airtable_client.search_by_field.assert_called_once_with("Floor", floor)

    @pytest.mark.asyncio
    async def test_find_by_floor_string_input(self, repository, mock_airtable_client):
        """Test floor search with string input works."""
        floor = "Ground"
        mock_records = [
            {
                "id": "rec1",
                "fields": {
                    "FullNameRU": "Участник 1",
                    "Floor": "Ground",
                    "RoomNumber": "G01",
                },
            }
        ]

        mock_airtable_client.search_by_field.return_value = mock_records

        # This test should FAIL - method doesn't exist yet
        result = await repository.find_by_floor(floor)

        assert len(result) == 1
        mock_airtable_client.search_by_field.assert_called_once_with("Floor", floor)

    @pytest.mark.asyncio
    async def test_find_by_floor_empty_result(self, repository, mock_airtable_client):
        """Test floor search with no participants returns empty list."""
        floor = 99
        mock_airtable_client.search_by_field.return_value = []

        # This test should FAIL - method doesn't exist yet
        result = await repository.find_by_floor(floor)

        assert result == []
        mock_airtable_client.search_by_field.assert_called_once_with("Floor", floor)

    @pytest.mark.asyncio
    async def test_find_by_floor_api_error(self, repository, mock_airtable_client):
        """Test floor search handles API errors."""
        floor = 2
        mock_airtable_client.search_by_field.side_effect = AirtableAPIError(
            "API Error", status_code=500
        )

        # This test should FAIL - method doesn't exist yet
        with pytest.raises(
            RepositoryError, match="Failed to find participants by floor"
        ):
            await repository.find_by_floor(floor)

    @pytest.mark.asyncio
    async def test_get_available_floors_success(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test successful floor discovery returns sorted unique floors."""

        # Mock Airtable client returning records with floor data
        mock_records = [
            {"id": "rec1", "fields": {"Floor": 2}},
            {"id": "rec2", "fields": {"Floor": 1}},
            {"id": "rec3", "fields": {"Floor": 3}},
            {"id": "rec4", "fields": {"Floor": 2}},  # Duplicate
            {"id": "rec5", "fields": {"Floor": 1}},  # Duplicate
        ]

        mock_airtable_client.list_records.return_value = mock_records

        # This test should FAIL - method doesn't exist yet
        result = await repository.get_available_floors()

        # Should return unique floors, sorted ascending
        assert result == [1, 2, 3]

        # Should use fields parameter to only fetch floor data
        mock_airtable_client.list_records.assert_called_once()
        call_args = mock_airtable_client.list_records.call_args
        assert "fields" in call_args.kwargs
        # Floor field mapping should be used

    @pytest.mark.asyncio
    async def test_get_available_floors_with_none_values(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test floor discovery filters out None and invalid floor values."""

        mock_records = [
            {"id": "rec1", "fields": {"Floor": 2}},
            {"id": "rec2", "fields": {"Floor": None}},  # Should be filtered out
            {"id": "rec3", "fields": {}},  # No floor field - should be filtered out
            {"id": "rec4", "fields": {"Floor": 1}},
            {
                "id": "rec5",
                "fields": {"Floor": ""},
            },  # Empty string - should be filtered out
        ]

        mock_airtable_client.list_records.return_value = mock_records

        result = await repository.get_available_floors()

        # Should only return valid numeric floors
        assert result == [1, 2]

    @pytest.mark.asyncio
    async def test_get_available_floors_empty_result(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test floor discovery with no participants returns empty list."""
        mock_airtable_client.list_records.return_value = []

        result = await repository.get_available_floors()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_available_floors_api_timeout(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test floor discovery handles timeout gracefully."""
        # Mock timeout error
        mock_airtable_client.list_records.side_effect = asyncio.TimeoutError()

        # Should return empty list and log warning, not raise exception
        result = await repository.get_available_floors()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_available_floors_api_error(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test floor discovery handles API errors gracefully."""
        # Mock API error
        mock_airtable_client.list_records.side_effect = AirtableAPIError(
            "Rate limit exceeded", status_code=429
        )

        # Should return empty list and log warning, not raise exception
        result = await repository.get_available_floors()

        assert result == []

    @pytest.mark.asyncio
    async def test_get_available_floors_caching_behavior(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test that floor discovery uses caching to avoid repeated API calls."""
        # Mock successful first call
        mock_records = [
            {"id": "rec1", "fields": {"Floor": 2}},
            {"id": "rec2", "fields": {"Floor": 1}},
        ]
        mock_airtable_client.list_records.return_value = mock_records

        # First call should hit API
        result1 = await repository.get_available_floors()
        assert result1 == [1, 2]
        assert mock_airtable_client.list_records.call_count == 1

        # Second call within cache TTL should use cached data
        result2 = await repository.get_available_floors()
        assert result2 == [1, 2]
        # Should still be 1 call - cached result used
        assert mock_airtable_client.list_records.call_count == 1

    @pytest.mark.asyncio
    async def test_get_available_floors_cache_expiry(
        self, repository, mock_airtable_client, clear_floor_cache
    ):
        """Test that cache expires after TTL and makes fresh API call."""
        # Mock successful responses
        mock_records_first = [{"id": "rec1", "fields": {"Floor": 1}}]
        mock_records_second = [{"id": "rec2", "fields": {"Floor": 2}}]

        mock_airtable_client.list_records.side_effect = [
            mock_records_first,
            mock_records_second,
        ]

        # Mock time to control cache expiry
        with patch("src.data.airtable.airtable_participant_repo.time") as mock_time:
            # First call at time 0
            mock_time.time.return_value = 0
            result1 = await repository.get_available_floors()
            assert result1 == [1]
            assert mock_airtable_client.list_records.call_count == 1

            # Second call at time 301 (beyond 300s TTL)
            mock_time.time.return_value = 301
            result2 = await repository.get_available_floors()
            assert result2 == [2]
            # Should make fresh API call
            assert mock_airtable_client.list_records.call_count == 2


class TestFieldConversion:
    """Test field conversion for Airtable format."""

    def test_convert_field_updates_to_airtable_with_date_of_birth(self, repository):
        """Test that date_of_birth is properly serialized to ISO format."""
        field_updates = {
            "date_of_birth": date(1995, 8, 20),
            "age": 28,
            "full_name_ru": "Иван Иванов",
        }

        result = repository._convert_field_updates_to_airtable(field_updates)

        # Should serialize date_of_birth to ISO format string
        assert result["DateOfBirth"] == "1995-08-20"
        assert result["Age"] == 28
        assert result["FullNameRU"] == "Иван Иванов"

    def test_convert_field_updates_to_airtable_with_none_date_of_birth(
        self, repository
    ):
        """Test that None date_of_birth is passed through for clearing."""
        field_updates = {
            "date_of_birth": None,
            "age": None,
        }

        result = repository._convert_field_updates_to_airtable(field_updates)

        # Should pass None through for clearing fields
        assert result["DateOfBirth"] is None
        assert result["Age"] is None

    def test_clearing_behavior_end_to_end(self, repository):
        """Test that clearing behavior works end-to-end with validation and conversion."""
        from src.services.participant_update_service import ParticipantUpdateService

        service = ParticipantUpdateService()

        # Test clearing date_of_birth
        validated_dob = service.validate_field_input("date_of_birth", "   ")
        assert validated_dob is None

        # Test clearing age
        validated_age = service.validate_field_input("age", "\t\n ")
        assert validated_age is None

        # Test that None values are properly converted for Airtable
        field_updates = {
            "date_of_birth": validated_dob,
            "age": validated_age,
        }

        result = repository._convert_field_updates_to_airtable(field_updates)

        # Should properly pass None to Airtable for field clearing
        assert result["DateOfBirth"] is None
        assert result["Age"] is None
