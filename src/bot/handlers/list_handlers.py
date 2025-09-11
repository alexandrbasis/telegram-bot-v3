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
from src.bot.handlers.search_handlers import main_menu_button, SearchStates


async def handle_get_list_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
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
        text=message_text, reply_markup=keyboard, parse_mode="MarkdownV2"
    )


async def handle_role_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle role selection callback for displaying participant lists.

    Processes list_role:TEAM or list_role:CANDIDATE callbacks.
    """
    query = update.callback_query
    await query.answer()

    # Extract role from callback data
    role = query.data.split(":")[1]
    
    # Store role and page in context for pagination
    context.user_data["current_role"] = role
    context.user_data["current_page"] = 1

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
                text="Неизвестный тип списка", parse_mode="MarkdownV2"
            )
            return

        # Format message with title and participant data
        message_text = f"{title}\n\n{data['formatted_list']}"

        # Add pagination keyboard based on data
        keyboard = get_list_pagination_keyboard(
            has_prev=data["has_prev"], has_next=data["has_next"]
        )

        await query.edit_message_text(
            text=message_text, reply_markup=keyboard, parse_mode="MarkdownV2"
        )

    except Exception as e:
        # Handle errors gracefully
        await query.edit_message_text(
            text=f"Произошла ошибка при получении списка участников: {str(e)}",
            parse_mode="MarkdownV2",
        )


async def handle_list_navigation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle list navigation callbacks.

    Processes list_nav:PREV, list_nav:NEXT, and list_nav:MAIN_MENU callbacks.
    
    Returns:
        Next conversation state
    """
    query = update.callback_query
    await query.answer()

    # Extract navigation action from callback data
    action = query.data.split(":")[1]

    if action == "MAIN_MENU":
        # Return to main menu using proper navigation
        return await main_menu_button(update, context)
        
    elif action in ["PREV", "NEXT"]:
        # Get current state from context
        current_role = context.user_data.get("current_role")
        current_page = context.user_data.get("current_page", 1)
        
        if not current_role:
            # Fallback if state is lost
            await query.edit_message_text(
                text="Произошла ошибка\\. Пожалуйста, выберите список заново\\.",
                parse_mode="MarkdownV2"
            )
            return SearchStates.MAIN_MENU
            
        # Calculate new page
        if action == "PREV":
            new_page = max(1, current_page - 1)
        else:  # NEXT
            new_page = current_page + 1
            
        # Update context
        context.user_data["current_page"] = new_page
        
        # Get participant list service
        list_service = service_factory.get_participant_list_service()
        
        try:
            # Get participant data based on role and new page
            if current_role == "TEAM":
                data = await list_service.get_team_members_list(page=new_page, page_size=20)
                title = "**Список участников команды**"
            elif current_role == "CANDIDATE":
                data = await list_service.get_candidates_list(page=new_page, page_size=20)
                title = "**Список кандидатов**"
            else:
                await query.edit_message_text(
                    text="Неизвестный тип списка", parse_mode="MarkdownV2"
                )
                return SearchStates.MAIN_MENU

            # Format message with title and participant data
            page_info = f" (страница {new_page})"
            message_text = f"{title}{page_info}\n\n{data['formatted_list']}"

            # Add pagination keyboard based on data
            keyboard = get_list_pagination_keyboard(
                has_prev=data["has_prev"], has_next=data["has_next"]
            )

            await query.edit_message_text(
                text=message_text, reply_markup=keyboard, parse_mode="MarkdownV2"
            )
            
            return SearchStates.MAIN_MENU

        except Exception as e:
            # Handle errors gracefully
            await query.edit_message_text(
                text=f"Произошла ошибка при получении списка участников: {str(e)}",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU
    
    return SearchStates.MAIN_MENU
