"""
Tests for CSV export command handlers.

Tests the /export command functionality including admin authentication,
progress notifications, and error handling.
"""

import asyncio
import tempfile
from datetime import datetime
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch

import pytest
from telegram import Message, Update, User
from telegram.error import BadRequest, NetworkError, RetryAfter, TelegramError
from telegram.ext import ContextTypes

from src.bot.handlers.export_handlers import (
    handle_export_command,
    handle_export_progress,
)
from src.config.settings import Settings
from src.models.participant import Participant, Role


class TestExportCommandHandler:
    """Test /export command handler functionality."""

    @pytest.fixture
    def mock_update(self):
        """Create mock update with export command."""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "/export"
        update.message.reply_text = AsyncMock()
        update.message.reply_document = AsyncMock()

        # Mock user
        user = Mock(spec=User)
        user.id = 123456
        user.username = "testuser"
        update.message.from_user = user
        update.effective_user = user

        return update

    @pytest.fixture
    def mock_context(self):
        """Create mock context with settings."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        context.bot_data = {}

        # Mock settings with proper telegram attribute
        settings = Mock()
        settings.telegram = Mock()
        settings.telegram.admin_user_ids = [123456, 789012]
        context.bot_data["settings"] = settings

        return context

    @pytest.fixture
    def mock_export_service(self):
        """Create mock export service."""
        service = Mock()
        service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        service.save_to_file = AsyncMock()
        service.is_within_telegram_limit = AsyncMock(return_value=True)
        service.estimate_file_size = AsyncMock(return_value=1000)
        return service

    @pytest.fixture
    def mock_participants(self):
        """Create mock participants for testing."""
        return [
            Participant(
                id="1",
                name="Test User 1",
                full_name_ru="Тестовый Пользователь 1",
                role=Role.TEAM,
                email="test1@example.com",
            ),
            Participant(
                id="2",
                name="Test User 2",
                full_name_ru="Тестовый Пользователь 2",
                role=Role.CANDIDATE,
                email="test2@example.com",
            ),
        ]

    @pytest.mark.asyncio
    async def test_export_command_admin_user_success(
        self, mock_update, mock_context, mock_export_service
    ):
        """Test that admin users can successfully export data."""
        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # Should send initial processing message
            assert mock_update.message.reply_text.call_count >= 1
            first_call = mock_update.message.reply_text.call_args_list[0]
            assert "Начинаю экспорт" in first_call[0][0]

            # Should call export service
            mock_export_service.export_to_csv_async.assert_called_once()

            # Should send document with CSV file
            mock_update.message.reply_document.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_command_non_admin_denied(self, mock_update, mock_context):
        """Test that non-admin users are denied access."""
        # Set user as non-admin
        mock_update.effective_user.id = 999999

        await handle_export_command(mock_update, mock_context)

        # Should send access denied message
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert "У вас нет прав" in call_args[0][0]

        # Should not send document
        mock_update.message.reply_document.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_command_progress_notifications(
        self, mock_update, mock_context, mock_export_service, mock_participants
    ):
        """Test that progress notifications are sent during export."""
        # For this test, we'll just verify the progress callback is passed
        # The actual progress notification is tested separately
        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
        ) as mock_get_service:
            mock_get_service.return_value = mock_export_service

            await handle_export_command(mock_update, mock_context)

            # Verify get_export_service was called with a progress callback
            mock_get_service.assert_called_once()
            call_args = mock_get_service.call_args
            assert "progress_callback" in call_args[1]
            assert call_args[1]["progress_callback"] is not None

    @pytest.mark.asyncio
    async def test_export_command_empty_data(self, mock_update, mock_context):
        """Test handling when no participants exist."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(return_value="")
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # Should inform user about empty data
            calls = mock_update.message.reply_text.call_args_list
            assert any("нет данных" in call[0][0].lower() for call in calls)

    @pytest.mark.asyncio
    async def test_export_command_file_size_limit_exceeded(
        self, mock_update, mock_context, mock_export_service
    ):
        """Test handling when file exceeds Telegram size limit."""
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=False)
        mock_export_service.estimate_file_size = AsyncMock(
            return_value=60_000_000
        )  # 60MB

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # Should warn about file size
            calls = mock_update.message.reply_text.call_args_list
            assert any(
                "превышает лимит" in call[0][0].lower()
                or "слишком большой" in call[0][0].lower()
                or "предупреждение" in call[0][0].lower()
                for call in calls
            )

    @pytest.mark.asyncio
    async def test_export_command_error_handling(self, mock_update, mock_context):
        """Test proper error handling during export."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            side_effect=Exception("Database connection failed")
        )

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # Should send error message to user
            calls = mock_update.message.reply_text.call_args_list
            assert any(
                "ошибка" in call[0][0].lower() or "не удалось" in call[0][0].lower()
                for call in calls
            )

            # Should not send document
            mock_update.message.reply_document.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_command_with_none_settings(self, mock_update):
        """Test handling when settings are not available."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.bot_data = {}  # No settings

        await handle_export_command(mock_update, context)

        # Should handle gracefully
        mock_update.message.reply_text.assert_called()
        call_args = mock_update.message.reply_text.call_args
        assert "ошибка" in call_args[0][0].lower()

    @pytest.mark.asyncio
    async def test_export_progress_callback_throttling(
        self, mock_update, mock_context, mock_export_service
    ):
        """Test that progress notifications are throttled."""
        progress_calls = []

        async def track_progress(*args, **kwargs):
            progress_calls.append(datetime.now())
            return Mock()

        mock_update.message.reply_text.side_effect = track_progress

        # Simulate many rapid progress updates
        def export_with_many_updates(progress_callback=None):
            if progress_callback:
                for i in range(101):  # 101 progress updates
                    progress_callback(i, 100)
            return "data"

        mock_export_service.export_to_csv.side_effect = export_with_many_updates

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # Should throttle updates (not send all 101)
            # Expecting significantly fewer messages due to throttling
            assert len(progress_calls) < 20  # Reasonable throttled amount

    @pytest.mark.asyncio
    async def test_export_command_cleanup_on_error(
        self, mock_update, mock_context, mock_export_service
    ):
        """Test that temporary files are cleaned up on error."""
        temp_file_path = None

        def save_file_mock(path):
            nonlocal temp_file_path
            temp_file_path = path
            # Create actual temp file to test cleanup
            Path(path).write_text("test data")
            raise Exception("Save failed")

        mock_export_service.save_to_file = Mock(side_effect=save_file_mock)

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(mock_update, mock_context)

            # File should be cleaned up even on error
            if temp_file_path:
                assert not Path(temp_file_path).exists()


class TestExportProgressHandler:
    """Test export progress notification handler."""

    @pytest.mark.asyncio
    async def test_handle_export_progress_formatting(self):
        """Test progress message formatting."""
        mock_update = Mock(spec=Update)
        mock_message = Mock(spec=Message)
        mock_message.reply_text = AsyncMock()

        # Test various progress percentages
        test_cases = [
            (0, 100, "0%"),
            (25, 100, "25%"),
            (50, 100, "50%"),
            (75, 100, "75%"),
            (100, 100, "100%"),
        ]

        for current, total, expected_percent in test_cases:
            await handle_export_progress(mock_message, current, total)

            # Should format percentage correctly
            call_args = mock_message.reply_text.call_args
            assert expected_percent in call_args[0][0]

    @pytest.mark.asyncio
    async def test_handle_export_progress_with_zero_total(self):
        """Test progress handler with zero total (edge case)."""
        mock_message = Mock(spec=Message)
        mock_message.reply_text = AsyncMock()

        await handle_export_progress(mock_message, 0, 0)

        # Should handle gracefully without division by zero
        mock_message.reply_text.assert_called_once()
        call_args = mock_message.reply_text.call_args
        # Should show some progress indication
        assert "экспорт" in call_args[0][0].lower()


class TestExportErrorHandling:
    """Test comprehensive error handling for file delivery scenarios."""

    @pytest.fixture
    def mock_update_with_file(self):
        """Create mock update for file delivery tests."""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = "/export"
        update.message.reply_text = AsyncMock()
        update.message.reply_document = AsyncMock()

        # Mock user
        user = Mock(spec=User)
        user.id = 123456
        user.username = "testuser"
        update.message.from_user = user
        update.effective_user = user

        return update

    @pytest.fixture
    def mock_context_with_settings(self):
        """Create mock context with settings."""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.user_data = {}
        context.bot_data = {}

        # Mock settings with proper telegram attribute
        settings = Mock()
        settings.telegram = Mock()
        settings.telegram.admin_user_ids = [123456, 789012]
        context.bot_data["settings"] = settings

        return context

    @pytest.mark.asyncio
    async def test_export_command_telegram_rate_limit_with_retry(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test RetryAfter error handling with automatic retry."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock RetryAfter error on first attempt, success on second
        retry_error = RetryAfter(retry_after=2)
        mock_update_with_file.message.reply_document.side_effect = [
            retry_error,
            None,  # Success on second attempt
        ]

        with (
            patch(
                "src.bot.handlers.export_handlers.service_factory.get_export_service",
                return_value=mock_export_service,
            ),
            patch("asyncio.sleep", return_value=None) as mock_sleep,
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should attempt retry
            assert mock_update_with_file.message.reply_document.call_count == 2
            mock_sleep.assert_called_once_with(4)  # retry_after + retry_delay

    @pytest.mark.asyncio
    async def test_export_command_file_too_large_error(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test BadRequest error for file too large."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock BadRequest with file too large error
        bad_request_error = BadRequest("Request Entity Too Large")
        mock_update_with_file.message.reply_document.side_effect = bad_request_error

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should send appropriate error message
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("слишком большой" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_export_command_invalid_file_error(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test BadRequest error for invalid file format."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock BadRequest with invalid file error
        bad_request_error = BadRequest("Invalid file format")
        mock_update_with_file.message.reply_document.side_effect = bad_request_error

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should send appropriate error message
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("формата файла" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_export_command_network_error_with_retries(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test NetworkError with retry logic."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock persistent network error
        network_error = NetworkError("Connection timeout")
        mock_update_with_file.message.reply_document.side_effect = network_error

        with (
            patch(
                "src.bot.handlers.export_handlers.service_factory.get_export_service",
                return_value=mock_export_service,
            ),
            patch("asyncio.sleep", return_value=None) as mock_sleep,
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should retry 3 times
            assert mock_update_with_file.message.reply_document.call_count == 3
            # Should send network error message
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("сети" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_export_command_general_telegram_error(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test general TelegramError handling."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock general Telegram error
        telegram_error = TelegramError("API Error")
        mock_update_with_file.message.reply_document.side_effect = telegram_error

        with patch(
            "src.bot.handlers.export_handlers.service_factory.get_export_service",
            return_value=mock_export_service,
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should send Telegram API error message
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("telegram api" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_export_command_file_size_check_before_upload(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test file size check before attempting upload."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock file creation that results in oversized file
        with (
            patch("tempfile.NamedTemporaryFile"),
            patch("pathlib.Path.stat") as mock_stat,
            patch(
                "src.bot.handlers.export_handlers.service_factory.get_export_service",
                return_value=mock_export_service,
            ),
        ):
            # Mock file size > 50MB
            mock_stat.return_value.st_size = 55 * 1024 * 1024  # 55MB

            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should send file too large message without attempting upload
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("слишком большой" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

            # Should not attempt document upload
            mock_update_with_file.message.reply_document.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_command_temp_file_creation_failure(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test handling of temporary file creation failure."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        # Mock tempfile creation failure
        with (
            patch(
                "src.bot.handlers.export_handlers.service_factory.get_export_service",
                return_value=mock_export_service,
            ),
            patch("tempfile.NamedTemporaryFile", side_effect=OSError("Disk full")),
        ):
            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should send error message about file creation
            error_calls = [
                call
                for call in mock_update_with_file.message.reply_text.call_args_list
                if any("создании файла" in str(arg).lower() for arg in call[0])
            ]
            assert len(error_calls) > 0

    @pytest.mark.asyncio
    async def test_export_command_user_interaction_logging(
        self, mock_update_with_file, mock_context_with_settings
    ):
        """Test that user interactions are properly logged."""
        mock_export_service = Mock()
        mock_export_service.export_to_csv_async = AsyncMock(
            return_value="field1,field2\nvalue1,value2"
        )
        mock_export_service.is_within_telegram_limit = AsyncMock(return_value=True)
        mock_export_service.estimate_file_size = AsyncMock(return_value=1000)

        with (
            patch(
                "src.bot.handlers.export_handlers.service_factory.get_export_service",
                return_value=mock_export_service,
            ),
            patch(
                "src.bot.handlers.export_handlers.UserInteractionLogger"
            ) as mock_logger_class,
        ):
            mock_logger = Mock()
            mock_logger_class.return_value = mock_logger

            await handle_export_command(
                mock_update_with_file, mock_context_with_settings
            )

            # Should log export initiation
            mock_logger.log_journey_step.assert_any_call(
                user_id=123456,
                step="export_command_initiated",
                context={"username": "testuser", "command": "/export"},
            )

            # Should log successful completion
            success_calls = [
                call
                for call in mock_logger.log_journey_step.call_args_list
                if call[1]["step"] == "export_completed_successfully"
            ]
            assert len(success_calls) > 0
