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
from typing import Callable, Dict, List, Optional

from src.config.field_mappings import AirtableFieldMapping
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.participant import Participant

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

    def __init__(
        self,
        repository: ParticipantRepository,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ):
        """
        Initialize the export service.

        Args:
            repository: Participant repository for data access
            progress_callback: Optional callback for progress updates (current, total)
        """
        self.repository = repository
        self.progress_callback = progress_callback

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

        # Process participants
        for index, participant in enumerate(participants):
            # Convert participant to CSV row
            row = self._participant_to_csv_row(participant)
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
        Export all participants to CSV format string (synchronous wrapper).

        This method provides a synchronous interface for the asynchronous
        get_all_participants_as_csv method, compatible with the existing
        export handler interface.

        Returns:
            CSV formatted string with all participant data

        Raises:
            Exception: If repository access fails
        """
        import asyncio

        # Check if we're already in an event loop
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            # No event loop running, create new one
            return asyncio.run(self.get_all_participants_as_csv())
        else:
            # Event loop is running, use it
            return loop.run_until_complete(self.get_all_participants_as_csv())

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

    def _get_csv_headers(self) -> List[str]:
        """
        Get CSV headers based on Airtable field names.

        Returns:
            List of Airtable field names for CSV headers
        """
        # Get all Airtable field names from mapping (excluding 'id')
        headers = []
        for (
            python_field,
            airtable_field,
        ) in AirtableFieldMapping.PYTHON_TO_AIRTABLE.items():
            if python_field != "record_id":  # Skip record_id as it's internal
                headers.append(airtable_field)

        return headers

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
                row[airtable_field] = value.isoformat()[:10]  # YYYY-MM-DD format
            elif hasattr(value, "value"):  # Enum
                row[airtable_field] = str(value.value)
            else:
                row[airtable_field] = str(value)

        return row
