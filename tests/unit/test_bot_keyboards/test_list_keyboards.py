"""
Tests for list keyboard functionality.

Tests keyboard layouts, button callback data, and navigation patterns
for participant list access functionality.
"""

import pytest
from telegram import InlineKeyboardMarkup

from src.bot.keyboards.list_keyboards import (
    create_department_filter_keyboard,
    get_list_pagination_keyboard,
    get_role_selection_keyboard,
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


class TestDepartmentFilterKeyboard:
    """Test department filter keyboard functionality."""

    def test_all_departments_in_keyboard(self):
        """Ensure all 13 departments plus 2 special options present."""
        keyboard = create_department_filter_keyboard()

        assert isinstance(keyboard, InlineKeyboardMarkup)

        # Count all buttons
        total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
        # Should have 15 buttons total (13 departments + All + No department)
        assert total_buttons == 15

    def test_russian_department_names(self):
        """Verify all department names have correct Russian translations."""
        keyboard = create_department_filter_keyboard()

        # Flatten all buttons for easier checking
        buttons = []
        for row in keyboard.inline_keyboard:
            buttons.extend(row)

        # Check special buttons have Russian text
        button_texts = [btn.text for btn in buttons]
        assert "🌐 Все участники" in button_texts  # All participants
        assert "❓ Без департамента" in button_texts  # No department

        # Check some department Russian translations are present
        assert "РОЭ" in button_texts
        assert "Часовня" in button_texts
        assert "Подготовка" in button_texts
        assert "Паланка" in button_texts
        assert "Администрация" in button_texts
        assert "Кухня" in button_texts
        assert "Оформление" in button_texts
        assert "Звонок" in button_texts
        assert "Освежение" in button_texts
        assert "Прославление" in button_texts
        assert "Медиа" in button_texts
        assert "Духовенство" in button_texts
        assert "Ректорат" in button_texts

    def test_keyboard_button_layout(self):
        """Validate keyboard layout is intuitive and consistent."""
        keyboard = create_department_filter_keyboard()

        # Should have multiple rows with consistent width
        rows = keyboard.inline_keyboard
        assert len(rows) > 0

        # First row should have special "All participants" button
        assert rows[0][0].text == "🌐 Все участники"

        # Last row should have "No department" button
        assert rows[-1][-1].text == "❓ Без департамента"

    def test_special_options_placement(self):
        """Confirm 'All participants' and 'No department' properly positioned."""
        keyboard = create_department_filter_keyboard()

        # First button should be "All participants"
        first_button = keyboard.inline_keyboard[0][0]
        assert first_button.text == "🌐 Все участники"
        assert first_button.callback_data == "list:filter:all"

        # Last button should be "No department"
        last_row = keyboard.inline_keyboard[-1]
        last_button = last_row[-1]
        assert last_button.text == "❓ Без департамента"
        assert last_button.callback_data == "list:filter:none"

    def test_keyboard_callback_data_structure(self):
        """Validate callback data format consistency."""
        keyboard = create_department_filter_keyboard()

        # Flatten all buttons
        buttons = []
        for row in keyboard.inline_keyboard:
            buttons.extend(row)

        for button in buttons:
            # All callbacks should start with "list:filter:"
            assert button.callback_data.startswith("list:filter:")

            # Extract the filter type
            parts = button.callback_data.split(":")
            assert len(parts) in [3, 4]  # 3 for "all"/"none", 4 for departments
            assert parts[0] == "list"
            assert parts[1] == "filter"

            if len(parts) == 3:
                # Special options: "all" or "none"
                assert parts[2] in ["all", "none"]
            else:
                # Department option
                assert parts[2] == "department"
                # parts[3] should be a valid department value

    def test_callback_data_uniqueness(self):
        """Ensure each department has unique callback identifier."""
        keyboard = create_department_filter_keyboard()

        # Collect all callback data
        callbacks = []
        for row in keyboard.inline_keyboard:
            for button in row:
                callbacks.append(button.callback_data)

        # Check for uniqueness
        assert len(callbacks) == len(set(callbacks))
        assert len(callbacks) == 15  # Total expected buttons

    def test_department_selection_flow(self):
        """Verify keyboard enables proper navigation flow."""
        keyboard = create_department_filter_keyboard()

        # Should be InlineKeyboardMarkup for use in messages
        assert isinstance(keyboard, InlineKeyboardMarkup)

        # All buttons should be clickable (have callback_data)
        for row in keyboard.inline_keyboard:
            for button in row:
                assert button.callback_data is not None
                assert len(button.callback_data) > 0

    def test_back_navigation_compatibility(self):
        """Confirm keyboard works with existing back button patterns."""
        keyboard = create_department_filter_keyboard()

        # Callback pattern should be compatible with existing handlers
        for row in keyboard.inline_keyboard:
            for button in row:
                # Should follow list navigation pattern
                assert "list:" in button.callback_data
                assert "filter:" in button.callback_data

    def test_translation_missing_departments(self):
        """Handle missing Russian translations gracefully."""
        # This test ensures the keyboard creation doesn't fail
        # even if some translations might be missing
        keyboard = create_department_filter_keyboard()

        # Should create keyboard successfully
        assert keyboard is not None
        assert isinstance(keyboard, InlineKeyboardMarkup)

        # Should have all buttons even if translations missing
        total_buttons = sum(len(row) for row in keyboard.inline_keyboard)
        assert total_buttons == 15
