"""
Unit tests for search conversation handler with room search integration.

Tests the ConversationHandler configuration and state management for room search.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.bot.handlers.room_search_handlers import RoomSearchStates


class TestSearchConversationRoomIntegration:
    """Test room search integration in main conversation handler."""

    def test_conversation_handler_has_room_search_entry_point(self):
        """Test that conversation handler includes room search command."""
        handler = get_search_conversation_handler()

        # Check that we have 3 entry points (start, search_room, search_floor)
        assert len(handler.entry_points) == 3

        # Check that search_room command is registered as entry point
        entry_commands = []
        for ep in handler.entry_points:
            if hasattr(ep, "commands"):
                entry_commands.extend(ep.commands)
        assert "search_room" in entry_commands

    def test_conversation_handler_has_room_search_states(self):
        """Test that conversation handler includes room search states."""
        handler = get_search_conversation_handler()

        # Check that room search states are configured
        assert RoomSearchStates.WAITING_FOR_ROOM in handler.states
        assert RoomSearchStates.SHOWING_ROOM_RESULTS in handler.states

    @pytest.fixture
    def mock_update_room_command(self):
        """Mock Update object for /search_room command."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        chat = Mock(spec=Chat)

        user.id = 123456789
        user.first_name = "TestUser"

        chat.id = 123456789
        chat.type = "private"

        message.from_user = user
        message.chat = chat
        message.text = "/search_room 205"
        message.reply_text = AsyncMock()

        update.effective_user = user
        update.message = message

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock ContextTypes.DEFAULT_TYPE."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    @patch("src.bot.handlers.room_search_handlers.get_search_service")
    async def test_room_search_command_integration(
        self, mock_get_service, mock_update_room_command, mock_context
    ):
        """Test that /search_room command works through conversation handler."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_room_formatted.return_value = [
            "1. Иван Петров (Ivan Petrov) - Этаж: 2, Комната: 205"
        ]
        mock_service.search_by_room.return_value = []
        mock_get_service.return_value = mock_service

        # Get conversation handler
        handler = get_search_conversation_handler()

        # Find the room search command handler
        room_search_entry = None
        for entry_point in handler.entry_points:
            if (
                hasattr(entry_point, "commands")
                and "search_room" in entry_point.commands
            ):
                room_search_entry = entry_point
                break

        assert (
            room_search_entry is not None
        ), "search_room command not found in entry points"

        # Execute the handler
        result = await room_search_entry.callback(
            mock_update_room_command, mock_context
        )

        # Should transition to showing room results
        assert result == RoomSearchStates.SHOWING_ROOM_RESULTS

        # Should have replied to user
        mock_update_room_command.message.reply_text.assert_called()
