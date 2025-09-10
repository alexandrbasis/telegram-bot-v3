"""
Unit tests for field mapping configuration.

Tests cover:
- Bidirectional field name mapping (Python <-> Airtable)
- Field type validation and constraints
- Select field options validation
- Search criteria mapping
- Field validation logic
"""

from datetime import date

import pytest

from src.config.field_mappings import (
    AirtableFieldMapping,
    FieldType,
    SearchFieldMapping,
    field_mapping,
    search_mapping,
)
from src.models.participant import Department, Gender, PaymentStatus, Role, Size


class TestAirtableFieldMapping:
    """Test suite for AirtableFieldMapping functionality."""

    def test_python_to_airtable_mapping(self):
        """Test Python field name to Airtable field name mapping."""
        # Test basic field mappings
        assert (
            AirtableFieldMapping.get_airtable_field_name("full_name_ru") == "FullNameRU"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("full_name_en") == "FullNameEN"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("contact_information")
            == "ContactInformation"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("payment_date")
            == "PaymentDate"
        )
        assert AirtableFieldMapping.get_airtable_field_name("record_id") == "id"
        
        # Test new fields
        assert (
            AirtableFieldMapping.get_airtable_field_name("date_of_birth") == "DateOfBirth"
        )
        assert AirtableFieldMapping.get_airtable_field_name("age") == "Age"

        # Test non-existent field
        assert AirtableFieldMapping.get_airtable_field_name("non_existent") is None

    def test_airtable_to_python_mapping(self):
        """Test Airtable field name to Python field name mapping."""
        # Test reverse mappings
        assert (
            AirtableFieldMapping.get_python_field_name("FullNameRU") == "full_name_ru"
        )
        assert (
            AirtableFieldMapping.get_python_field_name("FullNameEN") == "full_name_en"
        )
        assert (
            AirtableFieldMapping.get_python_field_name("ContactInformation")
            == "contact_information"
        )
        assert (
            AirtableFieldMapping.get_python_field_name("PaymentDate") == "payment_date"
        )
        assert AirtableFieldMapping.get_python_field_name("id") == "record_id"
        
        # Test new fields reverse mappings
        assert (
            AirtableFieldMapping.get_python_field_name("DateOfBirth") == "date_of_birth"
        )
        assert AirtableFieldMapping.get_python_field_name("Age") == "age"

        # Test non-existent field
        assert AirtableFieldMapping.get_python_field_name("NonExistent") is None

    def test_field_type_mapping(self):
        """Test field type definitions for validation."""
        # Test text fields
        assert AirtableFieldMapping.get_field_type("FullNameRU") == FieldType.TEXT
        assert AirtableFieldMapping.get_field_type("Church") == FieldType.TEXT

        # Test single select fields
        assert AirtableFieldMapping.get_field_type("Role") == FieldType.SINGLE_SELECT
        assert (
            AirtableFieldMapping.get_field_type("Department") == FieldType.SINGLE_SELECT
        )
        assert AirtableFieldMapping.get_field_type("Gender") == FieldType.SINGLE_SELECT

        # Test number fields
        assert AirtableFieldMapping.get_field_type("PaymentAmount") == FieldType.NUMBER

        # Test date fields
        assert AirtableFieldMapping.get_field_type("PaymentDate") == FieldType.DATE
        assert AirtableFieldMapping.get_field_type("DateOfBirth") == FieldType.DATE
        
        # Test age field (number type)
        assert AirtableFieldMapping.get_field_type("Age") == FieldType.NUMBER

        # Test non-existent field
        assert AirtableFieldMapping.get_field_type("NonExistent") is None

    def test_required_fields(self):
        """Test required field identification."""
        assert AirtableFieldMapping.is_required_field("FullNameRU") is True
        assert AirtableFieldMapping.is_required_field("FullNameEN") is False
        assert AirtableFieldMapping.is_required_field("PaymentAmount") is False
        assert AirtableFieldMapping.is_required_field("NonExistent") is False

    def test_field_constraints(self):
        """Test field constraint definitions."""
        # Test primary field constraints
        constraints = AirtableFieldMapping.get_field_constraints("FullNameRU")
        assert constraints["min_length"] == 1
        assert constraints["max_length"] == 100
        assert constraints["required"] is True

        # Test payment amount constraints
        constraints = AirtableFieldMapping.get_field_constraints("PaymentAmount")
        assert constraints["min_value"] == 0
        assert constraints["max_value"] == 99999

        # Test optional text field constraints
        constraints = AirtableFieldMapping.get_field_constraints("Church")
        assert constraints["max_length"] == 100
        assert "required" not in constraints or not constraints["required"]

        # Test new field constraints
        date_constraints = AirtableFieldMapping.get_field_constraints("DateOfBirth")
        assert "description" in date_constraints
        assert "Participant's date of birth" in date_constraints["description"]
        
        age_constraints = AirtableFieldMapping.get_field_constraints("Age")
        assert age_constraints["min_value"] == 0
        assert age_constraints["max_value"] == 120
        assert "description" in age_constraints

        # Test non-existent field
        constraints = AirtableFieldMapping.get_field_constraints("NonExistent")
        assert constraints == {}

    def test_select_field_options(self):
        """Test single select field option definitions."""
        # Test role options
        role_options = AirtableFieldMapping.get_select_options("Role")
        expected_roles = [role.value for role in Role]
        assert role_options == expected_roles
        assert "CANDIDATE" in role_options
        assert "TEAM" in role_options

        # Test department options
        dept_options = AirtableFieldMapping.get_select_options("Department")
        expected_depts = [dept.value for dept in Department]
        assert dept_options == expected_depts
        assert "Chapel" in dept_options
        assert "Kitchen" in dept_options

        # Test gender options
        gender_options = AirtableFieldMapping.get_select_options("Gender")
        expected_genders = [gender.value for gender in Gender]
        assert gender_options == expected_genders
        assert "M" in gender_options
        assert "F" in gender_options

        # Test non-select field
        options = AirtableFieldMapping.get_select_options("FullNameRU")
        assert options == []

    def test_field_lists(self):
        """Test field list generation."""
        airtable_fields = AirtableFieldMapping.get_all_airtable_fields()
        python_fields = AirtableFieldMapping.get_all_python_fields()

        # Check that we have both directions
        assert len(airtable_fields) == len(python_fields)
        assert "FullNameRU" in airtable_fields
        assert "full_name_ru" in python_fields
        assert "PaymentDate" in airtable_fields
        assert "payment_date" in python_fields

        # Check that all Python fields map to Airtable fields
        for py_field in python_fields:
            assert AirtableFieldMapping.get_airtable_field_name(py_field) is not None


class TestFieldValidation:
    """Test suite for field validation logic."""

    def test_validate_required_field_missing(self):
        """Test validation of missing required field."""
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", None)

        assert is_valid is False
        assert "required" in error.lower()
        assert "FullNameRU" in error

    def test_validate_required_field_present(self):
        """Test validation of present required field."""
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "FullNameRU", "Иван Иванов"
        )

        assert is_valid is True
        assert error == ""

    def test_validate_optional_field_missing(self):
        """Test validation of missing optional field."""
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameEN", None)

        assert is_valid is True
        assert error == ""

    def test_validate_text_field_constraints(self):
        """Test text field length constraints."""
        # Test minimum length
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", "")
        assert is_valid is False
        assert "at least 1 characters" in error

        # Test maximum length
        long_name = "x" * 101  # Exceeds 100 character limit
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "FullNameRU", long_name
        )
        assert is_valid is False
        assert "at most 100 characters" in error

        # Test valid length
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "FullNameRU", "Valid Name"
        )
        assert is_valid is True
        assert error == ""

    def test_validate_number_field_constraints(self):
        """Test number field value constraints."""
        # Test minimum value
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", -1)
        assert is_valid is False
        assert "at least 0" in error

        # Test maximum value
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentAmount", 100000
        )
        assert is_valid is False
        assert "at most 99999" in error

        # Test valid value
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentAmount", 500
        )
        assert is_valid is True
        assert error == ""

        # Test valid float
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentAmount", 500.0
        )
        assert is_valid is True
        assert error == ""

    def test_validate_select_field_options(self):
        """Test single select field option validation."""
        # Test valid option
        is_valid, error = AirtableFieldMapping.validate_field_value("Role", "CANDIDATE")
        assert is_valid is True
        assert error == ""

        # Test invalid option
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "Role", "INVALID_ROLE"
        )
        assert is_valid is False
        assert "must be one of" in error
        assert "CANDIDATE" in error
        assert "TEAM" in error

    def test_validate_date_field(self):
        """Test date field validation."""
        # Test valid date object
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentDate", date(2024, 1, 15)
        )
        assert is_valid is True
        assert error == ""

        # Test valid date string
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentDate", "2024-01-15"
        )
        assert is_valid is True
        assert error == ""

        # Test invalid type
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentDate", 12345
        )
        assert is_valid is False
        assert "must be a date" in error

    def test_validate_new_fields(self):
        """Test validation of new DateOfBirth and Age fields."""
        # Test valid DateOfBirth
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "DateOfBirth", date(1990, 5, 15)
        )
        assert is_valid is True
        assert error == ""

        # Test valid DateOfBirth as string
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "DateOfBirth", "1990-05-15"
        )
        assert is_valid is True
        assert error == ""

        # Test invalid DateOfBirth type
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "DateOfBirth", 12345
        )
        assert is_valid is False
        assert "must be a date" in error

        # Test valid Age
        is_valid, error = AirtableFieldMapping.validate_field_value("Age", 25)
        assert is_valid is True
        assert error == ""

        # Test Age minimum constraint
        is_valid, error = AirtableFieldMapping.validate_field_value("Age", -1)
        assert is_valid is False
        assert "at least 0" in error

        # Test Age maximum constraint
        is_valid, error = AirtableFieldMapping.validate_field_value("Age", 121)
        assert is_valid is False
        assert "at most 120" in error

        # Test Age type validation
        is_valid, error = AirtableFieldMapping.validate_field_value("Age", "twenty-five")
        assert is_valid is False
        assert "must be a number" in error

    def test_validate_type_mismatch(self):
        """Test validation with wrong data types."""
        # Text field with non-string
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", 123)
        assert is_valid is False
        assert "must be a string" in error

        # Number field with string
        is_valid, error = AirtableFieldMapping.validate_field_value(
            "PaymentAmount", "not_a_number"
        )
        assert is_valid is False
        assert "must be a number" in error

        # Select field with non-string
        is_valid, error = AirtableFieldMapping.validate_field_value("Role", 123)
        assert is_valid is False
        assert "must be a string" in error


class TestSearchFieldMapping:
    """Test suite for SearchFieldMapping functionality."""

    def test_search_criteria_mapping(self):
        """Test search criteria to Airtable field mapping."""
        assert SearchFieldMapping.get_search_field_name("full_name_ru") == "FullNameRU"
        assert SearchFieldMapping.get_search_field_name("full_name_en") == "FullNameEN"
        assert SearchFieldMapping.get_search_field_name("role") == "Role"
        assert SearchFieldMapping.get_search_field_name("department") == "Department"
        assert SearchFieldMapping.get_search_field_name("church") == "Church"

        # Test non-searchable field
        assert SearchFieldMapping.get_search_field_name("record_id") is None
        assert SearchFieldMapping.get_search_field_name("payment_amount") is None

    def test_searchable_fields_list(self):
        """Test getting list of searchable fields."""
        searchable_fields = SearchFieldMapping.get_searchable_fields()

        # Check expected searchable fields
        assert "full_name_ru" in searchable_fields
        assert "full_name_en" in searchable_fields
        assert "role" in searchable_fields
        assert "department" in searchable_fields
        assert "church" in searchable_fields
        assert "gender" in searchable_fields

        # Check non-searchable fields are not included
        assert "record_id" not in searchable_fields
        assert "payment_amount" not in searchable_fields
        assert "submitted_by" not in searchable_fields


class TestFieldMappingInstances:
    """Test suite for module-level field mapping instances."""

    def test_field_mapping_instance(self):
        """Test that field_mapping instance works correctly."""
        assert field_mapping.get_airtable_field_name("full_name_ru") == "FullNameRU"
        assert field_mapping.is_required_field("FullNameRU") is True

        is_valid, error = field_mapping.validate_field_value("FullNameRU", "Valid Name")
        assert is_valid is True
        assert error == ""

    def test_search_mapping_instance(self):
        """Test that search_mapping instance works correctly."""
        assert search_mapping.get_search_field_name("role") == "Role"

        searchable_fields = search_mapping.get_searchable_fields()
        assert "full_name_ru" in searchable_fields
        assert len(searchable_fields) > 0


class TestSelectOptionIDs:
    """Test suite for Select Option ID mappings."""

    def test_gender_option_ids(self):
        """Test Gender field Option ID mappings."""
        # RED phase - this test will fail until we implement OPTION_ID_MAPPINGS

        # Test Gender options (2 total)
        assert AirtableFieldMapping.get_option_id("Gender", "M") == "selZClW1ZQ0574g1o"
        assert AirtableFieldMapping.get_option_id("Gender", "F") == "sellCtTlpLKDRs7Uw"

        # Test invalid option
        assert AirtableFieldMapping.get_option_id("Gender", "Invalid") is None

    def test_size_option_ids(self):
        """Test Size field Option ID mappings."""
        # RED phase - this test will fail until we implement OPTION_ID_MAPPINGS

        # Test Size options (7 total)
        assert AirtableFieldMapping.get_option_id("Size", "XS") == "selNuViDUBjuth8lP"
        assert AirtableFieldMapping.get_option_id("Size", "S") == "selKoQLAR5xH9jQvg"
        assert AirtableFieldMapping.get_option_id("Size", "M") == "sel0Ci7MTtsPBtPi0"
        assert AirtableFieldMapping.get_option_id("Size", "L") == "sel5Zd5JF5WD8Y5ab"
        assert AirtableFieldMapping.get_option_id("Size", "XL") == "selmHioiHTrhhmpOO"
        assert AirtableFieldMapping.get_option_id("Size", "XXL") == "selPsyMnT0h7wyOly"
        assert AirtableFieldMapping.get_option_id("Size", "3XL") == "sel1NSFzQbfWVUEuS"

    def test_role_option_ids(self):
        """Test Role field Option ID mappings."""
        # RED phase - this test will fail until we implement OPTION_ID_MAPPINGS

        # Test Role options (2 total)
        assert (
            AirtableFieldMapping.get_option_id("Role", "CANDIDATE")
            == "seleMsONuukNzmB2M"
        )
        assert AirtableFieldMapping.get_option_id("Role", "TEAM") == "selycaljF0Qnq0tdD"

    def test_department_option_ids(self):
        """Test Department field Option ID mappings."""
        # RED phase - this test will fail until we implement OPTION_ID_MAPPINGS

        # Test Department options (13 total)
        assert (
            AirtableFieldMapping.get_option_id("Department", "ROE")
            == "selfaZRN9JukJMcZ5"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Chapel")
            == "sel6IPXCbLoWR5Ugd"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Setup")
            == "selAtROQz5C6CMZMk"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Palanka")
            == "sel1E7vNA7wgVDFLl"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Administration")
            == "selJBiWzoJiFmMlL6"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Kitchen")
            == "selBmfVPB1Jr6jTtQ"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Decoration")
            == "selrCvE3jP1Lxg5z5"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Bell")
            == "selX89NOZuBVjYD07"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Refreshment")
            == "selanq3i2UJWrsmkj"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Worship")
            == "selCKwn2YGIYqQRs8"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Media")
            == "selq5zRZtZ6LXMhN2"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Clergy")
            == "selksIu0oBzHq9Blm"
        )
        assert (
            AirtableFieldMapping.get_option_id("Department", "Rectorate")
            == "seliF8wxKVKpY2za3"
        )

    def test_payment_status_option_ids(self):
        """Test PaymentStatus field Option ID mappings."""
        # RED phase - this test will fail until we implement OPTION_ID_MAPPINGS

        # Test PaymentStatus options (3 total)
        assert (
            AirtableFieldMapping.get_option_id("PaymentStatus", "Paid")
            == "sel4ZcXLVs973Gizi"
        )
        assert (
            AirtableFieldMapping.get_option_id("PaymentStatus", "Partial")
            == "sel1WOFITijjZqaPQ"
        )
        assert (
            AirtableFieldMapping.get_option_id("PaymentStatus", "Unpaid")
            == "selFWmvtAQC7EEB72"
        )

    def test_translate_option_to_id(self):
        """Test translation of option value to Option ID."""
        # RED phase - this test will fail until we implement translation methods

        assert (
            AirtableFieldMapping.translate_option_to_id("Gender", "M")
            == "selZClW1ZQ0574g1o"
        )
        assert (
            AirtableFieldMapping.translate_option_to_id("Size", "L")
            == "sel5Zd5JF5WD8Y5ab"
        )
        assert (
            AirtableFieldMapping.translate_option_to_id("Role", "CANDIDATE")
            == "seleMsONuukNzmB2M"
        )

        # Test fallback for unknown option
        assert (
            AirtableFieldMapping.translate_option_to_id("Gender", "Unknown")
            == "Unknown"
        )

        # Test fallback for non-select field
        assert (
            AirtableFieldMapping.translate_option_to_id("FullNameRU", "Some Name")
            == "Some Name"
        )

    def test_option_id_completeness(self):
        """Test that all select fields have complete Option ID mappings."""
        # RED phase - this test will fail until we implement complete mapping

        # Verify total count: 2 Gender + 7 Size + 2 Role + 13 Department + 3 PaymentStatus = 27 Option IDs
        total_option_ids = 0

        # Count Gender options (2)
        gender_options = AirtableFieldMapping.get_all_option_ids("Gender")
        assert len(gender_options) == 2
        total_option_ids += len(gender_options)

        # Count Size options (7)
        size_options = AirtableFieldMapping.get_all_option_ids("Size")
        assert len(size_options) == 7
        total_option_ids += len(size_options)

        # Count Role options (2)
        role_options = AirtableFieldMapping.get_all_option_ids("Role")
        assert len(role_options) == 2
        total_option_ids += len(role_options)

        # Count Department options (13)
        dept_options = AirtableFieldMapping.get_all_option_ids("Department")
        assert len(dept_options) == 13
        total_option_ids += len(dept_options)

        # Count PaymentStatus options (3)
        payment_options = AirtableFieldMapping.get_all_option_ids("PaymentStatus")
        assert len(payment_options) == 3
        total_option_ids += len(payment_options)

        # Verify total is 27 Option IDs
        assert total_option_ids == 27


class TestAirtableFieldIDs:
    """Test suite for Airtable Field ID mappings."""

    def test_airtable_field_id_mapping(self):
        """Test Field ID mapping for all 13 fields."""
        # RED phase - this test will fail until we implement AIRTABLE_FIELD_IDS

        # Test text fields (6)
        assert AirtableFieldMapping.get_field_id("FullNameRU") == "fldOcpA3JW5MRmR6R"
        assert AirtableFieldMapping.get_field_id("FullNameEN") == "fldrFVukSmk0i9sqj"
        assert AirtableFieldMapping.get_field_id("Church") == "fld4CXL9InW0ogAQh"
        assert (
            AirtableFieldMapping.get_field_id("CountryAndCity") == "fldJ7dFRzx7bR9U6g"
        )
        assert AirtableFieldMapping.get_field_id("SubmittedBy") == "flduADiTl7jpiy8OH"
        assert (
            AirtableFieldMapping.get_field_id("ContactInformation")
            == "fldSy0Hbwl49VtZvf"
        )

        # Test single select fields (5)
        assert AirtableFieldMapping.get_field_id("Gender") == "fldOAGXoU0DqqFRmB"
        assert AirtableFieldMapping.get_field_id("Size") == "fldZyNgaaa1snp6s7"
        assert AirtableFieldMapping.get_field_id("Role") == "fldetbIGOkKFK0hYq"
        assert AirtableFieldMapping.get_field_id("Department") == "fldIh0eyPspgr1TWk"
        assert AirtableFieldMapping.get_field_id("PaymentStatus") == "fldQzc7m7eO0JzRZf"

        # Test number field (1)
        assert AirtableFieldMapping.get_field_id("PaymentAmount") == "fldyP24ZbeGD8nnaZ"

        # Test date field (1)
        assert AirtableFieldMapping.get_field_id("PaymentDate") == "fldylOQLqcBwkmzlh"
        
        # Test new fields (real field IDs from live Airtable)
        assert AirtableFieldMapping.get_field_id("DateOfBirth") == "fld1rN2cffxKuZh4i"
        assert AirtableFieldMapping.get_field_id("Age") == "fldZPh65PIekEbgvs"

        # Test non-existent field
        assert AirtableFieldMapping.get_field_id("NonExistent") is None

    def test_translate_fields_to_ids(self):
        """Test translation of field names to Field IDs."""
        # RED phase - this test will fail until we implement translation methods

        data = {"FullNameRU": "Иван Иванов", "Gender": "M", "PaymentAmount": 500}

        expected = {
            "fldOcpA3JW5MRmR6R": "Иван Иванов",
            "fldOAGXoU0DqqFRmB": "M",
            "fldyP24ZbeGD8nnaZ": 500,
        }

        result = AirtableFieldMapping.translate_fields_to_ids(data)
        assert result == expected

    def test_field_id_completeness(self):
        """Test that all 13 fields have Field ID mappings."""
        # RED phase - this test will fail until we implement complete mapping

        expected_field_ids = {
            "FullNameRU": "fldOcpA3JW5MRmR6R",
            "FullNameEN": "fldrFVukSmk0i9sqj",
            "Church": "fld4CXL9InW0ogAQh",
            "CountryAndCity": "fldJ7dFRzx7bR9U6g",
            "SubmittedBy": "flduADiTl7jpiy8OH",
            "ContactInformation": "fldSy0Hbwl49VtZvf",
            "Gender": "fldOAGXoU0DqqFRmB",
            "Size": "fldZyNgaaa1snp6s7",
            "Role": "fldetbIGOkKFK0hYq",
            "Department": "fldIh0eyPspgr1TWk",
            "PaymentStatus": "fldQzc7m7eO0JzRZf",
            "PaymentAmount": "fldyP24ZbeGD8nnaZ",
            "PaymentDate": "fldylOQLqcBwkmzlh",
        }

        for field_name, expected_id in expected_field_ids.items():
            actual_id = AirtableFieldMapping.get_field_id(field_name)
            assert (
                actual_id == expected_id
            ), f"Field {field_name}: expected {expected_id}, got {actual_id}"


class TestFieldMappingCompleteness:
    """Test suite for field mapping completeness and consistency."""

    def test_mapping_completeness(self):
        """Test that all model fields have proper mappings."""
        # Expected fields based on Participant model
        expected_python_fields = [
            "full_name_ru",
            "full_name_en",
            "church",
            "country_and_city",
            "submitted_by",
            "contact_information",
            "gender",
            "size",
            "role",
            "department",
            "payment_status",
            "payment_amount",
            "payment_date",
            "date_of_birth",
            "age",
            "record_id",
        ]

        python_fields = AirtableFieldMapping.get_all_python_fields()

        for expected_field in expected_python_fields:
            assert (
                expected_field in python_fields
            ), f"Missing Python field: {expected_field}"

    def test_bidirectional_consistency(self):
        """Test that bidirectional mapping is consistent."""
        python_fields = AirtableFieldMapping.get_all_python_fields()

        for py_field in python_fields:
            airtable_field = AirtableFieldMapping.get_airtable_field_name(py_field)
            assert airtable_field is not None

            reverse_py_field = AirtableFieldMapping.get_python_field_name(
                airtable_field
            )
            assert (
                reverse_py_field == py_field
            ), f"Bidirectional mapping inconsistency: {py_field} <-> {airtable_field}"

    def test_enum_option_completeness(self):
        """Test that all enum options are properly mapped."""
        # Test Role enum options
        role_options = AirtableFieldMapping.get_select_options("Role")
        for role in Role:
            assert role.value in role_options

        # Test Department enum options
        dept_options = AirtableFieldMapping.get_select_options("Department")
        for dept in Department:
            assert dept.value in dept_options

        # Test Gender enum options
        gender_options = AirtableFieldMapping.get_select_options("Gender")
        for gender in Gender:
            assert gender.value in gender_options
