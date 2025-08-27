"""
Unit tests for AirtableParticipantRepository.

Tests cover:
- All CRUD operations (create, read, update, delete)
- Search and filtering methods
- Bulk operations
- Error handling and exception mapping
- Repository abstraction compliance
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Dict, Any
from datetime import date

from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.data.airtable.airtable_client import AirtableClient, AirtableAPIError
from src.data.repositories.participant_repository import (
    RepositoryError, 
    ValidationError, 
    NotFoundError, 
    DuplicateError
)
from src.models.participant import Participant, Role, Gender, Department


@pytest.fixture
def mock_airtable_client():
    """Fixture providing a mock AirtableClient."""
    client = Mock(spec=AirtableClient)
    
    # Default successful responses
    client.create_record = AsyncMock(return_value={
        "id": "rec123456789012345",
        "fields": {
            "FullNameRU": "Иван Иванов",
            "FullNameEN": "Ivan Ivanov",
            "ContactInformation": "ivan@example.com",
            "Role": "CANDIDATE",
            "Department": "Chapel"
        }
    })
    
    client.get_record = AsyncMock(return_value={
        "id": "rec123456789012345",
        "fields": {
            "FullNameRU": "Иван Иванов",
            "FullNameEN": "Ivan Ivanov",
            "ContactInformation": "ivan@example.com",
            "Phone": "+1234567890",
            "Role": "CANDIDATE"
        }
    })
    
    client.update_record = AsyncMock(return_value={
        "id": "rec123456789012345",
        "fields": {
            "FullNameRU": "Иван Петров",
            "FullNameEN": "Ivan Petrov",
            "Email": "ivan.petrov@example.com",
            "Phone": "+1234567890",
            "Role": "CANDIDATE"
        }
    })
    
    client.delete_record = AsyncMock(return_value=True)
    
    client.list_records = AsyncMock(return_value=[
        {
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "Role": "CANDIDATE"
            }
        },
        {
            "id": "rec234567890123456",
            "fields": {
                "FullNameRU": "Петр Петров",
                "Role": "TEAM"
            }
        }
    ])
    
    client.search_by_field = AsyncMock(return_value=[
        {
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "ContactInformation": "ivan@example.com",
                "Role": "CANDIDATE"
            }
        }
    ])
    
    client.search_by_formula = AsyncMock(return_value=[
        {
            "id": "rec123456789012345",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "Role": "CANDIDATE"
            }
        }
    ])
    
    client.bulk_create = AsyncMock(return_value=[
        {
            "id": "rec123456789012345",
            "fields": {"FullNameRU": "Участник 1", "Role": "CANDIDATE"}
        },
        {
            "id": "rec234567890123456",
            "fields": {"FullNameRU": "Участник 2", "Role": "TEAM"}
        }
    ])
    
    client.bulk_update = AsyncMock(return_value=[
        {
            "id": "rec123456789012345",
            "fields": {"FullNameRU": "Обновленный 1", "Role": "CANDIDATE"}
        }
    ])
    
    client.test_connection = AsyncMock(return_value=True)
    
    return client


@pytest.fixture
def repository(mock_airtable_client):
    """Fixture providing AirtableParticipantRepository with mock client."""
    return AirtableParticipantRepository(mock_airtable_client)


@pytest.fixture
def sample_participant():
    """Fixture providing a sample Participant for testing."""
    return Participant(
        full_name_ru="Иван Иванов",
        full_name_en="Ivan Ivanov",
        contact_information="ivan@example.com",
        role=Role.CANDIDATE,
        department=Department.CHAPEL
    )


@pytest.fixture
def sample_participant_with_id():
    """Fixture providing a sample Participant with record_id for testing updates."""
    return Participant(
        record_id="rec123456789012345",
        full_name_ru="Иван Иванов", 
        full_name_en="Ivan Ivanov",
        contact_information="ivan@example.com",
        role=Role.CANDIDATE
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
    async def test_create_participant_success(self, repository, mock_airtable_client, sample_participant):
        """Test successful participant creation."""
        # Mock find_by_contact_information to return None (no duplicate)
        with patch.object(repository, 'find_by_contact_information', return_value=None):
            result = await repository.create(sample_participant)
        
        # Should call client.create_record with Airtable fields
        mock_airtable_client.create_record.assert_called_once()
        
        # Result should be a Participant with record_id
        assert isinstance(result, Participant)
        assert result.record_id == "rec123456789012345"
        assert result.full_name_ru == "Иван Иванов"
    
    @pytest.mark.asyncio
    async def test_create_participant_duplicate_email(self, repository, mock_airtable_client, sample_participant):
        """Test creation fails when participant with email already exists."""
        # Mock find_by_contact_information to return existing participant
        with patch.object(repository, 'find_by_contact_information', return_value=sample_participant):
            with pytest.raises(DuplicateError) as exc_info:
                await repository.create(sample_participant)
            
            assert "already exists" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_participant_validation_error(self, repository, mock_airtable_client, sample_participant):
        """Test creation with validation error from Airtable."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []
        
        # Mock Airtable API error with 422 status
        mock_airtable_client.create_record.side_effect = AirtableAPIError(
            "Validation failed", 
            status_code=422
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await repository.create(sample_participant)
        
        assert "Invalid participant data" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_participant_api_error(self, repository, mock_airtable_client, sample_participant):
        """Test creation with general API error."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []
        
        mock_airtable_client.create_record.side_effect = AirtableAPIError("Server error")
        
        with pytest.raises(RepositoryError) as exc_info:
            await repository.create(sample_participant)
        
        assert "Failed to create participant" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_participant_unexpected_error(self, repository, mock_airtable_client, sample_participant):
        """Test creation with unexpected error."""
        # Mock the duplicate check to return None (no duplicate found)
        mock_airtable_client.search_by_field.return_value = []
        
        mock_airtable_client.create_record.side_effect = RuntimeError("Unexpected error")
        
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
    async def test_update_participant_success(self, repository, mock_airtable_client, sample_participant_with_id):
        """Test successful participant update."""
        result = await repository.update(sample_participant_with_id)
        
        mock_airtable_client.update_record.assert_called_once()
        call_args = mock_airtable_client.update_record.call_args
        assert call_args[0][0] == "rec123456789012345"  # record_id
        
        assert isinstance(result, Participant)
        assert result.record_id == "rec123456789012345"
    
    @pytest.mark.asyncio
    async def test_update_participant_no_record_id(self, repository, sample_participant):
        """Test update fails without record_id."""
        with pytest.raises(ValidationError) as exc_info:
            await repository.update(sample_participant)
        
        assert "without record_id" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_participant_not_found(self, repository, mock_airtable_client, sample_participant_with_id):
        """Test update with participant not found."""
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Not found", 
            status_code=404
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await repository.update(sample_participant_with_id)
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_update_participant_validation_error(self, repository, mock_airtable_client, sample_participant_with_id):
        """Test update with validation error."""
        mock_airtable_client.update_record.side_effect = AirtableAPIError(
            "Validation failed",
            status_code=422
        )
        
        with pytest.raises(ValidationError) as exc_info:
            await repository.update(sample_participant_with_id)
        
        assert "Invalid participant data" in str(exc_info.value)


class TestAirtableParticipantRepositoryDelete:
    """Test suite for delete operations."""
    
    @pytest.mark.asyncio
    async def test_delete_participant_success(self, repository, mock_airtable_client, sample_participant_with_id):
        """Test successful participant deletion."""
        # Mock get_by_id to return existing participant
        with patch.object(repository, 'get_by_id', return_value=sample_participant_with_id):
            result = await repository.delete("rec123456789012345")
        
        mock_airtable_client.delete_record.assert_called_once_with("rec123456789012345")
        assert result is True
    
    @pytest.mark.asyncio
    async def test_delete_participant_not_found(self, repository, mock_airtable_client):
        """Test delete when participant not found."""
        # Mock get_by_id to return None
        with patch.object(repository, 'get_by_id', return_value=None):
            with pytest.raises(NotFoundError) as exc_info:
                await repository.delete("nonexistent")
        
        assert "not found" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_delete_participant_api_error(self, repository, mock_airtable_client):
        """Test delete with API error."""
        mock_airtable_client.delete_record.side_effect = AirtableAPIError(
            "Not found",
            status_code=404
        )
        
        with pytest.raises(NotFoundError) as exc_info:
            await repository.delete("rec123")
        
        assert "not found" in str(exc_info.value)


class TestAirtableParticipantRepositorySearch:
    """Test suite for search operations."""
    
    @pytest.mark.asyncio
    async def test_find_by_contact_information_success(self, repository, mock_airtable_client):
        """Test successful find by contact information."""
        result = await repository.find_by_contact_information("ivan@example.com")
        
        mock_airtable_client.search_by_field.assert_called_once_with("Contact Information", "ivan@example.com")
        
        assert isinstance(result, Participant)
        assert result.contact_information == "ivan@example.com"
    
    @pytest.mark.asyncio
    async def test_find_by_contact_information_not_found(self, repository, mock_airtable_client):
        """Test find by contact information when not found."""
        mock_airtable_client.search_by_field.return_value = []
        
        result = await repository.find_by_contact_information("notfound@example.com")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_find_by_telegram_id_success(self, repository, mock_airtable_client):
        """Test successful find by Telegram ID."""
        result = await repository.find_by_telegram_id(12345)
        
        mock_airtable_client.search_by_field.assert_called_once_with("Telegram ID", 12345)
        
        assert isinstance(result, Participant)
    
    @pytest.mark.asyncio
    async def test_search_by_name_success(self, repository, mock_airtable_client):
        """Test successful search by name pattern."""
        result = await repository.search_by_name("Иван")
        
        # Should call search_by_formula with proper formula
        mock_airtable_client.search_by_formula.assert_called_once()
        call_args = mock_airtable_client.search_by_formula.call_args[0][0]
        assert "SEARCH('Иван'" in call_args
        assert "Full Name (RU)" in call_args
        assert "Full Name (EN)" in call_args
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)
    
    @pytest.mark.asyncio
    async def test_find_by_role_success(self, repository, mock_airtable_client):
        """Test successful find by role."""
        result = await repository.find_by_role("CANDIDATE")
        
        mock_airtable_client.search_by_field.assert_called_once_with("Role", "CANDIDATE")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)
    
    @pytest.mark.asyncio
    async def test_find_by_department_success(self, repository, mock_airtable_client):
        """Test successful find by department."""
        result = await repository.find_by_department("Chapel")
        
        mock_airtable_client.search_by_field.assert_called_once_with("Department", "Chapel")
        
        assert isinstance(result, list)
        assert len(result) == 1
        assert isinstance(result[0], Participant)


class TestAirtableParticipantRepositoryBulkOperations:
    """Test suite for bulk operations."""
    
    @pytest.mark.asyncio
    async def test_bulk_create_success(self, repository, mock_airtable_client):
        """Test successful bulk create."""
        participants = [
            Participant(full_name_ru="Участник 1", role=Role.CANDIDATE),
            Participant(full_name_ru="Участник 2", role=Role.TEAM)
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
            "Validation failed",
            status_code=422
        )
        
        participants = [Participant(full_name_ru="Test", role=Role.CANDIDATE)]
        
        with pytest.raises(ValidationError) as exc_info:
            await repository.bulk_create(participants)
        
        assert "Invalid participant data in bulk create" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_bulk_update_success(self, repository, mock_airtable_client):
        """Test successful bulk update."""
        participants = [
            Participant(record_id="rec123456789012345", full_name_ru="Обновленный 1", role=Role.CANDIDATE)
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
        mock_airtable_client.test_connection.side_effect = AirtableAPIError("Connection failed")
        
        with pytest.raises(RepositoryError) as exc_info:
            await repository.health_check()
        
        assert "Repository health check failed" in str(exc_info.value)


class TestAirtableParticipantRepositoryErrorHandling:
    """Test suite for comprehensive error handling scenarios."""
    
    @pytest.mark.asyncio
    async def test_search_api_errors_convert_to_repository_errors(self, repository, mock_airtable_client):
        """Test that search API errors are properly converted to RepositoryError."""
        mock_airtable_client.search_by_field.side_effect = AirtableAPIError("Search failed")
        
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
        mock_airtable_client.search_by_formula.side_effect = AirtableAPIError("Formula search failed")
        
        with pytest.raises(RepositoryError):
            await repository.search_by_name("Test")
    
    @pytest.mark.asyncio
    async def test_invalid_records_are_skipped_in_list_operations(self, repository, mock_airtable_client):
        """Test that invalid records are skipped and logged during list operations."""
        # Mock list_records to return some valid and some invalid records
        mock_airtable_client.list_records.return_value = [
            {
                "id": "rec123456789012345",
                "fields": {"FullNameRU": "Valid Participant", "Role": "CANDIDATE"}
            },
            {
                "id": "rec234567890123456", 
                "fields": {"Invalid": "Record"}  # Missing required fields
            },
            {
                "id": "rec345678901234567",
                "fields": {"FullNameRU": "Another Valid", "Role": "TEAM"}
            }
        ]
        
        with patch('src.data.airtable.airtable_participant_repo.logger') as mock_logger:
            result = await repository.list_all()
        
        # Should return only valid participants
        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        
        # Should log warning for invalid record
        mock_logger.warning.assert_called_once()
        warning_call = mock_logger.warning.call_args[0][0]
        assert "Skipping invalid participant record" in warning_call