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


def test_enter_floor_with_discovery_russian():
    """Test floor discovery prompt with both button and manual input options."""
    expected = "Выберите этаж из списка или пришлите номер этажа цифрой:"
    assert InfoMessages.ENTER_FLOOR_WITH_DISCOVERY == expected


def test_available_floors_header_russian():
    """Test available floors header message."""
    expected = "📍 Доступные этажи:"
    assert InfoMessages.AVAILABLE_FLOORS_HEADER == expected


def test_no_floors_available_russian():
    """Test message when no floors have participants."""
    expected = "В данный момент участники не размещены ни на одном этаже. Пришлите номер этажа цифрой."
    assert InfoMessages.NO_FLOORS_AVAILABLE == expected


def test_floor_discovery_error_russian():
    """Test error message for floor discovery failure."""
    expected = "Произошла ошибка. Пришлите номер этажа цифрой."
    assert InfoMessages.FLOOR_DISCOVERY_ERROR == expected
