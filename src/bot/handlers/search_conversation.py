"""
ConversationHandler setup for participant search functionality.

Configures the complete conversation flow with entry points, states, and fallbacks
for the Russian name search feature.
"""

import logging
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters
)

from src.bot.handlers.search_handlers import (
    start_command,
    search_button,
    process_name_search,
    main_menu_button,
    handle_participant_selection,
    SearchStates
)
from src.bot.handlers.edit_participant_handlers import (
    show_participant_edit_menu,
    handle_field_edit_selection,
    handle_text_field_input,
    handle_button_field_selection,
    cancel_editing,
    save_changes,
    EditStates
)

logger = logging.getLogger(__name__)


def get_search_conversation_handler() -> ConversationHandler:
    """
    Create and configure the integrated search and editing conversation handler.
    
    This handler manages both search and editing workflows in a single conversation
    to maintain seamless user experience. While this creates some architectural coupling,
    it ensures proper state management and data flow between search and editing phases.
    
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
    
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command)
        ],
        states={
            # === SEARCH STATES ===
            SearchStates.MAIN_MENU: [
                CallbackQueryHandler(search_button, pattern="^search$")
            ],
            SearchStates.WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_name_search)
            ],
            SearchStates.SHOWING_RESULTS: [
                CallbackQueryHandler(main_menu_button, pattern="^main_menu$"),
                CallbackQueryHandler(handle_participant_selection, pattern="^select_participant:")
            ],
            
            # === EDITING STATES ===
            # Note: These states handle participant editing after selection from search results
            # This integration maintains seamless UX and proper state/data management
            EditStates.FIELD_SELECTION: [
                CallbackQueryHandler(handle_field_edit_selection, pattern="^edit_field:"),
                CallbackQueryHandler(save_changes, pattern="^save_changes$"),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$"),
                CallbackQueryHandler(main_menu_button, pattern="^main_menu$")
            ],
            EditStates.TEXT_INPUT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_field_input),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$")
            ],
            EditStates.BUTTON_SELECTION: [
                CallbackQueryHandler(handle_button_field_selection, pattern="^select_value:"),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$")
            ],
            EditStates.CONFIRMATION: [
                CallbackQueryHandler(save_changes, pattern="^save_changes$"),
                CallbackQueryHandler(cancel_editing, pattern="^cancel_edit$")
            ]
        },
        fallbacks=[
            CommandHandler("start", start_command)
        ],
        per_message=False,  # Required for mixed handler types (CommandHandler + MessageHandler + CallbackQueryHandler)
        # Note: PTB may emit a warning about CallbackQueryHandler tracking, but this is expected
        # for mixed conversations and functionality works correctly as verified by tests
    )
    
    logger.info("Search conversation handler configured successfully")
    return conversation_handler