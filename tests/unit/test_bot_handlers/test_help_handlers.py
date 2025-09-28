"""Unit tests for help command messaging and handler."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update

from src.bot.messages import get_help_message


class TestHelpMessageContent:
    def test_help_message_includes_all_sections(self):
        message = get_help_message()

        expected_sections = [
            "ℹ️ Справка по возможностям бота",
            "📌 Основные команды",
            "/start — Возврат к главному меню и приветствие",
            "/help — Справка по всем командам бота",
            "🔍 Поиск участников",
            "/search_room — Поиск участников по номеру комнаты",
            "/search_floor — Поиск участников по этажу",
            "Меню поиска — Интерактивный поиск через главное меню",
            "📤 Экспорт данных",
            "/export — Экспорт списков участников в различных форматах",
            "/export_direct — Прямой экспорт (устаревшая команда)",
            "🗓 Расписание",
            "/schedule — Просмотр расписания мероприятий",
            "🛠 Администрирование",
            "/logging — Переключение уровня логирования (админ)",
            "/auth_refresh — Обновление авторизации (админ)",
            "🏠 Возврат в главное меню — Используйте команду /start в любой момент",
        ]

        for section in expected_sections:
            assert section in message, f"Missing section: {section}"

        # Ensure sections appear in the defined order for readability
        indices = [message.index(section) for section in expected_sections]
        assert indices == sorted(indices), "Sections in help message are out of order"


@pytest.mark.asyncio
@patch("src.bot.handlers.help_handlers.get_help_message", return_value="test help")
async def test_handle_help_command_sends_help_text(mock_get_help_message):
    from src.bot.handlers.help_handlers import handle_help_command

    update = Mock(spec=Update)
    message = AsyncMock()
    update.effective_message = message

    context = Mock()

    await handle_help_command(update, context)

    mock_get_help_message.assert_called_once()
    message.reply_text.assert_awaited_once_with(
        "test help", disable_web_page_preview=True
    )
