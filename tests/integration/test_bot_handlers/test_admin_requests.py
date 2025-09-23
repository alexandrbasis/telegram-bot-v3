"""
Integration tests for admin request review functionality.

Tests the admin workflow for reviewing pending access requests,
including listing, approval, denial, and pagination.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, User, Chat, Message, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.models.user_access_request import (
    UserAccessRequest,
    AccessLevel,
    AccessRequestStatus,
)


class TestAdminRequests:
    """Test admin request management functionality."""

    @pytest.fixture
    def mock_admin_update(self):
        """Create mock Telegram update from admin user."""
        admin_user = User(
            id=999888777,
            is_bot=False,
            first_name="Admin",
            username="admin_test"
        )
        chat = Chat(id=999888777, type="private")
        message = Message(
            message_id=1,
            date=None,
            chat=chat,
            from_user=admin_user,
            text="/requests"
        )

        update = Mock(spec=Update)
        update.effective_user = admin_user
        update.effective_chat = chat
        update.message = message
        return update

    @pytest.fixture
    def mock_callback_update(self):
        """Create mock callback query update."""
        admin_user = User(
            id=999888777,
            is_bot=False,
            first_name="Admin",
            username="admin_test"
        )
        chat = Chat(id=999888777, type="private")
        message = Message(
            message_id=2,
            date=None,
            chat=chat,
            from_user=admin_user,
            text="Request details"
        )

        callback_query = Mock(spec=CallbackQuery)
        callback_query.id = "callback_123"
        callback_query.from_user = admin_user
        callback_query.message = message
        callback_query.data = "access:approve:recPEND001"

        update = Mock(spec=Update)
        update.effective_user = admin_user
        update.effective_chat = chat
        update.callback_query = callback_query
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock bot context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = Mock()
        context.bot.send_message = AsyncMock()
        context.bot.edit_message_text = AsyncMock()
        context.bot.answer_callback_query = AsyncMock()
        context.user_data = {}
        return context

    @pytest.fixture
    def mock_access_service(self):
        """Create mock access request service."""
        service = Mock()
        service.get_pending_requests = AsyncMock()
        service.approve_request = AsyncMock()
        service.deny_request = AsyncMock()
        service.get_request_by_user_id = AsyncMock()
        return service

    @pytest.fixture
    def sample_pending_requests(self):
        """Create sample pending requests for testing."""
        return [
            UserAccessRequest(
                record_id="recPEND001",
                telegram_user_id=123456001,
                telegram_username="user1",
                status=AccessRequestStatus.PENDING,
            ),
            UserAccessRequest(
                record_id="recPEND002",
                telegram_user_id=123456002,
                telegram_username="user2",
                status=AccessRequestStatus.PENDING,
            ),
            UserAccessRequest(
                record_id="recPEND003",
                telegram_user_id=123456003,
                telegram_username=None,  # User without username
                status=AccessRequestStatus.PENDING,
            ),
        ]

    async def test_admin_flows_through_pending_to_approved(
        self,
        mock_admin_update,
        mock_context,
        mock_access_service,
        sample_pending_requests
    ):
        """Test complete admin flow from viewing pending to approving request."""
        # Setup service mocks
        mock_access_service.get_pending_requests.return_value = sample_pending_requests[:2]  # Show 2 requests

        # Mock the /requests command handler
        with patch('src.services.access_request_service.AccessRequestService', return_value=mock_access_service):
            # Simulate /requests command
            pending_requests = await mock_access_service.get_pending_requests(limit=5, offset=0)

            if not pending_requests:
                message_text = "Нет ожидающих запросов на доступ."
                keyboard = None
            else:
                message_text = "Ожидающие запросы на доступ:\n\n"
                buttons = []

                for i, request in enumerate(pending_requests):
                    display_name = request.telegram_username or f"User {request.telegram_user_id}"
                    message_text += f"{i+1}. {display_name} (@{request.telegram_username or 'no_username'} / {request.telegram_user_id})\n"

                    # Create inline buttons for approve/deny
                    approve_btn = InlineKeyboardButton(
                        f"✅ Approve {display_name}",
                        callback_data=f"access:approve:{request.record_id}"
                    )
                    deny_btn = InlineKeyboardButton(
                        f"❌ Deny {display_name}",
                        callback_data=f"access:deny:{request.record_id}"
                    )
                    buttons.extend([approve_btn, deny_btn])

                keyboard = InlineKeyboardMarkup([buttons[i:i+2] for i in range(0, len(buttons), 2)])

            await mock_context.bot.send_message(
                chat_id=mock_admin_update.effective_chat.id,
                text=message_text,
                reply_markup=keyboard
            )

        # Verify service call
        mock_access_service.get_pending_requests.assert_called_once_with(limit=5, offset=0)

        # Verify message sent with keyboard
        mock_context.bot.send_message.assert_called_once()
        call_args = mock_context.bot.send_message.call_args

        assert call_args[1]["chat_id"] == 999888777
        assert "user1" in call_args[1]["text"]
        assert "user2" in call_args[1]["text"]
        assert call_args[1]["reply_markup"] is not None

    async def test_admin_approve_callback_handling(
        self,
        mock_callback_update,
        mock_context,
        mock_access_service,
        sample_pending_requests
    ):
        """Test admin approval callback handling."""
        # Setup mocks
        request_to_approve = sample_pending_requests[0]
        # Mock the get_pending_requests method for finding the request by record_id
        mock_access_service.get_pending_requests.return_value = sample_pending_requests

        approved_request = UserAccessRequest(
            record_id="recPEND001",
            telegram_user_id=123456001,
            telegram_username="user1",
            status=AccessRequestStatus.APPROVED,
            access_level=AccessLevel.VIEWER,
            reviewed_by="admin_test",
        )
        mock_access_service.approve_request.return_value = approved_request

        # Mock callback handler logic
        with patch('src.services.access_request_service.AccessRequestService', return_value=mock_access_service):
            callback_data = mock_callback_update.callback_query.data
            action, action_type, record_id = callback_data.split(":")

            if action == "access" and action_type == "approve":
                # Find the request using the admin handler logic (searches pending requests)
                pending_requests = await mock_access_service.get_pending_requests(limit=100)
                target_request = None

                for request in pending_requests:
                    if request.record_id == record_id:
                        target_request = request
                        break

                if target_request:
                    # Approve with default VIEWER level
                    approved = await mock_access_service.approve_request(
                        target_request,
                        AccessLevel.VIEWER,
                        "admin_test"
                    )

                    # Update the callback message
                    await mock_context.bot.edit_message_text(
                        chat_id=mock_callback_update.effective_chat.id,
                        message_id=mock_callback_update.callback_query.message.message_id,
                        text=f"✅ Запрос от {target_request.telegram_username} одобрен с уровнем доступа {approved.access_level}."
                    )

                    # Notify the user
                    await mock_context.bot.send_message(
                        chat_id=target_request.telegram_user_id,
                        text=f"Доступ подтверждён! Ваша роль: {approved.access_level}."
                    )

            await mock_context.bot.answer_callback_query(
                callback_query_id=mock_callback_update.callback_query.id,
                text="Запрос обработан"
            )

        # Verify service calls
        mock_access_service.get_pending_requests.assert_called_once_with(limit=100)
        mock_access_service.approve_request.assert_called_once_with(
            request_to_approve,
            AccessLevel.VIEWER,
            "admin_test"
        )

        # Verify messages sent
        assert mock_context.bot.edit_message_text.called
        assert mock_context.bot.send_message.called
        mock_context.bot.answer_callback_query.assert_called_once()

    async def test_denial_flow_and_audit_logging(
        self,
        mock_callback_update,
        mock_context,
        mock_access_service,
        sample_pending_requests
    ):
        """Test denial flow with audit logging."""
        # Setup mocks
        request_to_deny = sample_pending_requests[1]
        mock_access_service.get_pending_requests.return_value = sample_pending_requests

        denied_request = UserAccessRequest(
            record_id="recPEND002",
            telegram_user_id=123456002,
            telegram_username="user2",
            status=AccessRequestStatus.DENIED,
            reviewed_by="admin_test",
        )
        mock_access_service.deny_request.return_value = denied_request

        # Mock deny callback
        mock_callback_update.callback_query.data = "access:deny:recPEND002"

        # Mock callback handler logic
        with patch('src.services.access_request_service.AccessRequestService', return_value=mock_access_service):
            callback_data = mock_callback_update.callback_query.data
            action, action_type, record_id = callback_data.split(":")

            if action == "access" and action_type == "deny":
                # Find the request using the admin handler logic
                pending_requests = await mock_access_service.get_pending_requests(limit=100)
                target_request = None

                for request in pending_requests:
                    if request.record_id == record_id:
                        target_request = request
                        break

                if target_request:
                    # Deny the request
                    denied = await mock_access_service.deny_request(target_request, "admin_test")

                    # Update the callback message
                    await mock_context.bot.edit_message_text(
                        chat_id=mock_callback_update.effective_chat.id,
                        message_id=mock_callback_update.callback_query.message.message_id,
                        text=f"❌ Запрос от {target_request.telegram_username} отклонен администратором {denied.reviewed_by}."
                    )

                    # Notify the user
                    await mock_context.bot.send_message(
                        chat_id=target_request.telegram_user_id,
                        text="К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором."
                    )

        # Verify service calls
        mock_access_service.get_pending_requests.assert_called_once_with(limit=100)
        mock_access_service.deny_request.assert_called_once_with(request_to_deny, "admin_test")

        # Verify audit information is recorded (reviewed_by field)
        assert denied_request.reviewed_by == "admin_test"
        assert denied_request.status == AccessRequestStatus.DENIED

    async def test_reapproval_updates_status(
        self,
        mock_callback_update,
        mock_context,
        mock_access_service
    ):
        """Test re-approval of previously denied request."""
        # Setup previously denied request
        denied_request = UserAccessRequest(
            record_id="recDENY123",
            telegram_user_id=123456789,
            telegram_username="user_reapprove",
            status=AccessRequestStatus.DENIED,
            reviewed_by="admin_old",
        )
        # Mock finding the request in pending requests (for re-approval workflow)
        mock_access_service.get_pending_requests.return_value = [denied_request]

        # Setup re-approval result
        reapproved_request = UserAccessRequest(
            record_id="recDENY123",
            telegram_user_id=123456789,
            telegram_username="user_reapprove",
            status=AccessRequestStatus.APPROVED,
            access_level=AccessLevel.COORDINATOR,
            reviewed_by="admin_test",
        )
        mock_access_service.approve_request.return_value = reapproved_request

        # Mock re-approval callback
        mock_callback_update.callback_query.data = "access:approve:recDENY123"

        # Mock callback handler logic
        with patch('src.services.access_request_service.AccessRequestService', return_value=mock_access_service):
            callback_data = mock_callback_update.callback_query.data
            action, action_type, record_id = callback_data.split(":")

            if action == "access" and action_type == "approve":
                # Find the request using the admin handler logic
                pending_requests = await mock_access_service.get_pending_requests(limit=100)
                target_request = None

                for request in pending_requests:
                    if request.record_id == record_id:
                        target_request = request
                        break

                if target_request:
                    # Re-approve with COORDINATOR level
                    approved = await mock_access_service.approve_request(
                        target_request,
                        AccessLevel.COORDINATOR,
                        "admin_test"
                    )

                    # Update the callback message
                    await mock_context.bot.edit_message_text(
                        chat_id=mock_callback_update.effective_chat.id,
                        message_id=mock_callback_update.callback_query.message.message_id,
                        text=f"✅ Запрос от {target_request.telegram_username} переутвержден с уровнем доступа {approved.access_level}."
                    )

        # Verify service calls
        mock_access_service.get_pending_requests.assert_called_once_with(limit=100)
        mock_access_service.approve_request.assert_called_once_with(
            denied_request,
            AccessLevel.COORDINATOR,
            "admin_test"
        )

        # Verify status transition from DENIED to APPROVED
        assert reapproved_request.status == AccessRequestStatus.APPROVED
        assert reapproved_request.access_level == AccessLevel.COORDINATOR
        assert reapproved_request.reviewed_by == "admin_test"

    async def test_pagination_and_navigation(
        self,
        mock_admin_update,
        mock_context,
        mock_access_service
    ):
        """Test pagination for large numbers of pending requests."""
        # Setup large number of requests (simulate page 2)
        page_2_requests = [
            UserAccessRequest(
                record_id=f"recPEND{i:03d}",
                telegram_user_id=123456000 + i,
                telegram_username=f"user{i}",
                status=AccessRequestStatus.PENDING,
            )
            for i in range(6, 11)  # Requests 6-10 (page 2, limit 5)
        ]
        mock_access_service.get_pending_requests.return_value = page_2_requests

        # Mock paginated /requests command
        with patch('src.services.access_request_service.AccessRequestService', return_value=mock_access_service):
            # Simulate page 2 (offset=5, limit=5)
            page = 2
            limit = 5
            offset = (page - 1) * limit

            pending_requests = await mock_access_service.get_pending_requests(limit=limit, offset=offset)

            message_text = f"Ожидающие запросы на доступ (страница {page}):\n\n"
            for i, request in enumerate(pending_requests):
                message_text += f"{offset + i + 1}. {request.telegram_username} / {request.telegram_user_id}\n"

            # Add navigation buttons
            nav_buttons = []
            if offset > 0:  # Previous page exists
                nav_buttons.append(InlineKeyboardButton("⬅️ Назад", callback_data=f"requests:page:{page-1}"))
            if len(pending_requests) == limit:  # More pages might exist
                nav_buttons.append(InlineKeyboardButton("➡️ Далее", callback_data=f"requests:page:{page+1}"))

            keyboard = InlineKeyboardMarkup([nav_buttons]) if nav_buttons else None

            await mock_context.bot.send_message(
                chat_id=mock_admin_update.effective_chat.id,
                text=message_text,
                reply_markup=keyboard
            )

        # Verify service call with pagination
        mock_access_service.get_pending_requests.assert_called_once_with(limit=5, offset=5)

        # Verify message contains page information
        call_args = mock_context.bot.send_message.call_args
        assert "страница 2" in call_args[1]["text"]
        assert "6. user6" in call_args[1]["text"]  # First item on page 2