from src.bot.messages import InfoMessages


def test_enter_room_number_russian():
    assert InfoMessages.ENTER_ROOM_NUMBER == "Введите номер комнаты для поиска:"
