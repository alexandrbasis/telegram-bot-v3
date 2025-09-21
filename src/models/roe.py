"""
ROE data model for Airtable integration.

This module defines the Pydantic model for ROE table records,
including validation and serialization methods.
"""

from typing import List

from pydantic import BaseModel, ConfigDict, Field


class ROE(BaseModel):
    """
    Data model for ROE (Rollo of Encouragement) table records.

    Attributes:
        id: Airtable record ID
        roe_topic: The topic of the ROE (primary field)
        roista: List of participant record IDs for the main presenter(s)
        assistant: List of participant record IDs for assistant(s)
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(..., description="Airtable record ID")
    roe_topic: str = Field(..., description="The topic of the ROE")
    roista: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for the main presenter(s)"
    )
    assistant: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs for assistant(s)"
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
            id=record["id"],
            roe_topic=fields.get("RoeTopic", ""),
            roista=fields.get("Roista", []),
            assistant=fields.get("Assistant", [])
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