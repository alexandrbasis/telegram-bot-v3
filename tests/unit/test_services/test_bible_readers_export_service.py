"""
Unit tests for BibleReadersExportService.

Tests the CSV export functionality for BibleReaders including:
- Repository integration
- Participant data hydration
- Field mapping accuracy
- CSV formatting
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

from src.config.field_mappings.bible_readers import BibleReadersFieldMapping
from src.data.repositories.bible_readers_repository import BibleReadersRepository
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.bible_readers import BibleReader
from src.models.participant import Department, Participant, Role
from src.services.bible_readers_export_service import BibleReadersExportService


@pytest.fixture
def mock_bible_readers_repository():
    """Create a mock BibleReaders repository."""
    repo = AsyncMock(spec=BibleReadersRepository)
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
    ]


@pytest.fixture
def sample_bible_readers():
    """Create sample BibleReader data for testing."""
    return [
        BibleReader(
            record_id="rec001",
            where="Утренняя служба",
            participants=["rec001", "rec002"],
            churches=["Москва Церковь", "Санкт-Петербург Церковь"],
            room_numbers=["205", "101"],
            when=date(2025, 1, 25),
            bible="Псалом 23:1-6",
        ),
        BibleReader(
            record_id="rec002",
            where="Вечерняя служба",
            participants=["rec001"],
            churches=["Москва Церковь"],
            room_numbers=["205"],
            when=date(2025, 1, 26),
            bible="Иоанн 3:16",
        ),
    ]


@pytest.fixture
def export_service(mock_bible_readers_repository, mock_participant_repository):
    """Create a BibleReadersExportService instance with mock repositories."""
    return BibleReadersExportService(
        bible_readers_repository=mock_bible_readers_repository,
        participant_repository=mock_participant_repository,
    )


class TestBibleReadersExportServiceInit:
    """Test BibleReadersExportService initialization."""

    def test_init_with_repositories(
        self, mock_bible_readers_repository, mock_participant_repository
    ):
        """Test service initialization with repository dependencies."""
        service = BibleReadersExportService(
            bible_readers_repository=mock_bible_readers_repository,
            participant_repository=mock_participant_repository,
        )
        assert service.bible_readers_repository == mock_bible_readers_repository
        assert service.participant_repository == mock_participant_repository

    def test_init_without_repositories(self):
        """Test service initialization fails without repositories."""
        with pytest.raises(TypeError):
            BibleReadersExportService()


class TestGetAllBibleReadersAsCSV:
    """Test get_all_bible_readers_as_csv method."""

    @pytest.mark.asyncio
    async def test_export_bible_readers_with_hydration(
        self,
        export_service,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
        sample_participants,
    ):
        """Test CSV export with participant data hydration."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        assert reader.fieldnames == ["#", "Where", "Participants", "When", "Bible"]
        rows = list(reader)

        assert len(rows) == 2

        # Check first row
        first_row = rows[0]
        assert first_row["Where"] == "Утренняя служба"
        assert first_row["When"] == "2025-01-25"
        assert first_row["Bible"] == "Псалом 23:1-6"
        assert "Иванов Иван Иванович" in first_row["Participants"]
        assert "Петрова Мария Сергеевна" in first_row["Participants"]

    @pytest.mark.asyncio
    async def test_export_bible_readers_empty_participants(
        self, export_service, mock_bible_readers_repository, mock_participant_repository
    ):
        """Test CSV export with Bible readers that have empty participant lists."""
        # Arrange
        bible_readers = [
            BibleReader(
                record_id="rec001",
                where="Пустая служба",
                participants=[],
                when=date(2025, 1, 25),
                bible="Псалом 1:1",
            )
        ]
        mock_bible_readers_repository.list_all.return_value = bible_readers

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        assert rows[0]["Participants"] == ""

    @pytest.mark.asyncio
    async def test_export_bible_readers_missing_participants(
        self, export_service, mock_bible_readers_repository, mock_participant_repository
    ):
        """Test CSV export when some participant IDs don't exist."""
        # Arrange
        bible_readers = [
            BibleReader(
                record_id="rec001",
                where="Служба с отсутствующими участниками",
                participants=["rec001", "rec999"],  # rec999 doesn't exist
                when=date(2025, 1, 25),
                bible="Псалом 1:1",
            )
        ]
        sample_participants = [
            Participant(
                record_id="rec001",
                full_name_ru="Существующий участник",
            )
        ]

        mock_bible_readers_repository.list_all.return_value = bible_readers
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 1
        # Should only include existing participant
        assert rows[0]["Participants"] == "Существующий участник"

    @pytest.mark.asyncio
    async def test_csv_headers_match_field_mapping(
        self, export_service, mock_bible_readers_repository, mock_participant_repository
    ):
        """Test that CSV headers match the BibleReaders field mapping."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        headers = reader.fieldnames

        expected_headers = export_service._get_csv_headers()
        assert headers == expected_headers

    @pytest.mark.asyncio
    async def test_export_with_progress_callback(
        self,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
    ):
        """Test CSV export with progress tracking."""
        # Arrange
        progress_calls = []

        def progress_callback(current: int, total: int):
            progress_calls.append((current, total))

        service = BibleReadersExportService(
            bible_readers_repository=mock_bible_readers_repository,
            participant_repository=mock_participant_repository,
            progress_callback=progress_callback,
        )

        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.return_value = None

        # Act
        await service.get_all_bible_readers_as_csv()

        # Assert
        assert len(progress_calls) > 0
        assert progress_calls[0] == (0, 2)  # Initial progress
        assert progress_calls[-1][0] == 2  # Final progress


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


class TestCSVFormattingAndFileOperations:
    """Test CSV formatting and file operations."""

    @pytest.mark.asyncio
    async def test_save_to_file(
        self,
        export_service,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
    ):
        """Test saving CSV export to file."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.return_value = None

        # Act
        file_path = await export_service.save_to_file()

        # Assert
        assert Path(file_path).exists()
        assert file_path.endswith(".csv")

        # Verify file content
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            assert "Where" in content
            assert "Утренняя служба" in content

        # Cleanup
        Path(file_path).unlink()

    @pytest.mark.asyncio
    async def test_estimate_file_size(
        self, export_service, mock_bible_readers_repository
    ):
        """Test file size estimation."""
        # Arrange
        sample_bible_readers = [
            BibleReader(record_id=f"rec{i}", where=f"Service {i}") for i in range(100)
        ]
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers

        # Act
        estimated_size = await export_service.estimate_file_size()

        # Assert
        assert estimated_size > 0
        assert isinstance(estimated_size, int)


class TestLineNumberIntegration:
    """Test line number integration in BibleReaders CSV exports."""

    @pytest.mark.asyncio
    async def test_csv_headers_include_line_number_column(
        self, export_service, mock_bible_readers_repository
    ):
        """Test that CSV headers include line number column as first column."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        headers = reader.fieldnames

        # Line number column should be first
        assert headers[0] == "#"
        assert headers == ["#", "Where", "Participants", "When", "Bible"]

    @pytest.mark.asyncio
    async def test_csv_rows_include_sequential_line_numbers(
        self,
        export_service,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
    ):
        """Test that CSV rows include sequential line numbers starting from 1."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["#"] == "1"
        assert rows[1]["#"] == "2"

    @pytest.mark.asyncio
    async def test_line_numbers_with_empty_list(
        self, export_service, mock_bible_readers_repository
    ):
        """Test line numbers with empty Bible readers list."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        headers = reader.fieldnames

        # Should have headers with line number column but no data rows
        assert headers[0] == "#"
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_line_numbers_with_large_list(
        self, export_service, mock_bible_readers_repository, mock_participant_repository
    ):
        """Test line numbers with large Bible readers list (3+ digit numbers)."""
        # Arrange
        large_bible_readers_list = []
        for i in range(150):
            large_bible_readers_list.append(
                BibleReader(
                    record_id=f"rec{i:03d}",
                    where=f"Service {i}",
                    participants=[],
                    when=date(2025, 1, 25),
                    bible=f"Psalm {i}:1",
                )
            )

        mock_bible_readers_repository.list_all.return_value = large_bible_readers_list
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 150
        # With 150 rows, line numbers should be right-aligned to width 3
        assert rows[0]["#"] == "  1"    # First row (padded to 3 chars)
        assert rows[99]["#"] == "100"   # 3-digit number
        assert rows[149]["#"] == "150"  # 3-digit number

    @pytest.mark.asyncio
    async def test_line_numbers_preserve_data_integrity(
        self,
        export_service,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
        sample_participants,
    ):
        """Test that adding line numbers doesn't affect other data columns."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.side_effect = lambda id: next(
            (p for p in sample_participants if p.record_id == id), None
        )

        # Act
        csv_data = await export_service.get_all_bible_readers_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        # Verify first row data integrity with line numbers
        first_row = rows[0]
        assert first_row["#"] == "1"
        assert first_row["Where"] == "Утренняя служба"
        assert first_row["When"] == "2025-01-25"
        assert first_row["Bible"] == "Псалом 23:1-6"
        assert "Иванов Иван Иванович" in first_row["Participants"]
        assert "Петрова Мария Сергеевна" in first_row["Participants"]

        # Verify second row data integrity with line numbers
        second_row = rows[1]
        assert second_row["#"] == "2"
        assert second_row["Where"] == "Вечерняя служба"
        assert second_row["When"] == "2025-01-26"
        assert second_row["Bible"] == "Иоанн 3:16"

    @pytest.mark.asyncio
    async def test_line_numbers_in_saved_file(
        self,
        export_service,
        mock_bible_readers_repository,
        mock_participant_repository,
        sample_bible_readers,
    ):
        """Test that line numbers appear in saved CSV files."""
        # Arrange
        mock_bible_readers_repository.list_all.return_value = sample_bible_readers
        mock_participant_repository.get_by_id.return_value = None

        # Act
        file_path = await export_service.save_to_file()

        # Assert
        assert Path(file_path).exists()

        # Verify file content includes line numbers
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            # Check that line numbers are present in headers and data
            assert "#,Where,Participants,When,Bible" in content
            assert "1,Утренняя служба" in content
            assert "2,Вечерняя служба" in content

        # Cleanup
        Path(file_path).unlink()
