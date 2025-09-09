"""
Unit tests for search conversation handler with floor search integration.

Tests the ConversationHandler configuration and state management for floor search.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.floor_search_handlers import FloorSearchStates
from src.bot.handlers.search_conversation import get_search_conversation_handler


class TestSearchConversationFloorIntegration:
    """Test floor search integration in main conversation handler."""

    def test_conversation_handler_has_floor_search_entry_point(self):
        """Test that conversation handler includes floor search command."""
        handler = get_search_conversation_handler()

        # Check that we have at least 3 entry points (start, search_room, search_floor)
        # Note: We now have 6+ entry points including text button handlers for timeout recovery
        assert len(handler.entry_points) >= 3

        # Check that search_floor command is registered as entry point
        entry_commands = []
        for ep in handler.entry_points:
            if hasattr(ep, "commands"):
                entry_commands.extend(ep.commands)
        assert "search_floor" in entry_commands

    def test_conversation_handler_has_floor_search_states(self):
        """Test that conversation handler includes floor search states."""
        handler = get_search_conversation_handler()

        # Check that floor search states are configured
        assert FloorSearchStates.WAITING_FOR_FLOOR in handler.states
        assert FloorSearchStates.SHOWING_FLOOR_RESULTS in handler.states

    @pytest.fixture
    def mock_update_floor_command(self):
        """Mock Update object for /search_floor command."""
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
        message.text = "/search_floor 2"
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
    @patch("src.bot.handlers.floor_search_handlers.get_search_service")
    async def test_floor_search_command_integration(
        self, mock_get_service, mock_update_floor_command, mock_context
    ):
        """Test that /search_floor command works through conversation handler."""
        # Mock search service
        mock_service = AsyncMock()
        mock_service.search_by_floor.return_value = []
        mock_get_service.return_value = mock_service

        # Get conversation handler
        handler = get_search_conversation_handler()

        # Find the floor search command handler
        floor_search_entry = None
        for entry_point in handler.entry_points:
            if (
                hasattr(entry_point, "commands")
                and "search_floor" in entry_point.commands
            ):
                floor_search_entry = entry_point
                break

        assert (
            floor_search_entry is not None
        ), "search_floor command not found in entry points"

        # Execute the handler
        result = await floor_search_entry.callback(
            mock_update_floor_command, mock_context
        )

        # Should transition to showing floor results
        assert result == FloorSearchStates.SHOWING_FLOOR_RESULTS

        # Should have replied to user
        mock_update_floor_command.message.reply_text.assert_called()
