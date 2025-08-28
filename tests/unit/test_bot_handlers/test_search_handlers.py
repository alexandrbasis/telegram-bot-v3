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