"""
Integration tests for list handlers with search conversation.

Tests that the participant list functionality integrates properly
with the main search conversation handler.
"""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import CallbackQuery, Message, Update
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
        context.user_data = {}
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
        """Test that role selection callback handler exists and shows department selection for TEAM."""
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

        # Verify department selection keyboard was shown (not direct service call)
        mock_role_callback_update.callback_query.edit_message_text.assert_called_once()
        call_args = mock_role_callback_update.callback_query.edit_message_text.call_args
        message_text = call_args[1]["text"]

        # Should show department selection instead of participant list
        assert "Выберите департамент" in message_text

        # Should have keyboard with department options
        assert "reply_markup" in call_args[1]

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


class TestDepartmentFilteringIntegration:
    """Test complete department filtering workflow integration."""

    @pytest.fixture
    def conversation_handler(self):
        """Get the conversation handler."""
        return get_search_conversation_handler()

    @pytest.fixture
    def mock_context(self):
        """Create mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.fixture
    def mock_team_role_update(self):
        """Create mock update for team role selection."""
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
    def mock_department_finance_update(self):
        """Create mock update for Finance department selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list:filter:department:Finance"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_chat = Mock()
        update.effective_chat.id = 12345
        update.effective_user = Mock()
        update.effective_user.id = 67890
        return update

    @pytest.fixture
    def mock_department_all_update(self):
        """Create mock update for All participants selection."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list:filter:all"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_chat = Mock()
        update.effective_chat.id = 12345
        update.effective_user = Mock()
        update.effective_user.id = 67890
        return update

    @pytest.fixture
    def mock_navigation_next_update(self):
        """Create mock update for next page navigation."""
        update = Mock(spec=Update)
        update.callback_query = Mock(spec=CallbackQuery)
        update.callback_query.data = "list_nav:NEXT"
        update.callback_query.answer = AsyncMock()
        update.callback_query.edit_message_text = AsyncMock()
        update.effective_chat = Mock()
        update.effective_chat.id = 12345
        update.effective_user = Mock()
        update.effective_user.id = 67890
        return update

    def test_department_filter_callbacks_included_in_conversation(
        self, conversation_handler
    ):
        """Test that department filter callbacks are included in conversation states."""
        # Check that list:filter callback handlers are included in conversation states
        callback_patterns = []

        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern"):
                    callback_patterns.append(str(handler.pattern))

        # Should include patterns for department filter selection
        filter_patterns = [p for p in callback_patterns if "list:filter:" in p]
        assert (
            len(filter_patterns) > 0
        ), "Should have department filter callback patterns"

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.service_factory")
    async def test_complete_department_workflow_finance_filter(
        self,
        mock_service_factory,
        conversation_handler,
        mock_team_role_update,
        mock_department_finance_update,
        mock_context,
    ):
        """Test complete workflow: Team selection → Finance department → Filtered list."""
        # Setup mock service
        mock_service = Mock()
        mock_finance_data = {
            "formatted_list": "1\\. Чиф: **Finance Chief**\n   🏢 Департамент: Finance\n   ⛪ Церковь: Test Church",
            "has_prev": False,
            "has_next": False,
            "total_count": 1,
            "current_offset": 0,
            "next_offset": None,
            "prev_offset": None,
            "actual_displayed": 1,
        }
        mock_service.get_team_members_list = AsyncMock(return_value=mock_finance_data)
        mock_service_factory.get_participant_list_service.return_value = mock_service

        # Find handlers in conversation states
        role_handler = None
        filter_handler = None

        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern"):
                    pattern = str(handler.pattern)
                    if "list_role:" in pattern and not role_handler:
                        role_handler = handler
                    elif "list:filter:" in pattern and not filter_handler:
                        filter_handler = handler

        assert role_handler is not None, "Role handler should be found"
        assert filter_handler is not None, "Filter handler should be found"

        # Step 1: Team role selection (should show department selection)
        await role_handler.callback(mock_team_role_update, mock_context)

        # Verify department selection was shown
        mock_team_role_update.callback_query.edit_message_text.assert_called_once()
        team_call_args = (
            mock_team_role_update.callback_query.edit_message_text.call_args
        )
        team_message = team_call_args[1]["text"]
        assert "Выберите департамент" in team_message

        # Verify selected_role was stored
        assert mock_context.user_data.get("selected_role") == "TEAM"

        # Step 2: Finance department selection (should show filtered list)
        await filter_handler.callback(mock_department_finance_update, mock_context)

        # Verify service was called with Finance filter
        mock_service.get_team_members_list.assert_called_once_with(
            department="Finance", offset=0, page_size=20
        )

        # Verify filtered list was shown
        mock_department_finance_update.callback_query.edit_message_text.assert_called_once()
        finance_call_args = (
            mock_department_finance_update.callback_query.edit_message_text.call_args
        )
        finance_message = finance_call_args[1]["text"]
        assert "Finance" in finance_message
        assert "Finance Chief" in finance_message

        # Verify context was updated
        assert mock_context.user_data.get("current_role") == "TEAM"
        assert mock_context.user_data.get("current_department") == "Finance"
        assert mock_context.user_data.get("current_offset") == 0

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.service_factory")
    async def test_complete_department_workflow_all_participants(
        self,
        mock_service_factory,
        conversation_handler,
        mock_team_role_update,
        mock_department_all_update,
        mock_context,
    ):
        """Test complete workflow: Team selection → All participants → Complete list."""
        # Setup mock service
        mock_service = Mock()
        mock_all_data = {
            "formatted_list": "1\\. Чиф: **Team Lead**\n2\\. **Team Member**\n",
            "has_prev": False,
            "has_next": True,
            "total_count": 25,
            "current_offset": 0,
            "next_offset": 20,
            "prev_offset": None,
            "actual_displayed": 20,
        }
        mock_service.get_team_members_list = AsyncMock(return_value=mock_all_data)
        mock_service_factory.get_participant_list_service.return_value = mock_service

        # Find handlers
        role_handler = None
        filter_handler = None

        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern"):
                    pattern = str(handler.pattern)
                    if "list_role:" in pattern and not role_handler:
                        role_handler = handler
                    elif "list:filter:" in pattern and not filter_handler:
                        filter_handler = handler

        # Step 1: Team role selection
        await role_handler.callback(mock_team_role_update, mock_context)

        # Step 2: All participants selection
        await filter_handler.callback(mock_department_all_update, mock_context)

        # Verify service was called with None filter (all participants)
        mock_service.get_team_members_list.assert_called_once_with(
            department=None, offset=0, page_size=20
        )

        # Verify all participants list was shown
        mock_department_all_update.callback_query.edit_message_text.assert_called_once()
        all_call_args = (
            mock_department_all_update.callback_query.edit_message_text.call_args
        )
        all_message = all_call_args[1]["text"]
        assert "Все Тимы" in all_message
        assert "Team Lead" in all_message

        # Verify context was updated correctly
        assert mock_context.user_data.get("current_role") == "TEAM"
        assert mock_context.user_data.get("current_department") == "all"

    @pytest.mark.asyncio
    @patch("src.bot.handlers.list_handlers.service_factory")
    async def test_department_navigation_preserves_context(
        self,
        mock_service_factory,
        conversation_handler,
        mock_navigation_next_update,
        mock_context,
    ):
        """Test that navigation preserves department context correctly."""
        # Setup context with department filter
        mock_context.user_data = {
            "current_role": "TEAM",
            "current_department": "Finance",
            "current_offset": 0,
        }

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
        mock_service_factory.get_participant_list_service.return_value = mock_service

        # Find navigation handler
        nav_handler = None
        for state_handlers in conversation_handler.states.values():
            for handler in state_handlers:
                if hasattr(handler, "pattern") and "list_nav:" in str(handler.pattern):
                    nav_handler = handler
                    break
            if nav_handler:
                break

        assert nav_handler is not None, "Navigation handler should be found"

        # Execute navigation
        await nav_handler.callback(mock_navigation_next_update, mock_context)

        # Verify service was called with preserved Finance filter
        assert mock_service.get_team_members_list.call_count == 2
        mock_service.get_team_members_list.assert_any_call(
            department="Finance", offset=0, page_size=20
        )
        mock_service.get_team_members_list.assert_any_call(
            department="Finance", offset=20, page_size=20
        )

        # Verify context offset was updated
        assert mock_context.user_data["current_offset"] == 20

        # Verify department was preserved in title
        nav_call_args = (
            mock_navigation_next_update.callback_query.edit_message_text.call_args
        )
        nav_message = nav_call_args[1]["text"]
        assert "Finance" in nav_message
