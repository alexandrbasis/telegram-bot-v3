"""
Telegram bot handlers for floor search functionality.

Implements conversation flow for floor-based participant search with room
grouping, using ConversationHandler states and reply keyboards.
"""

import logging
from enum import IntEnum
from typing import List
from collections import defaultdict

from telegram import (
    Update,
    ReplyKeyboardMarkup,
)
from telegram.ext import ContextTypes

from src.services.search_service import SearchService
from src.models.participant import Participant

logger = logging.getLogger(__name__)


class FloorSearchStates(IntEnum):
    """Conversation states for floor search flow."""

    WAITING_FOR_FLOOR = 30
    SHOWING_FLOOR_RESULTS = 31


def get_search_service():
    """
    Get search service instance.

    This is a placeholder that should be replaced with proper DI.
    """
    # TODO: Replace with proper DI container
    from src.data.airtable.airtable_client import AirtableClient
    from src.data.airtable.airtable_participant_repo import (
        AirtableParticipantRepository,
    )
    from src.config.settings import get_settings

    settings = get_settings()
    client = AirtableClient(settings.get_airtable_config())
    repository = AirtableParticipantRepository(client)
    return SearchService(repository)


def get_floor_search_keyboard() -> ReplyKeyboardMarkup:
    """Reply keyboard for floor search navigation."""
    keyboard = [["🏠 Главное меню", "🔍 Поиск участников"]]
    return ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True,
        one_time_keyboard=False,
        selective=False
    )


def format_floor_results(participants: List[Participant], floor: int) -> str:
    """
    Format floor search results grouped by room.

    Args:
        participants: List of participants on the floor
        floor: Floor number

    Returns:
        Formatted string with room-by-room breakdown
    """
    if not participants:
        return f"❌ На этаже {floor} участники не найдены."

    # Group participants by room
    rooms = defaultdict(list)
    for participant in participants:
        room = participant.room_number or "Неизвестно"
        rooms[room].append(participant)

    # Sort rooms by number (handle both string and numeric rooms)
    def room_sort_key(room):
        try:
            return int(room)
        except (ValueError, TypeError):
            return float("inf")  # Put non-numeric rooms at the end

    sorted_rooms = sorted(rooms.keys(), key=room_sort_key)

    # Build formatted message
    result_lines = [
        f"🏢 Найдено участников на этаже {floor}: {len(participants)}\n"
    ]

    for room in sorted_rooms:
        room_participants = rooms[room]
        result_lines.append(f"🚪 Комната {room}:")

        for i, participant in enumerate(room_participants, 1):
            # Format participant name with preference for Russian
            name_ru = participant.full_name_ru or "Неизвестно"
            name_en = participant.full_name_en or ""

            participant_line = f"  {i}. {name_ru}"
            if name_en and name_en != name_ru:
                participant_line += f" ({name_en})"

            result_lines.append(participant_line)

        result_lines.append("")  # Empty line between rooms

    return "\n".join(result_lines)


async def handle_floor_search_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle /search_floor command.

    Processes floor search with optional floor number parameter.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state
    """
    user = update.effective_user
    message_text = update.message.text.strip()

    logger.info(f"User {user.id} initiated floor search: '{message_text}'")

    # Parse floor number from command if provided
    parts = message_text.split()
    if len(parts) > 1:
        floor_input = parts[1]
        # Process floor search directly
        context.user_data["current_floor"] = floor_input

        await update.message.reply_text(
            text=f"🔍 Ищу участников на этаже {floor_input}...",
            reply_markup=get_floor_search_keyboard(),
        )

        # Process the search immediately
        return await process_floor_search_with_input(
            update, context, floor_input
        )
    else:
        # Ask for floor number
        await update.message.reply_text(
            text="Введите номер этажа для поиска:",
            reply_markup=get_floor_search_keyboard(),
        )

        return FloorSearchStates.WAITING_FOR_FLOOR


async def process_floor_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Process floor search from user input.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state
    """
    floor_input = update.message.text.strip()
    return await process_floor_search_with_input(update, context, floor_input)


async def process_floor_search_with_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE, floor_input: str
) -> int:
    """
    Process floor search with specific floor input.

    Args:
        update: Telegram update object
        context: Bot context
        floor_input: Floor number/input to search

    Returns:
        Next conversation state
    """
    user = update.effective_user

    logger.info(f"User {user.id} searching floor: '{floor_input}'")

    # Validate floor input (should be numeric)
    try:
        floor_number = int(floor_input)
    except ValueError:
        await update.message.reply_text(
            text="❌ Пожалуйста, введите корректный номер этажа "
                 "(должен быть числом).",
            reply_markup=get_floor_search_keyboard()
        )
        return FloorSearchStates.WAITING_FOR_FLOOR

    try:
        # Get search service
        search_service = get_search_service()

        # Search participants by floor
        participants = await search_service.search_by_floor(floor_number)

        # Store results in user data
        context.user_data["floor_search_results"] = participants
        context.user_data["current_floor"] = floor_input

        # Format and send results
        results_message = format_floor_results(participants, floor_number)

        await update.message.reply_text(
            text=results_message,
            reply_markup=get_floor_search_keyboard()
        )

        if participants:
            logger.info(
                f"Found {len(participants)} participants on floor "
                f"{floor_number} for user {user.id}"
            )
        else:
            logger.info(
                f"No participants found on floor {floor_number} "
                f"for user {user.id}"
            )

    except Exception as e:
        logger.error(f"Error during floor search for user {user.id}: {e}")

        # Send error message
        await update.message.reply_text(
            text="❌ Произошла ошибка при поиске. Попробуйте позже.",
            reply_markup=get_floor_search_keyboard(),
        )

    return FloorSearchStates.SHOWING_FLOOR_RESULTS
