"""
Integration tests for notification admin command handler registration.

Tests verify that notification commands are properly registered with the
application and accessible through the command dispatcher.
"""

import os
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Update
from telegram.ext import Application

from src.main import create_application


class TestNotificationCommandRegistration:
    """Test notification admin command handler registration in main application."""

    def test_notifications_command_registered(self):
        """Test that /notifications command is properly registered."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder") as mock_app_builder,
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.get_export_conversation_handler"),
            patch("src.main.get_schedule_handlers", return_value=[]),
        ):
            # Setup mocks
            mock_builder = Mock()
            mock_builder.token.return_value = mock_builder
            mock_builder.request.return_value = mock_builder
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}
            mock_app.add_handler = Mock()
            mock_app.post_init = None
            mock_builder.build.return_value = mock_app
            mock_app_builder.return_value = mock_builder

            # Act
            app = create_application()

            # Assert - check that handler was added
            assert mock_app.add_handler.called
            # Find the notifications command handler in the calls
            handler_calls = [call[0][0] for call in mock_app.add_handler.call_args_list]
            notifications_handlers = [
                h
                for h in handler_calls
                if hasattr(h, "commands") and "notifications" in h.commands
            ]
            assert (
                len(notifications_handlers) == 1
            ), "/notifications command should be registered"

    def test_set_notification_time_command_registered(self):
        """Test that /set_notification_time command is properly registered."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder") as mock_app_builder,
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.get_export_conversation_handler"),
            patch("src.main.get_schedule_handlers", return_value=[]),
        ):
            # Setup mocks
            mock_builder = Mock()
            mock_builder.token.return_value = mock_builder
            mock_builder.request.return_value = mock_builder
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}
            mock_app.add_handler = Mock()
            mock_app.post_init = None
            mock_builder.build.return_value = mock_app
            mock_app_builder.return_value = mock_builder

            # Act
            app = create_application()

            # Assert - check that handler was added
            handler_calls = [call[0][0] for call in mock_app.add_handler.call_args_list]
            time_handlers = [
                h
                for h in handler_calls
                if hasattr(h, "commands") and "set_notification_time" in h.commands
            ]
            assert (
                len(time_handlers) == 1
            ), "/set_notification_time command should be registered"

    def test_test_stats_command_registered(self):
        """Test that /test_stats command is properly registered."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder") as mock_app_builder,
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.get_export_conversation_handler"),
            patch("src.main.get_schedule_handlers", return_value=[]),
        ):
            # Setup mocks
            mock_builder = Mock()
            mock_builder.token.return_value = mock_builder
            mock_builder.request.return_value = mock_builder
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}
            mock_app.add_handler = Mock()
            mock_app.post_init = None
            mock_builder.build.return_value = mock_app
            mock_app_builder.return_value = mock_builder

            # Act
            app = create_application()

            # Assert - check that handler was added
            handler_calls = [call[0][0] for call in mock_app.add_handler.call_args_list]
            test_handlers = [
                h
                for h in handler_calls
                if hasattr(h, "commands") and "test_stats" in h.commands
            ]
            assert len(test_handlers) == 1, "/test_stats command should be registered"

    def test_all_notification_commands_registered(self):
        """Test that all three notification commands are registered."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "TELEGRAM_BOT_TOKEN": "test_bot_token",
        }

        with (
            patch.dict(os.environ, env_vars, clear=True),
            patch("src.main.Application.builder") as mock_app_builder,
            patch("src.main.get_search_conversation_handler"),
            patch("src.main.get_export_conversation_handler"),
            patch("src.main.get_schedule_handlers", return_value=[]),
        ):
            # Setup mocks
            mock_builder = Mock()
            mock_builder.token.return_value = mock_builder
            mock_builder.request.return_value = mock_builder
            mock_app = Mock(spec=Application)
            mock_app.bot_data = {}
            mock_app.add_handler = Mock()
            mock_app.post_init = None
            mock_builder.build.return_value = mock_app
            mock_app_builder.return_value = mock_builder

            # Act
            app = create_application()

            # Assert - verify all three commands are registered
            handler_calls = [call[0][0] for call in mock_app.add_handler.call_args_list]

            # Extract all registered commands
            all_commands = set()
            for handler in handler_calls:
                if hasattr(handler, "commands"):
                    all_commands.update(handler.commands)

            # Check that all notification commands are present
            expected_commands = {"notifications", "set_notification_time", "test_stats"}
            assert expected_commands.issubset(
                all_commands
            ), f"All notification commands should be registered. Found: {all_commands}"
