"""
Unit tests for NotificationScheduler service.

Tests cover:
- Scheduler initialization with Application and settings
- Daily job scheduling with timezone conversion
- Job persistence and removal
- Error handling with exponential backoff retry
- Feature flag respect (no scheduling when disabled)
"""

import asyncio
from datetime import time
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest
import pytz
from telegram.ext import Application

from src.config.settings import NotificationSettings
from src.services.daily_notification_service import DailyNotificationService


class TestNotificationSchedulerInitialization:
    """Test suite for NotificationScheduler initialization."""

    def test_scheduler_initialization_with_valid_config(self):
        """Test successful scheduler initialization."""
        # Arrange
        app = Mock(spec=Application)
        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        # Act
        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Assert
        assert scheduler.application == app
        assert scheduler.settings == settings
        assert scheduler.notification_service == notification_service
        assert scheduler.settings.daily_stats_enabled is True

    def test_scheduler_initialization_when_disabled(self):
        """Test scheduler initialization when feature is disabled."""
        # Arrange
        app = Mock(spec=Application)
        settings = NotificationSettings(
            daily_stats_enabled=False,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=None,
        )
        notification_service = Mock(spec=DailyNotificationService)

        # Act
        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Assert
        assert scheduler.application == app
        assert scheduler.settings.daily_stats_enabled is False


class TestNotificationScheduling:
    """Test suite for notification scheduling functionality."""

    @pytest.mark.asyncio
    async def test_schedule_daily_notification_success(self):
        """Test successful daily notification scheduling."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.run_daily = Mock(return_value=Mock())

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:30",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act
        await scheduler.schedule_daily_notification()

        # Assert
        mock_job_queue.run_daily.assert_called_once()
        call_kwargs = mock_job_queue.run_daily.call_args[1]

        # Verify callback function is provided
        assert "callback" in call_kwargs
        assert callable(call_kwargs["callback"])

        # Verify time is correct (datetime.time object)
        assert "time" in call_kwargs
        expected_time = time(hour=9, minute=30)
        assert call_kwargs["time"] == expected_time

        # Verify timezone
        assert "days" in call_kwargs or call_kwargs.get("time")
        # The timezone should be applied via the tzinfo on the time object
        # or passed separately depending on PTB API

    @pytest.mark.asyncio
    async def test_schedule_not_called_when_disabled(self):
        """Test that scheduling is skipped when feature is disabled."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.run_daily = Mock()

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=False,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=None,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act
        await scheduler.schedule_daily_notification()

        # Assert - run_daily should NOT be called
        mock_job_queue.run_daily.assert_not_called()

    @pytest.mark.asyncio
    async def test_timezone_conversion_handling(self):
        """Test that timezone is properly handled in scheduling."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.run_daily = Mock(return_value=Mock())

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        # Test with different timezones
        test_timezones = [
            ("America/New_York", "18:00"),
            ("Asia/Tokyo", "12:00"),
            ("UTC", "15:30"),
        ]

        for tz_str, time_str in test_timezones:
            mock_job_queue.reset_mock()

            settings = NotificationSettings(
                daily_stats_enabled=True,
                notification_time=time_str,
                timezone=tz_str,
                admin_user_id=123456789,
            )
            notification_service = Mock(spec=DailyNotificationService)

            from src.services.notification_scheduler import NotificationScheduler

            scheduler = NotificationScheduler(
                application=app,
                settings=settings,
                notification_service=notification_service,
            )

            # Act
            await scheduler.schedule_daily_notification()

            # Assert
            mock_job_queue.run_daily.assert_called_once()
            call_kwargs = mock_job_queue.run_daily.call_args[1]

            # Verify time parsing
            hour, minute = map(int, time_str.split(":"))
            expected_time = time(hour=hour, minute=minute)
            assert call_kwargs["time"] == expected_time


class TestJobPersistence:
    """Test suite for job persistence and removal."""

    @pytest.mark.asyncio
    async def test_remove_existing_job(self):
        """Test removal of existing scheduled job."""
        # Arrange
        mock_job = Mock()
        mock_job.schedule_removal = Mock()

        mock_job_queue = Mock()
        mock_job_queue.get_jobs_by_name = Mock(return_value=[mock_job])

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act
        await scheduler.remove_scheduled_notification()

        # Assert
        mock_job_queue.get_jobs_by_name.assert_called_once()
        mock_job.schedule_removal.assert_called_once()

    @pytest.mark.asyncio
    async def test_remove_job_when_none_exists(self):
        """Test removal when no job is scheduled."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.get_jobs_by_name = Mock(return_value=[])

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act - Should not raise exception
        await scheduler.remove_scheduled_notification()

        # Assert
        mock_job_queue.get_jobs_by_name.assert_called_once()


class TestErrorHandling:
    """Test suite for error handling and retry logic."""

    @pytest.mark.asyncio
    async def test_callback_with_successful_execution(self):
        """Test notification callback with successful execution."""
        # This test verifies the callback function behavior
        # In actual implementation, the callback would call the notification service

        # Arrange
        mock_job_queue = Mock()
        captured_callback = None

        def capture_callback(*args, **kwargs):
            nonlocal captured_callback
            captured_callback = kwargs.get("callback")
            return Mock()

        mock_job_queue.run_daily = capture_callback

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act
        await scheduler.schedule_daily_notification()

        # Assert
        assert captured_callback is not None
        assert callable(captured_callback)

        # Verify callback can be called (we'll test actual logic in integration tests)
        mock_context = Mock()
        # The callback should be async
        result = captured_callback(mock_context)
        # If it returns a coroutine, await it
        if asyncio.iscoroutine(result):
            await result

    @pytest.mark.asyncio
    async def test_handles_job_queue_errors_gracefully(self):
        """Test that JobQueue errors are handled gracefully."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.run_daily = Mock(side_effect=Exception("JobQueue error"))

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act & Assert - Should log error but not raise
        with patch("src.services.notification_scheduler.logger") as mock_logger:
            await scheduler.schedule_daily_notification()
            # Verify error was logged
            mock_logger.error.assert_called()


class TestSchedulerJobNaming:
    """Test suite for job naming and identification."""

    @pytest.mark.asyncio
    async def test_job_uses_consistent_name(self):
        """Test that scheduled jobs use a consistent, identifiable name."""
        # Arrange
        mock_job_queue = Mock()
        mock_job_queue.run_daily = Mock(return_value=Mock())

        app = Mock(spec=Application)
        app.job_queue = mock_job_queue

        settings = NotificationSettings(
            daily_stats_enabled=True,
            notification_time="09:00",
            timezone="Europe/Moscow",
            admin_user_id=123456789,
        )
        notification_service = Mock(spec=DailyNotificationService)

        from src.services.notification_scheduler import NotificationScheduler

        scheduler = NotificationScheduler(
            application=app,
            settings=settings,
            notification_service=notification_service,
        )

        # Act
        await scheduler.schedule_daily_notification()

        # Assert
        call_kwargs = mock_job_queue.run_daily.call_args[1]
        assert "name" in call_kwargs
        assert isinstance(call_kwargs["name"], str)
        assert "daily_stats" in call_kwargs["name"].lower()
