"""
Unit tests for ROEExportService.

Tests the CSV export functionality for ROE including:
- Repository integration
- Participant data hydration for presenters, assistants, and prayer partners
- Field mapping accuracy
- CSV formatting
- Scheduling metadata handling
- Error handling
"""

import csv
import io
import tempfile
from datetime import date
from pathlib import Path
from typing import List, Optional
from unittest.mock import AsyncMock, MagicMock, Mock, call, patch

import pytest

from src.config.field_mappings.roe import ROEFieldMapping
from src.data.repositories.roe_repository import ROERepository
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.roe import ROE
from src.models.participant import Participant, Role, Department
from src.services.roe_export_service import ROEExportService


@pytest.fixture
def mock_roe_repository():
    """Create a mock ROE repository."""
    repo = AsyncMock(spec=ROERepository)
    return repo


@pytest.fixture
def mock_participant_repository():
    """Create a mock participant repository."""
    repo = AsyncMock(spec=ParticipantRepository)
    return repo


@pytest.fixture
def sample_participants():
    """Create sample participant data for hydration testing."""
    return [
        Participant(
            record_id="rec001",
            full_name_ru="Иванов Иван Иванович",
            full_name_en="Ivanov Ivan Ivanovich",
            church="Москва Церковь",
            role=Role.TEAM,
            department=Department.WORSHIP,
            room_number="205",
        ),
        Participant(
            record_id="rec002",
            full_name_ru="Петрова Мария Сергеевна",
            full_name_en="Petrova Maria Sergeevna",
            church="Санкт-Петербург Церковь",
            role=Role.CANDIDATE,
            department=Department.KITCHEN,
            room_number="101",
        ),
        Participant(
            record_id="rec003",
            full_name_ru="Сидоров Петр Александрович",
            full_name_en="Sidorov Petr Alexandrovich",
            church="Екатеринбург Церковь",
            role=Role.TEAM,
            department=Department.MEDIA,
            room_number="302",
        ),
    ]


@pytest.fixture
def sample_roe_sessions():
    """Create sample ROE data for testing."""
    return [
        ROE(
            record_id="rec001",
            roe_topic="Божья любовь",
            roista=["rec001"],
            assistant=["rec002"],
            prayer=["rec003"],
            roe_date=date(2025, 1, 25),
            roe_timing="Morning",
            roe_duration=15,
            roista_church=["Москва Церковь"],
            roista_department=["Worship"],
            roista_room=["205"],
            assistant_church=["Санкт-Петербург Церковь"],
            assistant_department=["Kitchen"],
            assistant_room=["101"],
        ),
        ROE(
            record_id="rec002",
            roe_topic="Прощение",
            roista=["rec002", "rec003"],  # Multiple presenters
            assistant=[],  # No assistant
            prayer=["rec001"],
            roe_date=date(2025, 1, 26),
            roe_timing="Evening",
            roe_duration=20,
            roista_church=["Санкт-Петербург Церковь", "Екатеринбург Церковь"],
            roista_department=["Kitchen", "Media"],
            roista_room=["101", "302"],
        ),
    ]


@pytest.fixture
def export_service(mock_roe_repository, mock_participant_repository):
    """Create a ROEExportService instance with mock repositories."""
    return ROEExportService(
        roe_repository=mock_roe_repository,
        participant_repository=mock_participant_repository
    )


class TestROEExportServiceInit:
    """Test ROEExportService initialization."""

    def test_init_with_repositories(self, mock_roe_repository, mock_participant_repository):
        """Test service initialization with repository dependencies."""
        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository
        )
        assert service.roe_repository == mock_roe_repository
        assert service.participant_repository == mock_participant_repository

    def test_init_without_repositories(self):
        """Test service initialization fails without repositories."""
        with pytest.raises(TypeError):
            ROEExportService()


class TestGetAllROEAsCSV:
    """Test get_all_roe_as_csv method."""

    @pytest.mark.asyncio
    async def test_export_roe_with_hydration(
        self, export_service, mock_roe_repository, mock_participant_repository,
        sample_roe_sessions, sample_participants
    ):
        """Test CSV export with participant data hydration."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 2

        # Check first row
        first_row = rows[0]
        assert first_row["RoeTopic"] == "Божья любовь"
        assert first_row["RoeDate"] == "2025-01-25"
        assert first_row["RoeTiming"] == "Morning"
        assert first_row["RoeDuration"] == "15"
        assert "Иванов Иван Иванович" in first_row["RoistaNames"]
        assert "Петрова Мария Сергеевна" in first_row["AssistantNames"]
        assert "Сидоров Петр Александрович" in first_row["PrayerNames"]

        # Check second row with multiple presenters
        second_row = rows[1]
        assert second_row["RoeTopic"] == "Прощение"
        assert "Петрова Мария Сергеевна" in second_row["RoistaNames"]
        assert "Сидоров Петр Александрович" in second_row["RoistaNames"]
        assert second_row["AssistantNames"] == ""  # No assistant

    @pytest.mark.asyncio
    async def test_export_roe_empty_relationships(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test CSV export with ROE sessions that have empty participant lists."""
        # Arrange
        roe_sessions = [
            ROE(
                record_id="rec001",
                roe_topic="Пустая сессия",
                roista=[],
                assistant=[],
                prayer=[],
                roe_date=date(2025, 1, 25),
                roe_timing="Morning",
                roe_duration=10,
            )
        ]
        mock_roe_repository.list_all.return_value = roe_sessions

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["RoistaNames"] == ""
        assert rows[0]["AssistantNames"] == ""
        assert rows[0]["PrayerNames"] == ""

    @pytest.mark.asyncio
    async def test_export_roe_missing_participants(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test CSV export when some participant IDs don't exist."""
        # Arrange
        roe_sessions = [
            ROE(
                record_id="rec001",
                roe_topic="Сессия с отсутствующими участниками",
                roista=["rec001", "rec999"],  # rec999 doesn't exist
                assistant=["rec888"],  # rec888 doesn't exist
                prayer=["rec002"],
                roe_date=date(2025, 1, 25),
            )
        ]
        sample_participants = [
            Participant(
                record_id="rec001",
                full_name_ru="Существующий участник 1",
            ),
            Participant(
                record_id="rec002",
                full_name_ru="Существующий участник 2",
            ),
        ]

        mock_roe_repository.list_all.return_value = roe_sessions
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        # Should only include existing participants
        assert rows[0]["RoistaNames"] == "Существующий участник 1"
        assert rows[0]["AssistantNames"] == ""  # Missing participant excluded
        assert rows[0]["PrayerNames"] == "Существующий участник 2"

    @pytest.mark.asyncio
    async def test_csv_headers_match_field_mapping(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test that CSV headers match the ROE field mapping."""
        # Arrange
        mock_roe_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        headers = reader.fieldnames

        expected_headers = export_service._get_csv_headers()
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def test_export_with_progress_callback(
        self, mock_roe_repository, mock_participant_repository, sample_roe_sessions
    ):
        """Test CSV export with progress tracking."""
        # Arrange
        progress_calls = []

        def progress_callback(current: int, total: int):
            progress_calls.append((current, total))

        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
            progress_callback=progress_callback
        )

        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        await service.get_all_roe_as_csv()

        # Assert
        assert len(progress_calls) > 0
        assert progress_calls[0] == (0, 2)  # Initial progress
        assert progress_calls[-1][0] == 2   # Final progress


class TestParticipantHydration:
    """Test participant data hydration functionality."""

    @pytest.mark.asyncio
    async def test_hydrate_participant_names(
        self, export_service, mock_participant_repository, sample_participants
    ):
        """Test hydration of participant names from IDs."""
        # Arrange
        participant_ids = ["rec001", "rec002"]
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        names = await export_service._hydrate_participant_names(participant_ids)

        # Assert
        expected_names = ["Иванов Иван Иванович", "Петрова Мария Сергеевна"]
        assert names == expected_names

    @pytest.mark.asyncio
    async def test_hydrate_participant_names_with_missing_ids(
        self, export_service, mock_participant_repository
    ):
        """Test hydration when some participant IDs don't exist."""
        # Arrange
        participant_ids = ["rec001", "rec999"]
        sample_participant = Participant(
            record_id="rec001",
            full_name_ru="Существующий участник",
        )

        mock_participant_repository.get_by_id.side_effect = lambda id: (
            sample_participant if id == "rec001" else None
        )

        # Act
        names = await export_service._hydrate_participant_names(participant_ids)

        # Assert
        # Should only include existing participant
        assert names == ["Существующий участник"]

    @pytest.mark.asyncio
    async def test_hydrate_participant_names_empty_list(
        self, export_service, mock_participant_repository
    ):
        """Test hydration with empty participant ID list."""
        # Arrange
        participant_ids = []

        # Act
        names = await export_service._hydrate_participant_names(participant_ids)

        # Assert
        assert names == []


class TestSchedulingAndMetadata:
    """Test handling of scheduling and metadata fields."""

    @pytest.mark.asyncio
    async def test_export_roe_with_scheduling_data(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test CSV export with complete scheduling metadata."""
        # Arrange
        roe_sessions = [
            ROE(
                record_id="rec001",
                roe_topic="Планированная сессия",
                roista=["rec001"],
                roe_date=date(2025, 2, 15),
                roe_timing="Afternoon Session 2",
                roe_duration=25,
            )
        ]
        mock_roe_repository.list_all.return_value = roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        row = rows[0]
        assert row["RoeDate"] == "2025-02-15"
        assert row["RoeTiming"] == "Afternoon Session 2"
        assert row["RoeDuration"] == "25"

    @pytest.mark.asyncio
    async def test_export_roe_with_null_scheduling_data(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test CSV export with null scheduling metadata."""
        # Arrange
        roe_sessions = [
            ROE(
                record_id="rec001",
                roe_topic="Незапланированная сессия",
                roista=["rec001"],
                roe_date=None,
                roe_timing=None,
                roe_duration=None,
            )
        ]
        mock_roe_repository.list_all.return_value = roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        row = rows[0]
        assert row["RoeDate"] == ""
        assert row["RoeTiming"] == ""
        assert row["RoeDuration"] == ""


class TestCSVFormattingAndFileOperations:
    """Test CSV formatting and file operations."""

    @pytest.mark.asyncio
    async def test_save_to_file(
        self, export_service, mock_roe_repository, mock_participant_repository,
        sample_roe_sessions
    ):
        """Test saving CSV export to file."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        file_path = await export_service.save_to_file()

        # Assert
        assert Path(file_path).exists()
        assert file_path.endswith(".csv")

        # Verify file content
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "RoeTopic" in content
            assert "Божья любовь" in content

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_estimate_file_size(
        self, export_service, mock_roe_repository
    ):
        """Test file size estimation."""
        # Arrange
        sample_roe_sessions = [
            ROE(record_id=f"rec{i}", roe_topic=f"Topic {i}")
            for i in range(50)
        ]
        mock_roe_repository.list_all.return_value = sample_roe_sessions

        # Act
        estimated_size = await export_service.estimate_file_size()

        # Assert
        assert estimated_size > 0
        assert isinstance(estimated_size, int)