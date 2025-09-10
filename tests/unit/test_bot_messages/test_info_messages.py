from src.bot.messages import InfoMessages


def test_enter_room_number_russian():
    assert InfoMessages.ENTER_ROOM_NUMBER == "Введите номер комнаты для поиска:"


def test_enter_date_of_birth_prompt_russian():
    """Test that date of birth prompt provides clear YYYY-MM-DD format guidance."""
    expected = "📅 Введите дату рождения в формате ГГГГ-ММ-ДД (например: 1990-05-15):"
    assert InfoMessages.ENTER_DATE_OF_BIRTH == expected


def test_enter_age_prompt_russian():
    """Test that age prompt provides numeric input guidance with valid range."""
    expected = "🔢 Введите возраст (от 0 до 120):"
    assert InfoMessages.ENTER_AGE == expected
