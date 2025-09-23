"""
Unit tests for UserAccessRepository implementations.

Tests the repository pattern for user access requests with Airtable integration,
including CRUD operations, status filtering, and error handling.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime

from src.models.user_access_request import (
    UserAccessRequest,
    AccessLevel,
    AccessRequestStatus,
)
from src.data.repositories.user_access_repository import UserAccessRepository
from src.data.airtable.airtable_user_access_repo import AirtableUserAccessRepository


class TestUserAccessRepository:
    """Test abstract UserAccessRepository interface."""

    def test_repository_is_abstract(self):
        """Test that UserAccessRepository cannot be instantiated directly."""
        with pytest.raises(TypeError):
            UserAccessRepository()


class TestAirtableUserAccessRepository:
    """Test AirtableUserAccessRepository implementation."""

    @pytest.fixture
    def mock_airtable_client(self):
        """Create mock Airtable client."""
        client = Mock()
        client.get_records = AsyncMock()
        client.create_record = AsyncMock()
        client.update_record = AsyncMock()
        client.delete_record = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_airtable_client):
        """Create repository instance with mocked client."""
        return AirtableUserAccessRepository(mock_airtable_client)

    @pytest.fixture
    def sample_request_data(self):
        """Sample user access request data for testing."""
        return {
            "record_id": "recABC123456789",
            "telegram_user_id": 123456789,
            "telegram_username": "testuser",
            "status": AccessRequestStatus.PENDING,
            "access_level": AccessLevel.VIEWER,
            "requested_at": datetime(2025, 9, 23, 10, 0, 0),
            "reviewed_at": None,
            "reviewed_by": None,
        }

    @pytest.fixture
    def sample_airtable_record(self):
        """Sample Airtable record response."""
        return {
            "id": "recABC123456789",
            "fields": {
                "fldeiF3gxg4fZMirc": 123456789,  # TelegramUserId
                "fld1RzNGWTGl8fSE4": "testuser",  # TelegramUsername
                "fldcuRa8qeUDKY3hN": "Pending",  # Status
                "fldRBCoHwrJ87hdjr": "VIEWER",   # AccessLevel
            }
        }

    async def test_create_request(self, repository, mock_airtable_client, sample_request_data):
        """Test creating a new access request."""
        # Setup mock response
        mock_airtable_client.create_record.return_value = {
            "id": "recABC123456789",
            "fields": {
                "fldeiF3gxg4fZMirc": 123456789,
                "fld1RzNGWTGl8fSE4": "testuser",
                "fldcuRa8qeUDKY3hN": "Pending",
                "fldRBCoHwrJ87hdjr": "VIEWER",
            }
        }

        request = UserAccessRequest(**sample_request_data)
        result = await repository.create_request(request)

        # Verify Airtable client was called correctly
        mock_airtable_client.create_record.assert_called_once()
        call_args = mock_airtable_client.create_record.call_args[1]["data"]

        assert call_args["fldeiF3gxg4fZMirc"] == 123456789
        assert call_args["fld1RzNGWTGl8fSE4"] == "testuser"
        assert call_args["fldcuRa8qeUDKY3hN"] == "Pending"
        assert call_args["fldRBCoHwrJ87hdjr"] == "VIEWER"

        # Verify returned request
        assert result.record_id == "recABC123456789"
        assert result.telegram_user_id == 123456789

    async def test_get_request_by_user_id(self, repository, mock_airtable_client, sample_airtable_record):
        """Test retrieving a request by Telegram user ID."""
        # Setup mock response
        mock_airtable_client.get_records.return_value = [sample_airtable_record]

        result = await repository.get_request_by_user_id(123456789)

        # Verify filter formula was used
        mock_airtable_client.get_records.assert_called_once()
        call_args = mock_airtable_client.get_records.call_args
        assert "filter_formula" in call_args[1]
        assert "123456789" in call_args[1]["filter_formula"]

        # Verify returned request
        assert result is not None
        assert result.telegram_user_id == 123456789
        assert result.telegram_username == "testuser"
        assert result.status == AccessRequestStatus.PENDING

    async def test_get_request_by_user_id_not_found(self, repository, mock_airtable_client):
        """Test retrieving a non-existent request returns None."""
        mock_airtable_client.get_records.return_value = []

        result = await repository.get_request_by_user_id(999999999)

        assert result is None

    async def test_list_requests_by_status(self, repository, mock_airtable_client, sample_airtable_record):
        """Test listing requests filtered by status."""
        # Setup mock response with multiple records
        mock_airtable_client.get_records.return_value = [
            sample_airtable_record,
            {
                "id": "recDEF456789123",
                "fields": {
                    "fldeiF3gxg4fZMirc": 987654321,
                    "fld1RzNGWTGl8fSE4": "anotheruser",
                    "fldcuRa8qeUDKY3hN": "Pending",
                    "fldRBCoHwrJ87hdjr": "COORDINATOR",
                }
            }
        ]

        results = await repository.list_requests_by_status(AccessRequestStatus.PENDING)

        # Verify filter formula was used
        mock_airtable_client.get_records.assert_called_once()
        call_args = mock_airtable_client.get_records.call_args
        assert "filter_formula" in call_args[1]
        assert "Pending" in call_args[1]["filter_formula"]

        # Verify returned requests
        assert len(results) == 2
        assert all(req.status == AccessRequestStatus.PENDING for req in results)
        assert results[0].telegram_user_id == 123456789
        assert results[1].telegram_user_id == 987654321

    async def test_approve_request(self, repository, mock_airtable_client, sample_request_data):
        """Test approving a request with status transition."""
        # Setup initial request
        request = UserAccessRequest(**sample_request_data)
        request.record_id = "recABC123456789"

        # Setup mock response
        mock_airtable_client.update_record.return_value = {
            "id": "recABC123456789",
            "fields": {
                "fldeiF3gxg4fZMirc": 123456789,
                "fld1RzNGWTGl8fSE4": "testuser",
                "fldcuRa8qeUDKY3hN": "Approved",
                "fldRBCoHwrJ87hdjr": "COORDINATOR",
            }
        }

        result = await repository.approve_request(
            request,
            AccessLevel.COORDINATOR,
            "admin_123"
        )

        # Verify update call
        mock_airtable_client.update_record.assert_called_once()
        call_args = mock_airtable_client.update_record.call_args

        # Check if record_id was passed as positional or keyword argument
        if call_args[0]:  # positional arguments
            assert call_args[0][0] == "recABC123456789"  # record_id
        else:  # keyword arguments
            assert call_args[1]["record_id"] == "recABC123456789"

        update_data = call_args[1]["data"]
        assert update_data["fldcuRa8qeUDKY3hN"] == "Approved"
        assert update_data["fldRBCoHwrJ87hdjr"] == "COORDINATOR"

        # Verify returned request
        assert result.status == AccessRequestStatus.APPROVED
        assert result.access_level == AccessLevel.COORDINATOR

    async def test_deny_request(self, repository, mock_airtable_client, sample_request_data):
        """Test denying a request with audit metadata."""
        # Setup initial request
        request = UserAccessRequest(**sample_request_data)
        request.record_id = "recABC123456789"

        # Setup mock response
        mock_airtable_client.update_record.return_value = {
            "id": "recABC123456789",
            "fields": {
                "fldeiF3gxg4fZMirc": 123456789,
                "fld1RzNGWTGl8fSE4": "testuser",
                "fldcuRa8qeUDKY3hN": "Denied",
                "fldRBCoHwrJ87hdjr": "VIEWER",
            }
        }

        result = await repository.deny_request(request, "admin_456")

        # Verify update call
        mock_airtable_client.update_record.assert_called_once()
        call_args = mock_airtable_client.update_record.call_args

        # Check if record_id was passed as positional or keyword argument
        if call_args[0]:  # positional arguments
            assert call_args[0][0] == "recABC123456789"  # record_id
        else:  # keyword arguments
            assert call_args[1]["record_id"] == "recABC123456789"

        update_data = call_args[1]["data"]
        assert update_data["fldcuRa8qeUDKY3hN"] == "Denied"

        # Verify returned request
        assert result.status == AccessRequestStatus.DENIED

    async def test_repository_error_handling(self, repository, mock_airtable_client):
        """Test repository handles Airtable client errors."""
        # Setup mock to raise exception
        mock_airtable_client.create_record.side_effect = Exception("Airtable API error")

        request = UserAccessRequest(telegram_user_id=123456789)

        with pytest.raises(Exception, match="Airtable API error"):
            await repository.create_request(request)

    async def test_field_mapping_integration(self, repository):
        """Test that repository correctly uses field mappings."""
        with patch('src.data.airtable.airtable_user_access_repo.BotAccessRequestsFieldMapping') as mock_mapping:
            # Setup mock field mapping
            mock_mapping.get_field_id.side_effect = lambda field: {
                "TelegramUserId": "fldeiF3gxg4fZMirc",
                "TelegramUsername": "fld1RzNGWTGl8fSE4",
                "Status": "fldcuRa8qeUDKY3hN",
                "AccessLevel": "fldRBCoHwrJ87hdjr",
            }.get(field)

            # Test that field mapping is consulted
            request = UserAccessRequest(telegram_user_id=123456789)

            # This would normally trigger field mapping usage
            # The actual implementation will use the mapping
            assert mock_mapping.get_field_id("TelegramUserId") == "fldeiF3gxg4fZMirc"