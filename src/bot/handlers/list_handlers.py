"""
Handlers for participant list functionality.

Provides conversation handlers for list access workflow:
Get List → Role Selection → List Display
"""

from telegram import Update
from telegram.ext import ContextTypes

from src.bot.handlers.search_handlers import SearchStates, main_menu_button
from src.bot.keyboards.list_keyboards import (
    get_list_pagination_keyboard,
    get_role_selection_keyboard,
)
from src.services import service_factory


async def handle_get_list_request(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle get list request from main menu.

    Shows role selection keyboard for choosing team or candidate lists.
    """
    message_text = (
        "Выберите тип списка участников:\n\n"
        # Escape '-' for MarkdownV2
        "👥 **Команда** \\- участники команды\n"
        "🎯 **Кандидаты** \\- кандидаты на участие"
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

    # Store role and offset in context for pagination
    context.user_data["current_role"] = role
    context.user_data["current_offset"] = 0

    # Get participant list service
    list_service = service_factory.get_participant_list_service()

    try:
        # Get participant data based on role
        if role == "TEAM":
            data = await list_service.get_team_members_list(offset=0, page_size=20)
            title = "**Список участников команды**"
        elif role == "CANDIDATE":
            data = await list_service.get_candidates_list(offset=0, page_size=20)
            title = "**Список кандидатов**"
        else:
            await query.edit_message_text(
                text="Неизвестный тип списка", parse_mode="MarkdownV2"
            )
            return

        # Format message with title and participant data
        start_pos = data["current_offset"] + 1
        end_pos = data["current_offset"] + data["actual_displayed"]
        # Escape '-' in range for MarkdownV2
        page_info = f" (элементы {start_pos}\\-{end_pos} из {data['total_count']})"
        message_text = f"{title}{page_info}\n\n{data['formatted_list']}"

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

    # Extract navigation action from callback data
    action = query.data.split(":")[1]

    if action == "MAIN_MENU":
        # Return to main menu using proper navigation (main_menu_button handles answer)
        return await main_menu_button(update, context)

    # Only answer for PREV/NEXT navigation
    await query.answer()

    if action in ["PREV", "NEXT"]:
        # Get current state from context
        current_role = context.user_data.get("current_role")
        current_offset = context.user_data.get("current_offset", 0)

        if not current_role:
            # Fallback if state is lost
            await query.edit_message_text(
                text="Произошла ошибка\\. Пожалуйста, выберите список заново\\.",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

        # Get participant list service
        list_service = service_factory.get_participant_list_service()
        # Get current data to find navigation offsets
        try:
            if current_role == "TEAM":
                current_data = await list_service.get_team_members_list(
                    offset=current_offset, page_size=20
                )
            elif current_role == "CANDIDATE":
                current_data = await list_service.get_candidates_list(
                    offset=current_offset, page_size=20
                )
            else:
                await query.edit_message_text(
                    text="Неизвестный тип списка", parse_mode="MarkdownV2"
                )
                return SearchStates.MAIN_MENU

            # Calculate new offset based on navigation action
            if action == "PREV":
                new_offset = current_data.get("prev_offset")
                if new_offset is None:
                    # Already at the beginning
                    return SearchStates.MAIN_MENU
            else:  # NEXT
                new_offset = current_data.get("next_offset")
                if new_offset is None:
                    # Already at the end
                    return SearchStates.MAIN_MENU

            # Update context with new offset
            context.user_data["current_offset"] = new_offset
        except Exception as e:
            await query.edit_message_text(
                text=f"Произошла ошибка при навигации: {str(e)}",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

        try:
            # Get participant data based on role and new offset
            if current_role == "TEAM":
                data = await list_service.get_team_members_list(
                    offset=new_offset, page_size=20
                )
                title = "**Список участников команды**"
            elif current_role == "CANDIDATE":
                data = await list_service.get_candidates_list(
                    offset=new_offset, page_size=20
                )
                title = "**Список кандидатов**"
            else:
                await query.edit_message_text(
                    text="Неизвестный тип списка", parse_mode="MarkdownV2"
                )
                return SearchStates.MAIN_MENU

            # Format message with title and participant data
            start_pos = data["current_offset"] + 1
            end_pos = data["current_offset"] + data["actual_displayed"]
            # Escape '-' in range for MarkdownV2
            page_info = f" (элементы {start_pos}\\-{end_pos} из {data['total_count']})"
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
                text=f"Произошла ошибка при навигации: {str(e)}",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

    return SearchStates.MAIN_MENU
