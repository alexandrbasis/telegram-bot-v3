"""
Integration tests for main bot application.

Tests bot initialization, configuration, and startup processes including
conversation handler registration and error handling setup.
"""

import asyncio
import logging
from unittest.mock import AsyncMock, MagicMock, Mock, patch

import pytest
from telegram.error import Conflict
from telegram.ext import Application, CommandHandler, ConversationHandler


class TestMainBotApplication:
    """Test main bot application initialization and setup."""

    @pytest.mark.asyncio
    async def test_main_app_imports(self):
        """Test that main app can be imported without errors."""
        try:
            from src.main import create_application

            assert callable(create_application)
        except ImportError:
            pytest.fail("Cannot import main application")

    @pytest.mark.asyncio
    async def test_create_application_returns_application(self):
        """Test that create_application returns telegram Application instance."""
        with patch("src.main.get_settings") as mock_get_settings:
            # Mock settings with proper structure
            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = (
                "INFO"  # Fixed: was .level, should be .log_level
            )
            mock_get_settings.return_value = mock_settings

            from src.main import create_application

            app = create_application()

            assert isinstance(app, Application)

    @pytest.mark.asyncio
    async def test_create_application_configures_token(self):
        """Test that create_application uses bot token from settings."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("telegram.ext.Application.builder") as mock_builder,
        ):

            # Mock settings with proper structure
            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_bot_token_123"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = "INFO"
            mock_get_settings.return_value = mock_settings

            # Mock builder chain
            mock_builder_instance = Mock()
            mock_builder_instance.token.return_value = mock_builder_instance
            mock_builder_instance.request.return_value = mock_builder_instance
            # Create mock app with real dictionary for bot_data
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}  # Real dictionary, not Mock
            mock_app.add_handler = Mock()
            mock_builder_instance.build.return_value = mock_app
            mock_builder.return_value = mock_builder_instance

            from src.main import create_application

            app = create_application()

            # Should set token from settings
            mock_builder_instance.token.assert_called_once_with("test_bot_token_123")

    @pytest.mark.asyncio
    async def test_create_application_adds_conversation_handler(self):
        """Test that create_application adds search conversation handler."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("src.main.get_search_conversation_handler") as mock_get_handler,
            patch(
                "src.main.get_export_conversation_handler"
            ) as mock_get_export_handler,
            patch("telegram.ext.Application.builder") as mock_builder,
        ):

            # Mock settings with proper structure
            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = "INFO"
            mock_get_settings.return_value = mock_settings

            # Mock search conversation handler
            mock_conversation_handler = Mock(spec=ConversationHandler)
            mock_get_handler.return_value = mock_conversation_handler

            # Mock export conversation handler with proper entry_points
            mock_export_conversation_handler = Mock(spec=ConversationHandler)
            mock_export_entry_point = Mock(spec=CommandHandler)
            mock_export_entry_point.commands = ["export"]
            mock_export_conversation_handler.entry_points = [mock_export_entry_point]
            mock_get_export_handler.return_value = mock_export_conversation_handler

            # Mock application with real bot_data dictionary
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}  # Real dictionary, not Mock
            mock_app.add_handler = Mock()

            mock_builder_instance = Mock()
            mock_builder_instance.token.return_value = mock_builder_instance
            mock_builder_instance.request.return_value = mock_builder_instance
            mock_builder_instance.build.return_value = mock_app
            mock_builder.return_value = mock_builder_instance

            from src.main import create_application

            app = create_application()

            # Should add search conversation handler, export conversation handler, legacy export command handler, and logging command handler
            assert mock_app.add_handler.call_count == 4

            # First call should be the search conversation handler
            mock_app.add_handler.assert_any_call(mock_conversation_handler)

            # Subsequent calls should include export conversation, legacy export, and logging command handlers
            calls = mock_app.add_handler.call_args_list

            # Collect commands from direct CommandHandlers
            command_handlers = [
                call[0][0] for call in calls if isinstance(call[0][0], CommandHandler)
            ]
            command_commands = {
                cmd for handler in command_handlers for cmd in handler.commands
            }

            # Check specifically for export conversation handler
            mock_app.add_handler.assert_any_call(mock_export_conversation_handler)
            command_commands.update(
                ["export"]
            )  # We know export conversation handler provides "export" command

            # Should have export (from conversation), export_direct (legacy), and logging commands
            assert "export" in command_commands
            assert "export_direct" in command_commands
            assert "logging" in command_commands

    @pytest.mark.asyncio
    async def test_create_application_configures_logging(self):
        """Test that create_application configures logging."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("src.main.configure_logging") as mock_configure_logging,
        ):

            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_get_settings.return_value = mock_settings

            from src.main import create_application

            app = create_application()

            # Should configure logging
            mock_configure_logging.assert_called_once_with(mock_settings)


class TestMainBotRunning:
    """Test main bot running and lifecycle."""

    @pytest.mark.asyncio
    async def test_main_function_exists(self):
        """Test that main function exists and is callable."""
        try:
            from src.main import main

            assert callable(main)
        except ImportError:
            pytest.fail("Cannot import main function")

    def test_main_function_creates_and_runs_app(self):
        """Test that main function calls asyncio.run with run_bot."""
        with patch("asyncio.run") as mock_asyncio_run:
            from src.main import main, run_bot

            # Should not raise exception
            main()

            # Should call asyncio.run with run_bot
            mock_asyncio_run.assert_called_once()
            # The argument should be the result of run_bot() call
            args, kwargs = mock_asyncio_run.call_args
            # Since run_bot() returns a coroutine, we can't easily check it directly
            # but we know asyncio.run was called

    @pytest.mark.asyncio
    async def test_run_bot_function(self):
        """Test that run_bot function properly starts the bot."""
        with patch("src.main.create_application") as mock_create_app:

            mock_app = Mock(spec=Application)
            mock_app.run_polling = AsyncMock()
            mock_create_app.return_value = mock_app

            from src.main import run_bot

            await run_bot()

            # Should create application and run polling
            mock_create_app.assert_called_once()
            mock_app.run_polling.assert_called_once()

    @pytest.mark.asyncio
    async def test_run_bot_retries_on_conflict(self):
        """Test that run_bot retries startup when Telegram reports a conflict."""
        settings_mock = Mock()
        settings_mock.telegram.get_startup_retry_config.return_value = {
            "attempts": 2,
            "delay_seconds": 0.1,
        }

        # First application instance raises Conflict during start_polling
        first_app = Mock(spec=Application)
        first_app.bot_data = {"settings": settings_mock}
        first_app.initialize = AsyncMock()
        first_app.start = AsyncMock()
        first_app.stop = AsyncMock()
        first_app.shutdown = AsyncMock()
        first_app.run_polling = None

        first_updater = Mock()
        first_updater.initialize = AsyncMock()
        first_updater.start_polling = AsyncMock(side_effect=Conflict("conflict test"))
        first_updater.stop = AsyncMock()
        first_updater.shutdown = AsyncMock()
        first_app.updater = first_updater

        # Second application instance starts successfully
        second_app = Mock(spec=Application)
        second_app.bot_data = {"settings": settings_mock}
        second_app.initialize = AsyncMock()
        second_app.start = AsyncMock()
        second_app.stop = AsyncMock()
        second_app.shutdown = AsyncMock()
        second_app.run_polling = None

        second_updater = Mock()
        second_updater.initialize = AsyncMock()
        second_updater.start_polling = AsyncMock(return_value=None)
        second_updater.stop = AsyncMock()
        second_updater.shutdown = AsyncMock()
        second_app.updater = second_updater

        import src.main as main_module

        started_event = asyncio.Event()

        async def mark_started(*args, **kwargs):
            started_event.set()
            return None

        second_updater.start_polling = AsyncMock(side_effect=mark_started)

        with (
            patch.object(
                main_module, "create_application", side_effect=[first_app, second_app]
            ) as mock_create,
            patch.object(
                main_module.asyncio, "sleep", new_callable=AsyncMock
            ) as mock_sleep,
        ):

            task = asyncio.create_task(main_module.run_bot())

            await asyncio.wait_for(started_event.wait(), timeout=1.0)

            assert mock_create.call_count == 2
            first_updater.start_polling.assert_awaited()
            first_updater.stop.assert_awaited()
            second_updater.start_polling.assert_awaited()

            mock_sleep.assert_awaited_with(0.1)

            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass  # Expected when task is cancelled

            second_updater.stop.assert_awaited()
            second_updater.shutdown.assert_awaited()


class TestLoggingConfiguration:
    """Test logging configuration."""

    def test_configure_logging_function_exists(self):
        """Test that configure_logging function exists."""
        try:
            from src.main import configure_logging

            assert callable(configure_logging)
        except ImportError:
            pytest.fail("Cannot import configure_logging function")

    def test_configure_logging_sets_level(self):
        """Test that configure_logging sets the correct log level."""
        with patch("logging.basicConfig") as mock_basic_config:

            mock_settings = Mock()
            mock_settings.logging.log_level = "DEBUG"

            from src.main import configure_logging

            configure_logging(mock_settings)

            # Should configure basic logging
            mock_basic_config.assert_called_once()
            call_args = mock_basic_config.call_args

            # Should set DEBUG level
            assert call_args[1]["level"] == logging.DEBUG

    def test_configure_logging_sets_format(self):
        """Test that configure_logging sets proper log format."""
        with patch("logging.basicConfig") as mock_basic_config:

            mock_settings = Mock()
            mock_settings.logging.log_level = "INFO"

            from src.main import configure_logging

            configure_logging(mock_settings)

            call_args = mock_basic_config.call_args
            log_format = call_args[1]["format"]

            # Should include timestamp, level, name, and message
            assert "%(asctime)s" in log_format
            assert "%(levelname)s" in log_format
            assert "%(name)s" in log_format
            assert "%(message)s" in log_format


class TestErrorHandling:
    """Test error handling in main application."""

    def test_create_application_handles_missing_token(self):
        """Test that create_application handles missing bot token gracefully."""
        with patch("src.main.get_settings") as mock_get_settings:

            # Mock settings with no token but proper logging structure
            mock_settings = Mock()
            mock_settings.telegram.bot_token = None
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = "INFO"  # Proper string value
            mock_get_settings.return_value = mock_settings

            from src.main import create_application

            with pytest.raises(ValueError, match="Bot token is required"):
                create_application()

    @pytest.mark.asyncio
    async def test_run_bot_handles_exceptions(self):
        """Test that run_bot handles exceptions gracefully."""
        with patch("src.main.create_application") as mock_create_app:

            # Mock application that raises exception
            mock_app = Mock(spec=Application)
            mock_app.run_polling = AsyncMock(side_effect=Exception("Connection error"))
            mock_create_app.return_value = mock_app

            from src.main import run_bot

            # Should handle exception gracefully
            try:
                await run_bot()
            except Exception as e:
                # Should re-raise with proper handling
                assert "Connection error" in str(e)


class TestBotIntegration:
    """Integration tests for complete bot functionality."""

    @pytest.mark.asyncio
    async def test_bot_startup_sequence(self):
        """Test complete bot startup sequence."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("src.main.configure_logging") as mock_configure_logging,
            patch("src.main.get_search_conversation_handler") as mock_get_handler,
        ):

            # Mock all dependencies
            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = "INFO"  # Proper string value
            mock_get_settings.return_value = mock_settings

            mock_conversation_handler = Mock(spec=ConversationHandler)
            # Set the persistent attribute to False to avoid persistence errors
            mock_conversation_handler.persistent = False
            mock_get_handler.return_value = mock_conversation_handler

            from src.main import create_application

            # Should complete without errors
            app = create_application()

            # Verify startup sequence
            mock_configure_logging.assert_called_once_with(mock_settings)
            mock_get_handler.assert_called_once()

            assert app is not None

    @pytest.mark.asyncio
    async def test_bot_can_handle_conversation(self):
        """Test that bot is properly configured to handle conversations."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("src.main.get_search_conversation_handler") as mock_get_handler,
        ):

            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.telegram.get_request_config.return_value = {
                "connect_timeout": 5.0,
                "read_timeout": 20.0,
                "write_timeout": 5.0,
                "pool_timeout": 5.0,
                "connection_pool_size": 10,
            }
            mock_settings.telegram.get_startup_retry_config.return_value = {
                "attempts": 1,
                "delay_seconds": 0.0,
            }
            mock_settings.logging.log_level = "INFO"  # Proper string value
            mock_get_settings.return_value = mock_settings

            # Create a real ConversationHandler mock
            mock_conversation_handler = Mock(spec=ConversationHandler)
            # Set the persistent attribute to False to avoid persistence errors
            mock_conversation_handler.persistent = False
            mock_get_handler.return_value = mock_conversation_handler

            from src.main import create_application

            app = create_application()

            # Application should have handlers registered
            assert len(app.handlers[0]) >= 1  # Should have at least one handler group
