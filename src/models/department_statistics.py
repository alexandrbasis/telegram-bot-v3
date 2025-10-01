"""
DepartmentStatistics data model for statistics collection service.

Provides structured data container for participant and team statistics
aggregated by departments with validation and serialization capabilities.
"""

from datetime import datetime
from typing import Dict

from pydantic import BaseModel, ConfigDict, Field, field_validator


class DepartmentStatistics(BaseModel):
    """
    Data model for department statistics collection results.

    Contains aggregated statistics about participants and teams by department,
    with validation and serialization methods for data exchange.
    """

    model_config = ConfigDict(
        str_strip_whitespace=True, validate_assignment=True, extra="forbid"
    )

    total_participants: int = Field(
        ..., ge=0, description="Total number of participants across all departments"
    )

    participants_by_department: Dict[str, int] = Field(
        ...,
        description=(
            "Count of all participants by department name, "
            "includes 'unassigned' for participants without department"
        ),
    )

    total_teams: int = Field(
        ..., ge=0, description="Total number of teams across all departments"
    )

    total_candidates: int = Field(
        ..., ge=0, description="Total number of candidates across all departments"
    )

    collection_timestamp: datetime = Field(
        ..., description="Timestamp when statistics were collected"
    )

    @field_validator("participants_by_department")
    @classmethod
    def validate_participants_by_department(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate that all department participant counts are non-negative."""
        for department, count in v.items():
            if count < 0:
                raise ValueError(
                    f"Department '{department}' cannot have negative "
                    f"participant count: {count}"
                )
        return v

    def __str__(self) -> str:
        """String representation of statistics."""
        dept_summary = ", ".join(
            [
                f"{dept}: {count}"
                for dept, count in self.participants_by_department.items()
            ]
        )
        return (
            f"DepartmentStatistics(participants={self.total_participants}, "
            f"candidates={self.total_candidates}, "
            f"teams={self.total_teams}, departments=[{dept_summary}])"
        )
