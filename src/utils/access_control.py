"""
Access control middleware and decorators for Telegram bot handlers.

Provides reusable authorization decorators to enforce role-based access control
across bot handlers without code duplication.
"""

import functools
import logging
import time
from typing import Callable, List, Optional, Union

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import get_settings
from src.services.security_audit_service import get_security_audit_service
from src.utils.auth_utils import get_user_role

logger = logging.getLogger(__name__)


def require_role(
    required_roles: Union[str, List[str]],
    unauthorized_message: str = "❌ У вас нет доступа к этой функции.",
):
    """
    Decorator to enforce role-based access control on bot handlers.

    Checks if the user has one of the required roles before allowing handler execution.
    Supports role hierarchy: admin > coordinator > viewer

    Args:
        required_roles: Single role string or list of roles that are allowed access
        unauthorized_message: Message to send if user lacks required role

    Returns:
        Decorator function that enforces role requirements

    Example:
        @require_role("admin")
        async def admin_only_handler(update, context):
            pass

        @require_role(["admin", "coordinator"])
        async def admin_or_coordinator_handler(update, context):
            pass
    """
    # Normalize to list for consistent handling
    if isinstance(required_roles, str):
        required_roles = [required_roles]

    def decorator(handler_func: Callable):
        @functools.wraps(handler_func)
        async def wrapper(
            update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs
        ):
            start_time = time.time()
            audit_service = get_security_audit_service()

            user = update.effective_user
            if not user:
                logger.warning("No user information available in update")

                # Log authorization event for missing user
                auth_event = audit_service.create_authorization_event(
                    user_id=None,
                    action=f"handler_access:{handler_func.__name__}",
                    result="denied",
                    user_role=None,
                    cache_state="no_user_info",
                    error_details="No user information available in update",
                )
                audit_service.log_authorization_event(auth_event)

                return

            # Resolve user role (this will internally log role resolution audit events)
            settings = get_settings()
            user_role = get_user_role(user.id, settings)

            # Determine handler action name
            handler_action = f"handler_access:{handler_func.__name__}"

            # Check if user has required role
            if not _has_required_role(user_role, required_roles):
                duration_ms = int((time.time() - start_time) * 1000)

                # Log denied authorization event with handler details
                auth_event = audit_service.create_authorization_event(
                    user_id=user.id,
                    action=handler_action,
                    result="denied",
                    user_role=user_role,
                    cache_state="role_resolved",
                    error_details=(
                        f"User role '{user_role}' insufficient for "
                        f"required roles: {required_roles}"
                    ),
                )
                audit_service.log_authorization_event(auth_event)

                # Log performance metrics for denied access
                perf_metrics = audit_service.create_performance_metrics(
                    operation="handler_authorization",
                    duration_ms=duration_ms,
                    cache_hit=True,  # Role was resolved (potentially from cache)
                    user_role=user_role,
                    additional_context={
                        "handler_name": handler_func.__name__,
                        "required_roles": required_roles,
                        "access_result": "denied",
                    },
                )
                audit_service.log_performance_metrics(perf_metrics)

                denied_message = (
                    f"Access denied: User {user.id} (role: {user_role}) attempted "
                    f"to access handler requiring roles: {required_roles}"
                )
                logger.warning(denied_message)

                # Send unauthorized message to user
                if (
                    hasattr(update, "message")
                    and update.message
                    and hasattr(update.message, "reply_text")
                ):
                    await update.message.reply_text(unauthorized_message)
                elif (
                    hasattr(update, "callback_query")
                    and update.callback_query
                    and update.callback_query.message
                    and hasattr(update.callback_query.message, "reply_text")
                ):
                    await update.callback_query.message.reply_text(unauthorized_message)
                    await update.callback_query.answer()

                return

            # User has required role, proceed with handler
            duration_ms = int((time.time() - start_time) * 1000)

            # Log successful authorization event
            auth_event = audit_service.create_authorization_event(
                user_id=user.id,
                action=handler_action,
                result="granted",
                user_role=user_role,
                cache_state="role_resolved",
            )
            audit_service.log_authorization_event(auth_event)

            # Log performance metrics for successful access
            perf_metrics = audit_service.create_performance_metrics(
                operation="handler_authorization",
                duration_ms=duration_ms,
                cache_hit=True,  # Role was resolved (potentially from cache)
                user_role=user_role,
                additional_context={
                    "handler_name": handler_func.__name__,
                    "required_roles": required_roles,
                    "access_result": "granted",
                },
            )
            audit_service.log_performance_metrics(perf_metrics)

            logger.debug(
                f"Access granted: User {user.id} (role: {user_role}) accessing handler"
            )

            return await handler_func(update, context, *args, **kwargs)

        return wrapper

    return decorator


def require_admin(unauthorized_message: str = "❌ Доступ только для администраторов."):
    """
    Decorator requiring admin role.

    Convenience decorator for handlers that require admin access only.
    """
    return require_role("admin", unauthorized_message)


def require_coordinator_or_above(
    unauthorized_message: str = "❌ Доступ для координаторов и администраторов.",
):
    """
    Decorator requiring coordinator or admin role.

    Convenience decorator for handlers that require coordinator-level access or higher.
    """
    return require_role(["admin", "coordinator"], unauthorized_message)


def require_viewer_or_above(
    unauthorized_message: str = "❌ Доступ только для авторизованных пользователей.",
):
    """
    Decorator requiring viewer, coordinator, or admin role.

    Convenience decorator for handlers that require any authorized access.
    """
    return require_role(["admin", "coordinator", "viewer"], unauthorized_message)


def _has_required_role(user_role: Optional[str], required_roles: List[str]) -> bool:
    """
    Check if user role meets the requirement.

    Implements role hierarchy: admin > coordinator > viewer

    Args:
        user_role: User's actual role (or None if unauthorized)
        required_roles: List of roles that would grant access

    Returns:
        True if user has sufficient access, False otherwise
    """
    if user_role is None:
        return False

    # Define role hierarchy (higher values = higher privileges)
    role_hierarchy = {"viewer": 1, "coordinator": 2, "admin": 3}

    user_level = role_hierarchy.get(user_role, 0)
    if user_level == 0:
        # Unknown role
        return False

    # Check if user role meets or exceeds any of the required roles
    for required_role in required_roles:
        required_level = role_hierarchy.get(required_role, float("inf"))
        if user_level >= required_level:
            return True

    return False


def get_user_role_from_update(update: Update) -> Optional[str]:
    """
    Utility function to extract user role from an Update object.

    Convenience function for handlers that need to access user role
    without applying decorator-based access control.

    Args:
        update: Telegram update object

    Returns:
        User's role string or None if unauthorized/unavailable
    """
    user = update.effective_user
    if not user:
        return None

    settings = get_settings()
    return get_user_role(user.id, settings)
