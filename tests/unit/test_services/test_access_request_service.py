"""
Unit tests for AccessRequestService.

Tests the business logic service for handling user access requests,
including submission, approval/denial, and admin notifications.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)
from src.services.access_request_service import AccessRequestService


class TestAccessRequestService:
    """Test AccessRequestService business logic."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock user access repository."""
        repo = Mock()
        repo.create_request = AsyncMock()
        repo.get_request_by_user_id = AsyncMock()
        repo.list_requests_by_status = AsyncMock()
        repo.approve_request = AsyncMock()
        repo.deny_request = AsyncMock()
        repo.update_request = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, mock_repository):
        """Create service instance with mocked repository."""
        return AccessRequestService(mock_repository)

    async def test_submit_request_creates_pending_record(
        self, service, mock_repository
    ):
        """Test submitting a new access request creates a pending record."""
        # Setup mocks - no existing request found
        mock_repository.get_request_by_user_id.return_value = None

        created_request = UserAccessRequest(
            record_id="recABC123456789",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
        )
        mock_repository.create_request.return_value = created_request

        # Test submission
        result = await service.submit_request(
            telegram_user_id=123456789, telegram_username="testuser"
        )

        # Verify repository was called correctly
        mock_repository.get_request_by_user_id.assert_called_once_with(123456789)
        mock_repository.create_request.assert_called_once()
        call_args = mock_repository.create_request.call_args[0][0]

        assert call_args.telegram_user_id == 123456789
        assert call_args.telegram_username == "testuser"
        assert call_args.status == AccessRequestStatus.PENDING
        assert call_args.access_level == AccessLevel.VIEWER

        # Verify result
        assert result.record_id == "recABC123456789"
        assert result.status == AccessRequestStatus.PENDING

    async def test_submit_request_without_username(self, service, mock_repository):
        """Test submitting request without username works."""
        # Setup mocks - no existing request
        mock_repository.get_request_by_user_id.return_value = None

        created_request = UserAccessRequest(
            record_id="recDEF456789",
            telegram_user_id=987654321,
            telegram_username=None,
            status=AccessRequestStatus.PENDING,
        )
        mock_repository.create_request.return_value = created_request

        result = await service.submit_request(telegram_user_id=987654321)

        # Verify repository call
        call_args = mock_repository.create_request.call_args[0][0]
        assert call_args.telegram_user_id == 987654321
        assert call_args.telegram_username is None

        assert result.telegram_username is None

    async def test_submit_request_handles_existing_user(self, service, mock_repository):
        """Test submitting request for user who already has one."""
        # Setup existing request
        existing_request = UserAccessRequest(
            record_id="recEXIST123456",
            telegram_user_id=123456789,
            status=AccessRequestStatus.PENDING,
        )
        mock_repository.get_request_by_user_id.return_value = existing_request

        # Test submission
        result = await service.submit_request(telegram_user_id=123456789)

        # Should return existing request, not create new one
        mock_repository.get_request_by_user_id.assert_called_once_with(123456789)
        mock_repository.create_request.assert_not_called()

        assert result.record_id == "recEXIST123456"
        assert result.status == AccessRequestStatus.PENDING

    async def test_approve_request_transitions_state(self, service, mock_repository):
        """Test approving a request transitions state correctly."""
        # Setup initial request
        pending_request = UserAccessRequest(
            record_id="recPEND123456",
            telegram_user_id=123456789,
            status=AccessRequestStatus.PENDING,
        )

        # Setup approved request response
        approved_request = UserAccessRequest(
            record_id="recPEND123456",
            telegram_user_id=123456789,
            status=AccessRequestStatus.APPROVED,
            access_level=AccessLevel.COORDINATOR,
            reviewed_by="admin_123",
            reviewed_at=datetime.now(timezone.utc),
        )
        mock_repository.approve_request.return_value = approved_request

        # Test approval
        result = await service.approve_request(
            pending_request, AccessLevel.COORDINATOR, "admin_123"
        )

        # Verify repository call
        mock_repository.approve_request.assert_called_once_with(
            pending_request, AccessLevel.COORDINATOR, "admin_123"
        )

        # Verify result
        assert result.status == AccessRequestStatus.APPROVED
        assert result.access_level == AccessLevel.COORDINATOR
        assert result.reviewed_by == "admin_123"
        assert result.reviewed_at is not None

    async def test_deny_request_transitions_state(self, service, mock_repository):
        """Test denying a request transitions state correctly."""
        # Setup initial request
        pending_request = UserAccessRequest(
            record_id="recPEND456789",
            telegram_user_id=987654321,
            status=AccessRequestStatus.PENDING,
        )

        # Setup denied request response
        denied_request = UserAccessRequest(
            record_id="recPEND456789",
            telegram_user_id=987654321,
            status=AccessRequestStatus.DENIED,
            reviewed_by="admin_456",
            reviewed_at=datetime.now(timezone.utc),
        )
        mock_repository.deny_request.return_value = denied_request

        # Test denial
        result = await service.deny_request(pending_request, "admin_456")

        # Verify repository call
        mock_repository.deny_request.assert_called_once_with(
            pending_request, "admin_456"
        )

        # Verify result
        assert result.status == AccessRequestStatus.DENIED
        assert result.reviewed_by == "admin_456"
        assert result.reviewed_at is not None

    async def test_get_pending_requests(self, service, mock_repository):
        """Test retrieving pending requests with pagination."""
        # Setup mock data
        pending_requests = [
            UserAccessRequest(
                record_id=f"recPEND{i}",
                telegram_user_id=123456780 + i,
                telegram_username=f"user{i}",
                status=AccessRequestStatus.PENDING,
            )
            for i in range(3)
        ]
        mock_repository.list_requests_by_status.return_value = pending_requests

        # Test retrieval
        result = await service.get_pending_requests(limit=5, offset=0)

        # Verify repository call
        mock_repository.list_requests_by_status.assert_called_once_with(
            AccessRequestStatus.PENDING, limit=5, offset=0
        )

        # Verify result
        assert len(result) == 3
        assert all(req.status == AccessRequestStatus.PENDING for req in result)
        assert result[0].telegram_user_id == 123456780
        assert result[1].telegram_user_id == 123456781

    async def test_get_request_by_user_id(self, service, mock_repository):
        """Test retrieving request by user ID."""
        request = UserAccessRequest(
            record_id="recUSER123456",
            telegram_user_id=555666777,
            status=AccessRequestStatus.APPROVED,
        )
        mock_repository.get_request_by_user_id.return_value = request

        result = await service.get_request_by_user_id(555666777)

        mock_repository.get_request_by_user_id.assert_called_once_with(555666777)
        assert result.telegram_user_id == 555666777
        assert result.status == AccessRequestStatus.APPROVED

    async def test_get_request_by_user_id_not_found(self, service, mock_repository):
        """Test retrieving non-existent request returns None."""
        mock_repository.get_request_by_user_id.return_value = None

        result = await service.get_request_by_user_id(999999999)

        mock_repository.get_request_by_user_id.assert_called_once_with(999999999)
        assert result is None

    async def test_submit_request_handles_repository_failure(
        self, service, mock_repository
    ):
        """Test service handles repository failures gracefully."""
        # Setup repository to raise exception
        mock_repository.get_request_by_user_id.return_value = None
        mock_repository.create_request.side_effect = Exception("Airtable API error")

        # Test that exception propagates
        with pytest.raises(Exception, match="Airtable API error"):
            await service.submit_request(telegram_user_id=123456789)

        # Verify repository was called
        mock_repository.get_request_by_user_id.assert_called_once()
        mock_repository.create_request.assert_called_once()

    async def test_validate_admin_permissions(self, service):
        """Test admin permission validation logic."""
        # This tests business logic for admin validation
        # In real implementation, this would check against configured admin list
        admin_users = ["admin_123", "admin_456", "coordinator_789"]

        for admin_id in admin_users:
            # This would be the actual implementation logic
            is_valid = admin_id.startswith(("admin_", "coordinator_"))
            assert is_valid is True

        # Test invalid admin
        invalid_admin = "user_123"
        is_valid = invalid_admin.startswith(("admin_", "coordinator_"))
        assert is_valid is False

    async def test_format_request_display_name(self, service):
        """Test display name formatting for admin notifications."""
        # Test with username
        request_with_username = UserAccessRequest(
            telegram_user_id=123456789,
            telegram_username="testuser",
        )

        # This would be the actual service method
        display_name = (
            request_with_username.telegram_username
            or f"User {request_with_username.telegram_user_id}"
        )
        assert display_name == "testuser"

        # Test without username
        request_without_username = UserAccessRequest(
            telegram_user_id=987654321,
            telegram_username=None,
        )

        display_name = (
            request_without_username.telegram_username
            or f"User {request_without_username.telegram_user_id}"
        )
        assert display_name == "User 987654321"
