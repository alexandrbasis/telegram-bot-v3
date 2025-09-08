"""
Tests for backward compatibility validation after centralizing field references.

This test suite validates that all repository search methods maintain identical
functionality after centralization changes, ensuring no regressions.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config.field_mappings import AirtableFieldMapping
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Participant


class TestFieldReferenceBackwardCompatibility:
    """Test suite for backward compatibility validation."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient for testing."""
        client = MagicMock()
        client.search_by_field = AsyncMock()
        client.search_by_formula = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_client):
        """Create AirtableParticipantRepository with mock client."""
        return AirtableParticipantRepository(mock_client)

    @pytest.fixture
    def mock_participant_record(self):
        """Create a mock participant record for testing."""
        return {
            "id": "recBackwardCompat123",
            "fields": {
                "FullNameRU": "Тест Совместимость",
                "FullNameEN": "Test Compatibility",
                "TelegramID": "555666777",
                "ContactInformation": "compat@example.com",
                "Role": "CANDIDATE",
            },
        }

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_backward_compatibility(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that find_by_telegram_id maintains identical functionality after centralization."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_participant.full_name_ru = "Тест Совместимость"
            mock_participant.full_name_en = "Test Compatibility"
            mock_from_record.return_value = mock_participant

            # Act: Test the method
            telegram_id = 555666777
            result = await repository.find_by_telegram_id(telegram_id)

            # Assert: Functionality preserved
            assert result is not None, "Should return participant when found"
            assert (
                result.full_name_ru == "Тест Совместимость"
            ), "Should preserve participant data"
            assert (
                result.full_name_en == "Test Compatibility"
            ), "Should preserve participant data"

            # Verify method called with correct field (now centralized)
            mock_client.search_by_field.assert_called_once_with(
                "TelegramID", telegram_id
            )

            # Verify Participant creation called correctly
            mock_from_record.assert_called_once_with(mock_participant_record)

    @pytest.mark.asyncio
    async def test_find_by_telegram_id_not_found_compatibility(
        self, repository, mock_client
    ):
        """Test that find_by_telegram_id handles not found case identically."""
        # Setup: Mock empty search result
        mock_client.search_by_field.return_value = []

        # Act: Test not found scenario
        result = await repository.find_by_telegram_id(999999999)

        # Assert: Should return None (same as before)
        assert result is None, "Should return None when participant not found"

        # Verify correct field mapping was used
        mock_client.search_by_field.assert_called_once_with("TelegramID", 999999999)

    @pytest.mark.asyncio
    async def test_find_by_contact_information_backward_compatibility(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that find_by_contact_information maintains identical functionality."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_participant.contact_information = "compat@example.com"
            mock_from_record.return_value = mock_participant

            # Act: Test the method
            contact_info = "compat@example.com"
            result = await repository.find_by_contact_information(contact_info)

            # Assert: Functionality preserved
            assert result is not None, "Should return participant when found"
            assert (
                result.contact_information == contact_info
            ), "Should preserve contact information"

            # Verify method called with correct field (now centralized)
            mock_client.search_by_field.assert_called_once_with(
                "ContactInformation", contact_info
            )

            # Verify Participant creation called correctly
            mock_from_record.assert_called_once_with(mock_participant_record)

    @pytest.mark.asyncio
    async def test_find_by_contact_information_not_found_compatibility(
        self, repository, mock_client
    ):
        """Test that find_by_contact_information handles not found case identically."""
        # Setup: Mock empty search result
        mock_client.search_by_field.return_value = []

        # Act: Test not found scenario
        result = await repository.find_by_contact_information("nonexistent@example.com")

        # Assert: Should return None (same as before)
        assert result is None, "Should return None when participant not found"

        # Verify correct field mapping was used
        mock_client.search_by_field.assert_called_once_with(
            "ContactInformation", "nonexistent@example.com"
        )

    @pytest.mark.asyncio
    async def test_search_by_name_backward_compatibility(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that search_by_name maintains identical functionality with centralized formula references."""
        # Setup: Mock successful search
        mock_client.search_by_formula.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_participant.full_name_ru = "Тест Совместимость"
            mock_from_record.return_value = mock_participant

            # Act: Test the method
            name_pattern = "Тест"
            result = await repository.search_by_name(name_pattern)

            # Assert: Functionality preserved
            assert result is not None, "Should return participants when found"
            assert len(result) > 0, "Should return list of participants"
            assert (
                result[0].full_name_ru == "Тест Совместимость"
            ), "Should preserve participant data"

            # Verify formula uses centralized field references
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should use internal field name format (not display name format)
            assert f"SEARCH('{name_pattern}', {{FullNameRU}})" in formula_arg
            assert f"SEARCH('{name_pattern}', {{FullNameEN}})" in formula_arg

            # Should NOT use old display name format
            assert "{Full Name (RU)}" not in formula_arg
            assert "{Full Name (EN)}" not in formula_arg

    @pytest.mark.asyncio
    async def test_search_by_name_empty_results_compatibility(
        self, repository, mock_client
    ):
        """Test that search_by_name handles empty results identically."""
        # Setup: Mock empty search result
        mock_client.search_by_formula.return_value = []

        # Act: Test empty results scenario
        result = await repository.search_by_name("nonexistent")

        # Assert: Should return empty list (same as before)
        assert result is not None, "Should return list, not None"
        assert len(result) == 0, "Should return empty list when no matches"

    @pytest.mark.asyncio
    async def test_search_by_criteria_formula_compatibility(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that search_by_criteria maintains formula functionality."""
        # Setup: Mock successful search
        mock_client.search_by_formula.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Test criteria search with name fields
            criteria = {"full_name_ru": "Тест", "full_name_en": "Test"}
            result = await repository.search_by_criteria(criteria)

            # Assert: Functionality preserved
            assert result is not None, "Should return participants when found"
            assert len(result) > 0, "Should return list of participants"

            # Verify formula construction
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should use consistent field references (same format as search_by_name)
            assert "SEARCH('Тест', {FullNameRU})" in formula_arg
            assert "SEARCH('Test', {FullNameEN})" in formula_arg

    @pytest.mark.asyncio
    async def test_error_handling_backward_compatibility(self, repository, mock_client):
        """Test that error handling behavior is preserved after centralization."""
        # Setup: Mock client to raise exception
        from src.data.airtable.airtable_client import AirtableAPIError

        mock_client.search_by_field.side_effect = AirtableAPIError("Test error", 500)

        # Act & Assert: Should raise RepositoryError (same as before)
        from src.data.repositories.participant_repository import RepositoryError

        with pytest.raises(RepositoryError) as exc_info:
            await repository.find_by_telegram_id(123456789)

        assert "Failed to find participant by Telegram ID" in str(exc_info.value)

        # Verify it attempted to use correct field mapping
        mock_client.search_by_field.assert_called_once_with("TelegramID", 123456789)

    @pytest.mark.asyncio
    async def test_parameter_type_handling_compatibility(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that parameter type handling is preserved."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Test with different parameter types (should work same as before)

            # Test integer Telegram ID
            result1 = await repository.find_by_telegram_id(123456789)
            assert result1 is not None

            # Test string contact information
            result2 = await repository.find_by_contact_information("test@example.com")
            assert result2 is not None

            # Test string name pattern
            mock_client.search_by_formula.return_value = [mock_participant_record]
            result3 = await repository.search_by_name("test pattern")
            assert result3 is not None and len(result3) > 0

    def test_field_mapping_values_unchanged(self):
        """Test that the actual field name values haven't changed after centralization."""
        # These values should remain constant to maintain compatibility

        # Verify field name mappings produce expected Airtable field names
        assert (
            AirtableFieldMapping.get_airtable_field_name("telegram_id") == "TelegramID"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("contact_information")
            == "ContactInformation"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("full_name_ru") == "FullNameRU"
        )
        assert (
            AirtableFieldMapping.get_airtable_field_name("full_name_en") == "FullNameEN"
        )

        # Verify formula field references produce expected format
        assert (
            AirtableFieldMapping.build_formula_field("full_name_ru") == "{FullNameRU}"
        )
        assert (
            AirtableFieldMapping.build_formula_field("full_name_en") == "{FullNameEN}"
        )

        # These values must remain stable for backward compatibility

    @pytest.mark.asyncio
    async def test_logging_behavior_preserved(
        self, repository, mock_client, mock_participant_record
    ):
        """Test that logging behavior is preserved after centralization."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [mock_participant_record]

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            with patch(
                "src.data.airtable.airtable_participant_repo.logger"
            ) as mock_logger:
                # Act: Perform search operations
                await repository.find_by_telegram_id(123456789)
                await repository.find_by_contact_information("test@example.com")

                # Assert: Logging behavior preserved
                assert mock_logger.debug.called, "Should log debug information"

                # Check log messages contain expected information
                debug_calls = [call[0][0] for call in mock_logger.debug.call_args_list]
                assert any(
                    "Finding participant by Telegram ID" in msg for msg in debug_calls
                )
                assert any(
                    "Finding participant by contact information" in msg
                    for msg in debug_calls
                )
