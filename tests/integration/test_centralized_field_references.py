"""
Integration tests for centralized field references.

This test suite validates that all search operations work correctly with
centralized field references through end-to-end integration testing.
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Participant
from src.config.field_mappings import AirtableFieldMapping


class TestCentralizedFieldReferencesIntegration:
    """Integration test suite for centralized field references."""

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
    def sample_participant_records(self):
        """Create sample participant records for testing."""
        return [
            {
                "id": "recSample1",
                "fields": {
                    "FullNameRU": "Иван Иванов",
                    "FullNameEN": "Ivan Ivanov",
                    "TelegramID": "123456789",
                    "ContactInformation": "ivan@example.com",
                    "Role": "CANDIDATE",
                }
            },
            {
                "id": "recSample2",
                "fields": {
                    "FullNameRU": "Мария Петрова",
                    "FullNameEN": "Maria Petrova",
                    "TelegramID": "987654321",
                    "ContactInformation": "maria@example.com",
                    "Role": "TEAM",
                }
            }
        ]

    @pytest.mark.asyncio
    async def test_telegram_id_lookup_integration(self, repository, mock_client, sample_participant_records):
        """Test Telegram ID lookup integration with centralized field references."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [sample_participant_records[0]]

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_participant.full_name_ru = "Иван Иванов"
            mock_from_record.return_value = mock_participant

            # Act: Perform Telegram ID lookup
            result = await repository.find_by_telegram_id(123456789)

            # Assert: Integration works correctly
            assert result is not None
            assert result.full_name_ru == "Иван Иванов"

            # Verify centralized field mapping was used
            expected_field = AirtableFieldMapping.get_airtable_field_name("telegram_id")
            mock_client.search_by_field.assert_called_once_with(expected_field, 123456789)
            assert mock_client.search_by_field.call_args[0][0] == "TelegramID"

    @pytest.mark.asyncio
    async def test_contact_info_lookup_integration(self, repository, mock_client, sample_participant_records):
        """Test contact information lookup integration with centralized field references."""
        # Setup: Mock successful search
        mock_client.search_by_field.return_value = [sample_participant_records[0]]

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_participant.contact_information = "ivan@example.com"
            mock_from_record.return_value = mock_participant

            # Act: Perform contact information lookup
            result = await repository.find_by_contact_information("ivan@example.com")

            # Assert: Integration works correctly
            assert result is not None
            assert result.contact_information == "ivan@example.com"

            # Verify centralized field mapping was used
            expected_field = AirtableFieldMapping.get_airtable_field_name("contact_information")
            mock_client.search_by_field.assert_called_once_with(expected_field, "ivan@example.com")
            assert mock_client.search_by_field.call_args[0][0] == "ContactInformation"

    @pytest.mark.asyncio
    async def test_formula_based_search_integration(self, repository, mock_client, sample_participant_records):
        """Test formula-based search integration with centralized field references."""
        # Setup: Mock successful search
        mock_client.search_by_formula.return_value = sample_participant_records

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Perform formula-based name search
            result = await repository.search_by_name("Иван")

            # Assert: Integration works correctly
            assert result is not None
            assert len(result) > 0

            # Verify centralized formula field references were used
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should contain centralized formula references
            expected_ru_field = AirtableFieldMapping.build_formula_field("full_name_ru")
            expected_en_field = AirtableFieldMapping.build_formula_field("full_name_en")

            assert expected_ru_field in formula_arg
            assert expected_en_field in formula_arg
            assert "{FullNameRU}" in formula_arg
            assert "{FullNameEN}" in formula_arg

    @pytest.mark.asyncio
    async def test_search_criteria_integration(self, repository, mock_client, sample_participant_records):
        """Test search by criteria integration with centralized field references."""
        # Setup: Mock successful search
        mock_client.search_by_formula.return_value = sample_participant_records

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Perform criteria-based search
            result = await repository.search_by_criteria({"full_name_ru": "Иван"})

            # Assert: Integration works correctly
            assert result is not None
            assert len(result) > 0

            # Verify formula uses centralized field references
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should use consistent format with search_by_name
            assert "{FullNameRU}" in formula_arg

    @pytest.mark.asyncio
    async def test_all_search_methods_use_consistent_field_references(self, repository, mock_client, sample_participant_records):
        """Test that all search methods use consistent centralized field references."""
        # Setup: Mock all search operations
        mock_client.search_by_field.return_value = [sample_participant_records[0]]
        mock_client.search_by_formula.return_value = sample_participant_records

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Test all centralized search methods
            telegram_result = await repository.find_by_telegram_id(123456789)
            contact_result = await repository.find_by_contact_information("test@example.com")

            # Reset mock to track formula calls separately
            mock_client.search_by_formula.reset_mock()

            name_result = await repository.search_by_name("test")
            criteria_result = await repository.search_by_criteria({"full_name_ru": "test"})

            # Assert: All methods work
            assert telegram_result is not None
            assert contact_result is not None
            assert name_result is not None
            assert criteria_result is not None

            # Verify field reference consistency
            telegram_field_call = mock_client.search_by_field.call_args_list[0][0][0]
            contact_field_call = mock_client.search_by_field.call_args_list[1][0][0]

            assert telegram_field_call == "TelegramID"
            assert contact_field_call == "ContactInformation"

            # Verify formula consistency
            formula_calls = [call[0][0] for call in mock_client.search_by_formula.call_args_list]
            for formula in formula_calls:
                # All formulas should use internal field name format
                if "{FullNameRU}" in formula or "{FullNameEN}" in formula:
                    assert "{Full Name (RU)}" not in formula, "Should not use display name format"
                    assert "{Full Name (EN)}" not in formula, "Should not use display name format"

    @pytest.mark.asyncio
    async def test_field_mapping_resilience_simulation(self, repository, mock_client, sample_participant_records):
        """Test system resilience to field mapping changes (simulated)."""
        # This test simulates what would happen if Airtable field display names changed
        # but our centralized mappings remained consistent

        # Setup: Mock successful operations
        mock_client.search_by_field.return_value = [sample_participant_records[0]]
        mock_client.search_by_formula.return_value = sample_participant_records

        with patch('src.data.airtable.airtable_participant_repo.Participant.from_airtable_record') as mock_from_record:
            mock_participant = MagicMock(spec=Participant)
            mock_from_record.return_value = mock_participant

            # Act: Perform operations that previously used hardcoded field names

            # 1. Telegram ID search (was "Telegram ID", now uses mapping)
            telegram_result = await repository.find_by_telegram_id(123456789)

            # 2. Contact info search (was "Contact Information", now uses mapping)
            contact_result = await repository.find_by_contact_information("test@example.com")

            # 3. Name search (was "{Full Name (RU)}", now uses mapping)
            name_result = await repository.search_by_name("test")

            # Assert: All operations succeed with centralized mappings
            assert telegram_result is not None
            assert contact_result is not None
            assert name_result is not None

            # Verify that centralized mappings were used (not hardcoded strings)
            field_calls = [call[0][0] for call in mock_client.search_by_field.call_args_list]
            formula_calls = [call[0][0] for call in mock_client.search_by_formula.call_args_list]

            # Should use mapped field names
            assert "TelegramID" in field_calls  # Not "Telegram ID"
            assert "ContactInformation" in field_calls  # Not "Contact Information"

            # Should use internal formula format
            for formula in formula_calls:
                if "FullNameRU" in formula:
                    assert "{FullNameRU}" in formula  # Not "{Full Name (RU)}"
                if "FullNameEN" in formula:
                    assert "{FullNameEN}" in formula  # Not "{Full Name (EN)}"

    def test_field_mapping_constants_integration_ready(self):
        """Test that field mapping constants are properly configured for integration."""
        # Verify all required mappings exist for integration
        required_mappings = ["telegram_id", "contact_information", "full_name_ru", "full_name_en"]

        for python_field in required_mappings:
            airtable_field = AirtableFieldMapping.get_airtable_field_name(python_field)
            assert airtable_field is not None, f"Missing mapping for {python_field}"

            field_id = AirtableFieldMapping.get_field_id(airtable_field)
            assert field_id is not None, f"Missing field ID for {airtable_field}"

        # Verify formula field references
        for formula_field in ["full_name_ru", "full_name_en"]:
            formula_ref = AirtableFieldMapping.build_formula_field(formula_field)
            assert formula_ref is not None, f"Missing formula reference for {formula_field}"
            assert "{" in formula_ref and "}" in formula_ref, f"Invalid formula format: {formula_ref}"
