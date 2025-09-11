"""
Handlers for participant list functionality.

Provides conversation handlers for list access workflow:
Get List → Role Selection → List Display
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.keyboards.list_keyboards import (
    get_role_selection_keyboard,
    get_list_pagination_keyboard,
)
from src.services import service_factory


async def handle_get_list_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle get list request from main menu.
    
    Shows role selection keyboard for choosing team or candidate lists.
    """
    message_text = (
        "Выберите тип списка участников:\n\n"
        "👥 **Команда** - участники команды\n"
        "🎯 **Кандидаты** - кандидаты на участие"
    )
    
    keyboard = get_role_selection_keyboard()
    
    await update.message.reply_text(
        text=message_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )


async def handle_role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle role selection callback for displaying participant lists.
    
    Processes list_role:TEAM or list_role:CANDIDATE callbacks.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract role from callback data
    role = query.data.split(":")[1]
    
    # Get participant list service
    list_service = service_factory.get_participant_list_service()
    
    try:
        # Get participant data based on role
        if role == "TEAM":
            data = await list_service.get_team_members_list(page=1, page_size=20)
            title = "**Список участников команды**"
        elif role == "CANDIDATE":
            data = await list_service.get_candidates_list(page=1, page_size=20)
            title = "**Список кандидатов**"
        else:
            await query.edit_message_text(
                text="Неизвестный тип списка",
                parse_mode='Markdown'
            )
            return
        
        # Format message with title and participant data
        message_text = f"{title}\n\n{data['formatted_list']}"
        
        # Add pagination keyboard based on data
        keyboard = get_list_pagination_keyboard(
            has_prev=data['has_prev'], 
            has_next=data['has_next']
        )
        
        await query.edit_message_text(
            text=message_text,
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    except Exception as e:
        # Handle errors gracefully
        await query.edit_message_text(
            text=f"Произошла ошибка при получении списка участников: {str(e)}",
            parse_mode='Markdown'
        )


async def handle_list_navigation(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """
    Handle list navigation callbacks.
    
    Processes list_nav:PREV, list_nav:NEXT, and list_nav:MAIN_MENU callbacks.
    """
    query = update.callback_query
    await query.answer()
    
    # Extract navigation action from callback data
    action = query.data.split(":")[1]
    
    if action == "MAIN_MENU":
        # Return to main menu (placeholder implementation)
        await query.edit_message_text(
            text="Возвращение в главное меню...",
            parse_mode='Markdown'
        )
    elif action == "PREV":
        # Handle previous page (placeholder)
        await query.edit_message_text(
            text="Предыдущая страница...",
            parse_mode='Markdown'
        )
    elif action == "NEXT":
        # Handle next page (placeholder)
        await query.edit_message_text(
            text="Следующая страница...",
            parse_mode='Markdown'
        )