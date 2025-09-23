"""
Tests for Israel Missions 2025 import service.

Tests cover the complete import workflow including CSV processing, validation,
duplicate detection, dry-run vs live mode, error handling, and reporting.
"""

import asyncio
import csv
import json
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, Mock, patch
from datetime import datetime

import pytest

from src.services.israel_missions_import_service import (
    IsraelMissionsImportService,
    ImportMode,
    ImportResult,
    ImportRecordResult,
    ImportSummary,
)
from src.data.repositories.participant_repository import (
    DuplicateError,
    RepositoryError,
    ValidationError,
)
from src.models.participant import Participant


@pytest.fixture
def mock_repository():
    """Create a mock participant repository."""
    repository = AsyncMock()
    return repository


@pytest.fixture
def import_service(mock_repository):
    """Create import service with mock repository."""
    return IsraelMissionsImportService(
        participant_repository=mock_repository,
        rate_limit_delay=0.01  # Fast for testing
    )


@pytest.fixture
def sample_csv_data():
    """Sample CSV data for testing."""
    return [
        {
            "FullNameRU": "Иван Петров",
            "DateOfBirth": "7/2/1992",
            "Gender": "Male",
            "Size": "L",
            "ContactInformation": "+7-495-123-4567",
            "CountryAndCity": "Москва, Россия",
            "Role": "TEAM"
        },
        {
            "FullNameRU": "Мария Иванова",
            "DateOfBirth": "12/25/1988",
            "Gender": "Female",
            "Size": "M",
            "ContactInformation": "maria@example.com",
            "CountryAndCity": "Санкт-Петербург, Россия",
            "Role": "CANDIDATE"
        }
    ]


@pytest.fixture
def csv_file(sample_csv_data):
    """Create a temporary CSV file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        if sample_csv_data:
            writer = csv.DictWriter(f, fieldnames=sample_csv_data[0].keys())
            writer.writeheader()
            writer.writerows(sample_csv_data)

        temp_path = Path(f.name)

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()


class TestImportSummary:
    """Test ImportSummary functionality."""

    def test_import_summary_initialization(self):
        """Test ImportSummary is properly initialized."""
        summary = ImportSummary()

        assert summary.total_rows == 0
        assert summary.successful == 0
        assert summary.duplicates_skipped == 0
        assert summary.validation_errors == 0
        assert summary.api_errors == 0
        assert summary.transformation_errors == 0
        assert summary.records == []
        assert summary.end_time is None

    def test_add_result_success(self):
        """Test adding successful results."""
        summary = ImportSummary()
        result = ImportRecordResult(
            row_number=1,
            result=ImportResult.SUCCESS,
            message="Created successfully"
        )

        summary.add_result(result)

        assert summary.total_rows == 1
        assert summary.successful == 1
        assert len(summary.records) == 1

    def test_add_result_various_types(self):
        """Test adding different result types."""
        summary = ImportSummary()

        # Add one of each type
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(2, ImportResult.DUPLICATE_SKIP, "Duplicate"))
        summary.add_result(ImportRecordResult(3, ImportResult.VALIDATION_ERROR, "Invalid"))
        summary.add_result(ImportRecordResult(4, ImportResult.API_ERROR, "API fail"))
        summary.add_result(ImportRecordResult(5, ImportResult.TRANSFORMATION_ERROR, "Transform fail"))

        assert summary.total_rows == 5
        assert summary.successful == 1
        assert summary.duplicates_skipped == 1
        assert summary.validation_errors == 1
        assert summary.api_errors == 1
        assert summary.transformation_errors == 1

    def test_success_rate_calculation(self):
        """Test success rate calculation."""
        summary = ImportSummary()

        # Add 3 successful out of 5 total
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(2, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(3, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(4, ImportResult.VALIDATION_ERROR, "Error"))
        summary.add_result(ImportRecordResult(5, ImportResult.API_ERROR, "Error"))

        assert summary.get_success_rate() == 60.0

    def test_empty_summary_success_rate(self):
        """Test success rate calculation for empty summary."""
        summary = ImportSummary()
        assert summary.get_success_rate() == 0.0

    def test_is_successful_with_errors(self):
        """Test is_successful returns False when errors exist."""
        summary = ImportSummary()
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(2, ImportResult.VALIDATION_ERROR, "Error"))

        assert summary.is_successful() is False

    def test_is_successful_with_duplicates_only(self):
        """Test is_successful returns True when only duplicates (no errors)."""
        summary = ImportSummary()
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "OK"))
        summary.add_result(ImportRecordResult(2, ImportResult.DUPLICATE_SKIP, "Duplicate"))

        assert summary.is_successful() is True


class TestImportService:
    """Test IsraelMissionsImportService functionality."""

    def test_service_initialization(self, mock_repository):
        """Test service initializes correctly."""
        service = IsraelMissionsImportService(
            participant_repository=mock_repository,
            rate_limit_delay=0.5
        )

        assert service.repository == mock_repository
        assert service.rate_limit_delay == 0.5
        assert service._duplicate_cache == {}

    @pytest.mark.asyncio
    async def test_dry_run_import_successful(self, import_service, csv_file):
        """Test dry-run import with successful validation."""
        summary = await import_service.import_from_csv(
            csv_file,
            mode=ImportMode.DRY_RUN
        )

        assert summary.total_rows == 2
        assert summary.successful == 2
        assert summary.validation_errors == 0
        assert summary.api_errors == 0
        assert summary.is_successful()

        # Verify no actual repository calls were made
        import_service.repository.create.assert_not_called()

    @pytest.mark.asyncio
    async def test_live_import_successful(self, import_service, csv_file):
        """Test live import with successful creation."""
        # Mock successful participant creation
        mock_participant = Mock(spec=Participant)
        mock_participant.record_id = "recABC123"
        import_service.repository.create.return_value = mock_participant

        # Mock Participant.from_airtable_fields to avoid actual instantiation
        with patch('src.services.israel_missions_import_service.Participant') as mock_participant_class:
            mock_participant_class.from_airtable_fields.return_value = Mock(spec=Participant)

            summary = await import_service.import_from_csv(
                csv_file,
                mode=ImportMode.LIVE
            )

        assert summary.total_rows == 2
        assert summary.successful == 2
        assert summary.validation_errors == 0

        # Verify repository was called for each record
        assert import_service.repository.create.call_count == 2

    @pytest.mark.asyncio
    async def test_import_with_validation_errors(self, import_service):
        """Test import handles validation errors correctly."""
        # Create CSV with missing required fields
        invalid_data = [{"FullNameRU": "", "ContactInformation": ""}]  # Empty required fields

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["FullNameRU", "ContactInformation"])
            writer.writeheader()
            writer.writerows(invalid_data)
            csv_path = Path(f.name)

        try:
            summary = await import_service.import_from_csv(csv_path, mode=ImportMode.DRY_RUN)

            assert summary.total_rows == 1
            assert summary.successful == 0
            assert summary.validation_errors == 1
            assert not summary.is_successful()

            # Check error message contains missing fields
            error_record = summary.records[0]
            assert "Missing required fields" in error_record.message

        finally:
            csv_path.unlink()

    @pytest.mark.asyncio
    async def test_import_with_duplicate_detection(self, import_service, csv_file):
        """Test duplicate detection during live import."""
        # First call succeeds, second raises DuplicateError
        mock_participant = Mock(spec=Participant)
        mock_participant.record_id = "recABC123"

        import_service.repository.create.side_effect = [
            mock_participant,  # First record succeeds
            DuplicateError("Duplicate participant")  # Second record fails
        ]

        with patch('src.services.israel_missions_import_service.Participant') as mock_participant_class:
            mock_participant_class.from_airtable_fields.return_value = Mock(spec=Participant)

            summary = await import_service.import_from_csv(
                csv_file,
                mode=ImportMode.LIVE
            )

        assert summary.total_rows == 2
        assert summary.successful == 1
        assert summary.duplicates_skipped == 1
        assert summary.is_successful()  # Duplicates don't count as errors

    @pytest.mark.asyncio
    async def test_import_with_api_errors(self, import_service, csv_file):
        """Test handling of API errors during live import."""
        import_service.repository.create.side_effect = RepositoryError("API connection failed")

        with patch('src.services.israel_missions_import_service.Participant') as mock_participant_class:
            mock_participant_class.from_airtable_fields.return_value = Mock(spec=Participant)

            summary = await import_service.import_from_csv(
                csv_file,
                mode=ImportMode.LIVE
            )

        assert summary.total_rows == 2
        assert summary.successful == 0
        assert summary.api_errors == 2
        assert not summary.is_successful()

    @pytest.mark.asyncio
    async def test_import_nonexistent_file(self, import_service):
        """Test import raises FileNotFoundError for missing file."""
        with pytest.raises(FileNotFoundError):
            await import_service.import_from_csv("nonexistent.csv")

    @pytest.mark.asyncio
    async def test_import_with_max_records_limit(self, import_service, csv_file):
        """Test import respects max_records parameter."""
        summary = await import_service.import_from_csv(
            csv_file,
            mode=ImportMode.DRY_RUN,
            max_records=1
        )

        assert summary.total_rows == 1  # Should only process 1 record despite CSV having 2

    @pytest.mark.asyncio
    async def test_rate_limiting_in_live_mode(self, import_service, csv_file):
        """Test rate limiting is applied in live mode."""
        mock_participant = Mock(spec=Participant)
        mock_participant.record_id = "recABC123"
        import_service.repository.create.return_value = mock_participant

        with patch('src.services.israel_missions_import_service.Participant') as mock_participant_class:
            mock_participant_class.from_airtable_fields.return_value = Mock(spec=Participant)

            with patch('asyncio.sleep') as mock_sleep:
                await import_service.import_from_csv(csv_file, mode=ImportMode.LIVE)

                # Should have called sleep for rate limiting (2 records = 2 sleep calls)
                assert mock_sleep.call_count == 2
                mock_sleep.assert_called_with(0.01)  # Our test delay

    @pytest.mark.asyncio
    async def test_duplicate_cache_functionality(self, import_service):
        """Test duplicate cache works within a session."""
        # Test _cache_duplicate_keys method
        import_service._cache_duplicate_keys("123456789", "john|1990", "recABC123")

        assert "123456789" in import_service._duplicate_cache
        assert "john|1990" in import_service._duplicate_cache
        assert import_service._duplicate_cache["123456789"] == "recABC123"

        # Test _check_for_duplicates method
        duplicate_info = await import_service._check_for_duplicates("123456789", "")
        assert "contact key '123456789' (cached)" in duplicate_info

        duplicate_info = await import_service._check_for_duplicates("", "john|1990")
        assert "name+DOB key 'john|1990' (cached)" in duplicate_info

        # Test no duplicate found
        duplicate_info = await import_service._check_for_duplicates("999999999", "jane|1985")
        assert duplicate_info is None


class TestReportGeneration:
    """Test report generation functionality."""

    def test_format_summary_report_successful(self, import_service):
        """Test formatting of successful import summary."""
        summary = ImportSummary()
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "Created"))
        summary.add_result(ImportRecordResult(2, ImportResult.SUCCESS, "Created"))
        summary.finalize()

        report = import_service.format_summary_report(summary)

        assert "ISRAEL MISSIONS 2025 IMPORT SUMMARY" in report
        assert "✅ Successful: 2" in report
        assert "Success rate: 100.0%" in report
        assert "✅ SUCCESS" in report

    def test_format_summary_report_with_errors(self, import_service):
        """Test formatting of summary with errors."""
        summary = ImportSummary()
        summary.add_result(ImportRecordResult(1, ImportResult.SUCCESS, "Created"))
        summary.add_result(ImportRecordResult(2, ImportResult.VALIDATION_ERROR, "Missing field"))
        summary.add_result(ImportRecordResult(3, ImportResult.DUPLICATE_SKIP, "Duplicate found"))
        summary.finalize()

        report = import_service.format_summary_report(summary)

        assert "❌ Validation errors: 1" in report
        assert "🔄 Duplicates skipped: 1" in report
        assert "Success rate: 33.3%" in report
        assert "⚠️ PARTIAL/FAILED" in report
        assert "ERROR DETAILS:" in report
        assert "Row 2: Missing field" in report
        assert "DUPLICATE DETAILS:" in report
        assert "Row 3: Duplicate found" in report

    def test_get_dry_run_preview(self, import_service):
        """Test dry-run payload preview generation."""
        summary = ImportSummary()

        # Add successful results with payloads
        payload1 = {"FullNameRU": "Test User", "ContactInformation": "+7123456789"}
        payload2 = {"FullNameRU": "Another User", "ContactInformation": "test@example.com"}

        summary.add_result(ImportRecordResult(
            1, ImportResult.SUCCESS, "OK", payload=payload1
        ))
        summary.add_result(ImportRecordResult(
            2, ImportResult.SUCCESS, "OK", payload=payload2
        ))
        summary.add_result(ImportRecordResult(
            3, ImportResult.VALIDATION_ERROR, "Error"  # No payload
        ))

        preview = import_service.get_dry_run_preview(summary, max_samples=2)

        assert "DRY-RUN PAYLOAD PREVIEW" in preview
        assert "Sample 1 (Row 1):" in preview
        assert "Sample 2 (Row 2):" in preview
        assert "Test User" in preview
        # Should show redacted contact info
        assert "+7*****89" in preview or "+7*******89" in preview  # Depending on redaction logic

    def test_format_payload_preview_redacts_contact(self, import_service):
        """Test payload preview redacts sensitive information."""
        payload = {
            "FullNameRU": "Test User",
            "ContactInformation": "+7-495-123-4567",
            "Other": "Normal field"
        }

        formatted = import_service._format_payload_preview(payload)

        # Should contain redacted contact info, not original
        assert "+7-495-123-4567" not in formatted
        assert "Test User" in formatted
        assert "Normal field" in formatted


class TestIntegrationScenarios:
    """Integration test scenarios for complete workflows."""

    @pytest.mark.asyncio
    async def test_complete_dry_run_workflow(self, import_service):
        """Test complete dry-run workflow from CSV to report."""
        # Create CSV with mixed valid and invalid data
        csv_data = [
            {
                "FullNameRU": "Валид Юзеров",
                "DateOfBirth": "1/1/1990",
                "Gender": "Male",
                "Size": "L",
                "ContactInformation": "+7-495-123-4567",
                "CountryAndCity": "Moscow",
                "Role": "TEAM"
            },
            {
                "FullNameRU": "",  # Invalid - empty required field
                "DateOfBirth": "invalid-date",
                "Gender": "Other",
                "Size": "XXXL",  # Invalid size
                "ContactInformation": "test@example.com",
                "CountryAndCity": "",
                "Role": "INVALID"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
            csv_path = Path(f.name)

        try:
            # Run dry-run import
            summary = await import_service.import_from_csv(csv_path, ImportMode.DRY_RUN)

            # Generate reports
            summary_report = import_service.format_summary_report(summary)
            preview_report = import_service.get_dry_run_preview(summary)

            # Verify summary
            assert summary.total_rows == 2
            assert summary.successful == 1
            assert summary.validation_errors == 1

            # Verify reports contain expected content
            assert "ISRAEL MISSIONS 2025 IMPORT SUMMARY" in summary_report
            assert "DRY-RUN PAYLOAD PREVIEW" in preview_report
            assert "Валид Юзеров" in preview_report

        finally:
            csv_path.unlink()

    @pytest.mark.asyncio
    async def test_complete_live_import_workflow(self, import_service):
        """Test complete live import workflow with mocked repository."""
        # Setup mock repository responses
        mock_participants = [
            Mock(spec=Participant, record_id="rec1"),
            Mock(spec=Participant, record_id="rec2")
        ]
        import_service.repository.create.side_effect = mock_participants

        # Create valid CSV
        csv_data = [
            {
                "FullNameRU": "User One",
                "ContactInformation": "+7-495-111-1111",
                "DateOfBirth": "1/1/1990",
                "Gender": "Male",
                "Size": "M",
                "CountryAndCity": "Moscow",
                "Role": "TEAM"
            },
            {
                "FullNameRU": "User Two",
                "ContactInformation": "+7-495-222-2222",
                "DateOfBirth": "2/2/1985",
                "Gender": "Female",
                "Size": "S",
                "CountryAndCity": "SPB",
                "Role": "CANDIDATE"
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=csv_data[0].keys())
            writer.writeheader()
            writer.writerows(csv_data)
            csv_path = Path(f.name)

        try:
            with patch('src.services.israel_missions_import_service.Participant') as mock_participant_class:
                mock_participant_class.from_airtable_fields.return_value = Mock(spec=Participant)

                # Run live import
                summary = await import_service.import_from_csv(csv_path, ImportMode.LIVE)

                # Verify results
                assert summary.total_rows == 2
                assert summary.successful == 2
                assert summary.is_successful()

                # Verify repository calls
                assert import_service.repository.create.call_count == 2

                # Verify duplicate cache was populated
                assert len(import_service._duplicate_cache) > 0

        finally:
            csv_path.unlink()