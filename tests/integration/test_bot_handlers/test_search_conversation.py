"""
Integration tests for search conversation handler.

Tests the complete ConversationHandler integration with entry points, 
states, and fallbacks for the Russian name search feature.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from telegram.ext import ConversationHandler, CommandHandler, CallbackQueryHandler, MessageHandler, filters

from src.bot.handlers.search_conversation import get_search_conversation_handler
from src.bot.handlers.search_handlers import SearchStates


class TestSearchConversationHandler:
    """Test search conversation handler configuration."""
    
    def test_get_search_conversation_handler_returns_conversation_handler(self):
        """Test that get_search_conversation_handler returns ConversationHandler instance."""
        handler = get_search_conversation_handler()
        
        assert isinstance(handler, ConversationHandler)
    
    def test_conversation_handler_has_entry_points(self):
        """Test that conversation handler has proper entry points."""
        handler = get_search_conversation_handler()
        
        # Should have /start command as entry point
        assert len(handler.entry_points) >= 1
        
        # Entry point should be CommandHandler for "start"
        start_handler = handler.entry_points[0]
        assert isinstance(start_handler, CommandHandler)
        assert "start" in start_handler.commands
    
    def test_conversation_handler_has_states(self):
        """Test that conversation handler has all required states."""
        handler = get_search_conversation_handler()
        
        # Should have states for MAIN_MENU, WAITING_FOR_NAME, SHOWING_RESULTS
        states = handler.states
        assert SearchStates.MAIN_MENU in states
        assert SearchStates.WAITING_FOR_NAME in states
        assert SearchStates.SHOWING_RESULTS in states
    
    def test_main_menu_state_handlers(self):
        """Test MAIN_MENU state has callback query handlers."""
        handler = get_search_conversation_handler()
        
        main_menu_handlers = handler.states[SearchStates.MAIN_MENU]
        
        # Should have callback query handler for search button
        assert any(isinstance(h, CallbackQueryHandler) for h in main_menu_handlers)
    
    def test_waiting_for_name_state_handlers(self):
        """Test WAITING_FOR_NAME state has message handlers."""
        handler = get_search_conversation_handler()
        
        waiting_handlers = handler.states[SearchStates.WAITING_FOR_NAME]
        
        # Should have message handler for text input
        assert any(isinstance(h, MessageHandler) for h in waiting_handlers)
    
    def test_showing_results_state_handlers(self):
        """Test SHOWING_RESULTS state has callback query handlers."""
        handler = get_search_conversation_handler()
        
        results_handlers = handler.states[SearchStates.SHOWING_RESULTS]
        
        # Should have callback query handler for main menu button
        assert any(isinstance(h, CallbackQueryHandler) for h in results_handlers)
    
    def test_conversation_handler_has_fallbacks(self):
        """Test that conversation handler has fallback handlers."""
        handler = get_search_conversation_handler()
        
        # Should have fallback handlers (like /start to restart conversation)
        assert len(handler.fallbacks) >= 1
        
        # Fallback should include start command
        fallback_handler = handler.fallbacks[0]
        assert isinstance(fallback_handler, CommandHandler)
        assert "start" in fallback_handler.commands


@pytest.mark.asyncio
class TestSearchConversationFlow:
    """Test the complete conversation flow integration."""
    
    @pytest.fixture
    def mock_update_message(self):
        """Mock Update for message-based interactions."""
        update = Mock()
        message = Mock()
        user = Mock()
        
        user.id = 123456
        user.first_name = "Test"
        
        message.from_user = user
        message.reply_text = AsyncMock()
        
        update.message = message
        update.callback_query = None
        update.effective_user = user
        
        return update
    
    @pytest.fixture
    def mock_update_callback(self):
        """Mock Update for callback query interactions."""
        update = Mock()
        callback_query = Mock()
        message = Mock()
        user = Mock()
        
        user.id = 123456
        user.first_name = "Test"
        
        message.edit_text = AsyncMock()
        
        callback_query.from_user = user
        callback_query.message = message
        callback_query.answer = AsyncMock()
        
        update.callback_query = callback_query
        update.message = None
        update.effective_user = user
        
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Mock context object."""
        context = Mock()
        context.user_data = {}
        return context
    
    async def test_conversation_start_to_search_flow(self, mock_update_message, mock_update_callback, mock_context):
        """Test complete flow from /start to search button to name input."""
        from src.bot.handlers.search_handlers import start_command, search_button
        
        # Step 1: /start command
        result = await start_command(mock_update_message, mock_context)
        assert result == SearchStates.MAIN_MENU
        assert 'search_results' in mock_context.user_data
        
        # Step 2: Search button click
        mock_update_callback.callback_query.data = "search"
        result = await search_button(mock_update_callback, mock_context)
        assert result == SearchStates.WAITING_FOR_NAME
        
        mock_update_callback.callback_query.answer.assert_called_once()
        mock_update_callback.callback_query.message.edit_text.assert_called_once()
    
    async def test_conversation_search_to_results_flow(self, mock_update_message, mock_context):
        """Test flow from name input to search results."""
        with patch('src.bot.handlers.search_handlers.get_participant_repository') as mock_repo_getter, \
             patch('src.bot.handlers.search_handlers.SearchService') as mock_search_service:
            
            from src.bot.handlers.search_handlers import process_name_search
            from src.models.participant import Participant
            from src.services.search_service import SearchResult
            
            # Mock dependencies
            mock_repo = AsyncMock()
            test_participant = Participant(full_name_ru="Test User")
            
            # Mock the enhanced search method that is called first
            mock_repo.search_by_name_enhanced.return_value = [
                (test_participant, 0.9, "Test User")  # (participant, score, formatted_result)
            ]
            mock_repo.list_all.return_value = [test_participant]
            mock_repo_getter.return_value = mock_repo
            
            mock_service = Mock()
            mock_service.search_participants.return_value = [
                SearchResult(participant=Participant(full_name_ru="Test User"), similarity_score=0.9)
            ]
            mock_search_service.return_value = mock_service
            
            # Set up search query
            mock_update_message.message.text = "Test"
            mock_context.user_data = {'search_results': []}
            
            # Process search
            result = await process_name_search(mock_update_message, mock_context)
            
            assert result == SearchStates.SHOWING_RESULTS
            assert len(mock_context.user_data['search_results']) > 0
            mock_update_message.message.reply_text.assert_called_once()
    
    async def test_conversation_results_to_main_menu_flow(self, mock_update_callback, mock_context):
        """Test flow from search results back to main menu."""
        from src.bot.handlers.search_handlers import main_menu_button
        
        # Set up context with search results
        mock_context.user_data = {'search_results': [Mock()]}  # Some results
        mock_update_callback.callback_query.data = "main_menu"
        
        # Return to main menu
        result = await main_menu_button(mock_update_callback, mock_context)
        
        assert result == SearchStates.MAIN_MENU
        assert mock_context.user_data['search_results'] == []
        
        mock_update_callback.callback_query.answer.assert_called_once()
        mock_update_callback.callback_query.message.edit_text.assert_called_once()


class TestConversationHandlerImport:
    """Test that conversation handler can be imported and used."""
    
    def test_import_conversation_handler(self):
        """Test that conversation handler can be imported without errors."""
        from src.bot.handlers.search_conversation import get_search_conversation_handler
        
        # Should be able to import and call without errors
        handler = get_search_conversation_handler()
        assert handler is not None