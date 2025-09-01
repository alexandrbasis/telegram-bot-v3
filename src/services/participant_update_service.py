"""
Participant field update service with validation.

Provides validation logic for all participant field types including text,
numeric, date, and enum fields with Russian error messages.
"""

import logging
from datetime import date
from typing import Any, Union

from src.models.participant import Gender, Size, Role, Department, PaymentStatus

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Custom exception for field validation errors."""
    pass


class ParticipantUpdateService:
    """
    Service for validating and converting participant field updates.
    
    Handles validation for all 13 participant fields with appropriate
    type conversion and Russian error messages.
    """
    
    # Field type classifications
    TEXT_FIELDS = [
        'full_name_ru', 'full_name_en', 'church', 'country_and_city',
        'contact_information', 'submitted_by'
    ]
    
    BUTTON_FIELDS = ['gender', 'size', 'role', 'department', 'payment_status']
    
    SPECIAL_FIELDS = ['payment_amount', 'payment_date']
    
    # Required fields that cannot be empty
    REQUIRED_FIELDS = ['full_name_ru']
    
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
        # Trim whitespace
        user_input = user_input.strip()
        
        if field_name in self.TEXT_FIELDS:
            return self._validate_text_field(field_name, user_input)
        
        elif field_name == 'payment_amount':
            return self._validate_payment_amount(user_input)
        
        elif field_name == 'payment_date':
            return self._validate_payment_date(user_input)
        
        else:
            raise ValidationError(f"Неизвестное поле для валидации: {field_name}")
    
    def _validate_text_field(self, field_name: str, user_input: str) -> str:
        """Validate text field input."""
        if not user_input and field_name in self.REQUIRED_FIELDS:
            raise ValidationError(f"Поле '{self._get_field_label(field_name)}' не может быть пустым")
        
        return user_input
    
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
            year, month, day = user_input.split('-')
            parsed_date = date(int(year), int(month), int(day))
            return parsed_date
        except ValueError as e:
            if "invalid literal" in str(e) or len(user_input.split('-')) != 3:
                raise ValidationError("Неверный формат даты. Используйте ГГГГ-ММ-ДД (например: 2024-01-15)")
            else:
                raise ValidationError("Некорректная дата. Проверьте день и месяц.")
        except Exception:
            raise ValidationError("Неверный формат даты. Используйте ГГГГ-ММ-ДД")
    
    def convert_button_value(self, field_name: str, selected_value: str) -> Union[Gender, Size, Role, Department, PaymentStatus]:
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
            if field_name == 'gender':
                return Gender(selected_value)
            
            elif field_name == 'size':
                return Size(selected_value)
            
            elif field_name == 'role':
                return Role(selected_value)
            
            elif field_name == 'department':
                return Department(selected_value)
            
            elif field_name == 'payment_status':
                return PaymentStatus(selected_value)
            
        except ValueError:
            raise ValueError(f"Invalid {field_name} value: {selected_value}")
    
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
        if field_name == 'gender':
            if field_value == Gender.MALE:
                return "Мужской"
            elif field_value == Gender.FEMALE:
                return "Женский"
        
        # Role translations
        elif field_name == 'role':
            if field_value == Role.CANDIDATE:
                return "Кандидат"
            elif field_value == Role.TEAM:
                return "Команда"
        
        # Payment status translations
        elif field_name == 'payment_status':
            if field_value == PaymentStatus.PAID:
                return "Оплачено"
            elif field_value == PaymentStatus.PARTIAL:
                return "Частично"
            elif field_value == PaymentStatus.UNPAID:
                return "Не оплачено"
        
        # For other fields (size, department), return the string value
        if hasattr(field_value, 'value'):
            return field_value.value
        
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
        return {
            'payment_status': PaymentStatus.PAID,
            'payment_date': date.today()
        }
    
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
            'full_name_ru': 'Имя на русском',
            'full_name_en': 'Имя на английском',
            'church': 'Церковь',
            'country_and_city': 'Местоположение',
            'contact_information': 'Контакты',
            'submitted_by': 'Отправитель',
            'gender': 'Пол',
            'size': 'Размер',
            'role': 'Роль',
            'department': 'Отдел',
            'payment_status': 'Статус платежа',
            'payment_amount': 'Сумма платежа',
            'payment_date': 'Дата платежа'
        }
        return field_labels.get(field_name, field_name)