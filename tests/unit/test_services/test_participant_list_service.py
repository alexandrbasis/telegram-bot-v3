"""
Tests for participant list service functionality.

Tests role-based filtering, list formatting, pagination, and date formatting
for participant list display functionality.
"""

import pytest
from unittest.mock import AsyncMock, Mock
from datetime import date

from src.models.participant import Participant, Role
from src.services.participant_list_service import ParticipantListService


class TestParticipantListService:
    """Test participant list service functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Create mock participant repository."""
        repository = Mock()
        repository.get_by_role = AsyncMock()
        return repository

    @pytest.fixture
    def service(self, mock_repository):
        """Create participant list service with mock repository."""
        return ParticipantListService(mock_repository)

    @pytest.fixture
    def sample_team_participants(self):
        """Create sample team participants for testing."""
        return [
            Participant(
                full_name_ru="Иванов Иван Иванович",
                size="M",
                church="Церковь Святого Духа",
                date_of_birth=date(1985, 6, 15),
                role=Role.TEAM,
            ),
            Participant(
                full_name_ru="Петров Петр Петрович",
                size="L",
                church="Храм Христа Спасителя",
                date_of_birth=date(1990, 12, 3),
                role=Role.TEAM,
            ),
        ]

    @pytest.fixture
    def sample_candidate_participants(self):
        """Create sample candidate participants for testing."""
        return [
            Participant(
                full_name_ru="Сидоров Сидор Сидорович",
                size="S",
                church="Свято-Троицкая церковь",
                date_of_birth=date(1988, 3, 22),
                role=Role.CANDIDATE,
            ),
        ]

    @pytest.mark.asyncio
    async def test_get_team_members_list(self, service, mock_repository, sample_team_participants):
        """Test getting team members list."""
        mock_repository.get_by_role.return_value = sample_team_participants
        
        result = await service.get_team_members_list(page=1, page_size=20)
        
        # Should call repository with TEAM role
        mock_repository.get_by_role.assert_called_once_with("TEAM")
        
        # Should return formatted list data
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result
        assert "total_count" in result
        assert "page" in result

    @pytest.mark.asyncio
    async def test_get_candidates_list(self, service, mock_repository, sample_candidate_participants):
        """Test getting candidates list."""
        mock_repository.get_by_role.return_value = sample_candidate_participants
        
        result = await service.get_candidates_list(page=1, page_size=20)
        
        # Should call repository with CANDIDATE role
        mock_repository.get_by_role.assert_called_once_with("CANDIDATE")
        
        # Should return formatted list data
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result
        assert "total_count" in result
        assert "page" in result

    @pytest.mark.asyncio
    async def test_list_formatting_with_all_fields(self, service, mock_repository, sample_team_participants):
        """Test list formatting includes all required fields."""
        mock_repository.get_by_role.return_value = sample_team_participants
        
        result = await service.get_team_members_list(page=1, page_size=20)
        formatted_list = result["formatted_list"]
        
        # Should be numbered list format
        assert "1." in formatted_list
        assert "2." in formatted_list
        
        # Should contain all participant information
        assert "Иванов Иван Иванович" in formatted_list
        assert "Петров Петр Петрович" in formatted_list
        assert "15.06.1985" in formatted_list  # DD.MM.YYYY format
        assert "03.12.1990" in formatted_list
        assert "M" in formatted_list  # Size
        assert "L" in formatted_list
        assert "Церковь Святого Духа" in formatted_list
        assert "Храм Христа Спасителя" in formatted_list

    @pytest.mark.asyncio
    async def test_date_formatting_dd_mm_yyyy(self, service, mock_repository):
        """Test that dates are formatted as DD.MM.YYYY."""
        participants = [
            Participant(
                full_name_ru="Тестов Тест Тестович",
                date_of_birth=date(1995, 1, 7),  # Single digit day/month
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants
        
        result = await service.get_team_members_list(page=1, page_size=20)
        formatted_list = result["formatted_list"]
        
        # Should format single digit day/month with leading zeros
        assert "07.01.1995" in formatted_list

    @pytest.mark.asyncio
    async def test_missing_date_of_birth_handling(self, service, mock_repository):
        """Test handling of missing date of birth."""
        participants = [
            Participant(
                full_name_ru="Безданный Без Даты",
                date_of_birth=None,
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants
        
        result = await service.get_team_members_list(page=1, page_size=20)
        formatted_list = result["formatted_list"]
        
        # Should show "Не указано" for missing date
        assert "Не указано" in formatted_list

    @pytest.mark.asyncio
    async def test_pagination_first_page(self, service, mock_repository, sample_team_participants):
        """Test pagination for first page."""
        mock_repository.get_by_role.return_value = sample_team_participants
        
        result = await service.get_team_members_list(page=1, page_size=1)
        
        assert result["has_prev"] is False
        assert result["has_next"] is True  # Has more participants
        assert result["page"] == 1
        assert result["total_count"] == 2

    @pytest.mark.asyncio
    async def test_pagination_last_page(self, service, mock_repository, sample_team_participants):
        """Test pagination for last page."""
        mock_repository.get_by_role.return_value = sample_team_participants
        
        result = await service.get_team_members_list(page=2, page_size=1)
        
        assert result["has_prev"] is True
        assert result["has_next"] is False  # No more participants
        assert result["page"] == 2

    @pytest.mark.asyncio
    async def test_empty_participant_list(self, service, mock_repository):
        """Test handling of empty participant list."""
        mock_repository.get_by_role.return_value = []
        
        result = await service.get_team_members_list(page=1, page_size=20)
        
        assert result["formatted_list"] == "Участники не найдены."
        assert result["has_prev"] is False
        assert result["has_next"] is False
        assert result["total_count"] == 0

    @pytest.mark.asyncio
    async def test_message_length_constraint(self, service, mock_repository):
        """Test that formatted list stays under 4096 character limit."""
        # Create many participants to test length constraint
        many_participants = []
        for i in range(100):
            many_participants.append(
                Participant(
                    full_name_ru=f"Участник Номер {i:03d} С Очень Длинным Именем",
                    size="XL",
                    church=f"Очень Длинное Название Церкви Номер {i:03d}",
                    date_of_birth=date(1990, 1, 1),
                    role=Role.TEAM,
                )
            )
        mock_repository.get_by_role.return_value = many_participants
        
        result = await service.get_team_members_list(page=1, page_size=100)
        formatted_list = result["formatted_list"]
        
        # Should stay under Telegram message limit
        assert len(formatted_list) < 4096

    @pytest.mark.asyncio
    async def test_missing_optional_fields(self, service, mock_repository):
        """Test handling of missing optional fields (size, church)."""
        participants = [
            Participant(
                full_name_ru="Минималист Мин Минович",
                size=None,
                church=None,
                date_of_birth=date(1985, 5, 10),
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants
        
        result = await service.get_team_members_list(page=1, page_size=20)
        formatted_list = result["formatted_list"]
        
        # Should handle missing fields gracefully
        assert "Минималист Мин Минович" in formatted_list
        assert "10.05.1985" in formatted_list
        # Should show placeholders for missing fields
        assert formatted_list.count("—") >= 2  # For missing size and church