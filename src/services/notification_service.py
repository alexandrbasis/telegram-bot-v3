"""
Notification service for sending alerts and updates.

Handles sending notifications to admins and users about access requests,
with retry mechanisms for transient failures and proper error handling.
"""

import asyncio
import logging
from typing import Dict, Optional, List
from telegram import Bot
from telegram.error import TelegramError, NetworkError, BadRequest

from src.models.user_access_request import UserAccessRequest, AccessLevel


logger = logging.getLogger(__name__)


class NotificationService:
    """
    Service for sending notifications about access requests.

    Handles admin alerts for new requests and user notifications for decisions,
    with retry logic for network failures and localization support.
    """

    def __init__(self, bot: Bot, admin_ids: List[int]):
        """
        Initialize notification service.

        Args:
            bot: Telegram Bot instance for sending messages
            admin_ids: List of admin user IDs to notify
        """
        self.bot = bot
        self.admin_ids = admin_ids
        self.max_retries = 3
        self.retry_delay = 1.0  # seconds

    async def notify_admins_of_new_request(
        self, request: UserAccessRequest
    ) -> Dict[int, bool]:
        """
        Notify all admins about a new access request.

        Args:
            request: The new access request to notify about

        Returns:
            Dictionary mapping admin ID to success status
        """
        results = {}

        # Format display name
        display_name = f"@{request.telegram_username}" if request.telegram_username else "User"

        # Create notification message
        message = (
            f"🔔 Новый запрос на доступ: {display_name} ({request.telegram_user_id})."
        )

        # Send notifications concurrently to all admins
        tasks = []
        for admin_id in self.admin_ids:
            task = self._send_notification_async(admin_id, message)
            tasks.append(task)

        # Gather results concurrently
        task_results = await asyncio.gather(*tasks, return_exceptions=True)

        # Map results to admin IDs
        for admin_id, result in zip(self.admin_ids, task_results):
            if isinstance(result, Exception):
                results[admin_id] = False
                logger.error(f"Failed to notify admin {admin_id}: {result}")
            else:
                results[admin_id] = result
                if result:
                    logger.info(f"Successfully notified admin {admin_id} about new request")

        return results

    async def notify_user_decision(
        self,
        user_id: int,
        approved: bool,
        access_level: Optional[AccessLevel] = None,
        admin_notes: Optional[str] = None,
        language: str = "ru"
    ) -> bool:
        """
        Notify a user about the decision on their access request.

        Args:
            user_id: Telegram user ID to notify
            approved: Whether the request was approved
            access_level: Access level granted (if approved)
            admin_notes: Optional admin comments
            language: Language for the message (ru/en)

        Returns:
            True if notification was sent successfully
        """
        # Build message based on decision and language
        if approved:
            message = self._format_approval_message(access_level, admin_notes, language)
        else:
            message = self._format_denial_message(admin_notes, language)

        # Send notification with retry
        try:
            await self._send_with_retry(user_id, message)
            logger.info(f"Successfully notified user {user_id} of decision: approved={approved}")
            return True
        except Exception as e:
            logger.error(f"Failed to notify user {user_id} of decision: {e}")
            return False

    def _format_approval_message(
        self,
        access_level: Optional[AccessLevel],
        admin_notes: Optional[str],
        language: str
    ) -> str:
        """Format approval message based on language."""
        if language == "en":
            message = f"✅ You're all set! Assigned access level: {access_level.value if access_level else 'VIEWER'}."

            if admin_notes:
                message += f"\n\nAdmin note: {admin_notes}"

            message += "\n\nUse /start to begin working with the bot."
        else:  # Default to Russian
            message = f"✅ Доступ подтверждён! Ваша роль: {access_level.value if access_level else 'VIEWER'}."

            if admin_notes:
                message += f"\n\nКомментарий администратора: {admin_notes}"

            message += "\n\nИспользуйте /start для начала работы с ботом."

        return message

    def _format_denial_message(
        self,
        admin_notes: Optional[str],
        language: str
    ) -> str:
        """Format denial message based on language."""
        if language == "en":
            message = "❌ We weren't able to approve your access right now. Contact an admin if you believe this is a mistake."

            if admin_notes:
                message += f"\n\nAdmin note: {admin_notes}"
        else:  # Default to Russian
            message = "❌ К сожалению, в доступе отказано. Если это ошибка, пожалуйста свяжитесь с администратором."

            if admin_notes:
                message += f"\n\nКомментарий администратора: {admin_notes}"

        return message

    async def _send_notification_async(self, chat_id: int, text: str) -> bool:
        """
        Wrapper for sending notification with error handling.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send

        Returns:
            True if sent successfully, False otherwise
        """
        try:
            await self._send_with_retry(chat_id, text)
            return True
        except Exception:
            return False

    async def _send_with_retry(self, chat_id: int, text: str) -> None:
        """
        Send a message with retry logic for transient failures.

        Args:
            chat_id: Telegram chat ID
            text: Message text to send

        Raises:
            TelegramError: If all retry attempts fail
        """
        last_error = None

        for attempt in range(self.max_retries):
            try:
                await self.bot.send_message(chat_id=chat_id, text=text)
                return  # Success

            except BadRequest as e:
                # Don't retry on bad requests (e.g., user blocked bot)
                logger.warning(f"Bad request when sending to {chat_id}: {e}")
                raise

            except NetworkError as e:
                last_error = e
                logger.warning(
                    f"Network error on attempt {attempt + 1}/{self.max_retries} "
                    f"when sending to {chat_id}: {e}"
                )

                if attempt < self.max_retries - 1:
                    # Exponential backoff
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))

            except TelegramError as e:
                last_error = e
                logger.error(f"Telegram error when sending to {chat_id}: {e}")

                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        # All retries exhausted
        raise last_error if last_error else TelegramError("Failed to send message")