"""
Statistics collection service for participant and team data aggregation.

Provides efficient statistics collection from Airtable with performance optimization,
rate limiting compliance, and in-memory aggregation for daily reporting.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict

from src.data.repositories.participant_repository import (
    ParticipantRepository,
    RepositoryError,
)
from src.models.department_statistics import DepartmentStatistics
from src.models.participant import Department, Role

logger = logging.getLogger(__name__)


class StatisticsError(Exception):
    """Custom exception for statistics collection errors."""

    pass


class StatisticsService:
    """
    Service for collecting and aggregating participant statistics by department.

    Efficiently queries participant data from Airtable repository and aggregates
    statistics in memory to minimize API calls and provide structured results.
    """

    def __init__(self, repository: ParticipantRepository):
        """
        Initialize statistics service with participant repository.

        Args:
            repository: Participant repository for data access
        """
        self.repository = repository
        logger.info("Initialized StatisticsService")

    async def collect_statistics(self) -> DepartmentStatistics:
        """
        Collect comprehensive participant and team statistics by department.

        Uses paginated queries to efficiently retrieve participant data and
        aggregates statistics in memory to minimize API calls and control
        memory usage. Counts participants and teams by department.

        Returns:
            DepartmentStatistics: Aggregated statistics with totals and
            department breakdowns, including collection timestamp

        Raises:
            StatisticsError: If data collection or aggregation fails
        """
        logger.info("Starting statistics collection")
        collection_start = datetime.now()

        try:
            # Fetch all participants in single request
            # Airtable doesn't support offset pagination
            # Repository will use max_records internally to prevent unlimited fetches
            logger.debug("Fetching all participants from repository")
            all_participants = await self.repository.list_all()
            participants_processed = len(all_participants)

            logger.debug(
                f"Retrieved {len(all_participants)} participants from repository"
            )

            # Initialize aggregation counters
            total_participants = len(all_participants)
            total_teams = 0
            participants_by_department: Dict[str, int] = defaultdict(int)

            # Aggregate statistics in memory for optimal performance
            for participant in all_participants:
                # Count teams (participants with TEAM role)
                if participant.role == Role.TEAM:
                    total_teams += 1

                # Aggregate by department (count all participants)
                if participant.department:
                    # Handle both Department enum and string values with proper checking
                    if isinstance(participant.department, Department):
                        department_name = participant.department.value
                    elif isinstance(participant.department, str):
                        logger.warning(
                            f"Received string department for participant "
                            f"{participant.record_id}"
                        )
                        department_name = participant.department
                    else:
                        raise ValueError(
                            f"Unexpected department type: "
                            f"{type(participant.department)}"
                        )
                    participants_by_department[department_name] += 1
                else:
                    # Track participants without department assignment
                    participants_by_department["unassigned"] += 1

            # Convert defaultdict to regular dict for consistent serialization
            participants_by_dept_dict = dict(participants_by_department)

            collection_timestamp = datetime.now()
            collection_duration = (
                collection_timestamp - collection_start
            ).total_seconds()

            # Create structured statistics result
            statistics = DepartmentStatistics(
                total_participants=total_participants,
                participants_by_department=participants_by_dept_dict,
                total_teams=total_teams,
                collection_timestamp=collection_timestamp,
            )

            logger.info(
                f"Statistics collection completed in {collection_duration:.2f}s: "
                f"{total_participants} participants, {total_teams} teams, "
                f"{len(participants_by_dept_dict)} departments"
            )

            return statistics

        except RepositoryError as e:
            logger.error(
                f"Repository error during statistics collection: "
                f"{type(e).__name__}"
            )
            logger.debug(f"Full error details: {e}")  # Only log details at debug level
            raise StatisticsError(
                "Unable to collect statistics at this time"
            ) from e
        except Exception as e:
            # Use try/except to safely access participants_processed variable
            try:
                processed_count = participants_processed
            except NameError:
                processed_count = 0

            logger.error(
                f"Unexpected error during statistics collection after processing "
                f"{processed_count} participants"
            )
            raise StatisticsError("Statistics collection failed") from e
