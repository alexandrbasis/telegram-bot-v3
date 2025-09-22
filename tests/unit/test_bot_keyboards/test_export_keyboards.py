"""
Tests for export selection keyboard builders.

Validates keyboard layouts for export options and department selection
with proper Russian labels and callback data integration.
"""

import pytest

from src.bot.keyboards.export_keyboards import (
    get_export_selection_keyboard,
    get_department_selection_keyboard,
)
from src.bot.handlers.export_states import ExportCallbackData


class TestExportSelectionKeyboard:
    """Test main export selection keyboard generation."""

    def test_export_selection_keyboard_structure(self):
        """Test that export selection keyboard has correct structure."""
        keyboard = get_export_selection_keyboard()

        # Should be an InlineKeyboardMarkup
        assert hasattr(keyboard, 'inline_keyboard')

        # Should have 4 rows (6 export options + cancel arranged in rows)
        # Row 1: Export All, Export Team
        # Row 2: Export Candidates, Export by Department
        # Row 3: Export Bible Readers, Export ROE
        # Row 4: Cancel
        assert len(keyboard.inline_keyboard) == 4

    def test_export_selection_keyboard_buttons(self):
        """Test that all required export buttons are present with correct labels."""
        keyboard = get_export_selection_keyboard()

        # Flatten all buttons to check content
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)

        # Should have 7 buttons total (6 export types + cancel)
        assert len(all_buttons) == 7

        # Check Russian labels are present
        button_texts = [btn.text for btn in all_buttons]
        expected_labels = [
            "📊 Экспорт всех участников",
            "👥 Экспорт команды",
            "🆕 Экспорт кандидатов",
            "🏢 Экспорт по отделу",
            "📖 Экспорт Bible Readers",
            "🎯 Экспорт ROE",
            "❌ Отмена"
        ]

        for expected_label in expected_labels:
            assert expected_label in button_texts

    def test_export_selection_keyboard_callback_data(self):
        """Test that buttons have correct callback data."""
        keyboard = get_export_selection_keyboard()

        # Flatten all buttons to check callback data
        all_buttons = []
        for row in keyboard.inline_keyboard:
            all_buttons.extend(row)

        # Extract callback data
        callback_data = [btn.callback_data for btn in all_buttons]

        # Check that expected callback patterns are present
        expected_callbacks = [
            ExportCallbackData.EXPORT_ALL,
            ExportCallbackData.EXPORT_TEAM,
            ExportCallbackData.EXPORT_CANDIDATES,
            ExportCallbackData.EXPORT_BY_DEPARTMENT,
            ExportCallbackData.EXPORT_BIBLE_READERS,
            ExportCallbackData.EXPORT_ROE,
            ExportCallbackData.CANCEL
        ]

        for expected_callback in expected_callbacks:
            assert expected_callback in callback_data

    def test_export_selection_keyboard_layout(self):
        """Test that keyboard layout is optimized for mobile."""
        keyboard = get_export_selection_keyboard()

        # Check row structure
        rows = keyboard.inline_keyboard

        # Row 1: 2 buttons (Export All, Export Team)
        assert len(rows[0]) == 2

        # Row 2: 2 buttons (Export Candidates, Export by Department)
        assert len(rows[1]) == 2

        # Row 3: 2 buttons (Export Bible Readers, Export ROE)
        assert len(rows[2]) == 2

        # Row 4: 1 button (Cancel)
        assert len(rows[3]) == 1


class TestDepartmentSelectionKeyboard:
    """Test department selection keyboard generation."""

    def test_department_selection_keyboard_structure(self):
        """Test that department selection keyboard has correct structure."""
        keyboard = get_department_selection_keyboard()

        # Should be an InlineKeyboardMarkup
        assert hasattr(keyboard, 'inline_keyboard')

        # Should have multiple rows for 13 departments + navigation
        # Expect 7 rows: 6 rows of 2 departments each + 1 row with last dept + navigation
        assert len(keyboard.inline_keyboard) >= 7

    def test_department_selection_keyboard_departments(self):
        """Test that all 13 departments are present with correct labels."""
        keyboard = get_department_selection_keyboard()

        # Flatten all buttons except navigation (last row)
        department_buttons = []
        for row in keyboard.inline_keyboard[:-1]:  # Exclude last row (navigation)
            department_buttons.extend(row)

        # Should have 13 department buttons
        assert len(department_buttons) == 13

        # Check all departments are present
        button_texts = [btn.text for btn in department_buttons]
        expected_departments = [
            "ROE", "Chapel", "Setup", "Palanka", "Administration",
            "Kitchen", "Decoration", "Bell", "Refreshment",
            "Worship", "Media", "Clergy", "Rectorate"
        ]

        for dept in expected_departments:
            assert dept in button_texts

    def test_department_selection_keyboard_callback_data(self):
        """Test that department buttons have correct callback data."""
        keyboard = get_department_selection_keyboard()

        # Get department buttons (exclude navigation row)
        department_buttons = []
        for row in keyboard.inline_keyboard[:-1]:
            department_buttons.extend(row)

        # Check callback data patterns
        for button in department_buttons:
            callback = button.callback_data
            # Should match department callback pattern
            assert callback.startswith("export:department:")
            # Should contain a valid department name
            dept_name = ExportCallbackData.parse_department(callback)
            assert dept_name is not None
            assert dept_name == button.text  # Button text should match department name

    def test_department_selection_keyboard_navigation(self):
        """Test that navigation buttons are present in department keyboard."""
        keyboard = get_department_selection_keyboard()

        # Last row should contain navigation buttons
        nav_row = keyboard.inline_keyboard[-1]
        nav_buttons = [btn.text for btn in nav_row]
        nav_callbacks = [btn.callback_data for btn in nav_row]

        # Should have Back and Cancel buttons
        assert "🔙 Назад" in nav_buttons
        assert "❌ Отмена" in nav_buttons

        # Check callback data
        assert ExportCallbackData.BACK_TO_EXPORT_SELECTION in nav_callbacks
        assert ExportCallbackData.CANCEL in nav_callbacks

    def test_department_selection_keyboard_layout(self):
        """Test that department keyboard layout is mobile-optimized."""
        keyboard = get_department_selection_keyboard()

        # Most rows should have 2 buttons for better mobile experience
        row_lengths = [len(row) for row in keyboard.inline_keyboard[:-1]]  # Exclude nav row

        # Most rows should have 2 buttons (some may have 1 if odd total)
        assert all(length <= 2 for length in row_lengths)

        # At least some rows should have 2 buttons
        assert 2 in row_lengths