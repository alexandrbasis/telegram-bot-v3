"""
Israel Missions 2025 CSV → Airtable mapping constants and normalization helpers.

This module provides typed mapping dictionaries and validation helpers for
safely importing participant data from Google Form responses to Airtable.

Based on the mapping specification:
docs/data-integration/israel-missions-2025-mapping.md
"""

import re
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from src.config.field_mappings import AirtableFieldMapping


class IsraelMissionsMapping:
    """Mapping constants and helpers for Israel Missions 2025 participant import."""

    # CSV column → Airtable field mapping (based on mapping doc)
    CSV_TO_AIRTABLE: Dict[str, str] = {
        "FullNameRU": "FullNameRU",
        "DateOfBirth": "DateOfBirth",
        "Gender": "Gender",
        "Size": "Size",
        "ContactInformation": "ContactInformation",
        "CountryAndCity": "CountryAndCity",
        "Role": "Role",
    }

    # Derived/defaulted fields (not from CSV)
    DERIVED_FIELDS: Dict[str, str] = {
        "SubmittedBy": "Israel Missions 2025 Form",
        "Notes": "Imported on {timestamp} via Israel Missions importer.",
        "EnvironmentTag": "missions-2025",  # Optional - only if field exists
    }

    # Required fields for validation
    REQUIRED_FIELDS = ["FullNameRU", "ContactInformation"]

    # Gender normalization mapping (case-insensitive)
    GENDER_MAPPING: Dict[str, str] = {
        "female": "F",
        "male": "M",
        "f": "F",
        "m": "M",
    }

    # Valid size options (must match Airtable single select options)
    VALID_SIZES = {"XS", "S", "M", "L", "XL", "XXL", "3XL"}

    # Valid role options (must match Airtable single select options)
    VALID_ROLES = {"TEAM", "CANDIDATE"}

    # Default role when CSV is blank
    DEFAULT_ROLE = "TEAM"

    @classmethod
    def normalize_gender(cls, gender_value: Optional[str]) -> Optional[str]:
        """
        Normalize gender value according to mapping specification.

        Args:
            gender_value: Raw gender value from CSV

        Returns:
            Normalized gender ("F" or "M") or None if invalid/blank
        """
        if not gender_value or not isinstance(gender_value, str):
            return None

        normalized = gender_value.strip().lower()
        return cls.GENDER_MAPPING.get(normalized)

    @classmethod
    def validate_size(cls, size_value: Optional[str]) -> Tuple[bool, Optional[str]]:
        """
        Validate and normalize size value.

        Args:
            size_value: Raw size value from CSV

        Returns:
            Tuple of (is_valid, normalized_size or None)
        """
        # Handle empty/None values - these are valid as field is optional
        if size_value is None:
            return True, None

        if not isinstance(size_value, str):
            return False, None  # Non-string values are invalid

        size_value = size_value.strip()
        if not size_value:  # Empty string after stripping
            return True, None

        normalized = size_value.upper()
        if normalized in cls.VALID_SIZES:
            return True, normalized

        return False, None

    @classmethod
    def normalize_role(cls, role_value: Optional[str]) -> str:
        """
        Normalize role value with default fallback.

        Args:
            role_value: Raw role value from CSV

        Returns:
            Normalized role (always returns a valid role)
        """
        if not role_value or not isinstance(role_value, str):
            return cls.DEFAULT_ROLE

        normalized = role_value.strip().upper()
        if normalized in cls.VALID_ROLES:
            return normalized

        return cls.DEFAULT_ROLE

    @classmethod
    def parse_date_of_birth(cls, dob_value: Optional[str]) -> Optional[str]:
        """
        Parse date of birth from US format (M/D/Y) to European format (DD/MM/YYYY).

        Args:
            dob_value: Raw date string from CSV (e.g., "7/2/1992")

        Returns:
            European formatted date string (e.g., "02/07/1992") or None if invalid
        """
        if not dob_value or not isinstance(dob_value, str):
            return None

        dob_value = dob_value.strip()
        if not dob_value:
            return None

        try:
            # Parse US format: M/D/Y or M/D/YYYY
            parsed_date = datetime.strptime(dob_value, "%m/%d/%Y")
            # Return European format: DD/MM/YYYY
            return parsed_date.strftime("%d/%m/%Y")
        except ValueError:
            try:
                # Try alternative format just in case
                parsed_date = datetime.strptime(dob_value, "%m/%d/%y")
                return parsed_date.strftime("%d/%m/%Y")
            except ValueError:
                return None

    @classmethod
    def normalize_contact_for_duplicate_detection(cls, contact_info: str) -> str:
        """
        Normalize contact information for duplicate detection.

        Extracts digits only, strips +, -, spaces for phone number comparison.

        Args:
            contact_info: Raw contact information

        Returns:
            Normalized contact string (digits only for phone numbers)
        """
        if not contact_info:
            return ""

        # Extract digits only for phone number normalization
        digits_only = re.sub(r"[^\d]", "", contact_info)
        return digits_only

    @classmethod
    def redact_contact_for_logging(cls, contact_info: str) -> str:
        """
        Redact contact information for safe logging.

        Keeps first 2 and last 2 characters for phone numbers, masks middle.

        Args:
            contact_info: Raw contact information

        Returns:
            Redacted contact string safe for logging
        """
        if not contact_info or len(contact_info) < 5:
            return "****"

        # For phone numbers, show pattern like +7********01
        if contact_info.startswith("+") and len(contact_info) > 6:
            return (
                f"{contact_info[:2]}{'*' * (len(contact_info) - 4)}{contact_info[-2:]}"
            )

        # For other formats, mask middle
        return f"{contact_info[:2]}{'*' * (len(contact_info) - 4)}{contact_info[-2:]}"

    @classmethod
    def create_airtable_payload(
        cls, csv_row: Dict[str, Any], timestamp: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create Airtable payload from CSV row with transformations applied.

        Args:
            csv_row: Dictionary of CSV column values
            timestamp: ISO timestamp for notes (defaults to current time)

        Returns:
            Dictionary ready for Airtable API with field names and transformed values
        """
        if timestamp is None:
            timestamp = datetime.now().isoformat()

        payload = {}

        # Process CSV fields with transformations
        for csv_column, airtable_field in cls.CSV_TO_AIRTABLE.items():
            raw_value = csv_row.get(csv_column)

            # Role field should always be processed (even if None) to get default value
            if raw_value is None and airtable_field != "Role":
                continue

            # Apply field-specific transformations
            if airtable_field == "FullNameRU":
                transformed_value = raw_value.strip() if raw_value else None
            elif airtable_field == "DateOfBirth":
                transformed_value = cls.parse_date_of_birth(raw_value)
            elif airtable_field == "Gender":
                transformed_value = cls.normalize_gender(raw_value)
            elif airtable_field == "Size":
                is_valid, transformed_value = cls.validate_size(raw_value)
                if not is_valid:
                    transformed_value = None  # Skip invalid sizes
            elif airtable_field == "Role":
                transformed_value = cls.normalize_role(raw_value)
            elif airtable_field == "ContactInformation":
                transformed_value = raw_value.strip() if raw_value else None
            elif airtable_field == "CountryAndCity":
                transformed_value = raw_value.strip() if raw_value else None
            else:
                # Default: strip whitespace for text fields
                transformed_value = (
                    raw_value.strip() if isinstance(raw_value, str) else raw_value
                )

            # Only add non-None values to payload
            if transformed_value is not None:
                payload[airtable_field] = transformed_value

        # Add derived/default fields
        payload["SubmittedBy"] = cls.DERIVED_FIELDS["SubmittedBy"]
        existing_notes = payload.get("Notes", "")
        import_note = cls.DERIVED_FIELDS["Notes"].format(timestamp=timestamp)

        if existing_notes:
            payload["Notes"] = f"{existing_notes}\n{import_note}"
        else:
            payload["Notes"] = import_note

        return payload

    @classmethod
    def validate_required_fields(cls, payload: Dict[str, Any]) -> Tuple[bool, list]:
        """
        Validate that all required fields are present and non-empty.

        Args:
            payload: Airtable payload dictionary

        Returns:
            Tuple of (is_valid, list_of_missing_fields)
        """
        missing_fields = []

        for required_field in cls.REQUIRED_FIELDS:
            if required_field not in payload or not payload[required_field]:
                missing_fields.append(required_field)

        return len(missing_fields) == 0, missing_fields

    @classmethod
    def get_duplicate_detection_keys(cls, payload: Dict[str, Any]) -> Tuple[str, str]:
        """
        Extract keys for duplicate detection from payload.

        Returns normalized contact info and name+DOB combination.

        Args:
            payload: Airtable payload dictionary

        Returns:
            Tuple of (normalized_contact, name_dob_key)
        """
        # Primary key: normalized contact information
        contact_info = payload.get("ContactInformation", "")
        normalized_contact = cls.normalize_contact_for_duplicate_detection(contact_info)

        # Secondary key: case-folded name + DOB
        full_name = payload.get("FullNameRU", "").lower()
        dob = payload.get("DateOfBirth", "")
        name_dob_key = f"{full_name}|{dob}" if dob else full_name

        return normalized_contact, name_dob_key

    @classmethod
    def translate_to_field_ids(cls, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate Airtable field names to Field IDs for API calls.

        Args:
            payload: Dictionary with Airtable field names as keys

        Returns:
            Dictionary with Field IDs as keys
        """
        return AirtableFieldMapping.translate_fields_to_ids(payload)
