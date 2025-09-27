"""
Service for fetching and caching schedule entries from Airtable.
"""

from __future__ import annotations

import datetime as dt
import logging
import time
from typing import Dict, List, Optional, Tuple

from src.data.airtable.airtable_client_factory import AirtableClientFactory
from src.data.airtable.airtable_schedule_repo import AirtableScheduleRepository
from src.models.schedule import ScheduleEntry

logger = logging.getLogger(__name__)


class ScheduleService:
    """High-level API for retrieving schedule data with TTL cache."""

    # Lazily initialized repository (so tests can inject easily)
    def __init__(
        self,
        repository: Optional[AirtableScheduleRepository] = None,
        cache_ttl_seconds: int = 600,
    ) -> None:
        """Initialize service with optional repository injection."""
        # Validate TTL bounds (1 second to 1 hour)
        if not 1 <= cache_ttl_seconds <= 3600:
            raise ValueError("Cache TTL must be between 1 and 3600 seconds")
        self.cache_ttl_seconds = cache_ttl_seconds
        self._cache: Dict[str, Tuple[float, List[ScheduleEntry]]] = {}
        self._repo = repository or self._create_default_repository()

    @staticmethod
    def _create_default_repository() -> AirtableScheduleRepository:
        """Create default Airtable repository."""
        factory = AirtableClientFactory()
        client = factory.create_client("schedule")
        return AirtableScheduleRepository(client)

    def _get_repo(self) -> AirtableScheduleRepository:
        """Accessor for the underlying repository (allows late injection)."""
        return self._repo

    def _cache_key(self, date_from: dt.date, date_to: dt.date) -> str:
        return f"{date_from.isoformat()}_{date_to.isoformat()}"

    def clear_cache(self) -> None:
        self._cache.clear()

    async def get_schedule_range(
        self, date_from: dt.date, date_to: dt.date
    ) -> List[ScheduleEntry]:
        """Get schedule entries for an inclusive date range with caching."""
        if date_to < date_from:
            date_from, date_to = date_to, date_from

        key = self._cache_key(date_from, date_to)
        now = time.time()
        cached = self._cache.get(key)
        if cached and now - cached[0] <= self.cache_ttl_seconds:
            return cached[1]

        entries = await self._get_repo().fetch_schedule(date_from, date_to)
        self._cache[key] = (now, entries)
        return entries

    async def get_schedule_for_date(self, date_value: dt.date) -> List[ScheduleEntry]:
        return await self.get_schedule_range(date_value, date_value)

    async def refresh_schedule_range(
        self, date_from: dt.date, date_to: dt.date
    ) -> List[ScheduleEntry]:
        """Force refresh schedule entries for range by invalidating cache."""
        if date_to < date_from:
            date_from, date_to = date_to, date_from
        self.clear_cache()
        return await self.get_schedule_range(date_from, date_to)

    async def refresh_schedule_for_date(
        self, date_value: dt.date
    ) -> List[ScheduleEntry]:
        """Force refresh schedule entries for a single day."""
        return await self.refresh_schedule_range(date_value, date_value)
