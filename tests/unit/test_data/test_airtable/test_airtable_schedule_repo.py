"""Unit tests for AirtableScheduleRepository formula building and sorting."""

import datetime as dt

from src.data.airtable.airtable_schedule_repo import AirtableScheduleRepository


class TestScheduleFormula:
    def test_inclusive_date_range_formula_contains_boundaries(self):
        start = dt.date(2025, 11, 13)
        end = dt.date(2025, 11, 16)

        formula = AirtableScheduleRepository._build_formula(start, end)

        # Active flag must be enforced
        assert "{IsActive} = TRUE()" in formula

        # Lower bound inclusive: either after start or same day
        assert "IS_AFTER({Date}, '2025-11-13')" in formula
        assert "IS_SAME({Date}, '2025-11-13', 'day')" in formula

        # Upper bound inclusive: either before end or same day
        assert "IS_BEFORE({Date}, '2025-11-16')" in formula
        assert "IS_SAME({Date}, '2025-11-16', 'day')" in formula

        # Ensure no invalid arithmetic hacks like "+ 1" exist
        assert "+ 1" not in formula


class TestScheduleSorting:
    def test_sort_params(self):
        sort = AirtableScheduleRepository._sort_params()
        # Ensure deterministic, expected sort fields
        assert sort == ["Date", "Order", "StartTime"]
