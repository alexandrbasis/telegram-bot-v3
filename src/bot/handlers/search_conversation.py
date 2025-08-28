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
    SearchStates
)

logger = logging.getLogger(__name__)


def get_search_conversation_handler() -> ConversationHandler:
    """
    Create and configure the search conversation handler.
    
    Sets up the complete conversation flow:
    - Entry point: /start command
    - States: MAIN_MENU, WAITING_FOR_NAME, SHOWING_RESULTS
    - Fallbacks: /start to restart conversation
    
    Returns:
        Configured ConversationHandler instance
    """
    logger.info("Setting up search conversation handler")
    
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start_command)
        ],
        states={
            SearchStates.MAIN_MENU: [
                CallbackQueryHandler(search_button, pattern="^search$")
            ],
            SearchStates.WAITING_FOR_NAME: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, process_name_search)
            ],
            SearchStates.SHOWING_RESULTS: [
                CallbackQueryHandler(main_menu_button, pattern="^main_menu$")
            ]
        },
        fallbacks=[
            CommandHandler("start", start_command)
        ],
        per_message=False
    )
    
    logger.info("Search conversation handler configured successfully")
    return conversation_handler