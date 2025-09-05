"""
Unit tests for Participant model.

Tests cover:
- Model validation and constraints
- Airtable field mapping conversion
- Record creation from Airtable data
- Field validation and error handling
- Enum value validation
"""

import pytest
from datetime import date
from pydantic import ValidationError

from src.models.participant import (
    Participant,
    Gender,
    Size,
    Role,
    Department,
    PaymentStatus,
)


class TestParticipantModel:
    """Test suite for Participant model basic functionality."""

    def test_participant_creation_minimal_data(self):
        """Test creating participant with only required field."""
        participant = Participant(full_name_ru="Александр Басис")

        assert participant.full_name_ru == "Александр Басис"
        assert participant.full_name_en is None
        assert participant.gender is None
        assert participant.payment_amount is None

    def test_participant_creation_full_data(self):
        """Test creating participant with all fields populated."""
        payment_date = date(2025, 8, 27)

        participant = Participant(
            full_name_ru="Александр Басис",
            full_name_en="Alexandr Basis",
            church="Грейс",
            country_and_city="Москва, Россия",
            submitted_by="Admin",
            contact_information="+7 (999) 123-45-67",
            gender=Gender.MALE,
            size=Size.L,
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            payment_status=PaymentStatus.PAID,
            payment_amount=5000,
            payment_date=payment_date,
            record_id="rec123456789",
        )

        assert participant.full_name_ru == "Александр Басис"
        assert participant.full_name_en == "Alexandr Basis"
        assert participant.church == "Грейс"
        assert participant.country_and_city == "Москва, Россия"
        assert participant.submitted_by == "Admin"
        assert participant.contact_information == "+7 (999) 123-45-67"
        assert participant.gender == Gender.MALE
        assert participant.size == Size.L
        assert participant.role == Role.TEAM
        assert participant.department == Department.ADMINISTRATION
        assert participant.payment_status == PaymentStatus.PAID
        assert participant.payment_amount == 5000
        assert participant.payment_date == payment_date
        assert participant.record_id == "rec123456789"

    def test_full_name_ru_required(self):
        """Test that full_name_ru is required."""
        with pytest.raises(ValidationError) as exc_info:
            Participant()

        assert "full_name_ru" in str(exc_info.value)
        assert "Field required" in str(exc_info.value)

    def test_full_name_ru_cannot_be_empty(self):
        """Test that full_name_ru cannot be empty or whitespace."""
        with pytest.raises(ValidationError) as exc_info:
            Participant(full_name_ru="")

        assert "String should have at least 1 character" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            Participant(full_name_ru="   ")

        assert "cannot be empty" in str(exc_info.value)

    def test_full_name_ru_whitespace_trimmed(self):
        """Test that full_name_ru whitespace is trimmed."""
        participant = Participant(full_name_ru="  Александр Басис  ")

        assert participant.full_name_ru == "Александр Басис"


class TestParticipantEnums:
    """Test suite for enum field validation."""

    def test_gender_enum_values(self):
        """Test gender enum accepts valid values."""
        participant = Participant(full_name_ru="Test", gender=Gender.MALE)
        assert participant.gender == Gender.MALE

        participant = Participant(full_name_ru="Test", gender=Gender.FEMALE)
        assert participant.gender == Gender.FEMALE

    def test_size_enum_values(self):
        """Test size enum accepts all valid values."""
        sizes = [Size.XS, Size.S, Size.M, Size.L, Size.XL, Size.XXL, Size.XXXL]

        for size in sizes:
            participant = Participant(full_name_ru="Test", size=size)
            assert participant.size == size

    def test_role_enum_values(self):
        """Test role enum accepts valid values."""
        participant = Participant(full_name_ru="Test", role=Role.CANDIDATE)
        assert participant.role == Role.CANDIDATE

        participant = Participant(full_name_ru="Test", role=Role.TEAM)
        assert participant.role == Role.TEAM

    def test_department_enum_values(self):
        """Test department enum accepts all valid values."""
        departments = [
            Department.ROE,
            Department.CHAPEL,
            Department.SETUP,
            Department.PALANKA,
            Department.ADMINISTRATION,
            Department.KITCHEN,
            Department.DECORATION,
            Department.BELL,
            Department.REFRESHMENT,
            Department.WORSHIP,
            Department.MEDIA,
            Department.CLERGY,
            Department.RECTORATE,
        ]

        for dept in departments:
            participant = Participant(full_name_ru="Test", department=dept)
            assert participant.department == dept

    def test_payment_status_enum_values(self):
        """Test payment status enum accepts valid values."""
        statuses = [PaymentStatus.PAID, PaymentStatus.PARTIAL, PaymentStatus.UNPAID]

        for status in statuses:
            participant = Participant(full_name_ru="Test", payment_status=status)
            assert participant.payment_status == status


class TestParticipantValidation:
    """Test suite for field validation logic."""

    def test_payment_amount_non_negative(self):
        """Test payment amount must be non-negative."""
        # Valid amounts
        participant = Participant(full_name_ru="Test", payment_amount=0)
        assert participant.payment_amount == 0

        participant = Participant(full_name_ru="Test", payment_amount=5000)
        assert participant.payment_amount == 5000

        # Invalid negative amount
        with pytest.raises(ValidationError) as exc_info:
            Participant(full_name_ru="Test", payment_amount=-100)

        assert "Input should be greater than or equal to 0" in str(exc_info.value)

    def test_payment_amount_integer_only(self):
        """Test payment amount validates as integer."""
        with pytest.raises(ValidationError):
            Participant(full_name_ru="Test", payment_amount="not_a_number")

    def test_payment_date_validation(self):
        """Test payment date accepts valid date objects."""
        valid_date = date(2025, 8, 27)
        participant = Participant(full_name_ru="Test", payment_date=valid_date)

        assert participant.payment_date == valid_date

    def test_floor_field_validation(self):
        """Test floor field accepts valid integer/string values and handles empty/null cases."""
        # Valid integer floor
        participant = Participant(full_name_ru="Test", floor=3)
        assert participant.floor == 3

        # Valid string floor (e.g., "Ground", "Basement")
        participant = Participant(full_name_ru="Test", floor="Ground")
        assert participant.floor == "Ground"

        # Valid None/null floor
        participant = Participant(full_name_ru="Test", floor=None)
        assert participant.floor is None

    def test_room_number_field_validation(self):
        """Test room number field accepts alphanumeric values and handles empty/null cases."""
        # Valid numeric room number
        participant = Participant(full_name_ru="Test", room_number="101")
        assert participant.room_number == "101"

        # Valid alphanumeric room number
        participant = Participant(full_name_ru="Test", room_number="A12B")
        assert participant.room_number == "A12B"

        # Valid None/null room number
        participant = Participant(full_name_ru="Test", room_number=None)
        assert participant.room_number is None

        # Empty string should be None
        participant = Participant(full_name_ru="Test", room_number="")
        assert participant.room_number is None


class TestAirtableFieldMapping:
    """Test suite for Airtable API field mapping."""

    def test_to_airtable_fields_minimal(self):
        """Test conversion to Airtable format with minimal data."""
        participant = Participant(full_name_ru="Александр Басис")
        fields = participant.to_airtable_fields()

        assert fields == {"FullNameRU": "Александр Басис"}

    def test_to_airtable_fields_full(self):
        """Test conversion to Airtable format with all fields."""
        payment_date = date(2025, 8, 27)

        participant = Participant(
            full_name_ru="Александр Басис",
            full_name_en="Alexandr Basis",
            church="Грейс",
            country_and_city="Москва, Россия",
            submitted_by="Admin",
            contact_information="+7 (999) 123-45-67",
            gender=Gender.MALE,
            size=Size.L,
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            payment_status=PaymentStatus.PAID,
            payment_amount=5000,
            payment_date=payment_date,
            floor=3,
            room_number="101A",
        )

        fields = participant.to_airtable_fields()

        expected = {
            "FullNameRU": "Александр Басис",
            "FullNameEN": "Alexandr Basis",
            "Church": "Грейс",
            "CountryAndCity": "Москва, Россия",
            "SubmittedBy": "Admin",
            "ContactInformation": "+7 (999) 123-45-67",
            "Gender": "M",
            "Size": "L",
            "Role": "TEAM",
            "Department": "Administration",
            "PaymentStatus": "Paid",
            "PaymentAmount": 5000,
            "PaymentDate": "2025-08-27",
            "Floor": 3,
            "RoomNumber": "101A",
        }

        assert fields == expected

    def test_to_airtable_fields_excludes_none(self):
        """Test that None values are excluded from Airtable fields."""
        participant = Participant(
            full_name_ru="Test", full_name_en=None, payment_amount=None, gender=None
        )

        fields = participant.to_airtable_fields()

        assert fields == {"FullNameRU": "Test"}
        assert "FullNameEN" not in fields
        assert "PaymentAmount" not in fields
        assert "Gender" not in fields
        assert "Floor" not in fields
        assert "RoomNumber" not in fields

    def test_accommodation_fields_serialization(self):
        """Test Floor and Room Number fields serialize correctly to Airtable format."""
        # Integer floor with room number
        participant = Participant(full_name_ru="Test User", floor=2, room_number="201")
        fields = participant.to_airtable_fields()
        assert fields["Floor"] == 2
        assert fields["RoomNumber"] == "201"

        # String floor with alphanumeric room number
        participant = Participant(
            full_name_ru="Test User", floor="Ground", room_number="A12B"
        )
        fields = participant.to_airtable_fields()
        assert fields["Floor"] == "Ground"
        assert fields["RoomNumber"] == "A12B"

        # Only floor set
        participant = Participant(full_name_ru="Test User", floor=3, room_number=None)
        fields = participant.to_airtable_fields()
        assert fields["Floor"] == 3
        assert "RoomNumber" not in fields

        # Only room number set
        participant = Participant(
            full_name_ru="Test User", floor=None, room_number="Suite 100"
        )
        fields = participant.to_airtable_fields()
        assert fields["RoomNumber"] == "Suite 100"
        assert "Floor" not in fields


class TestAirtableRecordCreation:
    """Test suite for creating participant from Airtable records."""

    def test_from_airtable_record_minimal(self):
        """Test creating participant from minimal Airtable record."""
        record = {"id": "rec123456789", "fields": {"FullNameRU": "Александр Басис"}}

        participant = Participant.from_airtable_record(record)

        assert participant.record_id == "rec123456789"
        assert participant.full_name_ru == "Александр Басис"
        assert participant.full_name_en is None
        assert participant.gender is None

    def test_from_airtable_record_full(self):
        """Test creating participant from full Airtable record."""
        record = {
            "id": "rec123456789",
            "fields": {
                "FullNameRU": "Александр Басис",
                "FullNameEN": "Alexandr Basis",
                "Church": "Грейс",
                "CountryAndCity": "Москва, Россия",
                "SubmittedBy": "Admin",
                "ContactInformation": "+7 (999) 123-45-67",
                "Gender": "M",
                "Size": "L",
                "Role": "TEAM",
                "Department": "Administration",
                "PaymentStatus": "Paid",
                "PaymentAmount": 5000,
                "PaymentDate": "2025-08-27",
                "Floor": 3,
                "RoomNumber": "301A",
            },
        }

        participant = Participant.from_airtable_record(record)

        assert participant.record_id == "rec123456789"
        assert participant.full_name_ru == "Александр Басис"
        assert participant.full_name_en == "Alexandr Basis"
        assert participant.church == "Грейс"
        assert participant.country_and_city == "Москва, Россия"
        assert participant.submitted_by == "Admin"
        assert participant.contact_information == "+7 (999) 123-45-67"
        assert participant.gender == Gender.MALE
        assert participant.size == Size.L
        assert participant.role == Role.TEAM
        assert participant.department == Department.ADMINISTRATION
        assert participant.payment_status == PaymentStatus.PAID
        assert participant.payment_amount == 5000
        assert participant.payment_date == date(2025, 8, 27)
        assert participant.floor == 3
        assert participant.room_number == "301A"

    def test_from_airtable_record_missing_fields(self):
        """Test handling of Airtable records with missing required fields."""
        record = {"id": "rec123456789", "fields": {}}

        with pytest.raises(ValueError) as exc_info:
            Participant.from_airtable_record(record)

        assert "FullNameRU is required but missing" in str(exc_info.value)

    def test_from_airtable_record_enum_conversion(self):
        """Test proper enum conversion from Airtable record."""
        record = {
            "id": "rec123456789",
            "fields": {
                "FullNameRU": "Test",
                "Gender": "F",
                "Size": "XS",
                "Role": "CANDIDATE",
                "Department": "Chapel",
                "PaymentStatus": "Partial",
            },
        }

        participant = Participant.from_airtable_record(record)

        assert participant.gender == Gender.FEMALE
        assert participant.size == Size.XS
        assert participant.role == Role.CANDIDATE
        assert participant.department == Department.CHAPEL
        assert participant.payment_status == PaymentStatus.PARTIAL

    def test_accommodation_fields_deserialization(self):
        """Test Floor and Room Number fields deserialize correctly from Airtable records."""
        # Integer floor with room number
        record = {
            "id": "rec123456789",
            "fields": {"FullNameRU": "Test User", "Floor": 2, "RoomNumber": "201"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.floor == 2
        assert participant.room_number == "201"

        # String floor with alphanumeric room number
        record = {
            "id": "rec987654321",
            "fields": {
                "FullNameRU": "Test User 2",
                "Floor": "Ground",
                "RoomNumber": "A12B",
            },
        }
        participant = Participant.from_airtable_record(record)
        assert participant.floor == "Ground"
        assert participant.room_number == "A12B"

        # Missing accommodation fields (should be None)
        record = {"id": "rec111111111", "fields": {"FullNameRU": "Test User 3"}}
        participant = Participant.from_airtable_record(record)
        assert participant.floor is None
        assert participant.room_number is None

        # Only floor present
        record = {
            "id": "rec222222222",
            "fields": {"FullNameRU": "Test User 4", "Floor": "Basement"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.floor == "Basement"
        assert participant.room_number is None

        # Only room number present
        record = {
            "id": "rec333333333",
            "fields": {"FullNameRU": "Test User 5", "RoomNumber": "Suite 100"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.floor is None
        assert participant.room_number == "Suite 100"


class TestParticipantRoundtrip:
    """Test suite for roundtrip conversions (model -> Airtable -> model)."""

    def test_roundtrip_conversion(self):
        """Test that data survives roundtrip conversion."""
        original = Participant(
            full_name_ru="Александр Басис",
            full_name_en="Alexandr Basis",
            gender=Gender.MALE,
            size=Size.L,
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            payment_status=PaymentStatus.PAID,
            payment_amount=5000,
            payment_date=date(2025, 8, 27),
            floor=3,
            room_number="301A",
        )

        # Convert to Airtable format
        airtable_fields = original.to_airtable_fields()

        # Create mock Airtable record
        airtable_record = {"id": "rec123456789", "fields": airtable_fields}

        # Convert back to participant
        restored = Participant.from_airtable_record(airtable_record)

        # Verify data integrity (excluding record_id which is new)
        assert restored.full_name_ru == original.full_name_ru
        assert restored.full_name_en == original.full_name_en
        assert restored.gender == original.gender
        assert restored.size == original.size
        assert restored.role == original.role
        assert restored.department == original.department
        assert restored.payment_status == original.payment_status
        assert restored.payment_amount == original.payment_amount
        assert restored.payment_date == original.payment_date
        assert restored.floor == original.floor
        assert restored.room_number == original.room_number
        assert restored.record_id == "rec123456789"

    def test_roundtrip_conversion_accommodation_fields_only(self):
        """Test roundtrip conversion with only accommodation fields set."""
        original = Participant(
            full_name_ru="Test User", floor="Ground", room_number="A1"
        )

        # Convert to Airtable format
        airtable_fields = original.to_airtable_fields()

        # Verify Airtable format includes accommodation fields
        assert airtable_fields["Floor"] == "Ground"
        assert airtable_fields["RoomNumber"] == "A1"

        # Create mock Airtable record
        airtable_record = {"id": "rec123456789", "fields": airtable_fields}

        # Convert back to participant
        restored = Participant.from_airtable_record(airtable_record)

        # Verify accommodation data integrity
        assert restored.full_name_ru == original.full_name_ru
        assert restored.floor == original.floor
        assert restored.room_number == original.room_number
        assert restored.record_id == "rec123456789"
