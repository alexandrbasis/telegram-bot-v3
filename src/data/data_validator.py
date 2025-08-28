"""
Data validation service for Airtable field constraints.

This module provides comprehensive validation for participant data before
database operations, ensuring data integrity and preventing API errors.
"""

from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import date
import logging
import re

from src.models.participant import Participant
from src.config.field_mappings import AirtableFieldMapping, field_mapping
from src.data.repositories.participant_repository import ValidationError

logger = logging.getLogger(__name__)


class ValidationResult:
    """
    Result of data validation operation.
    
    Contains validation status, error messages, and field-specific errors.
    """
    
    def __init__(self, is_valid: bool = True):
        self.is_valid = is_valid
        self.errors: List[str] = []
        self.field_errors: Dict[str, List[str]] = {}
        self.warnings: List[str] = []
    
    def add_error(self, message: str, field: Optional[str] = None) -> None:
        """
        Add validation error.
        
        Args:
            message: Error message
            field: Field name if error is field-specific
        """
        self.is_valid = False
        self.errors.append(message)
        
        if field:
            if field not in self.field_errors:
                self.field_errors[field] = []
            self.field_errors[field].append(message)
    
    def add_warning(self, message: str) -> None:
        """
        Add validation warning.
        
        Args:
            message: Warning message
        """
        self.warnings.append(message)
    
    def get_error_summary(self) -> str:
        """
        Get summary of all validation errors.
        
        Returns:
            Formatted string of all errors
        """
        if not self.errors:
            return "No validation errors"
        
        if len(self.errors) == 1:
            return self.errors[0]
        
        return f"Multiple validation errors: {'; '.join(self.errors)}"
    
    def get_field_errors(self, field: str) -> List[str]:
        """
        Get validation errors for specific field.
        
        Args:
            field: Field name
            
        Returns:
            List of error messages for the field
        """
        return self.field_errors.get(field, [])
    
    def has_field_error(self, field: str) -> bool:
        """
        Check if specific field has validation errors.
        
        Args:
            field: Field name
            
        Returns:
            True if field has errors
        """
        return field in self.field_errors
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert validation result to dictionary.
        
        Returns:
            Dictionary representation of validation result
        """
        return {
            "is_valid": self.is_valid,
            "errors": self.errors,
            "field_errors": self.field_errors,
            "warnings": self.warnings,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings)
        }


class DataValidator:
    """
    Comprehensive data validator for Airtable participant data.
    
    Validates participant data against Airtable field constraints,
    data types, and business rules before database operations.
    """
    
    def __init__(self, field_mapping_instance: Optional[AirtableFieldMapping] = None):
        """
        Initialize data validator.
        
        Args:
            field_mapping_instance: Field mapping configuration, defaults to global instance
        """
        self.field_mapping = field_mapping_instance or field_mapping
        logger.debug("Initialized DataValidator")
    
    def validate_participant(self, participant: Participant) -> ValidationResult:
        """
        Validate complete participant data.
        
        Args:
            participant: Participant instance to validate
            
        Returns:
            ValidationResult with validation status and errors
        """
        logger.debug(f"Validating participant: {participant.full_name_ru}")
        
        result = ValidationResult()
        
        # Convert to Airtable fields for validation
        try:
            airtable_fields = participant.to_airtable_fields()
        except Exception as e:
            result.add_error(f"Failed to convert participant to Airtable format: {e}")
            return result
        
        # Validate each field
        for airtable_field, value in airtable_fields.items():
            field_result = self.validate_field(airtable_field, value)
            if not field_result.is_valid:
                for error in field_result.errors:
                    result.add_error(error, airtable_field)
            
            for warning in field_result.warnings:
                result.add_warning(warning)
        
        # Business rule validation
        self._validate_business_rules(participant, result)
        
        logger.debug(f"Validation result: {result.is_valid}, errors: {len(result.errors)}")
        return result
    
    def validate_field(self, airtable_field: str, value: Any) -> ValidationResult:
        """
        Validate single field value against constraints.
        
        Args:
            airtable_field: Airtable field name
            value: Field value to validate
            
        Returns:
            ValidationResult for the field
        """
        result = ValidationResult()
        
        # Use field mapping validation
        is_valid, error_message = self.field_mapping.validate_field_value(airtable_field, value)
        if not is_valid:
            result.add_error(error_message, airtable_field)
            return result
        
        # Additional custom validation
        self._validate_custom_constraints(airtable_field, value, result)
        
        return result
    
    def validate_bulk_data(self, participants: List[Participant]) -> Dict[int, ValidationResult]:
        """
        Validate multiple participants in bulk.
        
        Args:
            participants: List of participants to validate
            
        Returns:
            Dictionary mapping index to validation result for each participant
        """
        logger.debug(f"Bulk validating {len(participants)} participants")
        
        results = {}
        for i, participant in enumerate(participants):
            results[i] = self.validate_participant(participant)
        
        valid_count = sum(1 for result in results.values() if result.is_valid)
        logger.debug(f"Bulk validation complete: {valid_count}/{len(participants)} valid")
        
        return results
    
    def validate_partial_update(self, fields: Dict[str, Any]) -> ValidationResult:
        """
        Validate partial field updates.
        
        Args:
            fields: Dictionary of Airtable field names and values to validate
            
        Returns:
            ValidationResult for the update fields
        """
        logger.debug(f"Validating partial update: {list(fields.keys())}")
        
        result = ValidationResult()
        
        for airtable_field, value in fields.items():
            field_result = self.validate_field(airtable_field, value)
            if not field_result.is_valid:
                for error in field_result.errors:
                    result.add_error(error, airtable_field)
        
        return result
    
    def validate_search_criteria(self, criteria: Dict[str, Any]) -> ValidationResult:
        """
        Validate search criteria values.
        
        Args:
            criteria: Search criteria dictionary
            
        Returns:
            ValidationResult for search criteria
        """
        from src.config.field_mappings import SearchFieldMapping
        
        result = ValidationResult()
        
        for criteria_field, value in criteria.items():
            # Check if field is searchable
            airtable_field = SearchFieldMapping.get_search_field_name(criteria_field)
            if not airtable_field:
                result.add_error(f"Field '{criteria_field}' is not searchable")
                continue
            
            # Validate the value
            field_result = self.validate_field(airtable_field, value)
            if not field_result.is_valid:
                for error in field_result.errors:
                    result.add_error(f"Search criteria '{criteria_field}': {error}")
        
        return result
    
    def _validate_business_rules(self, participant: Participant, result: ValidationResult) -> None:
        """
        Validate business-specific rules and constraints.
        
        Args:
            participant: Participant to validate
            result: ValidationResult to add errors to
        """
        # Rule 1: Payment amount should be provided if payment status is not "Unpaid"
        if participant.payment_status and participant.payment_status != "Unpaid":
            if participant.payment_amount is None or participant.payment_amount <= 0:
                result.add_warning(
                    f"Payment amount should be specified when payment status is '{participant.payment_status}'"
                )
        
        # Rule 2: Payment date should be provided if payment amount is specified
        if participant.payment_amount and participant.payment_amount > 0:
            if participant.payment_date is None:
                result.add_warning("Payment date should be specified when payment amount is provided")
        
        # Rule 3: Contact information is strongly recommended
        if not participant.contact_information:
            result.add_warning("Contact information is recommended for participant communication")
        
        # Rule 4: Role-specific validation
        if participant.role:
            if participant.role == "TEAM" and not participant.department:
                result.add_warning("Team members should have a department assignment")
        
        # Rule 5: Name consistency validation
        if participant.full_name_en:
            # Basic check that English name doesn't contain Cyrillic characters
            if re.search(r'[а-яё]', participant.full_name_en.lower()):
                result.add_error("English name should not contain Cyrillic characters", "full_name_en")
        
        # Russian name should contain some Cyrillic characters
        if not re.search(r'[а-яё]', participant.full_name_ru.lower()):
            result.add_warning("Russian name should contain Cyrillic characters")
    
    def _validate_custom_constraints(self, airtable_field: str, value: Any, result: ValidationResult) -> None:
        """
        Apply custom validation constraints beyond basic field mapping.
        
        Args:
            airtable_field: Airtable field name
            value: Field value
            result: ValidationResult to add errors to
        """
        if value is None:
            return
        
        # Contact information validation
        if airtable_field == "ContactInformation" and isinstance(value, str):
            self._validate_contact_information(value, result)
        
        # Payment date validation
        elif airtable_field == "PaymentDate":
            self._validate_payment_date(value, result)
        
        # Church name validation
        elif airtable_field == "Church" and isinstance(value, str):
            self._validate_church_name(value, result)
        
        # Country and city validation
        elif airtable_field == "CountryAndCity" and isinstance(value, str):
            self._validate_location(value, result)
    
    def _validate_contact_information(self, contact_info: str, result: ValidationResult) -> None:
        """
        Validate contact information format.
        
        Args:
            contact_info: Contact information string
            result: ValidationResult to add errors to
        """
        contact_info = contact_info.strip()
        
        # Check if it looks like an email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        # Check if it looks like a phone number
        phone_pattern = r'^[\+]?[1-9][\d\s\-\(\)]{7,15}$'
        
        is_email = re.match(email_pattern, contact_info)
        is_phone = re.match(phone_pattern, contact_info)
        
        if not is_email and not is_phone and len(contact_info) > 5:
            result.add_warning("Contact information should be a valid email or phone number")
    
    def _validate_payment_date(self, payment_date: Union[str, date], result: ValidationResult) -> None:
        """
        Validate payment date constraints.
        
        Args:
            payment_date: Payment date value
            result: ValidationResult to add errors to
        """
        if isinstance(payment_date, str):
            try:
                payment_date = date.fromisoformat(payment_date)
            except ValueError:
                result.add_error("Payment date must be in YYYY-MM-DD format", "PaymentDate")
                return
        
        if isinstance(payment_date, date):
            today = date.today()
            
            # Payment date shouldn't be in the future
            if payment_date > today:
                result.add_warning("Payment date is in the future")
            
            # Payment date shouldn't be too far in the past (more than 2 years)
            from datetime import timedelta
            two_years_ago = today - timedelta(days=730)
            if payment_date < two_years_ago:
                result.add_warning("Payment date is more than 2 years ago")
    
    def _validate_church_name(self, church: str, result: ValidationResult) -> None:
        """
        Validate church name format.
        
        Args:
            church: Church name
            result: ValidationResult to add errors to
        """
        church = church.strip()
        
        # Check for reasonable length
        if len(church) < 3:
            result.add_warning("Church name seems too short")
        
        # Check if it contains numbers at the start (might be an error)
        if church and church[0].isdigit():
            result.add_warning("Church name starts with a number - please verify")
    
    def _validate_location(self, location: str, result: ValidationResult) -> None:
        """
        Validate country and city information.
        
        Args:
            location: Location string
            result: ValidationResult to add errors to
        """
        location = location.strip()
        
        # Check for reasonable format (should contain some separator or be descriptive)
        if len(location) < 3:
            result.add_warning("Location information seems too short")
        
        # Check if it looks like it might contain both country and city
        separators = [",", "/", "-", "(", ")"]
        has_separator = any(sep in location for sep in separators)
        
        if not has_separator and len(location.split()) < 2:
            result.add_warning("Location should include both country and city information")
    
    def get_validation_summary(self, results: Dict[int, ValidationResult]) -> Dict[str, Any]:
        """
        Generate summary of bulk validation results.
        
        Args:
            results: Dictionary of validation results by index
            
        Returns:
            Summary statistics and information
        """
        total_count = len(results)
        valid_count = sum(1 for result in results.values() if result.is_valid)
        invalid_count = total_count - valid_count
        
        total_errors = sum(len(result.errors) for result in results.values())
        total_warnings = sum(len(result.warnings) for result in results.values())
        
        # Field error frequency
        field_error_counts = {}
        for result in results.values():
            for field, errors in result.field_errors.items():
                field_error_counts[field] = field_error_counts.get(field, 0) + len(errors)
        
        # Most common errors
        error_frequency = {}
        for result in results.values():
            for error in result.errors:
                error_frequency[error] = error_frequency.get(error, 0) + 1
        
        most_common_errors = sorted(error_frequency.items(), key=lambda x: x[1], reverse=True)[:5]
        
        return {
            "total_records": total_count,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "validation_rate": valid_count / total_count if total_count > 0 else 0.0,
            "total_errors": total_errors,
            "total_warnings": total_warnings,
            "field_error_counts": field_error_counts,
            "most_common_errors": most_common_errors,
            "invalid_record_indices": [i for i, result in results.items() if not result.is_valid]
        }


def validate_participant(participant: Participant) -> ValidationResult:
    """
    Convenience function to validate a single participant.
    
    Args:
        participant: Participant instance to validate
        
    Returns:
        ValidationResult with validation status and errors
        
    Raises:
        ValidationError: If validation fails and strict mode is enabled
    """
    validator = DataValidator()
    return validator.validate_participant(participant)


def validate_participant_strict(participant: Participant) -> None:
    """
    Validate participant and raise ValidationError if invalid.
    
    Args:
        participant: Participant instance to validate
        
    Raises:
        ValidationError: If validation fails
    """
    result = validate_participant(participant)
    if not result.is_valid:
        raise ValidationError(f"Participant validation failed: {result.get_error_summary()}")


def validate_field_value(airtable_field: str, value: Any) -> ValidationResult:
    """
    Convenience function to validate a single field value.
    
    Args:
        airtable_field: Airtable field name
        value: Value to validate
        
    Returns:
        ValidationResult for the field
    """
    validator = DataValidator()
    return validator.validate_field(airtable_field, value)


# Global validator instance for convenience
_global_validator: Optional[DataValidator] = None


def get_validator() -> DataValidator:
    """
    Get global validator instance (singleton pattern).
    
    Returns:
        DataValidator instance
    """
    global _global_validator
    if _global_validator is None:
        _global_validator = DataValidator()
    return _global_validator