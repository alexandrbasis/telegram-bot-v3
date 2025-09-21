"""
BibleReaders data model for Airtable integration.

This module defines the Pydantic model for BibleReaders table records,
including validation and serialization methods.
"""

from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, field_serializer


class BibleReader(BaseModel):
    """
    Data model for BibleReaders table records.

    Attributes:
        id: Airtable record ID
        where: Location/session description (primary field)
        participants: List of participant record IDs
        when: Date of the reading session
        bible: Bible passage or reference
    """

    model_config = ConfigDict(str_strip_whitespace=True)

    id: str = Field(..., description="Airtable record ID")
    where: str = Field(..., description="Location or session description")
    participants: List[str] = Field(
        default_factory=list,
        description="List of participant record IDs"
    )
    when: Optional[date] = Field(None, description="Date of the reading session")
    bible: Optional[str] = Field(None, description="Bible passage or reference")

    @field_serializer("when", mode="plain", when_used="json")
    def serialize_date(self, value: Optional[date]) -> Optional[str]:
        """Serialize date to ISO format string for JSON serialization."""
        return value.isoformat() if value else None

    @classmethod
    def from_airtable_record(cls, record: dict) -> "BibleReader":
        """
        Create a BibleReader instance from an Airtable record.

        Args:
            record: Raw Airtable record with 'id' and 'fields' keys

        Returns:
            BibleReader instance
        """
        fields = record.get("fields", {})

        return cls(
            id=record["id"],
            where=fields.get("Where", ""),
            participants=fields.get("Participants", []),
            when=fields.get("When"),
            bible=fields.get("Bible")
        )

    def to_airtable_fields(self) -> dict:
        """
        Convert the model to Airtable fields format.

        Returns:
            Dictionary of field names to values for Airtable API
        """
        fields = {
            "Where": self.where,
            "Participants": self.participants
        }

        if self.when is not None:
            fields["When"] = self.when.isoformat()

        if self.bible is not None:
            fields["Bible"] = self.bible

        return fields