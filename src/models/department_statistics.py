"""
DepartmentStatistics data model for statistics collection service.

Provides structured data container for participant and team statistics
aggregated by departments with validation and serialization capabilities.
"""

import json
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
        str_strip_whitespace=True,
        validate_assignment=True,
        extra="forbid"
    )

    total_participants: int = Field(
        ...,
        ge=0,
        description="Total number of participants across all departments"
    )

    teams_by_department: Dict[str, int] = Field(
        ...,
        description="Count of teams/participants by department name, includes 'unassigned' for participants without department"
    )

    total_teams: int = Field(
        ...,
        ge=0,
        description="Total number of teams across all departments"
    )

    collection_timestamp: datetime = Field(
        ...,
        description="Timestamp when statistics were collected"
    )

    @field_validator('teams_by_department')
    @classmethod
    def validate_teams_by_department(cls, v: Dict[str, int]) -> Dict[str, int]:
        """Validate that all department team counts are non-negative."""
        for department, count in v.items():
            if count < 0:
                raise ValueError(f"Department '{department}' cannot have negative team count: {count}")
        return v

    def to_dict(self) -> Dict:
        """
        Convert to dictionary format for serialization.

        Returns:
            Dictionary representation with ISO timestamp format
        """
        return {
            "total_participants": self.total_participants,
            "teams_by_department": self.teams_by_department,
            "total_teams": self.total_teams,
            "collection_timestamp": self.collection_timestamp.isoformat()
        }

    def to_json(self) -> str:
        """
        Convert to JSON string format.

        Returns:
            JSON string representation
        """
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: Dict) -> 'DepartmentStatistics':
        """
        Create instance from dictionary data.

        Args:
            data: Dictionary with statistics data

        Returns:
            DepartmentStatistics instance
        """
        # Parse timestamp if it's a string
        timestamp = data["collection_timestamp"]
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)

        return cls(
            total_participants=data["total_participants"],
            teams_by_department=data["teams_by_department"],
            total_teams=data["total_teams"],
            collection_timestamp=timestamp
        )

    @classmethod
    def from_json(cls, json_data: str) -> 'DepartmentStatistics':
        """
        Create instance from JSON string.

        Args:
            json_data: JSON string with statistics data

        Returns:
            DepartmentStatistics instance
        """
        data = json.loads(json_data)
        return cls.from_dict(data)

    def __str__(self) -> str:
        """String representation of statistics."""
        dept_summary = ", ".join([f"{dept}: {count}" for dept, count in self.teams_by_department.items()])
        return f"DepartmentStatistics(participants={self.total_participants}, teams={self.total_teams}, departments=[{dept_summary}])"