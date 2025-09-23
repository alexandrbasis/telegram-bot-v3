"""
ConversationHandler setup for participant search functionality.

Configures the complete conversation flow with entry points, states, and fallbacks
for the Russian name search feature.
"""

import logging
import warnings
import re

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.handlers.admin_handlers import handle_logging_toggle_command
from src.bot.handlers.edit_participant_handlers import (
    EditStates,
    cancel_editing,
    handle_button_field_selection,
    handle_field_edit_selection,
    handle_text_field_input,
    save_changes,
)
from src.bot.handlers.floor_search_handlers import (
    FloorSearchStates,
    handle_floor_discovery_callback,
    handle_floor_search_command,
    handle_floor_selection_callback,
    process_floor_search,
)
from src.bot.handlers.list_handlers import (
    handle_department_filter_selection,
    handle_get_list_request,
    handle_list_navigation,
    handle_role_selection,
)
from src.bot.handlers.room_search_handlers import (
    RoomSearchStates,
    handle_room_search_command,
    process_room_search,
)
from src.bot.handlers.search_handlers import (
    SearchStates,
    back_to_search_modes,
    cancel_search,
    handle_participant_selection,
    handle_search_floor_mode,
    handle_search_name_mode,
    handle_search_room_mode,
    main_menu_button,
    process_name_search,
    search_button,
    start_command,
)
from src.bot.handlers.timeout_handlers import (
    get_timeout_recovery_handlers,
)
from src.bot.keyboards.search_keyboards import (
    NAV_BACK_TO_SEARCH_MODES,
    NAV_CANCEL,
    NAV_MAIN_MENU,
    NAV_SEARCH_FLOOR,
    NAV_SEARCH_NAME,
    NAV_SEARCH_ROOM,
)
from src.config.settings import get_telegram_settings

logger = logging.getLogger(__name__)


def get_search_conversation_handler() -> ConversationHandler:
    """
    Create and configure the integrated search and editing conversation handler.

    This handler manages both search and editing workflows in a single
    conversation to maintain seamless user experience. While this creates
    some architectural coupling, it ensures proper state management and
    data flow between search and editing phases.

    Search Flow:
    - Entry point: /start command
    - Search states: MAIN_MENU, WAITING_FOR_NAME, SHOWING_RESULTS

    Editing Flow (triggered from search results):
    - Edit states: FIELD_SELECTION, TEXT_INPUT, BUTTON_SELECTION, CONFIRMATION
    - Integrated fallbacks: Return to main menu from any state

    Returns:
        Configured ConversationHandler instance
    """
    logger.info("Setting up search conversation handler")

    # Suppress PTBUserWarning during handler construction due to mixed handler types
    try:
        from telegram.warnings import PTBUserWarning  # type: ignore
    except Exception:  # pragma: no cover - fallback for PTB variants
        try:
            from telegram._utils.warnings import PTBUserWarning  # type: ignore
        except Exception:
            PTBUserWarning = Warning  # type: ignore

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PTBUserWarning)

        conversation_handler = ConversationHandler(
            entry_points=[
            CommandHandler("start", start_command),
            CommandHandler("search_room", handle_room_search_command),
            CommandHandler("search_floor", handle_floor_search_command),
            # Entry points for text buttons to allow re-entry after timeout
            MessageHandler(filters.Regex("^🔍 Поиск участников$"), search_button),
            MessageHandler(
                filters.Regex("^📋 Получить список$"), handle_get_list_request
            ),
            MessageHandler(
                filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
            ),
            # Keep inline button support for stale buttons
            CallbackQueryHandler(search_button, pattern="^search$"),
            # Inline restart button entry point after timeout
            CallbackQueryHandler(main_menu_button, pattern="^restart_bot$"),
        ],
        states={
            # === SEARCH STATES ===
            SearchStates.MAIN_MENU: [
                # Text-based navigation from reply keyboard
                MessageHandler(filters.Regex(r"^🔍 Поиск участников$"), search_button),
                MessageHandler(
                    filters.Regex(r"^📋 Получить список$"), handle_get_list_request
                ),
                # Backward compat (if any inline button remains)
                CallbackQueryHandler(search_button, pattern="^search$"),
                # List callback handlers for role selection, department filtering, and navigation
                CallbackQueryHandler(handle_role_selection, pattern="^list_role:"),
                CallbackQueryHandler(
                    handle_department_filter_selection, pattern="^list:filter:"
                ),
                CallbackQueryHandler(handle_list_navigation, pattern="^list_nav:"),
            ],
            SearchStates.SEARCH_MODE_SELECTION: [
                # Search mode selection handlers
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_SEARCH_NAME)}$"),
                    handle_search_name_mode,
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_SEARCH_ROOM)}$"),
                    handle_search_room_mode,
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_SEARCH_FLOOR)}$"),
                    handle_search_floor_mode,
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                # List handlers for role selection, department filtering, and navigation
                CallbackQueryHandler(handle_role_selection, pattern="^list_role:"),
                CallbackQueryHandler(
                    handle_department_filter_selection, pattern="^list:filter:"
                ),
                CallbackQueryHandler(handle_list_navigation, pattern="^list_nav:"),
            ],
            SearchStates.WAITING_FOR_NAME: [
                # Name input
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(
                        rf"^{re.escape(NAV_MAIN_MENU)}$|^{re.escape(NAV_CANCEL)}$|^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$|^{re.escape(NAV_SEARCH_NAME)}$"
                    ),
                    process_name_search,
                ),
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_CANCEL)}$"), cancel_search
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
            ],
            SearchStates.SHOWING_RESULTS: [
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
                # Participant selection via inline buttons remains
                CallbackQueryHandler(
                    handle_participant_selection, pattern="^select_participant:"
                ),
                # Backward compat for inline main menu button if present
                CallbackQueryHandler(main_menu_button, pattern="^main_menu$"),
            ],
            # === ROOM SEARCH STATES ===
            RoomSearchStates.WAITING_FOR_ROOM: [
                # Room number input
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(
                        rf"^{re.escape(NAV_MAIN_MENU)}$|^{re.escape(NAV_CANCEL)}$|^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$|^{re.escape(NAV_SEARCH_ROOM)}$"
                    ),
                    process_room_search,
                ),
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_CANCEL)}$"), cancel_search
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
            ],
            RoomSearchStates.SHOWING_ROOM_RESULTS: [
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
            ],
            # === FLOOR SEARCH STATES ===
            FloorSearchStates.WAITING_FOR_FLOOR: [
                # Floor discovery and selection callbacks
                CallbackQueryHandler(
                    handle_floor_discovery_callback, pattern="^floor_discovery$"
                ),
                CallbackQueryHandler(
                    handle_floor_selection_callback, pattern=r"^floor_select_(\d+)$"
                ),
                # Floor number input
                MessageHandler(
                    filters.TEXT
                    & ~filters.COMMAND
                    & ~filters.Regex(
                        rf"^{re.escape(NAV_MAIN_MENU)}$|^{re.escape(NAV_CANCEL)}$|^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$|^{re.escape(NAV_SEARCH_FLOOR)}$"
                    ),
                    process_floor_search,
                ),
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_CANCEL)}$"), cancel_search
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
            ],
            FloorSearchStates.SHOWING_FLOOR_RESULTS: [
                # Navigation via reply keyboard
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_MAIN_MENU)}$"), main_menu_button
                ),
                MessageHandler(
                    filters.Regex(rf"^{re.escape(NAV_BACK_TO_SEARCH_MODES)}$"),
                    back_to_search_modes,
                ),
            ],
            # === EDITING STATES ===
            # Note: These states handle participant editing after selection from search results
            # This integration maintains seamless UX and proper state/data management
            EditStates.FIELD_SELECTION: [
                CallbackQueryHandler(
                    handle_field_edit_selection, pattern="^edit_field:"
                ),
                CallbackQueryHandler(save_changes, pattern="^save_changes$"),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$"),
                CallbackQueryHandler(main_menu_button, pattern="^main_menu$"),
            ],
            EditStates.TEXT_INPUT: [
                MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_text_field_input
                ),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$"),
            ],
            EditStates.BUTTON_SELECTION: [
                CallbackQueryHandler(
                    handle_button_field_selection, pattern="^select_value:"
                ),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$"),
            ],
            EditStates.CONFIRMATION: [
                CallbackQueryHandler(save_changes, pattern="^save_changes$"),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$"),
            ],
            # === TIMEOUT STATE ===
            ConversationHandler.TIMEOUT: [
                # Handle both messages and callback queries after timeout
                *get_timeout_recovery_handlers(),
            ],
        },
        fallbacks=[
            CommandHandler("start", start_command),
            CommandHandler("logging", handle_logging_toggle_command),
        ],
            # Timeout configuration: Convert minutes to seconds
            conversation_timeout=get_telegram_settings().conversation_timeout_minutes * 60,
            # Disable allow_reentry to avoid duplicate handler execution when
            # entry points overlap with state handlers (e.g., /start or menu buttons).
            allow_reentry=False,
            # Keep default mixed-handler behavior; warnings suppressed above
            per_message=False,
        )

    logger.info("Search conversation handler configured successfully")
    return conversation_handler
