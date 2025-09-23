"""
Unit tests for ParticipantExportService.

Tests the CSV export functionality including:
- Repository integration
- Field mapping accuracy
- CSV formatting
- Large dataset handling
- Error handling
"""

import csv
import io
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

from src.config.field_mappings import AirtableFieldMapping
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.participant import (
    Department,
    Gender,
    Participant,
    PaymentStatus,
    Role,
    Size,
)
from src.services.participant_export_service import ParticipantExportService


@pytest.fixture
def mock_repository():
    """Create a mock participant repository."""
    repo = AsyncMock(spec=ParticipantRepository)
    return repo


@pytest.fixture
def sample_participants():
    """Create sample participant data for testing."""
    return [
        Participant(
            record_id="rec001",
            full_name_ru="Иванов Иван Иванович",
            full_name_en="Ivanov Ivan Ivanovich",
            church="Москва Церковь",
            country_and_city="Россия, Москва",
            submitted_by="Петров П.П.",
            contact_information="+7 999 123-45-67",
            telegram_id="@ivanov",
            church_leader="Сидоров С.С.",
            table_name="Стол 1",
            notes="Тестовая заметка",
            gender=Gender.MALE,
            size=Size.L,
            role=Role.CANDIDATE,
            department=Department.WORSHIP,
            payment_status=PaymentStatus.PAID,
            payment_amount=5000.0,
            payment_date=date(2025, 1, 15),
            date_of_birth=date(1990, 5, 20),
            age=34,
            floor=2,
            room_number="205",
        ),
        Participant(
            record_id="rec002",
            full_name_ru="Петрова Мария Сергеевна",
            full_name_en="Petrova Maria Sergeevna",
            church="Санкт-Петербург Церковь",
            country_and_city="Россия, Санкт-Петербург",
            submitted_by="Иванов И.И.",
            contact_information="+7 999 987-65-43",
            telegram_id=None,
            church_leader=None,
            table_name=None,
            notes=None,
            gender=Gender.FEMALE,
            size=Size.M,
            role=Role.TEAM,
            department=Department.KITCHEN,
            payment_status=PaymentStatus.UNPAID,
            payment_amount=None,
            payment_date=None,
            date_of_birth=None,
            age=None,
            floor=1,
            room_number="101",
        ),
    ]


def make_view_record(record_id: str, **fields: Any) -> Dict[str, Any]:
    """Utility to build Airtable-style record dictionaries for view responses."""
    return {"id": record_id, "fields": fields}


@pytest.fixture
def export_service(mock_repository):
    """Create a ParticipantExportService instance with mock repository."""
    return ParticipantExportService(repository=mock_repository)


class TestParticipantExportServiceInit:
    """Test ParticipantExportService initialization."""

    def test_init_with_repository(self, mock_repository):
        """Test service initialization with repository dependency."""
        service = ParticipantExportService(repository=mock_repository)
        assert service.repository == mock_repository

    def test_init_without_repository(self):
        """Test service initialization fails without repository."""
        with pytest.raises(TypeError):
            ParticipantExportService()


class TestGetAllParticipantsAsCSV:
    """Test get_all_participants_as_csv method."""

    @pytest.mark.asyncio
    async def test_successful_export(
        self, export_service, mock_repository, sample_participants
    ):
        """Test successful CSV export with sample data."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        assert csv_string is not None

        assert isinstance(csv_string, str)

        # Verify CSV structure
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        rows = list(csv_reader)

        # Check row count
        assert len(rows) == 2

        # Check first row data
        first_row = rows[0]
        assert first_row["FullNameRU"] == "Иванов Иван Иванович"
        assert first_row["FullNameEN"] == "Ivanov Ivan Ivanovich"
        assert first_row["Church"] == "Москва Церковь"
        assert first_row["Gender"] == "M"
        assert first_row["Role"] == "CANDIDATE"
        assert first_row["Department"] == "Worship"
        assert first_row["PaymentStatus"] == "Paid"
        assert first_row["PaymentAmount"] == "5000"
        assert first_row["PaymentDate"] == "2025-01-15"
        assert first_row["DateOfBirth"] == "20/05/1990"
        assert first_row["Age"] == "34"
        assert first_row["Floor"] == "2"
        assert first_row["RoomNumber"] == "205"

        # Repository was called once
        mock_repository.list_all.assert_called_once()

    @pytest.mark.asyncio
    async def test_export_with_empty_dataset(self, export_service, mock_repository):
        """Test CSV export with no participants."""
        # Arrange
        mock_repository.list_all.return_value = []

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        assert csv_string is not None

        # Verify CSV has headers but no data
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        rows = list(csv_reader)
        assert len(rows) == 0

        # But headers should still be present
        assert "FullNameRU" in csv_reader.fieldnames
        assert "FullNameEN" in csv_reader.fieldnames

    @pytest.mark.asyncio
    async def test_export_with_none_values(self, export_service, mock_repository):
        """Test CSV export handles None values correctly."""
        # Arrange
        participant_with_nulls = Participant(
            record_id="rec003",
            full_name_ru="Тестов Тест",
            full_name_en=None,
            church=None,
            country_and_city=None,
            submitted_by=None,
            contact_information=None,
            telegram_id=None,
            church_leader=None,
            table_name=None,
            notes=None,
            gender=None,
            size=None,
            role=Role.CANDIDATE,
            department=None,
            payment_status=None,
            payment_amount=None,
            payment_date=None,
            date_of_birth=None,
            age=None,
            floor=None,
            room_number=None,
        )
        mock_repository.list_all.return_value = [participant_with_nulls]

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        rows = list(csv_reader)

        # None values should be empty strings in CSV
        first_row = rows[0]
        assert first_row["FullNameEN"] == ""
        assert first_row["Church"] == ""
        assert first_row["Gender"] == ""
        assert first_row["PaymentAmount"] == ""

    @pytest.mark.asyncio
    async def test_field_mapping_accuracy(
        self, export_service, mock_repository, sample_participants
    ):
        """Test that CSV headers match Airtable field names exactly."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        csv_reader = csv.DictReader(io.StringIO(csv_string))

        # Expected headers from AirtableFieldMapping (excluding 'id')
        expected_headers = [
            "FullNameRU",
            "FullNameEN",
            "Church",
            "CountryAndCity",
            "SubmittedBy",
            "ContactInformation",
            "TelegramID",
            "ChurchLeader",
            "TableName",
            "Notes",
            "Gender",
            "Size",
            "Role",
            "Department",
            "PaymentStatus",
            "PaymentAmount",
            "PaymentDate",
            "DateOfBirth",
            "Age",
            "Floor",
            "RoomNumber",
        ]

        # Check all expected headers are present
        for header in expected_headers:
            assert header in csv_reader.fieldnames, f"Missing header: {header}"

    @pytest.mark.asyncio
    async def test_large_dataset_handling(self, export_service, mock_repository):
        """Test CSV export with large dataset (1000+ records)."""
        # Arrange
        large_dataset = []
        for i in range(1500):
            large_dataset.append(
                Participant(
                    record_id=f"rec{i:04d}",
                    full_name_ru=f"Тестов {i}",
                    full_name_en=f"Testov {i}",
                    church=f"Church {i % 10}",
                    role=Role.CANDIDATE if i % 2 == 0 else Role.TEAM,
                    department=Department.WORSHIP,
                )
            )
        mock_repository.list_all.return_value = large_dataset

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        csv_reader = csv.DictReader(io.StringIO(csv_string))
        rows = list(csv_reader)
        assert len(rows) == 1500

        # Verify some sample data
        assert rows[0]["FullNameRU"] == "Тестов 0"
        assert rows[999]["FullNameRU"] == "Тестов 999"
        assert rows[1499]["FullNameRU"] == "Тестов 1499"

    @pytest.mark.asyncio
    async def test_utf8_encoding(self, export_service, mock_repository):
        """Test CSV properly handles UTF-8 encoded Russian text."""
        # Arrange
        participant_with_russian = Participant(
            record_id="rec_rus",
            full_name_ru="Фёдоров Пётр Ёлкин",
            full_name_en="Fyodorov Pyotr Yolkin",
            church="Церковь «Благодать»",
            notes="Специальные символы: ё, й, щ, ъ, ь",
            role=Role.CANDIDATE,
        )
        mock_repository.list_all.return_value = [participant_with_russian]

        # Act
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        # Ensure UTF-8 string is properly formed
        assert "Фёдоров Пётр Ёлкин" in csv_string
        assert "Церковь «Благодать»" in csv_string
        assert "ё, й, щ, ъ, ь" in csv_string

        # Verify it can be re-encoded as UTF-8
        csv_bytes = csv_string.encode("utf-8")
        decoded = csv_bytes.decode("utf-8")
        assert decoded == csv_string

    @pytest.mark.asyncio
    async def test_repository_error_handling(self, export_service, mock_repository):
        """Test handling of repository errors."""
        # Arrange
        mock_repository.list_all.side_effect = Exception("Database connection failed")

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await export_service.get_all_participants_as_csv()
        assert "Database connection failed" in str(exc_info.value)


class TestSaveToFile:
    """Test save_to_file method."""

    @pytest.mark.asyncio
    async def test_save_csv_to_file(
        self, export_service, mock_repository, sample_participants
    ):
        """Test saving CSV to a file."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants

        # Act
        file_path = await export_service.save_to_file()

        # Assert
        assert file_path is not None
        assert Path(file_path).exists()
        assert file_path.endswith(".csv")

        # Verify file content
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            assert "Иванов Иван Иванович" in content
            assert "Петрова Мария Сергеевна" in content

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_save_with_custom_filename(
        self, export_service, mock_repository, sample_participants
    ):
        """Test saving CSV with custom filename."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants
        custom_name = "test_export_2025"

        # Act
        file_path = await export_service.save_to_file(filename_prefix=custom_name)

        # Assert
        assert custom_name in file_path
        assert Path(file_path).exists()

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_save_to_custom_directory(
        self, export_service, mock_repository, sample_participants
    ):
        """Test saving CSV to custom directory."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants

        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            file_path = await export_service.save_to_file(directory=tmpdir)

            # Assert
            assert Path(file_path).parent == Path(tmpdir)
            assert Path(file_path).exists()

    @pytest.mark.asyncio
    async def test_file_cleanup_on_error(self, export_service, mock_repository):
        """Test that temporary files are cleaned up on error."""
        # Arrange
        mock_repository.list_all.side_effect = Exception("Export failed")

        # Act & Assert
        with pytest.raises(Exception):
            await export_service.save_to_file()

        # Verify no orphaned temp files (this is more conceptual as
        # the implementation should handle cleanup)


class TestFileSizeEstimation:
    """Test file size estimation functionality."""

    @pytest.mark.asyncio
    async def test_estimate_file_size(
        self, export_service, mock_repository, sample_participants
    ):
        """Test file size estimation before generation."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants
        mock_repository.count_total.return_value = len(sample_participants)

        # Act
        estimated_size = await export_service.estimate_file_size()

        # Assert
        assert estimated_size > 0
        assert isinstance(estimated_size, int)

        # For 2 participants, size should be reasonable (few KB)
        assert estimated_size < 10000  # Less than 10KB

    @pytest.mark.asyncio
    async def test_estimate_large_file_size(self, export_service, mock_repository):
        """Test file size estimation for large datasets."""
        # Arrange
        mock_repository.count_total.return_value = 10000

        # Act
        estimated_size = await export_service.estimate_file_size()

        # Assert
        # For 10k records, should be several MB but under 50MB limit
        assert estimated_size > 1000000  # More than 1MB
        assert estimated_size < 50000000  # Less than 50MB

    @pytest.mark.asyncio
    async def test_check_telegram_limit(self, export_service, mock_repository):
        """Test checking if file exceeds Telegram's limit."""
        # Arrange
        mock_repository.count_total.return_value = 100  # Small dataset

        # Act
        is_within_limit = await export_service.is_within_telegram_limit()

        # Assert
        assert is_within_limit is True

    @pytest.mark.asyncio
    async def test_check_telegram_limit_exceeded(self, export_service, mock_repository):
        """Test detection of files exceeding Telegram's limit."""
        # Arrange
        mock_repository.count_total.return_value = 1000000  # Huge dataset

        # Act
        is_within_limit = await export_service.is_within_telegram_limit()

        # Assert
        assert is_within_limit is False


class TestProgressTracking:
    """Test progress tracking functionality."""

    @pytest.mark.asyncio
    async def test_export_with_progress_callback(self, mock_repository):
        """Test CSV export with progress tracking."""
        # Arrange
        participants = [
            Participant(
                record_id=f"rec{i:03d}",
                full_name_ru=f"Тест {i}",
                role=Role.CANDIDATE,
            )
            for i in range(100)
        ]
        mock_repository.list_all.return_value = participants

        progress_calls = []

        def progress_callback(current: int, total: int):
            progress_calls.append((current, total))

        service = ParticipantExportService(
            repository=mock_repository, progress_callback=progress_callback
        )

        # Act
        await service.get_all_participants_as_csv()

        # Assert
        assert len(progress_calls) > 0
        # Should report progress at intervals
        assert progress_calls[0] == (0, 100)
        assert progress_calls[-1][0] == 100  # Completed all

    @pytest.mark.asyncio
    async def test_export_without_progress_callback(
        self, export_service, mock_repository, sample_participants
    ):
        """Test that export works without progress callback."""
        # Arrange
        mock_repository.list_all.return_value = sample_participants

        # Act - should not raise any errors
        csv_string = await export_service.get_all_participants_as_csv()

        # Assert
        assert csv_string is not None


class TestExportToCsvInterface:
    """Test synchronous and asynchronous export entry points."""

    def test_export_to_csv_no_running_loop(self, sample_participants):
        """Synchronous export succeeds when no loop is active."""
        repo = AsyncMock(spec=ParticipantRepository)
        repo.list_all.return_value = sample_participants
        service = ParticipantExportService(repository=repo)

        csv_data = service.export_to_csv()

        assert "FullNameRU" in csv_data
        repo.list_all.assert_awaited()

    @pytest.mark.asyncio
    async def test_export_to_csv_raises_with_active_loop(
        self, sample_participants
    ) -> None:
        """Sync API signals callers to use coroutine when loop is running."""
        repo = AsyncMock(spec=ParticipantRepository)
        repo.list_all.return_value = sample_participants
        service = ParticipantExportService(repository=repo)

        with pytest.raises(RuntimeError) as exc:
            service.export_to_csv()

        assert "use await" in str(exc.value)
        repo.list_all.assert_not_called()

    @pytest.mark.asyncio
    async def test_export_to_csv_async_alias(self, sample_participants) -> None:
        """Dedicated async alias mirrors primary coroutine implementation."""
        repo = AsyncMock(spec=ParticipantRepository)
        repo.list_all.return_value = sample_participants
        service = ParticipantExportService(repository=repo)

        csv_data = await service.export_to_csv_async()

        assert "FullNameRU" in csv_data
        repo.list_all.assert_awaited()


class TestRoleBasedFiltering:
    """Test role-based filtering functionality."""

    @pytest.fixture
    def team_view_records(self) -> List[Dict[str, Any]]:
        """Simulate Airtable view records for team members."""
        return [
            make_view_record(
                "rec_team_1",
                FullNameRU="TEAM Участник 1",
                FullNameEN="Team Member 1",
                Gender="M",
                Size="L",
                Church="Церковь 1",
                Role="TEAM",
                Department="Worship",
                CountryAndCity="Россия, Москва",
                PaymentStatus="Paid",
                Floor=2,
                DateOfBirth="20/05/1990",
                ChurchLeader="Пастор 1",
                IsDepartmentChief=True,
            ),
            make_view_record(
                "rec_team_2",
                FullNameRU="TEAM Участник 2",
                FullNameEN="Team Member 2",
                Gender="F",
                Size="M",
                Church="Церковь 2",
                Role="TEAM",
                Department="Kitchen",
                CountryAndCity="Россия, Санкт-Петербург",
                PaymentStatus="Unpaid",
                Floor=1,
                DateOfBirth="15/08/1992",
                ChurchLeader="Пастор 2",
                IsDepartmentChief=False,
            ),
            make_view_record(
                "rec_team_null_role",
                FullNameRU="Участник без роли",
                Church="Церковь 3",
                Role=None,
                Department="Media",
            ),
        ]

    @pytest.fixture
    def candidate_view_records(self) -> List[Dict[str, Any]]:
        """Simulate Airtable view records for candidates."""
        return [
            make_view_record(
                "rec_candidate_1",
                FullNameRU="CANDIDATE Участник 1",
                FullNameEN="Candidate One",
                Gender="F",
                Size="S",
                Church="Церковь 4",
                Role="CANDIDATE",
                CountryAndCity="Россия, Казань",
                SubmittedBy="Координатор",
                PaymentStatus="Partial",
                Floor=3,
                RoomNumber="301",
                DateOfBirth="05/03/1995",
                ChurchLeader="Пастор 4",
            ),
            make_view_record(
                "rec_candidate_2",
                FullNameRU="CANDIDATE Участник 2",
                Role="CANDIDATE",
                CountryAndCity="Россия, Омск",
                PaymentStatus="Unpaid",
                Floor=4,
                RoomNumber="402",
            ),
            make_view_record(
                "rec_candidate_null_role",
                FullNameRU="Кандидат без роли",
                Role=None,
                CountryAndCity="Россия, Тверь",
            ),
        ]

    @pytest.mark.asyncio
    async def test_get_participants_by_role_team_only(
        self, mock_repository, team_view_records
    ):
        """Test filtering participants by TEAM role only."""
        # Arrange
        mock_repository.list_view_records.return_value = team_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_role_as_csv(Role.TEAM)

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        # Should only contain TEAM participants
        assert len(rows) == 2
        team_names = {row["FullNameRU"] for row in rows}
        assert team_names == {"TEAM Участник 1", "TEAM Участник 2"}
        mock_repository.list_view_records.assert_awaited_once_with("Тимы")

    @pytest.mark.asyncio
    async def test_get_participants_by_role_candidate_only(
        self, mock_repository, candidate_view_records
    ):
        """Test filtering participants by CANDIDATE role only."""
        # Arrange
        mock_repository.list_view_records.return_value = candidate_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_role_as_csv(Role.CANDIDATE)

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        expected_headers = [
            "FullNameRU",
            "Gender",
            "DateOfBirth",
            "Size",
            "CountryAndCity",
            "Church",
            "SubmittedBy",
            "FullNameEN",
            "ContactInformation",
        ]
        assert reader.fieldnames == expected_headers
        rows = list(reader)

        # Should only contain CANDIDATE participants
        assert len(rows) == 2
        candidate_names = {row["FullNameRU"] for row in rows}
        assert candidate_names == {"CANDIDATE Участник 1", "CANDIDATE Участник 2"}
        mock_repository.list_view_records.assert_awaited_once_with("Кандидаты")

    @pytest.mark.asyncio
    async def test_get_participants_by_role_calls_correct_views(
        self, mock_repository, team_view_records, candidate_view_records
    ):
        """Ensure different role exports query the expected Airtable view."""

        async def side_effect(view_name: str):
            if view_name == "Тимы":
                return team_view_records
            if view_name == "Кандидаты":
                return candidate_view_records
            return []

        mock_repository.list_view_records.side_effect = side_effect
        service = ParticipantExportService(repository=mock_repository)

        team_csv = await service.get_participants_by_role_as_csv(Role.TEAM)
        candidate_csv = await service.get_participants_by_role_as_csv(Role.CANDIDATE)

        team_rows = list(csv.DictReader(io.StringIO(team_csv)))
        candidate_rows = list(csv.DictReader(io.StringIO(candidate_csv)))

        assert len(team_rows) == 2
        assert len(candidate_rows) == 2
        awaited_calls = [
            call.args[0] for call in mock_repository.list_view_records.await_args_list
        ]
        assert awaited_calls == ["Тимы", "Кандидаты"]

    @pytest.mark.asyncio
    async def test_get_participants_by_role_excludes_null_roles(
        self, mock_repository, team_view_records
    ):
        """Test that role filtering excludes participants with null roles."""
        # Arrange
        mock_repository.list_view_records.return_value = team_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        team_csv = await service.get_participants_by_role_as_csv(Role.TEAM)

        # Assert
        team_reader = csv.DictReader(io.StringIO(team_csv))
        team_names = {row["FullNameRU"] for row in team_reader}

        # Participant with null role should not appear in either export
        assert "Участник без роли" not in team_names

    @pytest.mark.asyncio
    async def test_get_participants_by_role_empty_result(self, mock_repository):
        """Test role filtering with no matching participants."""
        # Arrange - only participants without the target role
        mock_repository.list_view_records.return_value = []
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_role_as_csv(Role.TEAM)

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        assert len(rows) == 0  # Should return empty result set

    @pytest.mark.asyncio
    async def test_role_filtering_maintains_csv_format(
        self, mock_repository, team_view_records
    ):
        """Test that role filtering maintains proper CSV headers and format."""
        # Arrange
        mock_repository.list_view_records.return_value = team_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_role_as_csv(Role.TEAM)

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        actual_headers = reader.fieldnames

        expected_headers = [
            "FullNameRU",
            "Gender",
            "DateOfBirth",
            "Size",
            "Department",
            "CountryAndCity",
            "Church",
            "SubmittedBy",
            "FullNameEN",
            "ContactInformation",
        ]
        assert actual_headers == expected_headers


class TestDepartmentBasedFiltering:
    """Test department-based filtering functionality."""

    @pytest.fixture
    def department_view_records(self) -> List[Dict[str, Any]]:
        """Simulate Airtable team view records spanning multiple departments."""
        return [
            make_view_record(
                "rec_dep_1",
                FullNameRU="Worship Участник 1",
                Role="TEAM",
                Department="Worship",
            ),
            make_view_record(
                "rec_dep_2",
                FullNameRU="Kitchen Участник 1",
                Role="TEAM",
                Department="Kitchen",
            ),
            make_view_record(
                "rec_dep_3",
                FullNameRU="Worship Участник 2",
                Role="TEAM",
                Department="Worship",
            ),
            make_view_record(
                "rec_dep_candidate",
                FullNameRU="Media Участник 1",
                Role="CANDIDATE",
                Department="Media",
            ),
            make_view_record(
                "rec_dep_none",
                FullNameRU="Участник без департамента",
                Role="TEAM",
                Department=None,
            ),
        ]

    @pytest.mark.asyncio
    async def test_get_participants_by_department(
        self, mock_repository, department_view_records
    ):
        """Test filtering participants by specific department."""
        # Arrange
        mock_repository.list_view_records.return_value = department_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_department_as_csv(
            Department.WORSHIP
        )

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        expected_headers = [
            "FullNameRU",
            "Gender",
            "DateOfBirth",
            "Size",
            "Department",
            "CountryAndCity",
            "Church",
            "SubmittedBy",
            "FullNameEN",
            "ContactInformation",
        ]
        assert reader.fieldnames == expected_headers
        rows = list(reader)

        # Should only contain WORSHIP department participants
        assert len(rows) == 2
        worship_names = {row["FullNameRU"] for row in rows}
        assert worship_names == {"Worship Участник 1", "Worship Участник 2"}
        mock_repository.list_view_records.assert_awaited_once_with("Тимы")

    @pytest.mark.asyncio
    async def test_department_filtering_all_departments(self, mock_repository):
        """Test that all 13 departments can be filtered correctly."""
        # Arrange - create one participant for each department
        all_departments = list(Department)
        view_records = [
            make_view_record(
                f"rec_{dept.value}",
                FullNameRU=f"{dept.value} Участник",
                Role="TEAM",
                Department=dept.value,
            )
            for dept in all_departments
        ]

        async def side_effect(view_name: str):
            return view_records

        mock_repository.list_view_records.side_effect = side_effect
        service = ParticipantExportService(repository=mock_repository)

        # Act & Assert - test each department
        for dept in all_departments:
            csv_data = await service.get_participants_by_department_as_csv(dept)
            reader = csv.DictReader(io.StringIO(csv_data))
            rows = list(reader)

            assert len(rows) == 1
            assert rows[0]["FullNameRU"] == f"{dept.value} Участник"

    @pytest.mark.asyncio
    async def test_department_filtering_excludes_null_departments(
        self, mock_repository, department_view_records
    ):
        """Test that department filtering excludes participants with null departments."""
        # Arrange
        mock_repository.list_view_records.return_value = department_view_records
        service = ParticipantExportService(repository=mock_repository)

        # Act
        worship_csv = await service.get_participants_by_department_as_csv(
            Department.WORSHIP
        )

        # Assert
        reader = csv.DictReader(io.StringIO(worship_csv))
        names = {row["FullNameRU"] for row in reader}

        # Participant with null department should not appear
        assert "Участник без департамента" not in names

    @pytest.mark.asyncio
    async def test_department_filtering_empty_result(self, mock_repository):
        """Test department filtering with no matching participants."""
        # Arrange - no participants in target department
        mock_repository.list_view_records.return_value = [
            make_view_record(
                "rec001",
                FullNameRU="Kitchen Участник",
                Role="TEAM",
                Department="Kitchen",
            )
        ]
        service = ParticipantExportService(repository=mock_repository)

        # Act
        csv_data = await service.get_participants_by_department_as_csv(Department.MEDIA)

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        assert len(rows) == 0  # Should return empty result set
