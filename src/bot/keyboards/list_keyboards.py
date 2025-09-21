"""
Keyboard builders for participant list functionality.

Provides inline keyboard layouts for role selection and list pagination
with callback data patterns for list navigation.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.models.participant import Department
from src.utils.translations import DEPARTMENT_RUSSIAN


def get_role_selection_keyboard() -> InlineKeyboardMarkup:
    """
    Get role selection keyboard for choosing participant lists.

    Provides buttons for selecting Team Members or Candidates lists
    with stable callback data patterns.

    Returns:
        InlineKeyboardMarkup with role selection buttons
    """
    keyboard = [
        [InlineKeyboardButton("👥 Команда", callback_data="list_role:TEAM")],
        [InlineKeyboardButton("🎯 Кандидаты", callback_data="list_role:CANDIDATE")],
    ]

    return InlineKeyboardMarkup(keyboard)


def get_list_pagination_keyboard(
    has_prev: bool = False, has_next: bool = False, show_department_back: bool = False
) -> InlineKeyboardMarkup:
    """
    Get pagination keyboard for participant list navigation.

    Provides Previous/Next navigation buttons when needed and includes
    navigation options based on context.

    Args:
        has_prev: Whether previous page is available
        has_next: Whether next page is available
        show_department_back: Whether to show "back to department selection" button

    Returns:
        InlineKeyboardMarkup with pagination controls
    """
    keyboard = []

    # Add navigation row if any navigation buttons are needed
    nav_row = []
    if has_prev:
        nav_row.append(InlineKeyboardButton("⬅️ Назад", callback_data="list_nav:PREV"))
    if has_next:
        nav_row.append(InlineKeyboardButton("➡️ Далее", callback_data="list_nav:NEXT"))

    if nav_row:
        keyboard.append(nav_row)

    # Add department selection button if this is a team list
    if show_department_back:
        keyboard.append(
            [InlineKeyboardButton("🔄 Выбор департамента", callback_data="list_nav:DEPARTMENT")]
        )

    # Always add main menu button
    keyboard.append(
        [InlineKeyboardButton("🏠 Главное меню", callback_data="list_nav:MAIN_MENU")]
    )

    return InlineKeyboardMarkup(keyboard)


def create_department_filter_keyboard() -> InlineKeyboardMarkup:
    """
    Create department filter keyboard for participant filtering.

    Creates a keyboard with all 13 departments plus special options
    for "All participants" and "No department" filtering.
    Uses Russian translations for all department names.

    Returns:
        InlineKeyboardMarkup with 15 buttons total: first/last rows contain
        single special buttons, middle rows group department buttons in
        batches of three.
    """
    keyboard = []

    # First row: Special "All participants" button
    keyboard.append(
        [InlineKeyboardButton("🌐 Все участники", callback_data="list:filter:all")]
    )

    # Department buttons - organize in rows of 3
    department_buttons = []
    for department in Department:
        # Get Russian translation for department name
        russian_name = DEPARTMENT_RUSSIAN.get(department.value, department.value)
        button = InlineKeyboardButton(
            russian_name, callback_data=f"list:filter:department:{department.value}"
        )
        department_buttons.append(button)

    # Arrange department buttons in rows of 3
    for i in range(0, len(department_buttons), 3):
        row = department_buttons[i : i + 3]
        keyboard.append(row)

    # Last row: Special "No department" button
    keyboard.append(
        [InlineKeyboardButton("❓ Без департамента", callback_data="list:filter:none")]
    )

    return InlineKeyboardMarkup(keyboard)
