"""
Unit tests for export utility functions.

Tests line number formatting and CSV manipulation utilities
following TDD approach for AGB-72 implementation.
"""

import csv
import io
import pytest
from typing import List

from src.utils.export_utils import (
    format_line_number,
    add_line_numbers_to_csv,
    add_line_numbers_to_rows
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
        """Test line numbers with large dataset (3-digit numbers)."""
        # Create CSV with 150 rows to test 3-digit line numbers
        header = "Name,Value\n"
        rows = "\n".join([f"Person{i},{i*10}" for i in range(1, 151)])
        csv_input = header + rows + "\n"

        result = add_line_numbers_to_csv(csv_input)

        # Verify line numbers are present
        lines = result.strip().split('\n')
        assert lines[0] == "#,Name,Value"  # Header
        assert lines[1] == "1,Person1,10"  # First row
        assert lines[100] == "100,Person100,1000"  # 3-digit line number
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
            {"Name": "Bob", "Age": "35"}
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