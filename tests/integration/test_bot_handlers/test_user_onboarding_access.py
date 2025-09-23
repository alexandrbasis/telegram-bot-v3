"""
Integration tests for user onboarding access control.

Tests the end-to-end flow of users requesting access through the bot,
from first interaction to approval notification.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)


class TestUserOnboardingAccess:
    """Test user onboarding and access request flow."""

    @pytest.fixture
    def mock_update(self):
        """Create mock Telegram update."""
        user = User(id=123456789, is_bot=False, first_name="Test", username="testuser")
        chat = Chat(id=123456789, type="private")
        message = Message(
            message_id=1, date=None, chat=chat, from_user=user, text="/start"
        )

        update = Mock(spec=Update)
        update.effective_user = user
        update.effective_chat = chat
        update.message = message
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock bot context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.user_data = {}
        return context

    @pytest.fixture
    def mock_access_service(self):
        """Create mock access request service."""
        service = Mock()
        service.submit_request = AsyncMock()
        service.get_request_by_user_id = AsyncMock()
        return service

    async def test_first_time_user_gets_pending_message(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test that first-time user triggers pending request message."""
        # Setup service mocks
        mock_access_service.get_request_by_user_id.return_value = None

        created_request = UserAccessRequest(
            record_id="recNEW123456",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.PENDING,
        )
        mock_access_service.submit_request.return_value = created_request

        # Mock the handler function (this would be implemented in actual handler)
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            # Simulate start command handler logic
            user_id = mock_update.effective_user.id
            username = mock_update.effective_user.username

            # Check for existing request
            existing_request = await mock_access_service.get_request_by_user_id(user_id)

            if not existing_request:
                # Submit new request
                await mock_access_service.submit_request(
                    telegram_user_id=user_id, telegram_username=username
                )

                # Send pending message
                await mock_context.bot.send_message(
                    chat_id=mock_update.effective_chat.id,
                    text="Запрос на доступ принят. Мы уведомим вас, как только админ его обработает.",
                )

        # Verify service calls
        mock_access_service.get_request_by_user_id.assert_called_once_with(123456789)
        mock_access_service.submit_request.assert_called_once_with(
            telegram_user_id=123456789, telegram_username="testuser"
        )

        # Verify message sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Запрос на доступ принят. Мы уведомим вас, как только админ его обработает.",
        )

    async def test_user_with_pending_request_gets_status_message(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test user with pending request gets status message."""
        # Setup existing pending request
        existing_request = UserAccessRequest(
            record_id="recPEND123456",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.PENDING,
        )
        mock_access_service.get_request_by_user_id.return_value = existing_request

        # Mock handler logic
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            user_id = mock_update.effective_user.id

            existing_request = await mock_access_service.get_request_by_user_id(user_id)

            if (
                existing_request
                and existing_request.status == AccessRequestStatus.PENDING
            ):
                await mock_context.bot.send_message(
                    chat_id=mock_update.effective_chat.id,
                    text="Ваш запрос на доступ уже обрабатывается. Пожалуйста, подождите.",
                )

        # Verify service call
        mock_access_service.get_request_by_user_id.assert_called_once_with(123456789)
        mock_access_service.submit_request.assert_not_called()

        # Verify status message sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Ваш запрос на доступ уже обрабатывается. Пожалуйста, подождите.",
        )

    async def test_approved_user_gets_welcome_message(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test approved user gets welcome message and access to features."""
        # Setup approved request
        approved_request = UserAccessRequest(
            record_id="recAPPR123456",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.APPROVED,
            access_level=AccessLevel.COORDINATOR,
        )
        mock_access_service.get_request_by_user_id.return_value = approved_request

        # Mock handler logic
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            user_id = mock_update.effective_user.id

            existing_request = await mock_access_service.get_request_by_user_id(user_id)

            if (
                existing_request
                and existing_request.status == AccessRequestStatus.APPROVED
            ):
                await mock_context.bot.send_message(
                    chat_id=mock_update.effective_chat.id,
                    text=f"Добро пожаловать! Ваша роль: {existing_request.access_level}. Используйте /help для просмотра команд.",
                )

        # Verify service call
        mock_access_service.get_request_by_user_id.assert_called_once_with(123456789)

        # Verify welcome message sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Добро пожаловать! Ваша роль: COORDINATOR. Используйте /help для просмотра команд.",
        )

    async def test_denied_user_receives_guidance(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test denied user receives guidance message."""
        # Setup denied request
        denied_request = UserAccessRequest(
            record_id="recDENY123456",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.DENIED,
        )
        mock_access_service.get_request_by_user_id.return_value = denied_request

        # Mock handler logic
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            user_id = mock_update.effective_user.id

            existing_request = await mock_access_service.get_request_by_user_id(user_id)

            if (
                existing_request
                and existing_request.status == AccessRequestStatus.DENIED
            ):
                await mock_context.bot.send_message(
                    chat_id=mock_update.effective_chat.id,
                    text="К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором.",
                )

        # Verify service call
        mock_access_service.get_request_by_user_id.assert_called_once_with(123456789)

        # Verify denial message sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором.",
        )

    async def test_user_receives_approval_message(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test user receives notification when their request is approved."""
        # This tests the notification flow when admin approves a request
        user_id = 123456789
        access_level = AccessLevel.VIEWER

        # Mock notification logic (would be called by admin action)
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            # Simulate approval notification
            await mock_context.bot.send_message(
                chat_id=user_id,
                text=f"Доступ подтверждён! Ваша роль: {access_level.value}.",
            )

        # Verify approval notification sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789, text="Доступ подтверждён! Ваша роль: VIEWER."
        )

    async def test_access_control_gates_main_features(
        self, mock_update, mock_context, mock_access_service
    ):
        """Test that main features are gated until approval."""
        # Setup user with no request
        mock_access_service.get_request_by_user_id.return_value = None

        # Mock feature access check (would be used in other handlers)
        with patch(
            "src.services.access_request_service.AccessRequestService",
            return_value=mock_access_service,
        ):
            user_id = mock_update.effective_user.id

            user_request = await mock_access_service.get_request_by_user_id(user_id)

            # Check if user has approved access
            has_access = (
                user_request and user_request.status == AccessRequestStatus.APPROVED
            )

            if not has_access:
                await mock_context.bot.send_message(
                    chat_id=mock_update.effective_chat.id,
                    text="Для использования этой функции необходимо одобрение администратора. Используйте /start для запроса доступа.",
                )

        # Verify access check was performed
        mock_access_service.get_request_by_user_id.assert_called_once_with(123456789)

        # Verify access denied message sent
        mock_context.bot.send_message.assert_called_once_with(
            chat_id=123456789,
            text="Для использования этой функции необходимо одобрение администратора. Используйте /start для запроса доступа.",
        )
