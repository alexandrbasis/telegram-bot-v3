"""
Unit tests for search bot handlers and conversation flow.

Tests bot handler functions for name search functionality with ConversationHandler
state management and Russian interface.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Update, CallbackQuery, Message, User, Chat, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.bot.handlers.search_handlers import (
    start_command,
    search_button,
    process_name_search,
    main_menu_button,
    process_name_search_enhanced,
    create_participant_selection_keyboard,
    SearchStates
)
from src.services.search_service import SearchResult
from src.models.participant import Participant


class TestSearchStates:
    """Test conversation states enum."""
    
    def test_search_states_values(self):
        """Test that search states have correct integer values."""
        assert SearchStates.MAIN_MENU == 0
        assert SearchStates.WAITING_FOR_NAME == 1
        assert SearchStates.SHOWING_RESULTS == 2


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
    async def test_start_command_russian_greeting(self, mock_update_message, mock_context):
        """Test /start command sends Russian greeting with search button."""
        result = await start_command(mock_update_message, mock_context)
        
        # Should send Russian welcome message
        mock_update_message.message.reply_text.assert_called_once()
        call_args = mock_update_message.message.reply_text.call_args
        
        # Check Russian text in message
        message_text = call_args[1]['text']
        assert "Добро пожаловать" in message_text
        assert "Tres Dias" in message_text
        assert "участников" in message_text
        
        # Should include search button keyboard
        assert 'reply_markup' in call_args[1]
        keyboard = call_args[1]['reply_markup']
        assert isinstance(keyboard, InlineKeyboardMarkup)
        
        # Should return MAIN_MENU state
        assert result == SearchStates.MAIN_MENU
    
    @pytest.mark.asyncio
    async def test_start_command_user_data_initialization(self, mock_update_message, mock_context):
        """Test that /start command initializes user data."""
        await start_command(mock_update_message, mock_context)
        
        # Should initialize user_data
        assert 'search_results' in mock_context.user_data
        assert mock_context.user_data['search_results'] == []


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
        context.user_data = {'search_results': []}
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
        
        # Should contain Russian search prompt
        message_text = call_args[1]['text']
        assert "Введите имя" in message_text
        
        # Should return WAITING_FOR_NAME state
        assert result == SearchStates.WAITING_FOR_NAME


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
        context.user_data = {'search_results': []}
        return context
    
    @pytest.fixture
    def sample_search_results(self):
        """Sample search results for testing."""
        participant1 = Participant(full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov")
        participant2 = Participant(full_name_ru="Александра Петрова", full_name_en="Alexandra Petrova")
        
        return [
            SearchResult(participant=participant1, similarity_score=0.95),
            SearchResult(participant=participant2, similarity_score=0.85),
        ]
    
    @pytest.mark.asyncio
    async def test_process_name_search_with_results(self, mock_update_message, mock_context, sample_search_results):
        """Test name search processing with found results."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter, \
             patch('src.bot.handlers.search_handlers.SearchService') as mock_search_service:
            
            # Mock repository
            mock_repo = AsyncMock()
            mock_repo.list_all.return_value = [
                Participant(full_name_ru="Александр Иванов"),
                Participant(full_name_ru="Мария Сидорова"),
            ]
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError("Enhanced search not available")
            mock_repo_getter.return_value = mock_repo
            
            # Mock search service
            mock_service_instance = Mock()
            mock_service_instance.search_participants.return_value = sample_search_results
            mock_search_service.return_value = mock_service_instance
            
            result = await process_name_search(mock_update_message, mock_context)
            
            # Should call repository to get participants
            mock_repo.list_all.assert_called_once()
            
            # Should call search service with query
            mock_service_instance.search_participants.assert_called_once_with(
                "Александр Иванов", mock_repo.list_all.return_value
            )
            
            # Should reply with results
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args
            
            # Should contain Russian results text
            message_text = call_args[1]['text']
            assert "Найдено участников" in message_text
            assert "Александр Иванов" in message_text
            assert "Александра Петрова" in message_text
            
            # Should include main menu button
            assert 'reply_markup' in call_args[1]
            
            # Should store results in user_data
            assert mock_context.user_data['search_results'] == sample_search_results
            
            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS
    
    @pytest.mark.asyncio
    async def test_process_name_search_no_results(self, mock_update_message, mock_context):
        """Test name search processing with no results found."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter, \
             patch('src.bot.handlers.search_handlers.SearchService') as mock_search_service:
            
            # Mock repository
            mock_repo = AsyncMock()
            mock_repo.list_all.return_value = [Participant(full_name_ru="Мария Сидорова")]
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError("Enhanced search not available")
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
            message_text = call_args[1]['text']
            assert "Участники не найдены" in message_text
            
            # Should include main menu button
            assert 'reply_markup' in call_args[1]
            
            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS
    
    @pytest.mark.asyncio
    async def test_process_name_search_repository_error(self, mock_update_message, mock_context):
        """Test name search processing when repository fails."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter:
            
            # Mock repository that raises error
            mock_repo = AsyncMock()
            mock_repo.list_all.side_effect = Exception("Database error")
            # Mock enhanced search to not exist (triggers fallback)
            mock_repo.search_by_name_enhanced.side_effect = AttributeError("Enhanced search not available")
            mock_repo_getter.return_value = mock_repo
            
            result = await process_name_search(mock_update_message, mock_context)
            
            # Should reply with error message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args
            
            # Should contain Russian error text
            message_text = call_args[1]['text']
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
        context.user_data = {
            'search_results': [Mock()]  # Some previous results
        }
        return context
    
    @pytest.mark.asyncio
    async def test_main_menu_button_handler(self, mock_callback_query, mock_context):
        """Test main menu button click handler."""
        result = await main_menu_button(mock_callback_query, mock_context)
        
        # Should answer callback query
        mock_callback_query.callback_query.answer.assert_called_once()
        
        # Should edit message back to main menu
        mock_callback_query.callback_query.message.edit_text.assert_called_once()
        call_args = mock_callback_query.callback_query.message.edit_text.call_args
        
        # Should contain Russian welcome message
        message_text = call_args[1]['text']
        assert "Добро пожаловать" in message_text
        assert "участников" in message_text
        
        # Should include search button keyboard
        assert 'reply_markup' in call_args[1]
        
        # Should clear search results
        assert mock_context.user_data['search_results'] == []
        
        # Should return MAIN_MENU state
        assert result == SearchStates.MAIN_MENU


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
        with patch('src.bot.handlers.search_handlers.get_main_menu_keyboard'), \
             patch('src.bot.handlers.search_handlers.get_search_button_keyboard'):
            
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
            mock_update.message = None
            
            search_button_result = await search_button(mock_update, mock_context)
            assert search_button_result == SearchStates.WAITING_FOR_NAME


class TestEnhancedSearchHandlers:
    """Test enhanced search functionality with rich results."""
    
    @pytest.fixture
    def enhanced_sample_search_results(self):
        """Enhanced sample search results with rich formatting."""
        from src.models.participant import Role, Department
        
        participants = [
            Participant(
                full_name_ru="Александр Иванов",
                full_name_en="Alexander Ivanov", 
                role=Role.TEAM,
                department=Department.KITCHEN
            ),
            Participant(
                full_name_ru="Мария Петрова",
                full_name_en="Maria Petrova",
                role=Role.CANDIDATE, 
                department=Department.WORSHIP
            )
        ]
        
        return [
            (participants[0], 0.95, "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen"),
            (participants[1], 0.87, "Мария Петрова (Maria Petrova) - CANDIDATE, Worship")
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
    async def test_process_name_search_enhanced_with_rich_results(self, mock_update_message, mock_context, enhanced_sample_search_results):
        """Test enhanced search processing with rich participant information."""
        # Mock the enhanced repository method (to be implemented)
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter, \
             patch.object(mock_update_message.message, 'reply_text') as mock_reply:
            
            # Mock repository with enhanced search method
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = enhanced_sample_search_results
            mock_repo_getter.return_value = mock_repo
            
            result = await process_name_search_enhanced(mock_update_message, mock_context)
            
            # Should call enhanced search method
            mock_repo.search_by_name_enhanced.assert_called_once_with("Александр", threshold=0.8, limit=5)
            
            # Should reply with rich formatted results
            mock_reply.assert_called_once()
            call_args = mock_reply.call_args
            
            message_text = call_args[1]['text']
            assert "Найдено участников: 2" in message_text
            assert "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen" in message_text
            assert "Мария Петрова (Maria Petrova) - CANDIDATE, Worship" in message_text
            assert "95%" in message_text  # Similarity score
            assert "87%" in message_text
            
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
        
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter:
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []
            mock_repo_getter.return_value = mock_repo
            
            # Test Russian input
            await process_name_search_enhanced(russian_update, mock_context)
            mock_repo.search_by_name_enhanced.assert_called_with("Александр", threshold=0.8, limit=5)
            
            # Reset mock
            mock_repo.search_by_name_enhanced.reset_mock()
            
            # Test English input
            await process_name_search_enhanced(english_update, mock_context)
            mock_repo.search_by_name_enhanced.assert_called_with("Alexander", threshold=0.8, limit=5)
    
    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_no_results(self, mock_update_message, mock_context):
        """Test enhanced search with no results found."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter:
            
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = []
            mock_repo_getter.return_value = mock_repo
            
            result = await process_name_search_enhanced(mock_update_message, mock_context)
            
            # Should reply with no results message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args
            
            message_text = call_args[1]['text']
            assert "Участники не найдены" in message_text
            
            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS
    
    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_error_handling(self, mock_update_message, mock_context):
        """Test enhanced search error handling."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter:
            
            # Mock repository that raises error
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.side_effect = Exception("Enhanced search error")
            mock_repo_getter.return_value = mock_repo
            
            result = await process_name_search_enhanced(mock_update_message, mock_context)
            
            # Should reply with error message
            mock_update_message.message.reply_text.assert_called_once()
            call_args = mock_update_message.message.reply_text.call_args
            
            message_text = call_args[1]['text']
            assert "Ошибка" in message_text
            assert "Попробуйте позже" in message_text
            
            # Should return SHOWING_RESULTS state
            assert result == SearchStates.SHOWING_RESULTS
    
    @pytest.mark.asyncio
    async def test_process_name_search_enhanced_partial_name_matching(self, mock_context):
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
        
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter:
            
            from src.models.participant import Role, Department
            enhanced_participant = Participant(
                full_name_ru="Александр Иванов",
                full_name_en="Alexander Ivanov",
                role=Role.TEAM,
                department=Department.KITCHEN
            )
            
            mock_repo = AsyncMock()
            mock_repo.search_by_name_enhanced.return_value = [
                (enhanced_participant, 0.92, "Александр Иванов (Alexander Ivanov) - TEAM, Kitchen")
            ]
            mock_repo_getter.return_value = mock_repo
            
            # Test first name search
            result = await process_name_search_enhanced(first_name_update, mock_context)
            assert result == SearchStates.SHOWING_RESULTS
            mock_repo.search_by_name_enhanced.assert_called_with("Александр", threshold=0.8, limit=5)
            
            # Reset and test last name search
            mock_repo.search_by_name_enhanced.reset_mock()
            result = await process_name_search_enhanced(last_name_update, mock_context)
            assert result == SearchStates.SHOWING_RESULTS
            mock_repo.search_by_name_enhanced.assert_called_with("Иванов", threshold=0.8, limit=5)


class TestParticipantSelectionButtons:
    """Test participant selection button generation for interactive search results."""
    
    def test_create_participant_selection_keyboard_single_result(self):
        """Test button generation for single search result."""
        results = [
            SearchResult(
                participant=Participant(full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"),
                similarity_score=0.95
            )
        ]
        
        keyboard = create_participant_selection_keyboard(results)
        
        # Should have 1 button with participant name
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 2  # 1 participant button + 1 main menu button
        assert len(keyboard.inline_keyboard[0]) == 1  # 1 button in first row
        
        participant_button = keyboard.inline_keyboard[0][0]
        assert participant_button.text == "Александр Иванов"
        assert participant_button.callback_data.startswith("select_participant:")
        
    def test_create_participant_selection_keyboard_multiple_results(self):
        """Test button generation for multiple search results (2-5)."""
        results = [
            SearchResult(
                participant=Participant(full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"),
                similarity_score=0.95
            ),
            SearchResult(
                participant=Participant(full_name_ru="Александра Петрова", full_name_en="Alexandra Petrova"),
                similarity_score=0.87
            ),
            SearchResult(
                participant=Participant(full_name_ru="Алексей Сидоров", full_name_en="Alexey Sidorov"),
                similarity_score=0.82
            )
        ]
        
        keyboard = create_participant_selection_keyboard(results)
        
        # Should have 3 participant buttons + 1 main menu button = 4 rows
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 4
        
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
            results.append(SearchResult(
                participant=Participant(full_name_ru=f"Участник {i+1}", full_name_en=f"Participant {i+1}"),
                similarity_score=0.9 - i * 0.01
            ))
            
        keyboard = create_participant_selection_keyboard(results)
        
        # Should limit to 5 participant buttons + 1 main menu = 6 rows
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 6
        
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
                    record_id="test_id_123"
                ),
                similarity_score=0.89
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
                    full_name_ru="Сергей Волков",
                    full_name_en="Sergey Volkov"
                ),
                similarity_score=0.91
            ),
            SearchResult(
                participant=Participant(
                    full_name_ru="John Smith"  # English name in Russian field (some data may be like this)
                ),
                similarity_score=0.88
            )
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
        
        # Should only have main menu button
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert keyboard.inline_keyboard[0][0].text == "🏠 Главное меню"
        assert keyboard.inline_keyboard[0][0].callback_data == "main_menu"


