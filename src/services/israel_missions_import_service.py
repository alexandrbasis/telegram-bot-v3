"""
Israel Missions 2025 participant import service.

This service provides safe CSV-to-Airtable import functionality with:
- Dry-run validation before live operations
- Duplicate detection and prevention
- Comprehensive error handling and logging
- Per-record success/failure tracking
- Rate limiting and retry logic
"""

import asyncio
import csv
import logging
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union

from src.data.airtable.airtable_client import AirtableAPIError
from src.data.importers.israel_missions_mapping import IsraelMissionsMapping
from src.data.repositories.participant_repository import (
    DuplicateError,
    ParticipantRepository,
    RepositoryError,
)
from src.models.participant import Participant

logger = logging.getLogger(__name__)


class ImportMode(str, Enum):
    """Import operation modes."""

    DRY_RUN = "dry_run"
    LIVE = "live"


class ImportResult(str, Enum):
    """Import result types for individual records."""

    SUCCESS = "success"
    DUPLICATE_SKIP = "duplicate_skip"
    VALIDATION_ERROR = "validation_error"
    API_ERROR = "api_error"
    TRANSFORMATION_ERROR = "transformation_error"


class ImportRecordResult:
    """Result for a single record import attempt."""

    def __init__(
        self,
        row_number: int,
        result: ImportResult,
        message: str,
        payload: Optional[Dict[str, Any]] = None,
        error: Optional[Exception] = None,
        duplicate_keys: Optional[Tuple[str, str]] = None,
    ):
        self.row_number = row_number
        self.result = result
        self.message = message
        self.payload = payload  # For dry-run inspection
        self.error = error
        self.duplicate_keys = duplicate_keys
        self.timestamp = datetime.now().isoformat()


class ImportSummary:
    """Summary of import operation results."""

    def __init__(self):
        self.total_rows = 0
        self.successful = 0
        self.duplicates_skipped = 0
        self.validation_errors = 0
        self.api_errors = 0
        self.transformation_errors = 0
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.records: List[ImportRecordResult] = []

    def add_result(self, record_result: ImportRecordResult):
        """Add a record result to the summary."""
        self.records.append(record_result)
        self.total_rows += 1

        if record_result.result == ImportResult.SUCCESS:
            self.successful += 1
        elif record_result.result == ImportResult.DUPLICATE_SKIP:
            self.duplicates_skipped += 1
        elif record_result.result == ImportResult.VALIDATION_ERROR:
            self.validation_errors += 1
        elif record_result.result == ImportResult.API_ERROR:
            self.api_errors += 1
        elif record_result.result == ImportResult.TRANSFORMATION_ERROR:
            self.transformation_errors += 1

    def finalize(self):
        """Mark import as complete."""
        self.end_time = datetime.now()

    def get_duration_seconds(self) -> float:
        """Get import duration in seconds."""
        end_time = self.end_time or datetime.now()
        return (end_time - self.start_time).total_seconds()

    def is_successful(self) -> bool:
        """Check if import was entirely successful."""
        return (
            self.validation_errors + self.api_errors + self.transformation_errors
        ) == 0

    def get_success_rate(self) -> float:
        """Get success rate as percentage."""
        if self.total_rows == 0:
            return 0.0
        return (self.successful / self.total_rows) * 100.0


class IsraelMissionsImportService:
    """
    Service for importing Israel Missions 2025 participant data from CSV.

    Provides safe, validated import with dry-run capabilities and comprehensive
    error handling for production Airtable operations.
    """

    def __init__(
        self,
        participant_repository: ParticipantRepository,
        rate_limit_delay: float = 0.2,  # 5 requests/second default
    ):
        """
        Initialize import service.

        Args:
            participant_repository: Repository for participant operations
            rate_limit_delay: Delay between API calls in seconds
        """
        self.repository = participant_repository
        self.rate_limit_delay = rate_limit_delay
        self.mapping = IsraelMissionsMapping
        self._duplicate_cache: Dict[str, str] = {}  # normalized_key -> record_id
        logger.info("Initialized IsraelMissionsImportService")

    async def import_from_csv(
        self,
        csv_file_path: Union[str, Path],
        mode: ImportMode = ImportMode.DRY_RUN,
        max_records: Optional[int] = None,
    ) -> ImportSummary:
        """
        Import participants from CSV file.

        Args:
            csv_file_path: Path to CSV file
            mode: Import mode (dry_run or live)
            max_records: Maximum number of records to process (for testing)

        Returns:
            ImportSummary with detailed results

        Raises:
            FileNotFoundError: If CSV file doesn't exist
            PermissionError: If file can't be read
            RepositoryError: If database operations fail
        """
        csv_path = Path(csv_file_path)
        if not csv_path.exists():
            raise FileNotFoundError(f"CSV file not found: {csv_path}")

        summary = ImportSummary()

        logger.info(f"Starting {mode.value} import from {csv_path}")

        try:
            # Clear duplicate cache for fresh import
            self._duplicate_cache.clear()

            # Read and process CSV
            with open(csv_path, "r", encoding="utf-8") as csvfile:
                # Detect CSV format
                sample = csvfile.read(2048)
                csvfile.seek(0)
                sniffer = csv.Sniffer()
                delimiter = sniffer.sniff(sample).delimiter

                reader = csv.DictReader(csvfile, delimiter=delimiter)

                # Process each row
                for row_num, csv_row in enumerate(
                    reader, start=2
                ):  # Start at 2 (header is row 1)
                    if max_records and (row_num - 1) > max_records:
                        break

                    result = await self._process_csv_row(csv_row, row_num, mode)
                    summary.add_result(result)

                    # Rate limiting for live mode
                    if mode == ImportMode.LIVE and self.rate_limit_delay > 0:
                        await asyncio.sleep(self.rate_limit_delay)

        except Exception as e:
            logger.error(f"Failed to read CSV file {csv_path}: {e}")
            raise RepositoryError(f"CSV processing failed: {e}", e)

        finally:
            summary.finalize()

        logger.info(
            f"Import completed: {summary.successful}/{summary.total_rows} successful"
        )
        return summary

    async def _process_csv_row(
        self, csv_row: Dict[str, Any], row_number: int, mode: ImportMode
    ) -> ImportRecordResult:
        """Process a single CSV row."""
        try:
            # Step 1: Transform CSV to Airtable payload
            payload = self.mapping.create_airtable_payload(csv_row)

            # Step 2: Validate required fields
            is_valid, missing_fields = self.mapping.validate_required_fields(payload)
            if not is_valid:
                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.VALIDATION_ERROR,
                    message=f"Missing required fields: {missing_fields}",
                    payload=payload,
                )

            # Step 3: Check for duplicates
            contact_key, name_dob_key = self.mapping.get_duplicate_detection_keys(
                payload
            )
            duplicate_info = await self._check_for_duplicates(contact_key, name_dob_key)

            if duplicate_info:
                redacted_contact = self.mapping.redact_contact_for_logging(
                    payload.get("ContactInformation", "")
                )
                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.DUPLICATE_SKIP,
                    message=(
                        f"Duplicate detected: {duplicate_info} "
                        f"(contact: {redacted_contact})"
                    ),
                    payload=payload,
                    duplicate_keys=(contact_key, name_dob_key),
                )

            # Step 4: For dry-run, just validate and return success
            if mode == ImportMode.DRY_RUN:
                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.SUCCESS,
                    message="Validation passed - ready for import",
                    payload=payload,
                )

            # Step 5: Live mode - create participant
            try:
                # Create Participant object from payload
                participant = Participant.from_airtable_fields(payload)
                created_participant = await self.repository.create(participant)

                # Cache for duplicate detection
                if created_participant.record_id:
                    self._cache_duplicate_keys(
                        contact_key, name_dob_key, created_participant.record_id
                    )

                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.SUCCESS,
                    message=f"Created participant: {created_participant.record_id}",
                    payload=payload,
                )

            except DuplicateError as e:
                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.DUPLICATE_SKIP,
                    message=f"Duplicate detected during creation: {e}",
                    payload=payload,
                    error=e,
                )
            except (RepositoryError, AirtableAPIError) as e:
                return ImportRecordResult(
                    row_number=row_number,
                    result=ImportResult.API_ERROR,
                    message=f"API error: {e}",
                    payload=payload,
                    error=e,
                )

        except Exception as e:
            logger.error(f"Transformation error for row {row_number}: {e}")
            return ImportRecordResult(
                row_number=row_number,
                result=ImportResult.TRANSFORMATION_ERROR,
                message=f"Failed to transform CSV row: {e}",
                error=e,
            )

    async def _check_for_duplicates(
        self, contact_key: str, name_dob_key: str
    ) -> Optional[str]:
        """
        Check for duplicate participants using normalized keys.

        Args:
            contact_key: Normalized contact information
            name_dob_key: Normalized name+DOB combination

        Returns:
            Description of duplicate found, or None if no duplicate
        """
        # Check cache first
        if contact_key and contact_key in self._duplicate_cache:
            return f"contact key '{contact_key}' (cached)"

        if name_dob_key and name_dob_key in self._duplicate_cache:
            return f"name+DOB key '{name_dob_key}' (cached)"

        # TODO: Add actual database duplicate checking here
        # This would involve querying the repository for existing participants
        # with matching normalized contact info or name+DOB combinations

        return None

    def _cache_duplicate_keys(
        self, contact_key: str, name_dob_key: str, record_id: str
    ):
        """Cache duplicate detection keys for the session."""
        if contact_key:
            self._duplicate_cache[contact_key] = record_id
        if name_dob_key:
            self._duplicate_cache[name_dob_key] = record_id

    def format_summary_report(self, summary: ImportSummary) -> str:
        """
        Format a human-readable summary report.

        Args:
            summary: ImportSummary to format

        Returns:
            Formatted summary string
        """
        report_lines = [
            "=" * 60,
            "ISRAEL MISSIONS 2025 IMPORT SUMMARY",
            "=" * 60,
            f"Duration: {summary.get_duration_seconds():.1f} seconds",
            f"Total rows processed: {summary.total_rows}",
            "",
            "RESULTS:",
            f"  ✅ Successful: {summary.successful}",
            f"  🔄 Duplicates skipped: {summary.duplicates_skipped}",
            f"  ❌ Validation errors: {summary.validation_errors}",
            f"  🚫 API errors: {summary.api_errors}",
            f"  ⚠️ Transformation errors: {summary.transformation_errors}",
            "",
            f"Success rate: {summary.get_success_rate():.1f}%",
            (
                f"Overall status: "
                f"{'✅ SUCCESS' if summary.is_successful() else '⚠️ PARTIAL/FAILED'}"
            ),
        ]

        # Add error details if any
        if (
            summary.validation_errors
            + summary.api_errors
            + summary.transformation_errors
            > 0
        ):
            report_lines.extend(["", "ERROR DETAILS:", "-" * 40])

            for record in summary.records:
                if record.result in [
                    ImportResult.VALIDATION_ERROR,
                    ImportResult.API_ERROR,
                    ImportResult.TRANSFORMATION_ERROR,
                ]:
                    report_lines.append(f"Row {record.row_number}: {record.message}")

        # Add duplicate details if any
        if summary.duplicates_skipped > 0:
            report_lines.extend(["", "DUPLICATE DETAILS:", "-" * 40])

            for record in summary.records:
                if record.result == ImportResult.DUPLICATE_SKIP:
                    report_lines.append(f"Row {record.row_number}: {record.message}")

        report_lines.extend(["", "=" * 60])

        return "\n".join(report_lines)

    def get_dry_run_preview(self, summary: ImportSummary, max_samples: int = 5) -> str:
        """
        Get a preview of dry-run payloads for stakeholder review.

        Args:
            summary: Dry-run summary
            max_samples: Maximum number of payload samples to include

        Returns:
            Formatted preview string with JSON payloads
        """
        preview_lines = [
            "DRY-RUN PAYLOAD PREVIEW",
            "=" * 40,
            f"Showing first {max_samples} successful transformation samples:",
            "",
        ]

        sample_count = 0
        for record in summary.records:
            if record.result == ImportResult.SUCCESS and record.payload:
                sample_count += 1
                preview_lines.extend(
                    [
                        f"Sample {sample_count} (Row {record.row_number}):",
                        "-" * 20,
                        self._format_payload_preview(record.payload),
                        "",
                    ]
                )

                if sample_count >= max_samples:
                    break

        return "\n".join(preview_lines)

    def _format_payload_preview(self, payload: Dict[str, Any]) -> str:
        """Format payload for preview display."""
        import json

        # Remove sensitive data from preview
        safe_payload = payload.copy()

        # Redact contact information
        if "ContactInformation" in safe_payload:
            safe_payload["ContactInformation"] = (
                self.mapping.redact_contact_for_logging(
                    safe_payload["ContactInformation"]
                )
            )

        return json.dumps(safe_payload, indent=2, ensure_ascii=False)
