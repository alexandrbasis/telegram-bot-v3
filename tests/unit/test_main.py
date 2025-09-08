"""
Unit tests for main application integration with file logging.

Tests cover:
- File logging service initialization during application startup
- Integration with existing console logging
- Error handling during file logging setup
- Configuration-driven file logging behavior
"""

import logging
import os
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from src.main import configure_logging, create_application


class TestMainFileLoggingIntegration:
    """Test file logging integration with main application."""

    def test_configure_logging_with_file_logging_enabled(self):
        """Test that configure_logging initializes file logging when enabled."""
        # RED phase - this test will fail until we implement file logging integration

        # Mock settings with file logging enabled
        mock_settings = Mock()
        mock_settings.logging.log_level = "INFO"
        mock_settings.logging.enable_file_logging = True
        mock_settings.get_file_logging_config.return_value = Mock(
            enabled=True,
            log_dir=Path("/test/logs"),
            max_file_size=1024 * 1024,
            backup_count=5,
        )

        with patch("src.main.FileLoggingService") as mock_file_service:
            configure_logging(mock_settings)

            # Should create and initialize FileLoggingService
            mock_file_service.assert_called_once()
            mock_file_service.return_value.initialize_directories.assert_called_once()

    def test_configure_logging_with_file_logging_disabled(self):
        """Test that configure_logging skips file logging when disabled."""
        # Mock settings with file logging disabled
        mock_settings = Mock()
        mock_settings.logging.log_level = "INFO"
        mock_settings.logging.enable_file_logging = False
        mock_settings.get_file_logging_config.return_value = Mock(enabled=False)

        with patch("src.main.FileLoggingService") as mock_file_service:
            configure_logging(mock_settings)

            # Should not create FileLoggingService when disabled
            mock_file_service.assert_not_called()

    def test_configure_logging_preserves_existing_console_logging(self):
        """Test that file logging integration preserves existing console logging behavior."""
        mock_settings = Mock()
        mock_settings.logging.log_level = "DEBUG"
        mock_settings.logging.enable_file_logging = True
        mock_settings.get_file_logging_config.return_value = Mock(enabled=True)

        with (
            patch("src.main.FileLoggingService"),
            patch("src.main.logging.basicConfig") as mock_basic_config,
            patch("src.main.logging.getLogger") as mock_get_logger,
        ):

            configure_logging(mock_settings)

            # Should still configure basic console logging
            mock_basic_config.assert_called_once()
            # Should still set specific logger levels
            mock_get_logger.assert_any_call("telegram")
            mock_get_logger.assert_any_call("httpx")

    def test_configure_logging_handles_file_logging_errors_gracefully(self):
        """Test that configure_logging handles file logging initialization errors gracefully."""
        mock_settings = Mock()
        mock_settings.logging.log_level = "INFO"
        mock_settings.logging.enable_file_logging = True
        mock_settings.get_file_logging_config.return_value = Mock(enabled=True)

        # Mock FileLoggingService to raise an exception
        with (
            patch(
                "src.main.FileLoggingService",
                side_effect=Exception("File logging failed"),
            ),
            patch("src.main.logging.basicConfig") as mock_basic_config,
        ):

            # Should not crash the application
            configure_logging(mock_settings)

            # Console logging should still be configured
            mock_basic_config.assert_called_once()

    def test_create_application_initializes_file_logging(self):
        """Test that create_application properly initializes file logging during bot setup."""
        # RED phase - this test will fail until we integrate file logging in create_application

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "ENABLE_FILE_LOGGING": "true",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder") as mock_app_builder,
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.FileLoggingService") as mock_file_service,
        ):

            # Mock the application builder chain
            mock_builder = Mock()
            mock_builder.token.return_value = mock_builder
            mock_builder.build.return_value = Mock()
            mock_app_builder.return_value = mock_builder

            create_application()

            # Should create FileLoggingService during application creation
            mock_file_service.assert_called_once()

    def test_application_logging_integration_with_existing_loggers(self):
        """Test that file logging integrates with existing application loggers."""
        # RED phase - this test will fail until we implement logger integration

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "ENABLE_FILE_LOGGING": "true",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder"),
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.FileLoggingService") as mock_file_service,
            patch("src.main.logging.getLogger") as mock_get_logger,
        ):

            mock_file_service_instance = Mock()
            mock_file_service.return_value = mock_file_service_instance

            create_application()

            # Should integrate with main application logger
            mock_file_service_instance.get_application_logger.assert_called()


class TestFileLoggingServiceIntegration:
    """Test FileLoggingService integration points with main application."""

    def test_main_logger_gets_file_handler(self):
        """Test that main application logger gets file handler when file logging is enabled."""
        # This test verifies the integration creates proper file handlers for the main logger

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "ENABLE_FILE_LOGGING": "true",
            "FILE_LOG_DIR": "/test/app/logs",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder"),
            patch("src.main.get_search_conversation_handler"),
            patch(
                "src.services.file_logging_service.logging.handlers.RotatingFileHandler"
            ) as mock_handler,
        ):

            mock_handler_instance = Mock()
            mock_handler.return_value = mock_handler_instance

            app = create_application()

            # Verify file handler was created for main application logging
            assert (
                mock_handler.called
            ), "RotatingFileHandler should be created for application logging"

    def test_file_logging_uses_correct_directory_structure(self):
        """Test that file logging creates the expected directory structure."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "ENABLE_FILE_LOGGING": "true",
            "FILE_LOG_DIR": "/custom/log/path",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder"),
            patch("src.main.get_search_conversation_handler"),
            patch("pathlib.Path.mkdir") as mock_mkdir,
        ):

            create_application()

            # Should create the expected directory structure
            mock_mkdir.assert_called()

    def test_file_logging_error_handling_during_startup(self):
        """Test that application startup handles file logging errors without crashing."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
            "ENABLE_FILE_LOGGING": "true",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder"),
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.FileLoggingService", side_effect=Exception("Disk full")),
        ):

            # Should not crash even if file logging fails
            app = create_application()
            assert (
                app is not None
            ), "Application should be created even if file logging fails"
