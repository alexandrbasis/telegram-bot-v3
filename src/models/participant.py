"""
Participant model matching Airtable schema specifications.

This model defines the structure for participant data as stored in Airtable,
including all field types: text, single select, number, and date fields.
"""

from datetime import date
from enum import Enum
from typing import Any, Mapping, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_validator


class Gender(str, Enum):
    """Gender options matching Airtable single select field."""

    MALE = "M"
    FEMALE = "F"


class Size(str, Enum):
    """Clothing size options matching Airtable single select field."""

    XS = "XS"
    S = "S"
    M = "M"
    L = "L"
    XL = "XL"
    XXL = "XXL"
    XXXL = "3XL"


class Role(str, Enum):
    """Participant role options matching Airtable single select field."""

    CANDIDATE = "CANDIDATE"
    TEAM = "TEAM"


class Department(str, Enum):
    """Department assignment options matching Airtable single select field."""

    ROE = "ROE"
    CHAPEL = "Chapel"
    SETUP = "Setup"
    PALANKA = "Palanka"
    ADMINISTRATION = "Administration"
    KITCHEN = "Kitchen"
    DECORATION = "Decoration"
    BELL = "Bell"
    REFRESHMENT = "Refreshment"
    WORSHIP = "Worship"
    MEDIA = "Media"
    CLERGY = "Clergy"
    RECTORATE = "Rectorate"


class PaymentStatus(str, Enum):
    """Payment status options matching Airtable single select field."""

    PAID = "Paid"
    PARTIAL = "Partial"
    UNPAID = "Unpaid"


class Participant(BaseModel):
    """
    Participant model matching Airtable schema with field validation.

    All field names match Airtable field names for direct API integration.
    Includes validation for required fields and data types.
    """

    # Required primary field
    full_name_ru: str = Field(
        ..., min_length=1, description="Full name in Russian (primary field, required)"
    )

    # Optional text fields
    full_name_en: Optional[str] = Field(None, description="Full name in English")

    church: Optional[str] = Field(None, description="Church affiliation")

    country_and_city: Optional[str] = Field(None, description="Location information")

    submitted_by: Optional[str] = Field(
        None, description="Person who submitted the record"
    )

    contact_information: Optional[str] = Field(None, description="Contact details")

    # Single select fields
    gender: Optional[Gender] = Field(None, description="Participant gender")

    size: Optional[Size] = Field(None, description="Clothing size")

    role: Optional[Role] = Field(None, description="Participant role/status")

    department: Optional[Department] = Field(None, description="Department assignment")

    payment_status: Optional[PaymentStatus] = Field(
        None, description="Payment tracking status"
    )

    # Number field
    payment_amount: Optional[int] = Field(
        None, ge=0, description="Amount paid (integer only)"
    )

    # Date field
    payment_date: Optional[date] = Field(None, description="Date of payment")

    # Accommodation fields
    # Floor is stored as a number in Airtable (but accept int or str input upstream)
    floor: Optional[Union[int, str]] = Field(
        None, description="Accommodation floor (numeric in Airtable)"
    )

    # Room number is stored as a number in Airtable, but allow alphanumeric input upstream
    room_number: Optional[Union[int, str]] = Field(
        None,
        description="Accommodation room number (numeric in Airtable; allow alphanumeric upstream)",
    )

    # Airtable record ID (for updates)
    record_id: Optional[str] = Field(
        None, description="Airtable record ID for existing records"
    )

    @field_validator("full_name_ru")
    @classmethod
    def validate_full_name_ru(cls, v: str) -> str:
        """Ensure primary field is not empty."""
        if not v or not v.strip():
            raise ValueError("Full name in Russian is required and cannot be empty")
        return v.strip()

    @field_validator("room_number")
    @classmethod
    def validate_room_number(
        cls, v: Optional[Union[int, str]]
    ) -> Optional[Union[int, str]]:
        """Normalize room number: empty string -> None; otherwise keep provided type (int or str)."""
        if v == "":
            return None
        return v

    def to_airtable_fields(self) -> dict[str, object]:
        """
        Convert participant data to Airtable API format.

        Returns dictionary with Airtable field names as keys.
        None values are excluded to avoid API errors.
        """
        fields: dict[str, object] = {}

        # Required field
        fields["FullNameRU"] = self.full_name_ru

        # Optional text fields
        if self.full_name_en:
            fields["FullNameEN"] = self.full_name_en
        if self.church:
            fields["Church"] = self.church
        if self.country_and_city:
            fields["CountryAndCity"] = self.country_and_city
        if self.submitted_by:
            fields["SubmittedBy"] = self.submitted_by
        if self.contact_information:
            fields["ContactInformation"] = self.contact_information

        # Single select fields (use enum values)
        if self.gender:
            fields["Gender"] = self.gender
        if self.size:
            fields["Size"] = self.size
        if self.role:
            fields["Role"] = self.role
        if self.department:
            fields["Department"] = self.department
        if self.payment_status:
            fields["PaymentStatus"] = self.payment_status

        # Number field
        if self.payment_amount is not None:
            fields["PaymentAmount"] = self.payment_amount

        # Date field (convert to ISO format for Airtable)
        if self.payment_date:
            fields["PaymentDate"] = self.payment_date.isoformat()

        # Accommodation fields (exact Airtable field names)
        if self.floor is not None:
            # Ensure numeric when possible; Airtable field is numeric
            fields["Floor"] = (
                int(self.floor)
                if isinstance(self.floor, str) and self.floor.isdigit()
                else self.floor
            )
        if self.room_number is not None:
            fields["RoomNumber"] = self.room_number

        return fields

    @classmethod
    def from_airtable_record(cls, record: Mapping[str, Any]) -> "Participant":
        """
        Create Participant instance from Airtable record.

        Args:
            record: Airtable record dictionary with 'id' and 'fields' keys

        Returns:
            Participant instance
        """
        fields = record.get("fields", {})

        # Convert date string to date object if present
        payment_date = None
        if fields.get("PaymentDate"):
            payment_date = date.fromisoformat(fields["PaymentDate"])

        # Ensure we have the required field
        full_name_ru = fields.get("FullNameRU", "")
        if not full_name_ru:
            raise ValueError("FullNameRU is required but missing from Airtable record")

        return cls(
            record_id=record.get("id"),
            full_name_ru=full_name_ru,
            full_name_en=fields.get("FullNameEN"),
            church=fields.get("Church"),
            country_and_city=fields.get("CountryAndCity"),
            submitted_by=fields.get("SubmittedBy"),
            contact_information=fields.get("ContactInformation"),
            gender=Gender(fields["Gender"]) if fields.get("Gender") else None,
            size=Size(fields["Size"]) if fields.get("Size") else None,
            role=Role(fields["Role"]) if fields.get("Role") else None,
            department=(
                Department(fields["Department"]) if fields.get("Department") else None
            ),
            payment_status=(
                PaymentStatus(fields["PaymentStatus"])
                if fields.get("PaymentStatus")
                else None
            ),
            payment_amount=fields.get("PaymentAmount"),
            payment_date=payment_date,
            floor=fields.get("Floor"),
            room_number=fields.get("RoomNumber"),
        )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)
