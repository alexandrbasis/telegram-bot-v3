"""Handlers for the /help command providing bot usage guidance."""

import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.messages import get_help_message

logger = logging.getLogger(__name__)


async def handle_help_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Reply with comprehensive help text grouped by functional categories."""

    message = update.effective_message
    if not message:
        logger.warning("Received /help command without effective message")
        return

    help_text = get_help_message()
    await message.reply_text(help_text, disable_web_page_preview=True)
