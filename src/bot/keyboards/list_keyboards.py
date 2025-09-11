"""
Keyboard builders for participant list functionality.

Provides inline keyboard layouts for role selection and list pagination
with callback data patterns for list navigation.
"""

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


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
    has_prev: bool = False, has_next: bool = False
) -> InlineKeyboardMarkup:
    """
    Get pagination keyboard for participant list navigation.

    Provides Previous/Next navigation buttons when needed and always
    includes main menu return button.

    Args:
        has_prev: Whether previous page is available
        has_next: Whether next page is available

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

    # Always add main menu button
    keyboard.append(
        [InlineKeyboardButton("🏠 Главное меню", callback_data="list_nav:MAIN_MENU")]
    )

    return InlineKeyboardMarkup(keyboard)
