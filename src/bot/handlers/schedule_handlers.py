"""Handlers for /schedule command and callbacks."""

from __future__ import annotations

import datetime as dt
import logging
from typing import List, Optional

from telegram import Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler

from src.bot.keyboards.schedule import schedule_days_keyboard
from src.services.service_factory import get_schedule_service
from src.utils.schedule_formatter import format_schedule_day

logger = logging.getLogger(__name__)


SCHEDULE_DAYS: List[dt.date] = [
    dt.date(2025, 11, 13),
    dt.date(2025, 11, 14),
    dt.date(2025, 11, 15),
    dt.date(2025, 11, 16),
]

USER_DATA_LAST_DAY_KEY = "schedule:last_day"


async def handle_schedule_command(update: Update, context: CallbackContext) -> None:
    keyboard = schedule_days_keyboard(SCHEDULE_DAYS)
    context.user_data.pop(USER_DATA_LAST_DAY_KEY, None)
    await update.effective_message.reply_text(
        "Выберите день расписания:", reply_markup=keyboard
    )


async def handle_schedule_callback(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    if not query:
        return
    await query.answer()

    data = query.data or ""
    if data == "schedule:back":
        context.user_data.pop(USER_DATA_LAST_DAY_KEY, None)
        await query.edit_message_text(
            "Выберите день расписания:",
            reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
        )
        return
    if data == "schedule:refresh":
        last_day_iso: Optional[str] = context.user_data.get(USER_DATA_LAST_DAY_KEY)
        if not last_day_iso:
            await query.edit_message_text(
                "Выберите день расписания:",
                reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
            )
            return
        try:
            day = dt.date.fromisoformat(last_day_iso)
        except ValueError as e:
            logger.warning("Invalid cached date in refresh: %s", last_day_iso)
            context.user_data.pop(USER_DATA_LAST_DAY_KEY, None)
            await query.edit_message_text(
                "❌ Некорректная дата.",
                reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
            )
            return

        service = get_schedule_service()
        try:
            entries = await service.refresh_schedule_for_date(day)
        except Exception as e:
            logger.error("Schedule refresh failed: %s", e)
            await query.edit_message_text(
                "❌ Не удалось обновить расписание. Попробуйте позже.",
                reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
            )
            return

        entries = [e for e in entries if e.date == day and e.is_active]
        text = format_schedule_day(day, entries)
        await query.edit_message_text(
            text, reply_markup=schedule_days_keyboard(SCHEDULE_DAYS)
        )
        return

    if not data.startswith("schedule:"):
        return
    _, iso = data.split(":", 1)
    try:
        day = dt.date.fromisoformat(iso)
        # Validate date is within expected range
        if day not in SCHEDULE_DAYS:
            raise ValueError("Date outside schedule range")
    except (ValueError, TypeError) as e:
        logger.warning("Invalid date in callback: %s - %s", iso, e)
        await query.edit_message_text(
            "❌ Некорректная дата.",
            reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
        )
        return

    service = get_schedule_service()
    try:
        entries = await service.get_schedule_for_date(day)
    except Exception as e:
        logger.error("Schedule fetch failed: %s", e)
        await query.edit_message_text(
            "❌ Не удалось загрузить расписание. Попробуйте позже.",
            reply_markup=schedule_days_keyboard(SCHEDULE_DAYS),
        )
        return

    context.user_data[USER_DATA_LAST_DAY_KEY] = day.isoformat()

    # Filter by date to be safe
    entries = [e for e in entries if e.date == day and e.is_active]
    text = format_schedule_day(day, entries)
    await query.edit_message_text(
        text, reply_markup=schedule_days_keyboard(SCHEDULE_DAYS)
    )


def get_schedule_handlers() -> List:
    """Return PTB handlers for schedule feature."""
    return [
        CommandHandler("schedule", handle_schedule_command),
        CallbackQueryHandler(handle_schedule_callback, pattern=r"^schedule:.*"),
    ]
