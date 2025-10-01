"""
Unit tests for DepartmentStatistics model.

Tests data validation, serialization, and field constraints.
"""

from datetime import datetime
from typing import Dict

import pytest

from src.models.department_statistics import DepartmentStatistics


class TestDepartmentStatistics:
    """Test cases for DepartmentStatistics data model."""

    def test_create_valid_statistics(self):
        """Test creation of valid DepartmentStatistics instance."""
        # Arrange
        teams_by_dept = {"ROE": 5, "Chapel": 3, "Kitchen": 2}
        timestamp = datetime.now()

        # Act
        stats = DepartmentStatistics(
            total_participants=20,
            participants_by_department=teams_by_dept,
            total_teams=10,
            total_candidates=10,
            collection_timestamp=timestamp,
        )

        # Assert
        assert stats.total_participants == 20
        assert stats.participants_by_department == teams_by_dept
        assert stats.total_teams == 10
        assert stats.total_candidates == 10
        assert stats.collection_timestamp == timestamp

    def test_create_statistics_with_empty_departments(self):
        """Test creation with empty departments dictionary."""
        # Arrange & Act
        stats = DepartmentStatistics(
            total_participants=0,
            participants_by_department={},
            total_teams=0,
            total_candidates=0,
            collection_timestamp=datetime.now(),
        )

        # Assert
        assert stats.total_participants == 0
        assert stats.participants_by_department == {}
        assert stats.total_teams == 0
        assert stats.total_candidates == 0

    def test_create_statistics_with_unassigned_department(self):
        """Test creation with unassigned department category."""
        # Arrange
        teams_by_dept = {"ROE": 3, "unassigned": 2}

        # Act
        stats = DepartmentStatistics(
            total_participants=10,
            participants_by_department=teams_by_dept,
            total_teams=5,
            total_candidates=5,
            collection_timestamp=datetime.now(),
        )

        # Assert
        assert "unassigned" in stats.participants_by_department
        assert stats.participants_by_department["unassigned"] == 2

    def test_negative_participants_validation(self):
        """Test validation fails for negative participant count."""
        # Act & Assert
        with pytest.raises(ValueError):
            DepartmentStatistics(
                total_participants=-1,
                participants_by_department={},
                total_teams=0,
                total_candidates=0,
                collection_timestamp=datetime.now(),
            )

    def test_negative_teams_validation(self):
        """Test validation fails for negative team count."""
        # Act & Assert
        with pytest.raises(ValueError):
            DepartmentStatistics(
                total_participants=5,
                participants_by_department={},
                total_teams=-1,
                total_candidates=0,
                collection_timestamp=datetime.now(),
            )

    def test_negative_department_teams_validation(self):
        """Test validation fails for negative department team counts."""
        # Act & Assert
        with pytest.raises(ValueError):
            DepartmentStatistics(
                total_participants=5,
                participants_by_department={"ROE": -1},
                total_teams=2,
                total_candidates=3,
                collection_timestamp=datetime.now(),
            )

    def test_serialization_to_dict(self):
        """Test serialization to dictionary format using Pydantic's model_dump."""
        # Arrange
        timestamp = datetime(2025, 9, 28, 15, 30, 0)
        stats = DepartmentStatistics(
            total_participants=15,
            participants_by_department={"ROE": 5, "Chapel": 2},
            total_teams=7,
            total_candidates=8,
            collection_timestamp=timestamp,
        )

        # Act
        result = stats.model_dump()

        # Assert
        assert isinstance(result, dict)
        assert result["total_participants"] == 15
        assert result["participants_by_department"] == {"ROE": 5, "Chapel": 2}
        assert result["total_teams"] == 7
        assert result["total_candidates"] == 8
        assert result["collection_timestamp"] == timestamp

    def test_serialization_to_json(self):
        """Test JSON serialization using Pydantic's model_dump_json."""
        # Arrange
        stats = DepartmentStatistics(
            total_participants=10,
            participants_by_department={"ROE": 3},
            total_teams=3,
            total_candidates=7,
            collection_timestamp=datetime.now(),
        )

        # Act
        json_str = stats.model_dump_json()

        # Assert
        assert isinstance(json_str, str)
        assert "total_participants" in json_str
        assert "participants_by_department" in json_str
        assert "total_candidates" in json_str
        assert "10" in json_str

    def test_create_from_dict(self):
        """Test creation from dictionary using Pydantic's validation."""
        # Arrange
        data = {
            "total_participants": 25,
            "participants_by_department": {"ROE": 8, "Kitchen": 3},
            "total_teams": 11,
            "total_candidates": 14,
            "collection_timestamp": "2025-09-28T15:30:00",
        }

        # Act
        stats = DepartmentStatistics(**data)

        # Assert
        assert stats.total_participants == 25
        assert stats.participants_by_department == {"ROE": 8, "Kitchen": 3}
        assert stats.total_teams == 11
        assert stats.total_candidates == 14
        assert stats.collection_timestamp == datetime(2025, 9, 28, 15, 30, 0)

    def test_create_from_json(self):
        """Test creation from JSON string using Pydantic's model_validate_json."""
        # Arrange
        json_data = '{"total_participants": 12, "participants_by_department": {"Chapel": 4}, "total_teams": 4, "total_candidates": 8, "collection_timestamp": "2025-09-28T10:00:00"}'

        # Act
        stats = DepartmentStatistics.model_validate_json(json_data)

        # Assert
        assert stats.total_participants == 12
        assert stats.participants_by_department == {"Chapel": 4}
        assert stats.total_teams == 4
        assert stats.total_candidates == 8

    def test_equality_comparison(self):
        """Test equality comparison between instances."""
        # Arrange
        timestamp = datetime.now()
        stats1 = DepartmentStatistics(
            total_participants=10,
            participants_by_department={"ROE": 5},
            total_teams=5,
            total_candidates=5,
            collection_timestamp=timestamp,
        )
        stats2 = DepartmentStatistics(
            total_participants=10,
            participants_by_department={"ROE": 5},
            total_teams=5,
            total_candidates=5,
            collection_timestamp=timestamp,
        )

        # Act & Assert
        assert stats1 == stats2

    def test_inequality_comparison(self):
        """Test inequality comparison between instances."""
        # Arrange
        timestamp = datetime.now()
        stats1 = DepartmentStatistics(
            total_participants=10,
            participants_by_department={"ROE": 5},
            total_teams=5,
            total_candidates=5,
            collection_timestamp=timestamp,
        )
        stats2 = DepartmentStatistics(
            total_participants=15,
            participants_by_department={"ROE": 5},
            total_teams=5,
            total_candidates=10,
            collection_timestamp=timestamp,
        )

        # Act & Assert
        assert stats1 != stats2

    def test_string_representation(self):
        """Test string representation is informative."""
        # Arrange
        stats = DepartmentStatistics(
            total_participants=20,
            participants_by_department={"ROE": 8, "Chapel": 4},
            total_teams=12,
            total_candidates=8,
            collection_timestamp=datetime.now(),
        )

        # Act
        result = str(stats)

        # Assert
        assert "20" in result
        assert "12" in result
        assert "8" in result
        assert "ROE" in result or "Chapel" in result

    def test_total_candidates_field_exists(self):
        """Test that total_candidates field is present and accessible."""
        # Arrange & Act
        stats = DepartmentStatistics(
            total_participants=50,
            participants_by_department={"ROE": 20},
            total_teams=30,
            total_candidates=20,
            collection_timestamp=datetime.now(),
        )

        # Assert
        assert hasattr(stats, "total_candidates")
        assert stats.total_candidates == 20

    def test_negative_candidates_validation(self):
        """Test validation fails for negative candidate count."""
        # Act & Assert
        with pytest.raises(ValueError):
            DepartmentStatistics(
                total_participants=10,
                participants_by_department={},
                total_teams=5,
                total_candidates=-1,
                collection_timestamp=datetime.now(),
            )

    def test_mathematical_correctness_candidates_plus_teams(self):
        """Test that total_participants equals total_candidates + total_teams."""
        # Arrange
        candidates = 25
        teams = 75
        total = candidates + teams

        # Act
        stats = DepartmentStatistics(
            total_participants=total,
            participants_by_department={"ROE": 50, "Chapel": 50},
            total_teams=teams,
            total_candidates=candidates,
            collection_timestamp=datetime.now(),
        )

        # Assert
        assert stats.total_candidates + stats.total_teams == stats.total_participants
