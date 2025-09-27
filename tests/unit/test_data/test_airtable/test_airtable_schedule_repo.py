"""Unit tests for AirtableScheduleRepository formula building and behavior."""

import datetime as dt

import pytest

from src.data.airtable.airtable_client import AirtableAPIError
from src.data.airtable.airtable_schedule_repo import AirtableScheduleRepository
from src.data.repositories.participant_repository import RepositoryError


class TestScheduleFormula:
    def test_inclusive_date_range_formula_contains_boundaries(self):
        start = dt.date(2025, 11, 13)
        end = dt.date(2025, 11, 16)

        formula = AirtableScheduleRepository._build_formula(start, end)

        # Active flag must be enforced
        assert "{IsActive} = TRUE()" in formula

        # Lower bound inclusive: either after start or same day
        assert "IS_AFTER({EventDate}, '2025-11-13')" in formula
        assert "IS_SAME({EventDate}, '2025-11-13', 'day')" in formula

        # Upper bound inclusive: either before end or same day
        assert "IS_BEFORE({EventDate}, '2025-11-16')" in formula
        assert "IS_SAME({EventDate}, '2025-11-16', 'day')" in formula

        # Ensure no invalid arithmetic hacks like "+ 1" exist
        assert "+ 1" not in formula


class TestScheduleSorting:
    def test_sort_params(self):
        sort = AirtableScheduleRepository._sort_params()
        # Ensure deterministic, expected sort fields
        assert sort == ["EventDate", "Order", "StartTime"]


class FakeAirtableClient:
    """Simple fake Airtable client returning predefined records."""

    def __init__(self, records=None, error: Exception | None = None):
        self.records = records or []
        self.error = error
        self.calls = []

    async def list_records(self, **kwargs):
        self.calls.append(kwargs)
        if self.error is not None:
            raise self.error
        return self.records


@pytest.mark.asyncio
async def test_fetch_schedule_converts_records_and_skips_invalid():
    valid_record = {
        "id": "rec1",
        "fields": {
            "EventDate": "2025-11-13",
            "StartTime": "09:00",
            "EndTime": "",
            "EventTitle": "Утро",
            "IsActive": True,
        },
    }
    invalid_record = {
        "id": "rec2",
        "fields": {
            "EventDate": "2025-11-13",
        },
    }
    client = FakeAirtableClient(records=[valid_record, invalid_record])
    repo = AirtableScheduleRepository(client)

    entries = await repo.fetch_schedule(dt.date(2025, 11, 13), dt.date(2025, 11, 13))

    assert len(entries) == 1
    entry = entries[0]
    assert entry.record_id == "rec1"
    assert entry.end_time is None  # blank end time handled
    assert client.calls  # client invoked with parameters
    assert client.calls[0]["sort"] == ["EventDate", "Order", "StartTime"]


@pytest.mark.asyncio
async def test_fetch_schedule_wraps_airtable_errors():
    client = FakeAirtableClient(error=AirtableAPIError("boom"))
    repo = AirtableScheduleRepository(client)

    with pytest.raises(RepositoryError) as exc_info:
        await repo.fetch_schedule(dt.date(2025, 11, 13), dt.date(2025, 11, 16))

    assert "Failed to fetch schedule" in str(exc_info.value)
