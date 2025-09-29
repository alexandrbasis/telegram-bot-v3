"""
Daily notification service for automated statistics delivery.

Provides message formatting and delivery of daily participant statistics
to configured admin users with Russian localization and error handling.
"""

import logging
from typing import Dict

from telegram import Bot
from telegram.error import TelegramError

from src.models.department_statistics import DepartmentStatistics
from src.services.statistics_service import StatisticsError, StatisticsService

logger = logging.getLogger(__name__)


class NotificationError(Exception):
    """Custom exception for notification delivery errors."""

    pass


class DailyNotificationService:
    """
    Service for formatting and delivering daily statistics notifications.

    Integrates with StatisticsService for data collection and Telegram Bot
    for message delivery with professional Russian-localized formatting.
    """

    # Department name mapping: English → Russian with emoji
    DEPARTMENT_NAMES: Dict[str, str] = {
        "Palorm": "🎭 Палорма",
        "Secuela": "⛪️ Секуэла",
        "Rocha": "🎨 Роя",
        "Clausura": "📿 Клаусура",
        "unassigned": "❓ Без отдела",
    }

    def __init__(self, bot: Bot, statistics_service: StatisticsService):
        """
        Initialize notification service with dependencies.

        Args:
            bot: Telegram bot instance for message delivery
            statistics_service: Service for statistics collection
        """
        self.bot = bot
        self.statistics_service = statistics_service
        logger.info("Initialized DailyNotificationService")

    def _format_statistics_message(self, statistics: DepartmentStatistics) -> str:
        """
        Format statistics data into Russian-localized message.

        Args:
            statistics: Statistics data to format

        Returns:
            Formatted message string with Russian text and emoji
        """
        # Build message header
        message_lines = [
            "📊 Ежедневная статистика участников",
            "",
            f"👥 Всего участников: {statistics.total_participants}",
            f"👫 Всего команд: {statistics.total_teams}",
            "",
            "По отделам:",
        ]

        # Add department breakdown
        for dept_name, count in statistics.participants_by_department.items():
            # Translate department name to Russian with emoji
            russian_name = self.DEPARTMENT_NAMES.get(dept_name, f"❓ {dept_name}")
            message_lines.append(f"{russian_name}: {count} чел.")

        return "\n".join(message_lines)

    async def send_daily_statistics(self, admin_user_id: int) -> None:
        """
        Collect statistics and send notification to admin user.

        Args:
            admin_user_id: Telegram user ID of admin recipient

        Raises:
            NotificationError: If statistics collection or delivery fails
        """
        logger.info(
            f"Sending daily statistics notification to admin_user_id={admin_user_id}"
        )

        try:
            # Collect current statistics
            logger.debug("Collecting statistics from StatisticsService")
            statistics = await self.statistics_service.collect_statistics()

            # Format message
            message = self._format_statistics_message(statistics)
            logger.debug(f"Formatted statistics message ({len(message)} chars)")

            # Send notification via Telegram
            await self.bot.send_message(chat_id=admin_user_id, text=message)

            logger.info(
                f"Daily statistics notification sent successfully to "
                f"admin_user_id={admin_user_id}"
            )

        except StatisticsError as e:
            logger.error(
                f"Failed to collect statistics for notification: {type(e).__name__}"
            )
            logger.debug(f"Statistics error details: {e}")
            raise NotificationError("Failed to collect statistics") from e

        except TelegramError as e:
            logger.error(
                f"Failed to send notification via Telegram: {type(e).__name__}"
            )
            logger.debug(f"Telegram error details: {e}")
            raise NotificationError("Failed to send notification") from e

        except Exception as e:
            logger.error(
                f"Unexpected error during notification delivery: {type(e).__name__}"
            )
            logger.debug(f"Full error details: {e}")
            raise NotificationError("Notification delivery failed") from e
