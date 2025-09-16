"""
Tests for participant list service functionality.

Tests role-based filtering, list formatting, pagination, and date formatting
for participant list display functionality.
"""

from datetime import date
from unittest.mock import AsyncMock, Mock

import pytest

from src.models.participant import Department, Participant, Role
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
    async def test_get_team_members_list(
        self, service, mock_repository, sample_team_participants
    ):
        """Test getting team members list."""
        mock_repository.get_by_role.return_value = sample_team_participants

        result = await service.get_team_members_list(offset=0, page_size=20)

        # Should call repository with TEAM role
        mock_repository.get_by_role.assert_called_once_with("TEAM")

        # Should return formatted list data
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result
        assert "total_count" in result
        assert "current_offset" in result
        assert "next_offset" in result
        assert "prev_offset" in result
        assert "actual_displayed" in result

    @pytest.mark.asyncio
    async def test_get_candidates_list(
        self, service, mock_repository, sample_candidate_participants
    ):
        """Test getting candidates list."""
        mock_repository.get_by_role.return_value = sample_candidate_participants

        result = await service.get_candidates_list(offset=0, page_size=20)

        # Should call repository with CANDIDATE role
        mock_repository.get_by_role.assert_called_once_with("CANDIDATE")

        # Should return formatted list data
        assert "formatted_list" in result
        assert "has_prev" in result
        assert "has_next" in result
        assert "total_count" in result
        assert "current_offset" in result
        assert "next_offset" in result
        assert "prev_offset" in result
        assert "actual_displayed" in result

    @pytest.mark.asyncio
    async def test_list_formatting_with_all_fields(
        self, service, mock_repository, sample_team_participants
    ):
        """Test list formatting includes all required fields (updated format)."""
        mock_repository.get_by_role.return_value = sample_team_participants

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should be numbered list format (with MarkdownV2 escaping)
        assert "1\\." in formatted_list
        assert "2\\." in formatted_list

        # Should contain participant names and churches (retained fields)
        assert "Иванов Иван Иванович" in formatted_list
        assert "Петров Петр Петрович" in formatted_list
        assert "Церковь Святого Духа" in formatted_list
        assert "Храм Христа Спасителя" in formatted_list

        # Should include department field (new format)
        assert "🏢 Департамент:" in formatted_list

        # Should NOT include birth date or clothing size (removed fields)
        assert "📅" not in formatted_list
        assert "👕" not in formatted_list
        assert "Размер:" not in formatted_list
        assert "Дата рождения:" not in formatted_list

    @pytest.mark.asyncio
    async def test_new_format_department_display(self, service, mock_repository):
        """Test new format displays department field correctly."""
        from src.models.participant import Department

        participants = [
            Participant(
                full_name_ru="Тестов Тест Тестович",
                department=Department.KITCHEN,
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should display department in new format
        assert "🏢 Департамент: Kitchen" in formatted_list
        assert "Department.KITCHEN" not in formatted_list
        assert "Тестов Тест Тестович" in formatted_list

    @pytest.mark.asyncio
    async def test_missing_department_handling(self, service, mock_repository):
        """Test handling of missing department field."""
        participants = [
            Participant(
                full_name_ru="Безотдельный Без Отдела",
                department=None,
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should show placeholder for missing department
        assert "Безотдельный Без Отдела" in formatted_list
        assert "🏢 Департамент: —" in formatted_list

    @pytest.mark.asyncio
    async def test_pagination_first_page(
        self, service, mock_repository, sample_team_participants
    ):
        """Test pagination for first page."""
        mock_repository.get_by_role.return_value = sample_team_participants

        result = await service.get_team_members_list(offset=0, page_size=1)

        assert result["has_prev"] is False
        assert result["has_next"] is True  # Has more participants
        assert result["current_offset"] == 0
        assert result["total_count"] == 2

    @pytest.mark.asyncio
    async def test_pagination_last_page(
        self, service, mock_repository, sample_team_participants
    ):
        """Test pagination for last page."""
        mock_repository.get_by_role.return_value = sample_team_participants

        result = await service.get_team_members_list(offset=1, page_size=1)

        assert result["has_prev"] is True
        assert result["has_next"] is False  # No more participants
        assert result["current_offset"] == 1

    @pytest.mark.asyncio
    async def test_offset_clamped_to_last_full_page(self, service, mock_repository):
        """Offset beyond range should snap to the last available page."""
        participants = [
            Participant(full_name_ru=f"Участник {i}", role=Role.TEAM)
            for i in range(5)
        ]
        mock_repository.get_by_role.return_value = participants

        result = await service.get_team_members_list(offset=999, page_size=2)

        assert result["current_offset"] == 4
        assert result["has_prev"] is True
        assert result["has_next"] is False
        assert result["actual_displayed"] == 1

    @pytest.mark.asyncio
    async def test_empty_participant_list(self, service, mock_repository):
        """Test handling of empty participant list."""
        mock_repository.get_by_role.return_value = []

        result = await service.get_team_members_list(offset=0, page_size=20)

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

        result = await service.get_team_members_list(offset=0, page_size=100)
        formatted_list = result["formatted_list"]

        # Should stay under Telegram message limit
        assert len(formatted_list) < 4096

    @pytest.mark.asyncio
    async def test_missing_optional_fields(self, service, mock_repository):
        """Test handling of missing optional fields (department, church)."""
        participants = [
            Participant(
                full_name_ru="Минималист Мин Минович",
                department=None,
                church=None,
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should handle missing fields gracefully
        assert "Минималист Мин Минович" in formatted_list
        # Should show placeholders for missing optional fields
        assert "🏢 Департамент: —" in formatted_list  # Missing department
        assert "⛪ Церковь: —" in formatted_list  # Missing church


class TestTeamListDisplayUpdate:
    """Test team list display update requirements - show department, hide personal data."""

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
    def participants_with_department(self):
        """Create sample participants with department information."""
        return [
            Participant(
                full_name_ru="Иванов Иван Иванович",
                department=Department.SETUP,
                size="M",
                church="Церковь Святого Духа",
                date_of_birth=date(1985, 6, 15),
                role=Role.TEAM,
            ),
            Participant(
                full_name_ru="Петрова Мария Владимировна",
                department=Department.KITCHEN,
                size="S",
                church="Храм Христа Спасителя",
                date_of_birth=date(1990, 12, 3),
                role=Role.TEAM,
            ),
        ]

    @pytest.fixture
    def participants_with_empty_department(self):
        """Create sample participants with empty/None department."""
        return [
            Participant(
                full_name_ru="Сидоров Сидор Сидорович",
                department=None,
                size="L",
                church="Свято-Троицкая церковь",
                date_of_birth=date(1988, 3, 22),
                role=Role.TEAM,
            ),
        ]

    # Business Logic Tests
    @pytest.mark.asyncio
    async def test_team_list_includes_department(
        self, service, mock_repository, participants_with_department
    ):
        """Test that team list includes department field."""
        mock_repository.get_by_role.return_value = participants_with_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should include department information
        assert "🏢" in formatted_list or "Департамент:" in formatted_list
        assert Department.SETUP.value in formatted_list or "SETUP" in formatted_list
        assert Department.KITCHEN.value in formatted_list or "KITCHEN" in formatted_list

    @pytest.mark.asyncio
    async def test_team_list_excludes_birthdate(
        self, service, mock_repository, participants_with_department
    ):
        """Test that team list does NOT include birth date."""
        mock_repository.get_by_role.return_value = participants_with_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should NOT include birth date information
        assert "📅" not in formatted_list
        assert "Дата рождения:" not in formatted_list
        assert "15.06.1985" not in formatted_list
        assert "03.12.1990" not in formatted_list
        assert "15\\.06\\.1985" not in formatted_list
        assert "03\\.12\\.1990" not in formatted_list

    @pytest.mark.asyncio
    async def test_team_list_excludes_clothing_size(
        self, service, mock_repository, participants_with_department
    ):
        """Test that team list does NOT include clothing size."""
        mock_repository.get_by_role.return_value = participants_with_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should NOT include clothing size information
        assert "👕" not in formatted_list
        assert "Размер:" not in formatted_list
        # Don't check individual letters like "M" or "S" as they may appear in department names
        # The absence of "👕" and "Размер:" confirms clothing size is not displayed

    @pytest.mark.asyncio
    async def test_empty_department_handling(
        self, service, mock_repository, participants_with_empty_department
    ):
        """Test graceful handling when department field is empty or None."""
        mock_repository.get_by_role.return_value = participants_with_empty_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should handle empty department gracefully
        assert "Сидоров Сидор Сидорович" in formatted_list
        # Should show placeholder or skip department field
        assert "—" in formatted_list or "Не указан" in formatted_list

    @pytest.mark.asyncio
    async def test_department_formatting(
        self, service, mock_repository, participants_with_department
    ):
        """Test that department text is properly formatted (escaping, truncation)."""
        mock_repository.get_by_role.return_value = participants_with_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should properly escape Markdown special characters if any
        # Should contain properly formatted department names
        assert "Иванов Иван Иванович" in formatted_list
        assert "Петрова Мария Владимировна" in formatted_list

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_missing_department_field_in_airtable(self, service, mock_repository):
        """Test handling cases where department field doesn't exist in response."""
        participants_without_department = [
            Participant(
                full_name_ru="Тестов Тест Тестович",
                # department field omitted
                size="M",
                church="Тестовая церковь",
                date_of_birth=date(1985, 1, 1),
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants_without_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should handle missing department gracefully
        assert "Тестов Тест Тестович" in formatted_list
        # Should not crash and should show some placeholder
        assert len(formatted_list) > 0

    @pytest.mark.asyncio
    async def test_malformed_department_data(self, service, mock_repository):
        """Test handling unexpected department data formats."""
        # This test assumes we might get malformed data from Airtable
        participants_malformed = [
            Participant(
                full_name_ru="Проблемов Проблем Проблемович",
                department=None,  # Malformed - should be handled gracefully
                size="L",
                church="Проблемная церковь",
                date_of_birth=date(1980, 1, 1),
                role=Role.TEAM,
            ),
        ]
        mock_repository.get_by_role.return_value = participants_malformed

        result = await service.get_team_members_list(offset=0, page_size=20)

        # Should not crash with malformed data
        assert "formatted_list" in result
        assert result["total_count"] == 1

    # Integration-style Tests for Display Format
    @pytest.mark.asyncio
    async def test_team_list_end_to_end_new_format(
        self, service, mock_repository, participants_with_department
    ):
        """Test full flow from team command to formatted results with department."""
        mock_repository.get_by_role.return_value = participants_with_department

        result = await service.get_team_members_list(offset=0, page_size=20)
        formatted_list = result["formatted_list"]

        # Should include names and departments
        assert "Иванов Иван Иванович" in formatted_list
        assert "Петрова Мария Владимировна" in formatted_list

        # Should include church (retained field)
        assert "Церковь Святого Духа" in formatted_list
        assert "Храм Христа Спасителя" in formatted_list

        # Should exclude birth date and clothing size
        assert "📅" not in formatted_list
        assert "👕" not in formatted_list
        assert "Размер:" not in formatted_list
        assert "Дата рождения:" not in formatted_list

    @pytest.mark.asyncio
    async def test_team_list_pagination_with_department(
        self, service, mock_repository, participants_with_department
    ):
        """Test that department displays correctly across paginated results."""
        mock_repository.get_by_role.return_value = participants_with_department

        # Test first page
        result = await service.get_team_members_list(offset=0, page_size=1)
        formatted_list = result["formatted_list"]

        # Should include department in paginated results
        assert "Иванов Иван Иванович" in formatted_list
        assert result["has_next"] is True
        assert result["total_count"] == 2

    # User Interaction Tests
    @pytest.mark.asyncio
    async def test_team_list_message_length_with_department(
        self, service, mock_repository
    ):
        """Test that message doesn't exceed Telegram limits with department field."""
        # Create many participants with departments to test length constraint
        many_participants = []
        departments = [
            Department.KITCHEN,
            Department.SETUP,
            Department.ADMINISTRATION,
            Department.BELL,
        ]

        for i in range(50):
            many_participants.append(
                Participant(
                    full_name_ru=f"Участник Номер {i:03d} С Очень Длинным Именем",
                    department=departments[i % len(departments)],
                    church=f"Очень Длинное Название Церкви Номер {i:03d}",
                    date_of_birth=date(1990, 1, 1),
                    role=Role.TEAM,
                )
            )
        mock_repository.get_by_role.return_value = many_participants

        result = await service.get_team_members_list(offset=0, page_size=50)
        formatted_list = result["formatted_list"]

        # Should stay under Telegram message limit even with department field
        assert len(formatted_list) < 4096
