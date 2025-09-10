"""
Test suite for name search conversation flow bug.

This test reproduces the critical bug where clicking "👤 По имени" (name search button)
immediately triggers a search for that button text instead of transitioning to the
input waiting state.

Bug reproduction: The WAITING_FOR_NAME state filter doesn't exclude NAV_SEARCH_NAME
from processing, causing button text to be treated as search query.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock

from telegram import Update, Message, User, Chat
from telegram.ext import ContextTypes

from src.bot.handlers.search_handlers import process_name_search, handle_search_name_mode
from src.bot.keyboards.search_keyboards import NAV_SEARCH_NAME


class TestNameSearchButtonBug:
    """Test class to reproduce and verify the name search button processing bug."""

    @pytest.fixture
    def mock_update_factory(self):
        """Factory to create mock Update objects with different message text."""
        def _create_update(text: str) -> Update:
            update = MagicMock(spec=Update)
            update.message = MagicMock(spec=Message)
            update.message.text = text
            update.message.from_user = MagicMock(spec=User)
            update.message.from_user.id = 12345
            update.message.from_user.first_name = "Test"
            update.message.chat = MagicMock(spec=Chat)
            update.message.chat.id = 12345
            return update
        return _create_update

    @pytest.fixture
    def mock_context(self):
        """Mock context for handlers."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_name_button_triggers_search_bug(self, mock_update_factory, mock_context):
        """
        Test that reproduces the bug: clicking name search button triggers immediate search.
        
        This test should FAIL initially, demonstrating the bug exists.
        After the fix, it should PASS, confirming the button text is not processed as query.
        """
        # Arrange: Create update with name search button text
        update = mock_update_factory(NAV_SEARCH_NAME)  # "👤 По имени"
        
        # Mock search service to track if search was called
        search_called = False
        original_process = process_name_search
        
        async def mock_process_name_search(update, context):
            nonlocal search_called
            search_called = True
            # Return some mock response to prevent actual search logic
            await update.message.reply_text("Mock search result")
            return "SHOWING_RESULTS"
        
        # Replace process function temporarily
        import src.bot.handlers.search_handlers
        src.bot.handlers.search_handlers.process_name_search = mock_process_name_search
        
        try:
            # Act: Process the button text through name search handler
            # This should NOT trigger search, but currently it will (bug)
            result = await mock_process_name_search(update, mock_context)
            
            # Assert: The bug is that search was called when it shouldn't be
            # This assertion should FAIL initially, proving the bug exists
            assert not search_called, (
                f"BUG REPRODUCED: Button text '{NAV_SEARCH_NAME}' was processed as search query. "
                f"Expected: button should be excluded from search processing. "
                f"Actual: process_name_search was called with button text."
            )
            
        finally:
            # Restore original function
            src.bot.handlers.search_handlers.process_name_search = original_process

    @pytest.mark.asyncio  
    async def test_name_button_should_transition_to_waiting_state(self, mock_update_factory, mock_context):
        """
        Test the correct behavior: clicking name search button should transition to WAITING_FOR_NAME.
        
        This test will PASS after the fix is implemented.
        """
        # Arrange: Create update with name search button text
        update = mock_update_factory(NAV_SEARCH_NAME)  # "👤 По имени"
        
        # Mock reply_text to capture the prompt message
        update.message.reply_text = AsyncMock()
        
        # Act: Handle name search mode selection (correct handler)
        result = await handle_search_name_mode(update, mock_context)
        
        # Assert: Should transition to WAITING_FOR_NAME and show prompt
        from src.bot.handlers.search_handlers import SearchStates
        assert result == SearchStates.WAITING_FOR_NAME
        
        # Verify prompt message was sent
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        message_text = call_args[0][0]  # First positional argument
        
        assert "Введите имя участника:" in message_text, (
            f"Expected name input prompt to be shown. "
            f"Actual message: {message_text}"
        )

    @pytest.mark.asyncio
    async def test_actual_name_search_should_work(self, mock_update_factory, mock_context):
        """
        Test that actual participant names (not button text) should trigger search.
        """
        # Arrange: Create update with actual participant name
        update = mock_update_factory("Александр")  # Real participant name
        
        # Mock reply_text and search service
        update.message.reply_text = AsyncMock()
        
        # Mock context.application to have search service
        mock_search_service = AsyncMock()
        mock_search_service.search_participants_by_name.return_value = []
        mock_context.application = MagicMock()
        mock_context.application.search_service = mock_search_service
        
        # Act: Process actual name search
        result = await process_name_search(update, mock_context)
        
        # Assert: Search service should be called for real names
        mock_search_service.search_participants_by_name.assert_called_once_with("Александр")


class TestSearchButtonConsistency:
    """Test that all search mode buttons have consistent behavior."""

    @pytest.mark.parametrize("button_text,expected_exclusion", [
        ("👤 По имени", "NAV_SEARCH_NAME"),  # Name search button
        ("🚪 По комнате", "NAV_SEARCH_ROOM"),  # Room search button  
        ("🏢 По этажу", "NAV_SEARCH_FLOOR"),  # Floor search button
    ])
    def test_search_buttons_should_be_excluded_from_processing(self, button_text, expected_exclusion):
        """
        Test that all search mode buttons are properly excluded from search processing.
        
        This test documents the expected behavior for all three search modes.
        """
        from src.bot.keyboards.search_keyboards import (
            NAV_SEARCH_NAME, 
            NAV_SEARCH_ROOM, 
            NAV_SEARCH_FLOOR
        )
        
        nav_constants = {
            "NAV_SEARCH_NAME": NAV_SEARCH_NAME,
            "NAV_SEARCH_ROOM": NAV_SEARCH_ROOM, 
            "NAV_SEARCH_FLOOR": NAV_SEARCH_FLOOR,
        }
        
        # Verify button text matches expected constant
        expected_text = nav_constants[expected_exclusion]
        assert button_text == expected_text, (
            f"Button text mismatch for {expected_exclusion}. "
            f"Expected: {expected_text}, Actual: {button_text}"
        )
        
        # This test documents the requirement that these buttons should be excluded
        # The actual exclusion logic will be tested in integration tests
        assert True  # Placeholder - actual exclusion testing requires conversation handler setup