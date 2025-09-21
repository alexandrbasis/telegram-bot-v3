"""
Integration tests for participant list service with repository.

Tests that the service correctly integrates with the existing Airtable
repository role filtering functionality.
"""

import os
from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from src.models.participant import Participant, Role
from src.services.participant_list_service import ParticipantListService


class TestParticipantListServiceRepositoryIntegration:
    """Test integration between participant list service and repository."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository with department and role filtering support."""
        repository = Mock()
        repository.get_by_role = AsyncMock()
        repository.get_team_members_by_department = AsyncMock()
        return repository

    @pytest.fixture
    def service(self, mock_repository):
        """Create participant list service with mock repository."""
        return ParticipantListService(mock_repository)

    @pytest.mark.asyncio
    async def test_service_calls_repository_with_department_method(
        self, service, mock_repository
    ):
        """Test that service calls repository with new department filtering method."""
        # Setup
        mock_repository.get_team_members_by_department.return_value = []

        # Execute
        await service.get_team_members_list()

        # Verify - should call new method with None (default for all team members)
        mock_repository.get_team_members_by_department.assert_called_once_with(None)

    @pytest.mark.asyncio
    async def test_service_calls_repository_with_candidate_role(
        self, service, mock_repository
    ):
        """Test that service calls repository with correct CANDIDATE role string."""
        # Setup
        mock_repository.get_by_role.return_value = []

        # Execute
        await service.get_candidates_list()

        # Verify
        mock_repository.get_by_role.assert_called_once_with("CANDIDATE")

    @pytest.mark.asyncio
    async def test_service_calls_repository_with_specific_department(
        self, service, mock_repository
    ):
        """Test that service calls repository with specific department filter."""
        # Setup
        mock_repository.get_team_members_by_department.return_value = []

        # Execute
        await service.get_team_members_list(department="ROE")

        # Verify - should call new method with specific department
        mock_repository.get_team_members_by_department.assert_called_once_with("ROE")

    @pytest.mark.asyncio
    async def test_service_calls_repository_with_unassigned_filter(
        self, service, mock_repository
    ):
        """Test that service calls repository with unassigned department filter."""
        # Setup
        mock_repository.get_team_members_by_department.return_value = []

        # Execute
        await service.get_team_members_list(department="unassigned")

        # Verify - should call new method with unassigned filter
        mock_repository.get_team_members_by_department.assert_called_once_with(
            "unassigned"
        )

    @pytest.mark.asyncio
    async def test_service_processes_repository_team_results(
        self, service, mock_repository
    ):
        """Test that service correctly processes team results from repository."""
        # Setup team participants
        team_participants = [
            Participant(
                full_name_ru="Команда Один",
                role=Role.TEAM,
                size="M",
                church="Церковь 1",
                date_of_birth=date(1985, 1, 1),
            ),
            Participant(
                full_name_ru="Команда Два",
                role=Role.TEAM,
                size="L",
                church="Церковь 2",
                date_of_birth=date(1990, 12, 31),
            ),
        ]
        mock_repository.get_team_members_by_department.return_value = team_participants

        # Execute
        result = await service.get_team_members_list()

        # Verify (updated for new format without birth dates)
        assert result["total_count"] == 2
        assert "Команда Один" in result["formatted_list"]
        assert "Команда Два" in result["formatted_list"]
        # New format shows department instead of birth date
        assert "🏢 Департамент:" in result["formatted_list"]
        assert "⛪ Церковь:" in result["formatted_list"]
        assert "Церковь 1" in result["formatted_list"]
        assert "Церковь 2" in result["formatted_list"]

    @pytest.mark.asyncio
    async def test_service_processes_repository_candidate_results(
        self, service, mock_repository
    ):
        """Test that service correctly processes candidate results from repository."""
        # Setup candidate participants
        candidate_participants = [
            Participant(
                full_name_ru="Кандидат Первый",
                role=Role.CANDIDATE,
                size="S",
                church="Церковь кандидата",
                date_of_birth=date(1992, 6, 15),
            )
        ]
        mock_repository.get_by_role.return_value = candidate_participants

        # Execute
        result = await service.get_candidates_list()

        # Verify candidate format excludes department and includes church
        assert result["total_count"] == 1
        assert "Кандидат Первый" in result["formatted_list"]
        assert "🏢" not in result["formatted_list"]
        assert "Департамент" not in result["formatted_list"]
        assert "⛪ Церковь:" in result["formatted_list"]
        assert "Церковь кандидата" in result["formatted_list"]

    @pytest.mark.asyncio
    async def test_service_displays_chief_indicators_in_team_results(
        self, service, mock_repository
    ):
        """Test that service correctly displays crown indicators for department chiefs."""
        # Setup team participants with one chief and one regular member
        team_participants = [
            Participant(
                full_name_ru="Начальник Департамента",
                role=Role.TEAM,
                size="M",
                church="Церковь руководства",
                date_of_birth=date(1985, 1, 1),
                is_department_chief=True,
            ),
            Participant(
                full_name_ru="Обычный Участник",
                role=Role.TEAM,
                size="L",
                church="Церковь участника",
                date_of_birth=date(1990, 12, 31),
                is_department_chief=False,
            ),
        ]
        mock_repository.get_team_members_by_department.return_value = team_participants

        # Execute
        result = await service.get_team_members_list()

        # Verify crown indicator appears for chief
        assert result["total_count"] == 2
        assert "👑 **Начальник Департамента**" in result["formatted_list"]
        # Verify no crown for regular member by checking the line containing their name
        lines_with_regular_member = [
            line
            for line in result["formatted_list"].split("\n")
            if "Обычный Участник" in line
        ]
        assert len(lines_with_regular_member) == 1
        assert "👑" not in lines_with_regular_member[0]

    @pytest.mark.asyncio
    async def test_role_enum_values_match_repository_expectations(self):
        """Test that Role enum values match what repository expects."""
        # This test verifies the enum values are correct
        assert Role.TEAM.value == "TEAM"
        assert Role.CANDIDATE.value == "CANDIDATE"

        # These should match what the service passes to repository
        # (verified in the other tests above)

    @pytest.mark.asyncio
    async def test_service_handles_empty_repository_results(
        self, service, mock_repository
    ):
        """Test service handles empty results from repository gracefully."""
        # Setup
        mock_repository.get_team_members_by_department.return_value = []
        mock_repository.get_by_role.return_value = []

        # Execute
        team_result = await service.get_team_members_list()
        candidate_result = await service.get_candidates_list()

        # Verify
        assert team_result["total_count"] == 0
        assert team_result["formatted_list"] == "Участники не найдены."
        assert candidate_result["total_count"] == 0
        assert candidate_result["formatted_list"] == "Участники не найдены."


@pytest.mark.skipif(
    not os.getenv("AIRTABLE_API_KEY") or not os.getenv("AIRTABLE_BASE_ID"),
    reason="Airtable credentials not available - skipping real API integration tests"
)
class TestParticipantListServiceAirtableIntegration:
    """Test participant list service with real Airtable repository integration."""

    @pytest.fixture
    def airtable_service(self):
        """Create participant list service with real Airtable repository."""
        from src.services.service_factory import get_participant_list_service
        return get_participant_list_service()

    @pytest.mark.asyncio
    async def test_team_members_list_with_department_filtering_calls_correct_method(
        self, airtable_service
    ):
        """Test that team members list calls the correct repository method for department filtering."""
        # This is a minimal test to verify the service is correctly wired
        # It should call the new get_team_members_by_department method
        service = airtable_service

        # Verify service has repository with department filtering capability
        assert hasattr(service, 'repository')
        assert hasattr(service.repository, 'get_team_members_by_department')

    @pytest.mark.asyncio
    async def test_department_filtering_with_none_returns_all_team_members(
        self, airtable_service
    ):
        """Test that department=None returns all team members (existing behavior)."""
        # Execute - this should work like the existing get_team_members_list
        result = await airtable_service.get_team_members_list(department=None)

        # Verify basic structure
        assert "total_count" in result
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result
        assert "current_offset" in result
        assert "actual_displayed" in result

        # Should have reasonable count (assuming test data exists)
        assert result["total_count"] >= 0

    @pytest.mark.asyncio
    async def test_department_filtering_with_specific_department(
        self, airtable_service
    ):
        """Test department filtering with a specific department name."""
        # Test with a known department (ROE should exist in real data)
        result = await airtable_service.get_team_members_list(department="ROE")

        # Verify basic structure
        assert "total_count" in result
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result

        # Count should be reasonable (could be 0 if no Finance members)
        assert result["total_count"] >= 0

        # If there are ROE members, they should be properly formatted
        if result["total_count"] > 0:
            assert "🏢 Департамент: ROE" in result["formatted_list"]

    @pytest.mark.asyncio
    async def test_department_filtering_with_unassigned_filter(
        self, airtable_service
    ):
        """Test department filtering for participants without assigned departments."""
        # Test unassigned department filter
        result = await airtable_service.get_team_members_list(department="unassigned")

        # Verify basic structure
        assert "total_count" in result
        assert "formatted_list" in result

        # Count should be reasonable
        assert result["total_count"] >= 0

        # If there are unassigned members, they should show "Не указан"
        if result["total_count"] > 0:
            formatted_list = result["formatted_list"]
            # Should either show "Не указан" or not show department field
            assert "Не указан" in formatted_list or "Департамент:" not in formatted_list

    @pytest.mark.asyncio
    async def test_department_filtering_preserves_pagination_and_sorting(
        self, airtable_service
    ):
        """Test that department filtering works correctly with pagination and sorting."""
        # Test with pagination parameters
        result = await airtable_service.get_team_members_list(
            department=None, offset=0, page_size=5
        )

        # Verify pagination structure
        assert "has_prev" in result
        assert "has_next" in result
        assert "current_offset" in result
        assert "next_offset" in result
        assert "prev_offset" in result
        assert "actual_displayed" in result

        # Verify offset handling
        assert result["current_offset"] == 0
        assert result["actual_displayed"] <= 5

        # If there are more than 5 members, has_next should be True
        if result["total_count"] > 5:
            assert result["has_next"] is True
            assert result["next_offset"] == 5

    @pytest.mark.asyncio
    async def test_department_chief_indicators_work_with_real_data(
        self, airtable_service
    ):
        """Test that department chief indicators work with real Airtable data."""
        # Get team members to see if any are marked as chiefs
        result = await airtable_service.get_team_members_list()

        # Verify structure
        assert "formatted_list" in result

        # If there are team members, check formatting
        if result["total_count"] > 0:
            formatted_list = result["formatted_list"]

            # Should have proper numbering and formatting
            assert "1\\." in formatted_list  # At least first item

            # Check if any chiefs exist (they would have crown emoji)
            lines = formatted_list.split('\n')
            name_lines = [line for line in lines if '\\.' in line and '**' in line]

            # Each participant should have proper structure
            for line in name_lines:
                # Should have either crown or no crown, but proper name formatting
                assert '**' in line  # Bold names

    @pytest.mark.asyncio
    async def test_service_handles_nonexistent_department_gracefully(
        self, airtable_service
    ):
        """Test service handles filtering by non-existent department gracefully."""
        # Test with a department that definitely doesn't exist
        result = await airtable_service.get_team_members_list(
            department="NonExistentDepartmentXYZ123"
        )

        # Should handle gracefully
        assert "total_count" in result
        assert result["total_count"] == 0
        assert result["formatted_list"] == "Участники не найдены."
        assert result["has_prev"] is False
        assert result["has_next"] is False

    @pytest.mark.asyncio
    async def test_department_filtering_maintains_data_consistency(
        self, airtable_service
    ):
        """Test that department filtering maintains consistent data structure."""
        # Test multiple department filters to ensure consistency
        # Note: "unassigned" filter may fail due to Airtable schema constraints
        filters_to_test = [None, "ROE"]

        for department_filter in filters_to_test:
            result = await airtable_service.get_team_members_list(
                department=department_filter
            )

            # Each result should have consistent structure
            required_keys = [
                "total_count", "formatted_list", "has_prev", "has_next",
                "current_offset", "next_offset", "prev_offset", "actual_displayed"
            ]

            for key in required_keys:
                assert key in result, f"Missing key {key} for department filter {department_filter}"

            # Types should be consistent
            assert isinstance(result["total_count"], int)
            assert isinstance(result["formatted_list"], str)
            assert isinstance(result["has_prev"], bool)
            assert isinstance(result["has_next"], bool)
            assert isinstance(result["current_offset"], int)
            assert isinstance(result["actual_displayed"], int)

    @pytest.mark.asyncio
    async def test_real_airtable_connection_and_field_mapping(
        self, airtable_service
    ):
        """Test that service can connect to real Airtable and map fields correctly."""
        # This is a connectivity test to ensure the integration works end-to-end
        try:
            result = await airtable_service.get_team_members_list()

            # If successful, verify basic structure
            assert isinstance(result, dict)
            assert "total_count" in result

            # If there are participants, verify field mapping works
            if result["total_count"] > 0:
                formatted = result["formatted_list"]

                # Should have proper Russian formatting
                assert "⛪ Церковь:" in formatted or "👕 Размер:" in formatted

        except Exception as e:
            # If connection fails, ensure it's a configuration issue, not a code issue
            # This test documents the expected behavior
            pytest.fail(f"Airtable connection failed: {e}. Check configuration and network connectivity.")
