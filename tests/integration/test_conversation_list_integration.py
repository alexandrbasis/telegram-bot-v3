"""
Integration tests for list handlers with search conversation.

Tests that the participant list functionality integrates properly
with the main search conversation handler.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from telegram import Update, Message, CallbackQuery
from telegram.ext import ContextTypes

from src.bot.handlers.search_conversation import get_search_conversation_handler


class TestConversationListIntegration:
    """Test integration of list handlers with conversation flow."""

    @pytest.fixture
    def conversation_handler(self):
        """Get the conversation handler."""
        return get_search_conversation_handler()

    @pytest.fixture
    def mock_get_list_message_update(self):
        """Create mock update for get list message."""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "📋 Получить список"
        update.message.reply_text = AsyncMock()
        update.effective_chat = Mock()
        update.effective_chat.id = 12345
        update.effective_user = Mock()
        update.effective_user.id = 67890
        return update

    @pytest.fixture
    def mock_role_callback_update(self):
        """Create mock update for role selection callback."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_chat = Mock()
        update.effective_chat.id = 12345
        update.effective_user = Mock()
        update.effective_user.id = 67890
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        return context

    def test_conversation_handler_includes_get_list_entry_point(
        self, conversation_handler
    ):
        """Test that conversation handler includes get list message as entry point."""
        # Check that get list message is recognized as an entry point
        entry_point_patterns = []
        for handler in conversation_handler.entry_points:
            if hasattr(handler, "filters") and hasattr(handler.filters, "pattern"):
                entry_point_patterns.append(handler.filters.pattern)

        # Should include pattern for get list button
        assert any(
            "Получить список" in str(pattern) for pattern in entry_point_patterns
        )

    def test_conversation_handler_includes_list_callback_handlers(
        self, conversation_handler
    ):
        """Test that conversation handler includes list callback handlers in states."""
        # Check that list callback handlers are included in conversation states
        callback_patterns = []

        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern"):
                    callback_patterns.append(handler.pattern)

        # Should include patterns for list role selection and navigation
        patterns_found = []
        for pattern in callback_patterns:
            pattern_str = str(pattern)
            if "list_role:" in pattern_str:
                patterns_found.append("list_role")
            if "list_nav:" in pattern_str:
                patterns_found.append("list_nav")

        assert "list_role" in patterns_found
        assert "list_nav" in patterns_found

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.service_factory")
    async def test_get_list_message_triggers_role_selection(
        self,
        mock_service_factory,
        conversation_handler,
        mock_get_list_message_update,
        mock_context,
    ):
        """Test that get list message handler exists and is callable."""
        # Find the get list message handler from entry points
        get_list_handler = None
        for handler in conversation_handler.entry_points:
            if hasattr(handler, "filters") and hasattr(handler.filters, "pattern"):
                pattern_str = str(handler.filters.pattern)
                if "Получить список" in pattern_str:
                    get_list_handler = handler
                    break

        assert (
            get_list_handler is not None
        ), "Get list handler should be found in entry points"

        # Test that the handler is callable (integration verification)
        assert hasattr(
            get_list_handler, "callback"
        ), "Handler should have callback method"

        # Call the handler directly to test integration
        await get_list_handler.callback(mock_get_list_message_update, mock_context)

        # Verify role selection keyboard was shown
        mock_get_list_message_update.message.reply_text.assert_called_once()
        call_args = mock_get_list_message_update.message.reply_text.call_args

        # Check message contains role selection
        message_text = call_args[1]["text"]
        assert "Выберите тип списка участников:" in message_text

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.service_factory")
    async def test_role_callback_processes_correctly(
        self,
        mock_service_factory,
        conversation_handler,
        mock_role_callback_update,
        mock_context,
    ):
        """Test that role selection callback handler exists and is callable."""
        # Setup mock service
        mock_service = Mock()
        mock_service_data = {
            "formatted_list": "Test participant list",
            "has_prev": False,
            "has_next": False,
            "total_count": 1,
            "page": 1,
        }
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data)
        mock_service_factory.get_participant_list_service.return_value = mock_service

        # Find the callback handler in conversation states
        role_callback_handler = None
        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern") and "list_role:" in str(handler.pattern):
                    role_callback_handler = handler
                    break
            if role_callback_handler:
                break

        assert (
            role_callback_handler is not None
        ), "Role callback handler should be found in states"

        # Test that the handler is callable (integration verification)
        assert hasattr(
            role_callback_handler, "callback"
        ), "Handler should have callback method"

        # Call the handler directly to test integration
        await role_callback_handler.callback(mock_role_callback_update, mock_context)

        # Verify service was called and response was sent
        mock_service.get_team_members_list.assert_called_once()
        mock_role_callback_update.callback_query.edit_message_text.assert_called_once()

    def test_list_handlers_maintain_conversation_state_flow(self, conversation_handler):
        """Test that list handlers maintain proper conversation state flow."""
        # Verify that list handlers can return to main menu
        main_menu_patterns = []

        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern") and "main_menu" in str(handler.pattern):
                    main_menu_patterns.append(handler.pattern)
                elif hasattr(handler, "filters") and hasattr(
                    handler.filters, "pattern"
                ):
                    pattern_str = str(handler.filters.pattern)
                    if "Главное меню" in pattern_str:
                        main_menu_patterns.append(pattern_str)

        # Should have main menu navigation available
        assert len(main_menu_patterns) > 0

    def test_conversation_entry_points_include_list_functionality(
        self, conversation_handler
    ):
        """Test that conversation entry points properly include list functionality."""
        # Check that entry points can handle list functionality
        entry_handlers = conversation_handler.entry_points

        # Should have handlers that can process both search and list requests
        search_handlers = []
        list_handlers = []

        for handler in entry_handlers:
            if hasattr(handler, "filters") and hasattr(handler.filters, "pattern"):
                pattern = str(handler.filters.pattern)
                if "Поиск участников" in pattern:
                    search_handlers.append(handler)
                if "Получить список" in pattern:
                    list_handlers.append(handler)

        # Should have both search and list entry points
        assert len(search_handlers) > 0
        assert len(list_handlers) > 0
