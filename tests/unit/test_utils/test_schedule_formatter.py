"""Tests for schedule formatter utilities."""

import datetime as dt

from src.models.schedule import ScheduleEntry
from src.utils.schedule_formatter import format_schedule_day


def _entry(day: dt.date, hour: int, minute: int, title: str, **kwargs) -> ScheduleEntry:
    return ScheduleEntry(
        date=day,
        start_time=dt.time(hour, minute),
        title=title,
        **kwargs,
    )


def test_format_schedule_day_orders_by_time_then_order():
    day = dt.date(2025, 11, 13)
    entries = [
        _entry(day, 10, 0, "Second", order=5),
        _entry(day, 9, 0, "First"),
        _entry(day, 10, 0, "Priority", order=1),
    ]

    text = format_schedule_day(day, entries)

    lines = text.splitlines()[2:]
    assert "09:00" in lines[0]
    assert "Priority" in lines[1]
    assert "Second" in lines[2]


def test_format_schedule_day_handles_empty_day():
    day = dt.date(2025, 11, 14)

    text = format_schedule_day(day, [])

    assert "Нет событий" in text


def test_format_schedule_day_includes_location_and_audience():
    day = dt.date(2025, 11, 15)
    entries = [
        _entry(
            day,
            8,
            30,
            "Служение",
            end_time=dt.time(9, 30),
            location="Главный зал",
            audience="Все",
            description="Прославление",
        )
    ]

    text = format_schedule_day(day, entries)

    assert "08:30–09:30" in text
    assert "Главный зал" in text
    assert "Все" in text
    assert "Прославление" in text
