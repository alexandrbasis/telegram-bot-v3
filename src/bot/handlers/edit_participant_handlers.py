"""
Telegram bot handlers for participant editing functionality.

Implements conversation flow for editing participant fields with field-specific
input methods (buttons for predefined values, text input for open fields).
"""

import logging
from enum import IntEnum
from typing import Optional

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardRemove,
    Update,
)
from telegram.ext import ContextTypes

from src.bot.keyboards.edit_keyboards import (
    create_field_edit_keyboard,
    create_participant_edit_keyboard,
    get_field_icon,
)
from src.bot.messages import InfoMessages
from src.config.settings import get_settings
from src.models.participant import Gender, Participant, Role
from src.services.participant_update_service import (
    ParticipantUpdateService,
    ValidationError,
)
from src.services.search_service import format_participant_full

# Import repository factory at module level (no circular deps)
from src.services.service_factory import get_participant_repository
from src.services.user_interaction_logger import UserInteractionLogger

logger = logging.getLogger(__name__)


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


def _log_missing(
    user_logger: UserInteractionLogger,
    user_id: int,
    expected_action: str,
    error_context: str,
    error_type: str = "handler_error",
) -> None:
    """Compatibility wrapper for different log_missing_response signatures."""
    try:
        user_logger.log_missing_response(
            user_id=user_id,
            expected_action=expected_action,
            error_context=error_context,
        )
    except TypeError:
        # Fallback to legacy signature
        try:
            user_logger.log_missing_response(
                user_id=user_id,
                button_data=expected_action,
                error_type=error_type,
                error_message=error_context,
            )
        except Exception:
            # Swallow logging errors silently to avoid breaking flow
            pass


class EditStates(IntEnum):
    """Conversation states for participant editing flow."""

    FIELD_SELECTION = 0
    TEXT_INPUT = 1
    BUTTON_SELECTION = 2
    CONFIRMATION = 3


# (kept for reference)


def display_updated_participant(
    participant: Participant, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """
    Display complete participant information with current editing changes applied.

    Reconstructs participant object with all pending changes from the editing context
    and returns a formatted display string using format_participant_full().

    Args:
        participant: Original participant object
        context: Bot context containing editing_changes

    Returns:
        Formatted string with complete participant information including applied changes
    """
    # Get pending changes from context
    editing_changes = context.user_data.get("editing_changes", {})

    # Create a copy of the participant with changes applied
    updated_participant = Participant(
        record_id=participant.record_id,
        full_name_ru=editing_changes.get("full_name_ru", participant.full_name_ru),
        full_name_en=editing_changes.get("full_name_en", participant.full_name_en),
        church=editing_changes.get("church", participant.church),
        country_and_city=editing_changes.get(
            "country_and_city", participant.country_and_city
        ),
        contact_information=editing_changes.get(
            "contact_information", participant.contact_information
        ),
        submitted_by=editing_changes.get("submitted_by", participant.submitted_by),
        gender=editing_changes.get("gender", participant.gender),
        size=editing_changes.get("size", participant.size),
        role=editing_changes.get("role", participant.role),
        department=editing_changes.get("department", participant.department),
        payment_amount=editing_changes.get(
            "payment_amount", participant.payment_amount
        ),
        payment_status=editing_changes.get(
            "payment_status", participant.payment_status
        ),
        payment_date=editing_changes.get("payment_date", participant.payment_date),
        date_of_birth=editing_changes.get("date_of_birth", participant.date_of_birth),
        age=editing_changes.get("age", participant.age),
        floor=editing_changes.get("floor", getattr(participant, "floor", None)),
        room_number=editing_changes.get(
            "room_number", getattr(participant, "room_number", None)
        ),
    )

    # Use full participant formatting for complete transparency
    return format_participant_full(updated_participant, language="ru")


def reconstruct_participant_from_changes(
    editing_changes: dict, record_id: str = None
) -> str:
    """
    Reconstruct participant display from editing_changes when context is lost.

    Creates a formatted participant display using available editing changes data
    when the full participant context is not available.

    Args:
        editing_changes: Dictionary of field changes from editing session
        record_id: Optional record ID for context

    Returns:
        Formatted string with available participant information and recovery guidance
    """
    if not editing_changes:
        return (
            "⚠️ Информация об участнике временно недоступна.\n"
            "Ваши изменения сохранены, но полные данные не отображены.\n\n"
            "🔄 Вернитесь в главное меню и найдите участника снова для просмотра обновленной информации."
        )

    # Create display from available changes
    display_parts = ["📋 Обновленная информация:"]

    # Field labels for Russian display
    field_labels = {
        "full_name_ru": "👤 Имя на русском",
        "full_name_en": "👤 Имя на английском",
        "church": "⛪ Церковь",
        "country_and_city": "📍 Местоположение",
        "contact_information": "📞 Контакты",
        "submitted_by": "👥 Кто подал",
        "payment_amount": "💰 Сумма платежа",
        "gender": "👤 Пол",
        "size": "📏 Размер",
        "role": "📋 Роль",
        "department": "🏢 Департамент",
        "floor": "🏢 Этаж",
        "room_number": "🚪 Номер комнаты",
        "date_of_birth": "🎂 Дата рождения",
        "age": "🔢 Возраст",
    }

    for field, value in editing_changes.items():
        if field in field_labels:
            # Format date_of_birth if it's a date object
            if field == "date_of_birth" and hasattr(value, "isoformat"):
                formatted_value = value.isoformat()
            else:
                formatted_value = value
            display_parts.append(f"{field_labels[field]}: **{formatted_value}**")

    display_parts.extend(
        [
            "",
            "ℹ️ Показаны только измененные поля.",
            "🔄 Для просмотра полной информации найдите участника через поиск.",
        ]
    )

    return "\n".join(display_parts)


async def show_participant_edit_menu(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show participant editing interface with all fields.

    Displays current participant data with individual edit buttons for each field.
    Initializes editing state if needed.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (FIELD_SELECTION)
    """
    query = update.callback_query
    if query:
        await query.answer()

    # Get current participant from context
    participant = context.user_data.get("current_participant")
    if not participant:
        logger.error("No participant data found in context for editing")

        error_message = "Ошибка: данные участника не найдены."
        if query:
            await query.message.edit_text(
                text=error_message,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "🏠 Главное меню", callback_data="main_menu"
                            )
                        ]
                    ]
                ),
            )

        return EditStates.FIELD_SELECTION

    # Initialize editing state
    if "editing_changes" not in context.user_data:
        context.user_data["editing_changes"] = {}
    context.user_data["editing_field"] = None

    logger.info(f"Showing edit menu for participant: {participant.record_id}")

    # Remove reply keyboard while in edit mode to avoid confusion with inline UI
    try:
        if query and query.message:
            await query.message.reply_text(text=" ", reply_markup=ReplyKeyboardRemove())
    except Exception:
        # Non-fatal if remove fails
        pass

    # Create edit interface message
    message_text = "✏️ Редактирование участника\n\n"

    # Display current field values with Russian labels
    message_text += f"👤 Имя (русское): {participant.full_name_ru or 'Не указано'}\n"
    message_text += f"🌍 Имя (английское): {participant.full_name_en or 'Не указано'}\n"
    message_text += f"⛪ Церковь: {participant.church or 'Не указано'}\n"
    message_text += (
        f"📍 Местоположение: {participant.country_and_city or 'Не указано'}\n"
    )
    message_text += f"📞 Контакты: {participant.contact_information or 'Не указано'}\n"
    message_text += f"👨‍💼 Кто подал: {participant.submitted_by or 'Не указано'}\n"

    # Convert enum values to Russian for display
    gender_display = (
        "Мужской"
        if participant.gender == Gender.MALE
        else "Женский" if participant.gender == Gender.FEMALE else "Не указано"
    )
    message_text += f"👫 Пол: {gender_display}\n"
    message_text += f"👕 Размер: {participant.size or 'Не указано'}\n"

    role_display = (
        "Кандидат"
        if participant.role == Role.CANDIDATE
        else "Команда" if participant.role == Role.TEAM else "Не указано"
    )
    message_text += f"👥 Роль: {role_display}\n"
    message_text += f"📋 Департамент: {participant.department or 'Не указано'}\n"

    # Payment amount is still editable, but status/date are automated
    message_text += f"💵 Сумма платежа: {participant.payment_amount or 'Не указано'}\n"

    # Accommodation fields
    floor_display = getattr(participant, "floor", None)
    room_display = getattr(participant, "room_number", None)
    message_text += f"🏢 Этаж: {floor_display if floor_display not in (None, '') else 'Не указано'}\n"
    message_text += f"🚪 Номер комнаты: {room_display if room_display not in (None, '') else 'Не указано'}\n"

    # Date of birth and age fields
    date_of_birth_display = (
        participant.date_of_birth.isoformat() if participant.date_of_birth else "Не указано"
    )
    message_text += f"🎂 Дата рождения: {date_of_birth_display}\n"
    age_display = participant.age if participant.age is not None else 'Не указано'
    message_text += f"🔢 Возраст: {age_display}\n"

    # Show pending changes if any
    pending_changes = context.user_data.get("editing_changes", {})
    if pending_changes:
        message_text += f"\n⚠️ Несохраненные изменения: {len(pending_changes)}\n"

    message_text += "\nВыберите поле для редактирования:"

    # Create keyboard with field edit buttons
    keyboard = create_participant_edit_keyboard()

    if query:
        await query.message.edit_text(text=message_text, reply_markup=keyboard)

    return EditStates.FIELD_SELECTION


async def handle_field_edit_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle field edit button selection.

    Routes to appropriate input method based on field type:
    - Text input for free-text fields
    - Button selection for predefined options

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state based on field type
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

    # Parse field name from callback data
    field_name = query.data.split(":")[1]
    context.user_data["editing_field"] = field_name

    logger.info(f"User {user.id} selected field for editing: {field_name}")

    # Define field types and their input methods
    # Note: payment_status and payment_date are excluded as they are automatically
    # handled when payment_amount is entered (payment automation)
    BUTTON_FIELDS = ["gender", "size", "role", "department"]
    TEXT_FIELDS = [
        "full_name_ru",
        "full_name_en",
        "church",
        "country_and_city",
        "contact_information",
        "submitted_by",
        "payment_amount",
        "floor",
        "room_number",
        "date_of_birth",
        "age",
    ]

    if field_name in BUTTON_FIELDS:
        # Show button selection interface
        next_state = await show_field_button_selection(update, context, field_name)

        # Log bot response if logging is enabled
        if user_logger:
            user_logger.log_bot_response(
                user_id=user.id,
                response_type="edit_message",
                content=f"Field button selection for {field_name}",
                keyboard_info=f"Button options for field: {field_name}",
            )

        return next_state

    elif field_name in TEXT_FIELDS:
        # Show text input prompt
        next_state = await show_field_text_prompt(update, context, field_name)

        # Log bot response if logging is enabled
        if user_logger:
            user_logger.log_bot_response(
                user_id=user.id,
                response_type="edit_message",
                content=f"Text input prompt for {field_name}",
                keyboard_info="Cancel button",
            )

        return next_state

    else:
        logger.error(f"Unknown field type for editing: {field_name}")
        await query.message.edit_text(
            text="Ошибка: неизвестное поле для редактирования.",
            reply_markup=create_participant_edit_keyboard(),
        )

        # Log missing response if logging is enabled
        if user_logger:
            _log_missing(
                user_logger,
                user_id=user.id,
                expected_action="field_edit_selection",
                error_context=f"Unknown field type: {field_name}",
            )

        return EditStates.FIELD_SELECTION


async def show_field_button_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE, field_name: str
) -> int:
    """Show button selection interface for predefined field values."""
    query = update.callback_query

    # Field-specific prompts and keyboards
    field_prompts = {
        "gender": "Выберите пол:",
        "size": "Выберите размер:",
        "role": "Выберите роль:",
        "department": "Выберите Департамент:",
        "payment_status": "Выберите статус платежа:",
    }

    prompt = field_prompts.get(field_name, f"Выберите значение для {field_name}:")
    keyboard = create_field_edit_keyboard(field_name)

    await query.message.edit_text(text=prompt, reply_markup=keyboard)

    return EditStates.BUTTON_SELECTION


async def show_field_text_prompt(
    update: Update, context: ContextTypes.DEFAULT_TYPE, field_name: str
) -> int:
    """Show text input prompt for text fields."""
    query = update.callback_query

    # Field-specific prompts
    field_prompts = {
        "full_name_ru": "Отправьте новое имя на русском:",
        "full_name_en": "Отправьте новое имя на английском:",
        "church": "Отправьте название церкви:",
        "country_and_city": "Отправьте страну и город:",
        "contact_information": "Отправьте контактную информацию:",
        "submitted_by": "Отправьте имя того, кто подал:",
        "payment_amount": "Отправьте сумму платежа (только цифры):",
        "payment_date": "Отправьте дату в формате ГГГГ-ММ-ДД:",
        "floor": "Отправьте этаж (только цифры):",
        "room_number": "Отправьте номер комнаты (только цифры):",
        "date_of_birth": InfoMessages.ENTER_DATE_OF_BIRTH,
        "age": InfoMessages.ENTER_AGE,
    }

    prompt = field_prompts.get(
        field_name, f"Отправьте новое значение для {field_name}:"
    )

    await query.message.edit_text(
        text=prompt,
        reply_markup=InlineKeyboardMarkup(
            [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")]]
        ),
    )

    return EditStates.TEXT_INPUT


async def handle_text_field_input(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle text input for field editing.

    Validates input based on field type and stores changes.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (FIELD_SELECTION on success, TEXT_INPUT on error)
    """
    user_input = update.message.text.strip()
    field_name = context.user_data.get("editing_field")
    user = update.effective_user

    if not field_name:
        logger.error(f"No editing field set for user {user.id}")
        await update.message.reply_text(
            text="Ошибка: поле для редактирования не выбрано.",
            reply_markup=create_participant_edit_keyboard(),
        )
        return EditStates.FIELD_SELECTION

    logger.info(f"User {user.id} provided input '{user_input}' for field {field_name}")

    # Validate and convert input using update service
    try:
        update_service = ParticipantUpdateService()
        validated_value = update_service.validate_field_input(field_name, user_input)

        # Store the change
        context.user_data["editing_changes"][field_name] = validated_value
        context.user_data["editing_field"] = None

        # Display complete participant information with updated values
        participant = context.user_data.get("current_participant")
        if participant:
            try:
                complete_display = display_updated_participant(participant, context)

                await update.message.reply_text(
                    text=complete_display,
                    reply_markup=create_participant_edit_keyboard(),
                )
            except Exception as e:
                logger.error(
                    f"REGRESSION|DISPLAY_FUNCTION_ERROR|user_id={user.id}|field={field_name}|error={str(e)}"
                )

                # Fallback to simple success message with warning
                field_labels = {
                    "full_name_ru": "Имя на русском",
                    "full_name_en": "Имя на английском",
                    "church": "Церковь",
                    "country_and_city": "Местоположение",
                    "contact_information": "Контакты",
                    "submitted_by": "Кто подал",
                    "payment_amount": "Сумма платежа",
                    "floor": "Этаж",
                    "room_number": "Номер комнаты",
                    "date_of_birth": "Дата рождения",
                    "age": "Возраст",
                }

                field_label = field_labels.get(field_name, field_name)
                field_icon = get_field_icon(field_name)
                success_message = f"{field_icon} {field_label} обновлено: {user_input}\n\n⚠️ Полная информация временно недоступна"

                await update.message.reply_text(
                    text=success_message,
                    reply_markup=create_participant_edit_keyboard(),
                )
        else:
            # Fallback without participant context: simple message only (no reconstructed display)
            logger.error(
                f"REGRESSION|CONTEXT_LOSS|user_id={user.id}|field={field_name}|session_data={len(context.user_data.get('editing_changes', {}))} changes"
            )
            field_labels = {
                "full_name_ru": "Имя на русском",
                "full_name_en": "Имя на английском",
                "church": "Церковь",
                "country_and_city": "Местоположение",
                "contact_information": "Контакты",
                "submitted_by": "Кто подал",
                "payment_amount": "Сумма платежа",
                "date_of_birth": "Дата рождения",
                "age": "Возраст",
            }
            field_label = field_labels.get(field_name, field_name)
            field_icon = get_field_icon(field_name)
            success_message = f"{field_icon} {field_label} обновлено: {user_input}"
            await update.message.reply_text(
                text=success_message, reply_markup=create_participant_edit_keyboard()
            )

        return EditStates.FIELD_SELECTION

    except ValidationError as e:
        logger.info(f"Validation error for user {user.id} field {field_name}: {e}")

        await update.message.reply_text(
            text=f"❌ Ошибка: {e}",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")]]
            ),
        )

        return EditStates.TEXT_INPUT

    except Exception as e:
        logger.error(
            f"Unexpected error validating field {field_name} for user {user.id}: {e}"
        )

        await update.message.reply_text(
            text="❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")]]
            ),
        )

        return EditStates.TEXT_INPUT


async def handle_button_field_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Handle button selection for predefined field values.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Next conversation state (FIELD_SELECTION)
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

    field_name = context.user_data.get("editing_field")
    if not field_name:
        logger.error(f"No editing field set for user {user.id}")

        # Log missing response if logging is enabled
        if user_logger:
            _log_missing(
                user_logger,
                user_id=user.id,
                expected_action="button_field_selection",
                error_context="No editing field set in context",
                error_type="context_error",
            )

        return EditStates.FIELD_SELECTION

    # Parse selected value from callback data
    selected_value = query.data.split(":")[1]

    logger.info(f"User {user.id} selected {selected_value} for field {field_name}")

    # Convert string value to appropriate enum/type
    try:
        update_service = ParticipantUpdateService()
        validated_value = update_service.convert_button_value(
            field_name, selected_value
        )

        # Special handling for role → department business logic
        auto_message: Optional[str] = None
        prompt_department = False
        if field_name == "role":
            participant = context.user_data.get("current_participant")
            editing_changes = context.user_data.get("editing_changes", {})
            # Determine current effective role (consider previous unsaved changes)
            current_role = editing_changes.get(
                "role", getattr(participant, "role", None)
            )
            actions = update_service.get_role_department_actions(
                current_role, validated_value
            )

            if actions.get("clear_department"):
                # Clear any selected department when moving to CANDIDATE
                editing_changes["department"] = None
                context.user_data["editing_changes"] = editing_changes
                auto_message = update_service.build_auto_action_message(
                    "clear_department"
                )

            if actions.get("prompt_department"):
                prompt_department = True
                auto_message = update_service.build_auto_action_message(
                    "prompt_department"
                )

        # Store the change
        context.user_data["editing_changes"][field_name] = validated_value
        context.user_data["editing_field"] = None

        # Convert value back to Russian for display (needed for logging)
        display_value = update_service.get_russian_display_value(
            field_name, validated_value
        )

        # If we need to prompt for department, show department keyboard immediately
        if prompt_department:
            context.user_data["editing_field"] = "department"
            # Prefix prompt with auto_message if available
            if auto_message:
                await query.message.edit_text(
                    text=auto_message,
                    reply_markup=create_field_edit_keyboard("department"),
                )
            else:
                # Use standard flow
                return await show_field_button_selection(update, context, "department")

            # Stay in BUTTON_SELECTION state to await department
            return EditStates.BUTTON_SELECTION

        # Display complete participant information with updated values
        participant = context.user_data.get("current_participant")
        if participant:
            try:
                complete_display = display_updated_participant(participant, context)
                # Prepend auto action info if any
                if auto_message:
                    complete_display = f"{auto_message}\n\n{complete_display}"

                await query.message.edit_text(
                    text=complete_display,
                    reply_markup=create_participant_edit_keyboard(),
                )
            except Exception as e:
                logger.error(
                    f"REGRESSION|DISPLAY_FUNCTION_ERROR|user_id={user.id}|field={field_name}|error={str(e)}"
                )

                # Fallback to simple success message with warning
                field_labels = {
                    "gender": "Пол",
                    "size": "Размер",
                    "role": "Роль",
                    "department": "Департамент",
                    "payment_status": "Статус платежа",
                }

                field_label = field_labels.get(field_name, field_name)
                success_message = f"✅ {field_label} обновлено: {display_value}\n\n⚠️ Полная информация временно недоступна"

                await query.message.edit_text(
                    text=success_message,
                    reply_markup=create_participant_edit_keyboard(),
                )
        else:
            # Fallback without participant context: simple message only (no reconstructed display)
            logger.error(
                f"REGRESSION|CONTEXT_LOSS|user_id={user.id}|field={field_name}|session_data={len(context.user_data.get('editing_changes', {}))} changes"
            )
            field_labels = {
                "gender": "Пол",
                "size": "Размер",
                "role": "Роль",
                "department": "Департамент",
                "payment_status": "Статус платежа",
                "floor": "Этаж",
                "room_number": "Номер комнаты",
            }
            field_label = field_labels.get(field_name, field_name)
            success_message = f"✅ {field_label} обновлено: {display_value}"
            await query.message.edit_text(
                text=success_message, reply_markup=create_participant_edit_keyboard()
            )

        # Log bot response if logging is enabled
        if user_logger:
            user_logger.log_bot_response(
                user_id=user.id,
                response_type="edit_message",
                content=f"Field {field_name} updated to {display_value}",
                keyboard_info="Participant edit menu",
            )

        return EditStates.FIELD_SELECTION

    except (ValueError, KeyError) as e:
        logger.error(
            f"Invalid button value {selected_value} for field {field_name}: {e}"
        )

        await query.message.edit_text(
            text=f"❌ Ошибка: неверное значение для поля {field_name}.",
            reply_markup=create_field_edit_keyboard(field_name),
        )

        # Log missing response if logging is enabled
        if user_logger:
            _log_missing(
                user_logger,
                user_id=user.id,
                expected_action="button_field_selection",
                error_context=f"Invalid button value {selected_value} for field {field_name}: {e}",
                error_type="validation_error",
            )

        return EditStates.BUTTON_SELECTION


async def cancel_editing(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Cancel editing and return to search results.

    Clears all editing state and returns to previous conversation state.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Previous conversation state (SHOWING_RESULTS)
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

    logger.info(f"User {user.id} cancelled editing")

    # Clear editing state
    context.user_data["editing_changes"] = {}
    context.user_data["editing_field"] = None

    # Return to search results
    from src.bot.handlers.search_handlers import (
        SearchStates,
        get_results_navigation_keyboard,
    )

    # Update message text; reply keyboards must be sent in a separate message
    await query.message.edit_text(text="❌ Редактирование отменено.")
    # Restore navigation reply keyboard for results view
    await query.message.reply_text(
        text="Используйте клавиатуру для навигации.",
        reply_markup=get_results_navigation_keyboard(),
    )

    # Log bot response if logging is enabled
    if user_logger:
        user_logger.log_bot_response(
            user_id=user.id,
            response_type="edit_message",
            content="Editing cancelled",
            keyboard_info="Search results keyboard",
        )

    return SearchStates.SHOWING_RESULTS


async def save_changes(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Save pending changes to repository.

    Applies all pending field changes to the participant record in Airtable.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Previous conversation state (SHOWING_RESULTS)
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

    changes = context.user_data.get("editing_changes", {})
    participant = context.user_data.get("current_participant")

    logger.info(f"User {user.id} saving {len(changes)} changes")

    if not changes:
        await query.message.edit_text(
            text="ℹ️ Нет изменений для сохранения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
            ),
        )
        from src.bot.handlers.search_handlers import SearchStates

        return SearchStates.SHOWING_RESULTS

    if not participant or not participant.record_id:
        logger.error(f"No participant record ID for user {user.id}")
        await query.message.edit_text(
            text="❌ Ошибка: не удается определить участника для сохранения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
            ),
        )
        from src.bot.handlers.search_handlers import SearchStates

        return SearchStates.SHOWING_RESULTS

    try:
        # Enforce department requirement for TEAM role before saving
        update_service = ParticipantUpdateService()
        effective_role = changes.get("role", getattr(participant, "role", None))
        effective_department = changes.get(
            "department", getattr(participant, "department", None)
        )
        if (
            update_service.requires_department(effective_role)
            and not effective_department
        ):
            # Prompt user to select department and block save
            context.user_data["editing_field"] = "department"
            message = update_service.build_auto_action_message("prompt_department")
            await query.message.edit_text(
                text=message, reply_markup=create_field_edit_keyboard("department")
            )
            from src.bot.handlers.search_handlers import SearchStates

            return EditStates.BUTTON_SELECTION

        # Optionally apply payment automation if enabled and applicable
        suppress_automation = bool(context.user_data.get("suppress_payment_automation"))
        if not suppress_automation and "payment_amount" in changes:
            service = ParticipantUpdateService()
            amount = changes["payment_amount"]
            if service.is_paid_amount(amount):
                automated_fields = service.get_automated_payment_fields(amount)
                changes.update(automated_fields)
                logger.info(
                    f"Payment automation triggered for user {user.id}: amount={amount}, automated {automated_fields}"
                )

        # Update participant in repository
        repository = get_participant_repository()
        success = await repository.update_by_id(participant.record_id, changes)

        if success:
            # Update the participant object in context with changes
            for field, value in changes.items():
                setattr(participant, field, value)

            # Clear editing state
            context.user_data["editing_changes"] = {}
            context.user_data["editing_field"] = None
            context.user_data["suppress_payment_automation"] = False

            # Try to display the full updated participant profile. If it fails, fallback to short message.
            try:
                success_message = (
                    f"✅ Изменения сохранены успешно!\n\n"
                    f"{format_participant_full(participant, language='ru')}"
                )
                await query.message.edit_text(
                    text=success_message,
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🏠 Главное меню", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
                # Restore navigation reply keyboard for results view
                try:
                    from src.bot.handlers.search_handlers import (
                        get_results_navigation_keyboard,
                    )

                    await query.message.reply_text(
                        text="Используйте клавиатуру для навигации.",
                        reply_markup=get_results_navigation_keyboard(),
                    )
                except Exception:
                    pass
            except Exception as display_error:
                # Log regression marker to help diagnose display formatting errors
                logger.error(
                    f"REGRESSION|SAVE_DISPLAY_ERROR - Failed to render full participant after save for user {user.id}: {display_error}"
                )
                await query.message.edit_text(
                    text=f"✅ Изменения сохранены успешно! Обновлено полей: {len(changes)}",
                    reply_markup=InlineKeyboardMarkup(
                        [
                            [
                                InlineKeyboardButton(
                                    "🏠 Главное меню", callback_data="main_menu"
                                )
                            ]
                        ]
                    ),
                )
                # Restore navigation reply keyboard for results view
                try:
                    from src.bot.handlers.search_handlers import (
                        get_results_navigation_keyboard,
                    )

                    await query.message.reply_text(
                        text="Используйте клавиатуру для навигации.",
                        reply_markup=get_results_navigation_keyboard(),
                    )
                except Exception:
                    pass

            # Log successful save response if logging is enabled (short summary for logs is OK)
            if user_logger:
                user_logger.log_bot_response(
                    user_id=user.id,
                    response_type="edit_message",
                    content=f"Changes saved successfully: {len(changes)} fields updated",
                    keyboard_info="Main menu button",
                )

        else:
            # Create retry keyboard
            retry_keyboard = [
                [
                    InlineKeyboardButton("🔄 Повторить", callback_data="retry_save"),
                    InlineKeyboardButton("❌ Отменить", callback_data="cancel_editing"),
                ],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
            ]

            await query.message.edit_text(
                text="❌ Ошибка при сохранении изменений. Проверьте подключение и попробуйте еще раз.",
                reply_markup=InlineKeyboardMarkup(retry_keyboard),
            )

            # Log failed save response if logging is enabled
            if user_logger:
                _log_missing(
                    user_logger,
                    user_id=user.id,
                    expected_action="save_changes",
                    error_context="Save operation failed",
                    error_type="save_error",
                )

    except Exception as e:
        logger.error(f"Error saving changes for user {user.id}: {e}")

        # Create retry keyboard for exceptions
        retry_keyboard = [
            [
                InlineKeyboardButton("🔄 Повторить", callback_data="retry_save"),
                InlineKeyboardButton("❌ Отменить", callback_data="cancel_editing"),
            ],
            [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
        ]

        await query.message.edit_text(
            text="❌ Произошла ошибка при сохранении. Проверьте подключение и попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup(retry_keyboard),
        )

        # Log exception response if logging is enabled
        if user_logger:
            _log_missing(
                user_logger,
                user_id=user.id,
                expected_action="save_changes",
                error_context=f"Exception during save: {e}",
                error_type="exception",
            )

    from src.bot.handlers.search_handlers import SearchStates

    return SearchStates.SHOWING_RESULTS


async def show_save_confirmation(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """
    Show save confirmation with summary of pending changes.

    Displays all pending changes and asks user to confirm before saving to Airtable.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        CONFIRMATION state to wait for user confirmation
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

    changes = context.user_data.get("editing_changes", {})
    participant = context.user_data.get("current_participant")

    logger.info(
        f"User {user.id} requesting save confirmation for {len(changes)} changes"
    )

    if not changes:
        await query.message.edit_text(
            text="ℹ️ Нет изменений для сохранения.",
            reply_markup=InlineKeyboardMarkup(
                [[InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")]]
            ),
        )

        # Log bot response if logging is enabled
        if user_logger:
            user_logger.log_bot_response(
                user_id=user.id,
                response_type="edit_message",
                content="No changes to save",
                keyboard_info="Main menu button",
            )

        from src.bot.handlers.search_handlers import SearchStates

        return SearchStates.SHOWING_RESULTS

    # Build changes summary and suppress payment automation for this confirmation flow
    # to avoid implicit field additions; payment automation has its own dedicated tests/flow.
    context.user_data["suppress_payment_automation"] = True
    # Build changes summary
    changes_text = "📝 **Изменения для сохранения:**\n\n"

    # Field name translations for user display
    field_translations = {
        "full_name_ru": "Имя (рус)",
        "full_name_en": "Имя (англ)",
        "role": "Роль",
        "gender": "Пол",
        "size": "Размер",
        "department": "Департамент",
        "church": "Церковь",
        "country_and_city": "Страна/город",
        "contact_information": "Контакты",
        "payment_amount": "Сумма оплаты",
        "payment_date": "Дата оплаты",
        "payment_status": "Статус оплаты",
        "submitted_by": "Кто подал",
        "floor": "Этаж",
        "room_number": "Номер комнаты",
        "date_of_birth": "Дата рождения",
        "age": "Возраст",
    }

    for field, new_value in changes.items():
        field_name = field_translations.get(field, field)

        # Get current value for comparison
        current_value = (
            getattr(participant, field, "Не задано") if participant else "Не задано"
        )

        # Format value display
        if isinstance(new_value, str):
            display_value = new_value
        elif hasattr(new_value, "value"):  # Enum values
            display_value = new_value.value
        elif field == "date_of_birth" and hasattr(new_value, "isoformat"):
            display_value = new_value.isoformat()
        else:
            display_value = str(new_value)

        changes_text += f"• **{field_name}**: {current_value} → **{display_value}**\n"

    changes_text += f"\n💾 Подтвердить сохранение {len(changes)} изменений?"

    # Create confirmation keyboard
    keyboard = [
        [
            InlineKeyboardButton("✅ Сохранить", callback_data="confirm_save"),
            InlineKeyboardButton("❌ Отменить", callback_data="cancel_editing"),
        ],
        [InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")],
    ]

    await query.message.edit_text(
        text=changes_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown",
    )

    # Log bot response if logging is enabled
    if user_logger:
        user_logger.log_bot_response(
            user_id=user.id,
            response_type="edit_message",
            content=f"Save confirmation for {len(changes)} changes",
            keyboard_info="Save/Cancel confirmation buttons",
        )

    return EditStates.CONFIRMATION


async def retry_save(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """
    Retry save operation after previous failure.

    Retries the save operation with the same pending changes.

    Args:
        update: Telegram update object
        context: Bot context

    Returns:
        Previous conversation state (SHOWING_RESULTS)
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

    logger.info(f"User {user.id} retrying save operation")

    # Call the regular save_changes function
    return await save_changes(update, context)
