"""
Unit tests for data validation service.

Tests cover:
- ValidationResult functionality
- Single field validation
- Complete participant validation
- Business rule validation
- Bulk validation operations
- Custom constraint validation
- Search criteria validation
"""

from datetime import date, timedelta
from unittest.mock import Mock, patch

import pytest

from src.data.data_validator import (
    DataValidator,
    ValidationResult,
    get_validator,
    validate_field_value,
    validate_participant,
    validate_participant_strict,
)
from src.data.repositories.participant_repository import ValidationError
from src.models.participant import Department, Gender, Participant, PaymentStatus, Role


class TestValidationResult:
    """Test suite for ValidationResult functionality."""

    def test_initialization_valid(self):
        """Test ValidationResult initialization for valid result."""
        result = ValidationResult(is_valid=True)

        assert result.is_valid is True
        assert result.errors == []
        assert result.field_errors == {}
        assert result.warnings == []

    def test_initialization_invalid(self):
        """Test ValidationResult initialization for invalid result."""
        result = ValidationResult(is_valid=False)

        assert result.is_valid is False
        assert result.errors == []
        assert result.field_errors == {}
        assert result.warnings == []

    def test_add_general_error(self):
        """Test adding general validation error."""
        result = ValidationResult()
        result.add_error("General error message")

        assert result.is_valid is False
        assert "General error message" in result.errors
        assert result.field_errors == {}

    def test_add_field_error(self):
        """Test adding field-specific validation error."""
        result = ValidationResult()
        result.add_error("Field error message", "test_field")

        assert result.is_valid is False
        assert "Field error message" in result.errors
        assert "test_field" in result.field_errors
        assert "Field error message" in result.field_errors["test_field"]

    def test_add_multiple_field_errors(self):
        """Test adding multiple errors to same field."""
        result = ValidationResult()
        result.add_error("Error 1", "test_field")
        result.add_error("Error 2", "test_field")

        assert len(result.field_errors["test_field"]) == 2
        assert "Error 1" in result.field_errors["test_field"]
        assert "Error 2" in result.field_errors["test_field"]

    def test_add_warning(self):
        """Test adding validation warning."""
        result = ValidationResult()
        result.add_warning("Warning message")

        assert result.is_valid is True  # Warnings don't affect validity
        assert "Warning message" in result.warnings

    def test_get_error_summary_no_errors(self):
        """Test error summary with no errors."""
        result = ValidationResult()
        summary = result.get_error_summary()

        assert summary == "No validation errors"

    def test_get_error_summary_single_error(self):
        """Test error summary with single error."""
        result = ValidationResult()
        result.add_error("Single error")
        summary = result.get_error_summary()

        assert summary == "Single error"

    def test_get_error_summary_multiple_errors(self):
        """Test error summary with multiple errors."""
        result = ValidationResult()
        result.add_error("Error 1")
        result.add_error("Error 2")
        summary = result.get_error_summary()

        assert summary.startswith("Multiple validation errors:")
        assert "Error 1" in summary
        assert "Error 2" in summary

    def test_get_field_errors(self):
        """Test getting errors for specific field."""
        result = ValidationResult()
        result.add_error("Field error", "test_field")
        result.add_error("Another error", "other_field")

        field_errors = result.get_field_errors("test_field")
        assert len(field_errors) == 1
        assert "Field error" in field_errors

        missing_errors = result.get_field_errors("missing_field")
        assert missing_errors == []

    def test_has_field_error(self):
        """Test checking if field has errors."""
        result = ValidationResult()
        result.add_error("Field error", "test_field")

        assert result.has_field_error("test_field") is True
        assert result.has_field_error("other_field") is False

    def test_to_dict(self):
        """Test converting validation result to dictionary."""
        result = ValidationResult()
        result.add_error("Error message", "test_field")
        result.add_warning("Warning message")

        result_dict = result.to_dict()

        assert result_dict["is_valid"] is False
        assert "Error message" in result_dict["errors"]
        assert "test_field" in result_dict["field_errors"]
        assert "Warning message" in result_dict["warnings"]
        assert result_dict["error_count"] == 1
        assert result_dict["warning_count"] == 1


class TestDataValidator:
    """Test suite for DataValidator functionality."""

    @pytest.fixture
    def validator(self):
        """Fixture providing DataValidator instance."""
        return DataValidator()

    @pytest.fixture
    def valid_participant(self):
        """Fixture providing valid participant data."""
        return Participant(
            full_name_ru="Иван Иванов",
            full_name_en="Ivan Ivanov",
            contact_information="ivan@example.com",
            role=Role.CANDIDATE,
            department=Department.CHAPEL,
        )

    @pytest.fixture
    def invalid_participant(self):
        """Fixture providing participant with validation errors."""
        # Create with valid data first, then modify to bypass Pydantic validation
        participant = Participant(full_name_ru="Valid Name")

        # Create a mock participant that will produce invalid Airtable data
        mock_participant = Mock(spec=Participant)
        mock_participant.full_name_ru = "Valid Name"
        mock_participant.full_name_en = "Иван Иванов"  # Cyrillic in English name
        mock_participant.contact_information = "invalid-contact"
        mock_participant.payment_amount = 100000  # Exceeds maximum
        mock_participant.payment_date = date(2030, 1, 1)  # Future date
        mock_participant.payment_status = None
        mock_participant.role = None
        mock_participant.department = None

        # Mock the to_airtable_fields method to return invalid data
        mock_participant.to_airtable_fields.return_value = {
            "FullNameRU": "",  # Empty required field
            "FullNameEN": "Иван Иванов",  # Cyrillic in English name
            "ContactInformation": "invalid-contact",
            "PaymentAmount": 100000,  # Exceeds maximum
            "PaymentDate": date(2030, 1, 1),  # Future date
        }

        return mock_participant

    def test_validator_initialization(self):
        """Test DataValidator initialization."""
        validator = DataValidator()
        assert validator.field_mapping is not None

    def test_validator_initialization_custom_mapping(self):
        """Test DataValidator initialization with custom field mapping."""
        mock_mapping = Mock()
        validator = DataValidator(field_mapping_instance=mock_mapping)
        assert validator.field_mapping is mock_mapping

    def test_validate_valid_participant(self, validator, valid_participant):
        """Test validation of valid participant."""
        result = validator.validate_participant(valid_participant)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_invalid_participant(self, validator, invalid_participant):
        """Test validation of invalid participant."""
        result = validator.validate_participant(invalid_participant)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_participant_conversion_error(self, validator):
        """Test validation when participant conversion fails."""
        # Mock participant that raises exception on to_airtable_fields()
        mock_participant = Mock(spec=Participant)
        mock_participant.to_airtable_fields.side_effect = Exception("Conversion failed")
        mock_participant.full_name_ru = "Test"

        result = validator.validate_participant(mock_participant)

        assert result.is_valid is False
        assert len(result.errors) == 1
        assert "Failed to convert" in result.errors[0]

    def test_validate_field_valid(self, validator):
        """Test validation of valid field value."""
        result = validator.validate_field("FullNameRU", "Valid Name")

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_field_invalid(self, validator):
        """Test validation of invalid field value."""
        result = validator.validate_field("FullNameRU", "")

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_bulk_data(
        self, validator, valid_participant, invalid_participant
    ):
        """Test bulk validation of multiple participants."""
        participants = [valid_participant, invalid_participant, valid_participant]

        results = validator.validate_bulk_data(participants)

        assert len(results) == 3
        assert results[0].is_valid is True
        assert results[1].is_valid is False
        assert results[2].is_valid is True

    def test_validate_partial_update_valid(self, validator):
        """Test validation of valid partial update."""
        fields = {"FullNameRU": "Updated Name", "PaymentAmount": 500}

        result = validator.validate_partial_update(fields)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_partial_update_invalid(self, validator):
        """Test validation of invalid partial update."""
        fields = {"FullNameRU": "", "PaymentAmount": -100}

        result = validator.validate_partial_update(fields)

        assert result.is_valid is False
        assert len(result.errors) > 0

    def test_validate_search_criteria_valid(self, validator):
        """Test validation of valid search criteria."""
        criteria = {"full_name_ru": "Ivan", "role": "CANDIDATE"}

        result = validator.validate_search_criteria(criteria)

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_search_criteria_invalid_field(self, validator):
        """Test validation of search criteria with invalid field."""
        criteria = {"non_searchable_field": "value"}

        result = validator.validate_search_criteria(criteria)

        assert result.is_valid is False
        assert "not searchable" in result.errors[0]

    def test_validate_search_criteria_invalid_value(self, validator):
        """Test validation of search criteria with invalid value."""
        criteria = {"role": "INVALID_ROLE"}

        result = validator.validate_search_criteria(criteria)

        assert result.is_valid is False
        assert len(result.errors) > 0


class TestBusinessRules:
    """Test suite for business rule validation."""

    @pytest.fixture
    def validator(self):
        """Fixture providing DataValidator instance."""
        return DataValidator()

    def test_payment_amount_without_status(self, validator):
        """Test warning when payment amount provided without status."""
        participant = Participant(
            full_name_ru="Test User",
            payment_amount=500,
            # No payment_status set
        )

        result = validator.validate_participant(participant)

        # Should be valid but with warning
        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any(
            "payment date should be specified" in w.lower() for w in result.warnings
        )

    def test_payment_status_without_amount(self, validator):
        """Test warning when payment status is not Unpaid but no amount."""
        participant = Participant(
            full_name_ru="Test User",
            payment_status=PaymentStatus.PAID,
            # No payment_amount set
        )

        result = validator.validate_participant(participant)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any(
            "payment amount should be specified" in w.lower() for w in result.warnings
        )

    def test_team_role_without_department(self, validator):
        """Test warning when team member has no department."""
        participant = Participant(
            full_name_ru="Test User",
            role=Role.TEAM,
            # No department set
        )

        result = validator.validate_participant(participant)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("should have a department" in w.lower() for w in result.warnings)

    def test_missing_contact_information(self, validator):
        """Test warning when contact information is missing."""
        participant = Participant(
            full_name_ru="Test User"
            # No contact_information set
        )

        result = validator.validate_participant(participant)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any(
            "contact information is recommended" in w.lower() for w in result.warnings
        )

    def test_cyrillic_in_english_name(self, validator):
        """Test error when English name contains Cyrillic characters."""
        participant = Participant(
            full_name_ru="Иван Иванов",
            full_name_en="Ivan Иванов",  # Mixed Cyrillic and Latin
        )

        result = validator.validate_participant(participant)

        assert result.is_valid is False
        assert any("should not contain cyrillic" in e.lower() for e in result.errors)

    def test_no_cyrillic_in_russian_name(self, validator):
        """Test warning when Russian name has no Cyrillic characters."""
        participant = Participant(full_name_ru="John Smith")  # Latin only

        result = validator.validate_participant(participant)

        assert result.is_valid is True
        assert len(result.warnings) > 0
        assert any("should contain cyrillic" in w.lower() for w in result.warnings)


class TestCustomConstraints:
    """Test suite for custom constraint validation."""

    @pytest.fixture
    def validator(self):
        """Fixture providing DataValidator instance."""
        return DataValidator()

    def test_validate_email_contact(self, validator):
        """Test validation of email contact information."""
        result = validator.validate_field("ContactInformation", "user@example.com")

        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_validate_phone_contact(self, validator):
        """Test validation of phone contact information."""
        result = validator.validate_field("ContactInformation", "+1234567890")

        assert result.is_valid is True
        assert len(result.warnings) == 0

    def test_validate_invalid_contact(self, validator):
        """Test validation of invalid contact information."""
        result = validator.validate_field("ContactInformation", "not-valid-contact")

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any(
            "should be a valid email or phone" in w.lower() for w in result.warnings
        )

    def test_validate_future_payment_date(self, validator):
        """Test validation of future payment date."""
        future_date = date.today() + timedelta(days=30)
        result = validator.validate_field("PaymentDate", future_date)

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("in the future" in w.lower() for w in result.warnings)

    def test_validate_old_payment_date(self, validator):
        """Test validation of very old payment date."""
        old_date = date.today() - timedelta(days=800)  # More than 2 years
        result = validator.validate_field("PaymentDate", old_date)

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("more than 2 years ago" in w.lower() for w in result.warnings)

    def test_validate_invalid_date_string(self, validator):
        """Test validation of invalid date string."""
        result = validator.validate_field("PaymentDate", "invalid-date")

        assert result.is_valid is False
        assert len(result.errors) > 0
        assert any("yyyy-mm-dd format" in e.lower() for e in result.errors)

    def test_validate_short_church_name(self, validator):
        """Test validation of short church name."""
        result = validator.validate_field("Church", "St")

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("seems too short" in w.lower() for w in result.warnings)

    def test_validate_church_name_starts_with_number(self, validator):
        """Test validation of church name starting with number."""
        result = validator.validate_field("Church", "1st Baptist Church")

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("starts with a number" in w.lower() for w in result.warnings)

    def test_validate_short_location(self, validator):
        """Test validation of short location."""
        result = validator.validate_field("CountryAndCity", "NY")

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any("seems too short" in w.lower() for w in result.warnings)

    def test_validate_location_without_separator(self, validator):
        """Test validation of location without separator."""
        result = validator.validate_field("CountryAndCity", "Moscow")

        assert result.is_valid is True  # Warning, not error
        assert len(result.warnings) > 0
        assert any(
            "should include both country and city" in w.lower() for w in result.warnings
        )


class TestValidationSummary:
    """Test suite for validation summary functionality."""

    @pytest.fixture
    def validator(self):
        """Fixture providing DataValidator instance."""
        return DataValidator()

    def test_get_validation_summary(self, validator):
        """Test getting validation summary for bulk results."""
        # Create mock results
        result1 = ValidationResult(is_valid=True)
        result1.add_warning("Warning 1")

        result2 = ValidationResult(is_valid=False)
        result2.add_error("Error 1", "field1")
        result2.add_error("Error 2", "field2")

        result3 = ValidationResult(is_valid=True)

        results = {0: result1, 1: result2, 2: result3}

        summary = validator.get_validation_summary(results)

        assert summary["total_records"] == 3
        assert summary["valid_records"] == 2
        assert summary["invalid_records"] == 1
        assert summary["validation_rate"] == 2 / 3
        assert summary["total_errors"] == 2
        assert summary["total_warnings"] == 1
        assert summary["invalid_record_indices"] == [1]
        assert "field1" in summary["field_error_counts"]
        assert "field2" in summary["field_error_counts"]

    def test_get_validation_summary_empty(self, validator):
        """Test validation summary with empty results."""
        results = {}

        summary = validator.get_validation_summary(results)

        assert summary["total_records"] == 0
        assert summary["valid_records"] == 0
        assert summary["invalid_records"] == 0
        assert summary["validation_rate"] == 0.0


class TestConvenienceFunctions:
    """Test suite for convenience functions."""

    def test_validate_participant_function(self):
        """Test validate_participant convenience function."""
        participant = Participant(full_name_ru="Test User")

        result = validate_participant(participant)

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_validate_participant_strict_valid(self):
        """Test validate_participant_strict with valid data."""
        participant = Participant(full_name_ru="Test User")

        # Should not raise exception
        validate_participant_strict(participant)

    def test_validate_participant_strict_invalid(self):
        """Test validate_participant_strict with invalid data."""
        # Create a mock participant that produces invalid Airtable data
        mock_participant = Mock(spec=Participant)
        mock_participant.full_name_ru = "Valid Name"
        # Set all attributes that business rules might access
        mock_participant.payment_status = None
        mock_participant.payment_amount = None
        mock_participant.payment_date = None
        mock_participant.role = None
        mock_participant.contact_information = None
        mock_participant.department = None
        mock_participant.full_name_en = None
        mock_participant.to_airtable_fields.return_value = {
            "FullNameRU": "",  # Empty required field - will cause validation error
        }

        with pytest.raises(ValidationError) as exc_info:
            validate_participant_strict(mock_participant)

        assert "validation failed" in str(exc_info.value).lower()

    def test_validate_field_value_function(self):
        """Test validate_field_value convenience function."""
        result = validate_field_value("FullNameRU", "Valid Name")

        assert isinstance(result, ValidationResult)
        assert result.is_valid is True

    def test_get_validator_singleton(self):
        """Test get_validator singleton function."""
        validator1 = get_validator()
        validator2 = get_validator()

        assert validator1 is validator2
        assert isinstance(validator1, DataValidator)


class TestEdgeCases:
    """Test suite for edge cases and error conditions."""

    @pytest.fixture
    def validator(self):
        """Fixture providing DataValidator instance."""
        return DataValidator()

    def test_validate_none_values(self, validator):
        """Test validation with None values."""
        result = validator.validate_field("FullNameEN", None)  # Optional field

        assert result.is_valid is True

    def test_validate_empty_bulk_data(self, validator):
        """Test bulk validation with empty list."""
        results = validator.validate_bulk_data([])

        assert len(results) == 0

    def test_validate_empty_partial_update(self, validator):
        """Test partial update validation with empty fields."""
        result = validator.validate_partial_update({})

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_validate_empty_search_criteria(self, validator):
        """Test search criteria validation with empty criteria."""
        result = validator.validate_search_criteria({})

        assert result.is_valid is True
        assert len(result.errors) == 0

    def test_custom_validation_with_none(self, validator):
        """Test custom validation methods with None values."""
        result = ValidationResult()

        # Should not crash or add errors for None values
        validator._validate_custom_constraints("ContactInformation", None, result)
        validator._validate_custom_constraints("PaymentDate", None, result)
        validator._validate_custom_constraints("Church", None, result)

        assert result.is_valid is True
