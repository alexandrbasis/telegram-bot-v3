"""Integration tests for /help command registration."""

from unittest.mock import Mock, patch

import pytest
from telegram.ext import CommandHandler

from src.bot.handlers.help_handlers import handle_help_command
from src.config.settings import Settings
from src.main import create_application


@pytest.fixture
def mock_settings():
    settings = Mock(spec=Settings)
    settings.telegram = Mock()
    settings.telegram.bot_token = "test_token"
    settings.telegram.get_request_config.return_value = {
        "connect_timeout": 5.0,
        "read_timeout": 20.0,
        "write_timeout": 5.0,
        "pool_timeout": 5.0,
        "connection_pool_size": 10,
    }
    settings.telegram.get_startup_retry_config.return_value = {
        "attempts": 1,
        "delay_seconds": 0.0,
    }
    settings.telegram.admin_user_ids = []
    settings.logging = Mock()
    settings.logging.log_level = "INFO"
    settings.get_file_logging_config = Mock()
    settings.get_file_logging_config.return_value.enabled = False
    settings.application = Mock()
    settings.application.enable_schedule_feature = False
    return settings


@pytest.mark.asyncio
async def test_help_command_registered_globally(mock_settings):
    async def _noop(update, context):  # pragma: no cover - test helper
        return None

    with patch("src.main.get_settings", return_value=mock_settings):
        with patch(
            "src.main.get_search_conversation_handler",
            return_value=CommandHandler("dummy_search", _noop),
        ):
            with patch(
                "src.main.get_export_conversation_handler",
                return_value=CommandHandler("dummy_export", _noop),
            ):
                with patch("src.main.get_schedule_handlers", return_value=[]):
                    app = create_application()

    help_handlers = [
        handler
        for handler in app.handlers[0]
        if isinstance(handler, CommandHandler) and "help" in handler.commands
    ]

    assert help_handlers, "/help command handler not registered in default group"
    assert help_handlers[0].callback == handle_help_command
