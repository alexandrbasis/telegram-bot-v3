"""
Keyboard builders for export functionality.

Provides inline keyboard layouts for export type selection and department
selection with Russian labels optimized for mobile devices.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.bot.handlers.export_states import ExportCallbackData


def get_export_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Get export selection inline keyboard with 6 export options.

    Provides buttons for users to choose between different export types:
    - Export All Participants (current functionality)
    - Export Team Members (role-based filtering)
    - Export Candidates (role-based filtering)
    - Export by Department (department selection submenu)
    - Export Bible Readers (BibleReaders table)
    - Export ROE Sessions (ROE table)

    Returns:
        InlineKeyboardMarkup with export option buttons and cancel
    """
    keyboard = [
        # Row 1: General exports
        [
            InlineKeyboardButton(
                "📊 Экспорт всех участников",
                callback_data=ExportCallbackData.EXPORT_ALL
            ),
            InlineKeyboardButton(
                "👥 Экспорт команды",
                callback_data=ExportCallbackData.EXPORT_TEAM
            ),
        ],
        # Row 2: Filtered exports
        [
            InlineKeyboardButton(
                "🆕 Экспорт кандидатов",
                callback_data=ExportCallbackData.EXPORT_CANDIDATES
            ),
            InlineKeyboardButton(
                "🏢 Экспорт по отделу",
                callback_data=ExportCallbackData.EXPORT_BY_DEPARTMENT
            ),
        ],
        # Row 3: Special table exports
        [
            InlineKeyboardButton(
                "📖 Экспорт Bible Readers",
                callback_data=ExportCallbackData.EXPORT_BIBLE_READERS
            ),
            InlineKeyboardButton(
                "🎯 Экспорт ROE",
                callback_data=ExportCallbackData.EXPORT_ROE
            ),
        ],
        # Row 4: Navigation
        [
            InlineKeyboardButton(
                "❌ Отмена",
                callback_data=ExportCallbackData.CANCEL
            ),
        ],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_department_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Get department selection inline keyboard with all 13 departments.

    Provides buttons for users to select specific department for
    participant export filtering. Layout optimized for mobile.

    Returns:
        InlineKeyboardMarkup with department buttons and navigation
    """
    # All 13 departments as specified in requirements
    departments = [
        "ROE", "Chapel", "Setup", "Palanka", "Administration",
        "Kitchen", "Decoration", "Bell", "Refreshment",
        "Worship", "Media", "Clergy", "Rectorate"
    ]

    # Build department rows (2 buttons per row for mobile optimization)
    keyboard = []
    for i in range(0, len(departments), 2):
        row = []

        # Add first department in pair
        dept1 = departments[i]
        row.append(InlineKeyboardButton(
            dept1,
            callback_data=ExportCallbackData.department_callback(dept1)
        ))

        # Add second department if exists
        if i + 1 < len(departments):
            dept2 = departments[i + 1]
            row.append(InlineKeyboardButton(
                dept2,
                callback_data=ExportCallbackData.department_callback(dept2)
            ))

        keyboard.append(row)

    # Add navigation row
    navigation_row = [
        InlineKeyboardButton(
            "🔙 Назад",
            callback_data=ExportCallbackData.BACK_TO_EXPORT_SELECTION
        ),
        InlineKeyboardButton(
            "❌ Отмена",
            callback_data=ExportCallbackData.CANCEL
        ),
    ]
    keyboard.append(navigation_row)

    return InlineKeyboardMarkup(keyboard)
