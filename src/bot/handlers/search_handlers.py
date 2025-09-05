"""
Telegram bot handlers for participant name search functionality.

Implements conversation flow for Russian name search with fuzzy matching,
using ConversationHandler states and inline keyboards.
"""

import logging
from enum import IntEnum
from typing import List

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import ContextTypes

from src.services.search_service import (
    SearchService,
    SearchResult,
    format_match_quality,
)
from src.services.user_interaction_logger import UserInteractionLogger
from src.services.service_factory import get_participant_repository
from src.config.settings import get_settings
from src.bot.keyboards.search_keyboards import (
    get_main_menu_keyboard,
    get_search_mode_selection_keyboard,
    get_waiting_for_name_keyboard,
    get_results_navigation_keyboard,
    NAV_MAIN_MENU,
)

logger = logging.getLogger(__name__)


class SearchStates(IntEnum):
    """Conversation states for search flow."""

    MAIN_MENU = 10
    SEARCH_MODE_SELECTION = 13
    WAITING_FOR_NAME = 11
    SHOWING_RESULTS = 12


# Participant repository factory imported at top


def get_user_interaction_logger():
    """
    Get user interaction logger instance if logging is enabled.

    Returns:
        UserInteractionLogger instance or None if disabled
    """
    try:
        # Reset settings to pick up new environment variables
        from src.config.settings import reset_settings

        reset_settings()

        settings = get_settings()
        if not settings.logging.enable_user_interaction_logging:
            return None

        # Use configured log level for user interactions
        import logging

        log_level = getattr(
            logging, settings.logging.user_interaction_log_level.upper(), logging.INFO
        )
        return UserInteractionLogger(log_level=log_level)
    except Exception as e:
        logger.error(f"Failed to initialize user interaction logger: {e}")
        return None


# Backward compatibility constants
NAV_SEARCH = "🔍 Поиск участников"


def create_participant_selection_keyboard(
    search_results: List[SearchResult],
) -> InlineKeyboardMarkup:
    """
    Create interactive keyboard with participant selection buttons.

    Generates clickable buttons for each search result (up to 5 participants)
    with Russian name labels and callback data for selection handling.

    Args:
        search_results: List of SearchResult objects from participant search

    Returns:
        InlineKeyboardMarkup with participant selection buttons and main menu button
    """
    keyboard = []

    # Limit to maximum 5 results
    limited_results = search_results[:5]

    # Create participant selection buttons
    for result in limited_results:
        participant = result.participant

        # Prioritize Russian name for button label, fallback to English
        button_text = (
            (participant.full_name_ru and participant.full_name_ru.strip())
            or (participant.full_name_en and participant.full_name_en.strip())
            or "Неизвестный участник"
        )

        # Use record_id for callback data if available, otherwise fallback to name hash
        participant_id = getattr(participant, "record_id", None)
        if not participant_id:
            # Fallback: create identifier from name (this is for testing mostly)
            participant_id = str(
                hash(participant.full_name_ru or participant.full_name_en or "")
            )

        callback_data = f"select_participant:{participant_id}"

        keyboard.append(
            [InlineKeyboardButton(button_text, callback_data=callback_data)]
        )

    # Navigation is now handled by ReplyKeyboardMarkup; no inline main menu button

    return InlineKeyboardMarkup(keyboard)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle /start command.

    Sends Russian greeting with search button and initializes user data.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (MAIN_MENU)
    """
    user = update.effective_user
    logger.info(f"User {user.id} ({user.first_name}) started the bot")

    # Initialize user data
    context.user_data["search_results"] = []
    # Flag conversation-driven flows to prefer direct name entry upon pressing search
    context.user_data["force_direct_name_input"] = True

    # Send Russian welcome message with search button
    welcome_message = (
        "Добро пожаловать в бот Tres Dias! 🙏\n\n" "Выберите тип поиска участников."
    )

    await update.message.reply_text(
        text=welcome_message,
        reply_markup=get_main_menu_keyboard(),
    )

    return SearchStates.MAIN_MENU


async def search_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle search button callback.

    Shows search mode selection with name/room/floor options.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (SEARCH_MODE_SELECTION)
    """
    query = getattr(update, "callback_query", None)
    message = getattr(update, "message", None)

    if query:
        await query.answer()
        user = query.from_user
        button_data = query.data
    else:
        user = update.effective_user
        button_data = NAV_SEARCH
    user_logger = get_user_interaction_logger()

    # Log button click if logging is enabled
    if user_logger:
        user_logger.log_button_click(
            user_id=user.id,
            button_data=button_data,
            username=getattr(user, "username", None),
        )

    logger.info(f"User {user.id} clicked search button")

    # Backward compatibility behavior: if triggered via inline 'search' callback,
    # go directly to name input state to satisfy existing flows/tests.
    if (
        query
        and getattr(query, "data", None) == "search"
        and context.user_data.get("force_direct_name_input")
    ):
        prompt = "Введите имя участника:"  # Russian prompt for name input
        await query.message.edit_text(text=prompt)
        await query.message.reply_text(
            text="Отправьте имя или часть имени для поиска.",
            reply_markup=get_waiting_for_name_keyboard(),
        )

        if user_logger:
            user_logger.log_bot_response(
                user_id=user.id,
                response_type="edit_message",
                content=prompt,
            )
        return SearchStates.WAITING_FOR_NAME

    # Default: send search mode selection prompt
    search_prompt = "Выберите тип поиска:"
    if query:
        await query.message.edit_text(text=search_prompt)
        await query.message.reply_text(
            text="Используйте клавиатуру ниже для выбора типа поиска.",
            reply_markup=get_search_mode_selection_keyboard(),
        )
    elif message:
        await message.reply_text(
            text=search_prompt,
            reply_markup=get_search_mode_selection_keyboard(),
        )

    if user_logger:
        user_logger.log_bot_response(
            user_id=user.id,
            response_type="edit_message",
            content=search_prompt,
        )
    return SearchStates.SEARCH_MODE_SELECTION


async def process_name_search(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Process name search query with enhanced functionality.

    Searches participants using enhanced search with language detection,
    multi-field search, and rich formatting.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (SHOWING_RESULTS)
    """
    query = update.message.text.strip()
    user = update.effective_user

    logger.info(f"User {user.id} searching for: '{query}'")

    try:
        # Get repository
        repository = get_participant_repository()

        # Try enhanced search first, fallback to old method for backward compatibility
        try:
            enhanced_results = await repository.search_by_name_enhanced(
                query, threshold=0.8, limit=5
            )

            # Store results in user data (convert to old format for compatibility)
            search_results = []
            for participant, score, _ in enhanced_results:
                search_results.append(
                    SearchResult(participant=participant, similarity_score=score)
                )
            context.user_data["search_results"] = search_results

            if enhanced_results:
                # Format results message with rich information
                results_message = f"Найдено участников: {len(enhanced_results)}\n\n"

                for i, (participant, score, formatted_result) in enumerate(
                    enhanced_results, 1
                ):
                    # Use match quality labels instead of raw percentages
                    match_quality = format_match_quality(score)

                    # Use rich formatted result from repository
                    participant_info = f"{i}. {formatted_result} - {match_quality}"

                    results_message += participant_info + "\n"

                logger.info(
                    f"Found {len(enhanced_results)} participants for user {user.id}"
                )

            else:
                results_message = "Участники не найдены."
                logger.info(
                    f"No participants found for user {user.id} query: '{query}'"
                )

        except (AttributeError, NotImplementedError):
            # Fallback to old search method for backward compatibility
            logger.debug(
                "Enhanced search not available, falling back to original method"
            )

            # Get all participants from repository
            all_participants = await repository.list_all()

            # Search using fuzzy matching service
            search_service = SearchService(similarity_threshold=0.8, max_results=5)
            results = search_service.search_participants(query, all_participants)

            # Store results in user data
            context.user_data["search_results"] = results

            if results:
                # Format results message (original format)
                results_message = f"Найдено участников: {len(results)}\n\n"

                for i, result in enumerate(results, 1):
                    participant = result.participant
                    # Use match quality labels instead of raw percentages
                    match_quality = format_match_quality(result.similarity_score)

                    # Format participant info
                    name_ru = participant.full_name_ru or "Неизвестно"
                    name_en = participant.full_name_en or ""

                    participant_info = f"{i}. {name_ru}"
                    if name_en and name_en != name_ru:
                        participant_info += f" ({name_en})"

                    participant_info += f" - {match_quality}"

                    results_message += participant_info + "\n"

                logger.info(f"Found {len(results)} participants for user {user.id}")

            else:
                results_message = "Участники не найдены."
                logger.info(
                    f"No participants found for user {user.id} query: '{query}'"
                )

        # Send results with appropriate keyboard
        # Use interactive selection if we have results, otherwise show main menu
        search_results = context.user_data.get("search_results", [])
        if search_results:
            keyboard = create_participant_selection_keyboard(search_results)
            # Send results with inline selection keyboard
            await update.message.reply_text(text=results_message, reply_markup=keyboard)
            # Update navigation reply keyboard layout for results view
            await update.message.reply_text(
                text="Используйте клавиатуру для навигации.",
                reply_markup=get_results_navigation_keyboard(),
            )
        else:
            # No results; keep navigation keyboard to allow retry/main menu
            await update.message.reply_text(
                text=results_message,
                reply_markup=get_results_navigation_keyboard(),
            )

    except Exception as e:
        logger.error(f"Error during search for user {user.id}: {e}")

        # Log missing response if logging is enabled
        user_logger = get_user_interaction_logger()
        if user_logger:
            # Try to get the last button click from context or use 'search' as fallback
            last_button = context.user_data.get("last_button_click", "search")
            user_logger.log_missing_response(
                user_id=user.id,
                button_data=last_button,
                error_type="handler_error",
                error_message=f"Error during search for user {user.id}: {e}",
            )

        # Send error message
        error_message = "Ошибка. Попробуйте позже."
        await update.message.reply_text(
            text=error_message,
            reply_markup=get_results_navigation_keyboard(),
        )

    return SearchStates.SHOWING_RESULTS


async def process_name_search_enhanced(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Enhanced search processing with rich results.

    This function provides the same functionality as process_name_search
    but is kept separate for testing purposes.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (SHOWING_RESULTS)
    """
    return await process_name_search(update, context)


async def main_menu_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle main menu button callback.

    Returns user to main menu and clears search results.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (MAIN_MENU)
    """
    query = getattr(update, "callback_query", None)
    message = getattr(update, "message", None)

    if query:
        await query.answer()
        user = query.from_user
        button_data = query.data
    else:
        user = update.effective_user
        button_data = NAV_MAIN_MENU
    user_logger = get_user_interaction_logger()

    # Log button click if logging is enabled
    if user_logger:
        user_logger.log_button_click(
            user_id=user.id,
            button_data=button_data,
            username=getattr(user, "username", None),
        )

    logger.info(f"User {user.id} returned to main menu")

    # Clear search results
    context.user_data["search_results"] = []

    # Return to main menu
    welcome_message = (
        "Добро пожаловать в бот Tres Dias! 🙏\n\n" "Ищите участников по имени."
    )

    if query:
        await query.message.edit_text(text=welcome_message)
        # Send a new message to apply the reply keyboard
        await query.message.reply_text(
            text="Используйте клавиатуру ниже для навигации.",
            reply_markup=get_main_menu_keyboard(),
        )
    elif message:
        await message.reply_text(
            text=welcome_message,
            reply_markup=get_main_menu_keyboard(),
        )

    # Log bot response if logging is enabled
    if user_logger:
        user_logger.log_bot_response(
            user_id=user.id,
            response_type="edit_message",
            content=welcome_message,
            keyboard_info="1 button: search",
        )

    return SearchStates.MAIN_MENU


async def cancel_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel current search input and return to main menu."""
    user = update.effective_user
    logger.info(f"User {user.id} cancelled search input")

    # Clear transient search state
    context.user_data["search_results"] = []

    welcome_message = (
        "Добро пожаловать в бот Tres Dias! 🙏\n\n" "Ищите участников по имени."
    )

    await update.message.reply_text(
        text=welcome_message,
        reply_markup=get_main_menu_keyboard(),
    )

    return SearchStates.MAIN_MENU


async def handle_participant_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle participant selection from search results.

    Stores selected participant in context and shows editing interface.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (editing state)
    """
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_logger = get_user_interaction_logger()

    # Log button click if logging is enabled
    if user_logger:
        user_logger.log_button_click(
            user_id=user.id,
            button_data=query.data,
            username=getattr(user, "username", None),
        )

    logger.info(f"User {user.id} selected participant from results")

    # Parse participant ID from callback data
    participant_id = query.data.split(":")[1]

    # Find participant in stored search results
    search_results = context.user_data.get("search_results", [])
    selected_participant = None

    for result in search_results:
        participant = result.participant
        # Match by record_id or fallback to name hash
        current_id = getattr(participant, "record_id", None)
        if not current_id:
            current_id = str(
                hash(participant.full_name_ru or participant.full_name_en or "")
            )

        if current_id == participant_id:
            selected_participant = participant
            break

    if not selected_participant:
        logger.error(f"Participant not found for ID {participant_id}")

        # Log missing response if logging is enabled
        if user_logger:
            user_logger.log_missing_response(
                user_id=user.id,
                button_data=query.data,
                error_type="data_error",
                error_message=f"Participant not found for ID {participant_id}",
            )

        await query.message.edit_text(
            text="❌ Участник не найден.", reply_markup=get_main_menu_keyboard()
        )
        return SearchStates.SHOWING_RESULTS

    # Store selected participant for editing
    context.user_data["current_participant"] = selected_participant
    logger.info(
        "Selected participant: %s (ID: %s)",
        selected_participant.full_name_ru,
        participant_id,
    )

    # Log user journey step if logging is enabled
    if user_logger:
        user_logger.log_journey_step(
            user_id=user.id,
            step="participant_selected",
            context={
                "participant_id": participant_id,
                "participant_name": selected_participant.full_name_ru
                or selected_participant.full_name_en
                or "Unknown",
            },
        )

    # Import and show edit menu (dynamic import to avoid circular dependency)
    from src.bot.handlers.edit_participant_handlers import show_participant_edit_menu

    return await show_participant_edit_menu(update, context)


async def handle_search_name_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle name search mode selection.

    Transitions user to name search input state.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (WAITING_FOR_NAME)
    """
    user = update.effective_user
    logger.info(f"User {user.id} selected name search mode")

    # Send name search prompt
    search_prompt = "Введите имя участника:"

    await update.message.reply_text(
        text=search_prompt,
        reply_markup=get_waiting_for_name_keyboard(),
    )

    return SearchStates.WAITING_FOR_NAME


async def handle_search_room_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle room search mode selection.

    Delegates to room search handler.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (room search state)
    """
    user = update.effective_user
    logger.info(f"User {user.id} selected room search mode")

    # Import room search handler dynamically to avoid circular dependency
    from src.bot.handlers.room_search_handlers import handle_room_search_command

    # Simulate a room search command call
    return await handle_room_search_command(update, context)


async def handle_search_floor_mode(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle floor search mode selection.

    Delegates to floor search handler.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (floor search state)
    """
    user = update.effective_user
    logger.info(f"User {user.id} selected floor search mode")

    # Import floor search handler dynamically to avoid circular dependency
    from src.bot.handlers.floor_search_handlers import handle_floor_search_command

    # Simulate a floor search command call
    return await handle_floor_search_command(update, context)


async def back_to_search_modes(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle back to search modes button.

    Returns user to search mode selection state.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (SEARCH_MODE_SELECTION)
    """
    user = update.effective_user
    logger.info(f"User {user.id} returned to search mode selection")

    # Send search mode selection prompt
    search_prompt = "Выберите тип поиска:"

    await update.message.reply_text(
        text=search_prompt,
        reply_markup=get_search_mode_selection_keyboard(),
    )

    return SearchStates.SEARCH_MODE_SELECTION
