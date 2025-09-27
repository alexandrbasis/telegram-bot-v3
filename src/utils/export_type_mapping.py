"""
Export type to Russian description mapping utilities.

Provides centralized Russian translations for export types used in
success messages and user interface elements.
"""

from typing import Optional

# Russian translations for export types
EXPORT_TYPE_RUSSIAN = {
    "participants": "Участники",
    "candidates": "Кандидаты",
    "team": "Тим Мемберы",
    "departments": "Департаменты",
    "roe": "РОЭ",
    "bible_readers": "Чтецы",
}


def get_russian_export_description(export_type: Optional[str]) -> str:
    """
    Get Russian description for export type.

    Args:
        export_type: Export type identifier (e.g., "candidates", "team")

    Returns:
        Russian description string for the export type
    """
    if not export_type:
        return "Экспорт"

    # Convert to lowercase for case-insensitive lookup
    normalized_type = str(export_type).lower()

    return EXPORT_TYPE_RUSSIAN.get(normalized_type, export_type)
