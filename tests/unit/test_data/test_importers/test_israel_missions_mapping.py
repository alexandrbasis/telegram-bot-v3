"""
Tests for Israel Missions 2025 CSV → Airtable mapping functionality.

Tests cover field mapping, data transformation, validation, and edge cases
as specified in the mapping documentation and test plan.
"""

from datetime import datetime
from unittest.mock import patch

import pytest

from src.data.importers.israel_missions_mapping import IsraelMissionsMapping


class TestIsraelMissionsMapping:
    """Test class for Israel Missions mapping constants and helpers."""

    def test_csv_to_airtable_mapping_completeness(self):
        """Test that CSV mapping covers all required fields from spec."""
        expected_mappings = {
            "FullNameRU": "FullNameRU",
            "DateOfBirth": "DateOfBirth",
            "Gender": "Gender",
            "Size": "Size",
            "ContactInformation": "ContactInformation",
            "CountryAndCity": "CountryAndCity",
            "Role": "Role",
        }

        assert IsraelMissionsMapping.CSV_TO_AIRTABLE == expected_mappings

    def test_derived_fields_constants(self):
        """Test that derived field constants match specification."""
        derived = IsraelMissionsMapping.DERIVED_FIELDS

        assert derived["SubmittedBy"] == "Israel Missions 2025 Form"
        assert (
            "Imported on {timestamp} via Israel Missions importer." in derived["Notes"]
        )
        assert derived["EnvironmentTag"] == "missions-2025"

    def test_required_fields_definition(self):
        """Test that required fields match specification."""
        required = IsraelMissionsMapping.REQUIRED_FIELDS
        assert "FullNameRU" in required
        assert "ContactInformation" in required
        assert len(required) == 2


class TestGenderNormalization:
    """Test gender value normalization."""

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            ("Female", "F"),
            ("Male", "M"),
            ("female", "F"),
            ("male", "M"),
            ("FEMALE", "F"),
            ("MALE", "M"),
            ("f", "F"),
            ("m", "M"),
            ("F", "F"),
            ("M", "M"),
        ],
    )
    def test_normalize_gender_valid_values(self, input_value, expected):
        """Test gender normalization for valid values."""
        result = IsraelMissionsMapping.normalize_gender(input_value)
        assert result == expected

    @pytest.mark.parametrize(
        "input_value", ["", "   ", None, "Other", "Unknown", 123, []]
    )
    def test_normalize_gender_invalid_values(self, input_value):
        """Test gender normalization for invalid/empty values."""
        result = IsraelMissionsMapping.normalize_gender(input_value)
        assert result is None


class TestSizeValidation:
    """Test size validation and normalization."""

    @pytest.mark.parametrize(
        "input_value,expected_size",
        [
            ("XS", "XS"),
            ("S", "S"),
            ("M", "M"),
            ("L", "L"),
            ("XL", "XL"),
            ("XXL", "XXL"),
            ("3XL", "3XL"),
            ("xs", "XS"),
            ("s", "S"),
            ("m", "M"),
            ("  L  ", "L"),
        ],
    )
    def test_validate_size_valid_values(self, input_value, expected_size):
        """Test size validation for valid values."""
        is_valid, normalized = IsraelMissionsMapping.validate_size(input_value)
        assert is_valid is True
        assert normalized == expected_size

    @pytest.mark.parametrize(
        "input_value", ["XXXL", "Small", "Large", "Invalid", 123, []]
    )
    def test_validate_size_invalid_values(self, input_value):
        """Test size validation for invalid values."""
        is_valid, normalized = IsraelMissionsMapping.validate_size(input_value)
        assert is_valid is False
        assert normalized is None

    @pytest.mark.parametrize("input_value", [None, "", "   "])
    def test_validate_size_empty_values(self, input_value):
        """Test size validation for empty values (should be valid as optional)."""
        is_valid, normalized = IsraelMissionsMapping.validate_size(input_value)
        assert is_valid is True
        assert normalized is None


class TestRoleNormalization:
    """Test role normalization with default fallback."""

    @pytest.mark.parametrize(
        "input_value,expected",
        [
            ("TEAM", "TEAM"),
            ("CANDIDATE", "CANDIDATE"),
            ("team", "TEAM"),
            ("candidate", "CANDIDATE"),
            ("  TEAM  ", "TEAM"),
            ("Team", "TEAM"),
        ],
    )
    def test_normalize_role_valid_values(self, input_value, expected):
        """Test role normalization for valid values."""
        result = IsraelMissionsMapping.normalize_role(input_value)
        assert result == expected

    @pytest.mark.parametrize(
        "input_value", [None, "", "   ", "Invalid", "Member", 123, []]
    )
    def test_normalize_role_invalid_values_default_fallback(self, input_value):
        """Test role normalization defaults to TEAM for invalid values."""
        result = IsraelMissionsMapping.normalize_role(input_value)
        assert result == "TEAM"


class TestDateOfBirthParsing:
    """Test date of birth parsing from US to European format."""

    @pytest.mark.parametrize(
        "input_date,expected_output",
        [
            ("7/2/1992", "02/07/1992"),
            ("12/25/1985", "25/12/1985"),
            ("1/1/2000", "01/01/2000"),
            ("10/31/1995", "31/10/1995"),
        ],
    )
    def test_parse_date_of_birth_valid_dates(self, input_date, expected_output):
        """Test date parsing for valid US format dates."""
        result = IsraelMissionsMapping.parse_date_of_birth(input_date)
        assert result == expected_output

    @pytest.mark.parametrize(
        "input_date",
        [
            None,
            "",
            "   ",
            "invalid-date",
            "32/13/2000",  # Invalid month/day
            "2000-01-01",  # ISO format
            "01/01",  # Missing year
            123,
            [],
        ],
    )
    def test_parse_date_of_birth_invalid_dates(self, input_date):
        """Test date parsing for invalid dates."""
        result = IsraelMissionsMapping.parse_date_of_birth(input_date)
        assert result is None


class TestContactNormalization:
    """Test contact information normalization and redaction."""

    @pytest.mark.parametrize(
        "contact_info,expected",
        [
            ("+7-495-123-4567", "74951234567"),
            ("8 (495) 123-45-67", "84951234567"),
            ("+1 234 567 8900", "12345678900"),
            ("123-456-7890", "1234567890"),
            ("email@example.com123", "123"),  # Extracts only digits
        ],
    )
    def test_normalize_contact_for_duplicate_detection(self, contact_info, expected):
        """Test contact normalization extracts digits only."""
        result = IsraelMissionsMapping.normalize_contact_for_duplicate_detection(
            contact_info
        )
        assert result == expected

    def test_normalize_contact_empty_input(self):
        """Test contact normalization for empty input."""
        result = IsraelMissionsMapping.normalize_contact_for_duplicate_detection("")
        assert result == ""

    @pytest.mark.parametrize(
        "contact_info,expected_pattern",
        [
            (
                "+7-495-123-4567",
                "+7***********67",
            ),  # 15 chars: first 2 + 11 stars + last 2
            (
                "8 (495) 123-45-67",
                "8 *************67",
            ),  # 17 chars: first 2 + 13 stars + last 2
            ("short", "sh*rt"),  # 5 chars: masking middle
            ("12345", "12*45"),  # Minimum length for partial masking
            (
                "email@domain.com",
                "em************om",
            ),  # 15 chars: first 2 + 12 stars + last 2
        ],
    )
    def test_redact_contact_for_logging(self, contact_info, expected_pattern):
        """Test contact redaction for safe logging."""
        result = IsraelMissionsMapping.redact_contact_for_logging(contact_info)
        assert result == expected_pattern


class TestAirtablePayloadCreation:
    """Test complete Airtable payload creation with transformations."""

    def test_create_airtable_payload_complete_row(self):
        """Test payload creation with all CSV fields present."""
        csv_row = {
            "FullNameRU": "  Иван Петров  ",
            "DateOfBirth": "7/2/1992",
            "Gender": "Male",
            "Size": "l",
            "ContactInformation": "+7-495-123-4567",
            "CountryAndCity": "  Москва, Россия  ",
            "Role": "candidate",
        }

        payload = IsraelMissionsMapping.create_airtable_payload(
            csv_row, timestamp="2025-09-23T10:00:00"
        )

        expected = {
            "FullNameRU": "Иван Петров",
            "DateOfBirth": "02/07/1992",
            "Gender": "M",
            "Size": "L",
            "ContactInformation": "+7-495-123-4567",
            "CountryAndCity": "Москва, Россия",
            "Role": "CANDIDATE",
            "SubmittedBy": "Israel Missions 2025 Form",
            "Notes": "Imported on 2025-09-23T10:00:00 via Israel Missions importer.",
        }

        assert payload == expected

    def test_create_airtable_payload_minimal_row(self):
        """Test payload creation with only required fields."""
        csv_row = {
            "FullNameRU": "Мария Иванова",
            "ContactInformation": "maria@example.com",
        }

        payload = IsraelMissionsMapping.create_airtable_payload(csv_row)

        assert payload["FullNameRU"] == "Мария Иванова"
        assert payload["ContactInformation"] == "maria@example.com"
        assert payload["Role"] == "TEAM"  # Default role
        assert payload["SubmittedBy"] == "Israel Missions 2025 Form"
        assert "Imported on" in payload["Notes"]

    def test_create_airtable_payload_invalid_transformations(self):
        """Test payload creation handles invalid values gracefully."""
        csv_row = {
            "FullNameRU": "Test User",
            "ContactInformation": "test@example.com",
            "DateOfBirth": "invalid-date",  # Should be None
            "Gender": "Other",  # Should be None
            "Size": "HUGE",  # Should be None (invalid)
            "Role": "Leader",  # Should fallback to TEAM
        }

        payload = IsraelMissionsMapping.create_airtable_payload(csv_row)

        assert payload["FullNameRU"] == "Test User"
        assert payload["ContactInformation"] == "test@example.com"
        assert "DateOfBirth" not in payload  # Invalid date not included
        assert "Gender" not in payload  # Invalid gender not included
        assert "Size" not in payload  # Invalid size not included
        assert payload["Role"] == "TEAM"  # Fallback to default


class TestRequiredFieldsValidation:
    """Test required fields validation."""

    def test_validate_required_fields_complete(self):
        """Test validation passes with all required fields."""
        payload = {"FullNameRU": "Test User", "ContactInformation": "test@example.com"}

        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)
        assert is_valid is True
        assert missing == []

    def test_validate_required_fields_missing_name(self):
        """Test validation fails when FullNameRU is missing."""
        payload = {"ContactInformation": "test@example.com"}

        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)
        assert is_valid is False
        assert "FullNameRU" in missing

    def test_validate_required_fields_empty_contact(self):
        """Test validation fails when ContactInformation is empty."""
        payload = {"FullNameRU": "Test User", "ContactInformation": ""}

        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)
        assert is_valid is False
        assert "ContactInformation" in missing

    def test_validate_required_fields_all_missing(self):
        """Test validation fails when all required fields are missing."""
        payload = {}

        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)
        assert is_valid is False
        assert set(missing) == {"FullNameRU", "ContactInformation"}


class TestDuplicateDetection:
    """Test duplicate detection key generation."""

    def test_get_duplicate_detection_keys_complete(self):
        """Test duplicate key generation with complete data."""
        payload = {
            "FullNameRU": "Иван Петров",
            "DateOfBirth": "02/07/1992",
            "ContactInformation": "+7-495-123-4567",
        }

        contact_key, name_dob_key = IsraelMissionsMapping.get_duplicate_detection_keys(
            payload
        )

        assert contact_key == "74951234567"  # Normalized phone
        assert name_dob_key == "иван петров|02/07/1992"  # Lowercased name + DOB

    def test_get_duplicate_detection_keys_missing_dob(self):
        """Test duplicate key generation when DOB is missing."""
        payload = {
            "FullNameRU": "Мария Иванова",
            "ContactInformation": "maria@example.com",
        }

        contact_key, name_dob_key = IsraelMissionsMapping.get_duplicate_detection_keys(
            payload
        )

        assert contact_key == ""  # Email has no digits
        assert name_dob_key == "мария иванова"  # Name only when DOB missing

    def test_get_duplicate_detection_keys_empty_payload(self):
        """Test duplicate key generation with empty payload."""
        payload = {}

        contact_key, name_dob_key = IsraelMissionsMapping.get_duplicate_detection_keys(
            payload
        )

        assert contact_key == ""
        assert name_dob_key == ""


class TestFieldIdTranslation:
    """Test field ID translation for Airtable API calls."""

    def test_translate_to_field_ids(self):
        """Test that field name to ID translation works."""
        payload = {
            "FullNameRU": "Test User",
            "ContactInformation": "test@example.com",
            "Gender": "M",
        }

        # This should call the AirtableFieldMapping.translate_fields_to_ids method
        result = IsraelMissionsMapping.translate_to_field_ids(payload)

        # Should return dictionary with field IDs as keys
        assert isinstance(result, dict)
        # The exact IDs depend on AirtableFieldMapping configuration
        # We're testing that the method call works, not the specific mappings


class TestIntegrationScenarios:
    """Integration tests for end-to-end mapping scenarios."""

    def test_complete_import_workflow(self):
        """Test complete workflow from CSV row to validated Airtable payload."""
        csv_row = {
            "FullNameRU": "  Александр Сидоров  ",
            "DateOfBirth": "12/25/1988",
            "Gender": "MALE",
            "Size": "xl",
            "ContactInformation": "+7 (495) 987-65-43",
            "CountryAndCity": "Санкт-Петербург, Россия",
            "Role": "TEAM",
        }

        # Step 1: Create payload
        payload = IsraelMissionsMapping.create_airtable_payload(csv_row)

        # Step 2: Validate required fields
        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)
        assert is_valid is True

        # Step 3: Generate duplicate detection keys
        contact_key, name_key = IsraelMissionsMapping.get_duplicate_detection_keys(
            payload
        )
        assert contact_key == "74959876543"
        assert name_key == "александр сидоров|25/12/1988"

        # Step 4: Translate to field IDs
        field_id_payload = IsraelMissionsMapping.translate_to_field_ids(payload)
        assert isinstance(field_id_payload, dict)

        # Verify transformations were applied correctly
        assert payload["FullNameRU"] == "Александр Сидоров"  # Trimmed
        assert payload["DateOfBirth"] == "25/12/1988"  # US → EU format
        assert payload["Gender"] == "M"  # Male → M
        assert payload["Size"] == "XL"  # xl → XL
        assert payload["Role"] == "TEAM"  # Uppercase
        assert "Imported on" in payload["Notes"]  # Audit note added

    def test_edge_case_handling(self):
        """Test handling of edge cases and boundary conditions."""
        csv_row = {
            "FullNameRU": "",  # Empty required field
            "ContactInformation": "   ",  # Whitespace-only contact
            "Gender": "Other",  # Invalid gender
            "Size": "XXXL",  # Invalid size
            "Role": None,  # None role
        }

        payload = IsraelMissionsMapping.create_airtable_payload(csv_row)
        is_valid, missing = IsraelMissionsMapping.validate_required_fields(payload)

        # Should fail validation due to empty required fields
        assert is_valid is False
        assert "FullNameRU" in missing
        assert "ContactInformation" in missing

        # Invalid values should be handled gracefully
        assert "Gender" not in payload  # Invalid gender excluded
        assert "Size" not in payload  # Invalid size excluded
        assert payload["Role"] == "TEAM"  # Default role applied
