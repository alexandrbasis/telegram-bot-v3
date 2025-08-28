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

from src.services.search_service import SearchService, SearchResult
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
    Process name search query.
    
    Searches participants using fuzzy matching and displays results.
    
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
        # Get all participants from repository
        repository = get_participant_repository()
        all_participants = await repository.list_all()
        
        # Search using fuzzy matching service
        search_service = SearchService(similarity_threshold=0.8, max_results=5)
        results = search_service.search_participants(query, all_participants)
        
        # Store results in user data
        context.user_data['search_results'] = results
        
        if results:
            # Format results message
            results_message = f"Найдено участников: {len(results)}\n\n"
            
            for i, result in enumerate(results, 1):
                participant = result.participant
                score_percentage = int(result.similarity_score * 100)
                
                # Format participant info
                name_ru = participant.full_name_ru or "Неизвестно"
                name_en = participant.full_name_en or ""
                
                participant_info = f"{i}. {name_ru}"
                if name_en and name_en != name_ru:
                    participant_info += f" ({name_en})"
                
                participant_info += f" - {score_percentage}%"
                
                results_message += participant_info + "\n"
            
            logger.info(f"Found {len(results)} participants for user {user.id}")
            
        else:
            results_message = "Участники не найдены."
            logger.info(f"No participants found for user {user.id} query: '{query}'")
        
        # Send results with main menu button
        await update.message.reply_text(
            text=results_message,
            reply_markup=get_search_button_keyboard()
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