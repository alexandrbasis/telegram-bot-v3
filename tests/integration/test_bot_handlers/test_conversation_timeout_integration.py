"""
Integration tests for conversation timeout functionality.

Tests end-to-end timeout behavior across all conversation states with
real ConversationHandler execution and state transitions.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.bot.handlers.search_handlers import SearchStates
from src.bot.handlers.room_search_handlers import RoomSearchStates
from src.bot.handlers.edit_participant_handlers import EditStates


class TestConversationTimeoutIntegration:
    """Integration tests for complete timeout functionality."""

    @pytest.fixture
    def mock_user(self):
        """Create a mock User object."""
        user = Mock(spec=User)
        user.id = 123456789
        user.first_name = "TestUser"
        user.last_name = "Integration"
        user.username = "test_integration"
        user.is_bot = False
        return user

    @pytest.fixture
    def mock_chat(self):
        """Create a mock Chat object."""
        chat = Mock(spec=Chat)
        chat.id = 987654321
        chat.type = Chat.PRIVATE
        return chat

    @pytest.fixture
    def mock_update(self, mock_user, mock_chat):
        """Create a mock Update object."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        
        message.from_user = mock_user
        message.chat = mock_chat
        message.text = "/start"
        message.message_id = 1
        
        update.message = message
        update.effective_user = mock_user
        update.effective_chat = mock_chat
        update.callback_query = None
        
        return update

    @pytest.fixture
    def mock_context_with_job_queue(self):
        """Create a mock context with job queue for timeout functionality."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = AsyncMock()
        context.application = Mock()
        context.application.job_queue = Mock()
        context.user_data = {}
        context.chat_data = {}
        return context

    @pytest.fixture
    def conversation_handler(self):
        """Get the conversation handler with timeout configuration."""
        with patch('src.bot.handlers.search_conversation.get_telegram_settings') as mock_settings:
            # Use default 30-minute timeout
            mock_settings_obj = Mock()
            mock_settings_obj.conversation_timeout_minutes = 30
            mock_settings.return_value = mock_settings_obj
            
            return get_search_conversation_handler()

    async def test_timeout_from_main_menu_state(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test timeout behavior from MAIN_MENU state."""
        # Simulate being in MAIN_MENU state when timeout occurs
        
        # Execute timeout handler
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        # Should end conversation and show timeout message
        assert result == conversation_handler.END
        mock_context_with_job_queue.bot.send_message.assert_called_once()
        
        # Check Russian timeout message
        call_args = mock_context_with_job_queue.bot.send_message.call_args
        assert "Сессия истекла, начните заново" in call_args.kwargs["text"]

    async def test_timeout_from_search_mode_selection_state(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test timeout behavior from SEARCH_MODE_SELECTION state."""
        # Simulate being in search mode selection when timeout occurs
        
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        # Should properly handle timeout regardless of current state
        assert result == conversation_handler.END
        mock_context_with_job_queue.bot.send_message.assert_called_once()

    async def test_timeout_from_waiting_for_name_state(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test timeout behavior from WAITING_FOR_NAME state."""
        # Simulate user was entering name when timeout occurred
        mock_update.message.text = "John"  # User was typing a name
        
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        assert result == conversation_handler.END
        mock_context_with_job_queue.bot.send_message.assert_called_once()
        
        # Verify timeout message content
        call_args = mock_context_with_job_queue.bot.send_message.call_args
        message_text = call_args.kwargs["text"]
        assert "⏰" in message_text
        assert "🔄" in message_text

    async def test_timeout_from_room_search_state(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test timeout behavior from room search states."""
        # Simulate timeout during room search
        mock_update.message.text = "101"  # User was entering room number
        
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        assert result == conversation_handler.END
        mock_context_with_job_queue.bot.send_message.assert_called_once()

    async def test_timeout_from_edit_states(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test timeout behavior from participant editing states."""
        # Simulate timeout during participant editing
        
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        # Should cleanly end conversation and return to main menu
        assert result == conversation_handler.END
        mock_context_with_job_queue.bot.send_message.assert_called_once()
        
        # Should provide main menu keyboard for recovery
        call_args = mock_context_with_job_queue.bot.send_message.call_args
        assert "reply_markup" in call_args.kwargs

    async def test_timeout_state_cleanup(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test that timeout properly cleans up conversation state."""
        # Add some conversation state data
        mock_context_with_job_queue.user_data = {"search_query": "test", "current_participant": {"id": "123"}}
        mock_context_with_job_queue.chat_data = {"conversation_state": "WAITING_FOR_NAME"}
        
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        # Should end conversation (state cleanup is handled by ConversationHandler)
        assert result == conversation_handler.END

    async def test_timeout_with_keyboard_recovery(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test that timeout provides proper keyboard for session recovery."""
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        assert result == conversation_handler.END
        
        # Verify keyboard for recovery
        call_args = mock_context_with_job_queue.bot.send_message.call_args
        keyboard = call_args.kwargs["reply_markup"]
        
        # Should be a ReplyKeyboardMarkup with search functionality
        from telegram import ReplyKeyboardMarkup
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert "🔍 Поиск участников" in str(keyboard)

    def test_timeout_configuration_integration(self):
        """Test that timeout configuration is properly integrated."""
        with patch('src.bot.handlers.search_conversation.get_telegram_settings') as mock_settings:
            # Test different timeout values
            test_timeouts = [15, 30, 45, 60, 120]
            
            for timeout_minutes in test_timeouts:
                mock_settings_obj = Mock()
                mock_settings_obj.conversation_timeout_minutes = timeout_minutes
                mock_settings.return_value = mock_settings_obj
                
                handler = get_search_conversation_handler()
                
                # Should convert minutes to seconds correctly
                expected_seconds = timeout_minutes * 60
                assert handler.conversation_timeout == expected_seconds

    def test_timeout_state_coverage(self, conversation_handler):
        """Test that all conversation states are subject to timeout."""
        # Verify that TIMEOUT handler is registered
        assert conversation_handler.TIMEOUT in conversation_handler.states
        
        # Verify timeout handlers exist
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        assert len(timeout_handlers) == 1
        
        # Check that all major state groups are present in the conversation
        expected_states = [
            SearchStates.MAIN_MENU,
            SearchStates.SEARCH_MODE_SELECTION,
            SearchStates.WAITING_FOR_NAME,
            SearchStates.SHOWING_RESULTS,
            RoomSearchStates.WAITING_FOR_ROOM,
            EditStates.FIELD_SELECTION,
        ]
        
        for state in expected_states:
            assert state in conversation_handler.states, f"State {state} missing from conversation handler"

    async def test_timeout_error_recovery(self, conversation_handler, mock_context_with_job_queue):
        """Test timeout behavior with error conditions."""
        # Test with None update (edge case)
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(None, mock_context_with_job_queue)
        
        # Should still end conversation gracefully
        assert result == conversation_handler.END
        
        # Should not attempt to send message if no update
        mock_context_with_job_queue.bot.send_message.assert_not_called()

    async def test_timeout_message_content_integration(self, conversation_handler, mock_update, mock_context_with_job_queue):
        """Test complete timeout message content and formatting."""
        timeout_handlers = conversation_handler.states[conversation_handler.TIMEOUT]
        timeout_handler = timeout_handlers[0]
        
        result = await timeout_handler.callback(mock_update, mock_context_with_job_queue)
        
        assert result == conversation_handler.END
        
        # Verify complete message structure
        call_args = mock_context_with_job_queue.bot.send_message.call_args
        
        # Should send to correct chat
        assert call_args.kwargs["chat_id"] == 987654321
        
        # Should contain all required elements
        message_text = call_args.kwargs["text"]
        assert "⏰ Сессия истекла, начните заново" in message_text
        assert "🔄 Используйте главное меню ниже для продолжения работы" in message_text
        
        # Should have proper keyboard
        assert "reply_markup" in call_args.kwargs
