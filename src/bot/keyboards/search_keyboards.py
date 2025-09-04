"""
Keyboard builders for search functionality.

Provides reply keyboard layouts for search mode selection and navigation
with Russian labels optimized for mobile devices.
"""

from telegram import ReplyKeyboardMarkup


# Navigation button constants
NAV_SEARCH_NAME = "👤 По имени"
NAV_SEARCH_ROOM = "🚪 По комнате" 
NAV_SEARCH_FLOOR = "🏢 По этажу"
NAV_MAIN_MENU = "🏠 Главное меню"
NAV_CANCEL = "❌ Отмена"
NAV_BACK_TO_SEARCH_MODES = "🔙 Назад к поиску"


def get_main_menu_keyboard() -> ReplyKeyboardMarkup:
    """
    Get main menu reply keyboard with search mode selection button.
    
    Provides the primary navigation entry point that leads to search mode selection.
    
    Returns:
        ReplyKeyboardMarkup with search mode selection button
    """
    keyboard = [["🔍 Поиск участников"]]
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
    keyboard = [
        [NAV_SEARCH_NAME, NAV_SEARCH_ROOM],
        [NAV_SEARCH_FLOOR, NAV_MAIN_MENU]
    ]
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