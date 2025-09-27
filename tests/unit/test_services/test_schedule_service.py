"""Unit tests for ScheduleService caching and refresh behavior."""

import datetime as dt
from types import SimpleNamespace
from typing import List

import pytest

from src.models.schedule import ScheduleEntry
from src.services import schedule_service as schedule_service_module
from src.services.schedule_service import ScheduleService


class FakeRepository:
    """Fake repository that returns predefined sequences of entries."""

    def __init__(self, responses: List[List[ScheduleEntry]] | Exception):
        if isinstance(responses, Exception):
            self._responses = responses
        else:
            self._responses = [list(batch) for batch in responses]
        self.calls: list[tuple[dt.date, dt.date]] = []

    async def fetch_schedule(self, date_from: dt.date, date_to: dt.date):
        self.calls.append((date_from, date_to))
        if isinstance(self._responses, Exception):
            raise self._responses
        if not self._responses:
            return []
        return self._responses.pop(0)


class TimeStub:
    """Mutable time stub for deterministic cache tests."""

    def __init__(self, value: float = 1000.0):
        self.value = value

    def time(self) -> float:
        return self.value


def _entry(day: dt.date, hour: int, title: str) -> ScheduleEntry:
    return ScheduleEntry(
        date=day,
        start_time=dt.time(hour, 0),
        title=title,
    )


@pytest.fixture
def time_stub(monkeypatch):
    stub = TimeStub()
    monkeypatch.setattr(
        schedule_service_module, "time", SimpleNamespace(time=stub.time)
    )
    return stub


@pytest.mark.asyncio
async def test_get_schedule_range_uses_cache_within_ttl(time_stub):
    day = dt.date(2025, 11, 13)
    repo = FakeRepository([[_entry(day, 9, "Opening")]])

    service = ScheduleService(repository=repo, cache_ttl_seconds=300)

    first = await service.get_schedule_range(day, day)
    second = await service.get_schedule_range(day, day)

    assert repo.calls == [(day, day)]  # repository hit once
    assert first == second


@pytest.mark.asyncio
async def test_get_schedule_range_cache_expires_after_ttl(time_stub):
    day = dt.date(2025, 11, 13)
    repo = FakeRepository(
        [
            [_entry(day, 9, "Opening")],
            [_entry(day, 10, "Session")],
        ]
    )

    service = ScheduleService(repository=repo, cache_ttl_seconds=300)

    first = await service.get_schedule_range(day, day)
    time_stub.value += 301
    second = await service.get_schedule_range(day, day)

    assert len(repo.calls) == 2
    assert first != second
    assert second[0].title == "Session"


@pytest.mark.asyncio
async def test_refresh_schedule_for_date_bypasses_cache(time_stub):
    day = dt.date(2025, 11, 13)
    repo = FakeRepository(
        [
            [_entry(day, 9, "Opening")],
            [_entry(day, 10, "Updated")],
        ]
    )

    service = ScheduleService(repository=repo, cache_ttl_seconds=600)

    initial = await service.get_schedule_for_date(day)
    refreshed = await service.refresh_schedule_for_date(day)
    cached_after_refresh = await service.get_schedule_for_date(day)

    assert [call[0] for call in repo.calls] == [day, day]  # refresh triggers new fetch
    assert initial[0].title == "Opening"
    assert refreshed[0].title == "Updated"
    assert cached_after_refresh[0].title == "Updated"


@pytest.mark.asyncio
async def test_refresh_schedule_range_swaps_dates(time_stub):
    earlier = dt.date(2025, 11, 13)
    later = dt.date(2025, 11, 16)
    repo = FakeRepository([[_entry(earlier, 9, "Opening")]])

    service = ScheduleService(repository=repo, cache_ttl_seconds=600)

    await service.refresh_schedule_range(later, earlier)

    assert repo.calls[0] == (earlier, later)


def test_invalid_cache_ttl_raises_value_error():
    with pytest.raises(ValueError):
        ScheduleService(cache_ttl_seconds=0)

    with pytest.raises(ValueError):
        ScheduleService(cache_ttl_seconds=4000)


@pytest.mark.asyncio
async def test_repository_error_propagates(time_stub):
    day = dt.date(2025, 11, 13)
    repo = FakeRepository(Exception("boom"))

    service = ScheduleService(repository=repo)

    with pytest.raises(Exception) as exc_info:
        await service.get_schedule_for_date(day)

    assert "boom" in str(exc_info.value)
