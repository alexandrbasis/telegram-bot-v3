"""
Handlers for CSV export functionality.

Provides command handlers for exporting participant data to CSV format
with admin-only access control and progress notifications.
"""

import asyncio
import logging
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telegram import Message, Update
from telegram.error import BadRequest, NetworkError, RetryAfter, TelegramError
from telegram.ext import ContextTypes

# Import conversation handler for redirection
from src.bot.handlers.export_conversation_handlers import start_export_selection
from src.services import service_factory
from src.services.user_interaction_logger import UserInteractionLogger
from src.utils.auth_utils import is_admin_user
from src.utils.export_utils import format_export_success_message

logger = logging.getLogger(__name__)


async def _cleanup_temp_file(file_path: str) -> None:
    """
    Clean up temporary file with proper error handling.

    Args:
        file_path: Path to the temporary file to delete
    """
    try:
        if file_path and Path(file_path).exists():
            Path(file_path).unlink()
            logger.debug(f"Successfully cleaned up temporary file: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete temporary file {file_path}: {e}")


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
        # The progress message that will be edited in place to reduce chat noise
        self.progress_message: Optional[Message] = None
        # Guard concurrent updates to avoid duplicate messages
        import asyncio

        self._lock = asyncio.Lock()

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
            # Ensure only one progress message operation at a time
            async with self._lock:
                self.last_update = now
                self.last_percentage = percentage

                progress_bar = self._create_progress_bar(percentage)
                text = (
                    f"📊 Экспорт данных...\n\n"
                    f"{progress_bar}\n"
                    f"Прогресс: {percentage}% ({current}/{total})"
                )

                try:
                    # Send once, then edit the same message to avoid spamming the chat
                    if self.progress_message is None:
                        self.progress_message = await self.message.reply_text(text)
                    else:
                        await self.progress_message.edit_text(text)
                except BadRequest as e:
                    # Ignore harmless "message is not modified"; log other cases
                    if "message is not modified" not in str(e).lower():
                        logger.warning(f"Failed to edit progress message: {e}")
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

    # Initialize interaction logger
    interaction_logger = UserInteractionLogger()

    logger.info(f"Export command received from user {username} (ID: {user_id})")

    # Log the export attempt
    interaction_logger.log_journey_step(
        user_id=user_id,
        step="export_command_initiated",
        context={"username": username, "command": "/export"},
    )

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
        logger.warning(
            f"Unauthorized export attempt by user {username} (ID: {user_id})"
        )

        # Log unauthorized access attempt
        interaction_logger.log_journey_step(
            user_id=user_id,
            step="export_access_denied",
            context={"reason": "insufficient_permissions", "is_admin": False},
        )

        await update.message.reply_text(
            "🚫 У вас нет прав для выполнения этой команды.\n"
            "Только администраторы могут экспортировать данные."
        )
        return

    # Send initial message
    await update.message.reply_text(
        "🔄 Начинаю экспорт данных участников...\n" "Это может занять некоторое время."
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
        if not await export_service.is_within_telegram_limit():
            estimated_size_mb = await export_service.estimate_file_size() / (
                1024 * 1024
            )
            await update.message.reply_text(
                f"⚠️ Предупреждение: Файл может превышать лимит Telegram (50MB).\n"
                f"Приблизительный размер: {estimated_size_mb:.1f}MB\n"
                f"Попробую отправить, но возможна ошибка."
            )

        # Export data to CSV
        csv_data = await export_service.export_to_csv_async()

        # Check if data is empty
        if not csv_data or csv_data.strip() == "":
            await update.message.reply_text(
                "📭 Нет данных для экспорта.\n" "База данных участников пуста."
            )
            return

        # Create temporary file
        temp_file_path = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".csv",
                prefix=(
                    f"participants_export_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
                ),
                delete=False,
                # Write with UTF-8 BOM to ensure Excel correctly detects encoding
                encoding="utf-8-sig",
            ) as temp_file:
                temp_file.write(csv_data)
                temp_file_path = temp_file.name
        except Exception as e:
            logger.error(f"Failed to create temporary file for user {user_id}: {e}")
            await update.message.reply_text(
                "❌ Ошибка при создании файла для экспорта\n\n"
                "Попробуйте повторить команду позже или обратитесь к администратору."
            )
            return

        try:
            # Send file to user with comprehensive error handling
            file_size_mb = Path(temp_file_path).stat().st_size / (1024 * 1024)

            # Check file size limit before attempting upload
            if file_size_mb > 50:
                await update.message.reply_text(
                    f"❌ Файл слишком большой для отправки через Telegram\n\n"
                    f"📁 Размер файла: {file_size_mb:.2f}MB\n"
                    f"📏 Лимит Telegram: 50MB\n\n"
                    f"💡 Рекомендации:\n"
                    f"• Попробуйте экспортировать меньше данных\n"
                    f"• Обратитесь к администратору для получения файла"
                )
                return

            max_retries = 3
            retry_delay = 2

            for attempt in range(max_retries):
                try:
                    with open(temp_file_path, "rb") as file:
                        # Prepare UTC timestamp for caption
                        ts_utc = datetime.now(timezone.utc).strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )

                        # Format success message with participant count
                        base_msg = (
                            "✅ Экспорт завершен успешно!\n\n"
                            "📊 Файл содержит данные всех участников"
                        )
                        caption = format_export_success_message(
                            base_message=base_msg,
                            file_size_mb=file_size_mb,
                            timestamp=f"{ts_utc} UTC",
                            csv_data=csv_data,
                            export_type=None,  # Legacy all-participants export - no specific type
                        )

                        await update.message.reply_document(
                            document=file,
                            filename=(
                                f"participants_"
                                f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                            ),
                            caption=caption,
                        )

                    logger.info(
                        f"Export completed successfully for user {username} "
                        f"(ID: {user_id}). File size: {file_size_mb:.2f}MB"
                    )

                    # Log successful export
                    interaction_logger.log_journey_step(
                        user_id=user_id,
                        step="export_completed_successfully",
                        context={
                            "file_size_mb": round(file_size_mb, 2),
                            "delivery_method": "telegram_document",
                            "attempt": attempt + 1,
                        },
                    )
                    break  # Success, exit retry loop

                except RetryAfter as e:
                    if attempt < max_retries - 1:
                        wait_time = e.retry_after + retry_delay
                        logger.warning(
                            f"Telegram rate limit hit, waiting {wait_time}s before "
                            f"retry {attempt + 1}/{max_retries}"
                        )
                        await update.message.reply_text(
                            f"⏳ Telegram временно ограничивает загрузки\n"
                            f"Повторная попытка через {wait_time} секунд..."
                        )
                        await asyncio.sleep(wait_time)
                    else:
                        raise

                except BadRequest as e:
                    error_message = str(e).lower()
                    error_type = "unknown_bad_request"

                    if (
                        "file too large" in error_message
                        or "entity too large" in error_message
                    ):
                        error_type = "file_too_large"
                        await update.message.reply_text(
                            f"❌ Файл слишком большой для Telegram\n\n"
                            f"📁 Размер: {file_size_mb:.2f}MB\n"
                            f"🚫 Ошибка: {str(e)}\n\n"
                            f"Попробуйте уменьшить объем экспортируемых данных."
                        )
                    elif "invalid file" in error_message:
                        error_type = "invalid_file_format"
                        await update.message.reply_text(
                            f"❌ Ошибка формата файла\n\n"
                            f"🚫 Детали: {str(e)}\n\n"
                            f"Попробуйте повторить экспорт."
                        )
                    else:
                        await update.message.reply_text(
                            f"❌ Ошибка при отправке файла\n\n"
                            f"🚫 Причина: {str(e)}\n\n"
                            f"Попробуйте повторить экспорт позже."
                        )

                    # Log error details
                    interaction_logger.log_missing_response(
                        user_id=user_id,
                        button_data="export_command",
                        error_type=error_type,
                        error_message=f"BadRequest: {str(e)}",
                    )

                    logger.error(
                        f"BadRequest during file upload for user {user_id}: {e}"
                    )
                    return

                except NetworkError as e:
                    if attempt < max_retries - 1:
                        logger.warning(
                            f"Network error during file upload, retrying "
                            f"{attempt + 1}/{max_retries}: {e}"
                        )
                        await update.message.reply_text(
                            f"🌐 Проблемы с сетью, повторная попытка "
                            f"{attempt + 1}/{max_retries}..."
                        )
                        await asyncio.sleep(retry_delay * (attempt + 1))
                    else:
                        await update.message.reply_text(
                            "❌ Ошибка сети при отправке файла\n\n"
                            "🌐 Попробуйте повторить команду через несколько минут\n\n"
                            "Если проблема продолжается, обратитесь к администратору."
                        )
                        logger.error(
                            f"Persistent network error for user {user_id}: {e}"
                        )
                        return

                except TelegramError as e:
                    await update.message.reply_text(
                        f"❌ Ошибка Telegram API\n\n"
                        f"🚫 Детали: {str(e)}\n\n"
                        f"Попробуйте повторить экспорт через несколько минут."
                    )
                    logger.error(
                        f"Telegram API error during file upload for user {user_id}: {e}"
                    )
                    return

        finally:
            # Clean up temporary file - always execute
            await _cleanup_temp_file(temp_file_path)

    except Exception as e:
        logger.error(f"Export failed for user {username} (ID: {user_id}): {e}")
        await update.message.reply_text(
            "❌ Ошибка при экспорте данных.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору.\n\n"
            f"Детали ошибки: {str(e)}"
        )


async def handle_export_progress(message: Message, current: int, total: int) -> None:
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
        f"📊 Прогресс экспорта: {percentage}%\n" f"Обработано: {current} из {total}"
    )

    try:
        await message.reply_text(progress_text)
    except Exception as e:
        logger.warning(f"Failed to send progress notification: {e}")


async def handle_export_selection_redirect(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """
    Redirect export command to conversation flow.

    This function serves as a bridge between the old /export command handler
    and the new conversation-based export selection flow.

    Args:
        update: Telegram update object
        context: Telegram context object

    Returns:
        Conversation state from start_export_selection
    """
    # Simply delegate to the conversation handler
    return await start_export_selection(update, context)
