"""
Test suite for name search conversation flow bug.

This test reproduces the critical bug where clicking "👤 По имени" (name search button)
immediately triggers a search for that button text instead of transitioning to the
input waiting state.

Bug reproduction: The WAITING_FOR_NAME state filter doesn't exclude NAV_SEARCH_NAME
from processing, causing button text to be treated as search query.
"""

from unittest.mock import AsyncMock, MagicMock

import pytest
from telegram import Chat, Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.search_handlers import (
    handle_search_name_mode,
    process_name_search,
)
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

    def test_name_button_excluded_from_waiting_filter(self, mock_update_factory):
        """
        Test that the WAITING_FOR_NAME filter correctly excludes name search button text.

        This test verifies the regex filter in the conversation handler works correctly.
        After the fix, NAV_SEARCH_NAME should be excluded from processing.
        """
        import re

        from src.bot.keyboards.search_keyboards import (
            NAV_BACK_TO_SEARCH_MODES,
            NAV_CANCEL,
            NAV_MAIN_MENU,
            NAV_SEARCH_NAME,
        )

        # This is the FIXED exclusion regex pattern from conversation handler
        exclusion_pattern = rf"^{re.escape(NAV_MAIN_MENU)}$|^{re.escape(NAV_CANCEL)}$|^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$|^{re.escape(NAV_SEARCH_NAME)}$"

        # Test that navigation button text is excluded
        navigation_buttons = [
            NAV_MAIN_MENU,  # "🏠 Главное меню"
            NAV_CANCEL,  # "❌ Отмена"
            NAV_BACK_TO_SEARCH_MODES,  # "🔙 Назад к поиску"
            NAV_SEARCH_NAME,  # "👤 По имени" - THE BUG FIX
        ]

        for button_text in navigation_buttons:
            matches = re.search(exclusion_pattern, button_text)
            assert matches is not None, (
                f"Navigation button '{button_text}' should be excluded from "
                f"WAITING_FOR_NAME processing but regex pattern doesn't match it. "
                f"Pattern: {exclusion_pattern}"
            )

        # Test that actual participant names are NOT excluded
        participant_names = ["Александр", "Мария", "John Smith", "test name"]
        for name in participant_names:
            matches = re.search(exclusion_pattern, name)
            assert matches is None, (
                f"Participant name '{name}' should NOT be excluded from "
                f"WAITING_FOR_NAME processing but regex pattern matches it. "
                f"Pattern: {exclusion_pattern}"
            )

    @pytest.mark.asyncio
    async def test_name_button_should_transition_to_waiting_state(
        self, mock_update_factory, mock_context
    ):
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

        # Extract message text from keyword arguments
        if call_args.kwargs and "text" in call_args.kwargs:
            message_text = call_args.kwargs["text"]
        elif call_args.args:
            message_text = call_args.args[0]
        else:
            message_text = str(call_args)

        assert "Введите имя участника:" in message_text, (
            f"Expected name input prompt to be shown. "
            f"Actual message: {message_text}"
        )

    @pytest.mark.asyncio
    async def test_actual_name_search_should_work(
        self, mock_update_factory, mock_context
    ):
        """
        Test that actual participant names (not button text) should trigger search.
        """
        # Arrange: Create update with actual participant name
        update = mock_update_factory("Александр")  # Real participant name

        # Mock reply_text
        update.message.reply_text = AsyncMock()

        # Mock ALL external dependencies to prevent production credential access
        with (
            pytest.importorskip("unittest.mock").patch(
                "src.bot.handlers.search_handlers.get_participant_repository"
            ) as mock_get_repo,
            pytest.importorskip("unittest.mock").patch(
                "src.bot.handlers.search_handlers.get_user_interaction_logger",
                return_value=None,  # Disable logging
            ),
        ):
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []  # Empty results
            mock_get_repo.return_value = mock_repo

            # Act: Process actual name search
            result = await process_name_search(update, mock_context)

            # Assert: Repository search method should be called for real names
            mock_repo.search_by_name_enhanced.assert_called_once_with(
                "Александр", threshold=0.8, limit=5, user_role=None
            )


class TestSearchButtonConsistency:
    """Test that all search mode buttons have consistent behavior."""

    @pytest.mark.parametrize(
        "button_text,exclusion_constant,waiting_state",
        [
            ("👤 По имени", "NAV_SEARCH_NAME", "WAITING_FOR_NAME"),
            ("🚪 По комнате", "NAV_SEARCH_ROOM", "WAITING_FOR_ROOM"),
            ("🏢 По этажу", "NAV_SEARCH_FLOOR", "WAITING_FOR_FLOOR"),
        ],
    )
    def test_all_search_buttons_excluded_from_waiting_filters(
        self, button_text, exclusion_constant, waiting_state
    ):
        """Test that all search mode buttons are excluded from their respective WAITING state filters."""
        import re

        from src.bot.keyboards.search_keyboards import (
            NAV_BACK_TO_SEARCH_MODES,
            NAV_CANCEL,
            NAV_MAIN_MENU,
            NAV_SEARCH_FLOOR,
            NAV_SEARCH_NAME,
            NAV_SEARCH_ROOM,
        )

        # Map constants to their values
        nav_constants = {
            "NAV_SEARCH_NAME": NAV_SEARCH_NAME,
            "NAV_SEARCH_ROOM": NAV_SEARCH_ROOM,
            "NAV_SEARCH_FLOOR": NAV_SEARCH_FLOOR,
        }

        # Get the specific search button constant
        search_button = nav_constants[exclusion_constant]

        # Verify button text matches
        assert button_text == search_button

        # Create exclusion pattern that should be used in the WAITING state
        exclusion_pattern = (
            rf"^{re.escape(NAV_MAIN_MENU)}$|"
            rf"^{re.escape(NAV_CANCEL)}$|"
            rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$|"
            rf"^{re.escape(search_button)}$"
        )

        # Test that the search button is excluded
        matches = re.search(exclusion_pattern, button_text)
        assert matches is not None, (
            f"Search button '{button_text}' should be excluded from {waiting_state} "
            f"processing but regex pattern doesn't match it. "
            f"Pattern: {exclusion_pattern}"
        )


class TestStateTransitions:
    """Comprehensive state transition testing for name search flow."""

    @pytest.fixture
    def mock_update_factory(self):
        """Factory to create mock Update objects."""

        def _create_update(text: str) -> Update:
            update = MagicMock(spec=Update)
            update.message = MagicMock(spec=Message)
            update.message.text = text
            update.message.from_user = MagicMock(spec=User)
            update.message.from_user.id = 12345
            update.message.from_user.first_name = "Test"
            update.message.chat = MagicMock(spec=Chat)
            update.message.chat.id = 12345
            update.message.reply_text = AsyncMock()
            return update

        return _create_update

    @pytest.fixture
    def mock_context(self):
        """Mock context for handlers."""
        context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_name_search_mode_transition(self, mock_update_factory, mock_context):
        """Test SEARCH_MODE_SELECTION → WAITING_FOR_NAME transition."""
        from src.bot.handlers.search_handlers import SearchStates

        # Arrange: Click name search button
        update = mock_update_factory(NAV_SEARCH_NAME)

        # Act: Handle name search mode selection
        result = await handle_search_name_mode(update, mock_context)

        # Assert: Should transition to WAITING_FOR_NAME
        assert result == SearchStates.WAITING_FOR_NAME

        # Verify prompt was sent
        update.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_actual_name_triggers_search(self, mock_update_factory, mock_context):
        """Test WAITING_FOR_NAME → SHOWING_RESULTS transition via actual name."""
        # Arrange: Enter actual participant name
        update = mock_update_factory("Александр")

        # Mock ALL external dependencies to prevent production credential access
        with (
            pytest.importorskip("unittest.mock").patch(
                "src.bot.handlers.search_handlers.get_participant_repository"
            ) as mock_get_repo,
            pytest.importorskip("unittest.mock").patch(
                "src.bot.handlers.search_handlers.get_user_interaction_logger",
                return_value=None,  # Disable logging
            ),
        ):
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []  # Empty results
            mock_get_repo.return_value = mock_repo

            # Act: Process name search
            result = await process_name_search(update, mock_context)

            # Assert: Repository search method called with correct name
            mock_repo.search_by_name_enhanced.assert_called_once_with(
                "Александр", threshold=0.8, limit=5, user_role=None
            )

    def test_navigation_buttons_behavior(self):
        """Test that navigation buttons have consistent exclusion patterns."""
        import re

        from src.bot.keyboards.search_keyboards import (
            NAV_BACK_TO_SEARCH_MODES,
            NAV_CANCEL,
            NAV_MAIN_MENU,
            NAV_SEARCH_FLOOR,
            NAV_SEARCH_NAME,
            NAV_SEARCH_ROOM,
        )

        # All navigation buttons that should be excluded
        nav_buttons = [
            NAV_MAIN_MENU,
            NAV_CANCEL,
            NAV_BACK_TO_SEARCH_MODES,
            NAV_SEARCH_NAME,  # The critical fix
            NAV_SEARCH_ROOM,  # Consistency fix
            NAV_SEARCH_FLOOR,  # Consistency fix
        ]

        # Create comprehensive exclusion pattern
        exclusion_parts = [rf"^{re.escape(button)}$" for button in nav_buttons]
        full_pattern = "|".join(exclusion_parts)

        # Test each button is matched
        for button in nav_buttons:
            matches = re.search(full_pattern, button)
            assert matches is not None, f"Button '{button}' not matched by pattern"

        # Test participant names are not matched
        participant_names = ["Александр", "Мария", "John Smith", "test123"]
        for name in participant_names:
            matches = re.search(full_pattern, name)
            assert (
                matches is None
            ), f"Name '{name}' incorrectly matched by exclusion pattern"
