"""
Tests for Telegram ID search method using centralized field mapping.

This test ensures that the find_by_telegram_id method uses the centralized
field mapping constants instead of hardcoded field name strings.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config.field_mappings import AirtableFieldMapping
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Participant


class TestTelegramIDSearchCentralized:
    """Test suite for centralized Telegram ID search functionality."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient for testing."""
        client = MagicMock()
        client.search_by_field = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_client):
        """Create AirtableParticipantRepository with mock client."""
        return AirtableParticipantRepository(mock_client)

    @pytest.fixture
    def mock_participant_record(self):
        """Create a mock participant record for testing."""
        return {
            "id": "recTestRecord123",
            "fields": {
                "FullNameRU": "Тестовый Участник",
                "FullNameEN": "Test Participant",
                "TelegramID": "123456789",
                "Role": "CANDIDATE",
            },
        }

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_uses_field_mapping(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that find_by_telegram_id uses centralized field mapping instead of hardcoded string."""
        # RED phase - this test will fail until we update the repository method

        # Setup: Mock the client to return a participant record
        mock_client.search_by_field.return_value = [mock_participant_record]

        # Patch Participant.from_airtable_record to avoid complex object creation
        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Call find_by_telegram_id
            telegram_id = 123456789
            result = await repository.find_by_telegram_id(telegram_id)

            # Assert: Should use the centralized field mapping
            expected_field_name = AirtableFieldMapping.get_airtable_field_name(
                "telegram_id"
            )
            mock_client.search_by_field.assert_called_once_with(
                expected_field_name, telegram_id
            )

            # Should NOT use hardcoded string
            assert (
                mock_client.search_by_field.call_args[0][0] != "Telegram ID"
            ), "Should not use hardcoded 'Telegram ID' string"

            # Should use the mapped field name "TelegramID"
            assert (
                mock_client.search_by_field.call_args[0][0] == "TelegramID"
            ), f"Expected 'TelegramID', got: {mock_client.search_by_field.call_args[0][0]}"

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_functionality_preserved(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that find_by_telegram_id functionality is preserved after centralization."""
        # RED phase - this test will fail until we update the repository method

        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act
            result = await repository.find_by_telegram_id(123456789)

            # Assert: Should return the participant
            assert result is not None
            assert result == mock_participant

            # Should call from_airtable_record with the correct record
            mock_from_record.assert_called_once_with(mock_participant_record)

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_not_found(self, repository, mock_client):
        """Test find_by_telegram_id when no participant is found."""
        # RED phase - this test will fail until we update the repository method

        # Setup: Mock empty search result
        mock_client.search_by_field.return_value = []

        # Act
        result = await repository.find_by_telegram_id(999999999)

        # Assert: Should return None
        assert result is None

        # Should use centralized field mapping
        expected_field_name = AirtableFieldMapping.get_airtable_field_name(
            "telegram_id"
        )
        mock_client.search_by_field.assert_called_once_with(
            expected_field_name, 999999999
        )

    @pytest.mark.asyncio
    async def test_telegram_id_field_mapping_consistency(self, repository):
        """Test that Telegram ID field mapping is consistent across the system."""
        # RED phase - this test will pass once we have the field mapping, but repository won't use it yet

        # Test that the field mapping exists and is correct
        python_field = "telegram_id"
        airtable_field = AirtableFieldMapping.get_airtable_field_name(python_field)

        assert airtable_field is not None, "Telegram ID field mapping should exist"
        assert (
            airtable_field == "TelegramID"
        ), f"Expected 'TelegramID', got: {airtable_field}"

        # Test reverse mapping
        reverse_field = AirtableFieldMapping.get_python_field_name(airtable_field)
        assert reverse_field == python_field, "Reverse mapping should be consistent"

    def test_repository_imports_field_mapping(self):
        """Test that the repository file imports the field mapping classes."""
        # RED phase - this test will fail until we add the import

        # This test ensures the repository has access to field mapping
        from src.data.airtable import airtable_participant_repo

        # Should be able to access AirtableFieldMapping from the repository module
        assert hasattr(
            airtable_participant_repo, "AirtableFieldMapping"
        ), "Repository should import AirtableFieldMapping for centralized field access"
