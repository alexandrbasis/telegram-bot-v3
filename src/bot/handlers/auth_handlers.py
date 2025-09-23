"""
Authentication and access control handlers.

Handles user onboarding, access request submission, and access control
for bot features during the approval workflow.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

from src.services.access_request_service import AccessRequestService
from src.data.airtable.airtable_user_access_repo import AirtableUserAccessRepository
from src.data.airtable.airtable_client_factory import get_airtable_client
from src.models.user_access_request import AccessRequestStatus, AccessLevel


logger = logging.getLogger(__name__)


async def start_command_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle /start command with access control.

    Checks user's access status and either:
    - Welcomes approved users
    - Shows status for pending users
    - Creates new request for new users
    - Shows denial message for denied users
    """
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return

    # Initialize service
    airtable_client = get_airtable_client()
    repository = AirtableUserAccessRepository(airtable_client)
    service = AccessRequestService(repository)

    try:
        # Check existing access request
        existing_request = await service.get_request_by_user_id(user.id)

        if existing_request:
            if existing_request.status == AccessRequestStatus.APPROVED:
                # User is approved - show welcome message
                await context.bot.send_message(
                    chat_id=chat.id,
                    text=f"Добро пожаловать! Ваша роль: {existing_request.access_level.value}. "
                         f"Используйте /help для просмотра команд."
                )
            elif existing_request.status == AccessRequestStatus.PENDING:
                # User has pending request
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="Ваш запрос на доступ уже обрабатывается. Пожалуйста, подождите."
                )
            elif existing_request.status == AccessRequestStatus.DENIED:
                # User was denied
                await context.bot.send_message(
                    chat_id=chat.id,
                    text="К сожалению, в доступе отказано. "
                         "Если это ошибка, пожалуйста свяжитесь с администратором."
                )
        else:
            # New user - submit access request
            await service.submit_request(
                telegram_user_id=user.id,
                telegram_username=user.username
            )

            await context.bot.send_message(
                chat_id=chat.id,
                text="Запрос на доступ принят. Мы уведомим вас, как только админ его обработает."
            )

            # TODO: In Step 3, this will trigger admin notification
            logger.info(f"New access request submitted by user {user.id} (@{user.username})")

    except Exception as e:
        logger.error(f"Error handling start command for user {user.id}: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text="Произошла ошибка при обработке запроса. Пожалуйста, попробуйте позже."
        )


async def check_user_access(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """
    Check if user has approved access to bot features.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        True if user has access, False otherwise
    """
    user = update.effective_user
    chat = update.effective_chat

    if not user or not chat:
        return False

    # Initialize service
    airtable_client = get_airtable_client()
    repository = AirtableUserAccessRepository(airtable_client)
    service = AccessRequestService(repository)

    try:
        # Check user's access request
        user_request = await service.get_request_by_user_id(user.id)

        if service.check_user_access(user_request):
            return True

        # User doesn't have access - send appropriate message
        if user_request is None:
            # No request exists
            await context.bot.send_message(
                chat_id=chat.id,
                text="Для использования этой функции необходимо одобрение администратора. "
                     "Используйте /start для запроса доступа."
            )
        elif user_request.status == AccessRequestStatus.PENDING:
            # Request is pending
            await context.bot.send_message(
                chat_id=chat.id,
                text="Ваш запрос на доступ обрабатывается. Пожалуйста, подождите одобрения администратора."
            )
        elif user_request.status == AccessRequestStatus.DENIED:
            # Request was denied
            await context.bot.send_message(
                chat_id=chat.id,
                text="Доступ к этой функции был отклонен. "
                     "Обратитесь к администратору для получения дополнительной информации."
            )

        return False

    except Exception as e:
        logger.error(f"Error checking access for user {user.id}: {e}")
        await context.bot.send_message(
            chat_id=chat.id,
            text="Произошла ошибка при проверке доступа. Пожалуйста, попробуйте позже."
        )
        return False


async def get_user_access_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> AccessLevel:
    """
    Get user's access level if approved.

    Args:
        update: Telegram update
        context: Bot context

    Returns:
        User's AccessLevel if approved, VIEWER as default
    """
    user = update.effective_user

    if not user:
        return AccessLevel.VIEWER

    # Initialize service
    airtable_client = get_airtable_client()
    repository = AirtableUserAccessRepository(airtable_client)
    service = AccessRequestService(repository)

    try:
        # Check user's access request
        user_request = await service.get_request_by_user_id(user.id)
        access_level = service.get_access_level(user_request)

        return access_level if access_level else AccessLevel.VIEWER

    except Exception as e:
        logger.error(f"Error getting access level for user {user.id}: {e}")
        return AccessLevel.VIEWER


def require_access(handler_func):
    """
    Decorator to require approved access for handler functions.

    Usage:
        @require_access
        async def my_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Handler logic here
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        has_access = await check_user_access(update, context)
        if has_access:
            return await handler_func(update, context, *args, **kwargs)
        # Access denied message already sent by check_user_access
        return None

    return wrapper


def require_admin_access(handler_func):
    """
    Decorator to require admin access for handler functions.

    Usage:
        @require_admin_access
        async def admin_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            # Admin handler logic here
    """
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user = update.effective_user
        chat = update.effective_chat

        if not user or not chat:
            return

        # Check if user has access first
        has_access = await check_user_access(update, context)
        if not has_access:
            return

        # Check if user has admin level access
        access_level = await get_user_access_level(update, context)
        if access_level == AccessLevel.ADMIN:
            return await handler_func(update, context, *args, **kwargs)

        # User doesn't have admin access
        await context.bot.send_message(
            chat_id=chat.id,
            text="Эта команда доступна только администраторам."
        )
        return None

    return wrapper