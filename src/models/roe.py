"""
ROE data model for Airtable integration.

This module defines the Pydantic model for ROE table records,
including validation and serialization methods.
"""

from datetime import date
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, ConfigDict, Field


class ROE(BaseModel):
    """
    Data model for ROE (Rollo of Encouragement) table records.

    Attributes:
        record_id: Airtable record ID for existing records
        roe_topic: The topic of the ROE (primary field)
        roista: List of participant record IDs for the main presenter(s)
        assistant: List of participant record IDs for assistant(s)
        prayer: List of participant record IDs for prayer support
        roe_date: Scheduled date of the ROE talk
        roe_timing: Time slot or schedule marker
        roe_duration: Allocated duration for the ROE talk (in minutes)
        roista_church: Churches of the main Roista (lookup from participants)
        roista_department: Departments of the main Roista (lookup from participants)
        roista_room: Room numbers of the main Roista (lookup from participants)
        roista_notes: Notes about the main Roista (lookup from participants)
        assistant_church: Churches of the assistant Roista (lookup from
            participants)
        assistant_department: Departments of the assistant Roista (lookup from
            participants)
        assistant_room: Room numbers of the assistant Roista (lookup from
            participants)
    """

    model_config = ConfigDict(str_strip_whitespace=True, populate_by_name=True)

    record_id: Optional[str] = Field(
        None, description="Airtable record ID for existing records"
    )
    roe_topic: str = Field(..., description="The topic of the ROE")
    roista: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for the main presenter(s)",
    )
    assistant: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for assistant(s)",
    )
    prayer: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for prayer support",
    )
    roe_date: Optional[date] = Field(
        None,
        description="Scheduled date of the ROE talk",
    )
    roe_timing: Optional[str] = Field(
        None,
        description="Time slot or schedule marker",
    )
    roe_duration: Optional[int] = Field(
        None,
        description="Allocated duration for the ROE talk (in minutes)",
    )
    roista_church: Optional[List[str]] = Field(
        None,
        description="Churches of the main Roista (lookup from participants)",
        alias="RoistaChurch",
    )
    roista_department: Optional[List[str]] = Field(
        None,
        description="Departments of the main Roista (lookup from participants)",
        alias="RoistaDepartment",
    )
    roista_room: Optional[List[Union[int, str]]] = Field(
        None,
        description="Room numbers of the main Roista (lookup from participants)",
        alias="RoistaRoom",
    )
    roista_notes: Optional[List[str]] = Field(
        None,
        description="Notes about the main Roista (lookup from participants)",
        alias="RoistaNotes",
    )
    assistant_church: Optional[List[str]] = Field(
        None,
        description="Churches of the assistant Roista (lookup from participants)",
        alias="AssistantChuch",  # Note: Airtable has a typo in field name
    )
    assistant_department: Optional[List[str]] = Field(
        None,
        description="Departments of the assistant Roista (lookup from participants)",
        alias="AssistantDepartment",
    )
    assistant_room: Optional[List[Union[int, str]]] = Field(
        None,
        description="Room numbers of the assistant Roista (lookup from participants)",
        alias="AssistantRoom",
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

        roe_data: Dict[str, Any] = {
            "record_id": record.get("id"),
            "roe_topic": fields.get("RoeTopic", ""),
            "roista": fields.get("Roista", []),
            "assistant": fields.get("Assistant", []),
            "prayer": fields.get("Prayer", []),
            "roe_date": fields.get("RoeDate"),
            "roe_timing": fields.get("RoeTiming"),
            "roe_duration": fields.get("RoeDuration"),
        }

        if "RoistaChurch" in fields:
            roe_data["roista_church"] = fields["RoistaChurch"]
        if "RoistaDepartment" in fields:
            roe_data["roista_department"] = fields["RoistaDepartment"]
        if "RoistaRoom" in fields:
            roe_data["roista_room"] = fields["RoistaRoom"]
        if "RoistaNotes" in fields:
            roe_data["roista_notes"] = fields["RoistaNotes"]
        if "AssistantChuch" in fields:
            roe_data["assistant_church"] = fields["AssistantChuch"]
        if "AssistantDepartment" in fields:
            roe_data["assistant_department"] = fields["AssistantDepartment"]
        if "AssistantRoom" in fields:
            roe_data["assistant_room"] = fields["AssistantRoom"]

        return cls(**roe_data)

    def to_airtable_fields(self) -> dict:
        """
        Convert the model to Airtable fields format.

        Returns:
            Dictionary of field names to values for Airtable API
        """
        fields = {
            "RoeTopic": self.roe_topic,
            "Roista": self.roista,
            "Assistant": self.assistant,
            "Prayer": self.prayer,
        }

        # Add optional scheduling fields if they have values
        if self.roe_date is not None:
            fields["RoeDate"] = self.roe_date.isoformat()
        if self.roe_timing is not None:
            fields["RoeTiming"] = self.roe_timing
        if self.roe_duration is not None:
            fields["RoeDuration"] = self.roe_duration

        return fields
