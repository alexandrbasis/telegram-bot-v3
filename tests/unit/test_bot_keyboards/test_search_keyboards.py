"""
Tests for search keyboard functionality.

Tests keyboard layouts, button text, and navigation patterns
for search and list access functionality.
"""

import pytest
from telegram import InlineKeyboardMarkup, ReplyKeyboardMarkup

from src.bot.keyboards.search_keyboards import (
    NAV_BACK_TO_SEARCH_MODES,
    NAV_CANCEL,
    NAV_MAIN_MENU,
    NAV_SEARCH_FLOOR,
    NAV_SEARCH_NAME,
    NAV_SEARCH_ROOM,
    get_floor_discovery_keyboard,
    get_floor_selection_keyboard,
    get_main_menu_keyboard,
    get_results_navigation_keyboard,
    get_search_mode_selection_keyboard,
    get_waiting_for_floor_keyboard,
    get_waiting_for_name_keyboard,
    get_waiting_for_room_keyboard,
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
        assert [btn.text for btn in keyboard.keyboard[0]] == [
            NAV_SEARCH_NAME,
            NAV_SEARCH_ROOM,
        ]
        assert [btn.text for btn in keyboard.keyboard[1]] == [
            NAV_SEARCH_FLOOR,
            NAV_MAIN_MENU,
        ]


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


class TestFloorDiscoveryKeyboard:
    """Test floor discovery inline keyboard functionality."""

    def test_floor_discovery_keyboard_structure(self):
        """Test floor discovery keyboard has correct structure."""
        keyboard = get_floor_discovery_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        
    def test_floor_discovery_button_text(self):
        """Test floor discovery button has correct Russian text."""
        keyboard = get_floor_discovery_keyboard()
        
        button = keyboard.inline_keyboard[0][0]
        assert button.text == "Показать доступные этажи"
        
    def test_floor_discovery_callback_data(self):
        """Test floor discovery button has correct callback data."""
        keyboard = get_floor_discovery_keyboard()
        
        button = keyboard.inline_keyboard[0][0]
        assert button.callback_data == "floor_discovery"


class TestFloorSelectionKeyboard:
    """Test floor selection inline keyboard functionality."""
    
    def test_floor_selection_with_single_floor(self):
        """Test keyboard with single floor."""
        keyboard = get_floor_selection_keyboard([1])
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 1
        
        button = keyboard.inline_keyboard[0][0]
        assert button.text == "Этаж 1"
        assert button.callback_data == "floor_select_1"
        
    def test_floor_selection_with_multiple_floors(self):
        """Test keyboard with multiple floors in sorted order."""
        keyboard = get_floor_selection_keyboard([3, 1, 2])
        
        assert len(keyboard.inline_keyboard) == 1
        assert len(keyboard.inline_keyboard[0]) == 3
        
        # Check floors are sorted
        assert keyboard.inline_keyboard[0][0].text == "Этаж 1"
        assert keyboard.inline_keyboard[0][1].text == "Этаж 2"
        assert keyboard.inline_keyboard[0][2].text == "Этаж 3"
        
        # Check callback data
        assert keyboard.inline_keyboard[0][0].callback_data == "floor_select_1"
        assert keyboard.inline_keyboard[0][1].callback_data == "floor_select_2"
        assert keyboard.inline_keyboard[0][2].callback_data == "floor_select_3"
        
    def test_floor_selection_with_many_floors_creates_rows(self):
        """Test keyboard creates multiple rows with max 3 buttons per row."""
        keyboard = get_floor_selection_keyboard([1, 2, 3, 4, 5, 6, 7])
        
        assert len(keyboard.inline_keyboard) == 3  # 3 rows: 3+3+1
        assert len(keyboard.inline_keyboard[0]) == 3  # First row has 3 buttons
        assert len(keyboard.inline_keyboard[1]) == 3  # Second row has 3 buttons
        assert len(keyboard.inline_keyboard[2]) == 1  # Third row has 1 button
        
        # Check last button
        last_button = keyboard.inline_keyboard[2][0]
        assert last_button.text == "Этаж 7"
        assert last_button.callback_data == "floor_select_7"
        
    def test_floor_selection_with_empty_list(self):
        """Test keyboard returns None for empty floor list."""
        keyboard = get_floor_selection_keyboard([])
        
        assert keyboard is None
        
    def test_floor_selection_preserves_floor_numbers(self):
        """Test keyboard preserves exact floor numbers in callback data."""
        floors = [1, 3, 10, 25]
        keyboard = get_floor_selection_keyboard(floors)
        
        # Flatten all buttons to check
        all_buttons = [
            button
            for row in keyboard.inline_keyboard
            for button in row
        ]
        
        assert len(all_buttons) == 4
        assert all_buttons[0].callback_data == "floor_select_1"
        assert all_buttons[1].callback_data == "floor_select_3"
        assert all_buttons[2].callback_data == "floor_select_10"
        assert all_buttons[3].callback_data == "floor_select_25"
