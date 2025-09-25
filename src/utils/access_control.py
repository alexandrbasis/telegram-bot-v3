"""
Access control middleware and decorators for Telegram bot handlers.

Provides reusable authorization decorators to enforce role-based access control
across bot handlers without code duplication.
"""

import functools
import logging
from typing import Callable, List, Optional, Union

from telegram import Update
from telegram.ext import ContextTypes

from src.config.settings import get_settings
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
            user = update.effective_user
            if not user:
                logger.warning("No user information available in update")
                return

            # Resolve user role
            settings = get_settings()
            user_role = get_user_role(user.id, settings)

            # Check if user has required role
            if not _has_required_role(user_role, required_roles):
                logger.warning(
                    f"Access denied: User {user.id} (role: {user_role}) "
                    f"attempted to access handler requiring roles: {required_roles}"
                )

                # Send unauthorized message to user
                if hasattr(update, "message") and update.message:
                    await update.message.reply_text(unauthorized_message)
                elif hasattr(update, "callback_query") and update.callback_query:
                    await update.callback_query.message.reply_text(unauthorized_message)
                    await update.callback_query.answer()

                return

            # User has required role, proceed with handler
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
