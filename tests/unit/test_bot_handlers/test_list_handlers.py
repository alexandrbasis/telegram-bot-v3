"""
Tests for list handlers functionality.

Tests conversation handlers for participant list access functionality,
including role selection and main menu integration.
"""

from datetime import date
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import CallbackQuery, Message, Update
from telegram.ext import ContextTypes

from src.bot.handlers.list_handlers import (
    handle_get_list_request,
    handle_list_navigation,
    handle_role_selection,
)
from src.bot.handlers.search_handlers import SearchStates
from src.models.participant import Participant, Role


class TestGetListRequestHandler:
    """Test get list request handler functionality."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update with get list message."""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "📋 Получить список"
        update.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_handle_get_list_request_shows_role_selection(
        self, mock_update, mock_context
    ):
        """Test that get list request shows role selection keyboard."""
        await handle_get_list_request(mock_update, mock_context)

        # Should reply with role selection message and keyboard
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args

        # Check message text
        assert "Выберите тип списка участников:" in call_args[1]["text"]

        # Check that inline keyboard is provided
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]

        # Should have role selection buttons
        assert len(keyboard.inline_keyboard) == 2
        assert keyboard.inline_keyboard[0][0].callback_data == "list_role:TEAM"
        assert keyboard.inline_keyboard[1][0].callback_data == "list_role:CANDIDATE"

    @pytest.mark.asyncio
    async def test_handle_get_list_request_message_content(
        self, mock_update, mock_context
    ):
        """Test that get list request has correct message content."""
        await handle_get_list_request(mock_update, mock_context)

        call_args = mock_update.message.reply_text.call_args
        message_text = call_args[1]["text"]

        # Should contain role selection prompt and both role options
        assert "Выберите тип списка участников:" in message_text
        assert "Команда" in message_text
        assert "Кандидаты" in message_text


class TestRoleSelectionHandler:
    """Test role selection handler functionality."""

    @pytest.fixture
    def mock_team_update(self):
        """Create mock update for team selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_candidate_update(self):
        """Create mock update for candidate selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:CANDIDATE"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_handle_team_role_selection(self, mock_team_update, mock_context):
        """Test team role selection triggers department selection display."""
        await handle_role_selection(mock_team_update, mock_context)

        # Should answer the callback query
        mock_team_update.callback_query.answer.assert_called_once()

        # Should edit message with department selection keyboard
        mock_team_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_team_update.callback_query.edit_message_text.call_args

        message_text = call_args[1]["text"]
        assert "Выберите департамент" in message_text

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_handle_candidate_role_selection(
        self, mock_get_service, mock_candidate_update, mock_context
    ):
        """Test candidate role selection triggers candidate list display."""
        # Setup mock service
        mock_service = Mock()
        mock_service.get_candidates_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. **Кандидат Тест**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        await handle_role_selection(mock_candidate_update, mock_context)

        # Should answer the callback query
        mock_candidate_update.callback_query.answer.assert_called_once()

        # Should edit message with candidate list (placeholder for now)
        mock_candidate_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_candidate_update.callback_query.edit_message_text.call_args

        message_text = call_args[1]["text"]
        assert "Список кандидатов" in message_text

    @pytest.mark.asyncio
    async def test_role_selection_includes_department_keyboard(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection includes department filter keyboard."""
        await handle_role_selection(mock_team_update, mock_context)

        call_args = mock_team_update.callback_query.edit_message_text.call_args

        # Should include department filter keyboard
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]

        # Should have department filter buttons
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        # Should have "All teams" button
        all_buttons = [btn for btn in buttons if "Все Тимы" in btn.text]
        assert len(all_buttons) == 1


class TestListNavigationHandler:
    """Test list navigation handler functionality."""

    @pytest.fixture
    def mock_main_menu_update(self):
        """Create mock update for main menu navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:MAIN_MENU"
        update.callback_query.answer = AsyncMock()
        update.callback_query.message = Mock()
        update.callback_query.message.edit_text = AsyncMock()
        update.callback_query.message.reply_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_handle_main_menu_navigation(
        self, mock_main_menu_update, mock_context
    ):
        """Test main menu navigation returns to main menu."""
        await handle_list_navigation(mock_main_menu_update, mock_context)

        # Should answer the callback query once (via main_menu_button handler)
        mock_main_menu_update.callback_query.answer.assert_called_once()

        # Should edit message and then send reply with main menu keyboard
        mock_main_menu_update.callback_query.message.edit_text.assert_called_once()
        mock_main_menu_update.callback_query.message.reply_text.assert_called_once()

    @pytest.mark.asyncio
    async def test_navigation_handler_recognizes_callback_pattern(
        self, mock_main_menu_update, mock_context
    ):
        """Test that navigation handler recognizes list_nav callback patterns."""
        # This test verifies the callback data pattern is handled correctly
        callback_data = mock_main_menu_update.callback_query.data
        assert callback_data.startswith("list_nav:")

        action = callback_data.split(":")[1]
        assert action == "MAIN_MENU"


class TestRoleSelectionWithServiceIntegration:
    """Test role selection handler with service integration."""

    @pytest.fixture
    def mock_team_update(self):
        """Create mock update for team selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.fixture
    def mock_service_data(self):
        """Create mock service response data."""
        return {
            "formatted_list": "1. **Тестов Тест Тестович**\n   👕 Размер: M\n   ⛪ Церковь: Тестовая церковь\n   📅 Дата рождения: 01.01.1990",
            "has_prev": False,
            "has_next": True,
            "total_count": 10,
            "current_offset": 0,
            "next_offset": 20,
            "prev_offset": None,
            "actual_displayed": 1,
        }

    @pytest.mark.asyncio
    async def test_team_role_selection_shows_department_keyboard(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection shows department filter keyboard."""
        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Verify department selection keyboard is shown
        mock_team_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_team_update.callback_query.edit_message_text.call_args

        # Check message text contains department selection prompt
        message_text = call_args[1]["text"]
        assert "Выберите департамент для фильтрации участников команды" in message_text
        assert "🌐 **Все Тимы**" in message_text
        assert "🏢 **Департамент**" in message_text
        assert "❓ **Без департамента**" in message_text

        # Check that MarkdownV2 parsing is used
        assert call_args[1]["parse_mode"] == "MarkdownV2"

        # Check that user data is set
        assert mock_context.user_data["selected_role"] == "TEAM"

        # Check that a keyboard is provided
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]
        assert keyboard is not None

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_candidate_role_selection_calls_service(
        self, mock_get_service, mock_context, mock_service_data
    ):
        """Test that candidate role selection calls the participant list service."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:CANDIDATE"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        mock_service = Mock()
        mock_service.get_candidates_list = AsyncMock(return_value=mock_service_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_role_selection(update, mock_context)

        # Verify service was called
        mock_service.get_candidates_list.assert_called_once_with(offset=0, page_size=20)

    @pytest.mark.asyncio
    async def test_team_role_selection_keyboard_structure(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection creates proper keyboard structure."""
        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Get the keyboard from the call
        call_args = mock_team_update.callback_query.edit_message_text.call_args
        keyboard = call_args[1]["reply_markup"]

        # Check that keyboard has expected structure
        # Should have "All participants" button, department buttons, and "No department" button
        assert (
            len(keyboard.inline_keyboard) >= 3
        )  # At least all participants, some departments, no department

        # Check first button is "All participants"
        first_row = keyboard.inline_keyboard[0]
        assert len(first_row) == 1
        assert "Все Тимы" in first_row[0].text
        assert first_row[0].callback_data == "list:filter:all"

        # Check last button is "No department"
        last_row = keyboard.inline_keyboard[-1]
        assert len(last_row) == 1
        assert "Без департамента" in last_row[0].text
        assert last_row[0].callback_data == "list:filter:none"

    @pytest.mark.asyncio
    async def test_team_role_selection_sets_context(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection properly sets context data."""
        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Verify context is set correctly
        assert mock_context.user_data["selected_role"] == "TEAM"

        # Verify callback query was answered
        mock_team_update.callback_query.answer.assert_called_once()


class TestPaginationNavigationHandler:
    """Test pagination navigation functionality."""

    @pytest.fixture
    def mock_context_with_state(self):
        """Create mock context with pagination state."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"current_role": "TEAM", "current_offset": 20}
        return context

    @pytest.fixture
    def mock_next_update(self):
        """Create mock update for next page navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:NEXT"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_prev_update(self):
        """Create mock update for previous page navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:PREV"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_service_data_page2(self):
        """Create mock service response for offset 20."""
        return {
            "formatted_list": "21. **Иванов Иван Иванович**\n   👕 Размер: L\n   ⛪ Церковь: Церковь 2\n   📅 Дата рождения: 02.02.1985",
            "has_prev": True,
            "has_next": True,
            "total_count": 50,
            "current_offset": 20,
            "next_offset": 40,
            "prev_offset": 0,
            "actual_displayed": 1,
        }

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_next_navigation_updates_page_state(
        self,
        mock_get_service,
        mock_next_update,
        mock_context_with_state,
        mock_service_data_page2,
    ):
        """Test that NEXT navigation updates page state correctly."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value=mock_service_data_page2
        )
        mock_get_service.return_value = mock_service

        # Execute
        result = await handle_list_navigation(mock_next_update, mock_context_with_state)

        # Verify offset state updated
        assert mock_context_with_state.user_data["current_offset"] == 40

        # Verify service called twice: first with current offset, then with new offset
        assert mock_service.get_team_members_list.call_count == 2
        # First call gets pagination info from current offset (with default department=None)
        mock_service.get_team_members_list.assert_any_call(
            department=None, offset=20, page_size=20
        )
        # Second call gets data for new offset (with default department=None)
        mock_service.get_team_members_list.assert_any_call(
            department=None, offset=40, page_size=20
        )

        # Verify response includes range info (shows current data from service)
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        # Allow MarkdownV2 escaped hyphen as well
        assert (
            "(элементы 21-21 из 50)" in message_text
            or "(элементы 21\\-21 из 50)" in message_text
            or "\\(элементы 21\\-21 из 50\\)" in message_text
        )

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_prev_navigation_respects_page_bounds(
        self, mock_get_service, mock_prev_update, mock_service_data_page2
    ):
        """Test that PREV navigation respects page boundaries."""
        # Setup context at offset 0
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"current_role": "TEAM", "current_offset": 0}

        mock_service = Mock()
        offset0_data = {
            **mock_service_data_page2,
            "current_offset": 0,
            "prev_offset": None,
            "has_prev": False,
        }
        mock_service.get_team_members_list = AsyncMock(return_value=offset0_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_prev_update, context)

        # Should stay at offset 0 (no prev_offset available)
        assert context.user_data["current_offset"] == 0
        mock_service.get_team_members_list.assert_called_once_with(
            department=None, offset=0, page_size=20
        )

    @pytest.mark.asyncio
    async def test_navigation_without_state_shows_error(self, mock_next_update):
        """Test navigation without role state shows error message."""
        # Context without role state
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}

        # Execute
        result = await handle_list_navigation(mock_next_update, context)

        # Should show error and return to main menu
        mock_next_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Произошла ошибка" in message_text
        assert "выберите список заново" in message_text

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_handles_candidates_role(
        self, mock_get_service, mock_next_update, mock_service_data_page2
    ):
        """Test navigation works with CANDIDATE role."""
        # Setup context with candidate role
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"current_role": "CANDIDATE", "current_offset": 0}

        mock_service = Mock()
        mock_service.get_candidates_list = AsyncMock(
            return_value=mock_service_data_page2
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_next_update, context)

        # Should call candidates service twice: current offset then new offset
        assert mock_service.get_candidates_list.call_count == 2
        # First call gets pagination info from current offset
        mock_service.get_candidates_list.assert_any_call(offset=0, page_size=20)
        # Second call gets data for new offset
        mock_service.get_candidates_list.assert_any_call(offset=40, page_size=20)

        # Should update offset to next_offset from mock data
        assert context.user_data["current_offset"] == 40

        # Should show candidate title
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Список кандидатов" in message_text

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_shows_pagination_controls(
        self,
        mock_get_service,
        mock_next_update,
        mock_context_with_state,
        mock_service_data_page2,
    ):
        """Test that navigation displays proper pagination controls."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value=mock_service_data_page2
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_next_update, mock_context_with_state)

        # Verify pagination keyboard included
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        assert "reply_markup" in call_args[1]

        keyboard = call_args[1]["reply_markup"]
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        # Should have PREV, NEXT, and MAIN_MENU buttons
        prev_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:PREV"]
        next_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:NEXT"]
        main_buttons = [
            btn for btn in buttons if btn.callback_data == "list_nav:MAIN_MENU"
        ]

        assert len(prev_buttons) == 1
        assert len(next_buttons) == 1
        assert len(main_buttons) == 1

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.main_menu_button")
    async def test_main_menu_navigation_calls_proper_handler(
        self, mock_main_menu_button
    ):
        """Test that MAIN_MENU navigation calls the proper handler."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:MAIN_MENU"
        update.callback_query.answer = AsyncMock()
        update.callback_query.message = Mock()
        update.callback_query.message.edit_text = AsyncMock()
        update.callback_query.message.reply_text = AsyncMock()
        update.callback_query.from_user = Mock()
        update.callback_query.from_user.id = 12345
        update.callback_query.from_user.username = "testuser"
        update.effective_user = update.callback_query.from_user

        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}  # Real dict needed for main_menu_button
        mock_main_menu_button.return_value = 10  # SearchStates.MAIN_MENU

        # Execute
        result = await handle_list_navigation(update, context)

        # Should call main_menu_button handler
        mock_main_menu_button.assert_called_once_with(update, context)
        assert result == 10

    @pytest.mark.asyncio
    async def test_role_selection_stores_context_state(self):
        """Test that role selection stores pagination state in context."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}

        # Execute
        await handle_role_selection(update, context)

        # Verify state stored (TEAM role now stores selected_role and shows department selection)
        assert context.user_data["selected_role"] == "TEAM"


class TestTrimmingLogicAndPagination:
    """Test message trimming logic and pagination continuity."""

    @pytest.fixture
    def mock_service_data_with_trimming(self):
        """Create mock service response that would be trimmed."""
        return {
            "formatted_list": "Very long message content that exceeds limits...",
            "has_prev": False,
            "has_next": True,
            "total_count": 100,
            "current_offset": 0,
            "next_offset": 18,  # Next offset based on actual displayed count
            "prev_offset": None,
            "actual_displayed": 18,  # Less than page_size=20 due to trimming
        }

    @pytest.mark.asyncio
    async def test_team_role_shows_department_keyboard_not_list(
        self, mock_service_data_with_trimming
    ):
        """Test that team role shows department keyboard instead of list."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()

        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}

        # Execute
        await handle_role_selection(update, context)

        # Should show department keyboard, not a list with pagination
        call_args = update.callback_query.edit_message_text.call_args
        keyboard = call_args[1]["reply_markup"]
        message_text = call_args[1]["text"]

        # Verify it's the department selection message, not a list
        assert "Выберите департамент для фильтрации участников команды" in message_text

        # Verify there are no pagination buttons (PREV/NEXT) since this is department selection
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        next_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:NEXT"]
        prev_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:PREV"]

        assert len(next_buttons) == 0, "Department selection should not have pagination"
        assert len(prev_buttons) == 0, "Department selection should not have pagination"


class TestDepartmentSelectionHandler:
    """Test department selection handler functionality."""

    @pytest.fixture
    def mock_department_update(self):
        """Create mock update for department filter selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list:filter:department:Finance"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_all_participants_update(self):
        """Create mock update for all participants filter."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list:filter:all"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_no_department_update(self):
        """Create mock update for no department filter."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list:filter:none"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_department_filter_selection_calls_service_with_department(
        self, mock_get_service, mock_department_update, mock_context
    ):
        """Test department filter selection calls service with specific department."""
        from src.bot.handlers.list_handlers import handle_department_filter_selection

        # Setup mock service
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. Чиф: **Finance Chief**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_department_filter_selection(mock_department_update, mock_context)

        # Should call service with department filter
        mock_service.get_team_members_list.assert_called_once_with(
            department="Finance", offset=0, page_size=20
        )

        # Should answer callback and show filtered results
        mock_department_update.callback_query.answer.assert_called_once()
        mock_department_update.callback_query.edit_message_text.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_all_participants_filter_calls_service_without_department(
        self, mock_get_service, mock_all_participants_update, mock_context
    ):
        """Test all participants filter calls service without department filter."""
        from src.bot.handlers.list_handlers import handle_department_filter_selection

        # Setup mock service
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. Чиф: **All Team Members**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_department_filter_selection(
            mock_all_participants_update, mock_context
        )

        # Should call service without department filter (None)
        mock_service.get_team_members_list.assert_called_once_with(
            department=None, offset=0, page_size=20
        )

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_no_department_filter_calls_service_with_unassigned(
        self, mock_get_service, mock_no_department_update, mock_context
    ):
        """Test no department filter calls service with unassigned filter."""
        from src.bot.handlers.list_handlers import handle_department_filter_selection

        # Setup mock service
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. **Unassigned Member**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_department_filter_selection(
            mock_no_department_update, mock_context
        )

        # Should call service with "unassigned" filter
        mock_service.get_team_members_list.assert_called_once_with(
            department="unassigned", offset=0, page_size=20
        )

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_department_filter_stores_context_state(
        self, mock_get_service, mock_department_update, mock_context
    ):
        """Test department filter stores pagination and filter state in context."""
        from src.bot.handlers.list_handlers import handle_department_filter_selection

        # Setup mock service
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. **Finance Member**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_department_filter_selection(mock_department_update, mock_context)

        # Should store role, department, and offset in context
        assert mock_context.user_data["current_role"] == "TEAM"
        assert mock_context.user_data["current_department"] == "Finance"
        assert mock_context.user_data["current_offset"] == 0

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_department_filter_includes_filter_in_title(
        self, mock_get_service, mock_department_update, mock_context
    ):
        """Test department filter includes department name in list title."""
        from src.bot.handlers.list_handlers import handle_department_filter_selection

        # Setup mock service
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. **Finance Member**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_department_filter_selection(mock_department_update, mock_context)

        # Should include department in title
        call_args = mock_department_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Finance" in message_text


class TestRoleSelectionWithDepartmentFilter:
    """Test role selection handler with department filter integration."""

    @pytest.fixture
    def mock_team_update(self):
        """Create mock update for team selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_candidate_update(self):
        """Create mock update for candidate selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:CANDIDATE"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_team_role_selection_shows_department_filter_keyboard(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection now shows department filter keyboard instead of direct list."""
        await handle_role_selection(mock_team_update, mock_context)

        # Should answer the callback query
        mock_team_update.callback_query.answer.assert_called_once()

        # Should edit message with department selection keyboard, not participant list
        mock_team_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_team_update.callback_query.edit_message_text.call_args

        message_text = call_args[1]["text"]
        # Should ask for department selection
        assert (
            "Выберите департамент" in message_text
            or "департамент" in message_text.lower()
        )

        # Should include department filter keyboard
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]

        # Should have department selection buttons
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]

        # Should have "All participants" button
        all_buttons = [btn for btn in buttons if "Все Тимы" in btn.text]
        assert len(all_buttons) == 1
        assert all_buttons[0].callback_data == "list:filter:all"

        # Should have "No department" button
        none_buttons = [btn for btn in buttons if "Без департамента" in btn.text]
        assert len(none_buttons) == 1
        assert none_buttons[0].callback_data == "list:filter:none"

        # Should have at least one department button
        dept_buttons = [
            btn
            for btn in buttons
            if btn.callback_data.startswith("list:filter:department:")
        ]
        assert len(dept_buttons) > 0

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_candidate_role_selection_still_shows_direct_list(
        self, mock_get_service, mock_candidate_update, mock_context
    ):
        """Test that candidate role selection still shows direct list (no department filtering)."""
        # Setup mock service for candidates
        mock_service = Mock()
        mock_service.get_candidates_list = AsyncMock(
            return_value={
                "formatted_list": "1\\. **Candidate Test**\n",
                "has_prev": False,
                "has_next": False,
                "total_count": 1,
                "current_offset": 0,
                "next_offset": None,
                "prev_offset": None,
                "actual_displayed": 1,
            }
        )
        mock_get_service.return_value = mock_service

        await handle_role_selection(mock_candidate_update, mock_context)

        # Should call candidate service directly
        mock_service.get_candidates_list.assert_called_once_with(offset=0, page_size=20)

        # Should show candidate list, not department selection
        call_args = mock_candidate_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Список кандидатов" in message_text

    @pytest.mark.asyncio
    async def test_team_role_selection_stores_role_state(
        self, mock_team_update, mock_context
    ):
        """Test that team role selection stores role state for department filtering."""
        await handle_role_selection(mock_team_update, mock_context)

        # Should store team role in context for later use by department filter
        assert mock_context.user_data.get("selected_role") == "TEAM"


class TestNavigationWithDepartmentContext:
    """Test navigation handlers with department filtering context."""

    @pytest.fixture
    def mock_next_update(self):
        """Create mock update for next page navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:NEXT"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_prev_update(self):
        """Create mock update for previous page navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:PREV"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        return update

    @pytest.fixture
    def mock_department_context(self):
        """Create mock context with department filtering state."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            "current_role": "TEAM",
            "current_department": "Finance",
            "current_offset": 0,
        }
        return context

    @pytest.fixture
    def mock_all_participants_context(self):
        """Create mock context with 'all participants' filtering state."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            "current_role": "TEAM",
            "current_department": "all",
            "current_offset": 20,
        }
        return context

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_preserves_department_filter(
        self, mock_get_service, mock_next_update, mock_department_context
    ):
        """Test that navigation preserves department filter when paginating."""
        # Setup mock service
        mock_service = Mock()
        current_data = {
            "formatted_list": "1\\. **Finance Member 1**\n",
            "has_prev": False,
            "has_next": True,
            "total_count": 50,
            "current_offset": 0,
            "next_offset": 20,
            "prev_offset": None,
            "actual_displayed": 20,
        }
        next_data = {
            "formatted_list": "21\\. **Finance Member 21**\n",
            "has_prev": True,
            "has_next": True,
            "total_count": 50,
            "current_offset": 20,
            "next_offset": 40,
            "prev_offset": 0,
            "actual_displayed": 20,
        }
        mock_service.get_team_members_list = AsyncMock(
            side_effect=[current_data, next_data]
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_next_update, mock_department_context)

        # Should call service twice with Finance department filter preserved
        assert mock_service.get_team_members_list.call_count == 2
        # First call for current offset
        mock_service.get_team_members_list.assert_any_call(
            department="Finance", offset=0, page_size=20
        )
        # Second call for new offset
        mock_service.get_team_members_list.assert_any_call(
            department="Finance", offset=20, page_size=20
        )

        # Should update context offset
        assert mock_department_context.user_data["current_offset"] == 20

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_preserves_all_participants_filter(
        self, mock_get_service, mock_prev_update, mock_all_participants_context
    ):
        """Test that navigation preserves 'all participants' filter (None department)."""
        # Setup mock service
        mock_service = Mock()
        current_data = {
            "formatted_list": "21\\. **All Member 21**\n",
            "has_prev": True,
            "has_next": True,
            "total_count": 50,
            "current_offset": 20,
            "next_offset": 40,
            "prev_offset": 0,
            "actual_displayed": 20,
        }
        prev_data = {
            "formatted_list": "1\\. **All Member 1**\n",
            "has_prev": False,
            "has_next": True,
            "total_count": 50,
            "current_offset": 0,
            "next_offset": 20,
            "prev_offset": None,
            "actual_displayed": 20,
        }
        mock_service.get_team_members_list = AsyncMock(
            side_effect=[current_data, prev_data]
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_prev_update, mock_all_participants_context)

        # Should call service twice with None department filter (all participants)
        assert mock_service.get_team_members_list.call_count == 2
        # First call for current offset
        mock_service.get_team_members_list.assert_any_call(
            department=None, offset=20, page_size=20
        )
        # Second call for new offset
        mock_service.get_team_members_list.assert_any_call(
            department=None, offset=0, page_size=20
        )

        # Should update context offset
        assert mock_all_participants_context.user_data["current_offset"] == 0

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_shows_department_in_title(
        self, mock_get_service, mock_next_update, mock_department_context
    ):
        """Test that navigation displays department filter in list title."""
        # Setup mock service
        mock_service = Mock()
        current_data = {
            "formatted_list": "1\\. **Finance Member 1**\n",
            "has_prev": False,
            "has_next": True,
            "total_count": 50,
            "current_offset": 0,
            "next_offset": 20,
            "prev_offset": None,
            "actual_displayed": 20,
        }
        next_data = {
            "formatted_list": "21\\. **Finance Member 21**\n",
            "has_prev": True,
            "has_next": True,
            "total_count": 50,
            "current_offset": 20,
            "next_offset": 40,
            "prev_offset": 0,
            "actual_displayed": 20,
        }
        mock_service.get_team_members_list = AsyncMock(
            side_effect=[current_data, next_data]
        )
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_next_update, mock_department_context)

        # Should show department name in title
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Finance" in message_text
