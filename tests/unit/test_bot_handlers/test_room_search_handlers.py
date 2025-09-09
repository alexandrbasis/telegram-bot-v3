from src.bot.handlers.room_search_handlers import format_room_results_russian
from src.models.participant import Department, Participant, Role


def test_format_room_results_russian_empty():
    result = format_room_results_russian([], "101")
    assert result == "❌ В комнате 101 участники не найдены."


def test_format_room_results_russian_structure():
    participants = [
        Participant(
            record_id="rec1",
            full_name_ru="Иван Иванов",
            full_name_en="Ivan Ivanov",
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            floor=2,
            room_number="201",
        ),
        Participant(
            record_id="rec2",
            full_name_ru="Пётр Петров",
            full_name_en="Pyotr Petrov",
            role=Role.CANDIDATE,
            department=Department.WORSHIP,
            floor=2,
            room_number="201",
        ),
    ]

    result = format_room_results_russian(participants, "201")
    assert "🏠 Найдено участников в комнате 201: 2" in result

    # First participant
    assert "1. Иван Иванов (Ivan Ivanov)" in result
    assert "Роль: Команда" in result
    assert "Департамент: Администрация" in result
    assert "Этаж: 2" in result

    # Second participant
    assert "2. Пётр Петров (Pyotr Petrov)" in result
    assert "Роль: Кандидат" in result
    assert "Департамент: Прославление" in result
