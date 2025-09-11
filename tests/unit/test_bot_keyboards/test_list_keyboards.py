"""
Tests for list keyboard functionality.

Tests keyboard layouts, button callback data, and navigation patterns
for participant list access functionality.
"""

import pytest
from telegram import InlineKeyboardMarkup

from src.bot.keyboards.list_keyboards import (
    get_role_selection_keyboard,
    get_list_pagination_keyboard,
)


class TestRoleSelectionKeyboard:
    """Test role selection keyboard functionality for participant lists."""

    def test_role_selection_keyboard_structure(self):
        """Test that role selection keyboard has correct structure."""
        keyboard = get_role_selection_keyboard()
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should have 2 rows: Team and Candidates
        assert len(keyboard.inline_keyboard) == 2

    def test_role_selection_team_button(self):
        """Test team members button has correct text and callback data."""
        keyboard = get_role_selection_keyboard()
        
        team_button = keyboard.inline_keyboard[0][0]
        assert team_button.text == "👥 Команда"
        assert team_button.callback_data == "list_role:TEAM"

    def test_role_selection_candidate_button(self):
        """Test candidates button has correct text and callback data."""
        keyboard = get_role_selection_keyboard()
        
        candidates_button = keyboard.inline_keyboard[1][0]
        assert candidates_button.text == "🎯 Кандидаты"
        assert candidates_button.callback_data == "list_role:CANDIDATE"

    def test_role_selection_callback_data_format(self):
        """Test that callback data follows expected format."""
        keyboard = get_role_selection_keyboard()
        
        for row in keyboard.inline_keyboard:
            for button in row:
                assert button.callback_data.startswith("list_role:")
                role = button.callback_data.split(":")[1]
                assert role in ["TEAM", "CANDIDATE"]


class TestListPaginationKeyboard:
    """Test pagination keyboard functionality for participant lists."""

    def test_pagination_keyboard_structure(self):
        """Test pagination keyboard has correct button structure."""
        keyboard = get_list_pagination_keyboard(has_prev=True, has_next=True)
        
        assert isinstance(keyboard, InlineKeyboardMarkup)
        # Should have 2 rows: navigation and main menu
        assert len(keyboard.inline_keyboard) == 2

    def test_pagination_with_prev_and_next(self):
        """Test pagination keyboard when both prev and next are available."""
        keyboard = get_list_pagination_keyboard(has_prev=True, has_next=True)
        
        # First row should have Previous and Next buttons
        nav_row = keyboard.inline_keyboard[0]
        assert len(nav_row) == 2
        
        prev_button = nav_row[0]
        next_button = nav_row[1]
        
        assert prev_button.text == "⬅️ Назад"
        assert prev_button.callback_data == "list_nav:PREV"
        assert next_button.text == "➡️ Далее"
        assert next_button.callback_data == "list_nav:NEXT"

    def test_pagination_with_only_next(self):
        """Test pagination keyboard when only next is available."""
        keyboard = get_list_pagination_keyboard(has_prev=False, has_next=True)
        
        nav_row = keyboard.inline_keyboard[0]
        assert len(nav_row) == 1
        
        next_button = nav_row[0]
        assert next_button.text == "➡️ Далее"
        assert next_button.callback_data == "list_nav:NEXT"

    def test_pagination_with_only_prev(self):
        """Test pagination keyboard when only prev is available."""
        keyboard = get_list_pagination_keyboard(has_prev=True, has_next=False)
        
        nav_row = keyboard.inline_keyboard[0]
        assert len(nav_row) == 1
        
        prev_button = nav_row[0]
        assert prev_button.text == "⬅️ Назад"
        assert prev_button.callback_data == "list_nav:PREV"

    def test_pagination_without_nav_buttons(self):
        """Test pagination keyboard when no navigation buttons needed."""
        keyboard = get_list_pagination_keyboard(has_prev=False, has_next=False)
        
        # Should only have main menu button row
        assert len(keyboard.inline_keyboard) == 1

    def test_pagination_main_menu_button(self):
        """Test that main menu button is always present."""
        keyboard = get_list_pagination_keyboard(has_prev=True, has_next=True)
        
        # Main menu button should be in the last row
        main_menu_row = keyboard.inline_keyboard[-1]
        assert len(main_menu_row) == 1
        
        main_menu_button = main_menu_row[0]
        assert main_menu_button.text == "🏠 Главное меню"
        assert main_menu_button.callback_data == "list_nav:MAIN_MENU"

    def test_pagination_callback_data_format(self):
        """Test that all callback data follows expected format."""
        keyboard = get_list_pagination_keyboard(has_prev=True, has_next=True)
        
        for row in keyboard.inline_keyboard:
            for button in row:
                assert button.callback_data.startswith("list_nav:")
                action = button.callback_data.split(":")[1]
                assert action in ["PREV", "NEXT", "MAIN_MENU"]