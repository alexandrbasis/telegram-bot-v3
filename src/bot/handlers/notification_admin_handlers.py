"""
Administrative command handlers for notification configuration.

Provides admin-only commands to control daily statistics notifications:
- /notifications - View status and enable/disable notifications
- /set_notification_time - Configure delivery time and timezone
- /test_stats - Trigger immediate test notification
"""

import logging
from datetime import time
from typing import List

import pytz
from telegram import Update
from telegram.ext import ContextTypes

from src.services.daily_notification_service import (
    DailyNotificationService,
    NotificationError,
)
from src.services.service_factory import get_participant_repository
from src.services.statistics_service import StatisticsService
from src.utils.auth_utils import is_admin_user

logger = logging.getLogger(__name__)


async def handle_notifications_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /notifications command for viewing and toggling notification status.

    Usage:
        /notifications - Show current status
        /notifications on - Enable notifications
        /notifications off - Disable notifications

    Args:
        update: Telegram update with command
        context: Bot context with settings
    """
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    # Get settings
    settings = context.bot_data.get("settings")
    if not settings:
        await message.reply_text(
            "⚠️ Настройки недоступны. Обратитесь к администратору системы."
        )
        return

    # Check admin permission
    if not is_admin_user(user.id, settings):
        await message.reply_text(
            "🚫 У вас нет прав для управления уведомлениями о статистике."
        )
        return

    # Parse arguments
    args: List[str] = context.args or []

    # No arguments - show current status
    if not args:
        status = (
            "✅ Включены"
            if settings.notification.daily_stats_enabled
            else "❌ Выключены"
        )
        status_message = (
            f"📊 Статус уведомлений: {status}\n\n"
            f"Время: {settings.notification.notification_time}\n"
            f"Часовой пояс: {settings.notification.timezone}\n\n"
            f"Используйте `/notifications on` или `/notifications off` для изменения"
        )
        await message.reply_text(status_message, parse_mode="Markdown")
        return

    # Handle enable/disable
    choice = args[0].lower()
    if choice in {"on", "enable", "true"}:
        was_enabled = settings.notification.daily_stats_enabled
        settings.notification.daily_stats_enabled = True
        logger.info(f"User {user.id} ({user.username}) enabled daily notifications")

        # Reschedule notification if scheduler is available
        scheduler = context.bot_data.get("notification_scheduler")
        if scheduler and not was_enabled:
            try:
                await scheduler.schedule_daily_notification()
                await message.reply_text(
                    "✅ Ежедневные уведомления о статистике включены и запланированы.\n"
                    f"Время отправки: {settings.notification.notification_time} "
                    f"({settings.notification.timezone})"
                )
            except Exception as e:
                logger.error(f"Failed to schedule notification: {e}", exc_info=True)
                await message.reply_text(
                    "⚠️ Уведомления включены, но не удалось запланировать отправку. "
                    "Проверьте логи."
                )
        else:
            await message.reply_text(
                "✅ Ежедневные уведомления о статистике включены.\n"
                f"Время отправки: {settings.notification.notification_time} "
                f"({settings.notification.timezone})"
            )

    elif choice in {"off", "disable", "false"}:
        was_enabled = settings.notification.daily_stats_enabled
        settings.notification.daily_stats_enabled = False
        logger.info(f"User {user.id} ({user.username}) disabled daily notifications")

        # Remove scheduled notification if scheduler is available
        scheduler = context.bot_data.get("notification_scheduler")
        if scheduler and was_enabled:
            try:
                await scheduler.remove_scheduled_notification()
                await message.reply_text(
                    "✅ Ежедневные уведомления о статистике выключены и "
                    "удалены из расписания."
                )
            except Exception as e:
                logger.error(f"Failed to remove notification: {e}", exc_info=True)
                await message.reply_text(
                    "⚠️ Уведомления выключены, но не удалось удалить из расписания. "
                    "Проверьте логи."
                )
        else:
            await message.reply_text(
                "✅ Ежедневные уведомления о статистике выключены."
            )

    else:
        await message.reply_text(
            "⚠️ Неизвестная опция. Используйте `/notifications on` или "
            "`/notifications off`.",
            parse_mode="Markdown",
        )


async def handle_set_notification_time_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /set_notification_time command for configuring delivery time and timezone.

    Usage:
        /set_notification_time HH:MM [timezone]
        Examples:
            /set_notification_time 14:30
            /set_notification_time 14:30 America/New_York

    Args:
        update: Telegram update with command
        context: Bot context with settings
    """
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    # Get settings
    settings = context.bot_data.get("settings")
    if not settings:
        await message.reply_text(
            "⚠️ Настройки недоступны. Обратитесь к администратору системы."
        )
        return

    # Check admin permission
    if not is_admin_user(user.id, settings):
        await message.reply_text("🚫 У вас нет прав для настройки времени уведомлений.")
        return

    # Parse arguments
    args: List[str] = context.args or []

    if not args:
        await message.reply_text(
            "ℹ️ Использование: `/set_notification_time HH:MM [timezone]`\n\n"
            f"Текущее время: {settings.notification.notification_time}\n"
            f"Часовой пояс: {settings.notification.timezone}\n\n"
            "Примеры:\n"
            "  • `/set_notification_time 14:30`\n"
            "  • `/set_notification_time 09:00 America/New_York`",
            parse_mode="Markdown",
        )
        return

    # Parse and validate time
    time_str = args[0]
    try:
        # Validate time format (HH:MM)
        hour, minute = map(int, time_str.split(":"))
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Invalid time range")
        # Create time object to validate
        _ = time(hour=hour, minute=minute)
    except (ValueError, AttributeError):
        await message.reply_text(
            "⚠️ Неверный формат времени. Используйте формат HH:MM (например, 14:30)."
        )
        return

    # Parse and validate timezone if provided
    timezone_str = settings.notification.timezone
    if len(args) > 1:
        timezone_str = args[1]
        try:
            _ = pytz.timezone(timezone_str)
        except pytz.UnknownTimeZoneError:
            await message.reply_text(
                f"⚠️ Неизвестный часовой пояс: {timezone_str}\n\n"
                "Примеры правильных часовых поясов:\n"
                "  • Europe/Moscow\n"
                "  • America/New_York\n"
                "  • Asia/Tokyo"
            )
            return

    # Update settings
    settings.notification.notification_time = time_str
    settings.notification.timezone = timezone_str

    logger.info(
        f"User {user.id} ({user.username}) set notification time to "
        f"{time_str} {timezone_str}"
    )

    # Reschedule notification if enabled and scheduler is available
    scheduler = context.bot_data.get("notification_scheduler")
    if scheduler and settings.notification.daily_stats_enabled:
        try:
            await scheduler.reschedule_notification()
            await message.reply_text(
                f"✅ Время уведомлений обновлено и перепланировано:\n"
                f"Время: {time_str}\n"
                f"Часовой пояс: {timezone_str}\n\n"
                f"Изменения вступили в силу немедленно."
            )
        except Exception as e:
            logger.error(f"Failed to reschedule notification: {e}", exc_info=True)
            await message.reply_text(
                f"✅ Время уведомлений обновлено:\n"
                f"Время: {time_str}\n"
                f"Часовой пояс: {timezone_str}\n\n"
                f"⚠️ Не удалось перепланировать уведомления. Проверьте логи."
            )
    else:
        # Construct message with conditional note about disabled state
        disabled_note = (
            "ℹ️ Уведомления в данный момент выключены."
            if not settings.notification.daily_stats_enabled
            else ""
        )
        await message.reply_text(
            f"✅ Время уведомлений обновлено:\n"
            f"Время: {time_str}\n"
            f"Часовой пояс: {timezone_str}\n\n"
            f"{disabled_note}"
        )


async def handle_test_stats_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /test_stats command for sending immediate test notification.

    Triggers an immediate statistics notification to verify configuration
    without waiting for scheduled time.

    Args:
        update: Telegram update with command
        context: Bot context with settings
    """
    message = update.effective_message
    user = update.effective_user
    if message is None or user is None:
        return

    # Get settings
    settings = context.bot_data.get("settings")
    if not settings:
        await message.reply_text(
            "⚠️ Настройки недоступны. Обратитесь к администратору системы."
        )
        return

    # Check admin permission
    if not is_admin_user(user.id, settings):
        await message.reply_text(
            "🚫 У вас нет прав для тестирования уведомлений о статистике."
        )
        return

    # Send processing message
    await message.reply_text("⏳ Отправляю тестовое уведомление...")

    try:
        logger.info(
            f"User {user.id} ({user.username}) requested test statistics notification"
        )

        # Create services (same pattern as in main.py)
        repository = get_participant_repository()
        statistics_service = StatisticsService(repository=repository)
        notification_service = DailyNotificationService(
            bot=context.bot, statistics_service=statistics_service
        )

        # Send notification to requesting admin
        await notification_service.send_daily_statistics(user.id)

        logger.info(f"Test notification sent successfully to user {user.id}")
        await message.reply_text(
            "✅ Тестовое уведомление отправлено успешно!\n"
            "Проверьте сообщение со статистикой выше."
        )

    except NotificationError as e:
        logger.error(
            f"Failed to send test notification for user {user.id}: {e}",
            exc_info=True,
        )
        await message.reply_text(
            "⚠️ Ошибка при отправке уведомления.\n"
            "Проверьте логи для получения подробной информации."
        )
    except Exception as e:
        logger.error(
            f"Unexpected error sending test notification for user {user.id}: {e}",
            exc_info=True,
        )
        await message.reply_text(
            "⚠️ Произошла непредвиденная ошибка при отправке уведомления."
        )
