"""
Authentication utilities for the Telegram bot.

Provides functions for user authorization and access control.
"""

import logging
from typing import Union

from src.config.settings import Settings

logger = logging.getLogger(__name__)


def is_admin_user(user_id: Union[int, str, None], settings: Settings) -> bool:
    """
    Check if a user is an admin based on their Telegram user ID.

    Args:
        user_id: Telegram user ID (int, str, or None)
        settings: Application settings containing admin user IDs

    Returns:
        True if the user is an admin, False otherwise

    Examples:
        >>> settings = Settings()
        >>> settings.telegram.admin_user_ids = [123456, 789012]
        >>> is_admin_user(123456, settings)
        True
        >>> is_admin_user(999999, settings)
        False
    """
    # Handle None user ID
    if user_id is None:
        logger.debug("User ID is None, denying admin access")
        return False

    # Convert string to int if needed
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logger.debug(f"Invalid user ID format: {user_id}")
            return False

    # Check if user is in admin list
    is_admin = user_id in settings.telegram.admin_user_ids

    if is_admin:
        logger.info(f"Admin access granted for user ID: {user_id}")
    else:
        logger.debug(f"Admin access denied for user ID: {user_id}")

    return is_admin