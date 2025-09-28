"""
Utilities to format schedule entries for Telegram output.
"""

from __future__ import annotations

import datetime as dt
from typing import Iterable, List, Optional, Sequence, Tuple

from src.models.schedule import ScheduleEntry

SECTION_MARKERS: Tuple[str, ...] = (
    "section:",
    "секция:",
    "раздел:",
    "block:",
    "блок:",
)

AUDIENCE_ALIASES = {
    "all": "Все",
    "все": "Все",
    "team": "Тимы",
    "тимы": "Тимы",
    "команда": "Тимы",
    "tm": "Тимы",
    "tim": "Тимы",
    "candidates": "Кандидаты",
    "candidate": "Кандидаты",
    "кандидаты": "Кандидаты",
    "leadership": "Тимы",
    "clergy": "Тимы",
}

DEFAULT_AUDIENCE_LABEL = "Все"


def format_time(t: dt.time) -> str:
    return t.strftime("%H:%M")


def _format_time_range(start: dt.time, end: Optional[dt.time]) -> str:
    time_part = format_time(start)
    if end:
        time_part += f"–{format_time(end)}"
    return time_part


def _normalize_text(value: Optional[str]) -> Optional[str]:
    if value is None:
        return None
    text = value.strip()
    return text or None


def _split_multiline(text: str) -> List[str]:
    lines: List[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if line:
            lines.append(line)
    return lines


def _match_section_header(line: str) -> Optional[str]:
    stripped = line.strip()
    if not stripped:
        return None
    if stripped.startswith("[") and stripped.endswith("]") and len(stripped) > 2:
        return stripped[1:-1].strip() or None

    lowered = stripped.casefold()
    for marker in SECTION_MARKERS:
        if lowered.startswith(marker):
            remainder = stripped[len(marker) :].strip()
            return remainder or None
    return None


def _extract_section_and_details(
    description: Optional[str],
) -> Tuple[Optional[str], List[str]]:
    normalized = _normalize_text(description)
    if not normalized:
        return None, []

    lines = _split_multiline(normalized)
    if not lines:
        return None, []

    section = _match_section_header(lines[0])
    if section:
        return section, lines[1:]
    return None, lines


def _looks_like_section_header(text: str) -> bool:
    normalized = text.strip()
    if not normalized:
        return False

    first_char = normalized[0]
    if not first_char.isalnum():
        return True

    lowered = normalized.casefold()
    return any(lowered.startswith(marker) for marker in SECTION_MARKERS)


def _translate_audience(value: Optional[str]) -> Optional[str]:
    normalized = _normalize_text(value)
    if normalized is None:
        return None

    key = normalized.casefold()
    return AUDIENCE_ALIASES.get(key, DEFAULT_AUDIENCE_LABEL)


def _extend_details(details: List[str], extra: Sequence[str]) -> None:
    for item in extra:
        for line in _split_multiline(item):
            details.append(line)


def format_schedule_day(date_value: dt.date, entries: Iterable[ScheduleEntry]) -> str:
    """Return formatted schedule string with RU-friendly layout."""

    entries_sorted = sorted(
        list(entries),
        key=lambda x: (
            x.start_time,
            x.order if x.order is not None else 9999,
        ),
    )

    day_label = next(
        (
            _normalize_text(entry.day_label)
            for entry in entries_sorted
            if _normalize_text(entry.day_label)
        ),
        None,
    )

    header = f"📅 {date_value.isoformat()}"
    if day_label:
        header += f" — {day_label}"

    if not entries_sorted:
        return f"{header}\n\nНет событий на этот день."

    parts: List[str] = [header, ""]
    current_section: Optional[str] = None

    for entry in entries_sorted:
        section_from_description, description_lines = _extract_section_and_details(
            entry.description
        )

        location_text = _normalize_text(entry.location)
        section = section_from_description

        if (
            section is None
            and location_text
            and _looks_like_section_header(location_text)
        ):
            section = location_text
            location_text = None

        if section and section != current_section:
            if parts and parts[-1] != "":
                parts.append("")
            parts.append(section)
            current_section = section

        time_text = _format_time_range(entry.start_time, entry.end_time)
        audience_label = _translate_audience(entry.audience)

        bullet = f"• {time_text} {entry.title}"
        if audience_label:
            bullet += f" — {audience_label}"
        parts.append(bullet)

        detail_lines: List[str] = []
        if location_text:
            detail_lines.append(location_text)
        _extend_details(detail_lines, description_lines)

        for detail in detail_lines:
            parts.append(f"  ◦ {detail}")

    return "\n".join(parts)
