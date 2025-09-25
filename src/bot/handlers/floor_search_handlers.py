"""
Telegram bot handlers for floor search functionality.

Implements conversation flow for floor-based participant search with room
grouping, using ConversationHandler states and reply keyboards.
"""

import logging
import re
from collections import defaultdict
from enum import IntEnum
from typing import List

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.search_keyboards import (
    get_floor_discovery_keyboard,
    get_floor_selection_keyboard,
    get_results_navigation_keyboard,
    get_waiting_for_floor_keyboard,
)
from src.bot.messages import ErrorMessages, InfoMessages, RetryMessages
from src.models.participant import Participant
from src.services.service_factory import get_search_service
from src.utils.access_control import require_viewer_or_above

logger = logging.getLogger(__name__)


class FloorSearchStates(IntEnum):
    """Conversation states for floor search flow."""

    WAITING_FOR_FLOOR = 30
    SHOWING_FLOOR_RESULTS = 31


# Search service is now imported from service_factory module


# Floor search keyboards are now imported from search_keyboards module


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

    # Sort rooms: numeric rooms first (by number), then alphanumeric (alphabetically)
    def room_sort_key(room):
        try:
            # Numeric rooms get priority 0 and sort by numeric value
            return (0, int(room))
        except (ValueError, TypeError):
            # Alphanumeric rooms get priority 1 and sort alphabetically
            return (1, str(room))

    sorted_rooms = sorted(rooms.keys(), key=room_sort_key)

    # Build formatted message
    result_lines = [f"🏢 Найдено участников на этаже {floor}: {len(participants)}\n"]

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


@require_viewer_or_above(
    "❌ Доступ к поиску по этажам только для авторизованных пользователей."
)
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
            text=InfoMessages.searching_floor(int(floor_input)),
            reply_markup=get_results_navigation_keyboard(),
        )

        # Process the search immediately
        return await process_floor_search_with_input(update, context, floor_input)
    else:
        # Ask for floor number with discovery button
        await update.message.reply_text(
            text=InfoMessages.ENTER_FLOOR_WITH_DISCOVERY,
            reply_markup=get_floor_discovery_keyboard(),
        )

        # Also show the reply keyboard for navigation
        await update.message.reply_text(
            text="Используйте кнопку выше или введите номер:",
            reply_markup=get_waiting_for_floor_keyboard(),
        )

        return FloorSearchStates.WAITING_FOR_FLOOR


@require_viewer_or_above(
    "❌ Доступ к поиску по этажам только для авторизованных пользователей."
)
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


async def execute_floor_search(
    message, context: ContextTypes.DEFAULT_TYPE, floor_input: str, user_id: int
) -> tuple[list, str]:
    """
    Execute floor search logic without UI dependencies.

    Args:
        message: Message object for responses (update.message or callback_query.message)
        context: Bot context
        floor_input: Floor number/input to search
        user_id: User ID for logging

    Returns:
        Tuple of (participants_list, results_message)

    Raises:
        ValueError: If floor input is invalid
        Exception: If search service fails
    """
    logger.info(f"User {user_id} searching floor: '{floor_input}'")

    # Validate floor input (should be numeric)
    floor_number = int(floor_input)  # Let ValueError propagate

    # Get search service and search participants
    search_service = get_search_service()
    participants = await search_service.search_by_floor(floor_number)

    # Store results in user data
    context.user_data["floor_search_results"] = participants
    context.user_data["current_floor"] = floor_input

    # Format results message
    results_message = format_floor_results(participants, floor_number)

    if participants:
        logger.info(
            f"Found {len(participants)} participants on floor "
            f"{floor_number} for user {user_id}"
        )
    else:
        logger.info(f"No participants found on floor {floor_number} for user {user_id}")

    return participants, results_message


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

    try:
        participants, results_message = await execute_floor_search(
            update.message, context, floor_input, user.id
        )

        await update.message.reply_text(
            text=results_message, reply_markup=get_results_navigation_keyboard()
        )

    except ValueError:
        await update.message.reply_text(
            text=RetryMessages.with_help(
                ErrorMessages.INVALID_FLOOR_NUMBER, RetryMessages.FLOOR_NUMBER_HELP
            ),
            reply_markup=get_waiting_for_floor_keyboard(),
        )
        return FloorSearchStates.WAITING_FOR_FLOOR

    except Exception as e:
        logger.error(f"Error during floor search for user {user.id}: {e}")

        # Send error message
        await update.message.reply_text(
            text=RetryMessages.with_help(
                ErrorMessages.SEARCH_ERROR_GENERIC, RetryMessages.RETRY_CONNECTION
            ),
            reply_markup=get_results_navigation_keyboard(),
        )

    return FloorSearchStates.SHOWING_FLOOR_RESULTS


async def handle_floor_discovery_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle floor discovery button callback.

    Fetches available floors from the backend and displays them as selection buttons.
    Acknowledges the callback query and edits the original message if possible.

    Args:
        update: Telegram update object with callback query
        context: Bot context
    """
    query = update.callback_query
    user = update.effective_user

    # Acknowledge the callback to stop the loading spinner
    await query.answer()

    logger.info(f"User {user.id} triggered floor discovery")

    try:
        # Get search service and fetch available floors
        search_service = get_search_service()
        floors = await search_service.get_available_floors()

        if floors:
            # Create floor selection keyboard
            keyboard = get_floor_selection_keyboard(floors)
            message_text = InfoMessages.AVAILABLE_FLOORS_HEADER

            logger.info(f"Found {len(floors)} available floors for user {user.id}")
        else:
            # No floors available
            keyboard = None
            message_text = InfoMessages.NO_FLOORS_AVAILABLE

            logger.info(f"No floors available for user {user.id}")

        # Edit the original message if present, otherwise send new message
        if query.message:
            await query.message.edit_text(text=message_text, reply_markup=keyboard)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=message_text,
                reply_markup=keyboard,
            )

    except Exception as e:
        logger.error(f"Error during floor discovery for user {user.id}: {e}")

        # Send error message
        error_text = InfoMessages.FLOOR_DISCOVERY_ERROR

        if query.message:
            await query.message.edit_text(text=error_text)
        else:
            await context.bot.send_message(
                chat_id=update.effective_chat.id, text=error_text
            )


async def handle_floor_selection_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle floor selection button callback.

    Processes the selected floor number from callback data and triggers
    the floor search with the selected number.

    Args:
        update: Telegram update object with callback query
        context: Bot context

    Returns:
        Next conversation state (SHOWING_FLOOR_RESULTS)
    """
    query = update.callback_query
    user = update.effective_user

    # Acknowledge the callback
    await query.answer()

    # Extract floor number from callback data using regex
    match = re.match(r"^floor_select_(\d+)$", query.data)
    if not match:
        logger.error(f"Invalid floor selection callback data: {query.data}")
        await query.message.edit_text(text=ErrorMessages.SYSTEM_ERROR_GENERIC)
        return FloorSearchStates.WAITING_FOR_FLOOR

    floor_number = match.group(1)
    logger.info(f"User {user.id} selected floor {floor_number}")

    # Send searching message
    await query.message.edit_text(text=InfoMessages.searching_floor(int(floor_number)))

    try:
        # Execute floor search using the helper function (no update mutation needed)
        participants, results_message = await execute_floor_search(
            query.message, context, floor_number, user.id
        )

        # Important: can't attach ReplyKeyboardMarkup via edit_text (inline only)
        # Send results as a new message to include reply keyboard
        await query.message.reply_text(
            text=results_message, reply_markup=get_results_navigation_keyboard()
        )

    except ValueError:
        # This shouldn't happen since callback data is validated, but handle gracefully
        logger.error(f"Invalid floor number from validated callback: {floor_number}")
        await query.message.edit_text(text=ErrorMessages.SYSTEM_ERROR_GENERIC)
        return FloorSearchStates.WAITING_FOR_FLOOR

    except Exception as e:
        logger.error(f"Error during floor search for user {user.id}: {e}")

        # Send error message
        await query.message.edit_text(
            text=RetryMessages.with_help(
                ErrorMessages.SEARCH_ERROR_GENERIC, RetryMessages.RETRY_CONNECTION
            ),
            reply_markup=get_results_navigation_keyboard(),
        )

    return FloorSearchStates.SHOWING_FLOOR_RESULTS
