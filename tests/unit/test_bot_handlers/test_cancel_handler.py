"""
Unit tests for cancel handler functionality.

Tests the cancel_search handler to ensure it properly resets user state
and provides consistent welcome message behavior.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.bot.handlers.search_handlers import SearchStates, cancel_search


class TestCancelSearchHandler:
    """Test cases for the cancel_search handler."""

    @pytest.mark.asyncio
    async def test_cancel_search_resets_state_and_shows_welcome_message(self):
        """Test that cancel_search resets state and shows unified welcome message."""
        # Create mock update and context
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.message = AsyncMock()

        mock_context = Mock()
        mock_context.user_data = {
            "search_results": [{"participant": "test"}],
            "force_direct_name_input": False,
            "other_state": "should_remain",
        }

        # Call the handler
        result = await cancel_search(mock_update, mock_context)

        # Verify state is properly reset using shared helper
        assert mock_context.user_data["search_results"] == []
        assert mock_context.user_data["force_direct_name_input"] is True
        assert (
            mock_context.user_data["other_state"] == "should_remain"
        )  # Other data preserved

        # Verify unified welcome message is used
        expected_message = (
            "Добро пожаловать в бот Tres Dias! 🙏\n\n"
            "Выберите тип поиска участников.\n"
            "ℹ️ Для подсказок используйте команду /help."
        )
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert call_args[1]["text"] == expected_message

        # Verify correct keyboard is provided
        assert "reply_markup" in call_args[1]

        # Verify correct state is returned
        assert result == SearchStates.MAIN_MENU

    @pytest.mark.asyncio
    async def test_cancel_search_handles_empty_user_data(self):
        """Test that cancel_search works correctly with empty user_data."""
        # Create mock update and context with empty user_data
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.message = AsyncMock()

        mock_context = Mock()
        mock_context.user_data = {}

        # Call the handler
        result = await cancel_search(mock_update, mock_context)

        # Verify state is properly initialized
        assert mock_context.user_data["search_results"] == []
        assert mock_context.user_data["force_direct_name_input"] is True

        # Verify unified welcome message is used
        expected_message = (
            "Добро пожаловать в бот Tres Dias! 🙏\n\n"
            "Выберите тип поиска участников.\n"
            "ℹ️ Для подсказок используйте команду /help."
        )
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert call_args[1]["text"] == expected_message

        # Verify correct state is returned
        assert result == SearchStates.MAIN_MENU

    @pytest.mark.asyncio
    async def test_cancel_search_equivalence_to_shared_helpers(self):
        """Test that cancel_search provides equivalent initialization to start_command/main_menu_button."""
        from src.bot.handlers.search_handlers import (
            get_welcome_message,
            initialize_main_menu_session,
        )

        # Create mock update and context
        mock_update = Mock()
        mock_update.effective_user.id = 12345
        mock_update.message = AsyncMock()

        mock_context = Mock()
        mock_context.user_data = {"existing_data": "preserved"}

        # Call cancel_search
        result = await cancel_search(mock_update, mock_context)

        # Create a fresh context for comparison
        comparison_context = Mock()
        comparison_context.user_data = {"existing_data": "preserved"}
        initialize_main_menu_session(comparison_context)

        # Verify equivalent state initialization
        assert (
            mock_context.user_data["search_results"]
            == comparison_context.user_data["search_results"]
        )
        assert (
            mock_context.user_data["force_direct_name_input"]
            == comparison_context.user_data["force_direct_name_input"]
        )
        assert (
            mock_context.user_data["existing_data"]
            == comparison_context.user_data["existing_data"]
        )

        # Verify equivalent welcome message
        expected_message = get_welcome_message()
        call_args = mock_update.message.reply_text.call_args
        assert call_args[1]["text"] == expected_message

        # Verify correct state is returned
        assert result == SearchStates.MAIN_MENU
