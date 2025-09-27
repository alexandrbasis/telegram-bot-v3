"""
Unit tests for export utility functions.

Tests line number formatting and CSV manipulation utilities
following TDD approach for AGB-72 implementation.
"""

import csv
import io
from typing import List

import pytest

from src.utils.export_utils import (
    add_line_numbers_to_csv,
    add_line_numbers_to_rows,
    extract_headers_from_view_records,
    extract_participant_count_from_csv,
    format_export_success_message,
    format_line_number,
    order_rows_by_view_headers,
)


class TestLineNumberFormatting:
    """Test line number formatting utility."""

    def test_format_line_number_basic(self):
        """Test basic line number formatting."""
        assert format_line_number(1) == "1"
        assert format_line_number(5) == "5"
        assert format_line_number(10) == "10"

    def test_format_line_number_large_numbers(self):
        """Test formatting with larger numbers."""
        assert format_line_number(99) == "99"
        assert format_line_number(100) == "100"
        assert format_line_number(999) == "999"
        assert format_line_number(1000) == "1000"

    def test_format_line_number_edge_cases(self):
        """Test edge cases for line number formatting."""
        # Should handle minimum valid line number
        assert format_line_number(1) == "1"

        # Should handle zero (even though not typically used)
        assert format_line_number(0) == "0"

    def test_format_line_number_invalid_input(self):
        """Test error handling for invalid inputs."""
        with pytest.raises(ValueError):
            format_line_number(-1)

    def test_format_line_number_with_width(self):
        """Test line number formatting with width parameter."""
        # Test right-alignment with width
        assert format_line_number(1, 3) == "  1"
        assert format_line_number(10, 3) == " 10"
        assert format_line_number(100, 3) == "100"

        # Test with different widths
        assert format_line_number(5, 1) == "5"
        assert format_line_number(5, 2) == " 5"
        assert format_line_number(5, 4) == "   5"

    def test_format_line_number_width_edge_cases(self):
        """Test edge cases for width parameter."""
        # Width exactly matching number length
        assert format_line_number(1, 1) == "1"
        assert format_line_number(99, 2) == "99"
        assert format_line_number(1000, 4) == "1000"

        # Width smaller than number length (should not truncate)
        assert format_line_number(100, 2) == "100"
        assert format_line_number(1000, 1) == "1000"

    def test_format_line_number_width_validation(self):
        """Test validation for width parameter."""
        # Invalid width values
        with pytest.raises(ValueError):
            format_line_number(1, 0)

        with pytest.raises(ValueError):
            format_line_number(1, -1)

        with pytest.raises(TypeError):
            format_line_number(1, "3")

        with pytest.raises(TypeError):
            format_line_number(1, 3.5)

    def test_format_line_number_width_none(self):
        """Test that width=None behaves like original function."""
        assert format_line_number(1, None) == "1"
        assert format_line_number(100, None) == "100"
        assert format_line_number(999, None) == "999"

        with pytest.raises(TypeError):
            format_line_number("1")

        with pytest.raises(TypeError):
            format_line_number(None)


class TestAddLineNumbersToCSV:
    """Test adding line numbers to CSV string."""

    def test_add_line_numbers_to_empty_csv(self):
        """Test adding line numbers to CSV with headers only."""
        csv_input = "Name,Age\n"
        result = add_line_numbers_to_csv(csv_input)

        expected = "#,Name,Age\n"
        assert result == expected

    def test_add_line_numbers_to_single_row_csv(self):
        """Test adding line numbers to CSV with one data row."""
        csv_input = "Name,Age\nJohn,25\n"
        result = add_line_numbers_to_csv(csv_input)

        expected = "#,Name,Age\n1,John,25\n"
        assert result == expected

    def test_add_line_numbers_to_multiple_rows_csv(self):
        """Test adding line numbers to CSV with multiple data rows."""
        csv_input = "Name,Age\nJohn,25\nJane,30\nBob,35\n"
        result = add_line_numbers_to_csv(csv_input)

        expected = "#,Name,Age\n1,John,25\n2,Jane,30\n3,Bob,35\n"
        assert result == expected

    def test_add_line_numbers_with_russian_content(self):
        """Test line numbers with Russian text content."""
        csv_input = "FullNameRU,Age\nИванов Иван,25\nПетров Петр,30\n"
        result = add_line_numbers_to_csv(csv_input)

        expected = "#,FullNameRU,Age\n1,Иванов Иван,25\n2,Петров Петр,30\n"
        assert result == expected

    def test_add_line_numbers_with_special_characters(self):
        """Test line numbers with special characters in CSV."""
        csv_input = 'Name,Description\n"John, Jr.",Contains comma\n"Jane ""Air"" Smith",Contains quotes\n'
        result = add_line_numbers_to_csv(csv_input)

        expected = '#,Name,Description\n1,"John, Jr.",Contains comma\n2,"Jane ""Air"" Smith",Contains quotes\n'
        assert result == expected

    def test_add_line_numbers_large_dataset(self):
        """Test line numbers with large dataset (3-digit numbers) and consistent width."""
        # Create CSV with 150 rows to test 3-digit line numbers
        header = "Name,Value\n"
        rows = "\n".join([f"Person{i},{i * 10}" for i in range(1, 151)])
        csv_input = header + rows + "\n"

        result = add_line_numbers_to_csv(csv_input)

        # Verify line numbers are present with consistent width
        lines = result.strip().split("\n")
        assert lines[0] == "#,Name,Value"  # Header

        # With 150 rows, all line numbers should be right-aligned to width 3
        assert lines[1] == "  1,Person1,10"  # First row (padded to 3 chars)
        assert (
            lines[10] == " 10,Person10,100"
        )  # Two-digit line number (padded to 3 chars)
        assert lines[100] == "100,Person100,1000"  # Three-digit line number
        assert lines[150] == "150,Person150,1500"  # Last row
        assert len(lines) == 151  # Header + 150 data rows

    def test_add_line_numbers_empty_string(self):
        """Test adding line numbers to empty string."""
        result = add_line_numbers_to_csv("")
        assert result == ""

    def test_add_line_numbers_invalid_csv(self):
        """Test error handling for malformed CSV."""
        # CSV with mismatched columns should still work
        csv_input = "A,B,C\n1,2\n3,4,5,6\n"
        result = add_line_numbers_to_csv(csv_input)

        expected = "#,A,B,C\n1,1,2\n2,3,4,5,6\n"
        assert result == expected


class TestAddLineNumbersToRows:
    """Test adding line numbers to row data structures."""

    def test_add_line_numbers_to_empty_rows(self):
        """Test adding line numbers to empty row list."""
        headers = ["Name", "Age"]
        rows = []

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Age"]
        assert result_rows == []

    def test_add_line_numbers_to_single_row(self):
        """Test adding line numbers to single row."""
        headers = ["Name", "Age"]
        rows = [{"Name": "John", "Age": "25"}]

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Age"]
        assert len(result_rows) == 1
        assert result_rows[0]["#"] == "1"
        assert result_rows[0]["Name"] == "John"
        assert result_rows[0]["Age"] == "25"

    def test_add_line_numbers_to_multiple_rows(self):
        """Test adding line numbers to multiple rows."""
        headers = ["Name", "Age"]
        rows = [
            {"Name": "John", "Age": "25"},
            {"Name": "Jane", "Age": "30"},
            {"Name": "Bob", "Age": "35"},
        ]

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Age"]
        assert len(result_rows) == 3

        # Check line numbers are sequential
        for i, row in enumerate(result_rows, 1):
            assert row["#"] == str(i)

        # Check original data is preserved
        assert result_rows[0]["Name"] == "John"
        assert result_rows[1]["Name"] == "Jane"
        assert result_rows[2]["Name"] == "Bob"

    def test_add_line_numbers_to_rows_with_width_consistency(self):
        """Test that line numbers in rows have consistent width formatting."""
        headers = ["Name", "Value"]
        # Create 150 rows to test 3-digit width consistency
        rows = [{"Name": f"Person{i}", "Value": str(i * 10)} for i in range(1, 151)]

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Value"]
        assert len(result_rows) == 150

        # With 150 rows, all line numbers should be right-aligned to width 3
        assert result_rows[0]["#"] == "  1"  # First row (padded to 3 chars)
        assert result_rows[9]["#"] == " 10"  # Two-digit line number (padded to 3 chars)
        assert result_rows[99]["#"] == "100"  # Three-digit line number
        assert result_rows[149]["#"] == "150"  # Last row

        # Verify original data is preserved
        assert result_rows[0]["Name"] == "Person1"
        assert result_rows[149]["Name"] == "Person150"

    def test_add_line_numbers_with_russian_headers(self):
        """Test line numbers with Russian header names."""
        headers = ["FullNameRU", "Department"]
        rows = [{"FullNameRU": "Иванов Иван", "Department": "IT"}]

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "FullNameRU", "Department"]
        assert result_rows[0]["#"] == "1"
        assert result_rows[0]["FullNameRU"] == "Иванов Иван"

    def test_add_line_numbers_preserves_extra_fields(self):
        """Test that extra fields in rows are preserved."""
        headers = ["Name", "Age"]
        rows = [{"Name": "John", "Age": "25", "ExtraField": "extra_value"}]

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Age"]
        assert result_rows[0]["#"] == "1"
        assert result_rows[0]["ExtraField"] == "extra_value"

    def test_add_line_numbers_handles_missing_fields(self):
        """Test handling rows with missing fields."""
        headers = ["Name", "Age", "City"]
        rows = [{"Name": "John", "Age": "25"}]  # Missing City

        result_headers, result_rows = add_line_numbers_to_rows(headers, rows)

        assert result_headers == ["#", "Name", "Age", "City"]
        assert result_rows[0]["#"] == "1"
        assert result_rows[0]["Name"] == "John"
        assert result_rows[0]["Age"] == "25"
        # City field should be missing (not added by the function)


class TestParticipantCountExtraction:
    """Test participant count extraction from CSV data."""

    def test_extract_count_from_valid_csv_with_line_numbers(self):
        """Test extracting count from valid CSV with line numbers."""
        csv_data = (
            "#,Name,Age\n" "1,John Doe,25\n" "2,Jane Smith,30\n" "3,Bob Johnson,35"
        )

        result = extract_participant_count_from_csv(csv_data)
        assert result == 3

    def test_extract_count_from_empty_csv(self):
        """Test extracting count from empty CSV."""
        csv_data = "#,Name,Age\n"  # Header only, no data rows

        result = extract_participant_count_from_csv(csv_data)
        assert result is None

    def test_extract_count_from_empty_string(self):
        """Test extracting count from empty string."""
        result = extract_participant_count_from_csv("")
        assert result is None

        result = extract_participant_count_from_csv("   ")
        assert result is None

    def test_extract_count_from_none(self):
        """Test extracting count from None."""
        result = extract_participant_count_from_csv(None)
        assert result is None

    def test_extract_count_from_large_csv(self):
        """Test extracting count from large CSV with many rows."""
        lines = ["#,Name,Department"]
        for i in range(500):
            lines.append(f"{i + 1},Person {i + 1},Department {i % 5}")

        csv_data = "\n".join(lines)
        result = extract_participant_count_from_csv(csv_data)
        assert result == 500

    def test_extract_count_from_malformed_csv(self):
        """Test extracting count from malformed CSV raises ValueError."""
        malformed_csv = "Invalid\nCSV\nData"

        # This should still work as DictReader is quite tolerant
        result = extract_participant_count_from_csv(malformed_csv)
        # DictReader will treat first line as headers and count remaining lines
        assert result == 2

    def test_extract_count_from_unicode_csv(self):
        """Test extracting count from CSV with Unicode content."""
        csv_data = "#,ФИО,Возраст\n" "1,Иванов Иван,25\n" "2,Петрова Мария,30"

        result = extract_participant_count_from_csv(csv_data)
        assert result == 2


class TestExportSuccessMessageFormatting:
    """Test export success message formatting with participant count."""

    def test_format_message_with_participant_count(self):
        """Test formatting message with participant count extracted from CSV."""
        csv_data = "#,Name,Age\n" "1,John Doe,25\n" "2,Jane Smith,30"

        result = format_export_success_message(
            base_message="✅ Экспорт завершен успешно!",
            file_size_mb=1.5,
            timestamp="2025-01-26 15:30:00 UTC",
            csv_data=csv_data,
        )

        expected = (
            "✅ Экспорт завершен успешно!\n"
            "\n"
            "👥 Участников: 2\n"
            "📁 Размер файла: 1.50MB\n"
            "📅 Дата экспорта: 2025-01-26 15:30:00 UTC"
        )
        assert result == expected

    def test_format_message_without_csv_data(self):
        """Test formatting message without CSV data (no participant count)."""
        result = format_export_success_message(
            base_message="✅ Экспорт завершен успешно!",
            file_size_mb=2.75,
            timestamp="2025-01-26 15:30:00 UTC",
        )

        expected = (
            "✅ Экспорт завершен успешно!\n"
            "\n"
            "📁 Размер файла: 2.75MB\n"
            "📅 Дата экспорта: 2025-01-26 15:30:00 UTC"
        )
        assert result == expected

    def test_format_message_with_empty_csv(self):
        """Test formatting message with empty CSV (no participant count shown)."""
        csv_data = "#,Name,Age\n"  # Header only

        result = format_export_success_message(
            base_message="✅ Экспорт завершен успешно!",
            file_size_mb=0.1,
            timestamp="2025-01-26 15:30:00 UTC",
            csv_data=csv_data,
        )

        expected = (
            "✅ Экспорт завершен успешно!\n"
            "\n"
            "📁 Размер файла: 0.10MB\n"
            "📅 Дата экспорта: 2025-01-26 15:30:00 UTC"
        )
        assert result == expected

    def test_format_message_with_malformed_csv(self):
        """Test formatting message with malformed CSV (gracefully skips count)."""
        csv_data = "Invalid CSV Data"

        result = format_export_success_message(
            base_message="✅ Экспорт завершен успешно!",
            file_size_mb=1.0,
            timestamp="2025-01-26 15:30:00 UTC",
            csv_data=csv_data,
        )

        # Should gracefully skip participant count and include other info
        expected = (
            "✅ Экспорт завершен успешно!\n"
            "\n"
            "📁 Размер файла: 1.00MB\n"
            "📅 Дата экспорта: 2025-01-26 15:30:00 UTC"
        )
        assert result == expected

    def test_format_message_with_large_count(self):
        """Test formatting message with large participant count."""
        lines = ["#,Name,Department"]
        for i in range(1500):
            lines.append(f"{i + 1},Person {i + 1},Department")

        csv_data = "\n".join(lines)

        result = format_export_success_message(
            base_message="✅ Экспорт завершен успешно!",
            file_size_mb=10.25,
            timestamp="2025-01-26 15:30:00 UTC",
            csv_data=csv_data,
        )

        expected = (
            "✅ Экспорт завершен успешно!\n"
            "\n"
            "👥 Участников: 1500\n"
            "📁 Размер файла: 10.25MB\n"
            "📅 Дата экспорта: 2025-01-26 15:30:00 UTC"
        )
        assert result == expected


class TestExtractHeadersFromViewRecords:
    """Test extracting headers from Airtable view records."""

    def test_extract_headers_from_empty_records(self):
        """Test extracting headers from empty record list."""
        records = []
        headers = extract_headers_from_view_records(records)
        assert headers == []

    def test_extract_headers_from_single_record(self):
        """Test extracting headers from single record preserves field order."""
        records = [
            {
                "fields": {
                    "Name": "John Doe",
                    "Age": 25,
                    "Department": "IT",
                }
            }
        ]

        # Should extract keys in the order they appear in the first record
        headers = extract_headers_from_view_records(records)
        assert headers == ["Name", "Age", "Department"]

    def test_extract_headers_from_multiple_records(self):
        """Test extracting headers accumulates all fields from all records."""
        records = [
            {
                "fields": {
                    "FullNameRU": "Иванов Иван",
                    "Department": "IT",
                    "Status": "Active",
                }
            },
            {
                "fields": {
                    "Status": "Inactive",  # Different order
                    "FullNameRU": "Петров Петр",
                    "Department": "HR",
                    "ExtraField": "Value",  # Extra field in second record
                }
            },
        ]

        # Should include all fields from all records, preserving first appearance order
        headers = extract_headers_from_view_records(records)
        assert headers == ["FullNameRU", "Department", "Status", "ExtraField"]

    def test_extract_headers_preserves_view_order(self):
        """Test that headers preserve Airtable view's column order."""
        # Simulate Airtable view response with specific field order
        records = [
            {
                "fields": {
                    "Дата": "2025-01-15",
                    "Время": "10:00",
                    "ФИО": "Иванов Иван",
                    "Роль": "Чтец",
                    "Текст": "Псалом 23",
                }
            }
        ]

        headers = extract_headers_from_view_records(records)
        # Order should match exactly as returned by view
        assert headers == ["Дата", "Время", "ФИО", "Роль", "Текст"]

    def test_extract_headers_handles_missing_fields(self):
        """Test extracting headers from record with no fields."""
        records = [{"fields": {}}]
        headers = extract_headers_from_view_records(records)
        assert headers == []

    def test_extract_headers_handles_none_records(self):
        """Test extracting headers from None returns empty list."""
        headers = extract_headers_from_view_records(None)
        assert headers == []


class TestOrderRowsByViewHeaders:
    """Test reordering rows to match view header order."""

    def test_order_rows_empty_inputs(self):
        """Test ordering with empty inputs."""
        result = order_rows_by_view_headers([], [], [])
        assert result == []

        result = order_rows_by_view_headers(["Name", "Age"], [], [])
        assert result == []

    def test_order_rows_single_row(self):
        """Test ordering single row to match view headers."""
        view_headers = ["Age", "Name", "Department"]
        original_headers = ["Name", "Age", "Department"]
        rows = [{"Name": "John", "Age": "25", "Department": "IT"}]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        # Row should be reordered to match view header order
        assert len(result) == 1
        assert list(result[0].keys()) == ["Age", "Name", "Department"]
        assert result[0]["Age"] == "25"
        assert result[0]["Name"] == "John"
        assert result[0]["Department"] == "IT"

    def test_order_rows_multiple_rows(self):
        """Test ordering multiple rows to match view headers."""
        view_headers = ["Department", "FullNameRU", "Status"]
        original_headers = ["FullNameRU", "Status", "Department"]
        rows = [
            {"FullNameRU": "Иванов Иван", "Status": "Active", "Department": "IT"},
            {"FullNameRU": "Петров Петр", "Status": "Inactive", "Department": "HR"},
        ]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 2
        # Check first row ordering
        assert list(result[0].keys()) == ["Department", "FullNameRU", "Status"]
        assert result[0]["Department"] == "IT"
        assert result[0]["FullNameRU"] == "Иванов Иван"

        # Check second row ordering
        assert list(result[1].keys()) == ["Department", "FullNameRU", "Status"]
        assert result[1]["Department"] == "HR"
        assert result[1]["FullNameRU"] == "Петров Петр"

    def test_order_rows_preserves_line_numbers(self):
        """Test that line number column is preserved during reordering."""
        view_headers = ["Name", "Age"]
        original_headers = ["#", "Age", "Name"]  # Line number included
        rows = [
            {"#": "1", "Age": "25", "Name": "John"},
            {"#": "2", "Age": "30", "Name": "Jane"},
        ]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        # Line numbers should be preserved even if not in view headers
        assert len(result) == 2
        assert "#" in result[0]
        assert result[0]["#"] == "1"
        assert result[1]["#"] == "2"
        # Other fields should be reordered
        assert list(result[0].keys()) == ["#", "Name", "Age"]

    def test_order_rows_handles_missing_fields(self):
        """Test ordering preserves all view headers even with missing field values."""
        view_headers = ["Name", "Age", "City"]
        original_headers = ["Name", "Age"]
        rows = [{"Name": "John", "Age": "25"}]  # Missing City

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 1
        # Should include all view headers, using empty string for missing values
        assert list(result[0].keys()) == ["Name", "Age", "City"]
        assert result[0]["Name"] == "John"
        assert result[0]["Age"] == "25"
        assert result[0]["City"] == ""  # Missing field gets empty string

    def test_order_rows_handles_extra_fields(self):
        """Test ordering handles rows with extra fields not in view."""
        view_headers = ["Name", "Age"]
        original_headers = ["Name", "Age", "Department", "City"]
        rows = [{"Name": "John", "Age": "25", "Department": "IT", "City": "NYC"}]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 1
        # Should only include fields from view headers
        assert list(result[0].keys()) == ["Name", "Age"]
        assert result[0]["Name"] == "John"
        assert result[0]["Age"] == "25"
        assert "Department" not in result[0]
        assert "City" not in result[0]

    def test_order_rows_complex_reordering(self):
        """Test complex reordering with Russian field names."""
        view_headers = ["Дата", "Время", "ФИО", "Роль", "Текст"]
        original_headers = ["ФИО", "Текст", "Роль", "Время", "Дата"]
        rows = [
            {
                "ФИО": "Иванов Иван",
                "Текст": "Псалом 23",
                "Роль": "Чтец",
                "Время": "10:00",
                "Дата": "2025-01-15",
            }
        ]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 1
        assert list(result[0].keys()) == view_headers
        assert result[0]["Дата"] == "2025-01-15"
        assert result[0]["Время"] == "10:00"
        assert result[0]["ФИО"] == "Иванов Иван"


class TestSparseRecordScenarios:
    """Test critical sparse-record scenarios that caused the original bug."""

    def test_extract_headers_first_record_missing_fields(self):
        """Test header extraction when first record misses fields from later records.

        This is the CRITICAL bug scenario: if the first record lacks values for some
        columns that appear in later records, those columns would be completely
        omitted from exports.
        """
        records = [
            {
                # First record missing "Email" and "Phone" fields
                "fields": {
                    "Name": "John Doe",
                    "Department": "IT"
                }
            },
            {
                # Second record has all fields including those missing from first
                "fields": {
                    "Name": "Jane Smith",
                    "Department": "HR",
                    "Email": "jane@example.com",  # Missing from first record
                    "Phone": "555-0123"  # Missing from first record
                }
            },
            {
                # Third record has different subset
                "fields": {
                    "Name": "Bob Wilson",
                    "Email": "bob@example.com",  # Has email but missing department & phone
                    "Position": "Manager"  # New field not in first records
                }
            }
        ]

        headers = extract_headers_from_view_records(records)

        # Should include ALL fields from ALL records in order of first appearance
        expected_headers = ["Name", "Department", "Email", "Phone", "Position"]
        assert headers == expected_headers

    def test_order_rows_with_sparse_data_preserves_all_columns(self):
        """Test row ordering preserves all view columns even with very sparse data."""
        view_headers = ["Name", "Department", "Email", "Phone", "Position"]
        original_headers = ["Name", "Department", "Email", "Phone", "Position"]

        # Simulate real-world sparse data where different records have different fields
        rows = [
            {"Name": "John Doe", "Department": "IT"},  # Missing Email, Phone, Position
            {"Name": "Jane Smith", "Email": "jane@example.com", "Phone": "555-0123"},  # Missing Department, Position
            {"Name": "Bob Wilson", "Position": "Manager"},  # Missing Department, Email, Phone
            {"Department": "Finance", "Email": "finance@example.com"}  # Missing Name, Phone, Position
        ]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 4

        # Verify all rows have all columns in correct order
        for row in result:
            assert list(row.keys()) == view_headers

        # Verify specific values and empty strings for missing data
        assert result[0]["Name"] == "John Doe"
        assert result[0]["Department"] == "IT"
        assert result[0]["Email"] == ""  # Missing, should be empty
        assert result[0]["Phone"] == ""  # Missing, should be empty
        assert result[0]["Position"] == ""  # Missing, should be empty

        assert result[1]["Name"] == "Jane Smith"
        assert result[1]["Department"] == ""  # Missing, should be empty
        assert result[1]["Email"] == "jane@example.com"
        assert result[1]["Phone"] == "555-0123"
        assert result[1]["Position"] == ""  # Missing, should be empty

    def test_end_to_end_sparse_airtable_view_simulation(self):
        """Test complete sparse-record workflow simulating real Airtable view data.

        This simulates the exact bug scenario: Airtable view where early records
        have missing field values, which would cause those columns to disappear
        from CSV exports entirely.
        """
        # Simulate Airtable view response where records have different field coverage
        airtable_records = [
            {
                "id": "rec1",
                "fields": {
                    "FullNameRU": "Иванов Иван",
                    "Status": "Candidate"
                    # Missing Email, Phone, Notes - these fields exist in view but not populated
                }
            },
            {
                "id": "rec2",
                "fields": {
                    "FullNameRU": "Петров Петр",
                    "Email": "petrov@example.com",
                    "Phone": "+7-123-456-7890"
                    # Missing Status, Notes
                }
            },
            {
                "id": "rec3",
                "fields": {
                    "FullNameRU": "Сидоров Сидор",
                    "Status": "Active",
                    "Email": "sidorov@example.com",
                    "Notes": "Special instructions"
                    # Missing Phone
                }
            }
        ]

        # Step 1: Extract headers from view records (should get ALL fields)
        view_headers = extract_headers_from_view_records(airtable_records)
        expected_view_headers = ["FullNameRU", "Status", "Email", "Phone", "Notes"]
        assert view_headers == expected_view_headers

        # Step 2: Convert to row format for CSV export
        rows = []
        for record in airtable_records:
            row = record["fields"].copy()
            rows.append(row)

        # Step 3: Reorder rows to match view header order (should preserve all columns)
        ordered_rows = order_rows_by_view_headers(view_headers, view_headers, rows)

        # Verify complete column structure is maintained
        assert len(ordered_rows) == 3
        for row in ordered_rows:
            assert list(row.keys()) == view_headers

        # Verify data integrity with proper empty string handling
        assert ordered_rows[0]["FullNameRU"] == "Иванов Иван"
        assert ordered_rows[0]["Status"] == "Candidate"
        assert ordered_rows[0]["Email"] == ""  # Missing in original, should be empty
        assert ordered_rows[0]["Phone"] == ""  # Missing in original, should be empty
        assert ordered_rows[0]["Notes"] == ""  # Missing in original, should be empty

        assert ordered_rows[1]["FullNameRU"] == "Петров Петр"
        assert ordered_rows[1]["Status"] == ""  # Missing in original, should be empty
        assert ordered_rows[1]["Email"] == "petrov@example.com"
        assert ordered_rows[1]["Phone"] == "+7-123-456-7890"
        assert ordered_rows[1]["Notes"] == ""  # Missing in original, should be empty

        assert ordered_rows[2]["FullNameRU"] == "Сидоров Сидор"
        assert ordered_rows[2]["Status"] == "Active"
        assert ordered_rows[2]["Email"] == "sidorov@example.com"
        assert ordered_rows[2]["Phone"] == ""  # Missing in original, should be empty
        assert ordered_rows[2]["Notes"] == "Special instructions"

    def test_extract_headers_extremely_sparse_first_record(self):
        """Test header extraction when first record has minimal fields."""
        records = [
            {
                "fields": {
                    "Name": "John"  # Only one field in first record
                }
            },
            {
                "fields": {
                    "Name": "Jane",
                    "Email": "jane@example.com",
                    "Department": "HR",
                    "Phone": "555-0123",
                    "Manager": "Bob Smith",
                    "StartDate": "2025-01-01"
                }
            }
        ]

        headers = extract_headers_from_view_records(records)

        # Should capture all fields, not just the one from first record
        expected_headers = ["Name", "Email", "Department", "Phone", "Manager", "StartDate"]
        assert headers == expected_headers

    def test_order_rows_with_line_numbers_and_sparse_data(self):
        """Test row ordering preserves line numbers and handles sparse data correctly."""
        view_headers = ["Name", "Email", "Phone"]
        original_headers = ["#", "Name", "Email", "Phone"]

        rows = [
            {"#": "1", "Name": "John"},  # Missing Email, Phone
            {"#": "2", "Email": "jane@example.com"},  # Missing Name, Phone
            {"#": "3", "Name": "Bob", "Phone": "555-0123"}  # Missing Email
        ]

        result = order_rows_by_view_headers(view_headers, original_headers, rows)

        assert len(result) == 3

        # Verify line numbers are preserved and all view headers are included
        for i, row in enumerate(result, 1):
            assert row["#"] == str(i)
            assert list(row.keys()) == ["#", "Name", "Email", "Phone"]

        # Verify sparse data handling
        assert result[0]["Name"] == "John"
        assert result[0]["Email"] == ""
        assert result[0]["Phone"] == ""

        assert result[1]["Name"] == ""
        assert result[1]["Email"] == "jane@example.com"
        assert result[1]["Phone"] == ""

        assert result[2]["Name"] == "Bob"
        assert result[2]["Email"] == ""
        assert result[2]["Phone"] == "555-0123"
