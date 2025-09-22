"""
Unit tests for Participant model.

Tests cover:
- Model validation and constraints
- Airtable field mapping conversion
- Record creation from Airtable data
- Field validation and error handling
- Enum value validation
"""

from datetime import date

import pytest
from pydantic import ValidationError

from src.models.participant import (
    Department,
    Gender,
    Participant,
    PaymentStatus,
    Role,
    Size,
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

    def test_new_fields_validation(self):
        """Test validation of new DateOfBirth and Age fields."""
        # Test valid DateOfBirth
        birth_date = date(1990, 5, 15)
        participant = Participant(full_name_ru="Test", date_of_birth=birth_date)
        assert participant.date_of_birth == birth_date

        # Test valid Age
        participant = Participant(full_name_ru="Test", age=25)
        assert participant.age == 25

        # Test Age constraints (should be >= 0)
        with pytest.raises(ValidationError) as exc_info:
            Participant(full_name_ru="Test", age=-1)
        assert "Input should be greater than or equal to 0" in str(exc_info.value)

        # Test Age as None (optional)
        participant = Participant(full_name_ru="Test", age=None)
        assert participant.age is None

        # Test DateOfBirth as None (optional)
        participant = Participant(full_name_ru="Test", date_of_birth=None)
        assert participant.date_of_birth is None


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
            date_of_birth=date(1990, 5, 15),
            age=35,
            church_leader="Пастор Иванов",
            table_name="Стол 1",
            notes="Специальные требования к питанию\nВегетарианская диета",
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
            "DateOfBirth": "15/5/1990",
            "Age": 35,
            "ChurchLeader": "Пастор Иванов",
            "TableName": "Стол 1",
            "Notes": "Специальные требования к питанию\nВегетарианская диета",
        }

        assert fields == expected

    def test_to_airtable_fields_excludes_none(self):
        """Test that None values are excluded from Airtable fields."""
        participant = Participant(
            full_name_ru="Test",
            full_name_en=None,
            payment_amount=None,
            gender=None,
            date_of_birth=None,
            age=None,
            church_leader=None,
            table_name=None,
            notes=None,
        )

        fields = participant.to_airtable_fields()

        assert fields == {"FullNameRU": "Test"}
        assert "FullNameEN" not in fields
        assert "PaymentAmount" not in fields
        assert "Gender" not in fields
        assert "Floor" not in fields
        assert "RoomNumber" not in fields
        assert "DateOfBirth" not in fields
        assert "Age" not in fields
        assert "ChurchLeader" not in fields
        assert "TableName" not in fields
        assert "Notes" not in fields

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

    def test_new_fields_serialization(self):
        """Test DateOfBirth and Age fields serialize correctly to Airtable format."""
        # Both fields present
        birth_date = date(1985, 12, 25)
        participant = Participant(
            full_name_ru="Test User", date_of_birth=birth_date, age=39
        )
        fields = participant.to_airtable_fields()
        assert fields["DateOfBirth"] == "25/12/1985"
        assert fields["Age"] == 39

        # Only DateOfBirth
        participant = Participant(
            full_name_ru="Test User", date_of_birth=birth_date, age=None
        )
        fields = participant.to_airtable_fields()
        assert fields["DateOfBirth"] == "25/12/1985"
        assert "Age" not in fields

        # Only Age
        participant = Participant(full_name_ru="Test User", date_of_birth=None, age=39)
        fields = participant.to_airtable_fields()
        assert fields["Age"] == 39
        assert "DateOfBirth" not in fields

        # Neither field set
        participant = Participant(
            full_name_ru="Test User", date_of_birth=None, age=None
        )
        fields = participant.to_airtable_fields()
        assert "DateOfBirth" not in fields
        assert "Age" not in fields

    def test_new_extended_fields_serialization(self):
        """Test ChurchLeader, TableName, and Notes fields serialize correctly to Airtable format."""
        # All three new fields present
        participant = Participant(
            full_name_ru="Test User",
            church_leader="Пастор Петров",
            table_name="Основной стол",
            notes="Важная информация:\n- Вегетарианец\n- Аллергия на орехи",
        )
        fields = participant.to_airtable_fields()
        assert fields["ChurchLeader"] == "Пастор Петров"
        assert fields["TableName"] == "Основной стол"
        assert (
            fields["Notes"] == "Важная информация:\n- Вегетарианец\n- Аллергия на орехи"
        )

        # Only ChurchLeader
        participant = Participant(
            full_name_ru="Test User",
            church_leader="Дьякон Иванов",
            table_name=None,
            notes=None,
        )
        fields = participant.to_airtable_fields()
        assert fields["ChurchLeader"] == "Дьякон Иванов"
        assert "TableName" not in fields
        assert "Notes" not in fields

        # Only TableName
        participant = Participant(
            full_name_ru="Test User",
            church_leader=None,
            table_name="Стол молодежи",
            notes=None,
        )
        fields = participant.to_airtable_fields()
        assert fields["TableName"] == "Стол молодежи"
        assert "ChurchLeader" not in fields
        assert "Notes" not in fields

        # Only Notes with multiline content
        participant = Participant(
            full_name_ru="Test User",
            church_leader=None,
            table_name=None,
            notes="Строка 1\nСтрока 2\nСтрока 3",
        )
        fields = participant.to_airtable_fields()
        assert fields["Notes"] == "Строка 1\nСтрока 2\nСтрока 3"
        assert "ChurchLeader" not in fields
        assert "TableName" not in fields

        # Empty strings should not be serialized
        participant = Participant(
            full_name_ru="Test User",
            church_leader="",
            table_name="",
            notes="",
        )
        fields = participant.to_airtable_fields()
        assert "ChurchLeader" not in fields
        assert "TableName" not in fields
        assert "Notes" not in fields


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
                "DateOfBirth": "15/5/1990",
                "Age": 35,
                "ChurchLeader": "Протоиерей Сидоров",
                "TableName": "Почетный стол",
                "Notes": "Особые потребности:\n- Wheelchair accessible\n- Диетические ограничения",
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
        assert participant.date_of_birth == date(1990, 5, 15)
        assert participant.age == 35
        assert participant.church_leader == "Протоиерей Сидоров"
        assert participant.table_name == "Почетный стол"
        assert (
            participant.notes
            == "Особые потребности:\n- Wheelchair accessible\n- Диетические ограничения"
        )

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

    def test_new_fields_deserialization(self):
        """Test DateOfBirth and Age fields deserialize correctly from Airtable records."""
        # Both fields present
        record = {
            "id": "rec123456789",
            "fields": {
                "FullNameRU": "Test User",
                "DateOfBirth": "25/12/1985",
                "Age": 39,
            },
        }
        participant = Participant.from_airtable_record(record)
        assert participant.date_of_birth == date(1985, 12, 25)
        assert participant.age == 39

        # Only DateOfBirth present
        record = {
            "id": "rec987654321",
            "fields": {"FullNameRU": "Test User 2", "DateOfBirth": "1990-06-15"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.date_of_birth == date(1990, 6, 15)
        assert participant.age is None

        # Only Age present
        record = {
            "id": "rec555666777",
            "fields": {"FullNameRU": "Test User 3", "Age": 25},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.age == 25
        assert participant.date_of_birth is None

        # Neither field present (should be None)
        record = {"id": "rec111111111", "fields": {"FullNameRU": "Test User 4"}}
        participant = Participant.from_airtable_record(record)
        assert participant.date_of_birth is None
        assert participant.age is None

    def test_new_extended_fields_deserialization(self):
        """Test ChurchLeader, TableName, and Notes fields deserialize correctly from Airtable records."""
        # All three extended fields present
        record = {
            "id": "rec123456789",
            "fields": {
                "FullNameRU": "Test User",
                "ChurchLeader": "Архимандрит Георгий",
                "TableName": "VIP стол",
                "Notes": "Многострочные заметки:\n1. Первый пункт\n2. Второй пункт\n3. Третий пункт",
            },
        }
        participant = Participant.from_airtable_record(record)
        assert participant.church_leader == "Архимандрит Георгий"
        assert participant.table_name == "VIP стол"
        assert (
            participant.notes
            == "Многострочные заметки:\n1. Первый пункт\n2. Второй пункт\n3. Третий пункт"
        )

        # Only ChurchLeader present
        record = {
            "id": "rec987654321",
            "fields": {"FullNameRU": "Test User 2", "ChurchLeader": "Диакон Алексей"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.church_leader == "Диакон Алексей"
        assert participant.table_name is None
        assert participant.notes is None

        # Only TableName present
        record = {
            "id": "rec555666777",
            "fields": {"FullNameRU": "Test User 3", "TableName": "Детский стол"},
        }
        participant = Participant.from_airtable_record(record)
        assert participant.table_name == "Детский стол"
        assert participant.church_leader is None
        assert participant.notes is None

        # Only Notes present (with special characters and formatting)
        record = {
            "id": "rec111222333",
            "fields": {
                "FullNameRU": "Test User 4",
                "Notes": "Special chars: !@#$%^&*()_+\nТекст на русском\nEmoji: 🙏✝️",
            },
        }
        participant = Participant.from_airtable_record(record)
        assert (
            participant.notes
            == "Special chars: !@#$%^&*()_+\nТекст на русском\nEmoji: 🙏✝️"
        )
        assert participant.church_leader is None
        assert participant.table_name is None

        # None of the extended fields present (should be None)
        record = {"id": "rec999888777", "fields": {"FullNameRU": "Test User 5"}}
        participant = Participant.from_airtable_record(record)
        assert participant.church_leader is None
        assert participant.table_name is None
        assert participant.notes is None


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
            date_of_birth=date(1985, 3, 10),
            age=40,
            church_leader="Епископ Николай",
            table_name="Главный стол",
            notes="Тестовые заметки\nВторая строка\nТретья строка",
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
        assert restored.date_of_birth == original.date_of_birth
        assert restored.age == original.age
        assert restored.church_leader == original.church_leader
        assert restored.table_name == original.table_name
        assert restored.notes == original.notes
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

    def test_roundtrip_conversion_new_fields_only(self):
        """Test roundtrip conversion with only DateOfBirth and Age fields set."""
        original = Participant(
            full_name_ru="Test User", date_of_birth=date(1992, 8, 20), age=32
        )

        # Convert to Airtable format
        airtable_fields = original.to_airtable_fields()

        # Verify Airtable format includes new fields
        assert airtable_fields["DateOfBirth"] == "1992-08-20"
        assert airtable_fields["Age"] == 32

        # Create mock Airtable record
        airtable_record = {"id": "rec123456789", "fields": airtable_fields}

        # Convert back to participant
        restored = Participant.from_airtable_record(airtable_record)

        # Verify new field data integrity
        assert restored.full_name_ru == original.full_name_ru
        assert restored.date_of_birth == original.date_of_birth
        assert restored.age == original.age
        assert restored.record_id == "rec123456789"

    def test_roundtrip_conversion_extended_fields_only(self):
        """Test roundtrip conversion with only ChurchLeader, TableName, and Notes fields set."""
        original = Participant(
            full_name_ru="Test User",
            church_leader="Митрополит Владимир",
            table_name="Духовенство",
            notes="Многострочный текст:\n- Пункт 1\n- Пункт 2\n- Особые требования",
        )

        # Convert to Airtable format
        airtable_fields = original.to_airtable_fields()

        # Verify Airtable format includes extended fields
        assert airtable_fields["ChurchLeader"] == "Митрополит Владимир"
        assert airtable_fields["TableName"] == "Духовенство"
        assert (
            airtable_fields["Notes"]
            == "Многострочный текст:\n- Пункт 1\n- Пункт 2\n- Особые требования"
        )

        # Create mock Airtable record
        airtable_record = {"id": "rec123456789", "fields": airtable_fields}

        # Convert back to participant
        restored = Participant.from_airtable_record(airtable_record)

        # Verify extended field data integrity
        assert restored.full_name_ru == original.full_name_ru
        assert restored.church_leader == original.church_leader
        assert restored.table_name == original.table_name
        assert restored.notes == original.notes
        assert restored.record_id == "rec123456789"


class TestParticipantDepartmentChiefField:
    """Test suite for the IsDepartmentChief field extension."""

    def test_participant_model_chief_field(self):
        """Verify IsDepartmentChief field exists with correct type."""
        # Test creation with chief field set to True
        participant = Participant(
            full_name_ru="Александр Басис", is_department_chief=True
        )
        assert participant.is_department_chief is True

        # Test creation with chief field set to False
        participant2 = Participant(
            full_name_ru="Иван Иванов", is_department_chief=False
        )
        assert participant2.is_department_chief is False

        # Test creation with chief field set to None (default)
        participant3 = Participant(full_name_ru="Петр Петров")
        assert participant3.is_department_chief is None

    def test_chief_field_serialization(self):
        """Validate chief status preserved during model serialization."""
        # Test with True value
        participant = Participant(
            full_name_ru="Александр Басис", is_department_chief=True
        )
        airtable_fields = participant.to_airtable_fields()
        assert "IsDepartmentChief" in airtable_fields
        assert airtable_fields["IsDepartmentChief"] is True

        # Test with False value
        participant2 = Participant(
            full_name_ru="Иван Иванов", is_department_chief=False
        )
        airtable_fields2 = participant2.to_airtable_fields()
        assert "IsDepartmentChief" in airtable_fields2
        assert airtable_fields2["IsDepartmentChief"] is False

        # Test with None value (should not be in output)
        participant3 = Participant(full_name_ru="Петр Петров", is_department_chief=None)
        airtable_fields3 = participant3.to_airtable_fields()
        assert "IsDepartmentChief" not in airtable_fields3

    def test_chief_field_deserialization(self):
        """Confirm chief status correctly loaded from Airtable data."""
        # Test with True value
        record_true = {
            "id": "rec123456789",
            "fields": {"FullNameRU": "Александр Басис", "IsDepartmentChief": True},
        }
        participant = Participant.from_airtable_record(record_true)
        assert participant.is_department_chief is True

        # Test with False value
        record_false = {
            "id": "rec987654321",
            "fields": {"FullNameRU": "Иван Иванов", "IsDepartmentChief": False},
        }
        participant2 = Participant.from_airtable_record(record_false)
        assert participant2.is_department_chief is False

        # Test with missing field (should default to None)
        record_none = {"id": "rec111111111", "fields": {"FullNameRU": "Петр Петров"}}
        participant3 = Participant.from_airtable_record(record_none)
        assert participant3.is_department_chief is None

    def test_model_backward_compatibility(self):
        """Ensure existing model functionality unaffected."""
        # Create a participant with existing fields but without chief field
        participant = Participant(
            full_name_ru="Александр Басис",
            full_name_en="Alexandr Basis",
            church="Грейс",
            department=Department.ADMINISTRATION,
            role=Role.TEAM,
        )

        # Verify existing fields work as before
        assert participant.full_name_ru == "Александр Басис"
        assert participant.full_name_en == "Alexandr Basis"
        assert participant.church == "Грейс"
        assert participant.department == Department.ADMINISTRATION
        assert participant.role == Role.TEAM

        # Verify chief field defaults to None when not specified
        assert participant.is_department_chief is None

        # Verify serialization doesn't include None chief field
        airtable_fields = participant.to_airtable_fields()
        assert "IsDepartmentChief" not in airtable_fields
        assert "FullNameRU" in airtable_fields
        assert "Department" in airtable_fields

    def test_boolean_validation(self):
        """Validate model handles true/false/None values for chief field."""
        # Test with explicit boolean values
        participant_true = Participant(
            full_name_ru="Chief True", is_department_chief=True
        )
        assert participant_true.is_department_chief is True

        participant_false = Participant(
            full_name_ru="Chief False", is_department_chief=False
        )
        assert participant_false.is_department_chief is False

        # Test with None value
        participant_none = Participant(
            full_name_ru="Chief None", is_department_chief=None
        )
        assert participant_none.is_department_chief is None

        # Test with no value provided (should default to None)
        participant_default = Participant(full_name_ru="Chief Default")
        assert participant_default.is_department_chief is None

    def test_invalid_chief_field_value(self):
        """Handle non-boolean values in IsDepartmentChief field."""
        # Pydantic converts truthy values to boolean, so test with invalid type that can't be converted
        with pytest.raises(ValidationError) as exc_info:
            Participant(
                full_name_ru="Test User",
                is_department_chief={
                    "invalid": "dict"
                },  # Dict cannot be converted to bool
            )
        assert "is_department_chief" in str(exc_info.value).lower()

        # Test that truthy values are converted (Pydantic behavior)
        participant_str = Participant(
            full_name_ru="Test User",
            is_department_chief="yes",  # String converts to True
        )
        assert participant_str.is_department_chief is True

        participant_int = Participant(
            full_name_ru="Test User",
            is_department_chief=1,  # Integer 1 converts to True
        )
        assert participant_int.is_department_chief is True

        participant_zero = Participant(
            full_name_ru="Test User",
            is_department_chief=0,  # Integer 0 converts to False
        )
        assert participant_zero.is_department_chief is False
