"""
Regression tests for participant search button functionality.

Tests the root cause fix for ConversationHandler per_message configuration
that was preventing search button from responding to clicks.
"""

import pytest
from unittest.mock import Mock
from telegram.ext import ConversationHandler

from src.bot.handlers.search_conversation import get_search_conversation_handler


class TestSearchButtonRegression:
    """Regression tests for search button configuration issues."""
    
    def test_conversation_handler_per_message_tracking_enabled(self):
        """
        Test that ConversationHandler has proper per_message tracking enabled.
        
        This test addresses the root cause where per_message=False was preventing
        CallbackQueryHandlers from being properly tracked, causing the search
        button to not respond to clicks.
        
        Expected behavior: per_message should be True (default) or explicitly set to True
        """
        handler = get_search_conversation_handler()
        
        # Verify it's a ConversationHandler
        assert isinstance(handler, ConversationHandler)
        
        # Check if per_message is properly configured for callback tracking
        # per_message should be True (default) or not explicitly set to False
        # This is the critical fix for the button not responding issue
        
        # Access per_message attribute directly - ConversationHandler stores it as _per_message
        per_message_value = getattr(handler, '_per_message', True)  # Default is True
        
        # per_message should not be False to allow CallbackQueryHandler tracking  
        # For mixed handler types, per_message=None allows auto-detection
        assert per_message_value is not False, \
            f"per_message={per_message_value} prevents CallbackQueryHandler tracking - this breaks the search button"
        
        # Additional verification: the handler should have the search button callback handler
        states = getattr(handler, 'states', {})
        
        # Import SearchStates to get the correct enum value
        from src.bot.handlers.search_handlers import SearchStates
        main_menu_handlers = states.get(SearchStates.MAIN_MENU, [])
        
        # Verify search button handler exists in MAIN_MENU state
        callback_handlers = [h for h in main_menu_handlers if hasattr(h, 'pattern') and h.pattern is not None]
        search_handlers = [h for h in callback_handlers if str(h.pattern.pattern) == '^search$']
        
        assert len(search_handlers) >= 1, f"Search button callback handler should be configured. Found handlers: {[str(h.pattern.pattern) if hasattr(h, 'pattern') else 'no pattern' for h in main_menu_handlers]}"
        
    def test_search_button_handler_pattern_matches_button_data(self):
        """
        Test that search button callback pattern matches button callback_data.
        
        Verifies the button callback_data="search" matches handler pattern="^search$"
        """
        handler = get_search_conversation_handler()
        
        # Get MAIN_MENU state handlers
        from src.bot.handlers.search_handlers import SearchStates
        states = getattr(handler, 'states', {})
        main_menu_handlers = states.get(SearchStates.MAIN_MENU, [])
        
        # Find the search button handler
        search_handler = None
        for h in main_menu_handlers:
            if hasattr(h, 'pattern') and h.pattern is not None and str(h.pattern.pattern) == '^search$':
                search_handler = h
                break
                
        assert search_handler is not None, f"Search button handler with pattern '^search$' should exist. Available handlers: {[str(h.pattern.pattern) if hasattr(h, 'pattern') and h.pattern else 'no pattern' for h in main_menu_handlers]}"
        
        # Test that the pattern matches the expected callback_data
        import re
        pattern = search_handler.pattern
        assert pattern.match("search"), "Handler pattern should match button callback_data 'search'"
        assert not pattern.match("search_extra"), "Handler pattern should be exact match"
        assert not pattern.match("presearch"), "Handler pattern should be exact match"