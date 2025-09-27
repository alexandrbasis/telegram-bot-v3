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
from src.data.repositories.participant_repository import ParticipantRepository
from src.data.repositories.roe_repository import ROERepository
from src.models.participant import Department, Participant, Role
from src.models.roe import ROE
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
        participant_repository=mock_participant_repository,
    )


class TestROEExportServiceInit:
    """Test ROEExportService initialization."""

    def test_init_with_repositories(
        self, mock_roe_repository, mock_participant_repository
    ):
        """Test service initialization with repository dependencies."""
        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
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
        self,
        export_service,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
        sample_participants,
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
        assert reader.fieldnames == [
            "#",
            "RoeTopic",
            "Roista",
            "RoeDate",
            "RoeTiming",
            "RoeDuration",
            "Assistant",
            "Prayer",
        ]
        rows = list(reader)

        assert len(rows) == 2

        # Check first row
        first_row = rows[0]
        assert first_row["RoeTopic"] == "Божья любовь"
        assert first_row["RoeDate"] == "2025-01-25"
        assert first_row["RoeTiming"] == "Morning"
        assert first_row["RoeDuration"] == "15"
        assert "Иванов Иван Иванович" in first_row["Roista"]
        assert "Петрова Мария Сергеевна" in first_row["Assistant"]
        assert "Сидоров Петр Александрович" in first_row["Prayer"]

        # Check second row with multiple presenters
        second_row = rows[1]
        assert second_row["RoeTopic"] == "Прощение"
        assert "Петрова Мария Сергеевна" in second_row["Roista"]
        assert "Сидоров Петр Александрович" in second_row["Roista"]
        assert second_row["Assistant"] == ""  # No assistant

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
        assert rows[0]["Roista"] == ""
        assert rows[0]["Assistant"] == ""
        assert rows[0]["Prayer"] == ""

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
        assert rows[0]["Roista"] == "Существующий участник 1"
        assert rows[0]["Assistant"] == ""  # Missing participant excluded
        assert rows[0]["Prayer"] == "Существующий участник 2"

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
            progress_callback=progress_callback,
        )

        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        await service.get_all_roe_as_csv()

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
        self,
        export_service,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
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
    async def test_estimate_file_size(self, export_service, mock_roe_repository):
        """Test file size estimation."""
        # Arrange
        sample_roe_sessions = [
            ROE(record_id=f"rec{i}", roe_topic=f"Topic {i}") for i in range(50)
        ]
        mock_roe_repository.list_all.return_value = sample_roe_sessions

        # Act
        estimated_size = await export_service.estimate_file_size()

        # Assert
        assert estimated_size > 0
        assert isinstance(estimated_size, int)


class TestLineNumberIntegration:
    """Test line number integration in ROE CSV exports."""

    @pytest.mark.asyncio
    async def test_csv_headers_include_line_number_column(
        self, export_service, mock_roe_repository
    ):
        """Test that CSV headers include line number column as first column."""
        # Arrange
        mock_roe_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        headers = reader.fieldnames

        # Line number column should be first
        assert headers[0] == "#"
        assert headers == [
            "#",
            "RoeTopic",
            "Roista",
            "RoeDate",
            "RoeTiming",
            "RoeDuration",
            "Assistant",
            "Prayer",
        ]

    @pytest.mark.asyncio
    async def test_csv_rows_include_sequential_line_numbers(
        self,
        export_service,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
    ):
        """Test that CSV rows include sequential line numbers starting from 1."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 2
        assert rows[0]["#"] == "1"
        assert rows[1]["#"] == "2"

    @pytest.mark.asyncio
    async def test_line_numbers_with_empty_list(
        self, export_service, mock_roe_repository
    ):
        """Test line numbers with empty ROE list."""
        # Arrange
        mock_roe_repository.list_all.return_value = []

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)
        headers = reader.fieldnames

        # Should have headers with line number column but no data rows
        assert headers[0] == "#"
        assert len(rows) == 0

    @pytest.mark.asyncio
    async def test_line_numbers_with_large_list(
        self, export_service, mock_roe_repository, mock_participant_repository
    ):
        """Test line numbers with large ROE list (3+ digit numbers)."""
        # Arrange
        large_roe_list = []
        for i in range(120):
            large_roe_list.append(
                ROE(
                    record_id=f"rec{i:03d}",
                    roe_topic=f"Topic {i}",
                    roista=[],
                    assistant=[],
                    prayer=[],
                    roe_date=date(2025, 1, 25),
                    roe_timing="Morning",
                    roe_duration=15,
                )
            )

        mock_roe_repository.list_all.return_value = large_roe_list
        mock_participant_repository.get_by_id.return_value = None

        # Act
        csv_data = await export_service.get_all_roe_as_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert len(rows) == 120
        # With 120 rows, line numbers should be right-aligned to width 3
        assert rows[0]["#"] == "  1"  # First row (padded to 3 chars)
        assert rows[99]["#"] == "100"  # 3-digit number
        assert rows[119]["#"] == "120"  # 3-digit number

    @pytest.mark.asyncio
    async def test_line_numbers_preserve_data_integrity(
        self,
        export_service,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
        sample_participants,
    ):
        """Test that adding line numbers doesn't affect other data columns."""
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

        # Verify first row data integrity with line numbers
        first_row = rows[0]
        assert first_row["#"] == "1"
        assert first_row["RoeTopic"] == "Божья любовь"
        assert first_row["RoeDate"] == "2025-01-25"
        assert first_row["RoeTiming"] == "Morning"
        assert first_row["RoeDuration"] == "15"
        assert "Иванов Иван Иванович" in first_row["Roista"]
        assert "Петрова Мария Сергеевна" in first_row["Assistant"]
        assert "Сидоров Петр Александрович" in first_row["Prayer"]

        # Verify second row data integrity with line numbers
        second_row = rows[1]
        assert second_row["#"] == "2"
        assert second_row["RoeTopic"] == "Прощение"
        assert second_row["RoeDate"] == "2025-01-26"
        assert second_row["RoeTiming"] == "Evening"
        assert second_row["RoeDuration"] == "20"

    @pytest.mark.asyncio
    async def test_line_numbers_in_saved_file(
        self,
        export_service,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
    ):
        """Test that line numbers appear in saved CSV files."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions
        mock_participant_repository.get_by_id.return_value = None

        # Act
        file_path = await export_service.save_to_file()

        # Assert
        assert Path(file_path).exists()

        # Verify file content includes line numbers
        with open(file_path, "r", encoding="utf-8-sig") as f:
            content = f.read()
            # Check that line numbers are present in headers and data
            assert (
                "#,RoeTopic,Roista,RoeDate,RoeTiming,RoeDuration,Assistant,Prayer"
                in content
            )
            assert "1,Божья любовь" in content
            assert "2,Прощение" in content

        # Cleanup
        Path(file_path).unlink()


class TestAsyncExportInterface:
    """Test async export interface methods."""

    @pytest.mark.asyncio
    async def test_export_to_csv_async_method_exists(
        self,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
        sample_participants,
    ):
        """Test that export_to_csv_async method exists and works like get_all_roe_as_csv."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions

        # Mock participant hydration
        async def mock_get_by_id(participant_id):
            for p in sample_participants:
                if p.record_id == participant_id:
                    return p
            return None

        mock_participant_repository.get_by_id = mock_get_by_id

        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
        )

        # Act
        csv_data = await service.export_to_csv_async()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        # Should have same format as existing method
        assert "#" in reader.fieldnames
        assert len(rows) == len(sample_roe_sessions)
        assert rows[0]["#"] == "1"

    def test_export_to_csv_sync_wrapper_no_running_loop(
        self,
        mock_roe_repository,
        mock_participant_repository,
        sample_roe_sessions,
        sample_participants,
    ):
        """Test synchronous export_to_csv wrapper when no event loop is running."""
        # Arrange
        mock_roe_repository.list_all.return_value = sample_roe_sessions

        # Mock participant hydration
        async def mock_get_by_id(participant_id):
            for p in sample_participants:
                if p.record_id == participant_id:
                    return p
            return None

        mock_participant_repository.get_by_id = mock_get_by_id

        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
        )

        # Act
        csv_data = service.export_to_csv()

        # Assert
        reader = csv.DictReader(io.StringIO(csv_data))
        rows = list(reader)

        assert "#" in reader.fieldnames
        assert len(rows) == len(sample_roe_sessions)

    @pytest.mark.asyncio
    async def test_export_to_csv_sync_wrapper_raises_with_active_loop(
        self, mock_roe_repository, mock_participant_repository
    ):
        """Test that sync wrapper raises error when called from async context."""
        # Arrange
        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
        )

        # Act & Assert
        with pytest.raises(
            RuntimeError, match="cannot be called while an event loop is running"
        ):
            service.export_to_csv()


class TestViewBasedExport:
    """Test view-based export functionality."""

    @pytest.mark.asyncio
    async def test_roe_export_uses_configured_view_name(
        self, mock_roe_repository, mock_participant_repository, monkeypatch
    ):
        """Test that ROE export uses view name from settings."""
        # Arrange
        from src.config.settings import Settings

        # Set required environment variables for test
        monkeypatch.setenv("AIRTABLE_API_KEY", "test_key")
        monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test_token")
        monkeypatch.setenv("AIRTABLE_ROE_EXPORT_VIEW", "Custom ROE View")

        # Create settings with custom view name from environment
        test_settings = Settings()

        # Mock repository to return view records with specific field order
        view_records = [
            {
                "id": "rec1",
                "fields": {
                    "RoeDate": "2025-01-15",
                    "RoeTopic": "Божья любовь",
                    "Roista": ["rec_p1"],
                    "RoeTiming": "09:00-10:30",
                }
            }
        ]
        mock_roe_repository.list_view_records.return_value = view_records

        # Mock participant hydration
        test_participant = Participant(
            record_id="rec_p1",
            full_name_ru="Иванов Иван",
            role=Role.TEAM,
            department=Department.WORSHIP
        )
        mock_participant_repository.get_by_id.return_value = test_participant

        service = ROEExportService(
            roe_repository=mock_roe_repository,
            participant_repository=mock_participant_repository,
            settings=test_settings
        )

        # Act
        csv_data = await service.get_all_roe_as_csv()

        # Assert
        # Verify the correct view name was used
        mock_roe_repository.list_view_records.assert_called_once_with(
            "Custom ROE View"
        )

        # Verify headers are in view order
        reader = csv.DictReader(io.StringIO(csv_data))
        actual_headers = reader.fieldnames

        # Headers should be in the order from the view (with # first)
        expected_headers = [
            "#",
            "RoeDate",
            "RoeTopic",
            "Roista",
            "RoeTiming",
        ]
        assert actual_headers == expected_headers

        # Verify participant hydration worked
        rows = list(reader)
        assert len(rows) == 1
        assert rows[0]["Roista"] == "Иванов Иван"
