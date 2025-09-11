"""
Keyboard builders for search functionality.

Provides reply keyboard layouts for search mode selection and navigation
with Russian labels optimized for mobile devices.
"""

from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

# Navigation button constants
NAV_SEARCH_NAME = "👤 По имени"
NAV_SEARCH_ROOM = "🚪 По комнате"
NAV_SEARCH_FLOOR = "🏢 По этажу"
NAV_MAIN_MENU = "🏠 Главное меню"
NAV_CANCEL = "❌ Отмена"
NAV_BACK_TO_SEARCH_MODES = "🔙 Назад к поиску"


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get main menu reply keyboard with search and list access buttons.

    Provides the primary navigation entry point that leads to search mode selection
    and participant list access functionality.

    Returns:
        ReplyKeyboardMarkup with search and get list buttons
    """
    keyboard = [["🔍 Поиск участников", "📋 Получить список"]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_search_mode_selection_keyboard() -> ReplyKeyboardMarkup:
    """
    Get search mode selection keyboard with name/room/floor options.

    Provides buttons for users to choose between different search modes,
    addressing the major issue identified in code review.

    Returns:
        ReplyKeyboardMarkup with search mode buttons and main menu navigation
    """
    keyboard = [[NAV_SEARCH_NAME, NAV_SEARCH_ROOM], [NAV_SEARCH_FLOOR, NAV_MAIN_MENU]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_waiting_for_name_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard shown while waiting for name input."""
    keyboard = [[NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_waiting_for_room_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard shown while waiting for room input."""
    keyboard = [[NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_waiting_for_floor_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard shown while waiting for floor input."""
    keyboard = [[NAV_BACK_TO_SEARCH_MODES, NAV_CANCEL]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_results_navigation_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard shown while viewing results (navigation only)."""
    keyboard = [[NAV_BACK_TO_SEARCH_MODES, NAV_MAIN_MENU]]
    return ReplyKeyboardMarkup(
        keyboard, resize_keyboard=True, one_time_keyboard=False, selective=False
    )


def get_floor_discovery_keyboard() -> InlineKeyboardMarkup:
    """
    Get inline keyboard with floor discovery button.
    
    Creates an inline keyboard with a single button that allows users to
    discover available floors without guessing numbers.
    
    Returns:
        InlineKeyboardMarkup with floor discovery button
    """
    keyboard = [
        [InlineKeyboardButton("Показать доступные этажи", callback_data="floor_discovery")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_floor_selection_keyboard(floors: List[int]) -> Optional[InlineKeyboardMarkup]:
    """
    Get inline keyboard with floor selection buttons.
    
    Creates an inline keyboard with buttons for each available floor,
    arranged in rows of up to 3 buttons for optimal mobile display.
    
    Args:
        floors: List of available floor numbers
        
    Returns:
        InlineKeyboardMarkup with floor selection buttons, or None if no floors
    """
    if not floors:
        return None
    
    # Sort floors for consistent display
    sorted_floors = sorted(floors)
    
    # Build keyboard with 3 buttons per row
    keyboard = []
    row = []
    for floor in sorted_floors:
        button = InlineKeyboardButton(
            f"Этаж {floor}",
            callback_data=f"floor_select_{floor}"
        )
        row.append(button)
        
        # Add row when it has 3 buttons
        if len(row) == 3:
            keyboard.append(row)
            row = []
    
    # Add any remaining buttons in the last row
    if row:
        keyboard.append(row)
    
    return InlineKeyboardMarkup(keyboard)
