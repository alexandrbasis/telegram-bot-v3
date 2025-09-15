"""
Handlers for CSV export functionality.

Provides command handlers for exporting participant data to CSV format
with admin-only access control and progress notifications.
"""

import asyncio
import logging
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Optional

from telegram import Message, Update
from telegram.ext import ContextTypes

from src.config.settings import Settings
from src.services import service_factory
from src.utils.auth_utils import is_admin_user

logger = logging.getLogger(__name__)


class ExportProgressTracker:
    """Track and throttle export progress notifications."""

    def __init__(self, message: Message, min_interval_seconds: float = 2.0):
        """
        Initialize progress tracker.

        Args:
            message: Telegram message to reply to
            min_interval_seconds: Minimum seconds between progress updates
        """
        self.message = message
        self.min_interval = min_interval_seconds
        self.last_update = None
        self.last_percentage = -1

    async def update(self, current: int, total: int) -> None:
        """
        Send throttled progress update.

        Args:
            current: Current progress count
            total: Total items count
        """
        if total == 0:
            percentage = 0
        else:
            percentage = int((current / total) * 100)

        # Throttle updates
        now = datetime.now()
        should_update = (
            self.last_update is None
            or (now - self.last_update).total_seconds() >= self.min_interval
            or percentage == 100
            or (percentage - self.last_percentage) >= 10  # Update every 10%
        )

        if should_update:
            self.last_update = now
            self.last_percentage = percentage

            progress_bar = self._create_progress_bar(percentage)
            message = (
                f"📊 Экспорт данных...\n\n"
                f"{progress_bar}\n"
                f"Прогресс: {percentage}% ({current}/{total})"
            )

            try:
                await self.message.reply_text(message)
            except Exception as e:
                logger.warning(f"Failed to send progress update: {e}")

    def _create_progress_bar(self, percentage: int) -> str:
        """Create visual progress bar."""
        filled = int(percentage / 10)
        empty = 10 - filled
        return "▓" * filled + "░" * empty


async def handle_export_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle /export command for CSV data export.

    Validates admin access, exports participant data to CSV,
    and sends the file to the user with progress notifications.

    Args:
        update: Telegram update object
        context: Telegram context object
    """
    user_id = update.effective_user.id if update.effective_user else None
    username = update.effective_user.username if update.effective_user else "Unknown"

    logger.info(f"Export command received from user {username} (ID: {user_id})")

    # Get settings from context
    settings = context.bot_data.get("settings")
    if not settings:
        logger.error("Settings not found in bot data")
        await update.message.reply_text(
            "⚠️ Ошибка конфигурации. Обратитесь к администратору."
        )
        return

    # Check admin access
    if not is_admin_user(user_id, settings):
        logger.warning(f"Unauthorized export attempt by user {username} (ID: {user_id})")
        await update.message.reply_text(
            "🚫 У вас нет прав для выполнения этой команды.\n"
            "Только администраторы могут экспортировать данные."
        )
        return

    # Send initial message
    initial_message = await update.message.reply_text(
        "🔄 Начинаю экспорт данных участников...\n"
        "Это может занять некоторое время."
    )

    try:
        # Create progress tracker
        progress_tracker = ExportProgressTracker(update.message)

        # Create progress callback
        async def progress_callback(current: int, total: int):
            await progress_tracker.update(current, total)

        # Get export service
        export_service = service_factory.get_export_service(
            progress_callback=lambda c, t: asyncio.create_task(progress_callback(c, t))
        )

        # Check estimated file size
        if not export_service.is_within_telegram_limit():
            estimated_size_mb = export_service.estimate_file_size() / (1024 * 1024)
            await update.message.reply_text(
                f"⚠️ Предупреждение: Файл может превышать лимит Telegram (50MB).\n"
                f"Приблизительный размер: {estimated_size_mb:.1f}MB\n"
                f"Попробую отправить, но возможна ошибка."
            )

        # Export data to CSV
        csv_data = export_service.export_to_csv()

        # Check if data is empty
        if not csv_data or csv_data.strip() == "":
            await update.message.reply_text(
                "📭 Нет данных для экспорта.\n"
                "База данных участников пуста."
            )
            return

        # Create temporary file
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            prefix=f"participants_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}_",
            delete=False,
            encoding="utf-8",
        ) as temp_file:
            temp_file.write(csv_data)
            temp_file_path = temp_file.name

        try:
            # Send file to user
            file_size_mb = Path(temp_file_path).stat().st_size / (1024 * 1024)
            await update.message.reply_document(
                document=open(temp_file_path, "rb"),
                filename=f"participants_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                caption=(
                    f"✅ Экспорт завершен успешно!\n\n"
                    f"📊 Файл содержит данные всех участников\n"
                    f"📁 Размер файла: {file_size_mb:.2f}MB\n"
                    f"📅 Дата экспорта: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                ),
            )

            logger.info(
                f"Export completed successfully for user {username} (ID: {user_id}). "
                f"File size: {file_size_mb:.2f}MB"
            )

        finally:
            # Clean up temporary file
            try:
                Path(temp_file_path).unlink()
            except Exception as e:
                logger.warning(f"Failed to delete temporary file: {e}")

    except Exception as e:
        logger.error(f"Export failed for user {username} (ID: {user_id}): {e}")
        await update.message.reply_text(
            "❌ Ошибка при экспорте данных.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.\n\n"
            f"Детали ошибки: {str(e)}"
        )


async def handle_export_progress(
    message: Message, current: int, total: int
) -> None:
    """
    Handle export progress notification.

    Sends formatted progress update to user.

    Args:
        message: Telegram message to reply to
        current: Current progress count
        total: Total items count
    """
    if total == 0:
        percentage = 0
    else:
        percentage = int((current / total) * 100)

    progress_text = (
        f"📊 Прогресс экспорта: {percentage}%\n"
        f"Обработано: {current} из {total}"
    )

    try:
        await message.reply_text(progress_text)
    except Exception as e:
        logger.warning(f"Failed to send progress notification: {e}")