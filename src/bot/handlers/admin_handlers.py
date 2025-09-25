"""Administrative command handlers."""

import logging
from typing import List

from telegram import Update
from telegram.ext import ContextTypes

from src.services.user_interaction_logger import (
    is_user_interaction_logging_enabled,
    set_user_interaction_logging_enabled,
)
from src.utils.auth_utils import invalidate_role_cache, is_admin_user

logger = logging.getLogger(__name__)


async def handle_logging_toggle_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /logging on|off admin command to toggle interaction logging."""
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    settings = context.bot_data.get("settings")
    if not settings:
        await message.reply_text(
            "⚠️ Настройки недоступны. Обратитесь к администратору системы."
        )
        return

    if not is_admin_user(user.id, settings):
        await message.reply_text(
            "🚫 У вас нет прав для управления логированием взаимодействий."
        )
        return

    args: List[str] = context.args or []
    if not args:
        status = "включено" if is_user_interaction_logging_enabled() else "выключено"
        await message.reply_text(
            "ℹ️ Логирование взаимодействий сейчас {}.\n"
            "Используйте `/logging on` или `/logging off`".format(status),
            parse_mode="Markdown",
        )
        return

    choice = args[0].lower()
    if choice in {"on", "enable", "true"}:
        set_user_interaction_logging_enabled(True)
        logger.info("User %s (%s) enabled interaction logging", user.id, user.username)
        await message.reply_text("✅ Логирование взаимодействий включено.")
    elif choice in {"off", "disable", "false"}:
        set_user_interaction_logging_enabled(False)
        logger.info("User %s (%s) disabled interaction logging", user.id, user.username)
        await message.reply_text("✅ Логирование взаимодействий отключено.")
    else:
        await message.reply_text(
            "⚠️ Неизвестная опция. Используйте `/logging on` или `/logging off`.",
            parse_mode="Markdown",
        )


async def handle_auth_refresh_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /auth_refresh admin command to refresh authorization cache."""
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    settings = context.bot_data.get("settings")
    if not settings:
        await message.reply_text(
            "⚠️ Настройки недоступны. Обратитесь к администратору системы."
        )
        return

    if not is_admin_user(user.id, settings):
        await message.reply_text("🚫 У вас нет прав для обновления кэша авторизации.")
        return

    # Clear the authorization cache
    invalidate_role_cache()

    logger.info(f"User {user.id} ({user.username}) cleared authorization cache")

    await message.reply_text(
        "✅ Кэш авторизации обновлен. Все роли пользователей будут "
        "перезагружены при следующем обращении к системе."
    )
