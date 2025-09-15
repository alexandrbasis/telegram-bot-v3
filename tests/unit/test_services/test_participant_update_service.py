"""
Unit tests for participant update service.

Tests field validation logic, value conversion, and error handling
for all participant field types.
"""

from datetime import date

import pytest

from src.models.participant import Department, Gender, PaymentStatus, Role, Size
from src.services.participant_update_service import (
    ParticipantUpdateService,
    ValidationError,
)


class TestParticipantUpdateService:
    """Test ParticipantUpdateService functionality."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()


class TestValidateFieldInput:
    """Test validate_field_input method."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_validate_text_field_valid_input(self):
        """Test validation of valid text field input."""
        result = self.service.validate_field_input("full_name_ru", "Иван Петров")
        assert result == "Иван Петров"

        result = self.service.validate_field_input("church", "Церковь Грейс")
        assert result == "Церковь Грейс"

    def test_validate_text_field_empty_optional(self):
        """Test validation of empty optional text field."""
        result = self.service.validate_field_input("full_name_en", "")
        assert result == ""

        result = self.service.validate_field_input("church", "   ")
        assert result == ""

    def test_validate_text_field_empty_required_raises_error(self):
        """Test validation of empty required field raises ValidationError."""
        with pytest.raises(ValidationError, match="не может быть пустым"):
            self.service.validate_field_input("full_name_ru", "")

        with pytest.raises(ValidationError, match="не может быть пустым"):
            self.service.validate_field_input("full_name_ru", "   ")

    def test_validate_payment_amount_valid_integer(self):
        """Test validation of valid payment amount returns integer."""
        # Test paid amount returns just the integer (automation handled separately)
        result = self.service.validate_field_input("payment_amount", "1000")
        assert result == 1000

        # Test zero amount returns just the integer
        result = self.service.validate_field_input("payment_amount", "0")
        assert result == 0

    def test_validate_payment_amount_invalid_input(self):
        """Test validation of invalid payment amount raises error."""
        with pytest.raises(ValidationError, match="должна быть числом"):
            self.service.validate_field_input("payment_amount", "not_a_number")

        with pytest.raises(ValidationError, match="не может быть отрицательной"):
            self.service.validate_field_input("payment_amount", "-100")

    def test_validate_payment_date_valid_format(self):
        """Test validation of valid payment date."""
        result = self.service.validate_field_input("payment_date", "2024-01-15")
        assert result == date(2024, 1, 15)

        result = self.service.validate_field_input("payment_date", "2023-12-31")
        assert result == date(2023, 12, 31)

    def test_validate_payment_date_invalid_format(self):
        """Test validation of invalid date format raises error."""
        with pytest.raises(ValidationError, match="формат даты"):
            self.service.validate_field_input("payment_date", "2024/01/15")

        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input("payment_date", "15-01-2024")

        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input("payment_date", "2024-13-01")

        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input("payment_date", "2024-02-30")

    def test_validate_floor_field_valid_integer(self):
        """Test floor field accepts valid integer values."""
        result = self.service.validate_field_input("floor", "3")
        assert result == 3  # Floor validation returns integer for numeric input

        result = self.service.validate_field_input("floor", "10")
        assert result == 10

        result = self.service.validate_field_input("floor", "0")
        assert result == 0

    def test_validate_floor_field_valid_string(self):
        """Test floor field accepts valid string values (e.g., 'Ground', 'Basement')."""
        result = self.service.validate_field_input("floor", "Ground")
        assert result == "Ground"

        result = self.service.validate_field_input("floor", "Basement")
        assert result == "Basement"

        result = self.service.validate_field_input("floor", "Mezzanine")
        assert result == "Mezzanine"

    def test_validate_floor_field_empty_optional(self):
        """Test floor field handles empty/null values correctly."""
        result = self.service.validate_field_input("floor", "")
        assert result == ""

        result = self.service.validate_field_input("floor", "   ")
        assert result == ""

    def test_validate_room_number_field_valid_numeric(self):
        """Test room number field accepts valid numeric values."""
        result = self.service.validate_field_input("room_number", "101")
        assert result == "101"

        result = self.service.validate_field_input("room_number", "2045")
        assert result == "2045"

    def test_validate_room_number_field_valid_alphanumeric(self):
        """Test room number field accepts valid alphanumeric values."""
        result = self.service.validate_field_input("room_number", "A12B")
        assert result == "A12B"

        result = self.service.validate_field_input("room_number", "Suite 100")
        assert result == "Suite 100"

        result = self.service.validate_field_input("room_number", "301A")
        assert result == "301A"

    def test_validate_room_number_field_empty_optional(self):
        """Test room number field handles empty/null values correctly."""
        result = self.service.validate_field_input("room_number", "")
        assert result == ""

        result = self.service.validate_field_input("room_number", "   ")
        assert result == ""

    def test_validate_unknown_field_raises_error(self):
        """Test validation of unknown field raises error."""
        with pytest.raises(ValidationError, match="Неизвестное поле"):
            self.service.validate_field_input("unknown_field", "value")

    def test_validate_date_of_birth_field_valid_date(self):
        """Test validation of date_of_birth field with valid YYYY-MM-DD format."""
        result = self.service.validate_field_input("date_of_birth", "1990-05-15")

        expected_date = date(1990, 5, 15)
        assert result == expected_date
        assert isinstance(result, date)

    def test_validate_date_of_birth_field_invalid_format(self):
        """Test validation of date_of_birth field with invalid format raises error."""
        with pytest.raises(
            ValidationError, match="❌ Неверный формат даты.*Введите дату рождения"
        ):
            self.service.validate_field_input("date_of_birth", "15/05/1990")

        with pytest.raises(
            ValidationError, match="❌ Неверный формат даты.*Введите дату рождения"
        ):
            self.service.validate_field_input(
                "date_of_birth", "1990-5-15"
            )  # No zero padding

    def test_validate_date_of_birth_field_invalid_date(self):
        """Test validation of date_of_birth field with invalid date values."""
        with pytest.raises(
            ValidationError, match="❌ Некорректная дата.*Введите дату рождения"
        ):
            self.service.validate_field_input(
                "date_of_birth", "1990-13-01"
            )  # Invalid month

        with pytest.raises(
            ValidationError, match="❌ Некорректная дата.*Введите дату рождения"
        ):
            self.service.validate_field_input(
                "date_of_birth", "1990-02-30"
            )  # Invalid day

    def test_validate_age_field_valid_range(self):
        """Test validation of age field with valid numeric values in 0-120 range."""
        assert self.service.validate_field_input("age", "25") == 25
        assert self.service.validate_field_input("age", "0") == 0
        assert self.service.validate_field_input("age", "120") == 120

    def test_validate_age_field_invalid_range(self):
        """Test validation of age field with values outside 0-120 range raises error."""
        with pytest.raises(
            ValidationError, match="❌ Возраст должен быть от 0 до 120.*Введите возраст"
        ):
            self.service.validate_field_input("age", "121")

        with pytest.raises(
            ValidationError, match="❌ Возраст должен быть от 0 до 120.*Введите возраст"
        ):
            self.service.validate_field_input("age", "-1")

    def test_validate_age_field_non_numeric(self):
        """Test validation of age field with non-numeric input raises error."""
        with pytest.raises(
            ValidationError, match="❌ Возраст должен быть числом.*Введите возраст"
        ):
            self.service.validate_field_input("age", "двадцать пять")

        with pytest.raises(
            ValidationError, match="❌ Возраст должен быть числом.*Введите возраст"
        ):
            self.service.validate_field_input("age", "25.5")

    def test_validate_date_of_birth_field_clearing_behavior(self):
        """Test that whitespace-only input clears date_of_birth field."""
        # Whitespace should be treated as clearing the field
        result = self.service.validate_field_input("date_of_birth", "   ")
        assert result is None

        result = self.service.validate_field_input("date_of_birth", "\t\n ")
        assert result is None

        result = self.service.validate_field_input("date_of_birth", "")
        assert result is None

    def test_validate_age_field_clearing_behavior(self):
        """Test that whitespace-only input clears age field."""
        # Whitespace should be treated as clearing the field
        result = self.service.validate_field_input("age", "   ")
        assert result is None

        result = self.service.validate_field_input("age", "\t\n ")
        assert result is None

        result = self.service.validate_field_input("age", "")
        assert result is None

    def test_validate_church_leader_field_valid_input(self):
        """Test validation of church_leader field with valid input."""
        result = self.service.validate_field_input("church_leader", "Пастор Иванов")
        assert result == "Пастор Иванов"

        result = self.service.validate_field_input(
            "church_leader", "Архимандрит Георгий"
        )
        assert result == "Архимандрит Георгий"

    def test_validate_church_leader_field_empty_optional(self):
        """Test church_leader field handles empty values correctly."""
        result = self.service.validate_field_input("church_leader", "")
        assert result == ""

        result = self.service.validate_field_input("church_leader", "   ")
        assert result == ""

    def test_validate_church_leader_field_length_limit(self):
        """Test church_leader field length validation (max 100 characters)."""
        # Valid length (exactly 100 characters)
        valid_name = "А" * 100
        result = self.service.validate_field_input("church_leader", valid_name)
        assert result == valid_name

        # Invalid length (over 100 characters)
        invalid_name = "А" * 101
        with pytest.raises(ValidationError, match="не может превышать 100 символов"):
            self.service.validate_field_input("church_leader", invalid_name)

    def test_validate_table_name_field_valid_input(self):
        """Test validation of table_name field with valid input."""
        result = self.service.validate_field_input("table_name", "Основной стол")
        assert result == "Основной стол"

        result = self.service.validate_field_input("table_name", "VIP стол")
        assert result == "VIP стол"

    def test_validate_table_name_field_empty_optional(self):
        """Test table_name field handles empty values correctly."""
        result = self.service.validate_field_input("table_name", "")
        assert result == ""

        result = self.service.validate_field_input("table_name", "   ")
        assert result == ""

    def test_validate_table_name_field_length_limit(self):
        """Test table_name field length validation (max 50 characters)."""
        # Valid length (exactly 50 characters)
        valid_name = "Стол" * 12 + "Ст"  # 50 characters exactly
        result = self.service.validate_field_input("table_name", valid_name)
        assert result == valid_name

        # Invalid length (over 50 characters)
        invalid_name = "А" * 51
        with pytest.raises(ValidationError, match="не может превышать 50 символов"):
            self.service.validate_field_input("table_name", invalid_name)

    def test_validate_notes_field_multiline_input(self):
        """Test validation of notes field with multiline input."""
        multiline_notes = "Строка 1\nСтрока 2\nСтрока 3"
        result = self.service.validate_field_input("notes", multiline_notes)
        assert result == multiline_notes

        # Test with various line endings
        mixed_endings = "Windows line\r\nUnix line\nMac line\r"
        result = self.service.validate_field_input("notes", mixed_endings)
        assert result == mixed_endings

    def test_validate_notes_field_preserves_formatting(self):
        """Test notes field preserves formatting and whitespace."""
        formatted_notes = (
            "  Отступ в начале\n    Больший отступ\n\nПустая строка выше  "
        )
        result = self.service.validate_field_input("notes", formatted_notes)
        assert result == formatted_notes

        # Test with special characters
        special_notes = "Special chars: !@#$%^&*()\nEmoji: 🙏✝️\nUnicode: ñáéíóú"
        result = self.service.validate_field_input("notes", special_notes)
        assert result == special_notes

    def test_validate_notes_field_empty_optional(self):
        """Test notes field handles empty values correctly."""
        result = self.service.validate_field_input("notes", "")
        assert result == ""

        result = self.service.validate_field_input("notes", "   ")
        assert result == "   "  # Notes preserve whitespace

    def test_validate_notes_field_length_limit(self):
        """Test notes field length validation (max 5000 characters)."""
        # Valid length (exactly 5000 characters)
        valid_notes = "А" * 5000
        result = self.service.validate_field_input("notes", valid_notes)
        assert result == valid_notes

        # Invalid length (over 5000 characters)
        invalid_notes = "А" * 5001
        with pytest.raises(ValidationError, match="не могут превышать 5000 символов"):
            self.service.validate_field_input("notes", invalid_notes)


class TestConvertButtonValue:
    """Test convert_button_value method."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_convert_gender_values(self):
        """Test conversion of gender button values."""
        result = self.service.convert_button_value("gender", "M")
        assert result == Gender.MALE

        result = self.service.convert_button_value("gender", "F")
        assert result == Gender.FEMALE

    def test_convert_size_values(self):
        """Test conversion of size button values."""
        result = self.service.convert_button_value("size", "XL")
        assert result == Size.XL

        result = self.service.convert_button_value("size", "3XL")
        assert result == Size.XXXL

    def test_convert_role_values(self):
        """Test conversion of role button values."""
        result = self.service.convert_button_value("role", "CANDIDATE")
        assert result == Role.CANDIDATE

        result = self.service.convert_button_value("role", "TEAM")
        assert result == Role.TEAM

    def test_convert_department_values(self):
        """Test conversion of department button values."""
        result = self.service.convert_button_value("department", "Worship")
        assert result == Department.WORSHIP

        result = self.service.convert_button_value("department", "Kitchen")
        assert result == Department.KITCHEN

    def test_convert_payment_status_values(self):
        """Test conversion of payment status button values."""
        result = self.service.convert_button_value("payment_status", "Paid")
        assert result == PaymentStatus.PAID

        result = self.service.convert_button_value("payment_status", "Partial")
        assert result == PaymentStatus.PARTIAL

        result = self.service.convert_button_value("payment_status", "Unpaid")
        assert result == PaymentStatus.UNPAID

    def test_convert_invalid_field_raises_error(self):
        """Test conversion of invalid field raises ValueError."""
        with pytest.raises(ValueError, match="not a button field"):
            self.service.convert_button_value("full_name_ru", "value")

    def test_convert_invalid_value_raises_error(self):
        """Test conversion of invalid value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid .* value"):
            self.service.convert_button_value("gender", "INVALID")

        with pytest.raises(ValueError, match="Invalid .* value"):
            self.service.convert_button_value("size", "HUGE")


class TestGetRussianDisplayValue:
    """Test get_russian_display_value method."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_get_gender_display_values(self):
        """Test Russian display values for gender."""
        result = self.service.get_russian_display_value("gender", Gender.MALE)
        assert result == "Мужской"

        result = self.service.get_russian_display_value("gender", Gender.FEMALE)
        assert result == "Женский"

    def test_get_role_display_values(self):
        """Test Russian display values for role."""
        result = self.service.get_russian_display_value("role", Role.CANDIDATE)
        assert result == "Кандидат"

        result = self.service.get_russian_display_value("role", Role.TEAM)
        assert result == "Команда"

    def test_get_payment_status_display_values(self):
        """Test Russian display values for payment status."""
        result = self.service.get_russian_display_value(
            "payment_status", PaymentStatus.PAID
        )
        assert result == "Оплачено"

        result = self.service.get_russian_display_value(
            "payment_status", PaymentStatus.PARTIAL
        )
        assert result == "Частично"

        result = self.service.get_russian_display_value(
            "payment_status", PaymentStatus.UNPAID
        )
        assert result == "Не оплачено"

    def test_get_size_display_values(self):
        """Test display values for size (no translation needed)."""
        result = self.service.get_russian_display_value("size", Size.XL)
        assert result == "XL"

        result = self.service.get_russian_display_value("size", Size.XXXL)
        assert result == "3XL"

    def test_get_department_display_values(self):
        """Test display values for department (English preserved)."""
        result = self.service.get_russian_display_value(
            "department", Department.WORSHIP
        )
        assert result == "Worship"

        result = self.service.get_russian_display_value(
            "department", Department.KITCHEN
        )
        assert result == "Kitchen"

    def test_get_floor_display_values(self):
        """Test Russian display values for floor field."""
        result = self.service.get_russian_display_value("floor", 3)
        assert result == "3"

        result = self.service.get_russian_display_value("floor", "Ground")
        assert result == "Ground"

        result = self.service.get_russian_display_value("floor", "Basement")
        assert result == "Basement"

    def test_get_room_number_display_values(self):
        """Test Russian display values for room number field."""
        result = self.service.get_russian_display_value("room_number", "101")
        assert result == "101"

        result = self.service.get_russian_display_value("room_number", "A12B")
        assert result == "A12B"

        result = self.service.get_russian_display_value("room_number", "Suite 100")
        assert result == "Suite 100"

    def test_get_display_value_unknown_field_returns_string(self):
        """Test display value for unknown field returns string representation."""
        result = self.service.get_russian_display_value("unknown", "test_value")
        assert result == "test_value"


class TestFieldTypeValidation:
    """Test field type validation helpers."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_is_text_field(self):
        """Test text field identification."""
        text_fields = [
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

        for field in text_fields:
            assert self.service._is_text_field(field)

        assert not self.service._is_text_field("gender")
        assert not self.service._is_text_field("payment_amount")
        assert not self.service._is_text_field("floor")  # Floor is a special field
        assert not self.service._is_text_field(
            "room_number"
        )  # Room number is a special field

    def test_is_button_field(self):
        """Test button field identification."""
        button_fields = ["gender", "size", "role", "department", "payment_status"]

        for field in button_fields:
            assert self.service._is_button_field(field)

        assert not self.service._is_button_field("full_name_ru")
        assert not self.service._is_button_field("payment_amount")

    def test_is_special_field(self):
        """Test special field identification."""
        special_fields = ["payment_amount", "payment_date", "floor", "room_number"]

        for field in special_fields:
            assert self.service._is_special_field(field)

        assert not self.service._is_special_field("full_name_ru")
        assert not self.service._is_special_field("gender")


class TestValidationErrorClass:
    """Test ValidationError exception class."""

    def test_validation_error_creation(self):
        """Test ValidationError can be created with message."""
        error = ValidationError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from Exception."""
        error = ValidationError("Test")
        assert isinstance(error, Exception)

        # Should be catchable as Exception
        try:
            raise ValidationError("Test error")
        except Exception as e:
            assert isinstance(e, ValidationError)
            assert str(e) == "Test error"


class TestPaymentAutomation:
    """Test payment automation logic in field validation."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_validate_payment_amount_returns_integer_for_paid_amount(self):
        """Test that payment amount validation returns integer for paid amounts."""
        # Test payment amount >= 1 returns integer (automation handled separately)
        result = self.service.validate_field_input("payment_amount", "1")

        # Should return just the amount as integer
        assert result == 1
        assert isinstance(result, int)

    def test_validate_payment_amount_returns_integer_for_large_amount(self):
        """Test that large payment amounts also return integer."""
        result = self.service.validate_field_input("payment_amount", "5000")

        assert result == 5000
        assert isinstance(result, int)

    def test_validate_payment_amount_returns_integer_for_zero_amount(self):
        """Test that zero payment amount returns integer."""
        result = self.service.validate_field_input("payment_amount", "0")

        # Should return just the amount as integer
        assert result == 0
        assert isinstance(result, int)

    def test_validate_payment_amount_returns_integer_for_empty_amount(self):
        """Test that empty payment amount returns integer."""
        result = self.service.validate_field_input("payment_amount", "")

        # Should return just the amount (0) as integer
        assert result == 0
        assert isinstance(result, int)

    def test_get_automated_payment_fields_returns_correct_data(self):
        """Test helper method that generates automated payment fields."""
        # This method should exist to generate automation data
        automated_fields = self.service.get_automated_payment_fields(100)

        assert "payment_status" in automated_fields
        assert "payment_date" in automated_fields
        assert automated_fields["payment_status"] == PaymentStatus.PAID
        assert automated_fields["payment_date"] == date.today()

    def test_is_paid_amount_detection(self):
        """Test helper method that detects if an amount qualifies as paid."""
        # This method should exist to determine if amount triggers automation
        assert self.service.is_paid_amount(1) == True
        assert self.service.is_paid_amount(100) == True
        assert self.service.is_paid_amount(5000) == True
        assert self.service.is_paid_amount(0) == False
        assert (
            self.service.is_paid_amount(-1) == False
        )  # Invalid but tested for completeness


class TestRoleDepartmentLogic:
    """Tests for role ↔ department business logic helpers."""

    def setup_method(self):
        self.service = ParticipantUpdateService()

    def test_detect_role_transition(self):
        assert self.service.detect_role_transition(Role.TEAM, Role.TEAM) == "NO_CHANGE"
        assert (
            self.service.detect_role_transition(Role.CANDIDATE, Role.TEAM)
            == "CANDIDATE_TO_TEAM"
        )
        assert (
            self.service.detect_role_transition(Role.TEAM, Role.CANDIDATE)
            == "TEAM_TO_CANDIDATE"
        )
        # None old role treated as no change
        assert self.service.detect_role_transition(None, Role.TEAM) == "NO_CHANGE"

    def test_requires_department(self):
        assert self.service.requires_department(Role.TEAM) is True
        assert self.service.requires_department(Role.CANDIDATE) is False
        assert self.service.requires_department(None) is False

    def test_get_role_department_actions(self):
        actions = self.service.get_role_department_actions(Role.TEAM, Role.CANDIDATE)
        assert actions["clear_department"] is True
        assert actions["prompt_department"] is False

        actions = self.service.get_role_department_actions(Role.CANDIDATE, Role.TEAM)
        assert actions["clear_department"] is False
        assert actions["prompt_department"] is True

    def test_build_auto_action_message(self):
        clear_msg = self.service.build_auto_action_message("clear_department")
        prompt_msg = self.service.build_auto_action_message("prompt_department")
        assert "Департамент" in clear_msg
        assert "Команда" in prompt_msg


class TestTableNameBusinessRule:
    """Test TableName business rule validation."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_validate_table_name_business_rule_candidate_role_valid(self):
        """Test TableName is allowed for CANDIDATE role."""
        # Should not raise any exceptions
        self.service.validate_table_name_business_rule(Role.CANDIDATE, "Main table")
        self.service.validate_table_name_business_rule(Role.CANDIDATE, "VIP стол")

    def test_validate_table_name_business_rule_candidate_role_empty_valid(self):
        """Test empty/None TableName is allowed for CANDIDATE role."""
        # Should not raise any exceptions
        self.service.validate_table_name_business_rule(Role.CANDIDATE, None)
        self.service.validate_table_name_business_rule(Role.CANDIDATE, "")

    def test_validate_table_name_business_rule_team_role_with_table_name_invalid(self):
        """Test TableName is not allowed for TEAM role."""
        with pytest.raises(
            ValidationError, match="доступно только для роли «Кандидат»"
        ):
            self.service.validate_table_name_business_rule(Role.TEAM, "Some table")

        with pytest.raises(
            ValidationError, match="доступно только для роли «Кандидат»"
        ):
            self.service.validate_table_name_business_rule(Role.TEAM, "Основной стол")

    def test_validate_table_name_business_rule_team_role_empty_valid(self):
        """Test empty/None TableName is allowed for TEAM role."""
        # Should not raise any exceptions
        self.service.validate_table_name_business_rule(Role.TEAM, None)
        self.service.validate_table_name_business_rule(Role.TEAM, "")

    def test_validate_table_name_business_rule_none_role_valid(self):
        """Test TableName is allowed when role is None."""
        # Should not raise any exceptions
        self.service.validate_table_name_business_rule(None, "Some table")
        self.service.validate_table_name_business_rule(None, None)


class TestExtendedFieldClassification:
    """Test field type classification includes new extended fields."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()

    def test_extended_fields_are_text_fields(self):
        """Test that extended fields are classified as text fields."""
        extended_text_fields = ["church_leader", "table_name", "notes"]

        for field in extended_text_fields:
            assert self.service._is_text_field(field)

    def test_extended_fields_are_not_button_fields(self):
        """Test that extended fields are not classified as button fields."""
        extended_text_fields = ["church_leader", "table_name", "notes"]

        for field in extended_text_fields:
            assert not self.service._is_button_field(field)

    def test_extended_fields_are_not_special_fields(self):
        """Test that extended fields are not classified as special fields."""
        extended_text_fields = ["church_leader", "table_name", "notes"]

        for field in extended_text_fields:
            assert not self.service._is_special_field(field)
