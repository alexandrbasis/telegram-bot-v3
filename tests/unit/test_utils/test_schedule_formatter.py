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


def _bullet_lines(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("• ")]


def test_format_schedule_day_orders_by_time_then_order():
    day = dt.date(2025, 11, 13)
    entries = [
        _entry(day, 10, 0, "Second", order=5),
        _entry(day, 9, 0, "First"),
        _entry(day, 10, 0, "Priority", order=1),
    ]

    text = format_schedule_day(day, entries)

    bullets = _bullet_lines(text)

    assert bullets[0].startswith("• 09:00")
    assert "First" in bullets[0]
    assert "Priority" in bullets[1]
    assert "Second" in bullets[2]


def test_format_schedule_day_handles_empty_day():
    day = dt.date(2025, 11, 14)

    text = format_schedule_day(day, [])

    assert "Нет событий" in text


def test_format_schedule_day_includes_day_label_sections_and_details():
    day = dt.date(2025, 11, 15)
    entries = [
        _entry(
            day,
            5,
            30,
            "Подъём",
            audience="Team",
            description="Раздел: 🕔 Утро\nНачало дня",
            day_label="День выпускного",
        ),
        _entry(
            day,
            6,
            0,
            "Молитва",
            audience="All",
        ),
        _entry(
            day,
            10,
            40,
            "Сбор вещей",
            audience="Candidates",
            location="📦 Сборы",
            description="Подготовка к выезду",
        ),
    ]

    text = format_schedule_day(day, entries)
    lines = text.splitlines()

    assert lines[0] == "📅 2025-11-15 — День выпускного"
    assert "🕔 Утро" in lines
    assert "📦 Сборы" in lines

    bullets = _bullet_lines(text)
    assert bullets[0].endswith("— Тимы")
    assert bullets[1].endswith("— Все")
    assert bullets[2].endswith("— Кандидаты")

    detail_lines = [line for line in lines if line.strip().startswith("◦ ")]
    assert "Начало дня" in detail_lines[0]
    assert "Подготовка к выезду" in detail_lines[-1]

    assert "Team" not in text
    assert "All" not in text
    assert "Candidates" not in text


def test_format_schedule_day_includes_location_details_without_sections():
    day = dt.date(2025, 11, 16)
    entries = [
        _entry(
            day,
            8,
            30,
            "Служение",
            end_time=dt.time(9, 30),
            location="Главный зал",
            audience="leadership",
            description="Прославление\nМолитва",
        )
    ]

    text = format_schedule_day(day, entries)
    bullets = _bullet_lines(text)

    assert bullets[0].startswith("• 08:30–09:30 Служение")
    assert bullets[0].endswith("— Тимы")

    detail_lines = [
        line.strip() for line in text.splitlines() if line.strip().startswith("◦ ")
    ]
    assert "Главный зал" in detail_lines[0]
    assert "Прославление" in detail_lines[1]
    assert "Молитва" in detail_lines[2]
