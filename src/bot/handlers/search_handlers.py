"""
Telegram bot handlers for participant name search functionality.

Implements conversation flow for Russian name search with fuzzy matching,
using ConversationHandler states and inline keyboards.
"""

import logging
from enum import IntEnum
from typing import List

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.services.search_service import SearchService, SearchResult, format_match_quality
from src.data.repositories.participant_repository import RepositoryError

logger = logging.getLogger(__name__)


class SearchStates(IntEnum):
    """Conversation states for search flow."""
    MAIN_MENU = 0
    WAITING_FOR_NAME = 1
    SHOWING_RESULTS = 2


def get_participant_repository():
    """
    Get participant repository instance.
    
    This is a placeholder that should be replaced with proper dependency injection.
    """
    # TODO: Replace with proper DI container
    from src.data.airtable.airtable_client import AirtableClient
    from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
    from src.config.settings import get_settings
    
    settings = get_settings()
    client = AirtableClient(settings.get_airtable_config())
    return AirtableParticipantRepository(client)


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Get main menu keyboard with search button."""
    keyboard = [
        [InlineKeyboardButton("🔍 Поиск участников", callback_data="search")]
    ]
    return InlineKeyboardMarkup(keyboard)


def get_search_button_keyboard() -> InlineKeyboardMarkup:
    """Get keyboard with main menu button for search results."""
    keyboard = [
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]
    ]
    return InlineKeyboardMarkup(keyboard)


def create_participant_selection_keyboard(search_results: List[SearchResult]) -> InlineKeyboardMarkup:
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
        button_text = (participant.full_name_ru and participant.full_name_ru.strip()) or \
                     (participant.full_name_en and participant.full_name_en.strip()) or \
                     "Неизвестный участник"
            
        # Use participant record_id for callback data if available, otherwise use name hash
        participant_id = getattr(participant, 'record_id', None)
        if not participant_id:
            # Fallback: create identifier from name (this is for testing mostly)
            participant_id = str(hash(participant.full_name_ru or participant.full_name_en or ""))
            
        callback_data = f"select_participant:{participant_id}"
        
        keyboard.append([InlineKeyboardButton(button_text, callback_data=callback_data)])
    
    # Always add main menu button at the end
    keyboard.append([InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")])
    
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
    context.user_data['search_results'] = []
    
    # Send Russian welcome message with search button
    welcome_message = (
        "Добро пожаловать в бот Tres Dias! 🙏\n\n"
        "Ищите участников по имени."
    )
    
    await update.message.reply_text(
        text=welcome_message,
        reply_markup=get_main_menu_keyboard()
    )
    
    return SearchStates.MAIN_MENU


async def search_button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Handle search button callback.
    
    Prompts user to enter participant name for search.
    
    Args:
        update: Telegram update object
        context: Bot context
        
    Returns:
        Next conversation state (WAITING_FOR_NAME)
    """
    query = update.callback_query
    await query.answer()
    
    logger.info(f"User {query.from_user.id} clicked search button")
    
    # Send search prompt
    search_prompt = "Введите имя участника:"
    
    await query.message.edit_text(
        text=search_prompt,
        reply_markup=None
    )
    
    return SearchStates.WAITING_FOR_NAME


async def process_name_search(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
            enhanced_results = await repository.search_by_name_enhanced(query, threshold=0.8, limit=5)
            
            # Store results in user data (convert to old format for compatibility)
            search_results = []
            for participant, score, _ in enhanced_results:
                search_results.append(SearchResult(participant=participant, similarity_score=score))
            context.user_data['search_results'] = search_results
            
            if enhanced_results:
                # Format results message with rich information
                results_message = f"Найдено участников: {len(enhanced_results)}\n\n"
                
                for i, (participant, score, formatted_result) in enumerate(enhanced_results, 1):
                    # Use match quality labels instead of raw percentages
                    match_quality = format_match_quality(score)
                    
                    # Use rich formatted result from repository
                    participant_info = f"{i}. {formatted_result} - {match_quality}"
                    
                    results_message += participant_info + "\n"
                
                logger.info(f"Found {len(enhanced_results)} participants for user {user.id}")
                
            else:
                results_message = "Участники не найдены."
                logger.info(f"No participants found for user {user.id} query: '{query}'")
                
        except (AttributeError, NotImplementedError):
            # Fallback to old search method for backward compatibility
            logger.debug("Enhanced search not available, falling back to original method")
            
            # Get all participants from repository
            all_participants = await repository.list_all()
            
            # Search using fuzzy matching service
            search_service = SearchService(similarity_threshold=0.8, max_results=5)
            results = search_service.search_participants(query, all_participants)
            
            # Store results in user data
            context.user_data['search_results'] = results
            
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
                logger.info(f"No participants found for user {user.id} query: '{query}'")
        
        # Send results with appropriate keyboard
        # Use interactive participant selection if we have results, otherwise show main menu
        search_results = context.user_data.get('search_results', [])
        if search_results:
            keyboard = create_participant_selection_keyboard(search_results)
        else:
            keyboard = get_search_button_keyboard()
            
        await update.message.reply_text(
            text=results_message,
            reply_markup=keyboard
        )
        
    except Exception as e:
        logger.error(f"Error during search for user {user.id}: {e}")
        
        # Send error message
        error_message = "Ошибка. Попробуйте позже."
        await update.message.reply_text(
            text=error_message,
            reply_markup=get_search_button_keyboard()
        )
    
    return SearchStates.SHOWING_RESULTS


async def process_name_search_enhanced(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    query = update.callback_query
    await query.answer()
    
    logger.info(f"User {query.from_user.id} returned to main menu")
    
    # Clear search results
    context.user_data['search_results'] = []
    
    # Return to main menu
    welcome_message = (
        "Добро пожаловать в бот Tres Dias! 🙏\n\n"
        "Ищите участников по имени."
    )
    
    await query.message.edit_text(
        text=welcome_message,
        reply_markup=get_main_menu_keyboard()
    )
    
    return SearchStates.MAIN_MENU


async def handle_participant_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    logger.info(f"User {user.id} selected participant from results")
    
    # Parse participant ID from callback data
    participant_id = query.data.split(':')[1]
    
    # Find participant in stored search results
    search_results = context.user_data.get('search_results', [])
    selected_participant = None
    
    for result in search_results:
        participant = result.participant
        # Match by record_id or fallback to name hash
        current_id = getattr(participant, 'record_id', None)
        if not current_id:
            current_id = str(hash(participant.full_name_ru or participant.full_name_en or ""))
        
        if current_id == participant_id:
            selected_participant = participant
            break
    
    if not selected_participant:
        logger.error(f"Participant not found for ID {participant_id}")
        await query.message.edit_text(
            text="❌ Участник не найден.",
            reply_markup=get_search_button_keyboard()
        )
        return SearchStates.SHOWING_RESULTS
    
    # Store selected participant for editing
    context.user_data['current_participant'] = selected_participant
    logger.info(f"Selected participant: {selected_participant.full_name_ru} (ID: {participant_id})")
    
    # Import and show edit menu (dynamic import to avoid circular dependency)
    from src.bot.handlers.edit_participant_handlers import show_participant_edit_menu
    return await show_participant_edit_menu(update, context)