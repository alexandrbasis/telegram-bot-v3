"""
Integration tests for admin alert notifications.

Tests the complete flow of notifying admins about new access requests
including error recovery and batch processing.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest
from telegram import Bot
from telegram.error import NetworkError

from src.data.repositories.user_access_repository import UserAccessRepository
from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)
from src.services.access_request_service import AccessRequestService
from src.services.notification_service import NotificationService


@pytest.mark.asyncio
class TestAdminAlerts:
    """Integration tests for admin alert notifications."""

    @pytest.fixture
    def mock_repository(self):
        """Create a mock repository."""
        repo = AsyncMock(spec=UserAccessRepository)
        # Add required methods to the mock
        repo.create_request = AsyncMock()
        repo.get_request_by_user_id = AsyncMock()
        repo.list_requests_by_status = AsyncMock()
        repo.approve_request = AsyncMock()
        repo.deny_request = AsyncMock()
        return repo

    @pytest.fixture
    def bot_mock(self):
        """Create a mock bot instance."""
        bot = AsyncMock(spec=Bot)
        return bot

    @pytest.fixture
    def notification_service(self, bot_mock):
        """Create a NotificationService with test configuration."""
        admin_ids = [100000001, 100000002, 100000003]
        return NotificationService(bot=bot_mock, admin_ids=admin_ids)

    @pytest.fixture
    def access_service(self, mock_repository):
        """Create an AccessRequestService with mock repository."""
        return AccessRequestService(repository=mock_repository)

    async def test_admin_notified_on_new_request(
        self, notification_service, access_service, mock_repository, bot_mock
    ):
        """Test that admins are notified when a new access request is submitted."""
        # Arrange
        new_request = UserAccessRequest(
            record_id="recNewUser",
            telegram_user_id=123456789,
            telegram_username="newuser",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
            requested_at=datetime.now(timezone.utc),
        )

        # Mock repository responses for submit_request flow
        mock_repository.get_request_by_user_id.return_value = (
            None  # No existing request
        )
        mock_repository.create_request.return_value = new_request

        # Act - Submit request and notify admins
        created_request = await access_service.submit_request(
            telegram_user_id=123456789, telegram_username="newuser"
        )

        notification_results = await notification_service.notify_admins_of_new_request(
            created_request
        )

        # Assert
        assert created_request.record_id == "recNewUser"
        assert len(notification_results) == 3  # Three admins configured
        assert all(notification_results.values())  # All notifications successful

        # Verify each admin received the notification
        expected_message = "🔔 Новый запрос на доступ: @newuser (123456789)."
        for admin_id in [100000001, 100000002, 100000003]:
            bot_mock.send_message.assert_any_call(
                chat_id=admin_id, text=expected_message
            )

    async def test_admin_notification_with_network_recovery(
        self, notification_service, bot_mock
    ):
        """Test admin notifications recover from transient network errors."""
        # Arrange
        request = UserAccessRequest(
            record_id="recNetworkTest",
            telegram_user_id=987654321,
            telegram_username="networktest",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
        )

        # Simulate network issues for first admin, success for others
        bot_mock.send_message.side_effect = [
            NetworkError("Temporary network issue"),  # Admin 1 - first attempt
            MagicMock(),  # Admin 1 - retry succeeds
            MagicMock(),  # Admin 2 - succeeds
            MagicMock(),  # Admin 3 - succeeds
        ]

        # Act
        results = await notification_service.notify_admins_of_new_request(request)

        # Assert
        assert len(results) == 3
        # First admin should succeed after retry
        assert results[100000001] is True
        assert results[100000002] is True
        assert results[100000003] is True

    async def test_admin_notification_partial_failure(
        self, notification_service, bot_mock
    ):
        """Test handling when some admin notifications fail permanently."""
        # Arrange
        request = UserAccessRequest(
            record_id="recPartialFail",
            telegram_user_id=555666777,
            telegram_username="partialfail",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
        )

        # Admin 2 has permanent failure (e.g., blocked bot)
        def send_message_side_effect(chat_id, text):
            if chat_id == 100000002:
                raise NetworkError("User has blocked bot")
            return MagicMock()

        bot_mock.send_message.side_effect = send_message_side_effect

        # Act
        results = await notification_service.notify_admins_of_new_request(request)

        # Assert
        assert results[100000001] is True  # First admin succeeded
        assert results[100000002] is False  # Second admin failed
        assert results[100000003] is True  # Third admin succeeded

    async def test_bulk_admin_notifications_for_multiple_requests(
        self, notification_service, bot_mock
    ):
        """Test sending notifications for multiple pending requests."""
        # Arrange
        requests = [
            UserAccessRequest(
                record_id=f"recBulk{i}",
                telegram_user_id=111000 + i,
                telegram_username=f"bulkuser{i}",
                status=AccessRequestStatus.PENDING,
                access_level=AccessLevel.VIEWER,
            )
            for i in range(5)
        ]

        # Act
        all_results = []
        for request in requests:
            results = await notification_service.notify_admins_of_new_request(request)
            all_results.append(results)

        # Assert
        assert len(all_results) == 5
        for results in all_results:
            assert len(results) == 3  # Three admins
            assert all(results.values())  # All successful

        # Verify total calls (5 requests × 3 admins = 15 calls)
        assert bot_mock.send_message.call_count == 15

    async def test_admin_alert_formatting_with_display_name(
        self, notification_service, bot_mock
    ):
        """Test that admin alerts use proper display name formatting."""
        # Arrange
        test_cases = [
            # (username, expected_display)
            ("johndoe", "@johndoe"),
            (None, "User"),
            ("", "User"),
        ]

        for username, expected_display in test_cases:
            bot_mock.reset_mock()

            request = UserAccessRequest(
                record_id="recFormat",
                telegram_user_id=999888777,
                telegram_username=username,
                status=AccessRequestStatus.PENDING,
                access_level=AccessLevel.VIEWER,
            )

            # Act
            await notification_service.notify_admins_of_new_request(request)

            # Assert
            expected_text = (
                f"🔔 Новый запрос на доступ: {expected_display} (999888777)."
            )
            bot_mock.send_message.assert_any_call(chat_id=100000001, text=expected_text)

    async def test_concurrent_admin_notifications(self, notification_service, bot_mock):
        """Test that notifications to multiple admins are sent concurrently."""
        # Arrange
        import asyncio

        request = UserAccessRequest(
            record_id="recConcurrent",
            telegram_user_id=777888999,
            telegram_username="concurrent",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
        )

        # Track timing of calls
        call_times = []

        async def mock_send_message(chat_id, text):
            call_times.append(asyncio.get_event_loop().time())
            await asyncio.sleep(0.1)  # Simulate network delay
            return MagicMock()

        bot_mock.send_message.side_effect = mock_send_message

        # Act
        start_time = asyncio.get_event_loop().time()
        results = await notification_service.notify_admins_of_new_request(request)
        end_time = asyncio.get_event_loop().time()

        # Assert
        assert all(results.values())
        # If sequential, would take ~0.3s (3 × 0.1s)
        # If concurrent, should take ~0.1s
        total_time = end_time - start_time
        assert total_time < 0.2  # Allow some overhead

    async def test_admin_notification_logging_on_error(
        self, notification_service, bot_mock, caplog
    ):
        """Test that errors during admin notification are properly logged."""
        import logging

        # Arrange
        request = UserAccessRequest(
            record_id="recLogTest",
            telegram_user_id=333444555,
            telegram_username="logtest",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
        )

        bot_mock.send_message.side_effect = NetworkError("Connection refused")

        # Act
        with caplog.at_level(logging.WARNING):  # Capture WARNING and above
            results = await notification_service.notify_admins_of_new_request(request)

        # Assert
        assert all(not success for success in results.values())
        # Check for warnings or errors in the log
        assert "Connection refused" in caplog.text or "Network error" in caplog.text
