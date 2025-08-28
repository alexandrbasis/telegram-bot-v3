"""
Field mapping configurations for Airtable integration.

This module defines the mapping between Python model field names and 
Airtable field names, along with validation rules and constraints.
"""

from typing import Dict, List, Any, Optional
from enum import Enum

from src.models.participant import Role, Department, Gender, Size, PaymentStatus


class FieldType(str, Enum):
    """Airtable field types for validation and mapping."""
    TEXT = "singleLineText"
    LONG_TEXT = "multilineText"
    NUMBER = "number"
    DATE = "date"
    SINGLE_SELECT = "singleSelect"
    MULTIPLE_SELECT = "multipleRecordLinks"
    CHECKBOX = "checkbox"
    EMAIL = "email"
    PHONE = "phoneNumber"
    URL = "url"


class AirtableFieldMapping:
    """
    Mapping configuration between Python model fields and Airtable fields.
    
    Defines the bidirectional mapping and validation rules for each field.
    """
    
    # Airtable field name -> Field ID mapping (exact Field IDs from Airtable base)
    AIRTABLE_FIELD_IDS: Dict[str, str] = {
        # Text fields (6)
        "FullNameRU": "fldOcpA3JW5MRmR6R",      # Primary field, required
        "FullNameEN": "fldrFVukSmk0i9sqj",
        "Church": "fld4CXL9InW0ogAQh",
        "CountryAndCity": "fldJ7dFRzx7bR9U6g",
        "SubmittedBy": "flduADiTl7jpiy8OH", 
        "ContactInformation": "fldSy0Hbwl49VtZvf",
        
        # Single select fields (5)
        "Gender": "fldOAGXoU0DqqFRmB",
        "Size": "fldZyNgaaa1snp6s7",
        "Role": "fldetbIGOkKFK0hYq",
        "Department": "fldIh0eyPspgr1TWk",
        "PaymentStatus": "fldQzc7m7eO0JzRZf",
        
        # Number field (1)
        "PaymentAmount": "fldyP24ZbeGD8nnaZ",
        
        # Date field (1)
        "PaymentDate": "fldylOQLqcBwkmzlh"
    }
    
    # Python field name -> Airtable field name mapping
    PYTHON_TO_AIRTABLE: Dict[str, str] = {
        # Primary text fields
        "full_name_ru": "FullNameRU",
        "full_name_en": "FullNameEN", 
        "church": "Church",
        "country_and_city": "CountryAndCity",
        "submitted_by": "SubmittedBy",
        "contact_information": "ContactInformation",
        
        # Single select fields
        "gender": "Gender",
        "size": "Size",
        "role": "Role",
        "department": "Department", 
        "payment_status": "PaymentStatus",
        
        # Number fields
        "payment_amount": "PaymentAmount",
        
        # Date fields
        "payment_date": "PaymentDate",
        
        # Record ID (special field)
        "record_id": "id"
    }
    
    # Airtable field name -> Python field name mapping (reverse)
    AIRTABLE_TO_PYTHON: Dict[str, str] = {v: k for k, v in PYTHON_TO_AIRTABLE.items()}
    
    # Field type definitions for validation
    FIELD_TYPES: Dict[str, FieldType] = {
        "FullNameRU": FieldType.TEXT,
        "FullNameEN": FieldType.TEXT,
        "Church": FieldType.TEXT,
        "CountryAndCity": FieldType.TEXT,
        "SubmittedBy": FieldType.TEXT,
        "ContactInformation": FieldType.TEXT,
        "Gender": FieldType.SINGLE_SELECT,
        "Size": FieldType.SINGLE_SELECT,
        "Role": FieldType.SINGLE_SELECT,
        "Department": FieldType.SINGLE_SELECT,
        "PaymentStatus": FieldType.SINGLE_SELECT,
        "PaymentAmount": FieldType.NUMBER,
        "PaymentDate": FieldType.DATE
    }
    
    # Required fields (cannot be None/empty)
    REQUIRED_FIELDS: List[str] = [
        "FullNameRU"  # Primary field required by Airtable
    ]
    
    # Field constraints and validation rules
    FIELD_CONSTRAINTS: Dict[str, Dict[str, Any]] = {
        "FullNameRU": {
            "min_length": 1,
            "max_length": 100,
            "required": True,
            "description": "Primary field - participant's full name in Russian"
        },
        "FullNameEN": {
            "max_length": 100,
            "description": "Optional English name for international participants"
        },
        "Church": {
            "max_length": 100,
            "description": "Church or religious organization affiliation"
        },
        "CountryAndCity": {
            "max_length": 100,
            "description": "Geographic location information"
        },
        "SubmittedBy": {
            "max_length": 100,
            "description": "Person who submitted/registered this participant"
        },
        "ContactInformation": {
            "max_length": 200,
            "description": "Email, phone, or other contact details"
        },
        "PaymentAmount": {
            "min_value": 0,
            "max_value": 99999,
            "description": "Payment amount in currency units (integer)"
        },
        "PaymentDate": {
            "description": "Date when payment was received"
        }
    }
    
    # Single select field options (enum values)
    SELECT_FIELD_OPTIONS: Dict[str, List[str]] = {
        "Gender": [gender.value for gender in Gender],
        "Size": [size.value for size in Size],
        "Role": [role.value for role in Role], 
        "Department": [dept.value for dept in Department],
        "PaymentStatus": [status.value for status in PaymentStatus]
    }
    
    @classmethod
    def get_airtable_field_name(cls, python_field: str) -> Optional[str]:
        """
        Get Airtable field name from Python field name.
        
        Args:
            python_field: Python model field name
            
        Returns:
            Airtable field name or None if not found
        """
        return cls.PYTHON_TO_AIRTABLE.get(python_field)
    
    @classmethod
    def get_python_field_name(cls, airtable_field: str) -> Optional[str]:
        """
        Get Python field name from Airtable field name.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            Python model field name or None if not found
        """
        return cls.AIRTABLE_TO_PYTHON.get(airtable_field)
    
    @classmethod
    def get_field_type(cls, airtable_field: str) -> Optional[FieldType]:
        """
        Get field type for validation.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            FieldType enum value or None if not found
        """
        return cls.FIELD_TYPES.get(airtable_field)
    
    @classmethod
    def is_required_field(cls, airtable_field: str) -> bool:
        """
        Check if field is required.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            True if field is required
        """
        return airtable_field in cls.REQUIRED_FIELDS
    
    @classmethod
    def get_field_constraints(cls, airtable_field: str) -> Dict[str, Any]:
        """
        Get validation constraints for field.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            Dictionary of constraints or empty dict if none
        """
        return cls.FIELD_CONSTRAINTS.get(airtable_field, {})
    
    @classmethod
    def get_select_options(cls, airtable_field: str) -> List[str]:
        """
        Get valid options for single select fields.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            List of valid option values or empty list if not a select field
        """
        return cls.SELECT_FIELD_OPTIONS.get(airtable_field, [])
    
    @classmethod
    def validate_field_value(cls, airtable_field: str, value: Any) -> tuple[bool, str]:
        """
        Validate a field value against constraints.
        
        Args:
            airtable_field: Airtable field name
            value: Value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if value is None:
            if cls.is_required_field(airtable_field):
                return False, f"Field '{airtable_field}' is required but got None"
            return True, ""
        
        constraints = cls.get_field_constraints(airtable_field)
        field_type = cls.get_field_type(airtable_field)
        
        # Type-specific validation
        if field_type == FieldType.TEXT:
            if not isinstance(value, str):
                return False, f"Field '{airtable_field}' must be a string, got {type(value).__name__}"
            
            min_len = constraints.get("min_length", 0)
            max_len = constraints.get("max_length")
            
            if len(value) < min_len:
                return False, f"Field '{airtable_field}' must be at least {min_len} characters"
            
            if max_len and len(value) > max_len:
                return False, f"Field '{airtable_field}' must be at most {max_len} characters"
                
        elif field_type == FieldType.NUMBER:
            if not isinstance(value, (int, float)):
                return False, f"Field '{airtable_field}' must be a number, got {type(value).__name__}"
            
            min_val = constraints.get("min_value")
            max_val = constraints.get("max_value") 
            
            if min_val is not None and value < min_val:
                return False, f"Field '{airtable_field}' must be at least {min_val}"
            
            if max_val is not None and value > max_val:
                return False, f"Field '{airtable_field}' must be at most {max_val}"
                
        elif field_type == FieldType.SINGLE_SELECT:
            if not isinstance(value, str):
                return False, f"Field '{airtable_field}' must be a string, got {type(value).__name__}"
            
            valid_options = cls.get_select_options(airtable_field)
            if valid_options and value not in valid_options:
                return False, f"Field '{airtable_field}' must be one of {valid_options}, got '{value}'"
                
        elif field_type == FieldType.DATE:
            from datetime import date
            if not isinstance(value, (str, date)):
                return False, f"Field '{airtable_field}' must be a date or date string, got {type(value).__name__}"
        
        return True, ""
    
    @classmethod
    def get_all_airtable_fields(cls) -> List[str]:
        """
        Get list of all Airtable field names.
        
        Returns:
            List of all Airtable field names
        """
        return list(cls.PYTHON_TO_AIRTABLE.values())
    
    @classmethod
    def get_all_python_fields(cls) -> List[str]:
        """
        Get list of all Python field names.
        
        Returns:
            List of all Python model field names  
        """
        return list(cls.PYTHON_TO_AIRTABLE.keys())
    
    @classmethod
    def get_field_id(cls, airtable_field: str) -> Optional[str]:
        """
        Get Airtable Field ID from field name.
        
        Args:
            airtable_field: Airtable field name
            
        Returns:
            Airtable Field ID or None if not found
        """
        return cls.AIRTABLE_FIELD_IDS.get(airtable_field)
    
    @classmethod
    def translate_fields_to_ids(cls, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate field names to Field IDs for API calls.
        
        Args:
            data: Dictionary with field names as keys
            
        Returns:
            Dictionary with Field IDs as keys, preserving unknown fields
        """
        translated = {}
        for field_name, value in data.items():
            field_id = cls.get_field_id(field_name)
            key = field_id if field_id else field_name
            translated[key] = value
        return translated


class SearchFieldMapping:
    """
    Mapping configuration for search operations.
    
    Defines how search criteria map to Airtable formula fields.
    """
    
    # Search criteria field mapping for repository search operations
    SEARCH_CRITERIA_MAPPING: Dict[str, str] = {
        "full_name_ru": "FullNameRU",
        "full_name_en": "FullNameEN", 
        "church": "Church",
        "role": "Role",
        "department": "Department",
        "payment_status": "PaymentStatus", 
        "gender": "Gender"
    }
    
    @classmethod
    def get_search_field_name(cls, criteria_field: str) -> Optional[str]:
        """
        Get Airtable field name for search criteria.
        
        Args:
            criteria_field: Search criteria field name
            
        Returns:
            Airtable field name or None if not searchable
        """
        return cls.SEARCH_CRITERIA_MAPPING.get(criteria_field)
    
    @classmethod
    def get_searchable_fields(cls) -> List[str]:
        """
        Get list of fields that can be used in search criteria.
        
        Returns:
            List of searchable field names
        """
        return list(cls.SEARCH_CRITERIA_MAPPING.keys())


# Field mapping instances for easy import
field_mapping = AirtableFieldMapping()
search_mapping = SearchFieldMapping()