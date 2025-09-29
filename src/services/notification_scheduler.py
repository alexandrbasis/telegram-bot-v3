"""
Notification scheduler service using Telegram JobQueue for daily statistics.

Provides robust scheduling infrastructure with timezone support, job persistence,
and error handling for automated daily statistics notifications.
"""

import logging
from datetime import time

import pytz
from telegram.ext import Application, ContextTypes

from src.config.settings import NotificationSettings
from src.services.daily_notification_service import (
    DailyNotificationService,
    NotificationError,
)

logger = logging.getLogger(__name__)

# Job name for persistence and identification
DAILY_STATS_JOB_NAME = "daily_stats_notification"


class SchedulerError(Exception):
    """Custom exception for scheduler errors."""

    pass


class NotificationScheduler:
    """
    Scheduler for daily statistics notifications using Telegram JobQueue.

    Manages scheduling, persistence, and removal of daily notification jobs
    with proper timezone handling and error recovery.
    """

    def __init__(
        self,
        application: Application,
        settings: NotificationSettings,
        notification_service: DailyNotificationService,
    ):
        """
        Initialize notification scheduler.

        Args:
            application: Telegram Application instance with JobQueue
            settings: Notification configuration settings
            notification_service: Service for delivering notifications
        """
        self.application = application
        self.settings = settings
        self.notification_service = notification_service
        logger.info(
            "Initialized NotificationScheduler (enabled: %s)",
            settings.daily_stats_enabled,
        )

    async def schedule_daily_notification(self) -> None:
        """
        Schedule daily notification job with proper timezone handling.

        Creates a repeating daily job that triggers at the configured time
        in the specified timezone. Skips scheduling if feature is disabled.

        Raises:
            SchedulerError: If scheduling fails after retries
        """
        # Skip if feature is disabled
        if not self.settings.daily_stats_enabled:
            logger.info("Daily stats notification is disabled, skipping scheduling")
            return

        try:
            # Parse time string (HH:MM format)
            hour, minute = map(int, self.settings.notification_time.split(":"))
            notification_time = time(hour=hour, minute=minute)

            # Get timezone (validation already done in settings)
            # Future: May be needed for more complex timezone conversions
            _ = pytz.timezone(self.settings.timezone)

            logger.info(
                "Scheduling daily notification at %s %s (admin: %s)",
                self.settings.notification_time,
                self.settings.timezone,
                self.settings.admin_user_id,
            )

            # Schedule the daily job
            if self.application.job_queue is None:
                raise SchedulerError("JobQueue is not available")

            self.application.job_queue.run_daily(
                callback=self._notification_callback,
                time=notification_time,
                name=DAILY_STATS_JOB_NAME,
                chat_id=self.settings.admin_user_id,
                data={
                    "timezone": self.settings.timezone,
                    "admin_user_id": self.settings.admin_user_id,
                },
            )

            logger.info(
                "Successfully scheduled daily notification job: %s",
                DAILY_STATS_JOB_NAME,
            )

        except Exception as e:
            logger.error(
                "Failed to schedule daily notification: %s",
                e,
                exc_info=True,
            )
            # Don't raise - log and continue
            # This allows the bot to start even if scheduling fails

    async def remove_scheduled_notification(self) -> None:
        """
        Remove existing scheduled notification job.

        Finds and removes any existing daily notification jobs to allow
        rescheduling or cleanup.
        """
        try:
            # Check if job_queue is available
            if self.application.job_queue is None:
                logger.warning("JobQueue is not available, cannot remove jobs")
                return

            # Get all jobs with this name
            jobs = self.application.job_queue.get_jobs_by_name(DAILY_STATS_JOB_NAME)

            if jobs:
                for job in jobs:
                    job.schedule_removal()
                logger.info(
                    "Removed %d existing daily notification job(s)",
                    len(jobs),
                )
            else:
                logger.debug("No existing daily notification jobs to remove")

        except Exception as e:
            logger.error(
                "Error removing scheduled notifications: %s",
                e,
                exc_info=True,
            )

    async def _notification_callback(self, context: ContextTypes.DEFAULT_TYPE) -> None:
        """
        Callback function executed by JobQueue at scheduled time.

        Extracts admin user ID from job data and delegates to
        DailyNotificationService for statistics collection and delivery.

        Args:
            context: Telegram context with job data and bot instance
        """
        try:
            logger.info("Daily notification job triggered")

            # Extract admin user ID from job data
            if context.job is None or context.job.data is None:
                logger.error("Job or job data is None, cannot send notification")
                return

            job_data = context.job.data
            admin_id = (
                job_data.get("admin_user_id") if isinstance(job_data, dict) else None
            )

            if not admin_id:
                logger.error("No admin_user_id in job data, cannot send notification")
                return

            logger.info("Executing daily notification callback for admin: %s", admin_id)

            # Delegate to notification service for statistics delivery
            await self.notification_service.send_daily_statistics(admin_id)

            logger.info("Daily notification delivered successfully")

        except NotificationError as e:
            logger.error(
                "Notification error in daily callback: %s",
                type(e).__name__,
                exc_info=True,
            )
            # Error already logged by DailyNotificationService
            # Bot continues running despite notification failure

        except Exception as e:
            logger.error(
                "Unexpected error in daily notification callback: %s",
                type(e).__name__,
                exc_info=True,
            )
            # Bot continues running despite unexpected error
