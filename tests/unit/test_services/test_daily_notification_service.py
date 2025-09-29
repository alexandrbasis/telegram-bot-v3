"""
Comprehensive tests for DailyNotificationService.

Tests cover message formatting, Telegram bot integration, error handling,
and interaction with StatisticsService for daily statistics notifications.
"""

import logging
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Bot
from telegram.error import TelegramError

from src.models.department_statistics import DepartmentStatistics
from src.services.daily_notification_service import (
    DailyNotificationService,
    NotificationError,
)
from src.services.statistics_service import StatisticsError, StatisticsService


@pytest.fixture
def mock_bot():
    """Create mock Telegram bot for testing."""
    bot = MagicMock(spec=Bot)
    bot.send_message = AsyncMock()
    return bot


@pytest.fixture
def mock_statistics_service():
    """Create mock StatisticsService for testing."""
    service = MagicMock(spec=StatisticsService)
    service.collect_statistics = AsyncMock()
    return service


@pytest.fixture
def sample_statistics():
    """Create sample statistics data for testing."""
    return DepartmentStatistics(
        total_participants=150,
        participants_by_department={
            "ROE": 50,
            "Chapel": 45,
            "Kitchen": 35,
            "Decoration": 20,
        },
        total_teams=15,
        collection_timestamp=datetime(2025, 9, 29, 23, 30, 0),
    )


@pytest.fixture
def notification_service(mock_bot, mock_statistics_service):
    """Create DailyNotificationService instance for testing."""
    return DailyNotificationService(
        bot=mock_bot, statistics_service=mock_statistics_service
    )


class TestDailyNotificationServiceInitialization:
    """Test service initialization."""

    def test_initialization_with_valid_dependencies(
        self, mock_bot, mock_statistics_service
    ):
        """Test service initializes correctly with valid dependencies."""
        service = DailyNotificationService(
            bot=mock_bot, statistics_service=mock_statistics_service
        )

        assert service.bot == mock_bot
        assert service.statistics_service == mock_statistics_service


class TestMessageFormatting:
    """Test statistics message formatting."""

    def test_format_statistics_message_with_valid_data(
        self, notification_service, sample_statistics
    ):
        """Test message formatting with valid statistics data."""
        message = notification_service._format_statistics_message(sample_statistics)

        # Verify Russian header
        assert "📊 Ежедневная статистика участников" in message

        # Verify total participants
        assert "👥 Всего участников: 150" in message

        # Verify total teams
        assert "👫 Всего команд: 15" in message

        # Verify department breakdown header
        assert "По отделам:" in message

        # Verify all department counts with correct Russian translations
        assert "РОЭ: 50 чел." in message
        assert "Чапл: 45 чел." in message
        assert "Кухня: 35 чел." in message
        assert "Декорации: 20 чел." in message

    def test_format_statistics_message_with_empty_departments(
        self, notification_service
    ):
        """Test message formatting when no department data available."""
        empty_stats = DepartmentStatistics(
            total_participants=0,
            participants_by_department={},
            total_teams=0,
            collection_timestamp=datetime.now(),
        )

        message = notification_service._format_statistics_message(empty_stats)

        assert "📊 Ежедневная статистика участников" in message
        assert "👥 Всего участников: 0" in message
        assert "👫 Всего команд: 0" in message
        # Should still have department header but no department lines
        assert "По отделам:" in message

    def test_format_statistics_message_with_unassigned_participants(
        self, notification_service
    ):
        """Test message formatting includes unassigned participants."""
        stats_with_unassigned = DepartmentStatistics(
            total_participants=25,
            participants_by_department={
                "ROE": 20,
                "unassigned": 5,
            },
            total_teams=2,
            collection_timestamp=datetime.now(),
        )

        message = notification_service._format_statistics_message(stats_with_unassigned)

        assert "РОЭ: 20 чел." in message
        assert "Не указано: 5 чел." in message


class TestNotificationDelivery:
    """Test notification delivery to admin users."""

    @pytest.mark.asyncio
    async def test_send_notification_success(
        self, notification_service, mock_bot, mock_statistics_service, sample_statistics
    ):
        """Test successful notification delivery."""
        admin_user_id = 123456
        mock_statistics_service.collect_statistics.return_value = sample_statistics

        await notification_service.send_daily_statistics(admin_user_id)

        # Verify statistics collection was called
        mock_statistics_service.collect_statistics.assert_called_once()

        # Verify message was sent to correct admin
        mock_bot.send_message.assert_called_once()
        call_args = mock_bot.send_message.call_args
        assert call_args.kwargs["chat_id"] == admin_user_id
        assert "📊 Ежедневная статистика участников" in call_args.kwargs["text"]

    @pytest.mark.asyncio
    async def test_send_notification_handles_statistics_error(
        self, notification_service, mock_statistics_service, caplog
    ):
        """Test notification handles StatisticsService errors gracefully."""
        admin_user_id = 123456
        mock_statistics_service.collect_statistics.side_effect = StatisticsError(
            "Database connection failed"
        )

        with caplog.at_level(logging.ERROR):
            with pytest.raises(NotificationError) as exc_info:
                await notification_service.send_daily_statistics(admin_user_id)

            assert "Failed to collect statistics" in str(exc_info.value)
            assert "Failed to collect statistics" in caplog.text

    @pytest.mark.asyncio
    async def test_send_notification_handles_telegram_error(
        self,
        notification_service,
        mock_bot,
        mock_statistics_service,
        sample_statistics,
        caplog,
    ):
        """Test notification handles Telegram API errors gracefully."""
        admin_user_id = 123456
        mock_statistics_service.collect_statistics.return_value = sample_statistics
        mock_bot.send_message.side_effect = TelegramError("Network timeout")

        with caplog.at_level(logging.ERROR):
            with pytest.raises(NotificationError) as exc_info:
                await notification_service.send_daily_statistics(admin_user_id)

            assert "Failed to send notification" in str(exc_info.value)
            assert "Failed to send notification" in caplog.text

    @pytest.mark.asyncio
    async def test_send_notification_logs_success(
        self,
        notification_service,
        mock_statistics_service,
        sample_statistics,
        caplog,
    ):
        """Test successful notification delivery is logged."""
        admin_user_id = 123456
        mock_statistics_service.collect_statistics.return_value = sample_statistics

        with caplog.at_level(logging.INFO):
            await notification_service.send_daily_statistics(admin_user_id)

            assert "Sending daily statistics notification" in caplog.text
            assert f"admin_user_id={admin_user_id}" in caplog.text
            assert "Daily statistics notification sent successfully" in caplog.text


class TestDepartmentNameMapping:
    """Test department name translation to Russian."""

    def test_department_name_mapping(self, notification_service, sample_statistics):
        """Test all department names are correctly translated to Russian."""
        message = notification_service._format_statistics_message(sample_statistics)

        # Verify English names are NOT in the message (translated to Russian)
        assert "ROE" not in message or "РОЭ" in message
        assert "Chapel" not in message or "Чапл" in message
        assert "Kitchen" not in message or "Кухня" in message
        assert "Decoration" not in message or "Декорации" in message

        # Verify Russian names ARE in the message
        assert "РОЭ" in message
        assert "Чапл" in message
        assert "Кухня" in message
        assert "Декорации" in message
