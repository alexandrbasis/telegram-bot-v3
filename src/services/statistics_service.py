"""
Statistics collection service for participant and team data aggregation.

Provides efficient statistics collection from Airtable with performance optimization,
rate limiting compliance, and in-memory aggregation for daily reporting.
"""

import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict

from src.data.repositories.participant_repository import ParticipantRepository
from src.models.department_statistics import DepartmentStatistics
from src.models.participant import Role

logger = logging.getLogger(__name__)


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

        Efficiently retrieves all participants from Airtable and aggregates
        statistics in memory to minimize API calls. Counts participants
        and teams by department, including unassigned participants.

        Returns:
            DepartmentStatistics: Aggregated statistics with totals and
            department breakdowns, including collection timestamp

        Raises:
            RepositoryError: If data retrieval from repository fails
        """
        logger.info("Starting statistics collection")
        collection_start = datetime.now()

        try:
            # Fetch all participants in a single batched query to minimize API calls
            all_participants = await self.repository.list_all()
            logger.debug(
                f"Retrieved {len(all_participants)} participants from repository"
            )

            # Initialize aggregation counters
            total_participants = len(all_participants)
            total_teams = 0
            teams_by_department: Dict[str, int] = defaultdict(int)

            # Aggregate statistics in memory for optimal performance
            for participant in all_participants:
                # Count all participants regardless of role
                # Count teams (participants with TEAM role)
                if participant.role == Role.TEAM:
                    total_teams += 1

                # Aggregate by department (count all participants, not just teams)
                if participant.department:
                    # Handle both Department enum and string values
                    department_name = (
                        participant.department.value
                        if hasattr(participant.department, "value")
                        else str(participant.department)
                    )
                    teams_by_department[department_name] += 1
                else:
                    # Track participants without department assignment
                    teams_by_department["unassigned"] += 1

            # Convert defaultdict to regular dict for consistent serialization
            teams_by_dept_dict = dict(teams_by_department)

            collection_timestamp = datetime.now()
            collection_duration = (
                collection_timestamp - collection_start
            ).total_seconds()

            # Create structured statistics result
            statistics = DepartmentStatistics(
                total_participants=total_participants,
                teams_by_department=teams_by_dept_dict,
                total_teams=total_teams,
                collection_timestamp=collection_timestamp,
            )

            logger.info(
                f"Statistics collection completed in {collection_duration:.2f}s: "
                f"{total_participants} participants, {total_teams} teams, "
                f"{len(teams_by_dept_dict)} departments"
            )

            return statistics

        except Exception as e:
            logger.error(f"Failed to collect statistics: {e}")
            raise
