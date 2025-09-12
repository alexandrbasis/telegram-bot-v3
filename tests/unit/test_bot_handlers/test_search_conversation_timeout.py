"""
Unit tests for search conversation handler timeout integration.

Tests the ConversationHandler timeout configuration and TIMEOUT state handling.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
)

from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.config.settings import get_telegram_settings


class TestSearchConversationTimeoutIntegration:
    """Test timeout integration in main conversation handler."""

    def test_conversation_handler_has_timeout_configuration(self):
        """Test that conversation handler includes timeout configuration."""
        with patch(
            "src.bot.handlers.search_conversation.get_telegram_settings"
        ) as mock_get_settings:
            # Mock settings with 45-minute timeout
            mock_settings = Mock()
            mock_settings.conversation_timeout_minutes = 45
            mock_get_settings.return_value = mock_settings

            handler = get_search_conversation_handler()

            # Should have conversation_timeout parameter set
            assert hasattr(handler, "conversation_timeout")
            # Timeout should be converted from minutes to seconds (45 * 60 = 2700)
            assert handler.conversation_timeout == 2700

    def test_conversation_handler_has_timeout_state(self):
        """Test that conversation handler includes TIMEOUT state handler."""
        handler = get_search_conversation_handler()

        # Check that TIMEOUT state is configured
        assert ConversationHandler.TIMEOUT in handler.states

        # Should have handlers for TIMEOUT state
        timeout_handlers = handler.states[ConversationHandler.TIMEOUT]
        assert len(timeout_handlers) > 0

    def test_timeout_handler_registered_correctly(self):
        """Test that timeout handler function is registered for TIMEOUT state."""
        handler = get_search_conversation_handler()

        # Get timeout handlers
        timeout_handlers = handler.states[ConversationHandler.TIMEOUT]

        # Should have handlers registered (message + callback query)
        assert len(timeout_handlers) >= 1

        # Verify presence of both MessageHandler and CallbackQueryHandler for timeout
        handler_types = {type(h).__name__ for h in timeout_handlers}
        assert "MessageHandler" in handler_types
        assert "CallbackQueryHandler" in handler_types

        # Handler should be callable
        timeout_handler = timeout_handlers[0]
        assert hasattr(timeout_handler, "callback")
        assert callable(timeout_handler.callback)

    @pytest.fixture
    def mock_context_with_job_queue(self):
        """Create a mock context with job queue (required for timeout functionality)."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = AsyncMock()
        context.application = Mock()
        context.application.job_queue = Mock()
        return context

    @pytest.fixture
    def mock_update_timeout(self):
        """Mock Update object for timeout testing."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        chat = Mock(spec=Chat)

        user.id = 123456789
        user.first_name = "Test"
        user.is_bot = False

        chat.id = 987654321
        chat.type = Chat.PRIVATE

        message.from_user = user
        message.chat = chat
        message.text = "/start"
        message.message_id = 1

        update.message = message
        update.effective_user = user
        update.effective_chat = chat

        return update

    async def test_timeout_handler_execution(
        self, mock_update_timeout, mock_context_with_job_queue
    ):
        """Test that timeout handler executes correctly when called."""
        handler = get_search_conversation_handler()

        # Get the timeout handler callback
        timeout_handlers = handler.states[ConversationHandler.TIMEOUT]
        timeout_handler = timeout_handlers[0]

        # Execute the timeout handler
        result = await timeout_handler.callback(
            mock_update_timeout, mock_context_with_job_queue
        )

        # Should return ConversationHandler.END
        assert result == ConversationHandler.END

        # Should send at least one message (timeout notice)
        assert mock_context_with_job_queue.bot.send_message.call_count >= 1

        # Check message content of the first message
        call_args = mock_context_with_job_queue.bot.send_message.call_args_list[0]
        assert "Сессия истекла, начните заново" in call_args.kwargs["text"]

    def test_default_timeout_configuration(self):
        """Test that default timeout configuration is applied correctly."""
        with patch(
            "src.bot.handlers.search_conversation.get_telegram_settings"
        ) as mock_get_settings:
            # Mock default settings (30 minutes)
            mock_settings = Mock()
            mock_settings.conversation_timeout_minutes = 30
            mock_get_settings.return_value = mock_settings

            handler = get_search_conversation_handler()

            # Should have default 30-minute timeout converted to seconds (1800)
            assert handler.conversation_timeout == 1800

    def test_custom_timeout_configuration(self):
        """Test that custom timeout configuration from environment is respected."""
        with patch(
            "src.bot.handlers.search_conversation.get_telegram_settings"
        ) as mock_get_settings:
            # Mock custom settings (60 minutes)
            mock_settings = Mock()
            mock_settings.conversation_timeout_minutes = 60
            mock_get_settings.return_value = mock_settings

            handler = get_search_conversation_handler()

            # Should have custom 60-minute timeout converted to seconds (3600)
            assert handler.conversation_timeout == 3600

    def test_timeout_applies_to_all_states(self):
        """Test that timeout configuration applies to all conversation states."""
        handler = get_search_conversation_handler()

        # All states should be subject to timeout (this is ConversationHandler behavior)
        # The timeout applies globally to the conversation, not per-state
        assert handler.conversation_timeout is not None
        assert handler.conversation_timeout > 0

        # Check that we have states configured
        assert len(handler.states) > 0

        # TIMEOUT state should be present for handling timeouts
        assert ConversationHandler.TIMEOUT in handler.states
