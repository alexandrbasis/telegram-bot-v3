"""
Unit tests for conversation timeout handlers.

Tests cover:
- Timeout message content and Russian language
- Main menu keyboard generation for recovery
- Handler function behavior and return values
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler

from src.bot.handlers.timeout_handlers import handle_conversation_timeout
from src.bot.keyboards.search_keyboards import NAV_MAIN_MENU


class TestConversationTimeoutHandler:
    """Test suite for conversation timeout handler functionality."""

    @pytest.fixture
    def mock_update(self):
        """Create a mock Update object."""
        update = MagicMock(spec=Update)
        update.effective_chat = MagicMock()
        update.effective_chat.id = 12345
        return update

    @pytest.fixture
    def mock_context(self):
        """Create a mock CallbackContext object."""
        context = MagicMock(spec=CallbackContext)
        context.bot = AsyncMock()
        return context

    async def test_timeout_message_content_russian(self, mock_update, mock_context):
        """Test that timeout message contains correct Russian text."""
        result = await handle_conversation_timeout(mock_update, mock_context)

        # Should return ConversationHandler.END
        assert result == ConversationHandler.END

        # Should send at least one message (timeout notice)
        assert mock_context.bot.send_message.call_count >= 1
        call_args = mock_context.bot.send_message.call_args_list[0]

        # Check message content
        assert "Сессия истекла, начните заново" in call_args.kwargs["text"]

    async def test_timeout_message_includes_main_menu_keyboard(
        self, mock_update, mock_context
    ):
        """Test that timeout message includes main menu keyboard for recovery."""
        result = await handle_conversation_timeout(mock_update, mock_context)

        # Should return ConversationHandler.END
        assert result == ConversationHandler.END

        # Should send message with keyboard (first message)
        assert mock_context.bot.send_message.call_count >= 1
        call_args = mock_context.bot.send_message.call_args_list[0]

        # Check that reply_markup is present
        assert "reply_markup" in call_args.kwargs
        keyboard = call_args.kwargs["reply_markup"]

        # Should contain search entry point (main menu functionality)
        keyboard_text = str(keyboard)
        assert "🔍 Поиск участников" in keyboard_text

    async def test_timeout_handler_returns_conversation_end(
        self, mock_update, mock_context
    ):
        """Test that timeout handler returns ConversationHandler.END."""
        result = await handle_conversation_timeout(mock_update, mock_context)
        assert result == ConversationHandler.END

    async def test_timeout_message_formatting(self, mock_update, mock_context):
        """Test that timeout message is properly formatted."""
        result = await handle_conversation_timeout(mock_update, mock_context)

        assert mock_context.bot.send_message.call_count >= 1
        call_args = mock_context.bot.send_message.call_args_list[0]

        # Check that message is sent to correct chat
        assert call_args.kwargs["chat_id"] == 12345

        # Check that message contains proper formatting
        message_text = call_args.kwargs["text"]
        assert (
            "⏰" in message_text or "🔄" in message_text
        )  # Should have timeout/restart emoji

    async def test_timeout_handler_with_none_update(self, mock_context):
        """Test timeout handler behavior with None update (edge case)."""
        # This should handle gracefully without crashing
        result = await handle_conversation_timeout(None, mock_context)

        # Should still return END state
        assert result == ConversationHandler.END

        # Should not attempt to send message if no update
        mock_context.bot.send_message.assert_not_called()

    async def test_timeout_keyboard_structure(self, mock_update, mock_context):
        """Test the structure and content of timeout recovery keyboard."""
        result = await handle_conversation_timeout(mock_update, mock_context)

        assert mock_context.bot.send_message.call_count >= 1
        call_args = mock_context.bot.send_message.call_args_list[0]

        # Get the keyboard
        keyboard = call_args.kwargs["reply_markup"]

        # Should be a ReplyKeyboardMarkup
        from telegram import ReplyKeyboardMarkup

        assert isinstance(keyboard, ReplyKeyboardMarkup)

        # Should have proper settings
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is False

    async def test_timeout_sends_inline_restart_button(self, mock_update, mock_context):
        """Ensure an inline /start restart button is sent as a second message."""
        await handle_conversation_timeout(mock_update, mock_context)

        # Expect at least two messages: main menu + inline restart
        assert mock_context.bot.send_message.call_count >= 2

        # Check the last call has InlineKeyboardMarkup with restart callback
        from telegram import InlineKeyboardMarkup

        last_call = mock_context.bot.send_message.call_args_list[-1]
        assert isinstance(last_call.kwargs.get("reply_markup"), InlineKeyboardMarkup)
        keyboard_str = str(last_call.kwargs["reply_markup"])
        assert "restart_bot" in keyboard_str
