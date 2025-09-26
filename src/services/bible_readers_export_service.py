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
from src.data.repositories.bible_readers_repository import BibleReadersRepository
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.bible_readers import BibleReader
from src.utils.export_utils import format_line_number

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
    ):
        """
        Initialize the export service.

        Args:
            bible_readers_repository: BibleReaders repository for data access
            participant_repository: Participant repository for name hydration
            progress_callback: Optional callback for progress updates (current, total)
        """
        self.bible_readers_repository = bible_readers_repository
        self.participant_repository = participant_repository
        self.progress_callback = progress_callback

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

        # Generate filename
        prefix = filename_prefix or "bible_readers_export"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{prefix}_{timestamp}.csv"
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
