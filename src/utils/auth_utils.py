"""
Authentication utilities for the Telegram bot.

Provides functions for user authorization and access control.
"""

import logging
from typing import Optional, Union

from src.config.settings import Settings
from src.models.user_access_request import AccessLevel, AccessRequestStatus
from src.services.access_request_service import AccessRequestService
from src.services.service_factory import get_user_access_repository

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


async def get_user_access_level(user_id: Union[int, str]) -> Optional[AccessLevel]:
    """
    Get user's access level from Airtable.

    Args:
        user_id: Telegram user ID

    Returns:
        AccessLevel if user is approved, None otherwise
    """
    # Convert to int if needed
    if isinstance(user_id, str):
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            logger.debug(f"Invalid user ID format: {user_id}")
            return None

    # Initialize service
    try:
        repository = get_user_access_repository()
        service = AccessRequestService(repository)

        # Get user's request from Airtable
        user_request = await service.get_request_by_user_id(user_id)

        if user_request and user_request.status == AccessRequestStatus.APPROVED:
            logger.debug(
                f"User {user_id} has access level: {user_request.access_level}"
            )
            return user_request.access_level

    except Exception as e:
        logger.error(f"Error checking user access level: {e}")

    return None


async def is_user_authorized(user_id: Union[int, str], settings: Settings) -> bool:
    """
    Check if user is authorized through either config or Airtable.

    Combines environment-configured admins with Airtable-approved users.

    Args:
        user_id: Telegram user ID
        settings: Application settings

    Returns:
        True if user is authorized, False otherwise
    """
    # Check if user is a configured admin first
    if is_admin_user(user_id, settings):
        return True

    # Check Airtable for approved access
    access_level = await get_user_access_level(user_id)
    return access_level is not None


def is_admin_or_coordinator(user_id: Union[int, str], settings: Settings) -> bool:
    """
    Check if user is an admin (from config) or coordinator (from Airtable).

    This synchronous wrapper checks config admins immediately.
    For Airtable coordinators, use async version.

    Args:
        user_id: Telegram user ID
        settings: Application settings

    Returns:
        True if user is admin/coordinator, False otherwise
    """
    # Config admins always have full access
    return is_admin_user(user_id, settings)


async def is_admin_or_coordinator_async(
    user_id: Union[int, str], settings: Settings
) -> bool:
    """
    Async check if user is an admin or coordinator.

    Args:
        user_id: Telegram user ID
        settings: Application settings

    Returns:
        True if user is admin/coordinator, False otherwise
    """
    # Check config admins first
    if is_admin_user(user_id, settings):
        return True

    # Check Airtable for coordinator or admin access
    access_level = await get_user_access_level(user_id)
    return (
        access_level in [AccessLevel.COORDINATOR, AccessLevel.ADMIN]
        if access_level
        else False
    )
