"""Tests for notification admin command handlers."""

from datetime import time
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Message, Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.notification_admin_handlers import (
    handle_notifications_command,
    handle_set_notification_time_command,
    handle_test_stats_command,
)
from src.config.settings import NotificationSettings, Settings


@pytest.fixture
def mock_settings():
    """Create mock settings with notification configuration."""
    settings = MagicMock(spec=Settings)
    settings.notification = NotificationSettings()
    settings.notification.daily_stats_enabled = True
    settings.notification.notification_time = "09:00"
    settings.notification.timezone = "Europe/Moscow"
    settings.notification.admin_user_id = 123456
    settings.telegram = MagicMock()
    settings.telegram.admin_user_ids = [123456, 789012]
    return settings


@pytest.fixture
def mock_update():
    """Create mock Telegram update with message and user."""
    update = MagicMock(spec=Update)
    update.effective_message = AsyncMock(spec=Message)
    update.effective_user = MagicMock(spec=User)
    update.effective_user.id = 123456  # Admin user
    update.effective_user.username = "test_admin"
    return update


@pytest.fixture
def mock_context(mock_settings):
    """Create mock context with settings."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.bot_data = {"settings": mock_settings}
    context.args = []
    return context


class TestNotificationsCommand:
    """Test /notifications command functionality."""

    @pytest.mark.asyncio
    async def test_show_current_status_enabled(
        self, mock_update, mock_context, mock_settings
    ):
        """Test showing current notification status when enabled."""
        # Arrange
        mock_settings.notification.daily_stats_enabled = True

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "📊 Статус уведомлений" in reply_text
        assert "✅ Включены" in reply_text
        assert "09:00" in reply_text
        assert "Europe/Moscow" in reply_text

    @pytest.mark.asyncio
    async def test_show_current_status_disabled(
        self, mock_update, mock_context, mock_settings
    ):
        """Test showing current notification status when disabled."""
        # Arrange
        mock_settings.notification.daily_stats_enabled = False

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "📊 Статус уведомлений" in reply_text
        assert "❌ Выключены" in reply_text

    @pytest.mark.asyncio
    async def test_enable_notifications(self, mock_update, mock_context, mock_settings):
        """Test enabling notifications via 'on' argument."""
        # Arrange
        mock_context.args = ["on"]
        mock_settings.notification.daily_stats_enabled = False

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        assert mock_settings.notification.daily_stats_enabled is True
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "✅" in reply_text
        assert "включены" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_disable_notifications(
        self, mock_update, mock_context, mock_settings
    ):
        """Test disabling notifications via 'off' argument."""
        # Arrange
        mock_context.args = ["off"]
        mock_settings.notification.daily_stats_enabled = True

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        assert mock_settings.notification.daily_stats_enabled is False
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "✅" in reply_text
        assert "выключены" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_non_admin_access_denied(
        self, mock_update, mock_context, mock_settings
    ):
        """Test access denied for non-admin users."""
        # Arrange
        mock_update.effective_user.id = 999999  # Non-admin user

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "🚫" in reply_text
        assert "нет прав" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_missing_settings(self, mock_update, mock_context):
        """Test handling when settings are not available."""
        # Arrange
        mock_context.bot_data = {}

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "⚠️" in reply_text
        assert "недоступны" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_invalid_argument(self, mock_update, mock_context):
        """Test invalid argument handling."""
        # Arrange
        mock_context.args = ["invalid"]

        # Act
        await handle_notifications_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "⚠️" in reply_text
        assert "on" in reply_text
        assert "off" in reply_text


class TestSetNotificationTimeCommand:
    """Test /set_notification_time command functionality."""

    @pytest.mark.asyncio
    async def test_set_valid_time(self, mock_update, mock_context, mock_settings):
        """Test setting valid notification time."""
        # Arrange
        mock_context.args = ["14:30"]

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        assert mock_settings.notification.notification_time == "14:30"
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "✅" in reply_text
        assert "14:30" in reply_text

    @pytest.mark.asyncio
    async def test_set_time_with_timezone(
        self, mock_update, mock_context, mock_settings
    ):
        """Test setting time with timezone."""
        # Arrange
        mock_context.args = ["14:30", "America/New_York"]

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        assert mock_settings.notification.notification_time == "14:30"
        assert mock_settings.notification.timezone == "America/New_York"
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "✅" in reply_text
        assert "14:30" in reply_text
        assert "America/New_York" in reply_text

    @pytest.mark.asyncio
    async def test_invalid_time_format(self, mock_update, mock_context):
        """Test handling invalid time format."""
        # Arrange
        mock_context.args = ["25:00"]  # Invalid hour

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "⚠️" in reply_text
        assert "формат" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_invalid_timezone(self, mock_update, mock_context):
        """Test handling invalid timezone."""
        # Arrange
        mock_context.args = ["14:30", "Invalid/Timezone"]

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "⚠️" in reply_text
        assert "часовой пояс" in reply_text.lower()

    @pytest.mark.asyncio
    async def test_missing_arguments(self, mock_update, mock_context):
        """Test handling missing time argument."""
        # Arrange
        mock_context.args = []

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "⚠️" in reply_text or "ℹ️" in reply_text
        assert "HH:MM" in reply_text

    @pytest.mark.asyncio
    async def test_non_admin_access_denied(
        self, mock_update, mock_context, mock_settings
    ):
        """Test access denied for non-admin users."""
        # Arrange
        mock_update.effective_user.id = 999999
        mock_context.args = ["14:30"]

        # Act
        await handle_set_notification_time_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "🚫" in reply_text
        assert "нет прав" in reply_text.lower()


class TestTestStatsCommand:
    """Test /test_stats command functionality."""

    @pytest.mark.asyncio
    async def test_send_test_notification_success(
        self, mock_update, mock_context, mock_settings
    ):
        """Test successful test notification delivery."""
        # Arrange
        with (
            patch(
                "src.bot.handlers.notification_admin_handlers.get_participant_repository"
            ) as mock_repo_factory,
            patch(
                "src.bot.handlers.notification_admin_handlers.StatisticsService"
            ) as mock_stats_service_class,
            patch(
                "src.bot.handlers.notification_admin_handlers.DailyNotificationService"
            ) as mock_notif_service_class,
        ):

            mock_repo = MagicMock()
            mock_repo_factory.return_value = mock_repo

            mock_stats_service = MagicMock()
            mock_stats_service_class.return_value = mock_stats_service

            mock_notif_service = MagicMock()
            mock_notif_service.send_daily_statistics = AsyncMock()
            mock_notif_service_class.return_value = mock_notif_service

            # Act
            await handle_test_stats_command(mock_update, mock_context)

            # Assert
            mock_notif_service.send_daily_statistics.assert_called_once_with(123456)
            mock_update.effective_message.reply_text.assert_called()
            # Should have two calls: sending + success
            assert mock_update.effective_message.reply_text.call_count == 2

    @pytest.mark.asyncio
    async def test_send_test_notification_failure(
        self, mock_update, mock_context, mock_settings
    ):
        """Test handling notification delivery failure."""
        # Arrange
        with (
            patch(
                "src.bot.handlers.notification_admin_handlers.get_participant_repository"
            ) as mock_repo_factory,
            patch(
                "src.bot.handlers.notification_admin_handlers.StatisticsService"
            ) as mock_stats_service_class,
            patch(
                "src.bot.handlers.notification_admin_handlers.DailyNotificationService"
            ) as mock_notif_service_class,
        ):

            mock_repo = MagicMock()
            mock_repo_factory.return_value = mock_repo

            mock_stats_service = MagicMock()
            mock_stats_service_class.return_value = mock_stats_service

            mock_notif_service = MagicMock()
            mock_notif_service.send_daily_statistics = AsyncMock(
                side_effect=Exception("Test error")
            )
            mock_notif_service_class.return_value = mock_notif_service

            # Act
            await handle_test_stats_command(mock_update, mock_context)

            # Assert
            mock_update.effective_message.reply_text.assert_called()
            # Find the error message call
            calls = mock_update.effective_message.reply_text.call_args_list
            error_call = next(
                (
                    call
                    for call in calls
                    if "⚠️" in str(call) or "ошибка" in str(call).lower()
                ),
                None,
            )
            assert error_call is not None

    @pytest.mark.asyncio
    async def test_non_admin_access_denied(
        self, mock_update, mock_context, mock_settings
    ):
        """Test access denied for non-admin users."""
        # Arrange
        mock_update.effective_user.id = 999999

        # Act
        await handle_test_stats_command(mock_update, mock_context)

        # Assert
        mock_update.effective_message.reply_text.assert_called_once()
        reply_text = mock_update.effective_message.reply_text.call_args[0][0]
        assert "🚫" in reply_text
        assert "нет прав" in reply_text.lower()
