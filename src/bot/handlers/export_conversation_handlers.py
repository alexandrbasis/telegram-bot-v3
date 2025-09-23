"""
Export conversation handlers for interactive export selection.

Implements conversation flow with state management for export type selection,
department filtering, and integration with export services through service factory.
"""

import asyncio
import logging
import tempfile
import warnings
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
)

from src.bot.handlers.export_states import ExportCallbackData, ExportStates
from src.bot.keyboards.export_keyboards import (
    get_department_selection_keyboard,
    get_export_selection_keyboard,
)
from src.models.participant import Department, Role
from src.services import service_factory
from src.services.user_interaction_logger import UserInteractionLogger
from src.utils.auth_utils import is_admin_user

logger = logging.getLogger(__name__)


async def start_export_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """
    Start export selection conversation.

    Validates admin access and shows export type selection menu.

    Args:
        update: Telegram update object
        context: Telegram context object

    Returns:
        Next conversation state or END if access denied
    """
    user_id = update.effective_user.id if update.effective_user else None
    username = update.effective_user.username if update.effective_user else "Unknown"

    # Initialize interaction logger
    interaction_logger = UserInteractionLogger()

    logger.info(f"Export selection started by user {username} (ID: {user_id})")

    # Log the export selection attempt
    interaction_logger.log_journey_step(
        user_id=user_id,
        step="export_selection_initiated",
        context={"username": username, "command": "/export"},
    )

    # Get settings from context
    settings = context.bot_data.get("settings")
    if not settings:
        logger.error("Settings not found in bot data")
        await update.message.reply_text(
            "⚠️ Ошибка конфигурации. Обратитесь к администратору."
        )
        return ConversationHandler.END

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
        return ConversationHandler.END

    # Show export selection menu
    keyboard = get_export_selection_keyboard()
    await update.message.reply_text(
        "🔧 Выберите тип экспорта:\n\n"
        "📊 *Все участники* - полный экспорт базы данных\n"
        "👥 *Команда* - только участники с ролью TEAM\n"
        "🆕 *Кандидаты* - только участники с ролью CANDIDATE\n"
        "🏢 *По отделу* - участники конкретного отдела\n"
        "📖 *Bible Readers* - экспорт таблицы Bible Readers\n"
        "🎯 *ROE* - экспорт таблицы ROE",
        parse_mode="Markdown",
        reply_markup=keyboard,
    )

    return ExportStates.SELECTING_EXPORT_TYPE


async def handle_export_type_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """
    Handle export type selection from inline keyboard.

    Processes export types and either starts export or shows department selection.

    Args:
        update: Telegram update object
        context: Telegram context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else None
    callback_data = query.data

    # Initialize interaction logger
    interaction_logger = UserInteractionLogger()

    logger.info(f"Export type selected: {callback_data} by user {user_id}")

    # Log the selection
    interaction_logger.log_journey_step(
        user_id=user_id,
        step="export_type_selected",
        context={"callback_data": callback_data},
    )

    # Handle department selection flow
    if callback_data == ExportCallbackData.EXPORT_BY_DEPARTMENT:
        keyboard = get_department_selection_keyboard()
        await query.edit_message_text(
            "🏢 Выберите отдел для экспорта:\n\n"
            "Будут экспортированы только участники выбранного отдела.",
            reply_markup=keyboard,
        )
        return ExportStates.SELECTING_DEPARTMENT

    # Handle direct export types
    await query.edit_message_text(
        "🔄 Начинаю экспорт данных...\n" "Это может занять некоторое время."
    )

    # Process the export based on type
    await _process_export_by_type(callback_data, query, context, user_id)

    return ConversationHandler.END


async def handle_department_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """
    Handle department selection from department keyboard.

    Processes department selection and starts filtered export.

    Args:
        update: Telegram update object
        context: Telegram context object

    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else None
    callback_data = query.data

    # Initialize interaction logger
    interaction_logger = UserInteractionLogger()

    # Handle back navigation
    if callback_data == ExportCallbackData.BACK_TO_EXPORT_SELECTION:
        keyboard = get_export_selection_keyboard()
        await query.edit_message_text(
            "🔧 Выберите тип экспорта:\n\n"
            "📊 *Все участники* - полный экспорт базы данных\n"
            "👥 *Команда* - только участники с ролью TEAM\n"
            "🆕 *Кандидаты* - только участники с ролью CANDIDATE\n"
            "🏢 *По отделу* - участники конкретного отдела\n"
            "📖 *Bible Readers* - экспорт таблицы Bible Readers\n"
            "🎯 *ROE* - экспорт таблицы ROE",
            parse_mode="Markdown",
            reply_markup=keyboard,
        )
        return ExportStates.SELECTING_EXPORT_TYPE

    # Parse department name
    department = ExportCallbackData.parse_department(callback_data)
    if not department:
        await query.edit_message_text("❌ Ошибка: неверный отдел выбран.")
        return ConversationHandler.END

    logger.info(f"Department selected: {department} by user {user_id}")

    # Log the department selection
    interaction_logger.log_journey_step(
        user_id=user_id,
        step="department_selected",
        context={"department": department},
    )

    await query.edit_message_text(
        f"🔄 Начинаю экспорт отдела '{department}'...\n"
        "Это может занять некоторое время."
    )

    # Process department export
    await _process_department_export(department, query, context, user_id)

    return ConversationHandler.END


async def cancel_export(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel export conversation.

    Ends the conversation and informs user of cancellation.

    Args:
        update: Telegram update object
        context: Telegram context object

    Returns:
        ConversationHandler.END
    """
    query = update.callback_query
    await query.answer()

    user_id = update.effective_user.id if update.effective_user else None

    # Initialize interaction logger
    interaction_logger = UserInteractionLogger()

    logger.info(f"Export cancelled by user {user_id}")

    # Log the cancellation
    interaction_logger.log_journey_step(
        user_id=user_id,
        step="export_cancelled",
        context={"reason": "user_cancelled"},
    )

    await query.edit_message_text(
        "❌ Экспорт отменён.\n\n"
        "Используйте команду /export для начала нового экспорта."
    )

    return ConversationHandler.END


async def _process_export_by_type(
    export_type: str, query, context: ContextTypes.DEFAULT_TYPE, user_id: Optional[int]
) -> None:
    """
    Process export based on selected type.

    Args:
        export_type: Export type callback data
        query: Telegram callback query
        context: Telegram context
        user_id: User ID for logging
    """
    try:
        # Create progress callback
        async def progress_callback(current: int, total: int):
            # Simplified progress update for conversation context
            if total > 0 and current % 50 == 0:  # Update every 50 items
                percentage = int((current / total) * 100)
                try:
                    await query.edit_message_text(
                        f"🔄 Экспорт в процессе: {percentage}%\n"
                        f"Обработано: {current} из {total}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress: {e}")

        # Get appropriate export service based on type
        if export_type == ExportCallbackData.EXPORT_ALL:
            export_service = service_factory.get_export_service(
                progress_callback=lambda c, t: asyncio.create_task(
                    progress_callback(c, t)
                )
            )
            csv_data = await export_service.export_to_csv_async()
            filename_prefix = "participants_all"

        elif export_type == ExportCallbackData.EXPORT_TEAM:
            export_service = service_factory.get_export_service(
                progress_callback=lambda c, t: asyncio.create_task(
                    progress_callback(c, t)
                )
            )
            csv_data = await export_service.get_participants_by_role_as_csv(Role.TEAM)
            filename_prefix = "participants_team"

        elif export_type == ExportCallbackData.EXPORT_CANDIDATES:
            export_service = service_factory.get_export_service(
                progress_callback=lambda c, t: asyncio.create_task(
                    progress_callback(c, t)
                )
            )
            csv_data = await export_service.get_participants_by_role_as_csv(
                Role.CANDIDATE
            )
            filename_prefix = "participants_candidates"

        elif export_type == ExportCallbackData.EXPORT_BIBLE_READERS:
            export_service = service_factory.get_bible_readers_export_service(
                progress_callback=lambda c, t: asyncio.create_task(
                    progress_callback(c, t)
                )
            )
            csv_data = await export_service.export_to_csv_async()
            filename_prefix = "bible_readers"

        elif export_type == ExportCallbackData.EXPORT_ROE:
            export_service = service_factory.get_roe_export_service(
                progress_callback=lambda c, t: asyncio.create_task(
                    progress_callback(c, t)
                )
            )
            csv_data = await export_service.export_to_csv_async()
            filename_prefix = "roe_sessions"

        else:
            await query.edit_message_text("❌ Неизвестный тип экспорта.")
            return

        # Send the file
        await _send_export_file(csv_data, filename_prefix, query, user_id)

    except Exception as e:
        logger.error(f"Export failed for user {user_id}: {e}")
        await query.edit_message_text(
            "❌ Ошибка при экспорте данных.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )


async def _process_department_export(
    department: str, query, context: ContextTypes.DEFAULT_TYPE, user_id: Optional[int]
) -> None:
    """
    Process department-specific export.

    Args:
        department: Department name
        query: Telegram callback query
        context: Telegram context
        user_id: User ID for logging
    """
    try:
        # Create progress callback
        async def progress_callback(current: int, total: int):
            if (
                total > 0 and current % 25 == 0
            ):  # Update every 25 items for smaller datasets
                percentage = int((current / total) * 100)
                try:
                    await query.edit_message_text(
                        f"🔄 Экспорт отдела '{department}': {percentage}%\n"
                        f"Обработано: {current} из {total}"
                    )
                except Exception as e:
                    logger.warning(f"Failed to update progress: {e}")

        # Get participant export service with department filtering
        export_service = service_factory.get_export_service(
            progress_callback=lambda c, t: asyncio.create_task(progress_callback(c, t))
        )
        csv_data = await export_service.get_participants_by_department_as_csv(
            Department(department)
        )

        # Send the file
        filename_prefix = f"participants_{department.lower()}"
        await _send_export_file(csv_data, filename_prefix, query, user_id)

    except Exception as e:
        logger.error(f"Department export failed for user {user_id}: {e}")
        await query.edit_message_text(
            f"❌ Ошибка при экспорте отдела '{department}'.\n"
            "Пожалуйста, попробуйте позже или обратитесь к администратору."
        )


async def _send_export_file(
    csv_data: str, filename_prefix: str, query, user_id: Optional[int]
) -> None:
    """
    Send CSV file to user via Telegram.

    Args:
        csv_data: CSV content
        filename_prefix: Prefix for filename
        query: Telegram callback query
        user_id: User ID for logging
    """
    # Check if data is empty
    if not csv_data or csv_data.strip() == "":
        await query.edit_message_text(
            "📭 Нет данных для экспорта.\n" "Попробуйте выбрать другой тип экспорта."
        )
        return

    # Create temporary file
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            suffix=".csv",
            prefix=(
                f"{filename_prefix}_" f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_"
            ),
            delete=False,
            encoding="utf-8-sig",
        ) as temp_file:
            temp_file.write(csv_data)
            temp_file_path = temp_file.name

        # Send file
        file_size_mb = Path(temp_file_path).stat().st_size / (1024 * 1024)

        with open(temp_file_path, "rb") as file:
            ts_utc = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

            await query.message.reply_document(
                document=file,
                filename=(
                    f"{filename_prefix}_"
                    f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                ),
                caption=(
                    f"✅ Экспорт завершен успешно!\n\n"
                    f"📁 Размер файла: {file_size_mb:.2f}MB\n"
                    f"📅 Дата экспорта: {ts_utc} UTC"
                ),
            )

        # Update final message
        await query.edit_message_text(
            "✅ Экспорт завершён!\n" "📁 Файл отправлен выше."
        )

        # Log successful export
        interaction_logger = UserInteractionLogger()
        interaction_logger.log_journey_step(
            user_id=user_id,
            step="export_completed_successfully",
            context={
                "file_size_mb": round(file_size_mb, 2),
                "filename_prefix": filename_prefix,
                "delivery_method": "telegram_document",
            },
        )

        logger.info(
            f"Export completed successfully for user {user_id}. "
            f"File size: {file_size_mb:.2f}MB, Type: {filename_prefix}"
        )

    except Exception as e:
        logger.error(f"Failed to send export file for user {user_id}: {e}")
        await query.edit_message_text(
            "❌ Ошибка при отправке файла.\n" "Попробуйте повторить экспорт."
        )

    finally:
        # Clean up temporary file
        if temp_file_path and Path(temp_file_path).exists():
            try:
                Path(temp_file_path).unlink()
                logger.debug(f"Cleaned up temporary file: {temp_file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete temporary file {temp_file_path}: {e}")


def get_export_conversation_handler() -> ConversationHandler:
    """
    Get configured export conversation handler.

    Returns:
        ConversationHandler with states, entry points, and fallbacks
    """
    # Suppress PTBUserWarning during handler construction due to mixed handler types
    try:
        from telegram.warnings import PTBUserWarning  # type: ignore
    except Exception:  # pragma: no cover - fallback for PTB variants
        try:
            from telegram._utils.warnings import PTBUserWarning  # type: ignore
        except Exception:
            PTBUserWarning = Warning  # type: ignore

    with warnings.catch_warnings():
        warnings.simplefilter("ignore", PTBUserWarning)

        return ConversationHandler(
            entry_points=[
                CommandHandler("export", start_export_selection),
            ],
            states={
                ExportStates.SELECTING_EXPORT_TYPE: [
                    CallbackQueryHandler(
                        handle_export_type_selection,
                        pattern=f"^({ExportCallbackData.EXPORT_ALL}|"
                        f"{ExportCallbackData.EXPORT_TEAM}|"
                        f"{ExportCallbackData.EXPORT_CANDIDATES}|"
                        f"{ExportCallbackData.EXPORT_BY_DEPARTMENT}|"
                        f"{ExportCallbackData.EXPORT_BIBLE_READERS}|"
                        f"{ExportCallbackData.EXPORT_ROE})$",
                    ),
                ],
                ExportStates.SELECTING_DEPARTMENT: [
                    CallbackQueryHandler(
                        handle_department_selection,
                        pattern=(
                            f"^(export:department:.+|"
                            f"{ExportCallbackData.BACK_TO_EXPORT_SELECTION})$"
                        ),
                    ),
                ],
                ExportStates.PROCESSING_EXPORT: [
                    # This state handles the export process, no additional handlers needed
                    # The export process ends the conversation automatically
                ],
            },
            fallbacks=[
                CallbackQueryHandler(
                    cancel_export, pattern=f"^{ExportCallbackData.CANCEL}$"
                ),
            ],
            # Keep default mixed-handler behavior; warnings suppressed above
            per_message=False,
        )
