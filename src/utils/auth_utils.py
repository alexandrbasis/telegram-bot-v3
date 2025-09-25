"""
Authentication utilities for the Telegram bot.

Provides functions for user authorization and access control.
"""

import logging
import time
from typing import Dict, Tuple, Union

from src.config.settings import Settings

logger = logging.getLogger(__name__)

# Role resolution cache with TTL
# Cache format: {user_id: (role, timestamp)}
_ROLE_CACHE: Dict[int, Tuple[Union[str, None], float]] = {}
_ROLE_CACHE_TTL_SECONDS = 300  # 5 minutes cache for role lookups


def _convert_user_id(user_id: Union[int, str, None]) -> Union[int, None]:
    """
    Convert user ID to int, handling None and invalid strings.

    Args:
        user_id: User ID to convert

    Returns:
        Converted user ID as int, or None if invalid
    """
    if user_id is None:
        return None

    if isinstance(user_id, str):
        try:
            return int(user_id)
        except (ValueError, TypeError):
            logger.debug(f"Invalid user ID format: {user_id}")
            return None

    return user_id


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
    # Convert and validate user ID
    user_id = _convert_user_id(user_id)
    if user_id is None:
        logger.debug("User ID is None or invalid, denying admin access")
        return False

    # Check if user is in admin list
    is_admin = user_id in settings.telegram.admin_user_ids

    if is_admin:
        logger.info(f"Admin access granted for user ID: {user_id}")
    else:
        logger.debug(f"Admin access denied for user ID: {user_id}")

    return is_admin


def _has_role_access(user_id: int, required_role: str, settings: Settings) -> bool:
    """
    Check if user has access to the required role based on role hierarchy.

    Role hierarchy: admin > coordinator > viewer

    Args:
        user_id: Validated user ID (guaranteed to be int)
        required_role: Required role level ("admin", "coordinator", "viewer")
        settings: Application settings containing role user IDs

    Returns:
        True if user has required role access or higher, False otherwise

    Raises:
        ValueError: If required_role is not supported
    """
    # Define role hierarchy order (highest to lowest)
    role_hierarchy = ["admin", "coordinator", "viewer"]
    role_lists = {
        "admin": settings.telegram.admin_user_ids,
        "coordinator": settings.telegram.coordinator_user_ids,
        "viewer": settings.telegram.viewer_user_ids,
    }

    # Guard against unknown roles
    if required_role not in role_hierarchy:
        logger.warning(f"Unknown role '{required_role}' requested, denying access")
        return False

    # Check roles in hierarchy order until we reach the required role
    required_role_index = role_hierarchy.index(required_role)

    for i in range(required_role_index + 1):
        role_name = role_hierarchy[i]
        if user_id in role_lists[role_name]:
            # Use hashed user ID for privacy in logs
            user_hash = hash(str(user_id)) & 0x7FFFFFFF  # Positive 31-bit hash
            if i < required_role_index:
                logger.debug(
                    f"{required_role.title()} access granted for "
                    f"{role_name} user (hash: {user_hash})"
                )
            else:
                logger.debug(
                    f"{required_role.title()} access granted for "
                    f"user (hash: {user_hash})"
                )
            return True

    # Use hashed user ID for privacy in logs
    user_hash = hash(str(user_id)) & 0x7FFFFFFF  # Positive 31-bit hash
    logger.debug(f"{required_role.title()} access denied for user (hash: {user_hash})")
    return False


def is_coordinator_user(user_id: Union[int, str, None], settings: Settings) -> bool:
    """
    Check if a user is a coordinator or has higher access (admin).

    Role hierarchy: admin > coordinator > viewer

    Args:
        user_id: Telegram user ID (int, str, or None)
        settings: Application settings containing role user IDs

    Returns:
        True if the user is a coordinator or admin, False otherwise
    """
    # Convert and validate user ID
    user_id = _convert_user_id(user_id)
    if user_id is None:
        logger.debug("User ID is None or invalid, denying coordinator access")
        return False

    return _has_role_access(user_id, "coordinator", settings)


def is_viewer_user(user_id: Union[int, str, None], settings: Settings) -> bool:
    """
    Check if a user is a viewer or has higher access (coordinator or admin).

    Role hierarchy: admin > coordinator > viewer

    Args:
        user_id: Telegram user ID (int, str, or None)
        settings: Application settings containing role user IDs

    Returns:
        True if the user has viewer access or higher, False otherwise
    """
    # Convert and validate user ID
    user_id = _convert_user_id(user_id)
    if user_id is None:
        logger.debug("User ID is None or invalid, denying viewer access")
        return False

    return _has_role_access(user_id, "viewer", settings)


def get_user_role(
    user_id: Union[int, str, None], settings: Settings
) -> Union[str, None]:
    """
    Get the highest role for a user based on role hierarchy with caching.

    Role hierarchy: admin > coordinator > viewer

    Args:
        user_id: Telegram user ID (int, str, or None)
        settings: Application settings containing role user IDs

    Returns:
        The highest role name ("admin", "coordinator", "viewer") or None if no role
    """
    # Convert and validate user ID
    user_id = _convert_user_id(user_id)
    if user_id is None:
        return None

    # Check cache first
    current_time = time.time()
    if user_id in _ROLE_CACHE:
        cached_role, timestamp = _ROLE_CACHE[user_id]
        if current_time - timestamp <= _ROLE_CACHE_TTL_SECONDS:
            return cached_role

    # Cache miss or expired - resolve role
    role = _resolve_user_role_uncached(user_id, settings)

    # Cache the result
    _ROLE_CACHE[user_id] = (role, current_time)

    return role


def _resolve_user_role_uncached(user_id: int, settings: Settings) -> Union[str, None]:
    """
    Resolve user role without caching (internal function).

    Args:
        user_id: Validated user ID (guaranteed to be int)
        settings: Application settings containing role user IDs

    Returns:
        The highest role name ("admin", "coordinator", "viewer") or None if no role
    """
    # Check roles in hierarchy order (highest to lowest)
    if user_id in settings.telegram.admin_user_ids:
        return "admin"

    if user_id in settings.telegram.coordinator_user_ids:
        return "coordinator"

    if user_id in settings.telegram.viewer_user_ids:
        return "viewer"

    return None


def invalidate_role_cache(user_id: Union[int, str, None] = None) -> None:
    """
    Invalidate role cache for a specific user or all users.

    Args:
        user_id: User ID to invalidate, or None to clear entire cache
    """
    if user_id is None:
        # Clear entire cache
        _ROLE_CACHE.clear()
        logger.debug("Role cache cleared for all users")
    else:
        # Convert and validate user ID
        user_id = _convert_user_id(user_id)
        if user_id is not None and user_id in _ROLE_CACHE:
            del _ROLE_CACHE[user_id]
            logger.debug(f"Role cache cleared for user ID: {user_id}")
