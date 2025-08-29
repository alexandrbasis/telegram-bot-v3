"""
Telegram bot handlers for participant editing functionality.

Implements conversation flow for editing participant fields with field-specific
input methods (buttons for predefined values, text input for open fields).
"""

import logging
from enum import IntEnum
from typing import Optional
from datetime import date

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from src.models.participant import Participant, Gender, Size, Role, Department, PaymentStatus
from src.bot.keyboards.edit_keyboards import (
    create_participant_edit_keyboard,
    create_field_edit_keyboard,
    create_save_cancel_keyboard
)
from src.services.participant_update_service import (
    ParticipantUpdateService,
    ValidationError
)

logger = logging.getLogger(__name__)


class EditStates(IntEnum):
    """Conversation states for participant editing flow."""
    FIELD_SELECTION = 0
    TEXT_INPUT = 1
    BUTTON_SELECTION = 2
    CONFIRMATION = 3


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


async def show_participant_edit_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    participant = context.user_data.get('current_participant')
    if not participant:
        logger.error("No participant data found in context for editing")
        
        error_message = "Ошибка: данные участника не найдены."
        if query:
            await query.message.edit_text(
                text=error_message,
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]])
            )
        
        return EditStates.FIELD_SELECTION
    
    # Initialize editing state
    if 'editing_changes' not in context.user_data:
        context.user_data['editing_changes'] = {}
    context.user_data['editing_field'] = None
    
    logger.info(f"Showing edit menu for participant: {participant.record_id}")
    
    # Create edit interface message
    message_text = "✏️ Редактирование участника\n\n"
    
    # Display current field values with Russian labels
    message_text += f"👤 Имя (русское): {participant.full_name_ru or 'Не указано'}\n"
    message_text += f"🌍 Имя (английское): {participant.full_name_en or 'Не указано'}\n"
    message_text += f"⛪ Церковь: {participant.church or 'Не указано'}\n"
    message_text += f"📍 Местоположение: {participant.country_and_city or 'Не указано'}\n"
    message_text += f"📞 Контакты: {participant.contact_information or 'Не указано'}\n"
    message_text += f"👨‍💼 Отправитель: {participant.submitted_by or 'Не указано'}\n"
    
    # Convert enum values to Russian for display
    gender_display = "Мужской" if participant.gender == Gender.MALE else "Женский" if participant.gender == Gender.FEMALE else "Не указано"
    message_text += f"👫 Пол: {gender_display}\n"
    message_text += f"👕 Размер: {participant.size or 'Не указано'}\n"
    
    role_display = "Кандидат" if participant.role == Role.CANDIDATE else "Команда" if participant.role == Role.TEAM else "Не указано"
    message_text += f"👥 Роль: {role_display}\n"
    message_text += f"📋 Отдел: {participant.department or 'Не указано'}\n"
    
    payment_status_display = {
        PaymentStatus.PAID: "Оплачено",
        PaymentStatus.PARTIAL: "Частично",
        PaymentStatus.UNPAID: "Не оплачено"
    }.get(participant.payment_status, "Не указано")
    message_text += f"💰 Статус платежа: {payment_status_display}\n"
    
    message_text += f"💵 Сумма платежа: {participant.payment_amount or 'Не указано'}\n"
    message_text += f"📅 Дата платежа: {participant.payment_date or 'Не указано'}\n"
    
    # Show pending changes if any
    pending_changes = context.user_data.get('editing_changes', {})
    if pending_changes:
        message_text += f"\n⚠️ Несохраненные изменения: {len(pending_changes)}\n"
    
    message_text += "\nВыберите поле для редактирования:"
    
    # Create keyboard with field edit buttons
    keyboard = create_participant_edit_keyboard()
    
    if query:
        await query.message.edit_text(
            text=message_text,
            reply_markup=keyboard
        )
    
    return EditStates.FIELD_SELECTION


async def handle_field_edit_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    
    # Parse field name from callback data
    field_name = query.data.split(':')[1]
    context.user_data['editing_field'] = field_name
    
    logger.info(f"User {query.from_user.id} selected field for editing: {field_name}")
    
    # Define field types and their input methods
    BUTTON_FIELDS = ['gender', 'size', 'role', 'department', 'payment_status']
    TEXT_FIELDS = ['full_name_ru', 'full_name_en', 'church', 'country_and_city', 
                   'contact_information', 'submitted_by', 'payment_amount', 'payment_date']
    
    if field_name in BUTTON_FIELDS:
        # Show button selection interface
        return await show_field_button_selection(update, context, field_name)
    
    elif field_name in TEXT_FIELDS:
        # Show text input prompt
        return await show_field_text_prompt(update, context, field_name)
    
    else:
        logger.error(f"Unknown field type for editing: {field_name}")
        await query.message.edit_text(
            text="Ошибка: неизвестное поле для редактирования.",
            reply_markup=create_participant_edit_keyboard()
        )
        return EditStates.FIELD_SELECTION


async def show_field_button_selection(update: Update, context: ContextTypes.DEFAULT_TYPE, field_name: str) -> int:
    """Show button selection interface for predefined field values."""
    query = update.callback_query
    
    # Field-specific prompts and keyboards
    field_prompts = {
        'gender': "Выберите пол:",
        'size': "Выберите размер:",
        'role': "Выберите роль:",
        'department': "Выберите отдел:",
        'payment_status': "Выберите статус платежа:"
    }
    
    prompt = field_prompts.get(field_name, f"Выберите значение для {field_name}:")
    keyboard = create_field_edit_keyboard(field_name)
    
    await query.message.edit_text(
        text=prompt,
        reply_markup=keyboard
    )
    
    return EditStates.BUTTON_SELECTION


async def show_field_text_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE, field_name: str) -> int:
    """Show text input prompt for text fields."""
    query = update.callback_query
    
    # Field-specific prompts
    field_prompts = {
        'full_name_ru': "Отправьте новое имя на русском:",
        'full_name_en': "Отправьте новое имя на английском:",
        'church': "Отправьте название церкви:",
        'country_and_city': "Отправьте страну и город:",
        'contact_information': "Отправьте контактную информацию:",
        'submitted_by': "Отправьте имя отправителя:",
        'payment_amount': "Отправьте сумму платежа (только цифры):",
        'payment_date': "Отправьте дату в формате ГГГГ-ММ-ДД:"
    }
    
    prompt = field_prompts.get(field_name, f"Отправьте новое значение для {field_name}:")
    
    await query.message.edit_text(
        text=prompt,
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")
        ]])
    )
    
    return EditStates.TEXT_INPUT


async def handle_text_field_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    field_name = context.user_data.get('editing_field')
    user = update.effective_user
    
    if not field_name:
        logger.error(f"No editing field set for user {user.id}")
        await update.message.reply_text(
            text="Ошибка: поле для редактирования не выбрано.",
            reply_markup=create_participant_edit_keyboard()
        )
        return EditStates.FIELD_SELECTION
    
    logger.info(f"User {user.id} provided input '{user_input}' for field {field_name}")
    
    # Validate and convert input using update service
    try:
        update_service = ParticipantUpdateService()
        validated_value = update_service.validate_field_input(field_name, user_input)
        
        # Store the change
        context.user_data['editing_changes'][field_name] = validated_value
        context.user_data['editing_field'] = None
        
        # Confirm the change and return to edit menu
        field_labels = {
            'full_name_ru': 'Имя на русском',
            'full_name_en': 'Имя на английском',
            'church': 'Церковь',
            'country_and_city': 'Местоположение',
            'contact_information': 'Контакты',
            'submitted_by': 'Отправитель',
            'payment_amount': 'Сумма платежа',
            'payment_date': 'Дата платежа'
        }
        
        field_label = field_labels.get(field_name, field_name)
        success_message = f"✅ {field_label} обновлено: {user_input}"
        
        await update.message.reply_text(
            text=success_message,
            reply_markup=create_participant_edit_keyboard()
        )
        
        return EditStates.FIELD_SELECTION
        
    except ValidationError as e:
        logger.info(f"Validation error for user {user.id} field {field_name}: {e}")
        
        await update.message.reply_text(
            text=f"❌ Ошибка: {e}",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")
            ]])
        )
        
        return EditStates.TEXT_INPUT
    
    except Exception as e:
        logger.error(f"Unexpected error validating field {field_name} for user {user.id}: {e}")
        
        await update.message.reply_text(
            text="❌ Произошла ошибка. Попробуйте еще раз.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")
            ]])
        )
        
        return EditStates.TEXT_INPUT


async def handle_button_field_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
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
    
    field_name = context.user_data.get('editing_field')
    if not field_name:
        logger.error(f"No editing field set for user {query.from_user.id}")
        return EditStates.FIELD_SELECTION
    
    # Parse selected value from callback data
    selected_value = query.data.split(':')[1]
    
    logger.info(f"User {query.from_user.id} selected {selected_value} for field {field_name}")
    
    # Convert string value to appropriate enum/type
    try:
        update_service = ParticipantUpdateService()
        validated_value = update_service.convert_button_value(field_name, selected_value)
        
        # Store the change
        context.user_data['editing_changes'][field_name] = validated_value
        context.user_data['editing_field'] = None
        
        # Confirm the change and return to edit menu
        field_labels = {
            'gender': 'Пол',
            'size': 'Размер',
            'role': 'Роль',
            'department': 'Отдел',
            'payment_status': 'Статус платежа'
        }
        
        field_label = field_labels.get(field_name, field_name)
        # Convert value back to Russian for display
        display_value = update_service.get_russian_display_value(field_name, validated_value)
        success_message = f"✅ {field_label} обновлено: {display_value}"
        
        await query.message.edit_text(
            text=success_message,
            reply_markup=create_participant_edit_keyboard()
        )
        
        return EditStates.FIELD_SELECTION
        
    except (ValueError, KeyError) as e:
        logger.error(f"Invalid button value {selected_value} for field {field_name}: {e}")
        
        await query.message.edit_text(
            text=f"❌ Ошибка: неверное значение для поля {field_name}.",
            reply_markup=create_field_edit_keyboard(field_name)
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
    logger.info(f"User {user.id} cancelled editing")
    
    # Clear editing state
    context.user_data['editing_changes'] = {}
    context.user_data['editing_field'] = None
    
    # Return to search results
    from src.bot.handlers.search_handlers import SearchStates, get_search_button_keyboard
    
    await query.message.edit_text(
        text="❌ Редактирование отменено.",
        reply_markup=get_search_button_keyboard()
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
    changes = context.user_data.get('editing_changes', {})
    participant = context.user_data.get('current_participant')
    
    logger.info(f"User {user.id} saving {len(changes)} changes")
    
    if not changes:
        await query.message.edit_text(
            text="ℹ️ Нет изменений для сохранения.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]])
        )
        from src.bot.handlers.search_handlers import SearchStates
        return SearchStates.SHOWING_RESULTS
    
    if not participant or not participant.record_id:
        logger.error(f"No participant record ID for user {user.id}")
        await query.message.edit_text(
            text="❌ Ошибка: не удается определить участника для сохранения.",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
            ]])
        )
        from src.bot.handlers.search_handlers import SearchStates
        return SearchStates.SHOWING_RESULTS
    
    try:
        # Update participant in repository
        repository = get_participant_repository()
        success = await repository.update_by_id(participant.record_id, changes)
        
        if success:
            # Update the participant object in context with changes
            for field, value in changes.items():
                setattr(participant, field, value)
            
            # Clear editing state
            context.user_data['editing_changes'] = {}
            context.user_data['editing_field'] = None
            
            await query.message.edit_text(
                text=f"✅ Изменения сохранены успешно! Обновлено полей: {len(changes)}",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("🏠 Главное меню", callback_data="main_menu")
                ]])
            )
            
        else:
            await query.message.edit_text(
                text="❌ Ошибка при сохранении изменений. Попробуйте позже.",
                reply_markup=create_save_cancel_keyboard()
            )
            
    except Exception as e:
        logger.error(f"Error saving changes for user {user.id}: {e}")
        
        await query.message.edit_text(
            text="❌ Произошла ошибка при сохранении. Попробуйте позже.",
            reply_markup=create_save_cancel_keyboard()
        )
    
    from src.bot.handlers.search_handlers import SearchStates
    return SearchStates.SHOWING_RESULTS