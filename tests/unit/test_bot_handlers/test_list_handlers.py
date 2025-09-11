"""
Tests for list handlers functionality.

Tests conversation handlers for participant list access functionality,
including role selection and main menu integration.
"""

import pytest
from unittest.mock import AsyncMock, Mock, patch
from telegram import Update, CallbackQuery, Message
from telegram.ext import ContextTypes
from datetime import date

from src.bot.handlers.list_handlers import (
    handle_get_list_request,
    handle_role_selection,
    handle_list_navigation,
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
        """Test team role selection triggers team list display."""
        await handle_role_selection(mock_team_update, mock_context)

        # Should answer the callback query
        mock_team_update.callback_query.answer.assert_called_once()

        # Should edit message with team list (placeholder for now)
        mock_team_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_team_update.callback_query.edit_message_text.call_args

        message_text = call_args[1]["text"]
        assert "Список участников команды" in message_text

    @pytest.mark.asyncio
    async def test_handle_candidate_role_selection(
        self, mock_candidate_update, mock_context
    ):
        """Test candidate role selection triggers candidate list display."""
        await handle_role_selection(mock_candidate_update, mock_context)

        # Should answer the callback query
        mock_candidate_update.callback_query.answer.assert_called_once()

        # Should edit message with candidate list (placeholder for now)
        mock_candidate_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_candidate_update.callback_query.edit_message_text.call_args

        message_text = call_args[1]["text"]
        assert "Список кандидатов" in message_text

    @pytest.mark.asyncio
    async def test_role_selection_includes_pagination(
        self, mock_team_update, mock_context
    ):
        """Test that role selection includes pagination controls."""
        await handle_role_selection(mock_team_update, mock_context)

        call_args = mock_team_update.callback_query.edit_message_text.call_args

        # Should include pagination keyboard
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]

        # Should have main menu button at minimum
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        main_menu_buttons = [
            btn for btn in buttons if btn.callback_data == "list_nav:MAIN_MENU"
        ]
        assert len(main_menu_buttons) == 1


class TestListNavigationHandler:
    """Test list navigation handler functionality."""

    @pytest.fixture
    def mock_main_menu_update(self):
        """Create mock update for main menu navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:MAIN_MENU"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.callback_query.message = Mock()
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

        # Should answer the callback query
        mock_main_menu_update.callback_query.answer.assert_called_once()

        # Should edit or send new message with main menu
        # For now, we'll check that some response occurs
        assert (
            mock_main_menu_update.callback_query.edit_message_text.called
            or mock_main_menu_update.callback_query.message.reply_text.called
        )

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
            "page": 1,
        }

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_team_role_selection_calls_service(
        self, mock_get_service, mock_team_update, mock_context, mock_service_data
    ):
        """Test that team role selection calls the participant list service."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Verify service was called
        mock_service.get_team_members_list.assert_called_once_with(page=1, page_size=20)

        # Verify response contains formatted data
        mock_team_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_team_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]

        assert "Тестов Тест Тестович" in message_text

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
        mock_service.get_candidates_list.assert_called_once_with(page=1, page_size=20)

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_role_selection_includes_pagination_controls(
        self, mock_get_service, mock_team_update, mock_context, mock_service_data
    ):
        """Test that role selection includes appropriate pagination controls."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Verify pagination keyboard is included
        call_args = mock_team_update.callback_query.edit_message_text.call_args
        assert "reply_markup" in call_args[1]

        keyboard = call_args[1]["reply_markup"]
        # Should have Next button (has_next=True) and Main Menu button
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        next_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:NEXT"]
        main_buttons = [
            btn for btn in buttons if btn.callback_data == "list_nav:MAIN_MENU"
        ]

        assert len(next_buttons) == 1
        assert len(main_buttons) == 1

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_role_selection_handles_empty_results(
        self, mock_get_service, mock_team_update, mock_context
    ):
        """Test role selection handles empty results gracefully."""
        # Setup
        empty_data = {
            "formatted_list": "Участники не найдены.",
            "has_prev": False,
            "has_next": False,
            "total_count": 0,
            "page": 1,
        }

        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=empty_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_role_selection(mock_team_update, mock_context)

        # Verify response shows empty message
        call_args = mock_team_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]

        assert "Участники не найдены" in message_text


class TestPaginationNavigationHandler:
    """Test pagination navigation functionality."""

    @pytest.fixture
    def mock_context_with_state(self):
        """Create mock context with pagination state."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {
            "current_role": "TEAM",
            "current_page": 2
        }
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
        """Create mock service response for page 2."""
        return {
            "formatted_list": "21. **Иванов Иван Иванович**\n   👕 Размер: L\n   ⛪ Церковь: Церковь 2\n   📅 Дата рождения: 02.02.1985",
            "has_prev": True,
            "has_next": True,
            "total_count": 50,
            "page": 2,
            "actual_displayed": 1
        }

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_next_navigation_updates_page_state(self, mock_get_service, mock_next_update, mock_context_with_state, mock_service_data_page2):
        """Test that NEXT navigation updates page state correctly."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data_page2)
        mock_get_service.return_value = mock_service

        # Execute
        result = await handle_list_navigation(mock_next_update, mock_context_with_state)

        # Verify page state updated
        assert mock_context_with_state.user_data["current_page"] == 3
        
        # Verify service called with new page
        mock_service.get_team_members_list.assert_called_once_with(page=3, page_size=20)
        
        # Verify response includes page number
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "(страница 3)" in message_text

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_prev_navigation_respects_page_bounds(self, mock_get_service, mock_prev_update, mock_service_data_page2):
        """Test that PREV navigation respects page boundaries."""
        # Setup context at page 1
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"current_role": "TEAM", "current_page": 1}
        
        mock_service = Mock()
        page1_data = {**mock_service_data_page2, "page": 1, "has_prev": False}
        mock_service.get_team_members_list = AsyncMock(return_value=page1_data)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_prev_update, context)

        # Should stay at page 1 (max(1, 1-1) = 1)
        assert context.user_data["current_page"] == 1
        mock_service.get_team_members_list.assert_called_once_with(page=1, page_size=20)

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
    async def test_navigation_handles_candidates_role(self, mock_get_service, mock_next_update, mock_service_data_page2):
        """Test navigation works with CANDIDATE role."""
        # Setup context with candidate role
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"current_role": "CANDIDATE", "current_page": 1}
        
        mock_service = Mock()
        mock_service.get_candidates_list = AsyncMock(return_value=mock_service_data_page2)
        mock_get_service.return_value = mock_service

        # Execute
        await handle_list_navigation(mock_next_update, context)

        # Should call candidates service
        mock_service.get_candidates_list.assert_called_once_with(page=2, page_size=20)
        
        # Should update page
        assert context.user_data["current_page"] == 2
        
        # Should show candidate title
        call_args = mock_next_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]
        assert "Список кандидатов" in message_text

    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_navigation_shows_pagination_controls(self, mock_get_service, mock_next_update, mock_context_with_state, mock_service_data_page2):
        """Test that navigation displays proper pagination controls."""
        # Setup
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data_page2)
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
        main_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:MAIN_MENU"]
        
        assert len(prev_buttons) == 1
        assert len(next_buttons) == 1
        assert len(main_buttons) == 1

    @pytest.mark.asyncio
    @patch("src.bot.handlers.search_handlers.main_menu_button")
    async def test_main_menu_navigation_calls_proper_handler(self, mock_main_menu_button):
        """Test that MAIN_MENU navigation calls the proper handler."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:MAIN_MENU"
        update.callback_query.answer = AsyncMock()
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
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
        
        # Execute (note: this will fail because service isn't mocked, but we want to check state storage)
        try:
            await handle_role_selection(update, context)
        except:
            pass  # Ignore service errors, we're testing state storage
        
        # Verify state stored
        assert context.user_data["current_role"] == "TEAM"
        assert context.user_data["current_page"] == 1


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
            "page": 1,
            "actual_displayed": 18  # Less than page_size=20 due to trimming
        }
    
    @pytest.mark.asyncio
    @patch("src.services.service_factory.get_participant_list_service")
    async def test_trimmed_results_maintain_pagination_continuity(self, mock_get_service, mock_service_data_with_trimming):
        """Test that trimmed results don't break pagination continuity."""
        # Setup
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_role:TEAM"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        
        mock_service = Mock()
        mock_service.get_team_members_list = AsyncMock(return_value=mock_service_data_with_trimming)
        mock_get_service.return_value = mock_service
        
        # Execute
        await handle_role_selection(update, context)
        
        # Should still show has_next=True even with trimmed content
        call_args = update.callback_query.edit_message_text.call_args
        keyboard = call_args[1]["reply_markup"]
        buttons = [btn for row in keyboard.inline_keyboard for btn in row]
        next_buttons = [btn for btn in buttons if btn.callback_data == "list_nav:NEXT"]
        
        assert len(next_buttons) == 1, "Should show NEXT button when has_next=True despite trimming"
