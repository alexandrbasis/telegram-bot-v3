"""Unit tests for help command messaging and handler."""

from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update

from src.bot.messages import get_help_message


class TestHelpMessageContent:
    def test_help_message_includes_all_sections_with_schedule(self):
        """Test help message includes schedule when feature is enabled."""
        message = get_help_message(include_schedule=True)

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

    def test_help_message_excludes_schedule_when_disabled(self):
        """Test help message excludes schedule when feature is disabled."""
        message = get_help_message(include_schedule=False)

        # Should include these sections
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
            "🛠 Администрирование",
            "/logging — Переключение уровня логирования (админ)",
            "/auth_refresh — Обновление авторизации (админ)",
            "🏠 Возврат в главное меню — Используйте команду /start в любой момент",
        ]

        # Should NOT include schedule sections
        excluded_sections = [
            "🗓 Расписание",
            "/schedule — Просмотр расписания мероприятий",
        ]

        for section in expected_sections:
            assert section in message, f"Missing section: {section}"

        for section in excluded_sections:
            assert section not in message, f"Schedule section should not be present: {section}"

    def test_help_message_default_includes_schedule(self):
        """Test help message includes schedule by default for backward compatibility."""
        message = get_help_message()  # No explicit parameter

        assert "🗓 Расписание" in message
        assert "/schedule — Просмотр расписания мероприятий" in message


@pytest.mark.asyncio
@patch("src.bot.handlers.help_handlers.get_help_message", return_value="test help")
async def test_handle_help_command_sends_help_text(mock_get_help_message):
    """Test basic help command functionality without schedule feature flag."""
    from src.bot.handlers.help_handlers import handle_help_command

    update = Mock(spec=Update)
    message = AsyncMock()
    update.effective_message = message

    context = Mock()
    context.bot_data = {}  # No settings, should default to include_schedule=False

    await handle_help_command(update, context)

    mock_get_help_message.assert_called_once_with(include_schedule=False)
    message.reply_text.assert_awaited_once_with(
        "test help", disable_web_page_preview=True
    )


@pytest.mark.asyncio
@patch("src.bot.handlers.help_handlers.get_help_message", return_value="test help with schedule")
async def test_handle_help_command_with_schedule_enabled(mock_get_help_message):
    """Test help command when schedule feature is enabled in settings."""
    from src.bot.handlers.help_handlers import handle_help_command

    update = Mock(spec=Update)
    message = AsyncMock()
    update.effective_message = message

    # Mock settings with schedule feature enabled
    app_settings = Mock()
    app_settings.enable_schedule_feature = True
    settings = Mock()
    settings.application = app_settings

    context = Mock()
    context.bot_data = {"settings": settings}

    await handle_help_command(update, context)

    mock_get_help_message.assert_called_once_with(include_schedule=True)
    message.reply_text.assert_awaited_once_with(
        "test help with schedule", disable_web_page_preview=True
    )


@pytest.mark.asyncio
@patch("src.bot.handlers.help_handlers.get_help_message", return_value="test help no schedule")
async def test_handle_help_command_with_schedule_disabled(mock_get_help_message):
    """Test help command when schedule feature is disabled in settings."""
    from src.bot.handlers.help_handlers import handle_help_command

    update = Mock(spec=Update)
    message = AsyncMock()
    update.effective_message = message

    # Mock settings with schedule feature disabled
    app_settings = Mock()
    app_settings.enable_schedule_feature = False
    settings = Mock()
    settings.application = app_settings

    context = Mock()
    context.bot_data = {"settings": settings}

    await handle_help_command(update, context)

    mock_get_help_message.assert_called_once_with(include_schedule=False)
    message.reply_text.assert_awaited_once_with(
        "test help no schedule", disable_web_page_preview=True
    )
