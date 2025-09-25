"""
Telegram bot handlers for room search functionality.

Implements conversation flow for room-based participant search,
using ConversationHandler states and reply keyboards.
"""

import logging
import re
from enum import IntEnum
from typing import List

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.search_keyboards import (
    get_results_navigation_keyboard,
    get_waiting_for_room_keyboard,
)
from src.bot.messages import ErrorMessages, InfoMessages, RetryMessages
from src.models.participant import Participant
from src.services.service_factory import get_search_service
from src.utils.access_control import require_viewer_or_above
from src.utils.translations import department_to_russian, role_to_russian

logger = logging.getLogger(__name__)


class RoomSearchStates(IntEnum):
    """Conversation states for room search flow."""

    WAITING_FOR_ROOM = 20
    SHOWING_ROOM_RESULTS = 21


# Search service is now imported from service_factory module


# Room search keyboards are now imported from search_keyboards module


@require_viewer_or_above(
    "❌ Доступ к поиску по комнатам только для авторизованных пользователей."
)
async def handle_room_search_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle /search_room command.

    Processes room search with optional room number parameter.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state
    """
    user = update.effective_user
    message_text = update.message.text.strip()

    logger.info(f"User {user.id} initiated room search: '{message_text}'")

    # Parse room number from command if provided
    parts = message_text.split()
    if len(parts) > 1:
        room_number = parts[1]
        # Process room search directly
        context.user_data["current_room"] = room_number

        await update.message.reply_text(
            text=InfoMessages.searching_room(room_number),
            reply_markup=get_results_navigation_keyboard(),
        )

        # Process the search immediately
        return await process_room_search_with_number(update, context, room_number)
    else:
        # Ask for room number
        await update.message.reply_text(
            text=InfoMessages.ENTER_ROOM_NUMBER,
            reply_markup=get_waiting_for_room_keyboard(),
        )

        return RoomSearchStates.WAITING_FOR_ROOM


@require_viewer_or_above(
    "❌ Доступ к поиску по комнатам только для авторизованных пользователей."
)
async def process_room_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Process room search from user input.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state
    """
    room_number = update.message.text.strip()
    return await process_room_search_with_number(update, context, room_number)


@require_viewer_or_above(
    "❌ Доступ к поиску по комнатам только для авторизованных пользователей."
)
async def process_room_search_with_number(
    update: Update, context: ContextTypes.DEFAULT_TYPE, room_number: str
) -> int:
    """
    Process room search with specific room number.

    Args:
        update: Telegram update object
        context: Bot context
        room_number: Room number to search

    Returns:
        Next conversation state
    """
    user = update.effective_user

    logger.info(f"User {user.id} searching room: '{room_number}'")

    # Validate room number (should contain digits)
    if not re.search(r"\d", room_number):
        await update.message.reply_text(
            text=RetryMessages.with_help(
                ErrorMessages.INVALID_ROOM_NUMBER, RetryMessages.ROOM_NUMBER_HELP
            ),
            reply_markup=get_waiting_for_room_keyboard(),
        )
        return RoomSearchStates.WAITING_FOR_ROOM

    try:
        # Get search service
        search_service = get_search_service()

        # Search participants by room (for context storage)
        participants = await search_service.search_by_room(room_number)

        # Store results in user data
        context.user_data["room_search_results"] = participants
        context.user_data["current_room"] = room_number

        # Format and send results in Russian with structured fields
        results_message = format_room_results_russian(participants, room_number)

        if participants:
            logger.info(
                f"Found {len(participants)} participants in room "
                f"{room_number} for user {user.id}"
            )
        else:
            logger.info(
                f"No participants found in room {room_number} " f"for user {user.id}"
            )

        # Send results
        await update.message.reply_text(
            text=results_message, reply_markup=get_results_navigation_keyboard()
        )

    except Exception as e:
        logger.error(f"Error during room search for user {user.id}: {e}")

        # Send error message
        await update.message.reply_text(
            text=RetryMessages.with_help(
                ErrorMessages.SEARCH_ERROR_GENERIC, RetryMessages.RETRY_CONNECTION
            ),
            reply_markup=get_results_navigation_keyboard(),
        )

    return RoomSearchStates.SHOWING_ROOM_RESULTS


def format_room_results_russian(
    participants: List[Participant], room_number: str
) -> str:
    """
    Format room search results in Russian with role, department, and floor.

    Args:
        participants: List of participants found in the room
        room_number: Room identifier provided by the user

    Returns:
        Formatted multi-line string ready to send to the user
    """
    if not participants:
        return ErrorMessages.no_participants_in_room(room_number)

    lines: List[str] = [
        f"🏠 Найдено участников в комнате {room_number}: {len(participants)}\n"
    ]

    for idx, p in enumerate(participants, 1):
        name_ru = p.full_name_ru or "Неизвестно"
        name_en = p.full_name_en or ""

        # Line 1: name(s)
        line = f"{idx}. {name_ru}"
        if name_en and name_en != name_ru:
            line += f" ({name_en})"
        lines.append(line)

        # Line 2: details (role, department, floor)
        has_role = getattr(p, "role", None)
        role_label = role_to_russian(p.role) if has_role else "Не указано"
        dept_label = (
            department_to_russian(p.department)
            if getattr(p, "department", None)
            else "Не указано"
        )
        floor_label = (
            str(p.floor)
            if getattr(p, "floor", None) not in (None, "")
            else "Неизвестно"
        )
        details = (
            f"   👥 Роль: {role_label} | 📋 Департамент: {dept_label} | "
            f"🏢 Этаж: {floor_label}"
        )
        lines.append(details)

        # Spacer line between participants
        if idx != len(participants):
            lines.append("")

    return "\n".join(lines)
