"""Handlers for participant list functionality."""

import logging

from telegram import Update
from telegram.error import BadRequest
from telegram.ext import ContextTypes
from telegram.helpers import escape_markdown

from src.bot.handlers.search_handlers import SearchStates, main_menu_button
from src.bot.keyboards.list_keyboards import (
    create_department_filter_keyboard,
    get_list_pagination_keyboard,
    get_role_selection_keyboard,
)
from src.services import service_factory
from src.utils.translations import department_to_russian

logger = logging.getLogger(__name__)

_MESSAGE_NOT_MODIFIED = "Message is not modified"


async def _safe_edit_message_text(
    query,
    *,
    text: str,
    reply_markup=None,
    parse_mode: str | None = None,
) -> None:
    """Edit message while suppressing harmless "message is not modified" errors."""

    try:
        await query.edit_message_text(
            text=text, reply_markup=reply_markup, parse_mode=parse_mode
        )
    except BadRequest as exc:
        if _MESSAGE_NOT_MODIFIED in str(exc):
            logger.debug(
                "List handler ignored message-not-modified for callback %s", query.data
            )
            return
        raise


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
    For TEAM role, shows department selection keyboard.
    For CANDIDATE role, shows direct list.
    """
    query = update.callback_query
    await query.answer()

    # Extract role from callback data
    role = query.data.split(":")[1]

    if role == "TEAM":
        # For team members, show department selection keyboard instead of direct list
        context.user_data["selected_role"] = "TEAM"

        message_text = (
            "Выберите департамент для фильтрации участников команды:\n\n"
            "🌐 **Все Тимы** \\- показать всех участников команды\n"
            "🏢 **Департамент** \\- показать участников конкретного департамента\n"
            "❓ **Без департамента** \\- показать участников "
            "без назначенного департамента"
        )

        keyboard = create_department_filter_keyboard()

        await _safe_edit_message_text(
            query,
            text=message_text,
            reply_markup=keyboard,
            parse_mode="MarkdownV2",
        )

    elif role == "CANDIDATE":
        # For candidates, show direct list (no department filtering)
        context.user_data["current_role"] = role
        context.user_data["current_offset"] = 0

        # Get participant list service
        list_service = service_factory.get_participant_list_service()

        try:
            data = await list_service.get_candidates_list(offset=0, page_size=20)
            title = "**Список кандидатов**"

            # Format message with title and participant data
            start_pos = data["current_offset"] + 1
            end_pos = data["current_offset"] + data["actual_displayed"]
            # Escape parentheses and '-' for MarkdownV2
            page_info = (
                f" \\(элементы {start_pos}\\-{end_pos} из {data['total_count']}\\)"
            )
            message_text = f"{title}{page_info}\n\n{data['formatted_list']}"

            # Add pagination keyboard based on data
            keyboard = get_list_pagination_keyboard(
                has_prev=data["has_prev"], has_next=data["has_next"]
            )

            await _safe_edit_message_text(
                query,
                text=message_text,
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )

        except Exception as e:
            # Handle errors gracefully
            error_text = escape_markdown(str(e), version=2)
            await _safe_edit_message_text(
                query,
                text=f"Произошла ошибка при получении списка участников: {error_text}",
                parse_mode="MarkdownV2",
            )

    else:
        await _safe_edit_message_text(
            query, text="Неизвестный тип списка", parse_mode="MarkdownV2"
        )


async def handle_list_navigation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle list navigation callbacks.

    Processes list_nav:PREV, list_nav:NEXT, list_nav:DEPARTMENT, and
    list_nav:MAIN_MENU callbacks.

    Returns:
        Next conversation state
    """
    query = update.callback_query

    # Extract navigation action from callback data
    action = query.data.split(":")[1]

    if action == "MAIN_MENU":
        # Return to main menu using proper navigation (main_menu_button handles answer)
        return await main_menu_button(update, context)

    if action == "DEPARTMENT":
        # Return to department selection for team members
        await query.answer()

        message_text = (
            "Выберите департамент для фильтрации участников команды:\n\n"
            "🌐 **Все Тимы** \\- показать всех участников команды\n"
            "🏢 **Департамент** \\- показать участников конкретного департамента\n"
            "❓ **Без департамента** \\- показать участников "
            "без назначенного департамента"
        )

        keyboard = create_department_filter_keyboard()

        await _safe_edit_message_text(
            query,
            text=message_text,
            reply_markup=keyboard,
            parse_mode="MarkdownV2",
        )

        return SearchStates.MAIN_MENU

    # Only answer for PREV/NEXT navigation
    await query.answer()

    if action in ["PREV", "NEXT"]:
        # Get current state from context
        current_role = context.user_data.get("current_role")
        current_offset = context.user_data.get("current_offset", 0)
        current_department = context.user_data.get("current_department")

        if not current_role:
            # Fallback if state is lost
            await _safe_edit_message_text(
                query,
                text="Произошла ошибка\\. Пожалуйста, выберите список заново\\.",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

        # Get participant list service
        list_service = service_factory.get_participant_list_service()
        # Get current data to find navigation offsets
        try:
            if current_role == "TEAM":
                # Determine department filter for team members
                if current_department == "all":
                    department_filter = None
                elif current_department == "none":
                    department_filter = "unassigned"
                elif current_department:
                    department_filter = current_department
                else:
                    department_filter = None

                current_data = await list_service.get_team_members_list(
                    department=department_filter, offset=current_offset, page_size=20
                )
            elif current_role == "CANDIDATE":
                current_data = await list_service.get_candidates_list(
                    offset=current_offset, page_size=20
                )
            else:
                await _safe_edit_message_text(
                    query, text="Неизвестный тип списка", parse_mode="MarkdownV2"
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
            error_text = escape_markdown(str(e), version=2)
            await _safe_edit_message_text(
                query,
                text=f"Произошла ошибка при навигации: {error_text}",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

        try:
            # Get participant data based on role and new offset
            if current_role == "TEAM":
                # Use same department filter for new offset
                data = await list_service.get_team_members_list(
                    department=department_filter, offset=new_offset, page_size=20
                )
                # Format title with department filter indication
                if current_department == "all":
                    title = "**Список участников команды: Все Тимы**"
                elif current_department == "none":
                    title = "**Список участников команды: Без департамента**"
                elif current_department:
                    dept_name_russian = department_to_russian(current_department)
                    dept_name_safe = escape_markdown(dept_name_russian, version=2)
                    title = f"**Список участников команды: {dept_name_safe}**"
                else:
                    title = "**Список участников команды**"
            elif current_role == "CANDIDATE":
                data = await list_service.get_candidates_list(
                    offset=new_offset, page_size=20
                )
                title = "**Список кандидатов**"
            else:
                await _safe_edit_message_text(
                    query, text="Неизвестный тип списка", parse_mode="MarkdownV2"
                )
                return SearchStates.MAIN_MENU

            # Format message with title and participant data
            start_pos = data["current_offset"] + 1
            end_pos = data["current_offset"] + data["actual_displayed"]
            # Escape parentheses and '-' for MarkdownV2
            page_info = (
                f" \\(элементы {start_pos}\\-{end_pos} из {data['total_count']}\\)"
            )
            message_text = f"{title}{page_info}\n\n{data['formatted_list']}"

            # Add pagination keyboard based on data
            # Show department back button for team lists, not for candidate lists
            show_dept_back = current_role == "TEAM"
            keyboard = get_list_pagination_keyboard(
                has_prev=data["has_prev"],
                has_next=data["has_next"],
                show_department_back=show_dept_back,
            )

            await _safe_edit_message_text(
                query,
                text=message_text,
                reply_markup=keyboard,
                parse_mode="MarkdownV2",
            )

            return SearchStates.MAIN_MENU

        except Exception as e:
            # Handle errors gracefully
            error_text = escape_markdown(str(e), version=2)
            await _safe_edit_message_text(
                query,
                text=f"Произошла ошибка при навигации: {error_text}",
                parse_mode="MarkdownV2",
            )
            return SearchStates.MAIN_MENU

    return SearchStates.MAIN_MENU


async def handle_department_filter_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """
    Handle department filter selection for team member lists.

    Processes list:filter:* callbacks to show filtered participant lists
    based on department selection.
    """
    query = update.callback_query
    await query.answer()

    # Parse callback data to extract filter type and value
    callback_parts = query.data.split(":")

    if len(callback_parts) < 3:
        await _safe_edit_message_text(
            query, text="Неизвестный фильтр", parse_mode="MarkdownV2"
        )
        return

    filter_type = callback_parts[2]  # "all", "none", or "department"

    # Determine department filter value
    if filter_type == "all":
        department_filter = None
        department_name = "Все Тимы"
        current_department = "all"
    elif filter_type == "none":
        department_filter = "unassigned"
        department_name = "Без департамента"
        current_department = "none"
    elif filter_type == "department" and len(callback_parts) >= 4:
        department_filter = callback_parts[3]
        department_name = department_to_russian(department_filter)
        current_department = department_filter
    else:
        await _safe_edit_message_text(
            query, text="Неизвестный фильтр департамента", parse_mode="MarkdownV2"
        )
        return

    department_name_safe = escape_markdown(department_name, version=2)

    # Store filter state in context for pagination
    context.user_data["current_role"] = "TEAM"
    context.user_data["current_department"] = current_department
    context.user_data["current_offset"] = 0

    # Get participant list service
    list_service = service_factory.get_participant_list_service()

    try:
        # Get filtered participant data
        data = await list_service.get_team_members_list(
            department=department_filter, offset=0, page_size=20
        )

        # Format title with department filter indication
        title = f"**Список участников команды: {department_name_safe}**"

        # Format message with title and participant data
        start_pos = data["current_offset"] + 1
        end_pos = data["current_offset"] + data["actual_displayed"]
        # Escape parentheses and '-' for MarkdownV2
        page_info = f" \\(элементы {start_pos}\\-{end_pos} из {data['total_count']}\\)"
        message_text = f"{title}{page_info}\n\n{data['formatted_list']}"

        # Add pagination keyboard based on data
        # (with department back button for team lists)
        keyboard = get_list_pagination_keyboard(
            has_prev=data["has_prev"],
            has_next=data["has_next"],
            show_department_back=True,
        )

        await _safe_edit_message_text(
            query,
            text=message_text,
            reply_markup=keyboard,
            parse_mode="MarkdownV2",
        )

    except Exception as e:
        # Handle errors gracefully
        error_text = escape_markdown(str(e), version=2)
        await _safe_edit_message_text(
            query,
            text=f"Произошла ошибка при получении списка участников: {error_text}",
            parse_mode="MarkdownV2",
        )
