"""
Participant field update service with validation.

Provides validation logic for all participant field types including text,
numeric, date, and enum fields with Russian error messages.
"""

import logging
from datetime import date
from typing import Any, Optional, Union

from src.models.participant import Department, Gender, PaymentStatus, Role, Size

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for field validation errors."""

    pass


class ParticipantUpdateService:
    """
    Service for validating and converting participant field updates.

    Handles validation for all participant fields with appropriate
    type conversion and Russian error messages.
    """

    # Field type classifications
    TEXT_FIELDS = [
        "full_name_ru",
        "full_name_en",
        "church",
        "country_and_city",
        "contact_information",
        "submitted_by",
        "church_leader",
        "table_name",
        "notes",
    ]

    BUTTON_FIELDS = ["gender", "size", "role", "department", "payment_status"]

    SPECIAL_FIELDS = [
        "payment_amount",
        "payment_date",
        "floor",
        "room_number",
        "date_of_birth",
        "age",
    ]

    # Required fields that cannot be empty
    REQUIRED_FIELDS = ["full_name_ru"]

    def validate_field_input(self, field_name: str, user_input: str) -> Any:
        """
        Validate and convert field input based on field type.

        Args:
            field_name: Name of the field being updated
            user_input: Raw user input string

        Returns:
            Validated and converted field value

        Raises:
            ValidationError: If input is invalid for the field type
        """
        # Trim whitespace for all fields except notes (which preserves formatting)
        if field_name != "notes":
            user_input = user_input.strip()

        if field_name in self.TEXT_FIELDS:
            return self._validate_text_field(field_name, user_input)

        elif field_name == "payment_amount":
            return self._validate_payment_amount(user_input)

        elif field_name == "payment_date":
            return self._validate_payment_date(user_input)

        elif field_name == "floor":
            return self._validate_floor(user_input)

        elif field_name == "room_number":
            return self._validate_room_number(user_input)

        elif field_name == "date_of_birth":
            return self._validate_date_of_birth(user_input)

        elif field_name == "age":
            return self._validate_age(user_input)

        else:
            raise ValidationError(f"Неизвестное поле для валидации: {field_name}")

    def _validate_text_field(self, field_name: str, user_input: str) -> str:
        """Validate text field input."""
        if not user_input and field_name in self.REQUIRED_FIELDS:
            raise ValidationError(
                f"Поле '{self._get_field_label(field_name)}' не может быть пустым"
            )

        # Special handling for notes field - preserve multiline and limit length
        if field_name == "notes":
            return self._validate_notes_field(user_input)

        # Apply length limits for other text fields
        if field_name == "church_leader" and len(user_input) > 100:
            raise ValidationError("Имя лидера церкви не может превышать 100 символов")

        if field_name == "table_name" and len(user_input) > 50:
            raise ValidationError("Название стола не может превышать 50 символов")

        return user_input

    def _validate_notes_field(self, user_input: str) -> str:
        """
        Validate notes field with multiline support.

        Preserves line breaks and formatting while applying length limits.
        """
        # Don't strip leading/trailing whitespace for notes to preserve formatting
        if len(user_input) > 5000:
            raise ValidationError("Заметки не могут превышать 5000 символов")

        return user_input

    def validate_table_name_business_rule(
        self, effective_role: Optional[Role], table_name: Optional[str]
    ) -> None:
        """
        Validate business rule that TableName is only allowed for CANDIDATE role.

        Args:
            effective_role: The effective role (current or changed)
            table_name: The table name value being saved

        Raises:
            ValidationError: If trying to save TableName for TEAM role
        """
        if table_name and effective_role == Role.TEAM:
            raise ValidationError("Название стола доступно только для роли «Кандидат»")

    def _validate_payment_amount(self, user_input: str) -> int:
        """
        Validate payment amount field.

        Returns just the validated amount as an integer. Payment automation
        is handled separately during the save process via get_automated_payment_fields.

        Returns:
            int: The validated payment amount
        """
        if not user_input:
            return 0  # Default to 0 for empty input

        try:
            amount = int(user_input)
            if amount < 0:
                raise ValidationError("Сумма платежа не может быть отрицательной")

            logger.info(f"Payment amount validated: {amount}")
            return amount
        except ValueError:
            raise ValidationError("Сумма платежа должна быть числом (только цифры)")

    def _validate_payment_date(self, user_input: str) -> date:
        """Validate payment date field."""
        if not user_input:
            raise ValidationError("Дата не может быть пустой")

        try:
            # Expected format: YYYY-MM-DD
            year, month, day = user_input.split("-")
            parsed_date = date(int(year), int(month), int(day))
            return parsed_date
        except ValueError as e:
            if "invalid literal" in str(e) or len(user_input.split("-")) != 3:
                raise ValidationError(
                    "Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 2024-01-15)"
                )
            else:
                raise ValidationError("Некорректная дата. Проверьте день и месяц.")
        except Exception:
            raise ValidationError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")

    def _validate_floor(self, user_input: str) -> Union[int, str]:
        """Validate floor field input.

        Accepts numeric strings (converted to int) and non-empty strings
        like 'Ground', 'Basement', returning them as-is. Empty -> ''.
        """
        value = user_input.strip()
        if value == "":
            return ""
        if value.isdigit():
            return int(value)
        return value

    def _validate_room_number(self, user_input: str) -> Union[int, str]:
        """Validate room number.

        Accepts numeric and alphanumeric values; returns '' for empty input.
        """
        value = user_input.strip()
        if value == "":
            return ""
        return value

    def _validate_date_of_birth(self, user_input: str) -> date | None:
        """Validate date of birth field in YYYY-MM-DD format."""
        # Handle clearing behavior: whitespace-only input clears the field
        if not user_input or user_input.strip() == "":
            return None

        try:
            # Expected format: YYYY-MM-DD
            year, month, day = user_input.split("-")
            if len(year) != 4 or len(month) != 2 or len(day) != 2:
                raise ValueError("Wrong format")
            parsed_date = date(int(year), int(month), int(day))
            return parsed_date
        except ValueError as e:
            if (
                "invalid literal" in str(e)
                or len(user_input.split("-")) != 3
                or "Wrong format" in str(e)
            ):
                from src.bot.messages import InfoMessages

                raise ValidationError(
                    f"❌ Неверный формат даты. {InfoMessages.ENTER_DATE_OF_BIRTH}"
                )
            else:
                from src.bot.messages import InfoMessages

                raise ValidationError(
                    f"❌ Некорректная дата. {InfoMessages.ENTER_DATE_OF_BIRTH}"
                )
        except Exception:
            from src.bot.messages import InfoMessages

            raise ValidationError(
                f"❌ Неверный формат даты. {InfoMessages.ENTER_DATE_OF_BIRTH}"
            )

    def _validate_age(self, user_input: str) -> int | None:
        """Validate age field as integer in 0-120 range."""
        # Handle clearing behavior: whitespace-only input clears the field
        if not user_input or user_input.strip() == "":
            return None

        try:
            age = int(user_input)
            if age < 0 or age > 120:
                from src.bot.messages import InfoMessages

                raise ValidationError(
                    f"❌ Возраст должен быть от 0 до 120. {InfoMessages.ENTER_AGE}"
                )

            logger.info(f"Age validated: {age}")
            return age
        except ValueError:
            from src.bot.messages import InfoMessages

            raise ValidationError(
                f"❌ Возраст должен быть числом. {InfoMessages.ENTER_AGE}"
            )

    def convert_button_value(
        self, field_name: str, selected_value: str
    ) -> Union[Gender, Size, Role, Department, PaymentStatus]:
        """
        Convert button selection to appropriate enum value.

        Args:
            field_name: Name of the field
            selected_value: Selected button value

        Returns:
            Appropriate enum value

        Raises:
            ValueError: If field is not a button field or value is invalid
        """
        if not self._is_button_field(field_name):
            raise ValueError(f"Field '{field_name}' is not a button field")

        try:
            if field_name == "gender":
                return Gender(selected_value)

            elif field_name == "size":
                return Size(selected_value)

            elif field_name == "role":
                return Role(selected_value)

            elif field_name == "department":
                return Department(selected_value)

            elif field_name == "payment_status":
                return PaymentStatus(selected_value)

        except ValueError:
            raise ValueError(f"Invalid {field_name} value: {selected_value}")
        # Safety: ensure all code paths return
        raise ValueError(f"Unsupported button field: {field_name}")

    def get_russian_display_value(self, field_name: str, field_value: Any) -> str:
        """
        Get Russian display representation of field value.

        Args:
            field_name: Name of the field
            field_value: Field value (enum or other type)

        Returns:
            Russian display string
        """
        # Gender translations
        if field_name == "gender":
            if field_value == Gender.MALE:
                return "Мужской"
            elif field_value == Gender.FEMALE:
                return "Женский"

        # Role translations
        elif field_name == "role":
            if field_value == Role.CANDIDATE:
                return "Кандидат"
            elif field_value == Role.TEAM:
                return "Команда"

        # Payment status translations
        elif field_name == "payment_status":
            if field_value == PaymentStatus.PAID:
                return "Оплачено"
            elif field_value == PaymentStatus.PARTIAL:
                return "Частично"
            elif field_value == PaymentStatus.UNPAID:
                return "Не оплачено"

        # For other fields (size, department), return the string value
        if hasattr(field_value, "value"):
            return str(field_value.value)

        return str(field_value)

    def is_paid_amount(self, amount: int) -> bool:
        """
        Determine if payment amount qualifies for automatic payment processing.

        Args:
            amount: Payment amount to check

        Returns:
            bool: True if amount >= 1, False otherwise
        """
        return amount >= 1

    def get_automated_payment_fields(self, amount: int) -> dict:
        """
        Generate automated field values when payment amount indicates payment.

        Args:
            amount: Payment amount that triggered automation

        Returns:
            dict: Automated field values with payment_status and payment_date
        """
        return {"payment_status": PaymentStatus.PAID, "payment_date": date.today()}

    def _is_text_field(self, field_name: str) -> bool:
        """Check if field is a text input field."""
        return field_name in self.TEXT_FIELDS

    def _is_button_field(self, field_name: str) -> bool:
        """Check if field is a button selection field."""
        return field_name in self.BUTTON_FIELDS

    def _is_special_field(self, field_name: str) -> bool:
        """Check if field is a special validation field."""
        return field_name in self.SPECIAL_FIELDS

    def _get_field_label(self, field_name: str) -> str:
        """Get Russian label for field name."""
        field_labels = {
            "full_name_ru": "Имя на русском",
            "full_name_en": "Имя на английском",
            "church": "Церковь",
            "country_and_city": "Местоположение",
            "contact_information": "Контакты",
            "submitted_by": "Кто подал",
            "gender": "Пол",
            "size": "Размер",
            "role": "Роль",
            "department": "Департамент",
            "payment_status": "Статус платежа",
            "payment_amount": "Сумма платежа",
            "payment_date": "Дата платежа",
            "floor": "Этаж",
            "room_number": "Номер комнаты",
            "date_of_birth": "Дата рождения",
            "age": "Возраст",
            "church_leader": "Лидер церкви",
            "table_name": "Название стола",
            "notes": "Заметки",
        }
        return field_labels.get(field_name, field_name)

    # === Role ↔ Department business logic helpers ===
    def detect_role_transition(self, old_role: Optional[Role], new_role: Role) -> str:
        """
        Determine the role transition type.

        Returns one of: 'NO_CHANGE', 'CANDIDATE_TO_TEAM', 'TEAM_TO_CANDIDATE'.
        If old_role is None, treat as 'NO_CHANGE' unless new_role is TEAM which
        will still require department downstream via requires_department().
        """
        try:
            if old_role == new_role:
                return "NO_CHANGE"
            if old_role == Role.CANDIDATE and new_role == Role.TEAM:
                return "CANDIDATE_TO_TEAM"
            if old_role == Role.TEAM and new_role == Role.CANDIDATE:
                return "TEAM_TO_CANDIDATE"
        except Exception:
            # Graceful fallback for unexpected values
            return "NO_CHANGE"
        return "NO_CHANGE"

    def requires_department(self, role: Optional[Role]) -> bool:
        """Return True if the given role requires a department selection."""
        return role == Role.TEAM

    def get_role_department_actions(
        self, old_role: Optional[Role], new_role: Role
    ) -> dict:
        """
        Compute automatic actions to apply when role changes.

        Returns a dict with flags:
        - clear_department: bool — clear department if changing to candidate
        - prompt_department: bool — prompt user to pick department when changing to team
        """
        transition = self.detect_role_transition(old_role, new_role)
        return {
            "clear_department": transition == "TEAM_TO_CANDIDATE",
            "prompt_department": transition == "CANDIDATE_TO_TEAM",
        }

    def build_auto_action_message(self, action: str) -> str:
        """
        Build a localized user-facing message for automatic actions.

        action: 'clear_department' | 'prompt_department'
        """
        if action == "clear_department":
            return "ℹ️ Департамент очищен из-за изменения роли на «Кандидат»."
        if action == "prompt_department":
            return "ℹ️ Для роли «Команда» необходимо выбрать Департамент. Пожалуйста, выберите Департамент."
        return ""
