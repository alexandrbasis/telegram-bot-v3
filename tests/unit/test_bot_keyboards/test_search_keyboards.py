"""
Tests for search keyboard functionality.

Tests keyboard layouts, button text, and navigation patterns
for search and list access functionality.
"""

import pytest
from telegram import ReplyKeyboardMarkup

from src.bot.keyboards.search_keyboards import (
    get_main_menu_keyboard,
    get_search_mode_selection_keyboard,
    get_waiting_for_name_keyboard,
    get_waiting_for_room_keyboard,
    get_waiting_for_floor_keyboard,
    get_results_navigation_keyboard,
    NAV_SEARCH_NAME,
    NAV_SEARCH_ROOM, 
    NAV_SEARCH_FLOOR,
    NAV_MAIN_MENU,
    NAV_CANCEL,
    NAV_BACK_TO_SEARCH_MODES,
)


class TestMainMenuKeyboard:
    """Test main menu keyboard functionality."""

    def test_main_menu_contains_search_button(self):
        """Test that main menu contains the search participants button."""
        keyboard = get_main_menu_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        assert keyboard.keyboard[0][0].text == "🔍 Поиск участников"

    def test_main_menu_contains_get_list_button(self):
        """Test that main menu contains the get list button."""
        keyboard = get_main_menu_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup) 
        # Check button text attributes
        button_texts = [button.text for row in keyboard.keyboard for button in row]
        assert "📋 Получить список" in button_texts

    def test_main_menu_has_correct_layout(self):
        """Test that main menu has both buttons arranged correctly."""
        keyboard = get_main_menu_keyboard()
        
        # Should have 2 buttons in the main menu row
        assert len(keyboard.keyboard) == 1
        assert len(keyboard.keyboard[0]) == 2
        assert keyboard.keyboard[0][0].text == "🔍 Поиск участников"
        assert keyboard.keyboard[0][1].text == "📋 Получить список"

    def test_main_menu_keyboard_properties(self):
        """Test that main menu keyboard has correct properties."""
        keyboard = get_main_menu_keyboard()
        
        assert keyboard.resize_keyboard is True
        assert keyboard.one_time_keyboard is False
        assert keyboard.selective is False


class TestSearchModeSelectionKeyboard:
    """Test search mode selection keyboard functionality."""

    def test_search_mode_selection_has_correct_buttons(self):
        """Test search mode keyboard contains all expected buttons."""
        keyboard = get_search_mode_selection_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        button_texts = [button.text for row in keyboard.keyboard for button in row]
        
        assert NAV_SEARCH_NAME in button_texts
        assert NAV_SEARCH_ROOM in button_texts
        assert NAV_SEARCH_FLOOR in button_texts
        assert NAV_MAIN_MENU in button_texts

    def test_search_mode_selection_layout(self):
        """Test search mode keyboard has correct layout."""
        keyboard = get_search_mode_selection_keyboard()
        
        assert len(keyboard.keyboard) == 2
        assert [btn.text for btn in keyboard.keyboard[0]] == [NAV_SEARCH_NAME, NAV_SEARCH_ROOM]
        assert [btn.text for btn in keyboard.keyboard[1]] == [NAV_SEARCH_FLOOR, NAV_MAIN_MENU]


class TestWaitingKeyboards:
    """Test keyboards shown while waiting for user input."""

    def test_waiting_for_name_keyboard(self):
        """Test waiting for name keyboard has navigation options."""
        keyboard = get_waiting_for_name_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        button_texts = [btn.text for btn in keyboard.keyboard[0]]
        assert button_texts == [NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]

    def test_waiting_for_room_keyboard(self):
        """Test waiting for room keyboard has navigation options."""
        keyboard = get_waiting_for_room_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        button_texts = [btn.text for btn in keyboard.keyboard[0]]
        assert button_texts == [NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]

    def test_waiting_for_floor_keyboard(self):
        """Test waiting for floor keyboard has navigation options."""
        keyboard = get_waiting_for_floor_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        button_texts = [btn.text for btn in keyboard.keyboard[0]]
        assert button_texts == [NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]


class TestResultsNavigationKeyboard:
    """Test results navigation keyboard functionality."""

    def test_results_navigation_keyboard(self):
        """Test results navigation keyboard has correct options."""
        keyboard = get_results_navigation_keyboard()
        
        assert isinstance(keyboard, ReplyKeyboardMarkup)
        button_texts = [btn.text for btn in keyboard.keyboard[0]]
        assert button_texts == [NAV_BACK_TO_SEARCH_MODES, NAV_MAIN_MENU]