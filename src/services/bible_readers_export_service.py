"""
Service for exporting BibleReaders data to CSV format.

Handles CSV generation from BibleReaders repository data with participant
hydration, proper field mapping, UTF-8 encoding, and file management.
"""

import csv
import io
import logging
import tempfile
from datetime import date, datetime
from pathlib import Path
from typing import Callable, Dict, List, Optional

from src.config.field_mappings.bible_readers import BibleReadersFieldMapping
from src.config.settings import Settings
from src.data.repositories.bible_readers_repository import BibleReadersRepository
from src.data.repositories.participant_repository import (
    ParticipantRepository,
    RepositoryError,
)
from src.models.bible_readers import BibleReader
from src.utils.export_utils import (
    extract_headers_from_view_records,
    format_line_number,
    generate_readable_export_filename,
    order_rows_by_view_headers,
)

logger = logging.getLogger(__name__)


class BibleReadersExportService:
    """
    Service for exporting BibleReaders data to CSV format.

    Provides functionality to:
    - Export all Bible readers to CSV with Airtable field mapping
    - Hydrate participant names from linked participant IDs
    - Handle large datasets efficiently
    - Manage file generation and cleanup
    - Estimate file sizes for Telegram upload limits
    - Track export progress for UI updates
    """

    # Telegram file upload limit (50MB)
    TELEGRAM_FILE_LIMIT = 50 * 1024 * 1024  # 50MB in bytes

    # Average bytes per record estimate (conservative)
    BYTES_PER_RECORD_ESTIMATE = (
        300  # Bible readers typically have less data than participants
    )

    def __init__(
        self,
        bible_readers_repository: BibleReadersRepository,
        participant_repository: ParticipantRepository,
        progress_callback: Optional[Callable[[int, int], None]] = None,
        settings: Optional[Settings] = None,
    ):
        """
        Initialize the export service.

        Args:
            bible_readers_repository: BibleReaders repository for data access
            participant_repository: Participant repository for name hydration
            progress_callback: Optional callback for progress updates (current, total)
            settings: Optional settings object for view configuration
        """
        self.bible_readers_repository = bible_readers_repository
        self.participant_repository = participant_repository
        self.progress_callback = progress_callback
        self._settings = settings

    @property
    def settings(self) -> Settings:
        """Get settings, lazily initializing if needed."""
        if self._settings is None:
            self._settings = Settings()
        return self._settings

    async def get_all_bible_readers_as_csv(self) -> str:
        """
        Export all Bible readers to CSV format string.

        Retrieves all Bible readers from the repository, hydrates participant names,
        and formats them as CSV with Airtable field names as headers.

        Returns:
            CSV formatted string with all Bible readers data

        Raises:
            Exception: If repository access fails
        """
        logger.info("Starting BibleReaders CSV export")

        # Try to use view-based export first
        try:
            view_name = self.settings.database.bible_readers_export_view
            logger.info(f"Using configured BibleReaders export view: {view_name}")
            return await self._export_view_to_csv(view_name)
        except (ValueError, AttributeError):
            # If settings can't be initialized, fall back to legacy method
            logger.info("Settings not available, using legacy export method")
            return await self._legacy_export()
        except RepositoryError as e:
            logger.warning(f"View export failed: {e}, falling back to legacy method")
            return await self._legacy_export()

    async def _legacy_export(self) -> str:
        """
        Legacy export method using list_all().
        """
        # Retrieve all Bible readers
        bible_readers = await self.bible_readers_repository.list_all()
        total_count = len(bible_readers)
        logger.info(f"Retrieved {total_count} Bible readers for export")

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

        # Calculate width for line numbers based on total count
        width = len(str(total_count)) if total_count > 0 else 1

        # Process Bible readers
        for index, bible_reader in enumerate(bible_readers):
            # Convert Bible reader to CSV row with participant hydration
            row = await self._bible_reader_to_csv_row(bible_reader)
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

        logger.info(f"BibleReaders CSV export completed with {total_count} records")
        return csv_string

    async def _export_view_to_csv(self, view_name: str) -> str:
        """
        Export Bible Readers records from Airtable view to CSV with view-based ordering.
        """
        # Get records from view
        raw_records = await self.bible_readers_repository.list_view_records(view_name)
        logger.info(
            f"Retrieved {len(raw_records)} records from BibleReaders view '{view_name}'"
        )

        # Extract headers from view
        view_headers = extract_headers_from_view_records(raw_records)
        if not view_headers:
            # Fall back to default headers
            view_headers = [h for h in self._get_csv_headers() if h != "#"]
        headers = ["#"] + view_headers

        # Report initial progress
        total_count = len(raw_records)
        if self.progress_callback:
            self.progress_callback(0, total_count)

        # Calculate width for line numbers
        width = len(str(total_count)) if total_count > 0 else 1

        # Prepare rows with view data and hydrated names
        prepared_rows = []
        for index, record in enumerate(raw_records):
            try:
                bible_reader = BibleReader.from_airtable_record(record)
            except Exception as exc:
                logger.warning(
                    f"Skipping invalid BibleReader record "
                    f"{record.get('id', 'unknown')} from view '{view_name}': {exc}"
                )
                continue

            # Get view field data
            view_data = record.get("fields", {})

            # Create row with view data and hydrated participant names
            row = {}
            for field_name, field_value in view_data.items():
                row[field_name] = self._format_raw_value(field_value)

            # Hydrate participant names for Participants field
            participant_names = await self._hydrate_participant_names(
                bible_reader.participants
            )

            # Override with hydrated names
            if participant_names:
                row["Participants"] = "; ".join(participant_names)

            # Add line number
            row["#"] = format_line_number(index + 1, width)
            prepared_rows.append(row)

            # Report progress
            if self.progress_callback:
                if (index + 1) % 10 == 0 or (index + 1) == len(raw_records):
                    self.progress_callback(index + 1, len(raw_records))

        # Reorder rows based on view headers
        if view_headers:
            reordered_rows = order_rows_by_view_headers(
                view_headers,
                list(prepared_rows[0].keys()) if prepared_rows else [],
                prepared_rows,
            )
        else:
            reordered_rows = prepared_rows

        # Write to CSV
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=headers, extrasaction="ignore")
        writer.writeheader()

        for row in reordered_rows:
            writer.writerow(row)

        csv_string = output.getvalue()
        output.close()

        logger.info(
            f"BibleReaders view export completed with {len(reordered_rows)} records"
        )
        return csv_string

    @staticmethod
    def _format_raw_value(value) -> str:
        """Format raw Airtable values for CSV output."""
        if value is None:
            return ""
        if isinstance(value, (date, datetime)):
            return value.isoformat()[:10]
        if isinstance(value, list):
            return "; ".join(str(item) for item in value)
        if isinstance(value, bool):
            return "TRUE" if value else "FALSE"
        return str(value)

    async def export_to_csv_async(self) -> str:
        """Async wrapper matching the export interface pattern."""
        return await self.get_all_bible_readers_as_csv()

    def export_to_csv(self) -> str:
        """
        Export all Bible readers to CSV using a synchronous interface.

        The method delegates to the async exporter when no event loop is
        running. When called from an async context it raises a descriptive
        error so callers can switch to the coroutine API instead of
        triggering ``RuntimeError`` via ``run_until_complete``.

        Returns:
            CSV formatted string with all Bible readers data

        Raises:
            RuntimeError: If invoked while an event loop is already running
        """
        import asyncio

        try:
            asyncio.get_running_loop()
        except RuntimeError:
            # Safe to run synchronously when no loop is active
            return asyncio.run(self.get_all_bible_readers_as_csv())

        raise RuntimeError(
            "BibleReadersExportService.export_to_csv() cannot be called while an event "
            "loop is running; use await "
            "export_to_csv_async() in async contexts."
        )

    async def save_to_file(
        self, directory: Optional[str] = None, filename_prefix: Optional[str] = None
    ) -> str:
        """
        Export Bible readers to a CSV file.

        Args:
            directory: Optional directory path (uses temp dir if not specified)
            filename_prefix: Optional prefix for filename
                (default: "bible_readers_export")

        Returns:
            Path to the created CSV file

        Raises:
            Exception: If file creation or export fails
        """
        # Generate CSV content
        csv_content = await self.get_all_bible_readers_as_csv()

        # Determine directory
        if directory:
            dir_path = Path(directory)
            dir_path.mkdir(parents=True, exist_ok=True)
        else:
            dir_path = Path(tempfile.gettempdir())

        # Generate human-readable filename
        filename = generate_readable_export_filename("bible_readers")
        file_path = dir_path / filename

        try:
            # Write to file with UTF-8 BOM so apps like Excel detect Cyrillic correctly
            with open(file_path, "w", encoding="utf-8-sig", newline="") as f:
                f.write(csv_content)

            logger.info(f"BibleReaders CSV file saved to: {file_path}")
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

        Uses record count from list_all and average record size to estimate.

        Returns:
            Estimated file size in bytes
        """
        # Get total record count by listing all records
        bible_readers = await self.bible_readers_repository.list_all()
        total_count = len(bible_readers)

        # Calculate header size (approximate)
        headers = self._get_csv_headers()
        header_size = len(",".join(headers)) + 2  # +2 for newline

        # Estimate total size
        estimated_size = header_size + (total_count * self.BYTES_PER_RECORD_ESTIMATE)

        logger.info(
            "Estimated BibleReaders CSV size: %s bytes for %s records",
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
                f"Estimated BibleReaders file size ({estimated_size} bytes) exceeds "
                f"Telegram limit ({self.TELEGRAM_FILE_LIMIT} bytes)"
            )

        return within_limit

    async def _hydrate_participant_names(self, participant_ids: List[str]) -> List[str]:
        """
        Hydrate participant IDs to full names.

        Args:
            participant_ids: List of participant record IDs

        Returns:
            List of participant full names (Russian)
        """
        if not participant_ids:
            return []

        names = []
        for participant_id in participant_ids:
            participant = await self.participant_repository.get_by_id(participant_id)
            if participant and participant.full_name_ru:
                names.append(participant.full_name_ru)

        return names

    def _get_csv_headers(self) -> List[str]:
        """
        Get CSV headers based on BibleReaders Airtable field names.

        Returns:
            List of Airtable field names for CSV headers plus hydrated fields
        """
        return ["#", "Where", "Participants", "When", "Bible"]

    async def _bible_reader_to_csv_row(
        self, bible_reader: BibleReader
    ) -> Dict[str, str]:
        """
        Convert a BibleReader object to a CSV row dictionary with participant hydration.

        Args:
            bible_reader: BibleReader instance to convert

        Returns:
            Dictionary with Airtable field names as keys and formatted values
        """
        row = {}

        # Map each field from BibleReader model
        for (
            python_field,
            airtable_field,
        ) in BibleReadersFieldMapping.PYTHON_TO_AIRTABLE.items():
            if python_field == "record_id":
                continue  # Skip internal record_id

            # Get value from Bible reader
            value = getattr(bible_reader, python_field, None)

            # Format value for CSV
            if value is None:
                row[airtable_field] = ""
            elif isinstance(value, date):
                row[airtable_field] = value.isoformat()  # YYYY-MM-DD format
            elif isinstance(value, list):
                # Handle list fields (participants, churches, room_numbers)
                if python_field == "participants":
                    # Skip participants IDs, we'll hydrate names separately
                    row[airtable_field] = "; ".join(value) if value else ""
                else:
                    # Format other list fields (churches, room_numbers)
                    row[airtable_field] = (
                        "; ".join(str(item) for item in value) if value else ""
                    )
            else:
                row[airtable_field] = str(value)

        # Hydrate participant names for Participants column
        participant_names = await self._hydrate_participant_names(
            bible_reader.participants
        )
        row["Participants"] = "; ".join(participant_names) if participant_names else ""

        return row
