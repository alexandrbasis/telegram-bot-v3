"""
Field mappings for the Schedule table in Airtable.
Maps field names to their Airtable field IDs.

NOTE: Field IDs need to be updated after the Schedule table is created in Airtable.
Replace all 'fld[TO_BE_FILLED]' with actual field IDs from Airtable.
"""

from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class ScheduleFieldMapping:
    """Field mappings for Schedule table."""

    # Primary field
    EVENT_TITLE: str = "fldwJzYx5l5NMnBET"  # EventTitle - singleLineText

    # Date and time fields
    EVENT_DATE: str = "fldywzhY2xGarPBjx"  # EventDate - date
    START_TIME: str = "fldy8llzYObPwtLAS"  # StartTime - singleLineText
    END_TIME: str = "fldSVERRPEGrt01P1"  # EndTime - singleLineText
    DURATION: str = "fld[NOT_CREATED]"  # Duration - duration (not created yet)

    # Description fields
    DESCRIPTION: str = "fldJC039MoBABhjDB"  # Description - multilineText
    LOCATION: str = "fldJv61i8wBKm85mV"  # Location - singleLineText
    NOTES: str = "fld[NOT_CREATED]"  # Notes - multilineText (not created yet)

    # Classification fields
    AUDIENCE: str = "fldJ2qrRz5eeJsvUQ"  # Audience - singleSelect
    EVENT_TYPE: str = "fld2FkrFTM3ArtdhC"  # EventType - singleSelect
    DAY_TAG: str = "fldaT1FRDW7p9zpvN"  # DayTag - singleSelect

    # Organization fields
    ORDER: str = "fldfehkMFGrZ8qV4Q"  # Order - number
    IS_ACTIVE: str = "fldS24f13v1STUFQ8"  # IsActive - checkbox
    IS_MANDATORY: str = "fld3A4pa7OOpJ3Ydc"  # IsMandatory - checkbox

    # Responsibility fields (not created yet)
    RESPONSIBLE_DEPARTMENT: str = (
        "fld[NOT_CREATED]"  # ResponsibleDepartment - singleSelect
    )
    RESPONSIBLE_PERSON: str = (
        "fld[NOT_CREATED]"  # ResponsiblePerson - multipleRecordLinks
    )

    @property
    def field_name_to_id(self) -> Dict[str, str]:
        """Get mapping of field names to field IDs."""
        return {
            "EventTitle": self.EVENT_TITLE,
            "EventDate": self.EVENT_DATE,
            "StartTime": self.START_TIME,
            "EndTime": self.END_TIME,
            "Duration": self.DURATION,
            "Description": self.DESCRIPTION,
            "Location": self.LOCATION,
            "Notes": self.NOTES,
            "Audience": self.AUDIENCE,
            "EventType": self.EVENT_TYPE,
            "DayTag": self.DAY_TAG,
            "Order": self.ORDER,
            "IsActive": self.IS_ACTIVE,
            "IsMandatory": self.IS_MANDATORY,
            "ResponsibleDepartment": self.RESPONSIBLE_DEPARTMENT,
            "ResponsiblePerson": self.RESPONSIBLE_PERSON,
        }

    @property
    def field_id_to_name(self) -> Dict[str, str]:
        """Get mapping of field IDs to field names."""
        return {v: k for k, v in self.field_name_to_id.items()}


# Single select field options (actual IDs from Airtable)
AUDIENCE_OPTIONS = {
    "All": "selw4mMpFAAX3MMHn",
    "Candidates": "selHrokUYNB1LJq4k",
    "Team": "selhyWR3HzMvJ0Eo8",
    "Clergy": "selC2xn33KAlmPmrh",
    "Leadership": "selIcB1agLkQK9XAI",
}

EVENT_TYPE_OPTIONS = {
    "Talk": "selaJbEmuyyHNfbeh",
    "Meal": "selzQiWxhxNN2f70N",
    "Chapel": "selBqnB3s1b4AJFNC",
    "ROE": "seltW5k8u0ydSoZUQ",
    "Activity": "seleRnLrfLo6gjl7s",
    "Break": "selGsfBHKnhrYl2Jm",
    "Prayer": "selz3IpA3qFmdSV9g",
    "Celebration": "seloBgHtrWI3oVh64",
}

DAY_TAG_OPTIONS = {
    "Day 0": "selVWqI7RSfGRObKh",  # Note: Simplified names from Airtable
    "Day 1": "seltyw13cDQHB7DBA",
    "Day 2": "selxCdMA3cGKiWyOc",
    "Day 3": "selarmFzvKP0Yjktm",
}

# View IDs (actual IDs from Airtable)
SCHEDULE_VIEWS = {
    "Active Events": "viwVk6sDqiF4qQyHM",  # Only this view exists currently
    # Additional views to be created:
    "All Events": "viw[TO_BE_CREATED]",
    "By Day": "viw[TO_BE_CREATED]",
    "November 13": "viw[TO_BE_CREATED]",
    "November 14": "viw[TO_BE_CREATED]",
    "November 15": "viw[TO_BE_CREATED]",
    "November 16": "viw[TO_BE_CREATED]",
    "Mandatory Events": "viw[TO_BE_CREATED]",
}

# Create singleton instance
schedule_field_mapping = ScheduleFieldMapping()


# Export convenience functions
def get_field_id(field_name: str) -> Optional[str]:
    """Get field ID by field name."""
    return schedule_field_mapping.field_name_to_id.get(field_name)


def get_field_name(field_id: str) -> Optional[str]:
    """Get field name by field ID."""
    return schedule_field_mapping.field_id_to_name.get(field_id)
