"""
Export utility functions for line number generation and CSV manipulation.

Provides utilities for adding line numbers to CSV exports to improve
usability for event organizers who need quick participant counting
and reference capabilities.
"""

import csv
import io
from typing import Any, Dict, List, Optional, Tuple


def format_line_number(line_num: int, width: Optional[int] = None) -> str:
    """
    Format a line number for display in CSV exports with right-alignment.

    Args:
        line_num: The line number to format (must be >= 0)
        width: Optional width for right-alignment. If provided, number is
               right-aligned and padded with spaces to this width.

    Returns:
        Formatted line number as string, right-aligned if width specified

    Raises:
        ValueError: If line_num is negative or width is <= 0
        TypeError: If line_num is not an integer
    """
    if not isinstance(line_num, int):
        raise TypeError(
            f"Line number must be an integer, got {type(line_num).__name__}"
        )

    if line_num < 0:
        raise ValueError(f"Line number must be non-negative, got {line_num}")

    if width is not None:
        if not isinstance(width, int):
            raise TypeError(f"Width must be an integer, got {type(width).__name__}")
        if width <= 0:
            raise ValueError(f"Width must be positive, got {width}")

        return f"{line_num:>{width}}"

    return str(line_num)


def add_line_numbers_to_csv(csv_string: str) -> str:
    """
    Add line numbers as the first column to a CSV string with consistent width.

    Parses the CSV, adds a '#' header column, and prepends sequential
    line numbers (starting from 1) to each data row. Line numbers are
    right-aligned with consistent width based on the total row count.

    Args:
        csv_string: CSV formatted string with headers and data rows

    Returns:
        CSV string with line numbers added as first column

    Raises:
        Exception: If CSV parsing fails
    """
    if not csv_string or not csv_string.strip():
        return csv_string

    # Parse CSV input
    input_stream = io.StringIO(csv_string)
    reader = csv.reader(input_stream)

    # Read all rows
    rows = list(reader)
    input_stream.close()

    if not rows:
        return csv_string

    # Calculate width for line numbers based on total data rows
    data_row_count = len(rows) - 1  # Exclude header row
    if data_row_count <= 0:
        width = 1
    else:
        width = len(str(data_row_count))

    # Create output stream
    output_stream = io.StringIO()

    # Process headers (first row)
    headers = rows[0]
    new_headers = ["#"] + headers

    writer = csv.writer(output_stream, lineterminator="\n")
    writer.writerow(new_headers)

    # Process data rows (add line numbers with consistent width)
    for line_num, row in enumerate(rows[1:], start=1):
        new_row = [format_line_number(line_num, width)] + row
        writer.writerow(new_row)

    result = output_stream.getvalue()
    output_stream.close()

    return result


def add_line_numbers_to_rows(
    headers: List[str], rows: List[Dict[str, Any]]
) -> Tuple[List[str], List[Dict[str, Any]]]:
    """
    Add line numbers to row data structures with consistent width formatting.

    Args:
        headers: List of column header names
        rows: List of row dictionaries with column data

    Returns:
        Tuple of (new_headers, new_rows) with line numbers added
    """
    # Add line number header
    new_headers = ["#"] + headers

    # Calculate width for line numbers based on total row count
    row_count = len(rows)
    if row_count <= 0:
        width = 1
    else:
        width = len(str(row_count))

    # Add line numbers to each row with consistent width
    new_rows = []
    for line_num, row in enumerate(rows, start=1):
        new_row = row.copy()  # Preserve all original fields
        new_row["#"] = format_line_number(line_num, width)
        new_rows.append(new_row)

    return new_headers, new_rows


def extract_participant_count_from_csv(csv_string: str) -> Optional[int]:
    """
    Extract participant count from CSV string by counting data rows.

    For CSV exports with line numbers, this counts all data rows
    (excluding the header row) to provide the total participant count.

    Args:
        csv_string: CSV formatted string with headers and data rows

    Returns:
        Number of data rows (participants) in the CSV, or None if empty/invalid

    Raises:
        ValueError: If CSV data is malformed or cannot be parsed
    """
    if not csv_string or not csv_string.strip():
        return None

    try:
        # Parse CSV data
        reader = csv.DictReader(io.StringIO(csv_string))

        # Count data rows
        count = 0
        for row in reader:
            count += 1

        return count if count > 0 else None

    except Exception as e:
        raise ValueError(f"Failed to parse CSV data: {e}")


def format_export_success_message(
    base_message: str,
    file_size_mb: float,
    timestamp: str,
    csv_data: Optional[str] = None,
) -> str:
    """
    Format export success message with optional participant count.

    Creates a standardized success message format for CSV exports
    that includes file size, timestamp, and optionally participant count
    extracted from the CSV data.

    Args:
        base_message: Base success message (e.g., "✅ Экспорт завершен успешно!")
        file_size_mb: File size in megabytes
        timestamp: Export timestamp string
        csv_data: Optional CSV data to extract participant count from

    Returns:
        Formatted success message string
    """
    message_parts = [base_message, ""]

    # Add participant count if available
    if csv_data:
        try:
            count = extract_participant_count_from_csv(csv_data)
            if count is not None:
                message_parts.append(f"👥 Участников: {count}")
        except Exception:
            # Silently skip count if extraction fails
            pass

    # Add file info
    message_parts.extend(
        [f"📁 Размер файла: {file_size_mb:.2f}MB", f"📅 Дата экспорта: {timestamp}"]
    )

    return "\n".join(message_parts)


def extract_headers_from_view_records(
    records: Optional[List[Dict[str, Any]]],
) -> List[str]:
    """
    Extract column headers from Airtable view records.

    Uses the first record's field order as returned by the view,
    which preserves the view's column ordering.

    Args:
        records: List of Airtable record dictionaries with 'fields' key

    Returns:
        List of field names in view order, or empty list if no records
    """
    if not records:
        return []

    # Get first record's fields
    if not records[0].get("fields"):
        return []

    # Python 3.7+ preserves dict insertion order, matching Airtable view order
    return list(records[0]["fields"].keys())


def order_rows_by_view_headers(
    view_headers: List[str], original_headers: List[str], rows: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Reorder row dictionaries to match view header order.

    Creates new row dictionaries with fields ordered according to
    view headers, preserving line numbers if present.

    Args:
        view_headers: Desired column order from view
        original_headers: Current column headers (may include '#')
        rows: List of row dictionaries to reorder

    Returns:
        List of reordered row dictionaries
    """
    if not rows:
        return []

    reordered_rows = []

    for row in rows:
        new_row = {}

        # Always preserve line number column first if present
        if "#" in row:
            new_row["#"] = row["#"]

        # Add fields in view header order
        for header in view_headers:
            if header in row:
                new_row[header] = row[header]

        reordered_rows.append(new_row)

    return reordered_rows
