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

    # Check if schedule feature is enabled from bot settings
    include_schedule = False
    if "settings" in context.bot_data:
        settings = context.bot_data["settings"]
        app_settings = getattr(settings, "application", None)
        if app_settings:
            include_schedule = getattr(app_settings, "enable_schedule_feature", False)

    help_text = get_help_message(include_schedule=include_schedule)
    await message.reply_text(help_text, disable_web_page_preview=True)
