"""
BibleReaders field mapping configuration for Airtable integration.

This module defines the mapping between Python model field names and
Airtable field names for the BibleReaders table, along with validation
rules and field ID mappings.
"""

from typing import Dict


class BibleReadersFieldMapping:
    """
    Mapping configuration between Python BibleReader model fields and Airtable fields.

    Defines the bidirectional mapping for BibleReaders table (tblGEnSfpPOuPLXcm).
    """

    # Airtable field name -> Field ID mapping (exact Field IDs from Airtable base)
    AIRTABLE_FIELD_IDS: Dict[str, str] = {
        # Primary field
        "Where": "fldsSNHSXJBhewCxq",  # Location or context of the Bible reading
        # Link fields
        "Participants": "fldVBlRvv295QhBlX",  # Links to participants assigned to read
        # Date field
        "When": "fld6WfIcctT2WZnNO",  # Date of the Bible reading session
        # Text field
        "Bible": "fldi18WKRAa7iUXBQ",  # Bible passage or reference to be read
        # Lookup fields (read-only from linked participants)
        "Church": "fldLookupChurch01",  # Churches of Bible readers (lookup)
        "RoomNumber": "fldLookupRoom001",  # Room numbers of Bible readers (lookup)
        # Special record ID pseudo-field mapping
        "id": "fldRECORDID000000",
    }

    # Python field name -> Airtable field name mapping
    PYTHON_TO_AIRTABLE: Dict[str, str] = {
        # Core fields
        "where": "Where",
        "participants": "Participants",
        "when": "When",
        "bible": "Bible",
        # Lookup fields (read-only)
        "churches": "Church",
        "room_numbers": "RoomNumber",
        # Record ID
        "record_id": "id",
    }

    # Airtable field name -> Python field name mapping (reverse mapping)
    AIRTABLE_TO_PYTHON: Dict[str, str] = {v: k for k, v in PYTHON_TO_AIRTABLE.items()}

    @classmethod
    def get_airtable_field_id(cls, airtable_field_name: str) -> str:
        """
        Get the Airtable field ID for a given field name.

        Args:
            airtable_field_name: The Airtable field name

        Returns:
            The corresponding field ID

        Raises:
            KeyError: If the field name is not found
        """
        return cls.AIRTABLE_FIELD_IDS[airtable_field_name]

    @classmethod
    def python_to_airtable_field(cls, python_field_name: str) -> str:
        """
        Convert Python field name to Airtable field name.

        Args:
            python_field_name: Python model field name

        Returns:
            Corresponding Airtable field name

        Raises:
            KeyError: If the field name is not found
        """
        return cls.PYTHON_TO_AIRTABLE[python_field_name]

    @classmethod
    def airtable_to_python_field(cls, airtable_field_name: str) -> str:
        """
        Convert Airtable field name to Python field name.

        Args:
            airtable_field_name: Airtable field name

        Returns:
            Corresponding Python model field name

        Raises:
            KeyError: If the field name is not found
        """
        return cls.AIRTABLE_TO_PYTHON[airtable_field_name]

    @classmethod
    def get_writable_fields(cls) -> Dict[str, str]:
        """
        Get only the writable fields (excludes lookup fields and record ID).

        Returns:
            Dictionary of python_field_name -> airtable_field_name for writable fields
        """
        # Exclude lookup fields and record ID which are read-only
        excluded_fields = {"churches", "room_numbers", "record_id"}
        return {
            python_field: airtable_field
            for python_field, airtable_field in cls.PYTHON_TO_AIRTABLE.items()
            if python_field not in excluded_fields
        }

    @classmethod
    def format_date_for_airtable(cls, date_value: str) -> str:
        """
        Format date value for Airtable using localized format.

        Args:
            date_value: ISO date string (YYYY-MM-DD)

        Returns:
            Date string formatted for Airtable (using format = l)
        """
        # Airtable uses localized date format (format = l)
        # For now, return ISO format as Airtable accepts it
        # This can be enhanced later if specific locale formatting is needed
        return date_value
