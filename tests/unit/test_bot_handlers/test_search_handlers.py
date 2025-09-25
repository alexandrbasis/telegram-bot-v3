"""
Unit tests for search bot handlers and conversation flow.

Tests bot handler functions for name search functionality with ConversationHandler
state management and Russian interface.
"""

from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from telegram import (
    CallbackQuery,
    Chat,
    InlineKeyboardMarkup,
    Message,
    ReplyKeyboardMarkup,
    Update,
    User,
)
from telegram.ext import ContextTypes

from src.bot.handlers.floor_search_handlers import FloorSearchStates
from src.bot.handlers.search_handlers import (
    SearchStates,
    back_to_search_modes,
    create_participant_selection_keyboard,
    get_welcome_message,
    handle_search_floor_mode,
    handle_search_name_mode,
    handle_search_room_mode,
    initialize_main_menu_session,
    main_menu_button,
    process_name_search,
    process_name_search_enhanced,
    search_button,
    start_command,
)
from src.models.participant import Participant
from src.services.search_service import SearchResult
from src.services.user_interaction_logger import UserInteractionLogger


class TestSearchStates:
    """Test conversation states enum."""

    def test_search_states_values(self):
        """Test that search states have correct integer values."""
        assert SearchStates.MAIN_MENU == 10
        assert SearchStates.SEARCH_MODE_SELECTION == 13
        assert SearchStates.WAITING_FOR_NAME == 11
        assert SearchStates.SHOWING_RESULTS == 12


class TestStartCommandHandler:
    """Test /start command handler."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for message."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        chat = Mock(spec=Chat)

        user.id = 123456
        user.first_name = "Test"
        user.language_code = "ru"

        chat.id = 123456
        chat.type = "private"

        message.from_user = user
        message.chat = chat
        message.reply_text = AsyncMock()

        update.message = message
        update.callback_query = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_start_command_russian_greeting(
        self, mock_update_message, mock_context
    ):
        """Test /start command sends Russian greeting with search button."""
        result = await start_command(mock_update_message, mock_context)

        # Should send Russian welcome message
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args

        # Check Russian text in message
        message_text = call_args[1]["text"]
        assert "Добро пожаловать" in message_text
        assert "Tres Dias" in message_text
        assert "участников" in message_text

        # Should include reply keyboard for navigation
        assert "reply_markup" in call_args[1]
        keyboard = call_args[1]["reply_markup"]
        assert isinstance(keyboard, ReplyKeyboardMarkup)

        # Should return MAIN_MENU state
        assert result == SearchStates.MAIN_MENU

    @pytest.mark.asyncio
    async def test_start_command_user_data_initialization(
        self, mock_update_message, mock_context
    ):
        """Test that /start command initializes user data."""
        await start_command(mock_update_message, mock_context)

        # Should initialize user_data
        assert "search_results" in mock_context.user_data
        assert mock_context.user_data["search_results"] == []
        assert "force_direct_name_input" in mock_context.user_data
        assert mock_context.user_data["force_direct_name_input"] is True

    @patch("src.bot.handlers.search_handlers.initialize_main_menu_session")
    @patch("src.bot.handlers.search_handlers.get_welcome_message")
    @pytest.mark.asyncio
    async def test_start_command_uses_shared_initialization(
        self,
        mock_get_welcome_message,
        mock_initialize_main_menu_session,
        mock_update_message,
        mock_context,
    ):
        """Test that start_command uses shared initialization helpers."""
        # Setup mocks
        mock_get_welcome_message.return_value = "Test welcome message"

        # Execute handler
        result = await start_command(mock_update_message, mock_context)

        # Verify shared helpers were called
        mock_initialize_main_menu_session.assert_called_once_with(mock_context)
        mock_get_welcome_message.assert_called_once()

        # Verify message uses shared welcome text
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args
        assert "Test welcome message" in call_args[1]["text"]

        # Should return correct state
        assert result == SearchStates.MAIN_MENU


class TestSearchButtonHandler:
    """Test search button callback handler."""

    @pytest.fixture
    def mock_callback_query(self):
        """Mock callback query for search button."""
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "Test"

        message.edit_text = AsyncMock()

        callback_query.from_user = user
        callback_query.data = "search"
        callback_query.message = message
        callback_query.answer = AsyncMock()

        update.callback_query = callback_query
        update.message = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"search_results": []}
        return context

    @pytest.mark.asyncio
    async def test_search_button_handler(self, mock_callback_query, mock_context):
        """Test search button click handler."""
        result = await search_button(mock_callback_query, mock_context)

        # Should answer callback query
        mock_callback_query.callback_query.answer.assert_called_once()

        # Should edit message with search prompt
        mock_callback_query.callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.callback_query.message.edit_text.call_args

        # Should contain Russian search mode selection prompt
        message_text = call_args[1]["text"]
        assert "Выберите тип поиска" in message_text

        # Should return SEARCH_MODE_SELECTION state
        assert result == SearchStates.SEARCH_MODE_SELECTION


class TestProcessNameSearchHandler:
    """Test name search processing handler."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for search message."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "Test"

        message.from_user = user
        message.text = "Александр Иванов"
        message.reply_text = AsyncMock()

        update.message = message
        update.callback_query = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"search_results": []}
        return context

    @pytest.fixture
    def sample_search_results(self):
        """Sample search results for testing."""
        participant1 = Participant(
            full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
        )
        participant2 = Participant(
            full_name_ru="Александра Петрова", full_name_en="Alexandra Petrova"
        )

        return [
            SearchResult(participant=participant1, similarity_score=0.95),
            SearchResult(participant=participant2, similarity_score=0.85),
        ]

    @pytest.mark.asyncio
    async def test_process_name_search_with_results(
        self, mock_update_message, mock_context, sample_search_results
    ):
        """Test name search processing with found results."""
        with (
            patch(
                "src.bot.handlers.search_handlers.get_participant_repository"
            ) as mock_repo_getter,
            patch(
                "src.bot.handlers.search_handlers.SearchService"
            ) as mock_search_service,
        ):

            # Mock repository
            mock_repo = AsyncMock()
            mock_repo.list_all.return_value = [
                Participant(full_name_ru="Александр Иванов"),
                Participant(full_name_ru="Мария Сидорова"),
            ]
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError(
                "Enhanced search not available"
            )
            mock_repo_getter.return_value = mock_repo

            # Mock search service
            mock_service_instance = Mock()
            mock_service_instance.search_participants.return_value = (
                sample_search_results
            )
            mock_search_service.return_value = mock_service_instance

            result = await process_name_search(mock_update_message, mock_context)

            # Should call repository to get participants
            mock_repo.list_all.assert_called_once()

            # Should call search service with query
            mock_service_instance.search_participants.assert_called_once_with(
                "Александр Иванов", mock_repo.list_all.return_value
            )

            # Should reply twice: results (inline) and navigation keyboard update
            assert mock_update_message.message.reply_text.await_count == 2
            first_call = mock_update_message.message.reply_text.await_args_list[0]
            second_call = mock_update_message.message.reply_text.await_args_list[1]

            # First call: results with inline selection
            message_text = first_call.kwargs["text"]
            assert "Найдено участников" in message_text
            assert "Александр Иванов" in message_text
            assert "Александра Петрова" in message_text
            assert isinstance(first_call.kwargs["reply_markup"], InlineKeyboardMarkup)

            # Second call: navigation keyboard update
            assert "reply_markup" in second_call.kwargs
            assert isinstance(second_call.kwargs["reply_markup"], ReplyKeyboardMarkup)

            # Should store results in user_data
            assert mock_context.user_data["search_results"] == sample_search_results

            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    async def test_process_name_search_no_results(
        self, mock_update_message, mock_context
    ):
        """Test name search processing with no results found."""
        with (
            patch(
                "src.bot.handlers.search_handlers.get_participant_repository"
            ) as mock_repo_getter,
            patch(
                "src.bot.handlers.search_handlers.SearchService"
            ) as mock_search_service,
        ):

            # Mock repository
            mock_repo = AsyncMock()
            mock_repo.list_all.return_value = [
                Participant(full_name_ru="Мария Сидорова")
            ]
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError(
                "Enhanced search not available"
            )
            mock_repo_getter.return_value = mock_repo

            # Mock search service - no results
            mock_service_instance = Mock()
            mock_service_instance.search_participants.return_value = []
            mock_search_service.return_value = mock_service_instance

            result = await process_name_search(mock_update_message, mock_context)

            # Should reply with no results message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args

            # Should contain Russian "no results" text
            message_text = call_args[1]["text"]
            assert "Участники не найдены" in message_text

            # Should include reply keyboard for navigation
            assert "reply_markup" in call_args[1]

            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    async def test_process_name_search_repository_error(
        self, mock_update_message, mock_context
    ):
        """Test name search processing when repository fails."""
        with patch(
            "src.bot.handlers.search_handlers.get_participant_repository"
        ) as mock_repo_getter:

            # Mock repository that raises error
            mock_repo = AsyncMock()
            mock_repo.list_all.side_effect = Exception("Database error")
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError(
                "Enhanced search not available"
            )
            mock_repo_getter.return_value = mock_repo

            result = await process_name_search(mock_update_message, mock_context)

            # Should reply with error message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args

            # Should contain Russian error text
            message_text = call_args[1]["text"]
            assert "Ошибка" in message_text
            assert "Попробуйте позже" in message_text

            # Should return SHOWING_RESULTS state (to allow retry)
            assert result == SearchStates.SHOWING_RESULTS


class TestMainMenuButtonHandler:
    """Test main menu button handler."""

    @pytest.fixture
    def mock_callback_query(self):
        """Mock callback query for main menu button."""
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "Test"

        message.edit_text = AsyncMock()

        callback_query.from_user = user
        callback_query.data = "main_menu"
        callback_query.message = message
        callback_query.answer = AsyncMock()

        update.callback_query = callback_query
        update.message = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object with search results."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"search_results": [Mock()]}  # Some previous results
        return context

    @pytest.mark.asyncio
    async def test_main_menu_button_handler(self, mock_callback_query, mock_context):
        """Test main menu button click handler."""
        result = await main_menu_button(mock_callback_query, mock_context)

        # Should answer callback query
        mock_callback_query.callback_query.answer.assert_called_once()

        # Should edit message back to main menu (text only) and send reply keyboard
        mock_callback_query.callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.callback_query.message.edit_text.call_args
        message_text = call_args.kwargs["text"]
        assert "Добро пожаловать" in message_text
        assert "участников" in message_text

        # A separate reply_text call should include reply keyboard
        mock_callback_query.callback_query.message.reply_text.assert_called_once()
        reply_call = mock_callback_query.callback_query.message.reply_text.call_args
        assert "reply_markup" in reply_call.kwargs
        assert isinstance(reply_call.kwargs["reply_markup"], ReplyKeyboardMarkup)

        # Should clear search results
        assert mock_context.user_data["search_results"] == []

        # Should return MAIN_MENU state
        assert result == SearchStates.MAIN_MENU

    @patch("src.bot.handlers.search_handlers.initialize_main_menu_session")
    @patch("src.bot.handlers.search_handlers.get_welcome_message")
    @pytest.mark.asyncio
    async def test_main_menu_button_uses_shared_initialization(
        self,
        mock_get_welcome_message,
        mock_initialize_main_menu_session,
        mock_callback_query,
        mock_context,
    ):
        """Test that main_menu_button uses shared initialization helpers."""
        # Setup mocks
        mock_get_welcome_message.return_value = "Test unified welcome message"

        # Execute handler
        result = await main_menu_button(mock_callback_query, mock_context)

        # Verify shared helpers were called
        mock_initialize_main_menu_session.assert_called_once_with(mock_context)
        mock_get_welcome_message.assert_called_once()

        # Verify message uses shared welcome text
        mock_callback_query.callback_query.message.edit_text.assert_called_once()
        edit_call_args = mock_callback_query.callback_query.message.edit_text.call_args
        assert "Test unified welcome message" in edit_call_args.kwargs["text"]

        # Should return correct state
        assert result == SearchStates.MAIN_MENU

    @patch("src.bot.handlers.search_handlers.get_welcome_message")
    @pytest.mark.asyncio
    async def test_main_menu_button_equivalent_welcome_message(
        self, mock_get_welcome_message, mock_callback_query, mock_context
    ):
        """Test that main_menu_button shows equivalent welcome message as start_command."""
        # Setup mock to return the unified message
        unified_message = (
            "Добро пожаловать в бот Tres Dias! 🙏\n\nВыберите тип поиска участников."
        )
        mock_get_welcome_message.return_value = unified_message

        # Execute handler
        await main_menu_button(mock_callback_query, mock_context)

        # Verify the unified welcome message is used
        mock_get_welcome_message.assert_called_once()
        edit_call_args = mock_callback_query.callback_query.message.edit_text.call_args
        assert unified_message in edit_call_args.kwargs["text"]


class TestHandlerIntegration:
    """Integration tests for handler flow."""

    @pytest.mark.asyncio
    async def test_conversation_flow_states(self):
        """Test that handlers return correct conversation states."""
        # This is a basic integration test to verify state flow
        mock_update = Mock()
        mock_context = Mock()
        mock_context.user_data = {}

        # Each handler should return the expected next state
        with (
            patch("src.bot.handlers.search_handlers.get_main_menu_keyboard"),
            patch("src.bot.handlers.search_handlers.get_waiting_for_name_keyboard"),
        ):

            # Mock message for start command
            mock_update.message = Mock()
            mock_update.message.reply_text = AsyncMock()
            mock_update.callback_query = None

            start_result = await start_command(mock_update, mock_context)
            assert start_result == SearchStates.MAIN_MENU

            # Mock callback query for search button
            mock_update.callback_query = Mock()
            mock_update.callback_query.answer = AsyncMock()
            mock_update.callback_query.message = Mock()
            mock_update.callback_query.message.edit_text = AsyncMock()
            mock_update.callback_query.callback_query = None
            # Our handler also sends a follow-up message to set reply keyboard
            mock_update.callback_query.message.reply_text = AsyncMock()
            mock_update.message = None

            search_button_result = await search_button(mock_update, mock_context)
            assert search_button_result == SearchStates.SEARCH_MODE_SELECTION


class TestEnhancedSearchHandlers:
    """Test enhanced search functionality with rich results."""

    @pytest.fixture
    def enhanced_sample_search_results(self):
        """Enhanced sample search results with rich formatting."""
        from src.models.participant import Department, Role

        participants = [
            Participant(
                full_name_ru="Александр Иванов",
                full_name_en="Alexander Ivanov",
                role=Role.TEAM,
                department=Department.KITCHEN,
            ),
            Participant(
                full_name_ru="Мария Петрова",
                full_name_en="Maria Petrova",
                role=Role.CANDIDATE,
                department=Department.WORSHIP,
            ),
        ]

        return [
            (
                participants[0],
                0.95,
                "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen",
            ),
            (
                participants[1],
                0.87,
                "Мария Петрова (Maria Petrova) - CANDIDATE, Worship",
            ),
        ]

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for text message."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "Test"

        message.text = "Александр"
        message.reply_text = AsyncMock()

        update.message = message
        update.effective_user = user
        update.callback_query = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_with_rich_results(
        self, mock_update_message, mock_context, enhanced_sample_search_results
    ):
        """Test enhanced search processing with rich participant information."""
        # Mock the enhanced repository method (to be implemented)
        with (
            patch(
                "src.bot.handlers.search_handlers.get_participant_repository"
            ) as mock_repo_getter,
            patch.object(mock_update_message.message, "reply_text") as mock_reply,
        ):

            # Mock repository with enhanced search method
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = (
                enhanced_sample_search_results
            )
            mock_repo_getter.return_value = mock_repo

            result = await process_name_search_enhanced(
                mock_update_message, mock_context
            )

            # Should call enhanced search method
            mock_repo.search_by_name_enhanced.assert_called_once_with(
                "Александр", threshold=0.8, limit=5, user_role=None
            )

            # Should reply twice: results (inline) and navigation keyboard update
            assert mock_reply.await_count == 2
            first_call = mock_reply.await_args_list[0]
            second_call = mock_reply.await_args_list[1]

            message_text = first_call.kwargs["text"]
            assert "Найдено участников: 2" in message_text
            assert "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen" in message_text
            assert "Мария Петрова (Maria Petrova) - CANDIDATE, Worship" in message_text
            assert (
                "Высокое совпадение" in message_text
            )  # Match quality labels instead of percentages
            assert isinstance(first_call.kwargs["reply_markup"], InlineKeyboardMarkup)
            # Navigation keyboard update
            assert isinstance(second_call.kwargs["reply_markup"], ReplyKeyboardMarkup)

            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_language_detection(self, mock_context):
        """Test enhanced search with different language inputs."""
        # Test Russian input
        russian_update = Mock(spec=Update)
        russian_update.message = Mock()
        russian_update.message.text = "Александр"
        russian_update.message.reply_text = AsyncMock()
        russian_update.effective_user = Mock()
        russian_update.effective_user.id = 123

        # Test English input
        english_update = Mock(spec=Update)
        english_update.message = Mock()
        english_update.message.text = "Alexander"
        english_update.message.reply_text = AsyncMock()
        english_update.effective_user = Mock()
        english_update.effective_user.id = 124

        with patch(
            "src.bot.handlers.search_handlers.get_participant_repository"
        ) as mock_repo_getter:
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []
            mock_repo_getter.return_value = mock_repo

            # Test Russian input
            await process_name_search_enhanced(russian_update, mock_context)
            mock_repo.search_by_name_enhanced.assert_called_with(
                "Александр", threshold=0.8, limit=5, user_role=None
            )

            # Reset mock
            mock_repo.search_by_name_enhanced.reset_mock()

            # Test English input
            await process_name_search_enhanced(english_update, mock_context)
            mock_repo.search_by_name_enhanced.assert_called_with(
                "Alexander", threshold=0.8, limit=5, user_role=None
            )

    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_no_results(
        self, mock_update_message, mock_context
    ):
        """Test enhanced search with no results found."""
        with patch(
            "src.bot.handlers.search_handlers.get_participant_repository"
        ) as mock_repo_getter:

            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []
            mock_repo_getter.return_value = mock_repo

            result = await process_name_search_enhanced(
                mock_update_message, mock_context
            )

            # Should reply with no results message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args

            message_text = call_args[1]["text"]
            assert "Участники не найдены" in message_text

            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_error_handling(
        self, mock_update_message, mock_context
    ):
        """Test enhanced search error handling."""
        with patch(
            "src.bot.handlers.search_handlers.get_participant_repository"
        ) as mock_repo_getter:

            # Mock repository that raises error
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.side_effect = Exception(
                "Enhanced search error"
            )
            mock_repo_getter.return_value = mock_repo

            result = await process_name_search_enhanced(
                mock_update_message, mock_context
            )

            # Should reply with error message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args

            message_text = call_args[1]["text"]
            assert "Ошибка" in message_text
            assert "Попробуйте позже" in message_text

            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS

    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_partial_name_matching(
        self, mock_context
    ):
        """Test enhanced search with partial names (first/last name only)."""
        # Test first name search
        first_name_update = Mock(spec=Update)
        first_name_update.message = Mock()
        first_name_update.message.text = "Александр"  # First name only
        first_name_update.message.reply_text = AsyncMock()
        first_name_update.effective_user = Mock()
        first_name_update.effective_user.id = 123

        # Test last name search
        last_name_update = Mock(spec=Update)
        last_name_update.message = Mock()
        last_name_update.message.text = "Иванов"  # Last name only
        last_name_update.message.reply_text = AsyncMock()
        last_name_update.effective_user = Mock()
        last_name_update.effective_user.id = 124

        with patch(
            "src.bot.handlers.search_handlers.get_participant_repository"
        ) as mock_repo_getter:

            from src.models.participant import Department, Role

            enhanced_participant = Participant(
                full_name_ru="Александр Иванов",
                full_name_en="Alexander Ivanov",
                role=Role.TEAM,
                department=Department.KITCHEN,
            )

            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = [
                (
                    enhanced_participant,
                    0.92,
                    "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen",
                )
            ]
            mock_repo_getter.return_value = mock_repo

            # Test first name search
            result = await process_name_search_enhanced(first_name_update, mock_context)
            assert result == SearchStates.SHOWING_RESULTS
            mock_repo.search_by_name_enhanced.assert_called_with(
                "Александр", threshold=0.8, limit=5, user_role=None
            )

            # Reset and test last name search
            mock_repo.search_by_name_enhanced.reset_mock()
            result = await process_name_search_enhanced(last_name_update, mock_context)
            assert result == SearchStates.SHOWING_RESULTS
            mock_repo.search_by_name_enhanced.assert_called_with(
                "Иванов", threshold=0.8, limit=5, user_role=None
            )


class TestParticipantSelectionButtons:
    """Test participant selection button generation for interactive search results."""

    def test_create_participant_selection_keyboard_single_result(self):
        """Test button generation for single search result."""
        results = [
            SearchResult(
                participant=Participant(
                    full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
                ),
                similarity_score=0.95,
            )
        ]

        keyboard = create_participant_selection_keyboard(results)

        # Should have 1 button with participant name (no inline main menu)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1  # 1 button in first row

        participant_button = keyboard.inline_keyboard[0][0]
        assert participant_button.text == "Александр Иванов"
        assert participant_button.callback_data.startswith("select_participant:")

    def test_create_participant_selection_keyboard_multiple_results(self):
        """Test button generation for multiple search results (2-5)."""
        results = [
            SearchResult(
                participant=Participant(
                    full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
                ),
                similarity_score=0.95,
            ),
            SearchResult(
                participant=Participant(
                    full_name_ru="Александра Петрова", full_name_en="Alexandra Petrova"
                ),
                similarity_score=0.87,
            ),
            SearchResult(
                participant=Participant(
                    full_name_ru="Алексей Сидоров", full_name_en="Alexey Sidorov"
                ),
                similarity_score=0.82,
            ),
        ]

        keyboard = create_participant_selection_keyboard(results)

        # Should have 3 participant button rows (no inline main menu)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 3

        # Check participant buttons
        for i in range(3):
            participant_button = keyboard.inline_keyboard[i][0]
            assert participant_button.callback_data.startswith("select_participant:")

        # Check names are correct
        assert keyboard.inline_keyboard[0][0].text == "Александр Иванов"
        assert keyboard.inline_keyboard[1][0].text == "Александра Петрова"
        assert keyboard.inline_keyboard[2][0].text == "Алексей Сидоров"

    def test_create_participant_selection_keyboard_max_results(self):
        """Test button generation for maximum 5 results."""
        results = []
        for i in range(7):  # Create 7 results but should limit to 5
            results.append(
                SearchResult(
                    participant=Participant(
                        full_name_ru=f"Участник {i+1}",
                        full_name_en=f"Participant {i+1}",
                    ),
                    similarity_score=0.9 - i * 0.01,
                )
            )

        keyboard = create_participant_selection_keyboard(results)

        # Should limit to 5 participant button rows (no inline main menu)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 5

        # Check first 5 are participant buttons
        for i in range(5):
            participant_button = keyboard.inline_keyboard[i][0]
            assert participant_button.callback_data.startswith("select_participant:")
            assert f"Участник {i+1}" in participant_button.text

    def test_create_participant_selection_keyboard_callback_data_format(self):
        """Test callback data format for participant selection."""
        results = [
            SearchResult(
                participant=Participant(
                    full_name_ru="Мария Козлова",
                    full_name_en="Maria Kozlova",
                    record_id="test_id_123",
                ),
                similarity_score=0.89,
            )
        ]

        keyboard = create_participant_selection_keyboard(results)
        participant_button = keyboard.inline_keyboard[0][0]

        # Callback data should include participant identifier
        assert participant_button.callback_data == "select_participant:test_id_123"

    def test_create_participant_selection_keyboard_name_priority_russian(self):
        """Test that Russian names are prioritized for button labels."""
        results = [
            SearchResult(
                participant=Participant(
                    full_name_ru="Сергей Волков", full_name_en="Sergey Volkov"
                ),
                similarity_score=0.91,
            ),
            SearchResult(
                participant=Participant(
                    full_name_ru="John Smith"  # English name in Russian field (some data may be like this)
                ),
                similarity_score=0.88,
            ),
        ]

        keyboard = create_participant_selection_keyboard(results)

        # First button should show Russian name
        assert keyboard.inline_keyboard[0][0].text == "Сергей Волков"
        # Second button should show full_name_ru field content (always prioritized)
        assert keyboard.inline_keyboard[1][0].text == "John Smith"

    def test_create_participant_selection_keyboard_empty_results(self):
        """Test keyboard generation with empty results list."""
        results = []

        keyboard = create_participant_selection_keyboard(results)

        # Should have no rows when there are no results (navigation is via reply keyboard)
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 0


class TestUserInteractionLogging:
    """Test user interaction logging integration in search handlers."""

    @pytest.fixture
    def mock_callback_query_with_user_details(self):
        """Mock callback query with detailed user information."""
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 12345
        user.first_name = "John"
        user.last_name = "Doe"
        user.username = "johndoe"

        message.edit_text = AsyncMock()

        callback_query.from_user = user
        callback_query.data = "search"
        callback_query.message = message
        callback_query.answer = AsyncMock()

        update.callback_query = callback_query
        update.message = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {"search_results": []}
        return context

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @pytest.mark.asyncio
    async def test_search_button_logs_button_click(
        self, mock_get_logger, mock_callback_query_with_user_details, mock_context
    ):
        """Test that search button click is logged with user interaction logger."""
        # Setup mock logger instance
        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        # Execute search button handler
        await search_button(mock_callback_query_with_user_details, mock_context)

        # Verify logger was instantiated
        mock_get_logger.assert_called_once()

        # Verify button click was logged with correct parameters
        mock_logger_instance.log_button_click.assert_called_once_with(
            user_id=12345, button_data="search", username="johndoe"
        )

        # Verify bot response was logged
        mock_logger_instance.log_bot_response.assert_called_once()
        response_call = mock_logger_instance.log_bot_response.call_args

        assert response_call[1]["user_id"] == 12345
        assert response_call[1]["response_type"] == "edit_message"
        assert "Выберите тип поиска" in response_call[1]["content"]

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @pytest.mark.asyncio
    async def test_main_menu_button_logs_interaction(
        self, mock_get_logger, mock_callback_query_with_user_details, mock_context
    ):
        """Test that main menu button click is logged."""
        # Setup mock
        mock_callback_query_with_user_details.callback_query.data = "main_menu"
        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        # Execute handler
        await main_menu_button(mock_callback_query_with_user_details, mock_context)

        # Verify button click logging
        mock_logger_instance.log_button_click.assert_called_once_with(
            user_id=12345, button_data="main_menu", username="johndoe"
        )

        # Verify bot response logging
        mock_logger_instance.log_bot_response.assert_called_once()
        response_call = mock_logger_instance.log_bot_response.call_args
        assert response_call[1]["response_type"] == "edit_message"
        assert "Добро пожаловать" in response_call[1]["content"]

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    @pytest.mark.asyncio
    async def test_participant_selection_logs_interaction(
        self, mock_repo, mock_get_logger
    ):
        """Test that participant selection from search results is logged."""
        # Setup participant selection callback
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        user.id = 67890
        user.username = "testuser"
        message.edit_text = AsyncMock()

        callback_query.from_user = user
        callback_query.data = "select_participant:rec123456"
        callback_query.message = message
        callback_query.answer = AsyncMock()

        update.callback_query = callback_query

        # Mock search results in context
        mock_participant = Participant(
            record_id="rec123456", full_name_ru="Тест Участник"
        )
        context.user_data = {
            "search_results": [
                SearchResult(participant=mock_participant, similarity_score=0.9)
            ]
        }

        # Mock logger
        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        # Import handler and execute
        from src.bot.handlers.search_handlers import handle_participant_selection

        with patch(
            "src.bot.handlers.edit_participant_handlers.show_participant_edit_menu",
            new=AsyncMock(return_value=1),
        ):
            await handle_participant_selection(update, context)

        # Verify participant selection was logged
        mock_logger_instance.log_button_click.assert_called_once_with(
            user_id=67890,
            button_data="select_participant:rec123456",
            username="testuser",
        )

        # Verify journey step logging
        mock_logger_instance.log_journey_step.assert_called_once_with(
            user_id=67890,
            step="participant_selected",
            context={
                "participant_id": "rec123456",
                "participant_name": "Тест Участник",
            },
        )

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @pytest.mark.asyncio
    async def test_search_button_without_username_logs_correctly(self, mock_get_logger):
        """Test logging when user has no username."""
        # Setup user without username
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        user.id = 99999
        user.username = None  # No username
        message.edit_text = AsyncMock()

        callback_query.from_user = user
        callback_query.data = "search"
        callback_query.message = message
        callback_query.answer = AsyncMock()

        update.callback_query = callback_query
        context.user_data = {}

        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        # Execute handler
        await search_button(update, context)

        # Verify logging called with None username
        mock_logger_instance.log_button_click.assert_called_once_with(
            user_id=99999, button_data="search", username=None
        )

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    @pytest.mark.asyncio
    async def test_search_error_logs_missing_response(self, mock_repo, mock_get_logger):
        """Test that search errors are logged as missing responses."""
        # Setup search failure
        mock_repo_instance = Mock()
        mock_repo_instance.search_by_name_enhanced = AsyncMock(
            side_effect=Exception("Database error")
        )
        mock_repo_instance.list_all = AsyncMock(side_effect=Exception("Database error"))
        mock_repo.return_value = mock_repo_instance

        # Setup update and context for name search
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        user.id = 11111
        user.username = "erroruser"
        message.text = "John"
        message.reply_text = AsyncMock()

        update.message = message
        update.effective_user = user

        context.user_data = {"last_button_click": "search"}

        mock_logger_instance = Mock()
        mock_get_logger.return_value = mock_logger_instance

        # Execute handler
        await process_name_search(update, context)

        # Verify error was logged as missing response
        mock_logger_instance.log_missing_response.assert_called_once_with(
            user_id=11111,
            button_data="search",
            error_type="handler_error",
            error_message="Error during search for user 11111: Database error",
        )

    @patch("src.bot.handlers.search_handlers.get_user_interaction_logger")
    @pytest.mark.asyncio
    async def test_logging_disabled_by_configuration(self, mock_get_logger):
        """Test that logging is disabled when configuration is set to false."""
        # Simulate disabled logging by returning None
        mock_get_logger.return_value = None

        # Setup callback
        update = Mock(spec=Update)
        callback_query = Mock(spec=CallbackQuery)
        user = Mock(spec=User)
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)

        user.id = 12345
        user.username = "testuser"
        callback_query.from_user = user
        callback_query.data = "search"
        callback_query.answer = AsyncMock()
        callback_query.message = Mock()
        callback_query.message.edit_text = AsyncMock()
        # Our handler also sends a follow-up message to set reply keyboard
        callback_query.message.reply_text = AsyncMock()

        update.callback_query = callback_query
        context.user_data = {}

        # Execute handler
        await search_button(update, context)

        # Provider is consulted but no logger is used
        mock_get_logger.assert_called_once()


class TestSearchModeSelection:
    """Test search mode selection handlers."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for message."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)
        chat = Mock(spec=Chat)

        user.id = 12345
        user.first_name = "TestUser"
        message.from_user = user
        message.chat = chat
        message.reply_text = AsyncMock()

        update.message = message
        update.effective_user = user
        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_handle_search_name_mode(self, mock_update_message, mock_context):
        """Test name search mode selection handler."""
        # Execute handler
        result = await handle_search_name_mode(mock_update_message, mock_context)

        # Verify correct state returned
        assert result == SearchStates.WAITING_FOR_NAME

        # Verify message sent
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args
        assert "Введите имя участника:" in call_args[1]["text"]
        assert isinstance(call_args[1]["reply_markup"], ReplyKeyboardMarkup)

    @pytest.mark.asyncio
    async def test_handle_search_room_mode(self, mock_update_message, mock_context):
        """Test room search mode selection handler."""
        # Execute handler
        result = await handle_search_room_mode(mock_update_message, mock_context)

        # Should prompt for room number and return waiting state
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "Введите номер комнаты" in call_args["text"]
        assert result == 20  # RoomSearchStates.WAITING_FOR_ROOM

    @pytest.mark.asyncio
    async def test_handle_search_floor_mode(self, mock_update_message, mock_context):
        """Test floor search mode selection handler."""
        # Execute handler
        result = await handle_search_floor_mode(mock_update_message, mock_context)

        # Should prompt for floor number and return waiting state
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args[1]
        assert "номер этажа" in call_args["text"].lower()
        assert result == FloorSearchStates.WAITING_FOR_FLOOR

    @pytest.mark.asyncio
    async def test_back_to_search_modes(self, mock_update_message, mock_context):
        """Test back to search modes handler."""
        # Execute handler
        result = await back_to_search_modes(mock_update_message, mock_context)

        # Verify correct state returned
        assert result == SearchStates.SEARCH_MODE_SELECTION

        # Verify message sent
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args
        assert "Выберите тип поиска:" in call_args[1]["text"]
        assert isinstance(call_args[1]["reply_markup"], ReplyKeyboardMarkup)


class TestSearchKeyboards:
    """Test search keyboard functionality."""

    def test_search_keyboards_import(self):
        """Test that search keyboards can be imported."""
        from src.bot.keyboards.search_keyboards import (
            NAV_BACK_TO_SEARCH_MODES,
            NAV_CANCEL,
            NAV_MAIN_MENU,
            NAV_SEARCH_FLOOR,
            NAV_SEARCH_NAME,
            NAV_SEARCH_ROOM,
            get_main_menu_keyboard,
            get_results_navigation_keyboard,
            get_search_mode_selection_keyboard,
            get_waiting_for_floor_keyboard,
            get_waiting_for_name_keyboard,
            get_waiting_for_room_keyboard,
        )

        # Test constants exist
        assert NAV_SEARCH_NAME == "👤 По имени"
        assert NAV_SEARCH_ROOM == "🚪 По комнате"
        assert NAV_SEARCH_FLOOR == "🏢 По этажу"
        assert NAV_MAIN_MENU == "🏠 Главное меню"
        assert NAV_CANCEL == "❌ Отмена"
        assert NAV_BACK_TO_SEARCH_MODES == "🔙 Назад к поиску"

    def test_search_mode_selection_keyboard(self):
        """Test search mode selection keyboard structure."""
        from src.bot.keyboards.search_keyboards import (
            get_search_mode_selection_keyboard,
        )

        keyboard = get_search_mode_selection_keyboard()
        assert isinstance(keyboard, ReplyKeyboardMarkup)

        # Verify keyboard has expected structure
        # keyboard.keyboard contains KeyboardButton objects, not strings
        assert len(keyboard.keyboard) == 2
        assert len(keyboard.keyboard[0]) == 2
        assert len(keyboard.keyboard[1]) == 2
        assert keyboard.keyboard[0][0].text == "👤 По имени"
        assert keyboard.keyboard[0][1].text == "🚪 По комнате"
        assert keyboard.keyboard[1][0].text == "🏢 По этажу"
        assert keyboard.keyboard[1][1].text == "🏠 Главное меню"

        # Verify keyboard properties
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is False


class TestSharedInitializationHelpers:
    """Test shared initialization helper functions for start_command and main_menu_button equivalence."""

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    def test_initialize_main_menu_session(self, mock_context):
        """Test that initialize_main_menu_session properly sets user_data."""
        # Execute initialization
        initialize_main_menu_session(mock_context)

        # Verify user_data is properly initialized
        assert "search_results" in mock_context.user_data
        assert mock_context.user_data["search_results"] == []
        assert "force_direct_name_input" in mock_context.user_data
        assert mock_context.user_data["force_direct_name_input"] is True

    def test_initialize_main_menu_session_preserves_other_data(self, mock_context):
        """Test that initialize_main_menu_session preserves existing user_data."""
        # Add some existing data
        mock_context.user_data["existing_key"] = "existing_value"
        mock_context.user_data["current_participant"] = "some_participant"

        # Execute initialization
        initialize_main_menu_session(mock_context)

        # Verify existing data is preserved
        assert mock_context.user_data["existing_key"] == "existing_value"
        assert mock_context.user_data["current_participant"] == "some_participant"

        # Verify new data is set
        assert mock_context.user_data["search_results"] == []
        assert mock_context.user_data["force_direct_name_input"] is True

    def test_get_welcome_message(self):
        """Test that get_welcome_message returns unified Russian welcome text."""
        message = get_welcome_message()

        # Should contain key Russian phrases
        assert "Добро пожаловать" in message
        assert "Tres Dias" in message
        assert "🙏" in message
        assert "участников" in message

        # Should be a string
        assert isinstance(message, str)
        assert len(message.strip()) > 0

    def test_get_welcome_message_consistency(self):
        """Test that get_welcome_message returns consistent text across multiple calls."""
        message1 = get_welcome_message()
        message2 = get_welcome_message()

        # Should return identical text every time
        assert message1 == message2


class TestStartCommandMainMenuButtonEquivalence:
    """Test equivalence between start_command and main_menu_button functionality."""

    @pytest.fixture
    def mock_update_message(self):
        """Mock Update object for start_command (message)."""
        update = Mock(spec=Update)
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "TestUser"

        message.from_user = user
        message.reply_text = AsyncMock()

        update.message = message
        update.effective_user = user

        return update

    @pytest.fixture
    def mock_update_callback(self):
        """Mock Update object for main_menu_button (callback query)."""
        update = Mock(spec=Update)
        callback_query = Mock()
        message = Mock(spec=Message)
        user = Mock(spec=User)

        user.id = 123456
        user.first_name = "TestUser"
        user.username = "testuser"

        callback_query.from_user = user
        callback_query.data = "main_menu"
        callback_query.answer = AsyncMock()
        callback_query.message = message

        message.edit_text = AsyncMock()
        message.reply_text = AsyncMock()

        update.callback_query = callback_query
        update.effective_user = user
        update.message = None

        return update

    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        return context

    @pytest.mark.asyncio
    async def test_start_command_and_main_menu_button_equivalent_initialization(
        self, mock_update_message, mock_update_callback, mock_context
    ):
        """Test that both handlers initialize user_data identically."""
        # Test start_command initialization
        context1 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context1.user_data = {}
        await start_command(mock_update_message, context1)

        # Test main_menu_button initialization
        context2 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context2.user_data = {}
        await main_menu_button(mock_update_callback, context2)

        # Both should have identical user_data initialization
        assert (
            context1.user_data["search_results"]
            == context2.user_data["search_results"]
            == []
        )
        assert (
            context1.user_data["force_direct_name_input"]
            == context2.user_data["force_direct_name_input"]
            == True
        )

    @pytest.mark.asyncio
    async def test_start_command_and_main_menu_button_equivalent_welcome_message(
        self, mock_update_message, mock_update_callback, mock_context
    ):
        """Test that both handlers use identical welcome message."""
        # Test start_command welcome message
        context1 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context1.user_data = {}
        await start_command(mock_update_message, context1)

        start_call_args = mock_update_message.message.reply_text.call_args
        start_welcome_message = start_call_args[1]["text"]

        # Test main_menu_button welcome message
        context2 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context2.user_data = {}
        await main_menu_button(mock_update_callback, context2)

        main_menu_edit_args = (
            mock_update_callback.callback_query.message.edit_text.call_args
        )
        main_menu_welcome_message = main_menu_edit_args[1]["text"]

        # Both should use identical welcome message
        assert start_welcome_message == main_menu_welcome_message
        assert "Добро пожаловать в бот Tres Dias! 🙏" in start_welcome_message
        assert "Выберите тип поиска участников" in start_welcome_message

    @pytest.mark.asyncio
    async def test_start_command_and_main_menu_button_equivalent_return_state(
        self, mock_update_message, mock_update_callback, mock_context
    ):
        """Test that both handlers return identical conversation state."""
        # Test start_command return state
        context1 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context1.user_data = {}
        result1 = await start_command(mock_update_message, context1)

        # Test main_menu_button return state
        context2 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context2.user_data = {}
        result2 = await main_menu_button(mock_update_callback, context2)

        # Both should return identical conversation state
        assert result1 == result2 == SearchStates.MAIN_MENU

    @pytest.mark.asyncio
    async def test_start_command_and_main_menu_button_keyboard_equivalence(
        self, mock_update_message, mock_update_callback, mock_context
    ):
        """Test that both handlers provide equivalent keyboard functionality."""
        # Test start_command keyboard
        context1 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context1.user_data = {}
        await start_command(mock_update_message, context1)

        start_call_args = mock_update_message.message.reply_text.call_args
        start_keyboard = start_call_args[1]["reply_markup"]

        # Test main_menu_button keyboard (from the reply_text call)
        context2 = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context2.user_data = {}
        await main_menu_button(mock_update_callback, context2)

        main_menu_reply_args = (
            mock_update_callback.callback_query.message.reply_text.call_args
        )
        main_menu_keyboard = main_menu_reply_args[1]["reply_markup"]

        # Both should provide ReplyKeyboardMarkup
        assert isinstance(start_keyboard, ReplyKeyboardMarkup)
        assert isinstance(main_menu_keyboard, ReplyKeyboardMarkup)

        # Both should have the same keyboard structure
        assert len(start_keyboard.keyboard) == len(main_menu_keyboard.keyboard)
        assert start_keyboard.resize_keyboard == main_menu_keyboard.resize_keyboard
