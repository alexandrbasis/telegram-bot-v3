"""
Unit tests for notification service.

Tests the notification service for admin alerts and user notifications
with retry mechanisms and error handling.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call
from datetime import datetime, timezone
from telegram import Bot, User
from telegram.error import TelegramError, NetworkError, BadRequest

from src.services.notification_service import NotificationService
from src.models.user_access_request import UserAccessRequest, AccessLevel, AccessRequestStatus


@pytest.mark.asyncio
class TestNotificationService:
    """Test suite for NotificationService."""

    @pytest.fixture
    def bot_mock(self):
        """Create a mock bot instance."""
        bot = AsyncMock(spec=Bot)
        return bot

    @pytest.fixture
    def notification_service(self, bot_mock):
        """Create a NotificationService instance with mocked dependencies."""
        admin_ids = [123456789, 987654321]
        return NotificationService(bot=bot_mock, admin_ids=admin_ids)

    @pytest.fixture
    def access_request(self):
        """Create a sample access request."""
        return UserAccessRequest(
            record_id="rec123",
            telegram_user_id=111222333,
            telegram_username="testuser",
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
            requested_at=datetime.now(timezone.utc)
        )

    async def test_notify_admins_of_new_request_sends_to_all_admins(
        self, notification_service, bot_mock, access_request
    ):
        """Test that admin notification is sent to all configured admins."""
        # Act
        results = await notification_service.notify_admins_of_new_request(
            access_request
        )

        # Assert
        assert len(results) == 2  # Two admin IDs configured
        assert all(results.values())  # All notifications successful

        # Verify bot.send_message was called for each admin
        expected_calls = [
            call(
                chat_id=123456789,
                text="🔔 Новый запрос на доступ: @testuser (111222333)."
            ),
            call(
                chat_id=987654321,
                text="🔔 Новый запрос на доступ: @testuser (111222333)."
            )
        ]
        bot_mock.send_message.assert_has_calls(expected_calls, any_order=True)

    async def test_notify_admins_without_username(
        self, notification_service, bot_mock
    ):
        """Test admin notification when user has no username."""
        # Arrange
        request = UserAccessRequest(
            record_id="rec456",
            telegram_user_id=444555666,
            telegram_username=None,
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER
        )

        # Act
        results = await notification_service.notify_admins_of_new_request(request)

        # Assert
        assert all(results.values())
        bot_mock.send_message.assert_any_call(
            chat_id=123456789,
            text="🔔 Новый запрос на доступ: User (444555666)."
        )

    async def test_notify_admins_handles_telegram_error_gracefully(
        self, notification_service, bot_mock, access_request
    ):
        """Test that notification continues for other admins on error."""
        # Arrange
        # Create a side effect function that fails for first admin, succeeds for second
        async def send_message_side_effect(chat_id, text):
            if chat_id == 123456789:
                raise NetworkError("Network unreachable")
            return MagicMock()

        bot_mock.send_message.side_effect = send_message_side_effect

        # Act
        results = await notification_service.notify_admins_of_new_request(
            access_request
        )

        # Assert
        assert results[123456789] is False  # First admin failed after all retries
        assert results[987654321] is True   # Second admin succeeded
        # First admin tries 3 times, second admin succeeds on first try
        assert bot_mock.send_message.call_count == 4

    async def test_notify_user_approval_sends_localized_message(
        self, notification_service, bot_mock, access_request
    ):
        """Test user approval notification with proper localization."""
        # Arrange
        access_request.status = AccessRequestStatus.APPROVED
        access_request.access_level = AccessLevel.COORDINATOR

        # Act
        success = await notification_service.notify_user_decision(
            user_id=access_request.telegram_user_id,
            approved=True,
            access_level=AccessLevel.COORDINATOR,
            language="ru"
        )

        # Assert
        assert success is True
        bot_mock.send_message.assert_called_once_with(
            chat_id=111222333,
            text="✅ Доступ подтверждён! Ваша роль: COORDINATOR.\n\nИспользуйте /start для начала работы с ботом."
        )

    async def test_notify_user_denial_sends_localized_message(
        self, notification_service, bot_mock
    ):
        """Test user denial notification with proper localization."""
        # Act
        success = await notification_service.notify_user_decision(
            user_id=999888777,
            approved=False,
            language="ru"
        )

        # Assert
        assert success is True
        bot_mock.send_message.assert_called_once_with(
            chat_id=999888777,
            text="❌ К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором."
        )

    async def test_notify_user_with_admin_notes(
        self, notification_service, bot_mock
    ):
        """Test notification includes admin notes when provided."""
        # Act
        success = await notification_service.notify_user_decision(
            user_id=555666777,
            approved=True,
            access_level=AccessLevel.VIEWER,
            admin_notes="Добро пожаловать в команду!",
            language="ru"
        )

        # Assert
        assert success is True
        expected_text = (
            "✅ Доступ подтверждён! Ваша роль: VIEWER.\n\n"
            "Комментарий администратора: Добро пожаловать в команду!\n\n"
            "Используйте /start для начала работы с ботом."
        )
        bot_mock.send_message.assert_called_once_with(
            chat_id=555666777,
            text=expected_text
        )

    async def test_notify_with_retry_on_network_error(
        self, notification_service, bot_mock
    ):
        """Test retry mechanism on network errors."""
        # Arrange
        bot_mock.send_message.side_effect = [
            NetworkError("Connection failed"),  # First attempt fails
            NetworkError("Connection failed"),  # Second attempt fails
            MagicMock()  # Third attempt succeeds
        ]

        # Act
        success = await notification_service.notify_user_decision(
            user_id=123123123,
            approved=True,
            access_level=AccessLevel.ADMIN,
            language="ru"
        )

        # Assert
        assert success is True
        assert bot_mock.send_message.call_count == 3  # Three attempts

    async def test_notify_max_retries_exceeded(
        self, notification_service, bot_mock
    ):
        """Test that notification fails after max retries."""
        # Arrange
        bot_mock.send_message.side_effect = NetworkError("Connection failed")

        # Act
        success = await notification_service.notify_user_decision(
            user_id=321321321,
            approved=True,
            language="ru"
        )

        # Assert
        assert success is False
        assert bot_mock.send_message.call_count == 3  # Max retries reached

    async def test_notify_english_localization(
        self, notification_service, bot_mock
    ):
        """Test English language localization."""
        # Act
        success = await notification_service.notify_user_decision(
            user_id=777888999,
            approved=True,
            access_level=AccessLevel.COORDINATOR,
            language="en"
        )

        # Assert
        assert success is True
        bot_mock.send_message.assert_called_once_with(
            chat_id=777888999,
            text="✅ You're all set! Assigned access level: COORDINATOR.\n\nUse /start to begin working with the bot."
        )

    async def test_notify_batch_admin_alerts_all_or_nothing(
        self, notification_service, bot_mock
    ):
        """Test batch admin notification returns individual results."""
        # Arrange
        requests = [
            UserAccessRequest(
                record_id=f"rec{i}",
                telegram_user_id=1000 + i,
                telegram_username=f"user{i}",
                status=AccessRequestStatus.PENDING,
                access_level=AccessLevel.VIEWER
            )
            for i in range(3)
        ]

        # Mock mixed results
        send_results = [True, False, True] * 2  # For 2 admins x 3 requests
        bot_mock.send_message.side_effect = [
            MagicMock() if success else NetworkError("Failed")
            for success in send_results
        ]

        # Act
        all_results = []
        for request in requests:
            results = await notification_service.notify_admins_of_new_request(request)
            all_results.append(results)

        # Assert
        assert len(all_results) == 3
        # Each request should have results for both admins
        for results in all_results:
            assert len(results) == 2

    async def test_notification_with_invalid_chat_id_handles_gracefully(
        self, notification_service, bot_mock
    ):
        """Test handling of invalid chat ID (user blocked bot)."""
        # Arrange
        bot_mock.send_message.side_effect = BadRequest("Chat not found")

        # Act
        success = await notification_service.notify_user_decision(
            user_id=999999999,
            approved=True,
            language="ru"
        )

        # Assert
        assert success is False
        # Should not retry on BadRequest (user blocked bot)
        assert bot_mock.send_message.call_count == 1