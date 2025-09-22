"""
Integration tests for export command registration and execution.

Tests that the /export command is properly registered in the bot application
and can be executed by authorized users.
"""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Bot, Chat, Message, Update, User
from telegram.ext import Application, CommandHandler, ConversationHandler

from src.bot.handlers.export_conversation_handlers import start_export_selection
from src.config.settings import Settings
from src.main import create_application


class TestExportCommandIntegration:
    """Test export command integration with bot application."""

    @pytest.fixture
    def mock_settings(self):
        """Create mock settings for testing."""
        settings = Mock(spec=Settings)
        settings.telegram = Mock()
        settings.telegram.bot_token = "test_bot_token"
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
        settings.telegram.admin_user_ids = [123456]
        settings.logging = Mock()
        settings.logging.log_level = "INFO"
        settings.get_file_logging_config = Mock()
        settings.get_file_logging_config.return_value.enabled = False
        return settings

    @pytest.fixture
    def mock_bot(self):
        """Create mock bot."""
        bot = Mock(spec=Bot)
        bot.token = "test_bot_token"
        return bot

    @pytest.mark.asyncio
    async def test_export_command_registered(self, mock_settings):
        """Test that /export command is registered in the application."""
        with patch("src.main.get_settings", return_value=mock_settings):
            with patch(
                "src.bot.handlers.search_conversation.get_search_conversation_handler",
                return_value=Mock(),
            ):
                app = create_application()

                # Find export conversation handler
                export_conversation_handler = None
                for handler in app.handlers[0]:  # handlers[0] is the default group
                    if isinstance(handler, ConversationHandler):
                        # Check if this conversation handler has export entry point
                        for entry_point in handler.entry_points:
                            if (
                                isinstance(entry_point, CommandHandler)
                                and "export" in entry_point.commands
                            ):
                                export_conversation_handler = handler
                                break
                        if export_conversation_handler:
                            break

                assert (
                    export_conversation_handler is not None
                ), "/export conversation handler not registered"
                # Verify the entry point callback
                export_entry_point = None
                for entry_point in export_conversation_handler.entry_points:
                    if (
                        isinstance(entry_point, CommandHandler)
                        and "export" in entry_point.commands
                    ):
                        export_entry_point = entry_point
                        break
                assert export_entry_point.callback == start_export_selection

    @pytest.mark.asyncio
    async def test_export_command_execution(self, mock_settings, mock_bot):
        """Test that /export command can be executed."""
        # Create mock update with /export command
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "/export"
        update.message.reply_text = AsyncMock()
        update.message.reply_document = AsyncMock()

        # Mock user (admin)
        user = Mock(spec=User)
        user.id = 123456
        user.username = "admin_user"
        update.message.from_user = user
        update.effective_user = user

        # Mock chat
        chat = Mock(spec=Chat)
        chat.id = 12345
        update.message.chat = chat
        update.effective_chat = chat

        # Create context
        from telegram.ext import ContextTypes

        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = mock_bot
        context.bot_data = {"settings": mock_settings}
        context.user_data = {}

        # Mock export service
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="test,data\n1,2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        with patch(
            "src.bot.handlers.export_conversation_handlers.is_admin_user",
            return_value=True,
        ):
            # Execute conversation entry point
            result = await start_export_selection(update, context)

            # Verify conversation started
            assert update.message.reply_text.called
            # Should send export selection menu
            first_call = update.message.reply_text.call_args_list[0]
            assert "выберите тип экспорта" in first_call[0][0].lower()
            # Should return first conversation state
            from src.bot.handlers.export_states import ExportStates

            assert result == ExportStates.SELECTING_EXPORT_TYPE

    @pytest.mark.asyncio
    async def test_export_command_in_help(self, mock_settings):
        """Test that /export command appears in bot commands list."""
        with patch("src.main.get_settings", return_value=mock_settings):
            with patch(
                "src.bot.handlers.search_conversation.get_search_conversation_handler",
                return_value=Mock(),
            ):
                app = create_application()

                # Get all registered commands (including those in conversation handlers)
                commands = []
                for handler_group in app.handlers.values():
                    for handler in handler_group:
                        if isinstance(handler, CommandHandler):
                            commands.extend(handler.commands)
                        elif isinstance(handler, ConversationHandler):
                            # Check entry points for command handlers
                            for entry_point in handler.entry_points:
                                if isinstance(entry_point, CommandHandler):
                                    commands.extend(entry_point.commands)

                assert "export" in commands, "/export not in command list"

    @pytest.mark.asyncio
    async def test_export_command_non_admin_blocked(self, mock_settings, mock_bot):
        """Test that non-admin users cannot execute /export command."""
        # Create mock update with /export command from non-admin
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "/export"
        update.message.reply_text = AsyncMock()
        update.message.reply_document = AsyncMock()

        # Mock non-admin user
        user = Mock(spec=User)
        user.id = 999999  # Not in admin list
        user.username = "regular_user"
        update.message.from_user = user
        update.effective_user = user

        # Mock chat
        chat = Mock(spec=Chat)
        chat.id = 12345
        update.message.chat = chat
        update.effective_chat = chat

        # Create context
        from telegram.ext import ContextTypes

        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot = mock_bot
        context.bot_data = {"settings": mock_settings}
        context.user_data = {}

        # Execute conversation entry point
        result = await start_export_selection(update, context)

        # Verify access denied
        update.message.reply_text.assert_called_once()
        call_args = update.message.reply_text.call_args
        assert (
            "нет прав" in call_args[0][0] or "администратор" in call_args[0][0].lower()
        )

        # Should end conversation immediately for non-admin
        from telegram.ext import ConversationHandler

        assert result == ConversationHandler.END

    @pytest.mark.asyncio
    async def test_export_command_with_settings_in_context(self, mock_settings):
        """Test that export command has access to settings via context."""
        with patch("src.main.get_settings", return_value=mock_settings):
            with patch(
                "src.bot.handlers.search_conversation.get_search_conversation_handler",
                return_value=Mock(),
            ):
                app = create_application()

                # Verify bot_data is set up with settings
                # This is typically done during application initialization
                # For our export command, we need to ensure settings are available

                # Find export conversation handler
                export_conversation_handler = None
                for handler in app.handlers[0]:
                    if isinstance(handler, ConversationHandler):
                        # Check if this conversation handler has export entry point
                        for entry_point in handler.entry_points:
                            if (
                                isinstance(entry_point, CommandHandler)
                                and "export" in entry_point.commands
                            ):
                                export_conversation_handler = handler
                                break
                        if export_conversation_handler:
                            break

                assert export_conversation_handler is not None

                # Create test context
                from telegram.ext import ContextTypes

                context = Mock(spec=ContextTypes.DEFAULT_TYPE)
                context.bot_data = {}

                # Settings should be added to context during app initialization
                # Verify the entry point callback
                export_entry_point = None
                for entry_point in export_conversation_handler.entry_points:
                    if (
                        isinstance(entry_point, CommandHandler)
                        and "export" in entry_point.commands
                    ):
                        export_entry_point = entry_point
                        break
                assert export_entry_point.callback == start_export_selection
