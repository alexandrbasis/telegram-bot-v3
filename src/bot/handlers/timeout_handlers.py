"""
Conversation timeout handlers for the Telegram bot.

Provides functionality to handle conversation timeouts with Russian
messages and main menu recovery options.
"""

import logging
from typing import Optional

from telegram import Update
from telegram.ext import (
    CallbackContext,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from src.bot.keyboards.search_keyboards import get_main_menu_keyboard

logger = logging.getLogger(__name__)


async def handle_conversation_timeout(
    update: Optional[Update], context: CallbackContext
) -> int:
    """
    Handle conversation timeout by showing Russian timeout message and main menu.

    This function is called when a conversation times out due to user inactivity.
    It displays a Russian timeout message and provides the main menu keyboard
    for session recovery.

    Args:
        update: The update that triggered the timeout (may be None)
        context: The callback context

    Returns:
        ConversationHandler.END to terminate the conversation
    """
    logger.info("Handling conversation timeout")

    # Handle edge case where update is None
    if update is None or update.effective_chat is None:
        logger.warning("Conversation timeout called with None update")
        return ConversationHandler.END

    # If this was triggered by a callback query, answer it to stop the spinner
    try:
        if update.callback_query:
            await update.callback_query.answer(text="⏰ Сессия истекла. Меню ниже.")
    except Exception as e:
        logger.debug(f"Failed to answer callback query on timeout: {e}")

    chat_id = update.effective_chat.id

    # Russian timeout message with emoji and recovery instruction
    timeout_message = (
        "⏰ Сессия истекла, начните заново\n\n"
        "🔄 Используйте главное меню ниже для продолжения работы"
    )

    # Send timeout message with main menu keyboard for recovery
    try:
        await context.bot.send_message(
            chat_id=chat_id, text=timeout_message, reply_markup=get_main_menu_keyboard()
        )
        logger.info(f"Sent timeout message to chat {chat_id}")
    except Exception as e:
        logger.error(f"Failed to send timeout message to chat {chat_id}: {e}")

    # End the conversation regardless of message send success
    return ConversationHandler.END


def get_timeout_recovery_handlers():
    """
    Standard timeout recovery handlers for ConversationHandler.TIMEOUT.

    Returns a list containing both a MessageHandler and a CallbackQueryHandler
    bound to `handle_conversation_timeout`, ensuring that after a timeout both
    regular messages and inline button taps (callback queries) trigger the
    recovery flow and that callback queries are answered to stop the spinner.

    Usage:
        ConversationHandler.TIMEOUT: [
            *get_timeout_recovery_handlers(),
        ]
    """
    return [
        MessageHandler(filters.ALL, handle_conversation_timeout),
        CallbackQueryHandler(handle_conversation_timeout),
    ]
