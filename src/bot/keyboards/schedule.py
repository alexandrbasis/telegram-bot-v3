"""Inline keyboards for schedule selection and actions."""

from __future__ import annotations

from datetime import date
from typing import List

from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def _date_label(d: date) -> str:
# Russian month abbreviations
RUSSIAN_MONTHS = (
    "янв", "фев", "мар", "апр", "май", "июн",
    "июл", "авг", "сен", "окт", "ноя", "дек"
)

def _date_label(d: date) -> str:
    """Format date as 'DD mon' in Russian."""
    return f"{d.day:02d} {RUSSIAN_MONTHS[d.month-1]}"
    return f"{d.day:02d} {months[d.month-1]}"


def schedule_days_keyboard(days: List[date]) -> InlineKeyboardMarkup:
    buttons: List[List[InlineKeyboardButton]] = []
    row: List[InlineKeyboardButton] = []
    for d in days:
        row.append(
            InlineKeyboardButton(
                _date_label(d), callback_data=f"schedule:{d.isoformat()}"
            )
        )
        if len(row) == 2:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    # Action row
    buttons.append(
        [
            InlineKeyboardButton("🔄 Обновить", callback_data="schedule:refresh"),
            InlineKeyboardButton("🔙 Назад", callback_data="schedule:back"),
        ]
    )

    return InlineKeyboardMarkup(buttons)
