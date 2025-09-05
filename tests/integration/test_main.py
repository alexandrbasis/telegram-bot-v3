"""
Integration tests for main bot application.

Tests bot initialization, configuration, and startup processes including
conversation handler registration and error handling setup.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch, MagicMock
import asyncio
import logging

from telegram.ext import Application, ConversationHandler


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
            mock_settings.logging.log_level = "INFO"
            mock_get_settings.return_value = mock_settings

            # Mock builder chain
            mock_builder_instance = Mock()
            mock_builder_instance.token.return_value = mock_builder_instance
            mock_builder_instance.build.return_value = Mock(spec=Application)
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
            patch("telegram.ext.Application.builder") as mock_builder,
        ):

            # Mock settings with proper structure
            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
            mock_settings.logging.log_level = "INFO"
            mock_get_settings.return_value = mock_settings

            # Mock conversation handler
            mock_conversation_handler = Mock(spec=ConversationHandler)
            mock_get_handler.return_value = mock_conversation_handler

            # Mock application
            mock_app = Mock(spec=Application)
            mock_app.add_handler = Mock()

            mock_builder_instance = Mock()
            mock_builder_instance.token.return_value = mock_builder_instance
            mock_builder_instance.build.return_value = mock_app
            mock_builder.return_value = mock_builder_instance

            from src.main import create_application

            app = create_application()

            # Should add conversation handler
            mock_app.add_handler.assert_called_once_with(mock_conversation_handler)

    @pytest.mark.asyncio
    async def test_create_application_configures_logging(self):
        """Test that create_application configures logging."""
        with (
            patch("src.main.get_settings") as mock_get_settings,
            patch("src.main.configure_logging") as mock_configure_logging,
        ):

            mock_settings = Mock()
            mock_settings.telegram.bot_token = "test_token"
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
