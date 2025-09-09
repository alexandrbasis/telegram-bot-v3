"""
Russian translation utilities for enums and display values.

Provides centralized mappings for department and role display
to ensure consistent Russian UI across bot messages.
"""

from typing import Optional, Union

from src.models.participant import Department, Role

# Complete Russian translations for Department enum values
DEPARTMENT_RUSSIAN = {
    Department.ROE.value: "РОЭ",
    Department.CHAPEL.value: "Часовня",
    Department.SETUP.value: "Подготовка",
    Department.PALANKA.value: "Паланка",
    Department.ADMINISTRATION.value: "Администрация",
    Department.KITCHEN.value: "Кухня",
    Department.DECORATION.value: "Оформление",
    Department.BELL.value: "Звонок",
    Department.REFRESHMENT.value: "Освежение",
    Department.WORSHIP.value: "Прославление",
    Department.MEDIA.value: "Медиа",
    Department.CLERGY.value: "Духовенство",
    Department.RECTORATE.value: "Ректорат",
}


def department_to_russian(value: Optional[Union[Department, str]]) -> str:
    """
    Translate Department enum or value to Russian display string.
    """
    if value is None or value == "":
        return "Не указано"
    v = value.value if hasattr(value, "value") else str(value)
    return DEPARTMENT_RUSSIAN.get(v, v)


def role_to_russian(value: Optional[Union[Role, str]]) -> str:
    """
    Translate Role enum or value to Russian display string.
    """
    if value is None or value == "":
        return "Не указано"
    v = value.value if hasattr(value, "value") else str(value)
    if v == Role.CANDIDATE.value:
        return "Кандидат"
    if v == Role.TEAM.value:
        return "Команда"
    return v
