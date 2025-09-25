"""
Abstract repository interface for participant data operations.

This interface defines the contract for participant data access, enabling
easy switching between different database implementations (Airtable, PostgreSQL, etc.)
without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Tuple, Union

from src.models.participant import Participant


class ParticipantRepository(ABC):
    """
    Abstract base class for participant data repositories.

    Defines the standard interface for participant CRUD operations and queries.
    Concrete implementations must provide specific database integration.
    """

    @abstractmethod
    async def create(self, participant: Participant) -> Participant:
        """
        Create a new participant record.

        Args:
            participant: Participant instance to create (record_id should be None)

        Returns:
            Participant instance with assigned record_id and any server-generated fields

        Raises:
            RepositoryError: If creation fails
            ValidationError: If participant data is invalid
        """
        pass

    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[Participant]:
        """
        Retrieve a participant by their record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            Participant instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_full_name_ru(self, full_name_ru: str) -> Optional[Participant]:
        """
        Retrieve a participant by their Russian full name (primary field).

        Args:
            full_name_ru: Full name in Russian

        Returns:
            Participant instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def update(self, participant: Participant) -> Participant:
        """
        Update an existing participant record.

        Args:
            participant: Participant instance with record_id and updated fields

        Returns:
            Updated participant instance

        Raises:
            RepositoryError: If update fails
            ValidationError: If participant data is invalid
            NotFoundError: If record_id doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """
        Delete a participant record.

        Args:
            record_id: Unique record identifier

        Returns:
            True if deletion was successful, False if record not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    @abstractmethod
    async def list_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Participant]:
        """
        Retrieve all participants with optional pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of participant instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def list_view_records(self, view: str) -> List[Dict[str, Any]]:
        """
        Retrieve raw Airtable records for a specific view.

        Args:
            view: Airtable view name to pull records from

        Returns:
            List of Airtable record dictionaries returned by the view

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def search_by_criteria(self, criteria: Dict[str, Any]) -> List[Participant]:
        """
        Search participants by multiple criteria.

        Args:
            criteria: Dictionary of search criteria where keys are field names
                     and values are the search values. Supported fields:
                     - full_name_ru: partial match (case-insensitive)
                     - full_name_en: partial match (case-insensitive)
                     - church: exact match
                     - role: exact match (Role enum)
                     - department: exact match (Department enum)
                     - payment_status: exact match (PaymentStatus enum)
                     - gender: exact match (Gender enum)

        Returns:
            List of participants matching the criteria

        Raises:
            RepositoryError: If search fails
            ValueError: If criteria contains unsupported fields or values
        """
        pass

    @abstractmethod
    async def get_by_role(self, role: str) -> List[Participant]:
        """
        Retrieve all participants with a specific role.

        Args:
            role: Role value (Role enum value)

        Returns:
            List of participants with the specified role

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_department(self, department: str) -> List[Participant]:
        """
        Retrieve all participants in a specific department.

        Args:
            department: Department value (Department enum value)

        Returns:
            List of participants in the specified department

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_payment_status(self, payment_status: str) -> List[Participant]:
        """
        Retrieve all participants with a specific payment status.

        Args:
            payment_status: Payment status value (PaymentStatus enum value)

        Returns:
            List of participants with the specified payment status

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def count_total(self) -> int:
        """
        Get the total number of participant records.

        Args:
            None

        Returns:
            Total count of participant records

        Raises:
            RepositoryError: If count operation fails
        """
        pass

    @abstractmethod
    async def bulk_create(self, participants: List[Participant]) -> List[Participant]:
        """
        Create multiple participant records in a batch operation.

        Args:
            participants: List of participant instances to create

        Returns:
            List of created participants with assigned record_ids

        Raises:
            RepositoryError: If bulk creation fails
            ValidationError: If any participant data is invalid
        """
        pass

    @abstractmethod
    async def bulk_update(self, participants: List[Participant]) -> List[Participant]:
        """
        Update multiple participant records in a batch operation.

        Args:
            participants: List of participant instances with record_ids to update

        Returns:
            List of updated participant instances

        Raises:
            RepositoryError: If bulk update fails
            ValidationError: If any participant data is invalid
            NotFoundError: If any record_id doesn't exist
        """
        pass

    @abstractmethod
    async def search_by_name_fuzzy(
        self, query: str, threshold: float = 0.8, limit: int = 5
    ) -> List[Tuple[Participant, float]]:
        """
        Search participants by name with fuzzy matching.

        Uses fuzzy string matching to find participants whose names are similar
        to the query string. Searches both Russian and English names.

        Args:
            query: Name or partial name to search for
            threshold: Minimum similarity score (0.0-1.0) to include in results
            limit: Maximum number of results to return

        Returns:
            List of tuples containing (Participant, similarity_score) sorted by
            similarity score in descending order

        Raises:
            RepositoryError: If search fails
        """
        pass

    # Optional enhanced search; default raises NotImplementedError in base
    async def search_by_name_enhanced(
        self,
        query: str,
        threshold: float = 0.8,
        limit: int = 5,
        user_role: Optional[str] = None,
    ) -> List[Tuple[Participant, float, str]]:
        """
        Enhanced search with language detection, multi-field search, and rich formatting.

        Uses enhanced search capabilities including automatic language detection,
        first/last name search, and rich participant information formatting.

        Args:
            query: Name or partial name to search for
            threshold: Minimum similarity score (0.0-1.0) to include in results
            limit: Maximum number of results to return
            user_role: User's role ("admin", "coordinator", "viewer", or None) for data filtering

        Returns:
            List of tuples containing (Participant, similarity_score, formatted_result)
            where formatted_result includes name, role, department, and other info
            sorted by similarity score in descending order

        Raises:
            RepositoryError: If search fails
        """
        raise NotImplementedError

    # Optional partial update; default raises NotImplementedError in base
    async def update_by_id(self, record_id: str, field_updates: Dict[str, Any]) -> bool:
        """
        Update specific fields of a participant by record ID.

        Updates only the specified fields, leaving other fields unchanged.

        Args:
            record_id: Unique record identifier
            field_updates: Dictionary of field names and new values to update

        Returns:
            True if update was successful, False otherwise

        Raises:
            RepositoryError: If update operation fails
            NotFoundError: If record_id doesn't exist
            ValidationError: If field_updates contains invalid data
        """
        raise NotImplementedError

    # Optional accommodation query; default raises NotImplementedError in base
    async def find_by_room_number(self, room_number: str) -> List[Participant]:
        """
        Find all participants assigned to a specific room number.

        Args:
            room_number: Room number to search for (as string to handle alphanumeric)

        Returns:
            List of participants in the specified room

        Raises:
            RepositoryError: If search fails
        """
        raise NotImplementedError

    # Optional accommodation query; default raises NotImplementedError in base
    async def find_by_floor(self, floor: Union[int, str]) -> List[Participant]:
        """
        Find all participants assigned to a specific floor.

        Args:
            floor: Floor number or identifier (int or str to handle "Ground" etc.)

        Returns:
            List of participants on the specified floor

        Raises:
            RepositoryError: If search fails
        """
        raise NotImplementedError

    @abstractmethod
    async def get_available_floors(self) -> List[int]:
        """
        Return unique numeric floors that have at least one participant.

        Retrieves all floors from the database that contain participants,
        filtering out empty floors and returning them sorted in ascending order.

        Args:
            None

        Returns:
            List of unique floor numbers (as integers) that contain participants,
            sorted in ascending order. Returns empty list if no floors found
            or if an error occurs.

        Raises:
            RepositoryError: If floor discovery fails
        """
        pass

    @abstractmethod
    async def get_team_members_by_department(
        self, department: Optional[str] = None
    ) -> List[Participant]:
        """
        Retrieve team members filtered by department with chief-first sorting.

        Retrieves participants with role "TEAM", optionally filtered by department.
        Results are sorted with department chiefs first, then by church alphabetically.
        Supports filtering by specific department, all participants, or unassigned only.

        Args:
            department: Department filter. Options:
                       - None: Return all team members
                       - Department enum value (e.g., "ROE", "Chapel"): Filter by specific department
                       - "unassigned": Return only participants with no department

        Returns:
            List of team member participants matching the department filter,
            sorted with chiefs first, then by church name alphabetically.
            Chiefs (IsDepartmentChief = true) always appear at the top.

        Raises:
            RepositoryError: If retrieval fails
            ValueError: If department value is invalid
        """
        pass


class RepositoryError(Exception):
    """Base exception for repository operations."""

    def __init__(self, message: str, original_error: Optional[Exception] = None):
        super().__init__(message)
        self.original_error = original_error


class NotFoundError(RepositoryError):
    """Exception raised when a requested record is not found."""

    pass


class ValidationError(RepositoryError):
    """Exception raised when data validation fails."""

    pass


class DuplicateError(RepositoryError):
    """Exception raised when attempting to create a duplicate record."""

    pass
