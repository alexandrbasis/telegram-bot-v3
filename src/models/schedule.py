"""Schedule model definitions for Airtable schedule integration."""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class ScheduleEntry(BaseModel):
    """Represents a single schedule item pulled from Airtable."""

    record_id: Optional[str] = Field(
        default=None, description="Airtable record identifier for the schedule entry"
    )
    date: dt.date = Field(..., description="Date of the schedule entry")
    start_time: dt.time = Field(..., description="Start time of the schedule entry")
    end_time: Optional[dt.time] = Field(
        default=None, description="Optional end time of the schedule entry"
    )
    title: str = Field(..., min_length=1, description="Title of the schedule entry")
    description: Optional[str] = Field(
        default=None, description="Description or details for the entry"
    )
    audience: Optional[str] = Field(
        default=None, description="Target audience for the entry"
    )
    day_label: Optional[str] = Field(
        default=None, description="Human-readable label for the day"
    )
    order: Optional[int] = Field(
        default=None, ge=0, description="Manual ordering value for the schedule"
    )
    is_active: bool = Field(
        default=True, description="Whether the schedule entry should be shown"
    )
    location: Optional[str] = Field(default=None, description="Location or room name")

    model_config = ConfigDict(validate_assignment=True)

    @field_validator("title")
    @classmethod
    def _validate_title(cls, value: str) -> str:
        stripped = value.strip()
        if not stripped:
            raise ValueError("title cannot be empty")
        return stripped

    @field_validator("day_label")
    @classmethod
    def _normalize_day_label(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return value
        stripped = value.strip()
        return stripped or None

    @model_validator(mode="after")
    def _validate_time_range(self):
        if self.end_time is not None and self.end_time <= self.start_time:
            raise ValueError("end_time must be after start_time when provided")
        return self

    def to_airtable_fields(self) -> dict[str, Any]:
        """Convert schedule entry into Airtable field representation."""
        fields: dict[str, Any] = {
            "Date": self.date.isoformat(),
            "StartTime": self.start_time.strftime("%H:%M"),
            "Title": self.title,
            "IsActive": self.is_active,
        }

        if self.end_time is not None:
            fields["EndTime"] = self.end_time.strftime("%H:%M")
        if self.description:
            fields["Description"] = self.description
        if self.audience:
            fields["Audience"] = self.audience
        if self.day_label:
            fields["DayLabel"] = self.day_label
        if self.order is not None:
            fields["Order"] = self.order
        if self.location:
            fields["Location"] = self.location

        return fields

    @classmethod
    def from_airtable_record(cls, record: Mapping[str, Any]) -> "ScheduleEntry":
        """Create schedule entry from Airtable record dictionary."""
        fields = record.get("fields", {})

        try:
            raw_date = fields["Date"]
            raw_start = fields["StartTime"]
            title = fields["Title"]
        except KeyError as error:
            raise ValueError(
                f"Schedule record is missing required field: {error.args[0]}"
            ) from error

        entry = cls(
            record_id=record.get("id"),
            date=dt.date.fromisoformat(raw_date),
            start_time=cls._parse_time(raw_start),
            end_time=cls._parse_optional_time(fields.get("EndTime")),
            title=title,
            description=fields.get("Description"),
            audience=fields.get("Audience"),
            day_label=fields.get("DayLabel"),
            order=fields.get("Order"),
            is_active=fields.get("IsActive", True),
            location=fields.get("Location"),
        )

        return entry

    @staticmethod
    def _parse_time(raw_value: str) -> dt.time:
        return dt.time.fromisoformat(raw_value)

    @classmethod
    def _parse_optional_time(cls, raw_value: Optional[str]) -> Optional[dt.time]:
        if raw_value is None:
            return None
        return cls._parse_time(raw_value)
