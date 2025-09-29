"""
Unit tests for StatisticsService.

Tests efficiency, aggregation accuracy, error handling, and rate limit compliance.
"""

import asyncio
import pytest
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

from src.services.statistics_service import StatisticsService, StatisticsError
from src.models.department_statistics import DepartmentStatistics
from src.data.repositories.participant_repository import RepositoryError
from src.models.participant import Participant, Department, Role


class TestStatisticsService:
    """Test cases for StatisticsService with Airtable integration."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock participant repository."""
        repository = AsyncMock()
        return repository

    @pytest.fixture
    def service(self, mock_repository):
        """Create StatisticsService instance with mock repository."""
        return StatisticsService(repository=mock_repository)

    @pytest.fixture
    def sample_participants(self):
        """Create sample participants for testing."""
        return [
            Participant(
                full_name_ru="Иван Иванов",
                role=Role.CANDIDATE,
                department=Department.ROE,
                record_id="rec1"
            ),
            Participant(
                full_name_ru="Петр Петров",
                role=Role.TEAM,
                department=Department.ROE,
                record_id="rec2"
            ),
            Participant(
                full_name_ru="Мария Сидорова",
                role=Role.CANDIDATE,
                department=Department.CHAPEL,
                record_id="rec3"
            ),
            Participant(
                full_name_ru="Анна Козлова",
                role=Role.TEAM,
                department=None,
                record_id="rec4"
            ),
        ]

    async def test_collect_statistics_basic_aggregation(self, service, mock_repository, sample_participants):
        """Test basic statistics collection and aggregation."""
        # Arrange - mock single call behavior
        mock_repository.list_all.return_value = sample_participants

        # Act
        result = await service.collect_statistics()

        # Assert
        assert isinstance(result, DepartmentStatistics)
        assert result.total_participants == 4
        assert result.total_teams == 2
        assert result.participants_by_department[Department.ROE.value] == 2
        assert result.participants_by_department[Department.CHAPEL.value] == 1
        assert "unassigned" in result.participants_by_department
        assert result.participants_by_department["unassigned"] == 1

    async def test_collect_statistics_empty_database(self, service, mock_repository):
        """Test statistics collection with empty database."""
        # Arrange
        mock_repository.list_all.return_value = []

        # Act
        result = await service.collect_statistics()

        # Assert
        assert result.total_participants == 0
        assert result.total_teams == 0
        assert len(result.participants_by_department) == 0

    async def test_collect_statistics_repository_error(self, service, mock_repository):
        """Test error handling for repository failures."""
        # Arrange
        mock_repository.list_all.side_effect = RepositoryError("Database connection failed")

        # Act & Assert
        with pytest.raises(StatisticsError):
            await service.collect_statistics()

    async def test_collect_statistics_performance_within_limits(self, service, mock_repository):
        """Test that statistics collection completes within performance targets."""
        # Arrange
        mock_repository.list_all.return_value = []

        # Act
        start_time = datetime.now()
        await service.collect_statistics()
        end_time = datetime.now()

        # Assert - should complete well under 30 seconds for typical datasets
        duration = (end_time - start_time).total_seconds()
        assert duration < 5.0  # Conservative test threshold

    async def test_collect_statistics_rate_limiting_compliance(self, service, mock_repository):
        """Test that service respects Airtable rate limits."""
        # Arrange
        mock_repository.list_all.return_value = []

        # Act - call multiple times rapidly
        tasks = []
        for _ in range(3):
            tasks.append(service.collect_statistics())

        # Should not raise rate limit errors
        results = await asyncio.gather(*tasks)

        # Assert
        assert len(results) == 3
        for result in results:
            assert isinstance(result, DepartmentStatistics)

    async def test_collect_statistics_with_candidates_only(self, service, mock_repository):
        """Test statistics with only candidates (no teams)."""
        # Arrange
        candidates_only = [
            Participant(
                full_name_ru="Кандидат 1",
                role=Role.CANDIDATE,
                department=Department.ROE,
                record_id="rec1"
            ),
            Participant(
                full_name_ru="Кандидат 2",
                role=Role.CANDIDATE,
                department=Department.CHAPEL,
                record_id="rec2"
            ),
        ]
        mock_repository.list_all.return_value = candidates_only

        # Act
        result = await service.collect_statistics()

        # Assert
        assert result.total_participants == 2
        assert result.total_teams == 0
        # Candidates are counted in participants_by_department
        assert result.participants_by_department[Department.ROE.value] == 1
        assert result.participants_by_department[Department.CHAPEL.value] == 1

    async def test_collect_statistics_timestamp_accuracy(self, service, mock_repository):
        """Test that collection timestamp is accurate."""
        # Arrange
        mock_repository.list_all.return_value = []
        before_time = datetime.now()

        # Act
        result = await service.collect_statistics()

        # Assert
        after_time = datetime.now()
        assert before_time <= result.collection_timestamp <= after_time

    async def test_service_initialization_with_repository(self, mock_repository):
        """Test service initialization requires repository."""
        # Act
        service = StatisticsService(repository=mock_repository)

        # Assert
        assert service.repository == mock_repository

    async def test_service_initialization_without_repository(self):
        """Test service initialization fails without repository."""
        # Act & Assert
        with pytest.raises(TypeError):
            StatisticsService()

    async def test_collect_statistics_single_call_optimization(self, service, mock_repository):
        """Test that statistics service uses single optimized call instead of pagination."""
        # Arrange - mock repository to return all data in single call
        all_participants = [
            Participant(
                full_name_ru="Participant 1",
                role=Role.TEAM,
                department=Department.ROE,
                record_id="rec1"
            ),
            Participant(
                full_name_ru="Participant 2",
                role=Role.CANDIDATE,
                department=Department.CHAPEL,
                record_id="rec2"
            ),
            Participant(
                full_name_ru="Participant 3",
                role=Role.CANDIDATE,
                department=Department.ROE,
                record_id="rec3"
            )
        ]

        # Configure mock to return all participants in single call
        mock_repository.list_all.return_value = all_participants

        # Act
        result = await service.collect_statistics()

        # Assert
        assert result.total_participants == 3
        assert result.total_teams == 1
        assert result.participants_by_department[Department.ROE.value] == 2
        assert result.participants_by_department[Department.CHAPEL.value] == 1

        # Verify single call was made (optimized approach)
        calls = mock_repository.list_all.call_args_list
        assert len(calls) == 1
        # Verify called without pagination parameters
        assert calls[0][1] == {} or calls[0][1] is None

    async def test_collect_statistics_with_string_departments(self, service, mock_repository):
        """Test statistics collection handles string department values correctly."""
        # Arrange - participants with string department values (edge case)
        # Use model_construct to bypass Pydantic validation for this edge case test
        participants_with_string_depts = [
            Participant.model_construct(
                full_name_ru="String Dept Participant 1",
                role=Role.CANDIDATE,
                department="Engineering",  # String instead of Department enum
                record_id="rec1"
            ),
            Participant.model_construct(
                full_name_ru="String Dept Participant 2",
                role=Role.TEAM,
                department="Marketing",  # String instead of Department enum
                record_id="rec2"
            ),
            Participant(
                full_name_ru="Normal Enum Participant",
                role=Role.CANDIDATE,
                department=Department.ROE,  # Normal Department enum
                record_id="rec3"
            ),
        ]
        mock_repository.list_all.return_value = participants_with_string_depts

        # Act
        result = await service.collect_statistics()

        # Assert
        assert result.total_participants == 3
        assert result.total_teams == 1

        # String departments should be handled correctly
        assert "Engineering" in result.participants_by_department
        assert "Marketing" in result.participants_by_department
        assert Department.ROE.value in result.participants_by_department

        assert result.participants_by_department["Engineering"] == 1
        assert result.participants_by_department["Marketing"] == 1
        assert result.participants_by_department[Department.ROE.value] == 1
