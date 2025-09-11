"""
Integration tests for participant list service with repository.

Tests that the service correctly integrates with the existing Airtable
repository role filtering functionality.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date

from src.models.participant import Participant, Role
from src.services.participant_list_service import ParticipantListService


class TestParticipantListServiceRepositoryIntegration:
    """Test integration between participant list service and repository."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock repository with role filtering support."""
        repository = Mock()
        repository.get_by_role = AsyncMock()
        return repository

    @pytest.fixture
    def service(self, mock_repository):
        """Create participant list service with mock repository."""
        return ParticipantListService(mock_repository)

    @pytest.mark.asyncio
    async def test_service_calls_repository_with_team_role(
        self, service, mock_repository
    ):
        """Test that service calls repository with correct TEAM role string."""
        # Setup
        mock_repository.get_by_role.return_value = []

        # Execute
        await service.get_team_members_list()

        # Verify
        mock_repository.get_by_role.assert_called_once_with("TEAM")

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
        mock_repository.get_by_role.return_value = team_participants

        # Execute
        result = await service.get_team_members_list()

        # Verify
        assert result["total_count"] == 2
        assert "Команда Один" in result["formatted_list"]
        assert "Команда Два" in result["formatted_list"]
        assert "01.01.1985" in result["formatted_list"]
        assert "31.12.1990" in result["formatted_list"]

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

        # Verify
        assert result["total_count"] == 1
        assert "Кандидат Первый" in result["formatted_list"]
        assert "15.06.1992" in result["formatted_list"]
        assert "S" in result["formatted_list"]
        assert "Церковь кандидата" in result["formatted_list"]

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
        mock_repository.get_by_role.return_value = []

        # Execute
        team_result = await service.get_team_members_list()
        candidate_result = await service.get_candidates_list()

        # Verify
        assert team_result["total_count"] == 0
        assert team_result["formatted_list"] == "Участники не найдены."
        assert candidate_result["total_count"] == 0
        assert candidate_result["formatted_list"] == "Участники не найдены."
