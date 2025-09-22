"""
ROE field mapping configuration for Airtable integration.

This module defines the mapping between Python model field names and
Airtable field names for the ROE table, along with validation rules
and field ID mappings.
"""

from typing import Dict


class ROEFieldMapping:
    """
    Mapping configuration between Python ROE model fields and Airtable fields.

    Defines the bidirectional mapping for ROE table (tbl0j8bcgkV3lVAdc).
    """

    # Airtable field name -> Field ID mapping (exact Field IDs from Airtable base)
    AIRTABLE_FIELD_IDS: Dict[str, str] = {
        # Primary field
        "RoeTopic": "fldSniGvfWpmkpc1r",  # The topic or name of the ROE session
        # Link fields
        "Roista": "fldLWsfnGvJ26GwMI",  # Links to main Roista (presenter)
        "Assistant": "fldtTUTsJy6oCg1sE",  # Links to assistant presenters
        "Prayer": "fldRSXoqNE16Inb7E",  # Prayer support assignments
        # Date and timing fields
        "RoeDate": "fldQHFNv68aNjuQOk",  # Scheduled date of the ROE talk
        "RoeTiming": "fldlobIBO2k62FaoA",  # Time slot or schedule marker
        "RoeDuration": "fldpTVshWBBvv2T8X",  # Allocated duration for the ROE talk
        # Lookup fields (read-only from linked participants)
        "RoistaChurch": "fldLookupRChurch",  # Churches of main Roista (lookup)
        "RoistaDepartment": "fldLookupRDept",  # Departments of main Roista (lookup)
        "RoistaRoom": "fldLookupRRoom",  # Room numbers of main Roista (lookup)
        "RoistaNotes": "fldLookupRNotes",  # Notes about main Roista (lookup)
        "AssistantChuch": "fldLookupAChuch",  # Churches of assistant (lookup, note typo)
        "AssistantDepartment": "fldLookupADept",  # Departments of assistant (lookup)
        "AssistantRoom": "fldLookupARoom",  # Room numbers of assistant (lookup)
        # Special record ID pseudo-field mapping
        "id": "fldRECORDID000000",
    }

    # Python field name -> Airtable field name mapping
    PYTHON_TO_AIRTABLE: Dict[str, str] = {
        # Core fields
        "roe_topic": "RoeTopic",
        "roista": "Roista",
        "assistant": "Assistant",
        "prayer": "Prayer",
        # Scheduling fields
        "roe_date": "RoeDate",
        "roe_timing": "RoeTiming",
        "roe_duration": "RoeDuration",
        # Lookup fields (read-only)
        "roista_church": "RoistaChurch",
        "roista_department": "RoistaDepartment",
        "roista_room": "RoistaRoom",
        "roista_notes": "RoistaNotes",
        "assistant_church": "AssistantChuch",  # Note: preserves Airtable typo
        "assistant_department": "AssistantDepartment",
        "assistant_room": "AssistantRoom",
        # Record ID
        "record_id": "id",
    }

    # Airtable field name -> Python field name mapping (reverse mapping)
    AIRTABLE_TO_PYTHON: Dict[str, str] = {
        v: k for k, v in PYTHON_TO_AIRTABLE.items()
    }

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
        excluded_fields = {
            "roista_church", "roista_department", "roista_room", "roista_notes",
            "assistant_church", "assistant_department", "assistant_room", "record_id"
        }
        return {
            python_field: airtable_field
            for python_field, airtable_field in cls.PYTHON_TO_AIRTABLE.items()
            if python_field not in excluded_fields
        }

    @classmethod
    def get_presenter_relationship_fields(cls) -> Dict[str, str]:
        """
        Get fields related to presenter and assistant relationships.

        Returns:
            Dictionary of python_field_name -> airtable_field_name for relationship fields
        """
        relationship_fields = {"roista", "assistant", "prayer"}
        return {
            python_field: airtable_field
            for python_field, airtable_field in cls.PYTHON_TO_AIRTABLE.items()
            if python_field in relationship_fields
        }

    @classmethod
    def get_scheduling_fields(cls) -> Dict[str, str]:
        """
        Get fields related to ROE scheduling and timing.

        Returns:
            Dictionary of python_field_name -> airtable_field_name for scheduling fields
        """
        scheduling_fields = {"roe_date", "roe_timing", "roe_duration"}
        return {
            python_field: airtable_field
            for python_field, airtable_field in cls.PYTHON_TO_AIRTABLE.items()
            if python_field in scheduling_fields
        }

    @classmethod
    def validate_presenter_relationships(cls, roe_data: dict) -> bool:
        """
        Validate that ROE has at least one presenter (roista or assistant).

        Args:
            roe_data: Dictionary containing ROE field data

        Returns:
            True if ROE has at least one presenter, False otherwise
        """
        roista = roe_data.get("roista", [])
        assistant = roe_data.get("assistant", [])

        # At least one presenter (roista or assistant) should be assigned
        return bool(roista or assistant)

    @classmethod
    def format_duration_for_airtable(cls, duration_minutes: int) -> str:
        """
        Format duration in minutes to Airtable duration format (h:mm).

        Args:
            duration_minutes: Duration in minutes

        Returns:
            Duration string in h:mm format for Airtable
        """
        hours = duration_minutes // 60
        minutes = duration_minutes % 60
        return f"{hours}:{minutes:02d}"