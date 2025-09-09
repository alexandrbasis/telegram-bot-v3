import pytest

from src.models.participant import Department, Role
from src.utils.translations import (
    DEPARTMENT_RUSSIAN,
    department_to_russian,
    role_to_russian,
)


def test_department_russian_mapping_complete():
    # Ensure all Department enum values are present
    all_values = {d.value for d in Department}
    assert set(DEPARTMENT_RUSSIAN.keys()) == all_values


@pytest.mark.parametrize(
    "dept,expected",
    [
        (Department.ADMINISTRATION, "Администрация"),
        (Department.KITCHEN, "Кухня"),
        (Department.MEDIA, "Медиа"),
        (Department.WORSHIP, "Прославление"),
    ],
)
def test_department_to_russian_known(dept, expected):
    assert department_to_russian(dept) == expected


def test_department_to_russian_fallback():
    # Unknown value should fallback to string
    assert department_to_russian("UnknownDept") == "UnknownDept"


@pytest.mark.parametrize(
    "role,expected",
    [
        (Role.CANDIDATE, "Кандидат"),
        (Role.TEAM, "Команда"),
        (None, "Не указано"),
    ],
)
def test_role_to_russian(role, expected):
    assert role_to_russian(role) == expected
