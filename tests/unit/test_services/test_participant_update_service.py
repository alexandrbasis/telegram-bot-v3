"""
Unit tests for participant update service.

Tests field validation logic, value conversion, and error handling
for all participant field types.
"""

import pytest
from datetime import date

from src.services.participant_update_service import (
    ParticipantUpdateService,
    ValidationError
)
from src.models.participant import Gender, Size, Role, Department, PaymentStatus


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
        result = self.service.validate_field_input('full_name_ru', 'Иван Петров')
        assert result == 'Иван Петров'
        
        result = self.service.validate_field_input('church', 'Церковь Грейс')
        assert result == 'Церковь Грейс'
    
    def test_validate_text_field_empty_optional(self):
        """Test validation of empty optional text field."""
        result = self.service.validate_field_input('full_name_en', '')
        assert result == ''
        
        result = self.service.validate_field_input('church', '   ')
        assert result == ''
    
    def test_validate_text_field_empty_required_raises_error(self):
        """Test validation of empty required field raises ValidationError."""
        with pytest.raises(ValidationError, match="не может быть пустым"):
            self.service.validate_field_input('full_name_ru', '')
        
        with pytest.raises(ValidationError, match="не может быть пустым"):
            self.service.validate_field_input('full_name_ru', '   ')
    
    def test_validate_payment_amount_valid_integer(self):
        """Test validation of valid payment amount."""
        result = self.service.validate_field_input('payment_amount', '1000')
        assert result == 1000
        
        result = self.service.validate_field_input('payment_amount', '0')
        assert result == 0
    
    def test_validate_payment_amount_invalid_input(self):
        """Test validation of invalid payment amount raises error."""
        with pytest.raises(ValidationError, match="должна быть числом"):
            self.service.validate_field_input('payment_amount', 'not_a_number')
        
        with pytest.raises(ValidationError, match="не может быть отрицательной"):
            self.service.validate_field_input('payment_amount', '-100')
    
    def test_validate_payment_date_valid_format(self):
        """Test validation of valid payment date."""
        result = self.service.validate_field_input('payment_date', '2024-01-15')
        assert result == date(2024, 1, 15)
        
        result = self.service.validate_field_input('payment_date', '2023-12-31')
        assert result == date(2023, 12, 31)
    
    def test_validate_payment_date_invalid_format(self):
        """Test validation of invalid date format raises error."""
        with pytest.raises(ValidationError, match="формат даты"):
            self.service.validate_field_input('payment_date', '2024/01/15')
        
        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input('payment_date', '15-01-2024')
        
        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input('payment_date', '2024-13-01')
        
        with pytest.raises(ValidationError, match="екорректная дата"):
            self.service.validate_field_input('payment_date', '2024-02-30')
    
    def test_validate_unknown_field_raises_error(self):
        """Test validation of unknown field raises error."""
        with pytest.raises(ValidationError, match="Неизвестное поле"):
            self.service.validate_field_input('unknown_field', 'value')


class TestConvertButtonValue:
    """Test convert_button_value method."""
    
    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()
    
    def test_convert_gender_values(self):
        """Test conversion of gender button values."""
        result = self.service.convert_button_value('gender', 'M')
        assert result == Gender.MALE
        
        result = self.service.convert_button_value('gender', 'F')
        assert result == Gender.FEMALE
    
    def test_convert_size_values(self):
        """Test conversion of size button values."""
        result = self.service.convert_button_value('size', 'XL')
        assert result == Size.XL
        
        result = self.service.convert_button_value('size', '3XL')
        assert result == Size.XXXL
    
    def test_convert_role_values(self):
        """Test conversion of role button values."""
        result = self.service.convert_button_value('role', 'CANDIDATE')
        assert result == Role.CANDIDATE
        
        result = self.service.convert_button_value('role', 'TEAM')
        assert result == Role.TEAM
    
    def test_convert_department_values(self):
        """Test conversion of department button values."""
        result = self.service.convert_button_value('department', 'Worship')
        assert result == Department.WORSHIP
        
        result = self.service.convert_button_value('department', 'Kitchen')
        assert result == Department.KITCHEN
    
    def test_convert_payment_status_values(self):
        """Test conversion of payment status button values."""
        result = self.service.convert_button_value('payment_status', 'Paid')
        assert result == PaymentStatus.PAID
        
        result = self.service.convert_button_value('payment_status', 'Partial')
        assert result == PaymentStatus.PARTIAL
        
        result = self.service.convert_button_value('payment_status', 'Unpaid')
        assert result == PaymentStatus.UNPAID
    
    def test_convert_invalid_field_raises_error(self):
        """Test conversion of invalid field raises ValueError."""
        with pytest.raises(ValueError, match="not a button field"):
            self.service.convert_button_value('full_name_ru', 'value')
    
    def test_convert_invalid_value_raises_error(self):
        """Test conversion of invalid value raises ValueError."""
        with pytest.raises(ValueError, match="Invalid .* value"):
            self.service.convert_button_value('gender', 'INVALID')
        
        with pytest.raises(ValueError, match="Invalid .* value"):
            self.service.convert_button_value('size', 'HUGE')


class TestGetRussianDisplayValue:
    """Test get_russian_display_value method."""
    
    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()
    
    def test_get_gender_display_values(self):
        """Test Russian display values for gender."""
        result = self.service.get_russian_display_value('gender', Gender.MALE)
        assert result == "Мужской"
        
        result = self.service.get_russian_display_value('gender', Gender.FEMALE)
        assert result == "Женский"
    
    def test_get_role_display_values(self):
        """Test Russian display values for role."""
        result = self.service.get_russian_display_value('role', Role.CANDIDATE)
        assert result == "Кандидат"
        
        result = self.service.get_russian_display_value('role', Role.TEAM)
        assert result == "Команда"
    
    def test_get_payment_status_display_values(self):
        """Test Russian display values for payment status."""
        result = self.service.get_russian_display_value('payment_status', PaymentStatus.PAID)
        assert result == "Оплачено"
        
        result = self.service.get_russian_display_value('payment_status', PaymentStatus.PARTIAL)
        assert result == "Частично"
        
        result = self.service.get_russian_display_value('payment_status', PaymentStatus.UNPAID)
        assert result == "Не оплачено"
    
    def test_get_size_display_values(self):
        """Test display values for size (no translation needed)."""
        result = self.service.get_russian_display_value('size', Size.XL)
        assert result == "XL"
        
        result = self.service.get_russian_display_value('size', Size.XXXL)
        assert result == "3XL"
    
    def test_get_department_display_values(self):
        """Test display values for department (English preserved)."""
        result = self.service.get_russian_display_value('department', Department.WORSHIP)
        assert result == "Worship"
        
        result = self.service.get_russian_display_value('department', Department.KITCHEN)
        assert result == "Kitchen"
    
    def test_get_display_value_unknown_field_returns_string(self):
        """Test display value for unknown field returns string representation."""
        result = self.service.get_russian_display_value('unknown', 'test_value')
        assert result == "test_value"


class TestFieldTypeValidation:
    """Test field type validation helpers."""
    
    def setup_method(self):
        """Set up test instance."""
        self.service = ParticipantUpdateService()
    
    def test_is_text_field(self):
        """Test text field identification."""
        text_fields = ['full_name_ru', 'full_name_en', 'church', 'country_and_city', 
                       'contact_information', 'submitted_by']
        
        for field in text_fields:
            assert self.service._is_text_field(field)
        
        assert not self.service._is_text_field('gender')
        assert not self.service._is_text_field('payment_amount')
    
    def test_is_button_field(self):
        """Test button field identification."""
        button_fields = ['gender', 'size', 'role', 'department', 'payment_status']
        
        for field in button_fields:
            assert self.service._is_button_field(field)
        
        assert not self.service._is_button_field('full_name_ru')
        assert not self.service._is_button_field('payment_amount')
    
    def test_is_special_field(self):
        """Test special field identification."""
        special_fields = ['payment_amount', 'payment_date']
        
        for field in special_fields:
            assert self.service._is_special_field(field)
        
        assert not self.service._is_special_field('full_name_ru')
        assert not self.service._is_special_field('gender')


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