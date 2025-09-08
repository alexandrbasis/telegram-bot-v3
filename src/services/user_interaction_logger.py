"""
User interaction logging service for detailed button click and bot response tracking.

Provides structured logging of all user interactions with buttons, bot responses,
conversation state changes, and user journey tracking for debugging purposes.
"""

import logging
import re
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from src.config.settings import get_settings


class InteractionType(Enum):
    """Types of user interactions that can be logged."""

    BUTTON_CLICK = "button_click"
    BOT_RESPONSE = "bot_response"
    MISSING_RESPONSE = "missing_response"
    JOURNEY_STEP = "journey_step"
    STATE_CHANGE = "state_change"


class LoggingError(Exception):
    """Custom exception for logging system errors."""

    pass


class UserInteractionLogger:
    """
    Service for logging detailed user interactions with the bot.

    Logs button clicks, bot responses, conversation state changes, and user
    journey steps with structured formatting for debugging and analysis.
    """

    # Sensitive data patterns to sanitize
    SENSITIVE_PATTERNS = [
        r"(token|api_key|password|auth):([^,\s]+)",
        r"(bearer|secret):([^,\s]+)",
    ]

    def __init__(
        self, logger_name: str = "user_interaction", log_level: int = logging.INFO
    ):
        """
        Initialize user interaction logger.

        Args:
            logger_name: Name for the logger instance
            log_level: Logging level (default: INFO)
        """
        self._logger = logging.getLogger(logger_name)

        # Set log level - prioritize provided level, fallback to settings
        if log_level != logging.INFO:  # Custom level provided
            self._logger.setLevel(log_level)
        else:
            # Use settings if available, otherwise use provided level
            try:
                settings = get_settings()
                level_name = settings.logging.log_level.upper()
                level = getattr(logging, level_name, log_level)
                self._logger.setLevel(level)
            except Exception:
                # Fallback to provided level if settings unavailable
                self._logger.setLevel(log_level)

    def log_button_click(
        self, user_id: Optional[int], button_data: str, username: Optional[str] = None
    ) -> None:
        """
        Log user button click with callback data.

        Args:
            user_id: Telegram user ID (None triggers warning)
            button_data: Callback query data from button click
            username: Optional username for context
        """
        try:
            # Validate input
            if user_id is None:
                self._logger.warning("BUTTON_CLICK log attempted with None user_id")
                return

            if not button_data:
                self._logger.warning(
                    f"BUTTON_CLICK log attempted with empty button_data for user {user_id}"
                )
                return

            # Sanitize sensitive data
            sanitized_data = self._sanitize_sensitive_data(button_data)

            # Create structured log message
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = (
                f"BUTTON_CLICK [{timestamp}] "
                f"user_id={user_id} username={username} button_data={sanitized_data}"
            )

            self._logger.info(log_message)

        except Exception as e:
            # Log error but don't raise exception to avoid breaking bot functionality
            self._logger.error(f"Failed to log button click for user {user_id}: {e}")

    def log_bot_response(
        self,
        user_id: int,
        response_type: str,
        content: str,
        keyboard_info: Optional[str] = None,
    ) -> None:
        """
        Log bot response to user interaction.

        Args:
            user_id: Telegram user ID
            response_type: Type of response (text_message, message_with_keyboard, etc.)
            content: Response content/text
            keyboard_info: Optional keyboard structure information
        """
        try:
            # Create structured log message with timing
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_message = (
                f"BOT_RESPONSE [{timestamp}] "
                f'user_id={user_id} response_type={response_type} content="{content}"'
            )

            if keyboard_info:
                log_message += f' keyboard_info="{keyboard_info}"'

            self._logger.info(log_message)

        except Exception as e:
            self._logger.error(f"Failed to log bot response for user {user_id}: {e}")

    def log_missing_response(
        self, user_id: int, button_data: str, error_type: str, error_message: str
    ) -> None:
        """
        Log missing or failed bot response.

        Args:
            user_id: Telegram user ID
            button_data: Original button data that triggered the interaction
            error_type: Type of error (timeout, handler_error, etc.)
            error_message: Detailed error message
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_message = (
                f"MISSING_RESPONSE [{timestamp}] "
                f"user_id={user_id} button_data={button_data} "
                f'error_type={error_type} error="{error_message}"'
            )

            # Use appropriate log level based on error type
            if error_type == "handler_error":
                self._logger.error(log_message)
            else:
                self._logger.warning(log_message)

        except Exception as e:
            self._logger.error(
                f"Failed to log missing response for user {user_id}: {e}"
            )

    def log_journey_step(
        self, user_id: int, step: str, context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log individual user journey step.

        Args:
            user_id: Telegram user ID
            step: Journey step identifier
            context: Optional context data for the step
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_message = (
                f"JOURNEY_STEP [{timestamp}] " f"user_id={user_id} step={step}"
            )

            # Add context information
            if context:
                context_parts = []
                for key, value in context.items():
                    context_parts.append(f"{key}={value}")
                log_message += f" {' '.join(context_parts)}"

            self._logger.info(log_message)

        except Exception as e:
            self._logger.error(f"Failed to log journey step for user {user_id}: {e}")

    def log_state_change(
        self, user_id: int, from_state: str, to_state: str, trigger: str
    ) -> None:
        """
        Log conversation state change.

        Args:
            user_id: Telegram user ID
            from_state: Previous conversation state
            to_state: New conversation state
            trigger: What triggered the state change
        """
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            log_message = (
                f"STATE_CHANGE [{timestamp}] "
                f"user_id={user_id} from_state={from_state} "
                f"to_state={to_state} trigger={trigger}"
            )

            self._logger.info(log_message)

        except Exception as e:
            self._logger.error(f"Failed to log state change for user {user_id}: {e}")

    def _sanitize_sensitive_data(self, data: str) -> str:
        """
        Sanitize sensitive data from log entries.

        Args:
            data: Original data string

        Returns:
            Sanitized data with sensitive patterns redacted
        """
        sanitized = data

        for pattern in self.SENSITIVE_PATTERNS:
            sanitized = re.sub(pattern, r"\1:[REDACTED]", sanitized)

        return sanitized
