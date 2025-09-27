"""
Airtable repository for reading Schedule entries.

Provides a simple API to fetch active schedule records within a date range
and convert them to domain models.
"""

from __future__ import annotations

import datetime as dt
import logging
from typing import Any, List, Mapping

from src.data.airtable.airtable_client import AirtableAPIError, AirtableClient
from src.data.repositories.participant_repository import RepositoryError
from src.models.schedule import ScheduleEntry

logger = logging.getLogger(__name__)


class AirtableScheduleRepository:
    """Repository for reading schedule records from Airtable."""

    def __init__(self, client: AirtableClient):
        self.client = client

    @staticmethod
    def _build_formula(date_from: dt.date, date_to: dt.date) -> str:
        """Build Airtable formula to filter by active flag and inclusive date range.

        Uses IS_AFTER/IS_BEFORE combined with IS_SAME to include boundary dates.
        Result: {Date} in [date_from, date_to] and {IsActive} = TRUE().
        """
        start_iso = date_from.isoformat()
        end_iso = date_to.isoformat()

        # Inclusive lower bound: {Date} >= start
        lower_inclusive = (
            "OR("
            f"IS_AFTER({{Date}}, '{start_iso}'), "
            f"IS_SAME({{Date}}, '{start_iso}', 'day')"
            ")"
        )
        # Inclusive upper bound: {Date} <= end
        upper_inclusive = (
            "OR("
            f"IS_BEFORE({{Date}}, '{end_iso}'), "
            f"IS_SAME({{Date}}, '{end_iso}', 'day')"
            ")"
        )

        return (
            "AND("  # active flag
            "{IsActive} = TRUE(),"
            f"{lower_inclusive},"
            f"{upper_inclusive}"
            ")"
        )

    @staticmethod
    def _sort_params() -> List[str]:
        """Return Airtable sort parameters by Date, Order, StartTime."""
        # Ascending for all fields; '-' prefix would indicate descending
        return ["Date", "Order", "StartTime"]

    def _convert(self, record: Mapping[str, Any]) -> ScheduleEntry:
        return ScheduleEntry.from_airtable_record(record)

    async def fetch_schedule(
        self, date_from: dt.date, date_to: dt.date
    ) -> List[ScheduleEntry]:
        """Fetch active schedule entries within the inclusive date range."""
        try:
            formula = self._build_formula(date_from, date_to)
            records = await self.client.list_records(
                formula=formula, sort=self._sort_params()
            )
            entries: List[ScheduleEntry] = []
            for rec in records:
                try:
                    entries.append(self._convert(rec))
                except Exception as e:
                    logger.warning(
                        "Skipping invalid schedule record %s: %s", rec.get("id"), e
                    )
            return entries
        except AirtableAPIError as e:
            raise RepositoryError(f"Failed to fetch schedule: {e}", e)
        except Exception as e:
            raise RepositoryError(f"Unexpected error fetching schedule: {e}", e)
