from src.bot.messages import ErrorMessages


def test_no_participants_in_room_message():
    assert (
        ErrorMessages.no_participants_in_room("301")
        == "❌ В комнате 301 участники не найдены."
    )
