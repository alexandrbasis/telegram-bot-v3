"""Schedule model definitions for Airtable schedule integration."""

from __future__ import annotations

import datetime as dt
from typing import Any, Mapping, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

# Airtable field names for the Schedule table
FIELD_EVENT_DATE = "EventDate"
FIELD_START_TIME = "StartTime"
FIELD_END_TIME = "EndTime"
FIELD_TITLE = "EventTitle"
FIELD_DESCRIPTION = "Description"
FIELD_AUDIENCE = "Audience"
FIELD_DAY_TAG = "DayTag"
FIELD_ORDER = "Order"
FIELD_IS_ACTIVE = "IsActive"
FIELD_LOCATION = "Location"


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
            FIELD_EVENT_DATE: self.date.isoformat(),
            FIELD_START_TIME: self.start_time.strftime("%H:%M"),
            FIELD_TITLE: self.title,
            FIELD_IS_ACTIVE: self.is_active,
        }

        if self.end_time is not None:
            fields[FIELD_END_TIME] = self.end_time.strftime("%H:%M")
        if self.description:
            fields[FIELD_DESCRIPTION] = self.description
        if self.audience:
            fields[FIELD_AUDIENCE] = self.audience
        if self.day_label:
            fields[FIELD_DAY_TAG] = self.day_label
        if self.order is not None:
            fields[FIELD_ORDER] = self.order
        if self.location:
            fields[FIELD_LOCATION] = self.location

        return fields

    @classmethod
    def from_airtable_record(cls, record: Mapping[str, Any]) -> "ScheduleEntry":
        """Create schedule entry from Airtable record dictionary."""
        fields = record.get("fields", {})

        try:
            raw_date = fields[FIELD_EVENT_DATE]
            raw_start = fields[FIELD_START_TIME]
            title = fields[FIELD_TITLE]
        except KeyError as error:
            raise ValueError(
                f"Schedule record is missing required field: {error.args[0]}"
            ) from error

        entry = cls(
            record_id=record.get("id"),
            date=dt.date.fromisoformat(raw_date),
            start_time=cls._parse_time(raw_start),
            end_time=cls._parse_optional_time(fields.get(FIELD_END_TIME)),
            title=title,
            description=cls._normalize_optional_str(fields.get(FIELD_DESCRIPTION)),
            audience=cls._normalize_optional_str(fields.get(FIELD_AUDIENCE)),
            day_label=cls._normalize_optional_str(fields.get(FIELD_DAY_TAG)),
            order=cls._parse_optional_int(fields.get(FIELD_ORDER)),
            is_active=bool(fields.get(FIELD_IS_ACTIVE, True)),
            location=cls._normalize_optional_str(fields.get(FIELD_LOCATION)),
        )

        return entry

    @staticmethod
    def _parse_time(raw_value: str) -> dt.time:
        return dt.time.fromisoformat(raw_value)

    @classmethod
    def _parse_optional_time(cls, raw_value: Optional[str]) -> Optional[dt.time]:
        if raw_value is None:
            return None
        if isinstance(raw_value, str) and not raw_value.strip():
            return None
        return cls._parse_time(raw_value)

    @staticmethod
    def _normalize_optional_str(value: Optional[Any]) -> Optional[str]:
        if value is None:
            return None
        if not isinstance(value, str):
            return str(value)
        stripped = value.strip()
        return stripped or None

    @staticmethod
    def _parse_optional_int(value: Optional[Any]) -> Optional[int]:
        if value is None:
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None
