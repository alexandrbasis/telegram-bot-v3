"""
Keyboard builders for participant editing functionality.

Provides inline keyboard layouts for field selection, value selection,
and editing workflow control with Russian labels.
"""

from typing import List, Optional

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from src.models.participant import (
    Department,
    Gender,
    PaymentStatus,
    Participant,
    Role,
    Size,
)


def get_field_icon(field_name: str) -> str:
    """
    Get the display icon for a specific field.

    Maps field names to their corresponding display icons used in participant
    information display, ensuring consistent visual language across the interface.

    Args:
        field_name: Name of the participant field

    Returns:
        Unicode emoji icon for the field, or default pencil icon if unknown
    """
    field_icons = {
        "full_name_ru": "👤",  # person
        "full_name_en": "🌍",  # globe
        "church": "⛪",  # church
        "country_and_city": "📍",  # location pin
        "contact_information": "📞",  # telephone
        "submitted_by": "👨‍💼",  # business person
        "gender": "👫",  # people
        "size": "👕",  # t-shirt
        "role": "👥",  # group
        "department": "📋",  # clipboard
        "payment_amount": "💵",  # money
        "floor": "🏢",  # building/floor
        "room_number": "🚪",  # door/room
        "date_of_birth": "🎂",  # birthday cake
        "age": "🔢",  # input numbers
        "church_leader": "🧑‍💼",  # church leader
        "table_name": "🪑",  # table
        "notes": "📝",  # notes
    }

    return field_icons.get(field_name, "✏️")  # Default to pencil for unknown fields


def create_participant_edit_keyboard(
    participant: Optional[Participant] = None,
) -> InlineKeyboardMarkup:
    """
    Create keyboard with edit buttons for participant fields.

    Generates buttons for editable participant fields with field-specific icons
    and Russian labels. Payment status and date are excluded as they are
    automatically handled when payment amount is entered. TableName is only
    shown for participants with CANDIDATE role.

    Args:
        participant: Optional participant object to determine role-based visibility

    Returns:
        InlineKeyboardMarkup with field edit buttons
    """
    keyboard = []

    # Text fields - row by row layout with field-specific icons
    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('full_name_ru')} Имя (русское)",
                callback_data="edit_field:full_name_ru",
            ),
            InlineKeyboardButton(
                f"{get_field_icon('full_name_en')} Имя (английское)",
                callback_data="edit_field:full_name_en",
            ),
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('church')} Церковь", callback_data="edit_field:church"
            ),
            InlineKeyboardButton(
                f"{get_field_icon('country_and_city')} Местоположение",
                callback_data="edit_field:country_and_city",
            ),
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('contact_information')} Контакты",
                callback_data="edit_field:contact_information",
            ),
            InlineKeyboardButton(
                f"{get_field_icon('submitted_by')} Кто подал",
                callback_data="edit_field:submitted_by",
            ),
        ]
    )

    # Selection fields with field-specific icons
    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('gender')} Пол", callback_data="edit_field:gender"
            ),
            InlineKeyboardButton(
                f"{get_field_icon('size')} Размер", callback_data="edit_field:size"
            ),
        ]
    )

    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('role')} Роль", callback_data="edit_field:role"
            ),
            InlineKeyboardButton(
                f"{get_field_icon('department')} Департамент",
                callback_data="edit_field:department",
            ),
        ]
    )

    # Payment amount field only (status/date are automated) + Accommodation fields
    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('payment_amount')} Сумма платежа",
                callback_data="edit_field:payment_amount",
            ),
            InlineKeyboardButton(
                f"{get_field_icon('floor')} Этаж", callback_data="edit_field:floor"
            ),
        ]
    )
    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('room_number')} Номер комнаты",
                callback_data="edit_field:room_number",
            )
        ]
    )

    # Demographic fields
    keyboard.append(
        [
            InlineKeyboardButton(
                f"{get_field_icon('date_of_birth')} Дата рождения",
                callback_data="edit_field:date_of_birth",
            ),
            InlineKeyboardButton(
                f"{get_field_icon('age')} Возраст",
                callback_data="edit_field:age",
            ),
        ]
    )

    # New fields - Church Leader and Notes for all roles
    church_leader_button = InlineKeyboardButton(
        f"{get_field_icon('church_leader')} Лидер церкви",
        callback_data="edit_field:church_leader",
    )
    notes_button = InlineKeyboardButton(
        f"{get_field_icon('notes')} Заметки",
        callback_data="edit_field:notes",
    )

    # Check if we should show TableName button (only for CANDIDATE role)
    participant_role = None
    if participant:
        participant_role = (
            participant.role.value
            if hasattr(participant.role, "value")
            else str(participant.role)
        ) if participant.role else None

    if participant_role == "CANDIDATE":
        # Add TableName button in a row with ChurchLeader
        keyboard.append([
            church_leader_button,
            InlineKeyboardButton(
                f"{get_field_icon('table_name')} Название стола",
                callback_data="edit_field:table_name",
            ),
        ])
        # Add Notes button on its own row
        keyboard.append([notes_button])
    else:
        # Add ChurchLeader and Notes buttons together
        keyboard.append([church_leader_button, notes_button])

    # Control buttons
    keyboard.append(
        [
            InlineKeyboardButton(
                "💾 Сохранить изменения", callback_data="save_changes"
            ),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit"),
        ]
    )

    return InlineKeyboardMarkup(keyboard)


def create_field_edit_keyboard(field_name: str) -> InlineKeyboardMarkup:
    """
    Create keyboard with options for specific field type.

    Generates inline keyboards with predefined values for selection fields
    (gender, size, role, department, payment_status).

    Args:
        field_name: Name of the field to create options for

    Returns:
        InlineKeyboardMarkup with field-specific options

    Raises:
        ValueError: If field_name is not a button-based field
    """
    if field_name == "gender":
        return _create_gender_keyboard()
    elif field_name == "size":
        return _create_size_keyboard()
    elif field_name == "role":
        return _create_role_keyboard()
    elif field_name == "department":
        return _create_department_keyboard()
    elif field_name == "payment_status":
        return _create_payment_status_keyboard()
    else:
        raise ValueError(f"Unknown field type for keyboard creation: {field_name}")


def _create_gender_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for gender selection."""
    keyboard = [
        [
            InlineKeyboardButton("🧔 Мужской", callback_data="select_value:M"),
            InlineKeyboardButton("👩 Женский", callback_data="select_value:F"),
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")],
    ]
    return InlineKeyboardMarkup(keyboard)


def _create_size_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for size selection."""
    keyboard = [
        [
            InlineKeyboardButton("XS", callback_data="select_value:XS"),
            InlineKeyboardButton("S", callback_data="select_value:S"),
            InlineKeyboardButton("M", callback_data="select_value:M"),
        ],
        [
            InlineKeyboardButton("L", callback_data="select_value:L"),
            InlineKeyboardButton("XL", callback_data="select_value:XL"),
            InlineKeyboardButton("XXL", callback_data="select_value:XXL"),
        ],
        [InlineKeyboardButton("3XL", callback_data="select_value:3XL")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")],
    ]
    return InlineKeyboardMarkup(keyboard)


def _create_role_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for role selection."""
    keyboard = [
        [
            InlineKeyboardButton("👤 Кандидат", callback_data="select_value:CANDIDATE"),
            InlineKeyboardButton("👥 Команда", callback_data="select_value:TEAM"),
        ],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")],
    ]
    return InlineKeyboardMarkup(keyboard)


def _create_department_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for department selection."""
    keyboard = [
        [
            InlineKeyboardButton("ROE", callback_data="select_value:ROE"),
            InlineKeyboardButton("Chapel", callback_data="select_value:Chapel"),
            InlineKeyboardButton("Setup", callback_data="select_value:Setup"),
        ],
        [
            InlineKeyboardButton("Palanka", callback_data="select_value:Palanka"),
            InlineKeyboardButton(
                "Administration", callback_data="select_value:Administration"
            ),
            InlineKeyboardButton("Kitchen", callback_data="select_value:Kitchen"),
        ],
        [
            InlineKeyboardButton("Decoration", callback_data="select_value:Decoration"),
            InlineKeyboardButton("Bell", callback_data="select_value:Bell"),
            InlineKeyboardButton(
                "Refreshment", callback_data="select_value:Refreshment"
            ),
        ],
        [
            InlineKeyboardButton("Worship", callback_data="select_value:Worship"),
            InlineKeyboardButton("Media", callback_data="select_value:Media"),
            InlineKeyboardButton("Clergy", callback_data="select_value:Clergy"),
        ],
        [InlineKeyboardButton("Rectorate", callback_data="select_value:Rectorate")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")],
    ]
    return InlineKeyboardMarkup(keyboard)


def _create_payment_status_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for payment status selection."""
    keyboard = [
        [
            InlineKeyboardButton("✅ Оплачено", callback_data="select_value:Paid"),
            InlineKeyboardButton("⏳ Частично", callback_data="select_value:Partial"),
        ],
        [InlineKeyboardButton("❌ Не оплачено", callback_data="select_value:Unpaid")],
        [InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit")],
    ]
    return InlineKeyboardMarkup(keyboard)


def create_save_cancel_keyboard() -> InlineKeyboardMarkup:
    """
    Create simple save/cancel keyboard.

    Used in confirmation dialogs and error states.

    Returns:
        InlineKeyboardMarkup with save and cancel buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("💾 Сохранить", callback_data="save_changes"),
            InlineKeyboardButton("❌ Отмена", callback_data="cancel_edit"),
        ]
    ]
    return InlineKeyboardMarkup(keyboard)
