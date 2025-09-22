"""
ROE data model for Airtable integration.

This module defines the Pydantic model for ROE table records,
including validation and serialization methods.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ROE(BaseModel):
    """
    Data model for ROE (Rollo of Encouragement) table records.

    Attributes:
        record_id: Airtable record ID for existing records
        roe_topic: The topic of the ROE (primary field)
        roista: List of participant record IDs for the main presenter(s)
        roista_church: Churches of the main Roista (lookup from participants)
        roista_department: Departments of the main Roista (lookup from participants)
        roista_room: Room numbers of the main Roista (lookup from participants)
        roista_notes: Notes about the main Roista (lookup from participants)
        assistant: List of participant record IDs for assistant(s)
        assistant_church: Churches of the assistant Roista (lookup from participants)
        assistant_department: Departments of the assistant Roista (lookup from participants)
        assistant_room: Room numbers of the assistant Roista (lookup from participants)
    """

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    record_id: Optional[str] = Field(None, description="Airtable record ID for existing records")
    roe_topic: str = Field(..., description="The topic of the ROE")
    roista: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for the main presenter(s)"
    )
    roista_church: Optional[List[str]] = Field(
        None,
        description="Churches of the main Roista (lookup from participants)",
        alias="RoistaChurch"
    )
    roista_department: Optional[List[str]] = Field(
        None,
        description="Departments of the main Roista (lookup from participants)",
        alias="RoistaDepartment"
    )
    roista_room: Optional[List[Union[int, str]]] = Field(
        None,
        description="Room numbers of the main Roista (lookup from participants)",
        alias="RoistaRoom"
    )
    roista_notes: Optional[List[str]] = Field(
        None,
        description="Notes about the main Roista (lookup from participants)",
        alias="RoistaNotes"
    )
    assistant: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for assistant(s)"
    )
    assistant_church: Optional[List[str]] = Field(
        None,
        description="Churches of the assistant Roista (lookup from participants)",
        alias="AssistantChuch"  # Note: Airtable has a typo in field name
    )
    assistant_department: Optional[List[str]] = Field(
        None,
        description="Departments of the assistant Roista (lookup from participants)",
        alias="AssistantDepartment"
    )
    assistant_room: Optional[List[Union[int, str]]] = Field(
        None,
        description="Room numbers of the assistant Roista (lookup from participants)",
        alias="AssistantRoom"
    )

    @classmethod
    def from_airtable_record(cls, record: dict) -> "ROE":
        """
        Create a ROE instance from an Airtable record.

        Args:
            record: Raw Airtable record with 'id' and 'fields' keys

        Returns:
            ROE instance
        """
        fields = record.get("fields", {})

        return cls(
            record_id=record.get("id"),
            roe_topic=fields.get("RoeTopic", ""),
            roista=fields.get("Roista", []),
            roista_church=fields.get("RoistaChurch"),
            roista_department=fields.get("RoistaDepartment"),
            roista_room=fields.get("RoistaRoom"),
            roista_notes=fields.get("RoistaNotes"),
            assistant=fields.get("Assistant", []),
            assistant_church=fields.get("AssistantChuch"),  # Airtable has typo
            assistant_department=fields.get("AssistantDepartment"),
            assistant_room=fields.get("AssistantRoom")
        )

    def to_airtable_fields(self) -> dict:
        """
        Convert the model to Airtable fields format.

        Returns:
            Dictionary of field names to values for Airtable API
        """
        return {
            "RoeTopic": self.roe_topic,
            "Roista": self.roista,
            "Assistant": self.assistant
        }