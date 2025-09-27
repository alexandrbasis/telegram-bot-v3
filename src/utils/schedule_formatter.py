"""
Utilities to format schedule entries for Telegram output.
"""

from __future__ import annotations

import datetime as dt
from typing import Iterable, List

from src.models.schedule import ScheduleEntry


def format_time(t: dt.time) -> str:
    return t.strftime("%H:%M")


def format_schedule_day(date_value: dt.date, entries: Iterable[ScheduleEntry]) -> str:
    """Return markdown string for a day's schedule entries in RU format."""
    items: List[str] = []
    for e in sorted(
        list(entries),
        key=lambda x: (
            x.start_time,
            x.order if x.order is not None else 9999,
        ),
    ):
        time_part = format_time(e.start_time)
        if e.end_time:
            time_part += f"–{format_time(e.end_time)}"
        title = e.title
        details: List[str] = []
        if e.location:
            details.append(e.location)
        if e.audience:
            details.append(e.audience)
        if e.description:
            details.append(e.description)
        tail = f" — {' • '.join(details)}" if details else ""
        items.append(f"• {time_part} — {title}{tail}")

    header = f"📅 Расписание на {date_value.strftime('%d.%m.%Y')}"
    body = "\n".join(items) if items else "Нет событий на этот день."
    return f"{header}\n\n{body}"
