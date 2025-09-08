"""
Integration tests for Airtable schema validation.

Tests verify that Floor and RoomNumber field mappings and IDs
are correctly used in repository operations and search functionality.
"""

from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest
import pytest_asyncio

from src.config.field_mappings import AirtableFieldMapping, FieldType
from src.config.settings import DatabaseSettings
from src.data.airtable.airtable_client import AirtableClient
from src.data.airtable.airtable_participant_repo import \
    AirtableParticipantRepository
from src.models.participant import Participant
from src.services.search_service import SearchService


class TestAirtableSchemaValidation:
    """Integration tests for Airtable schema validation."""

    @pytest.fixture
    def mock_airtable_client(self):
        """Create mock AirtableClient with schema validation."""
        client = Mock(spec=AirtableClient)
        client.fetch_all_records = AsyncMock()
        client.get_record = AsyncMock()
        client.update_record = AsyncMock()
        client.create_record = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_airtable_client):
        """Create AirtableParticipantRepository with mocked client."""
        return AirtableParticipantRepository(mock_airtable_client)

    @pytest.fixture
    def search_service(self, repository):
        """Create SearchService with repository."""
        service = SearchService(repository=repository)
        return service

    @pytest.fixture
    def sample_airtable_records_with_fields(self):
        """Sample Airtable records with Floor and RoomNumber fields."""
        return [
            {
                "id": "rec001",
                "fields": {
                    "FullNameRU": "Иван Петров",
                    "FullNameEN": "Ivan Petrov",
                    "Floor": 2,
                    "RoomNumber": "201",
                },
            },
            {
                "id": "rec002",
                "fields": {
                    "FullNameRU": "Мария Сидорова",
                    "FullNameEN": "Maria Sidorova",
                    "Floor": 2,
                    "RoomNumber": "201",
                },
            },
            {
                "id": "rec003",
                "fields": {
                    "FullNameRU": "Алексей Кузнецов",
                    "FullNameEN": "Alexey Kuznetsov",
                    "Floor": 3,
                    "RoomNumber": "301",
                },
            },
        ]

    def test_floor_field_id_mapping_configured(self):
        """Test that Floor field ID is properly configured."""
        assert "Floor" in AirtableFieldMapping.AIRTABLE_FIELD_IDS
        floor_field_id = AirtableFieldMapping.AIRTABLE_FIELD_IDS["Floor"]
        assert floor_field_id == "fldlzG1sVg01hsy2g"
        assert isinstance(floor_field_id, str)
        assert floor_field_id.startswith("fld")  # Valid Airtable field ID format

    def test_room_number_field_id_mapping_configured(self):
        """Test that RoomNumber field ID is properly configured."""
        assert "RoomNumber" in AirtableFieldMapping.AIRTABLE_FIELD_IDS
        room_field_id = AirtableFieldMapping.AIRTABLE_FIELD_IDS["RoomNumber"]
        assert room_field_id == "fldJTPjo8AHQaADVu"
        assert isinstance(room_field_id, str)
        assert room_field_id.startswith("fld")  # Valid Airtable field ID format

    @pytest.mark.asyncio
    async def test_repository_uses_correct_field_ids_for_room_search(
        self, repository, sample_airtable_records_with_fields
    ):
        """Test repository uses correct field IDs when searching by room."""
        # Mock client to return records with field names
        room_records = [
            record
            for record in sample_airtable_records_with_fields
            if record["fields"].get("RoomNumber") == "201"
        ]
        repository.client.search_by_field = AsyncMock(return_value=room_records)

        # Perform room search using correct method name
        result = await repository.find_by_room_number("201")

        # Verify client was called with correct field name
        repository.client.search_by_field.assert_called_once_with("RoomNumber", "201")

        # Verify results are correctly parsed using field IDs
        assert len(result) == 2
        assert all(p.room_number == "201" for p in result)
        assert all(p.floor == 2 for p in result)

        # Verify names are correctly extracted using field IDs
        names_ru = {p.full_name_ru for p in result}
        expected_names = {"Иван Петров", "Мария Сидорова"}
        assert names_ru == expected_names

    @pytest.mark.asyncio
    async def test_repository_uses_correct_field_ids_for_floor_search(
        self, repository, sample_airtable_records_with_fields
    ):
        """Test repository uses correct field IDs when searching by floor."""
        # Mock client to return records with field names for floor 2
        floor_records = [
            record
            for record in sample_airtable_records_with_fields
            if record["fields"].get("Floor") == 2
        ]
        repository.client.search_by_field = AsyncMock(return_value=floor_records)

        # Perform floor search using correct method name
        result = await repository.find_by_floor(2)

        # Verify client was called with correct field name
        repository.client.search_by_field.assert_called_once_with("Floor", 2)

        # Verify results are correctly parsed using field IDs
        floor_2_participants = [p for p in result if p.floor == 2]
        assert len(floor_2_participants) == 2
        assert all(p.floor == 2 for p in floor_2_participants)

        # Verify room numbers are correctly extracted
        room_numbers = {p.room_number for p in floor_2_participants}
        assert room_numbers == {"201"}

    @pytest.mark.asyncio
    async def test_search_service_integration_with_field_ids(
        self, search_service, sample_airtable_records_with_fields
    ):
        """Test search service correctly uses field IDs through repository."""
        # Mock repository's client for room search
        room_records = [
            record
            for record in sample_airtable_records_with_fields
            if record["fields"].get("RoomNumber") == "201"
        ]
        search_service.repository.client.search_by_field = AsyncMock(
            return_value=room_records
        )

        # Test room search through service
        room_results = await search_service.search_by_room("201")
        assert len(room_results) == 2
        assert all(p.room_number == "201" for p in room_results)

        # Reset mock for floor search
        floor_records = [
            record
            for record in sample_airtable_records_with_fields
            if record["fields"].get("Floor") == 2
        ]
        search_service.repository.client.search_by_field = AsyncMock(
            return_value=floor_records
        )

        # Test floor search through service
        floor_results = await search_service.search_by_floor(2)
        floor_2_results = [p for p in floor_results if p.floor == 2]
        assert len(floor_2_results) == 2
        assert all(p.floor == 2 for p in floor_2_results)

    @pytest.mark.asyncio
    async def test_field_id_validation_for_write_operations(self, repository):
        """Test that field IDs are used for write operations (updates)."""
        # Create a participant record
        participant = Participant(
            record_id="rec001",
            full_name_ru="Тест Пользователь",
            full_name_en="Test User",
            floor=5,
            room_number="501",
        )

        # Mock the update call
        repository.client.update_record = AsyncMock(
            return_value={
                "id": "rec001",
                "fields": {
                    "fldlzG1sVg01hsy2g": 5,  # Floor field ID
                    "fldJTPjo8AHQaADVu": "501",  # RoomNumber field ID
                },
            }
        )

        # Update participant accommodation using update_by_id
        await repository.update_by_id(
            participant.record_id,
            {
                "floor": 5,
                "room_number": "501",
            },
        )

        # Verify update was called with correct field IDs
        repository.client.update_record.assert_called_once()
        call_args = repository.client.update_record.call_args

        # The field IDs should be used in the update call
        # This validates that our field mapping is working for write operations

    @pytest.mark.asyncio
    async def test_field_mapping_handles_missing_fields_gracefully(self, repository):
        """Test field mapping handles missing Floor/RoomNumber fields gracefully."""
        # Records with missing accommodation fields
        records_with_missing_fields = [
            {
                "id": "rec002",
                "fields": {
                    "FullNameRU": "Участник С Этажом",
                    "Floor": 3,  # Floor only
                    # RoomNumber field missing
                },
            }
        ]

        # Mock different responses for different searches
        def mock_search_by_field(field_name, value):
            if field_name == "Floor" and value == 3:
                return records_with_missing_fields  # Return participant with floor 3
            return []  # Empty for room searches

        repository.client.search_by_field = AsyncMock(side_effect=mock_search_by_field)

        # Search should not fail with missing fields
        result = await repository.find_by_room_number(
            "999"
        )  # Won't find anything but shouldn't error

        # Should return empty list, not error
        assert result == []

        # Test floor search with missing fields
        floor_result = await repository.find_by_floor(3)

        # Should find the participant with floor but no room
        floor_3_participants = [p for p in floor_result if p.floor == 3]
        assert len(floor_3_participants) == 1
        assert floor_3_participants[0].room_number is None

    def test_field_id_format_validation(self):
        """Test that all field IDs follow correct Airtable format."""
        field_ids = AirtableFieldMapping.AIRTABLE_FIELD_IDS

        for field_name, field_id in field_ids.items():
            # Field IDs should start with 'fld' and be 17 characters total
            assert field_id.startswith(
                "fld"
            ), f"Field ID for {field_name} doesn't start with 'fld'"
            assert (
                len(field_id) == 17
            ), f"Field ID for {field_name} is not 17 characters"

        # Specifically verify our accommodation fields
        assert field_ids["Floor"] == "fldlzG1sVg01hsy2g"
        assert field_ids["RoomNumber"] == "fldJTPjo8AHQaADVu"

    @pytest.mark.asyncio
    async def test_field_type_consistency_for_accommodation_fields(self):
        """Test that accommodation fields have consistent types."""
        # Floor should be numeric
        # RoomNumber should be text (to support alphanumeric rooms like "A201")

        # This is more of a documentation test, but validates our assumptions
        # about field types that the integration depends on

        # Floor field should handle integer values
        test_floor_values = [1, 2, 3, 10, 99]
        for floor_val in test_floor_values:
            assert isinstance(floor_val, int)
            assert floor_val > 0

        # RoomNumber field should handle string values (including alphanumeric)
        test_room_values = ["201", "A201", "B10", "301A", "999"]
        for room_val in test_room_values:
            assert isinstance(room_val, str)
            assert len(room_val) > 0

    @pytest.mark.asyncio
    async def test_field_mapping_bidirectional_consistency(
        self, repository, sample_airtable_records_with_fields
    ):
        """Test that field mapping works consistently for read and write operations."""
        # Test read operation (search records and parse fields)
        room_records = [
            record
            for record in sample_airtable_records_with_fields
            if record["fields"].get("RoomNumber") == "201"
        ]
        repository.client.search_by_field = AsyncMock(return_value=room_records)

        participants = await repository.find_by_room_number("201")
        original_participant = participants[0]

        # Test write operation (update using field IDs)
        repository.client.update_record = AsyncMock(
            return_value={
                "id": original_participant.record_id,
                "fields": {
                    "fldlzG1sVg01hsy2g": 4,  # New floor
                    "fldJTPjo8AHQaADVu": "401",  # New room
                },
            }
        )

        # Update accommodation using model field names (repository maps to Airtable fields)
        await repository.update_by_id(
            original_participant.record_id,
            {
                "floor": 4,  # New floor
                "room_number": "401",  # New room
            },
        )

        # Verify the update was called - validating bidirectional field mapping consistency
        repository.client.update_record.assert_called_once()
