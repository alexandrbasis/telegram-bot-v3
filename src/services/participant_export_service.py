"""
Service for exporting participant data to CSV format.

Handles CSV generation from participant repository data with proper
field mapping, UTF-8 encoding, and file management.
"""

import csv
import io
import logging
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.config.field_mappings import AirtableFieldMapping
from src.data.airtable.airtable_client import AirtableAPIError
from src.data.repositories.participant_repository import (
    ParticipantRepository,
    RepositoryError,
)
from src.models.participant import Department, Participant, Role
from src.config.settings import Settings
from src.utils.export_utils import (
    extract_headers_from_view_records,
    format_line_number,
    order_rows_by_view_headers,
)

logger = logging.getLogger(__name__)


class ParticipantExportService:
    """
    Service for exporting participant data to CSV format.

    Provides functionality to:
    - Export all participants to CSV with Airtable field mapping
    - Handle large datasets efficiently
    - Manage file generation and cleanup
    - Estimate file sizes for Telegram upload limits
    - Track export progress for UI updates
    """

    # Telegram file upload limit (50MB)
    TELEGRAM_FILE_LIMIT = 50 * 1024 * 1024  # 50MB in bytes

    # Average bytes per participant record (estimated)
    BYTES_PER_RECORD_ESTIMATE = 500  # Conservative estimate

    # View names are now configured via settings
    # These constants are kept for backward compatibility but deprecated
    TEAM_VIEW_NAME = "Тимы"
    CANDIDATE_VIEW_NAME = "Кандидаты"

    # Fallback view field ordering to ensure consistent headers even when
    # Airtable returns sparse data (fields with no values are omitted).
    # This is now deprecated as we use view-based ordering from Airtable
    VIEW_HEADER_ORDER: Dict[str, List[str]] = {
        "Тимы": [
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
        ],
        "Кандидаты": [
            "FullNameRU",
            "Gender",
            "DateOfBirth",
            "Size",
            "CountryAndCity",
            "Church",
            "SubmittedBy",
            "FullNameEN",
            "ContactInformation",
        ],
    }

    def __init__(
        self,
        repository: ParticipantRepository,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the export service.

        Args:
            repository: Participant repository for data access
            progress_callback: Optional callback for progress updates (current, total)
            settings: Optional settings object for view configuration
        """
        self.repository = repository
        self.progress_callback = progress_callback
        self._settings = settings

    @property
    def settings(self) -> Settings:
        """Get settings, lazily initializing if needed."""
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    async def get_all_participants_as_csv(self) -> str:
        """
        Export all participants to CSV format string.

        Retrieves all participants from the repository and formats them
        as CSV with Airtable field names as headers.

        Returns:
            CSV formatted string with all participant data

        Raises:
            Exception: If repository access fails
        """
        logger.info("Starting participant CSV export")

        # Retrieve all participants
        participants = await self.repository.list_all()
        total_count = len(participants)
        logger.info(f"Retrieved {total_count} participants for export")

        # Report initial progress
        if self.progress_callback:
            self.progress_callback(0, total_count)

        # Create CSV in memory
        output = io.StringIO()

        # Define CSV headers using Airtable field names
        headers = self._get_csv_headers()

        # Create CSV writer
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")

        # Write headers
        writer.writeheader()

        # Calculate width for line numbers based on total participant count
        width = len(str(total_count)) if total_count > 0 else 1

        # Process participants
        for index, participant in enumerate(participants):
            # Convert participant to CSV row
            row = self._participant_to_csv_row(participant)
            # Add line number as first column with consistent width
            row["#"] = format_line_number(index + 1, width)
            writer.writerow(row)

            # Report progress at intervals (every 10 records or at end)
            if self.progress_callback:
                if (index + 1) % 10 == 0 or (index + 1) == total_count:
                    self.progress_callback(index + 1, total_count)

        # Get CSV string
        csv_string = output.getvalue()
        output.close()

        logger.info(f"CSV export completed with {total_count} records")
        return csv_string

    def export_to_csv(self) -> str:
        """
        Export all participants to CSV using a synchronous interface.

        The method delegates to the async exporter when no event loop is
        running. When called from an async context it raises a descriptive
        error so callers can switch to the coroutine API instead of
        triggering ``RuntimeError`` via ``run_until_complete``.

        Returns:
            CSV formatted string with all participant data

        Raises:
            RuntimeError: If invoked while an event loop is already running
        """
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # Safe to run synchronously when no loop is active
            return asyncio.run(self.get_all_participants_as_csv())

        raise RuntimeError(
            "ParticipantExportService.export_to_csv() cannot be called while an event "
            "loop is running; use await "
            "get_all_participants_as_csv() in async contexts."
        )

    async def export_to_csv_async(self) -> str:
        """Async wrapper matching the synchronous export method name."""
        return await self.get_all_participants_as_csv()

    async def save_to_file(
        self, directory: Optional[str] = None, filename_prefix: Optional[str] = None
    ) -> str:
        """
        Export participants to a CSV file.

        Args:
            directory: Optional directory path (uses temp dir if not specified)
            filename_prefix: Optional prefix for filename
                (default: "participants_export")

        Returns:
            Path to the created CSV file

        Raises:
            Exception: If file creation or export fails
        """
        # Generate CSV content
        csv_content = await self.get_all_participants_as_csv()

        # Determine directory
        if directory:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            dir_path = Path(tempfile.gettempdir())

        # Generate filename
        prefix = filename_prefix or "participants_export"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
        file_path = dir_path / filename

        try:
            # Write to file with UTF-8 BOM so apps like Excel detect Cyrillic
            # correctly when opening CSV files.
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(csv_content)

            logger.info(f"CSV file saved to: {file_path}")
            return str(file_path)

        except Exception as e:
            # Clean up file if it was partially created
            if file_path.exists():
                try:
                    file_path.unlink()
                except Exception:
                    # Best-effort cleanup only
                    pass
            raise e

    async def estimate_file_size(self) -> int:
        """
        Estimate the size of the CSV file before generation.

        Uses record count and average record size to estimate.

        Returns:
            Estimated file size in bytes
        """
        # Get total record count
        total_count = await self.repository.count_total()

        # Calculate header size (approximate)
        headers = self._get_csv_headers()
        header_size = len(",".join(headers)) + 2  # +2 for newline

        # Estimate total size
        estimated_size = header_size + (total_count * self.BYTES_PER_RECORD_ESTIMATE)

        logger.info(
            "Estimated CSV size: %s bytes for %s records",
            estimated_size,
            total_count,
        )
        return estimated_size

    async def is_within_telegram_limit(self) -> bool:
        """
        Check if the estimated file size is within Telegram's upload limit.

        Returns:
            True if file is within limit, False otherwise
        """
        estimated_size = await self.estimate_file_size()
        within_limit = estimated_size < self.TELEGRAM_FILE_LIMIT

        if not within_limit:
            logger.warning(
                f"Estimated file size ({estimated_size} bytes) exceeds "
                f"Telegram limit ({self.TELEGRAM_FILE_LIMIT} bytes)"
            )

        return within_limit

    async def get_participants_by_role_as_csv(self, role: Role) -> str:
        """
        Export participants filtered by role to CSV format.

        Retrieves all participants from the repository, filters by the specified role,
        and formats them as CSV with Airtable field names as headers.

        Args:
            role: The role to filter by (TEAM or CANDIDATE)

        Returns:
            CSV formatted string with filtered participant data

        Raises:
            Exception: If repository access fails
        """
        logger.info(f"Starting participant CSV export filtered by role: {role.value}")

        if role == Role.TEAM:
            # Use configured view name from settings for team exports
            view_name = "Тимы"  # Hardcoded for now as team view not yet configurable
            csv_string = await self._export_view_to_csv(
                view_name,
                filter_func=lambda record, participant: participant.role == Role.TEAM,
            )
            logger.info(
                "Team export completed using Airtable view '%s'", view_name
            )
            return csv_string

        if role == Role.CANDIDATE:
            # Use configured view name from settings for candidate exports
            # Fallback to constant for backward compatibility in tests
            try:
                view_name = self.settings.database.participant_export_view
            except (ValueError, AttributeError):
                # If settings can't be initialized (e.g., in tests), use the constant
                view_name = self.CANDIDATE_VIEW_NAME
            csv_string = await self._export_view_to_csv(
                view_name,
                filter_func=lambda record, participant: participant.role
                == Role.CANDIDATE,
            )
            logger.info(
                "Candidate export completed using Airtable view '%s'",
                view_name,
            )
            return csv_string

        # Fallback to legacy filtering for any other roles
        all_participants = await self.repository.list_all()
        filtered_participants = [
            p for p in all_participants if p.role is not None and p.role == role
        ]

        total_count = len(filtered_participants)
        logger.info(f"Filtered {total_count} participants with role {role.value}")

        if self.progress_callback:
            self.progress_callback(0, total_count)

        output = io.StringIO()
        headers = self._get_csv_headers()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()

        # Calculate width for line numbers based on total filtered count
        width = len(str(total_count)) if total_count > 0 else 1

        for index, participant in enumerate(filtered_participants):
            row = self._participant_to_csv_row(participant)
            # Add line number as first column with consistent width
            row["#"] = format_line_number(index + 1, width)
            writer.writerow(row)

            if self.progress_callback:
                if (index + 1) % 10 == 0 or (index + 1) == total_count:
                    self.progress_callback(index + 1, total_count)

        csv_string = output.getvalue()
        output.close()

        logger.info(f"Role-filtered CSV export completed with {total_count} records")
        return csv_string

    async def get_participants_by_department_as_csv(
        self, department: Department
    ) -> str:
        """
        Export participants filtered by department to CSV format.

        Retrieves all participants from the repository, filters by the specified
        department, and formats them as CSV with Airtable field names as headers.

        Args:
            department: The department to filter by

        Returns:
            CSV formatted string with filtered participant data

        Raises:
            Exception: If repository access fails
        """
        logger.info(
            "Starting participant CSV export filtered by department: %s",
            department.value,
        )

        def department_filter(record: Dict[str, Any], participant: Participant) -> bool:
            return (
                participant.department is not None
                and participant.department == department
            )

        # Use team view for department filtering (hardcoded for now)
        view_name = "Тимы"  # Hardcoded as team view not yet configurable
        csv_string = await self._export_view_to_csv(
            view_name, filter_func=department_filter
        )

        logger.info(
            "Department-filtered CSV export completed for %s using view '%s'",
            department.value,
            view_name,
        )
        return csv_string

    async def _export_view_to_csv(
        self,
        view_name: str,
        filter_func: Optional[Callable[[Dict[str, Any], Participant], bool]] = None,
    ) -> str:
        """Export Airtable view records to CSV, optionally filtering results."""
        try:
            raw_records = await self.repository.list_view_records(view_name)
            logger.info(
                "Retrieved %s records from Airtable view '%s'",
                len(raw_records),
                view_name,
            )
        except RepositoryError as error:
            # Check if this is a 422 VIEW_NAME_NOT_FOUND error
            if self._is_view_not_found_error(error):
                logger.info(
                    "View '%s' not found, falling back to list_all() with filtering",
                    view_name,
                )
                return await self._fallback_candidates_from_all_participants(
                    filter_func
                )
            else:
                # Re-raise other repository errors
                raise

        headers = self._determine_view_headers(view_name, raw_records)

        rows: List[Tuple[Dict[str, Any], Participant]] = []
        for record in raw_records:
            try:
                participant = Participant.from_airtable_record(record)
            except Exception as exc:  # pragma: no cover - defensive logging
                logger.warning(
                    "Skipping invalid participant record %s from view '%s': %s",
                    record.get("id", "unknown"),
                    view_name,
                    exc,
                )
                continue

            if filter_func and not filter_func(record, participant):
                continue

            rows.append((record, participant))

        if filter_func:
            logger.info(
                "Filtered view '%s' records down to %s rows for export",
                view_name,
                len(rows),
            )

        return self._records_to_csv(rows, headers)

    def _determine_view_headers(
        self, view_name: str, records: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Determine CSV headers matching the Airtable view ordering with line
        numbers as first column.
        """
        # Use the new utility to extract headers from view records
        headers = extract_headers_from_view_records(records)

        # If no headers found, fall back to default field mapping
        if not headers:
            headers = []
            for (
                python_field,
                airtable_field,
            ) in AirtableFieldMapping.PYTHON_TO_AIRTABLE.items():
                if python_field != "record_id":
                    headers.append(airtable_field)

        # Add line number column as first header
        return ["#"] + headers

    def _records_to_csv(
        self,
        rows: List[Tuple[Dict[str, Any], Participant]],
        headers: List[str],
    ) -> str:
        """Convert prepared participant rows to CSV string using ordered headers."""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()

        total_count = len(rows)
        if self.progress_callback and total_count >= 0:
            # Notify initial progress; guard division in callback implementation
            self.progress_callback(0, total_count)

        # Calculate width for line numbers based on total row count
        width = len(str(total_count)) if total_count > 0 else 1

        # Prepare all rows with data
        prepared_rows = []
        for index, (record, participant) in enumerate(rows):
            row_data = self._participant_to_csv_row(participant)
            airtable_fields = record.get("fields", {})

            # Merge mapped data with raw Airtable fields for completeness
            merged_row = {}
            for field_name, field_value in airtable_fields.items():
                merged_row[field_name] = self._format_raw_value(field_value)

            # Override with mapped values where available
            merged_row.update(row_data)

            # Add line number with consistent width
            merged_row["#"] = format_line_number(index + 1, width)
            prepared_rows.append(merged_row)

        # Extract view headers (without #) for reordering
        view_headers = [h for h in headers if h != "#"]

        # Use utility to reorder rows based on view headers
        if view_headers:
            reordered_rows = order_rows_by_view_headers(
                view_headers,
                list(prepared_rows[0].keys()) if prepared_rows else [],
                prepared_rows
            )
        else:
            reordered_rows = prepared_rows

        # Write reordered rows to CSV
        for index, row in enumerate(reordered_rows):
            writer.writerow(row)

            if (
                self.progress_callback
                and total_count > 0
                and ((index + 1) % 10 == 0 or (index + 1) == total_count)
            ):
                self.progress_callback(index + 1, total_count)

        csv_string = output.getvalue()
        output.close()
        return csv_string

    @staticmethod
    def _format_raw_value(value: Any) -> str:
        """Format raw Airtable values for CSV output when mapping is unavailable."""
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            return value.isoformat()[:10]
        if isinstance(value, list):
            return ", ".join(str(item) for item in value)
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        return str(value)

    def _get_csv_headers(self) -> List[str]:
        """
        Get CSV headers based on Airtable field names with line numbers as first column.

        Returns:
            List of headers with "#" as first column, followed by Airtable field names
        """
        # Get all Airtable field names from mapping (excluding 'id')
        headers = []
        for (
            python_field,
            airtable_field,
        ) in AirtableFieldMapping.PYTHON_TO_AIRTABLE.items():
            if python_field != "record_id":  # Skip record_id as it's internal
                headers.append(airtable_field)

        # Add line number column as first header
        return ["#"] + headers

    def _participant_to_csv_row(self, participant: Participant) -> Dict[str, str]:
        """
        Convert a Participant object to a CSV row dictionary.

        Args:
            participant: Participant instance to convert

        Returns:
            Dictionary with Airtable field names as keys and formatted values
        """
        row = {}

        # Map each field
        for (
            python_field,
            airtable_field,
        ) in AirtableFieldMapping.PYTHON_TO_AIRTABLE.items():
            if python_field == "record_id":
                continue  # Skip internal record_id

            # Get value from participant
            value = getattr(participant, python_field, None)

            # Format value for CSV
            if value is None:
                row[airtable_field] = ""
            elif isinstance(value, (date, datetime)):
                if airtable_field == "DateOfBirth":
                    row[airtable_field] = Participant._format_date_of_birth(value)
                else:
                    row[airtable_field] = value.isoformat()[:10]  # YYYY-MM-DD format
            elif hasattr(value, "value"):  # Enum
                row[airtable_field] = str(value.value)
            else:
                row[airtable_field] = str(value)

        return row

    def _is_view_not_found_error(self, error: RepositoryError) -> bool:
        """
        Check if the RepositoryError represents a 422 VIEW_NAME_NOT_FOUND error.

        Args:
            error: The RepositoryError to check

        Returns:
            True if this is a view not found error, False otherwise
        """
        if not hasattr(error, "original_error") or error.original_error is None:
            return False

        original_error = error.original_error

        # Check if it's an AirtableAPIError with status code 422
        if not isinstance(original_error, AirtableAPIError):
            return False

        if getattr(original_error, "status_code", None) != 422:
            return False

        # Check if the error message contains VIEW_NAME_NOT_FOUND indicator
        error_message = str(original_error)
        return "not found" in error_message.lower()

    async def _fallback_candidates_from_all_participants(
        self,
        filter_func: Optional[Callable[[Dict[str, Any], Participant], bool]] = None,
    ) -> str:
        """
        Fallback method to export participants using list_all() with filtering.

        Args:
            filter_func: Optional filter function to apply to participants

        Returns:
            CSV formatted string with filtered participant data
        """
        logger.info("Using fallback export via list_all() with provided filtering")

        # Get all participants
        all_participants = await self.repository.list_all()

        # Apply provided filter function if available, otherwise use all participants
        if filter_func:
            filtered_participants = []
            for participant in all_participants:
                # Pass empty dict as record since filter functions only use participant
                record: Dict[str, Any] = {}
                if filter_func(record, participant):
                    filtered_participants.append(participant)
        else:
            # If no filter provided, fall back to candidate filtering for compatibility
            filtered_participants = [
                p
                for p in all_participants
                if p.role is not None and p.role == Role.CANDIDATE
            ]

        total_count = len(filtered_participants)
        logger.info(f"Found {total_count} participants via fallback method")

        # Report initial progress
        if self.progress_callback:
            self.progress_callback(0, total_count)

        # Create CSV in memory
        output = io.StringIO()
        headers = self._get_csv_headers()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()

        # Calculate width for line numbers based on total count
        width = len(str(total_count)) if total_count > 0 else 1

        # Process filtered participants
        for index, participant in enumerate(filtered_participants):
            row = self._participant_to_csv_row(participant)
            # Add line number as first column with consistent width
            row["#"] = format_line_number(index + 1, width)
            writer.writerow(row)

            # Report progress at intervals
            if self.progress_callback:
                if (index + 1) % 10 == 0 or (index + 1) == total_count:
                    self.progress_callback(index + 1, total_count)

        csv_string = output.getvalue()
        output.close()

        logger.info(f"Fallback export completed with {total_count} records")
        return csv_string
