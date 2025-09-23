"""Administrative command handlers."""

import logging
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from src.bot.handlers.auth_handlers import require_admin_access
from src.bot.messages import AccessRequestMessages
from src.config.settings import Settings
from src.models.user_access_request import AccessLevel
from src.services.access_request_service import AccessRequestService
from src.services.notification_service import NotificationService
from src.services.service_factory import get_user_access_repository
from src.services.user_interaction_logger import (
    is_user_interaction_logging_enabled,
    set_user_interaction_logging_enabled,
)
from src.utils.auth_utils import is_admin_user

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


# Access Request Management Handlers


@require_admin_access
async def requests_command_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /requests command to show pending access requests.

    Shows paginated list of pending requests with approve/deny buttons.
    """
    chat = update.effective_chat

    if not chat:
        return

    # Initialize service
    repository = get_user_access_repository()
    service = AccessRequestService(repository)

    # Get page from context (default to page 1)
    page = context.user_data.get("requests_page", 1)
    limit = 5
    offset = (page - 1) * limit

    try:
        # Get pending requests
        pending_requests = await service.get_pending_requests(
            limit=limit, offset=offset
        )

        if not pending_requests:
            if page == 1:
                message_text = AccessRequestMessages.NO_PENDING_REQUESTS
                keyboard = None
            else:
                # No requests on this page, go back to page 1
                context.user_data["requests_page"] = 1
                await requests_command_handler(update, context)
                return
        else:
            message_text = f"Ожидающие запросы на доступ (страница {page}):\n\n"

            # Create request list with buttons
            keyboard_buttons = []

            for i, request in enumerate(pending_requests):
                display_name = service.format_display_name(request)
                message_text += f"{offset + i + 1}. {display_name} "
                message_text += (
                    f"(@{request.telegram_username or 'no_username'} / "
                    f"{request.telegram_user_id})\n"
                )

                # Create approve/deny buttons for each request
                approve_btn = InlineKeyboardButton(
                    f"✅ Approve {display_name}",
                    callback_data=f"access:approve:{request.record_id}",
                )
                deny_btn = InlineKeyboardButton(
                    f"❌ Deny {display_name}",
                    callback_data=f"access:deny:{request.record_id}",
                )
                keyboard_buttons.extend([approve_btn, deny_btn])

            # Add navigation buttons
            nav_buttons = []
            if offset > 0:  # Previous page exists
                nav_buttons.append(
                    InlineKeyboardButton(
                        "⬅️ Назад", callback_data=f"requests:page:{page-1}"
                    )
                )
            if len(pending_requests) == limit:  # More pages might exist
                nav_buttons.append(
                    InlineKeyboardButton(
                        "➡️ Далее", callback_data=f"requests:page:{page+1}"
                    )
                )

            # Add refresh button
            nav_buttons.append(
                InlineKeyboardButton("🔄 Обновить", callback_data="requests:refresh")
            )

            # Organize keyboard layout (2 buttons per row for requests,
            # navigation row at bottom)
            keyboard_layout = [
                keyboard_buttons[i : i + 2] for i in range(0, len(keyboard_buttons), 2)
            ]
            if nav_buttons:
                keyboard_layout.append(nav_buttons)

            keyboard = InlineKeyboardMarkup(keyboard_layout)

        await context.bot.send_message(
            chat_id=chat.id, text=message_text, reply_markup=keyboard
        )

    except Exception as e:
        logger.error(f"Error handling requests command: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text=AccessRequestMessages.LOAD_REQUESTS_ERROR_RU,
        )


async def access_callback_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle callback queries for access request actions.

    Handles approve, deny, and navigation callbacks.
    """
    query = update.callback_query
    user = update.effective_user
    chat = update.effective_chat

    if not query or not user or not chat:
        return

    await query.answer()

    # Parse callback data
    try:
        callback_parts = query.data.split(":")
        if len(callback_parts) < 2:
            await query.edit_message_text("Неверный формат команды.")
            return

        action = callback_parts[0]
        action_type = callback_parts[1]

        # Initialize service
        repository = get_user_access_repository()
        service = AccessRequestService(repository)

        if action == "access":
            # Handle approve/deny actions
            if len(callback_parts) != 3:
                await query.edit_message_text("Неверный формат команды доступа.")
                return

            record_id = callback_parts[2]
            await handle_access_action(
                query, service, action_type, record_id, user.username or str(user.id)
            )

        elif action == "requests":
            # Handle navigation actions
            if action_type == "page":
                if len(callback_parts) == 3:
                    page = int(callback_parts[2])
                    context.user_data["requests_page"] = page
                    # Create new update for the requests command
                    await requests_command_handler(update, context)
                    await query.delete_message()
            elif action_type == "refresh":
                # Refresh current page
                await requests_command_handler(update, context)
                await query.delete_message()

    except Exception as e:
        logger.error(f"Error handling access callback: {e}")
        await query.edit_message_text("Произошла ошибка при обработке команды.")


async def handle_access_action(
    query,
    service: AccessRequestService,
    action_type: str,
    record_id: str,
    admin_username: str,
) -> None:
    """
    Handle individual access approve/deny actions.

    Args:
        query: Callback query object
        service: Access request service
        action_type: "approve" or "deny"
        record_id: Record ID of the request
        admin_username: Username of the admin performing the action
    """
    try:
        # Find the request by scanning all pending requests
        # This is inefficient but works with current repository interface
        pending_requests = await service.get_pending_requests(
            limit=100
        )  # Reasonable limit
        target_request = None

        for request in pending_requests:
            if request.record_id == record_id:
                target_request = request
                break

        if not target_request:
            await query.edit_message_text("Запрос не найден или уже обработан.")
            return

        if action_type == "approve":
            # Approve with default VIEWER level
            approved_request = await service.approve_request(
                target_request, AccessLevel.VIEWER, admin_username
            )

            await query.edit_message_text(
                f"✅ Запрос от {service.format_display_name(target_request)} "
                f"одобрен с уровнем доступа {approved_request.access_level.value}."
            )

            # Notify the user
            try:
                settings = Settings()
                notification_service = NotificationService(
                    bot=query.bot, admin_ids=settings.telegram.admin_user_ids
                )
                success = await notification_service.notify_user_decision(
                    user_id=target_request.telegram_user_id,
                    approved=True,
                    access_level=approved_request.access_level,
                    language="ru",
                )
                if not success:
                    logger.warning(
                        f"Failed to notify user {target_request.telegram_user_id} "
                        f"about approval"
                    )
            except Exception as e:
                logger.error(f"Error notifying user about approval: {e}")

            logger.info(f"Request {record_id} approved by {admin_username}")

        elif action_type == "deny":
            # Deny the request
            denied_request = await service.deny_request(target_request, admin_username)

            await query.edit_message_text(
                f"❌ Запрос от {service.format_display_name(target_request)} "
                f"отклонен администратором {denied_request.reviewed_by}."
            )

            # Notify the user
            try:
                settings = Settings()
                notification_service = NotificationService(
                    bot=query.bot, admin_ids=settings.telegram.admin_user_ids
                )
                success = await notification_service.notify_user_decision(
                    user_id=target_request.telegram_user_id,
                    approved=False,
                    language="ru",
                )
                if not success:
                    logger.warning(
                        f"Failed to notify user {target_request.telegram_user_id} "
                        f"about denial"
                    )
            except Exception as e:
                logger.error(f"Error notifying user about denial: {e}")

            logger.info(f"Request {record_id} denied by {admin_username}")

        else:
            await query.edit_message_text("Неизвестное действие.")

    except Exception as e:
        logger.error(f"Error handling access action {action_type} for {record_id}: {e}")
        await query.edit_message_text("Произошла ошибка при обработке запроса.")


@require_admin_access
async def list_approved_users_handler(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle command to list approved users.

    Shows list of users with approved access for admin review.
    """
    chat = update.effective_chat

    if not chat:
        return

    # Initialize service
    repository = get_user_access_repository()
    service = AccessRequestService(repository)

    try:
        # Get approved requests
        approved_requests = await service.get_approved_requests(limit=20)

        if not approved_requests:
            message_text = "Нет одобренных пользователей."
        else:
            message_text = "Одобренные пользователи:\n\n"

            for i, request in enumerate(approved_requests):
                display_name = service.format_display_name(request)
                message_text += f"{i + 1}. {display_name} "
                message_text += f"(@{request.telegram_username or 'no_username'}) - "
                message_text += f"{request.access_level.value}\n"

        await context.bot.send_message(chat_id=chat.id, text=message_text)

    except Exception as e:
        logger.error(f"Error listing approved users: {e}")
        await context.bot.send_message(
            chat_id=chat.id, text="Произошла ошибка при загрузке списка пользователей."
        )
