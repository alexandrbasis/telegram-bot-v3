"""
Tests for formula field reference consistency in repository methods.

This test ensures that both search_by_criteria and search_by_name methods
use consistent formula field references from centralized constants instead
of mixed hardcoded formats.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.config.field_mappings import AirtableFieldMapping
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Department, Gender, PaymentStatus, Role


class TestFormulaConsistency:
    """Test suite for consistent formula field references in repository methods."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock AirtableClient for testing."""
        client = MagicMock()
        client.search_by_formula = AsyncMock()
        return client

    @pytest.fixture
    def repository(self, mock_client):
        """Create AirtableParticipantRepository with mock client."""
        return AirtableParticipantRepository(mock_client)

    @pytest.fixture
    def mock_participant_records(self):
        """Create mock participant records for testing."""
        return [
            {
                "id": "recTest1",
                "fields": {
                    "FullNameRU": "Иван Иванов",
                    "FullNameEN": "Ivan Ivanov",
                    "Role": "CANDIDATE",
                },
            },
            {
                "id": "recTest2",
                "fields": {
                    "FullNameRU": "Мария Петрова",
                    "FullNameEN": "Maria Petrova",
                    "Role": "TEAM",
                },
            },
        ]

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        "field, enum_value, expected",
        [
            ("role", Role.CANDIDATE, "CANDIDATE"),
            ("department", Department.KITCHEN, "Kitchen"),
            ("payment_status", PaymentStatus.PAID, "Paid"),
            ("gender", Gender.FEMALE, "F"),
        ],
    )
    async def test_search_by_criteria_quotes_enum_values(
        self, repository, mock_client, field, enum_value, expected
    ):
        """Ensure enum criteria are converted to string values and quoted."""
        mock_client.search_by_formula.return_value = []

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_from_record.return_value = MagicMock()

            await repository.search_by_criteria({field: enum_value})

        mock_client.search_by_formula.assert_called_once()
        formula_arg = mock_client.search_by_formula.call_args[0][0]
        airtable_field = AirtableFieldMapping.get_airtable_field_name(field)
        assert f"{{{airtable_field}}} = '{expected}'" in formula_arg
        assert f"{enum_value.__class__.__name__}." not in formula_arg

        mock_client.search_by_formula.reset_mock()

    @pytest.mark.asyncio
    async def test_search_by_criteria_uses_consistent_formula_format(
        self, repository, mock_client, mock_participant_records
    ):
        """Test that search_by_criteria uses consistent formula field format from centralized constants."""
        # RED phase - this test will fail until we update the repository method

        # Setup: Mock the client to return participant records
        mock_client.search_by_formula.return_value = mock_participant_records

        # Patch Participant.from_airtable_record to avoid complex object creation
        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock()
            mock_from_record.return_value = mock_participant

            # Act: Call search_by_criteria with name fields
            criteria = {"full_name_ru": "Иван", "full_name_en": "Ivan"}
            result = await repository.search_by_criteria(criteria)

            # Assert: Should use consistent formula field format from centralized constants
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should use centralized formula field references
            expected_ru_field = AirtableFieldMapping.build_formula_field(
                "full_name_ru"
            )  # "{FullNameRU}"
            expected_en_field = AirtableFieldMapping.build_formula_field(
                "full_name_en"
            )  # "{FullNameEN}"

            assert (
                expected_ru_field in formula_arg
            ), f"Formula should contain {expected_ru_field}"
            assert (
                expected_en_field in formula_arg
            ), f"Formula should contain {expected_en_field}"

            # Should NOT contain hardcoded inconsistent formats
            assert (
                "{Full Name (RU)}" not in formula_arg
            ), "Should not contain display name format"
            assert (
                "{Full Name (EN)}" not in formula_arg
            ), "Should not contain display name format"

    @pytest.mark.asyncio
    async def test_search_by_name_uses_consistent_formula_format(
        self, repository, mock_client, mock_participant_records
    ):
        """Test that search_by_name uses consistent formula field format from centralized constants."""
        # RED phase - this test will fail until we update the repository method

        # Setup: Mock the client to return participant records
        mock_client.search_by_formula.return_value = mock_participant_records

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock()
            mock_from_record.return_value = mock_participant

            # Act: Call search_by_name
            result = await repository.search_by_name("test_name")

            # Assert: Should use consistent formula field format from centralized constants
            mock_client.search_by_formula.assert_called_once()
            formula_arg = mock_client.search_by_formula.call_args[0][0]

            # Should use centralized formula field references
            expected_ru_field = AirtableFieldMapping.build_formula_field(
                "full_name_ru"
            )  # "{FullNameRU}"
            expected_en_field = AirtableFieldMapping.build_formula_field(
                "full_name_en"
            )  # "{FullNameEN}"

            assert (
                expected_ru_field in formula_arg
            ), f"Formula should contain {expected_ru_field}"
            assert (
                expected_en_field in formula_arg
            ), f"Formula should contain {expected_en_field}"

            # Should NOT contain inconsistent display name formats
            assert (
                "{Full Name (RU)}" not in formula_arg
            ), "Should not contain display name format"
            assert (
                "{Full Name (EN)}" not in formula_arg
            ), "Should not contain display name format"

    @pytest.mark.asyncio
    async def test_formula_consistency_between_methods(
        self, repository, mock_client, mock_participant_records
    ):
        """Test that both methods use the same formula field format for consistency."""
        # RED phase - this test will fail until both methods use consistent format

        # Setup
        mock_client.search_by_formula.return_value = mock_participant_records

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock()
            mock_from_record.return_value = mock_participant

            # Act: Call both methods
            await repository.search_by_criteria({"full_name_ru": "test"})
            criteria_formula = mock_client.search_by_formula.call_args[0][0]

            # Reset mock to capture second call
            mock_client.search_by_formula.reset_mock()

            await repository.search_by_name("test")
            name_formula = mock_client.search_by_formula.call_args[0][0]

            # Assert: Both methods should use the same field reference format
            ru_field_ref = AirtableFieldMapping.build_formula_field("full_name_ru")
            en_field_ref = AirtableFieldMapping.build_formula_field("full_name_en")

            # Both formulas should contain consistent field references
            assert (
                ru_field_ref in criteria_formula
            ), "search_by_criteria should use consistent RU field reference"
            assert en_field_ref in criteria_formula or "full_name_en" not in str(
                {"full_name_ru": "test"}
            ), "search_by_criteria should use consistent EN field reference when applicable"

            assert (
                ru_field_ref in name_formula
            ), "search_by_name should use consistent RU field reference"
            assert (
                en_field_ref in name_formula
            ), "search_by_name should use consistent EN field reference"

    def test_formula_field_constants_are_correct(self):
        """Test that formula field constants produce the expected format."""
        # RED phase - this test should pass since we already implemented the constants

        # Test that our constants produce the internal field name format (not display name format)
        ru_field = AirtableFieldMapping.build_formula_field("full_name_ru")
        en_field = AirtableFieldMapping.build_formula_field("full_name_en")

        # Should produce internal field name format
        assert ru_field == "{FullNameRU}", f"Expected '{{FullNameRU}}', got: {ru_field}"
        assert en_field == "{FullNameEN}", f"Expected '{{FullNameEN}}', got: {en_field}"

        # Should NOT produce display name format
        assert ru_field != "{Full Name (RU)}", "Should not produce display name format"
        assert en_field != "{Full Name (EN)}", "Should not produce display name format"

    @pytest.mark.asyncio
    async def test_backward_compatibility_preserved(
        self, repository, mock_client, mock_participant_records
    ):
        """Test that functionality is preserved after standardizing formula references."""
        # RED phase - this test should pass once we implement standardization correctly

        # Setup
        mock_client.search_by_formula.return_value = mock_participant_records

        with patch(
            "src.data.airtable.airtable_participant_repo.Participant.from_airtable_record"
        ) as mock_from_record:
            mock_participant = MagicMock()
            mock_from_record.return_value = mock_participant

            # Act: Test that both methods still work functionally
            criteria_result = await repository.search_by_criteria(
                {"full_name_ru": "test"}
            )
            name_result = await repository.search_by_name("test")

            # Assert: Both methods should return results (functionality preserved)
            assert criteria_result is not None, "search_by_criteria should still work"
            assert name_result is not None, "search_by_name should still work"
            assert (
                len(criteria_result) > 0
            ), "search_by_criteria should return participant objects"
            assert (
                len(name_result) > 0
            ), "search_by_name should return participant objects"
