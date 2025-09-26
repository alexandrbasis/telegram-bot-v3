"""
Authentication utilities for the Telegram bot.

Provides functions for user authorization and access control.
"""

import logging
import time
from typing import Dict, Tuple, Union

from src.config.settings import Settings
from src.services.security_audit_service import get_security_audit_service

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
    start_time = time.time()
    audit_service = get_security_audit_service()

    # Convert and validate user ID
    converted_user_id = _convert_user_id(user_id)
    if converted_user_id is None:
        logger.debug("User ID is None or invalid, denying admin access")

        # Log authorization event for invalid user ID
        auth_event = audit_service.create_authorization_event(
            user_id=None,
            action="admin_check",
            result="denied",
            user_role=None,
            cache_state="invalid_user_id",
            error_details="Invalid or None user ID provided",
        )
        audit_service.log_authorization_event(auth_event)

        return False

    # Check if user is in admin list
    is_admin = converted_user_id in settings.telegram.admin_user_ids

    # Calculate performance metrics
    duration_ms = int((time.time() - start_time) * 1000)

    # Log authorization event
    user_role = "admin" if is_admin else None
    auth_event = audit_service.create_authorization_event(
        user_id=converted_user_id,
        action="admin_check",
        result="granted" if is_admin else "denied",
        user_role=user_role,
        cache_state="direct_check",  # Direct settings check, no cache involved
        error_details=None if is_admin else "User not in admin list",
    )
    audit_service.log_authorization_event(auth_event)

    # Log performance metrics
    perf_metrics = audit_service.create_performance_metrics(
        operation="admin_check",
        duration_ms=duration_ms,
        cache_hit=False,  # Direct settings lookup
        user_role=user_role,
    )
    audit_service.log_performance_metrics(perf_metrics)

    if is_admin:
        logger.info(f"Admin access granted for user ID: {converted_user_id}")
    else:
        logger.debug(f"Admin access denied for user ID: {converted_user_id}")

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
    start_time = time.time()
    audit_service = get_security_audit_service()

    # Convert and validate user ID
    converted_user_id = _convert_user_id(user_id)
    if converted_user_id is None:
        # Log authorization event for invalid user ID
        auth_event = audit_service.create_authorization_event(
            user_id=None,
            action="role_resolution",
            result="denied",
            user_role=None,
            cache_state="invalid_user_id",
            error_details="Invalid or None user ID provided",
        )
        audit_service.log_authorization_event(auth_event)

        return None

    # Check cache first
    current_time = time.time()
    cache_hit = False
    cache_state = "miss"

    if converted_user_id in _ROLE_CACHE:
        cached_role, timestamp = _ROLE_CACHE[converted_user_id]
        if current_time - timestamp <= _ROLE_CACHE_TTL_SECONDS:
            cache_hit = True
            cache_state = "hit"
            role = cached_role
        else:
            cache_state = "expired"
            role = _resolve_user_role_uncached(converted_user_id, settings)
            # Cache the result
            _ROLE_CACHE[converted_user_id] = (role, current_time)
    else:
        cache_state = "miss"
        role = _resolve_user_role_uncached(converted_user_id, settings)
        # Cache the result
        _ROLE_CACHE[converted_user_id] = (role, current_time)

    # Calculate performance metrics
    duration_ms = int((time.time() - start_time) * 1000)

    # Log authorization event
    auth_event = audit_service.create_authorization_event(
        user_id=converted_user_id,
        action="role_resolution",
        result="granted" if role else "denied",
        user_role=role,
        cache_state=cache_state,
        error_details=None if role else "User has no assigned role",
    )
    audit_service.log_authorization_event(auth_event)

    # Log performance metrics
    perf_metrics = audit_service.create_performance_metrics(
        operation="role_resolution",
        duration_ms=duration_ms,
        cache_hit=cache_hit,
        user_role=role,
        additional_context={
            "cache_size": len(_ROLE_CACHE),
            "cache_ttl_seconds": _ROLE_CACHE_TTL_SECONDS,
        },
    )
    audit_service.log_performance_metrics(perf_metrics)

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
    start_time = time.time()
    audit_service = get_security_audit_service()

    if user_id is None:
        # Clear entire cache
        cache_size_before = len(_ROLE_CACHE)
        _ROLE_CACHE.clear()
        logger.debug("Role cache cleared for all users")

        # Log sync event for cache invalidation
        duration_ms = int((time.time() - start_time) * 1000)
        sync_event = audit_service.create_sync_event(
            sync_type="cache_invalidation_all",
            duration_ms=duration_ms,
            records_processed=cache_size_before,
            success=True,
        )
        audit_service.log_sync_event(sync_event)

    else:
        # Convert and validate user ID
        converted_user_id = _convert_user_id(user_id)
        if converted_user_id is not None and converted_user_id in _ROLE_CACHE:
            del _ROLE_CACHE[converted_user_id]
            logger.debug(f"Role cache cleared for user ID: {converted_user_id}")

            # Log sync event for specific user cache invalidation
            duration_ms = int((time.time() - start_time) * 1000)
            sync_event = audit_service.create_sync_event(
                sync_type="cache_invalidation_user",
                duration_ms=duration_ms,
                records_processed=1,
                success=True,
            )
            audit_service.log_sync_event(sync_event)
        else:
            # Log failed cache invalidation
            duration_ms = int((time.time() - start_time) * 1000)
            sync_event = audit_service.create_sync_event(
                sync_type="cache_invalidation_user",
                duration_ms=duration_ms,
                records_processed=0,
                success=False,
                error_details=f"User {user_id} not found in cache or invalid ID",
            )
            audit_service.log_sync_event(sync_event)
