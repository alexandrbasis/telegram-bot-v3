"""
Unit tests for field mapping configuration.

Tests cover:
- Bidirectional field name mapping (Python <-> Airtable)
- Field type validation and constraints
- Select field options validation
- Search criteria mapping
- Field validation logic
"""

import pytest
from datetime import date

from src.config.field_mappings import (
    AirtableFieldMapping,
    SearchFieldMapping, 
    FieldType,
    field_mapping,
    search_mapping
)
from src.models.participant import Role, Department, Gender, Size, PaymentStatus


class TestAirtableFieldMapping:
    """Test suite for AirtableFieldMapping functionality."""
    
    def test_python_to_airtable_mapping(self):
        """Test Python field name to Airtable field name mapping."""
        # Test basic field mappings
        assert AirtableFieldMapping.get_airtable_field_name("full_name_ru") == "FullNameRU"
        assert AirtableFieldMapping.get_airtable_field_name("full_name_en") == "FullNameEN"
        assert AirtableFieldMapping.get_airtable_field_name("contact_information") == "ContactInformation"
        assert AirtableFieldMapping.get_airtable_field_name("payment_date") == "PaymentDate"
        assert AirtableFieldMapping.get_airtable_field_name("record_id") == "id"
        
        # Test non-existent field
        assert AirtableFieldMapping.get_airtable_field_name("non_existent") is None
    
    def test_airtable_to_python_mapping(self):
        """Test Airtable field name to Python field name mapping."""
        # Test reverse mappings
        assert AirtableFieldMapping.get_python_field_name("FullNameRU") == "full_name_ru"
        assert AirtableFieldMapping.get_python_field_name("FullNameEN") == "full_name_en"
        assert AirtableFieldMapping.get_python_field_name("ContactInformation") == "contact_information"
        assert AirtableFieldMapping.get_python_field_name("PaymentDate") == "payment_date"
        assert AirtableFieldMapping.get_python_field_name("id") == "record_id"
        
        # Test non-existent field
        assert AirtableFieldMapping.get_python_field_name("NonExistent") is None
    
    def test_field_type_mapping(self):
        """Test field type definitions for validation."""
        # Test text fields
        assert AirtableFieldMapping.get_field_type("FullNameRU") == FieldType.TEXT
        assert AirtableFieldMapping.get_field_type("Church") == FieldType.TEXT
        
        # Test single select fields
        assert AirtableFieldMapping.get_field_type("Role") == FieldType.SINGLE_SELECT
        assert AirtableFieldMapping.get_field_type("Department") == FieldType.SINGLE_SELECT
        assert AirtableFieldMapping.get_field_type("Gender") == FieldType.SINGLE_SELECT
        
        # Test number fields
        assert AirtableFieldMapping.get_field_type("PaymentAmount") == FieldType.NUMBER
        
        # Test date fields
        assert AirtableFieldMapping.get_field_type("PaymentDate") == FieldType.DATE
        
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
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", "Иван Иванов")
        
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
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", long_name)
        assert is_valid is False
        assert "at most 100 characters" in error
        
        # Test valid length
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", "Valid Name")
        assert is_valid is True
        assert error == ""
    
    def test_validate_number_field_constraints(self):
        """Test number field value constraints."""
        # Test minimum value
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", -1)
        assert is_valid is False
        assert "at least 0" in error
        
        # Test maximum value
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", 100000)
        assert is_valid is False
        assert "at most 99999" in error
        
        # Test valid value
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", 500)
        assert is_valid is True
        assert error == ""
        
        # Test valid float
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", 500.0)
        assert is_valid is True
        assert error == ""
    
    def test_validate_select_field_options(self):
        """Test single select field option validation."""
        # Test valid option
        is_valid, error = AirtableFieldMapping.validate_field_value("Role", "CANDIDATE")
        assert is_valid is True
        assert error == ""
        
        # Test invalid option
        is_valid, error = AirtableFieldMapping.validate_field_value("Role", "INVALID_ROLE")
        assert is_valid is False
        assert "must be one of" in error
        assert "CANDIDATE" in error
        assert "TEAM" in error
    
    def test_validate_date_field(self):
        """Test date field validation."""
        # Test valid date object
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentDate", date(2024, 1, 15))
        assert is_valid is True
        assert error == ""
        
        # Test valid date string
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentDate", "2024-01-15")
        assert is_valid is True
        assert error == ""
        
        # Test invalid type
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentDate", 12345)
        assert is_valid is False
        assert "must be a date" in error
    
    def test_validate_type_mismatch(self):
        """Test validation with wrong data types."""
        # Text field with non-string
        is_valid, error = AirtableFieldMapping.validate_field_value("FullNameRU", 123)
        assert is_valid is False
        assert "must be a string" in error
        
        # Number field with string
        is_valid, error = AirtableFieldMapping.validate_field_value("PaymentAmount", "not_a_number")
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


class TestFieldMappingCompleteness:
    """Test suite for field mapping completeness and consistency."""
    
    def test_mapping_completeness(self):
        """Test that all model fields have proper mappings."""
        # Expected fields based on Participant model
        expected_python_fields = [
            "full_name_ru", "full_name_en", "church", "country_and_city",
            "submitted_by", "contact_information", "gender", "size", 
            "role", "department", "payment_status", "payment_amount", 
            "payment_date", "record_id"
        ]
        
        python_fields = AirtableFieldMapping.get_all_python_fields()
        
        for expected_field in expected_python_fields:
            assert expected_field in python_fields, f"Missing Python field: {expected_field}"
    
    def test_bidirectional_consistency(self):
        """Test that bidirectional mapping is consistent."""
        python_fields = AirtableFieldMapping.get_all_python_fields()
        
        for py_field in python_fields:
            airtable_field = AirtableFieldMapping.get_airtable_field_name(py_field)
            assert airtable_field is not None
            
            reverse_py_field = AirtableFieldMapping.get_python_field_name(airtable_field)
            assert reverse_py_field == py_field, f"Bidirectional mapping inconsistency: {py_field} <-> {airtable_field}"
    
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