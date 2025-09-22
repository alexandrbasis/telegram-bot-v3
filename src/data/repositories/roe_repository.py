"""
Abstract repository interface for ROE data operations.

This interface defines the contract for ROE data access, enabling
easy switching between different database implementations (Airtable, PostgreSQL, etc.)
without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.roe import ROE


class ROERepository(ABC):
    """
    Abstract base class for ROE data repositories.

    Defines the standard interface for ROE CRUD operations and queries.
    Concrete implementations must provide specific database integration.
    """

    @abstractmethod
    async def create(self, roe: ROE) -> ROE:
        """
        Create a new ROE record.

        Args:
            roe: ROE instance to create (id should be None for new records)

        Returns:
            ROE instance with assigned record_id and any server-generated fields

        Raises:
            RepositoryError: If creation fails
            ValidationError: If roe data is invalid
        """
        pass

    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[ROE]:
        """
        Retrieve a ROE by record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            ROE instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_topic(self, topic: str) -> Optional[ROE]:
        """
        Retrieve a ROE by their primary field (roe_topic).

        Args:
            topic: ROE topic string

        Returns:
            ROE instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def update(self, roe: ROE) -> ROE:
        """
        Update an existing ROE record.

        Args:
            roe: ROE instance with record_id and updated fields

        Returns:
            Updated ROE instance

        Raises:
            RepositoryError: If update fails
            ValidationError: If roe data is invalid
            NotFoundError: If record_id doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """
        Delete a ROE record.

        Args:
            record_id: Unique record identifier

        Returns:
            True if deletion was successful, False if record not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    @abstractmethod
    async def list_all(self) -> List[ROE]:
        """
        Retrieve all ROE records.

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_roista_id(self, roista_id: str) -> List[ROE]:
        """
        Retrieve all ROE records where a participant is the roista.

        Args:
            roista_id: Participant record identifier

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_assistant_id(self, assistant_id: str) -> List[ROE]:
        """
        Retrieve all ROE records where a participant is an assistant.

        Args:
            assistant_id: Participant record identifier

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass
