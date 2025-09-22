"""
Abstract repository interface for BibleReaders data operations.

This interface defines the contract for BibleReaders data access, enabling
easy switching between different database implementations (Airtable, PostgreSQL, etc.)
without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Optional

from src.models.bible_readers import BibleReader


class BibleReadersRepository(ABC):
    """
    Abstract base class for BibleReaders data repositories.

    Defines the standard interface for BibleReaders CRUD operations and queries.
    Concrete implementations must provide specific database integration.
    """

    @abstractmethod
    async def create(self, bible_reader: BibleReader) -> BibleReader:
        """
        Create a new BibleReader record.

        Args:
            bible_reader: BibleReader instance to create (id should be None for
                new records)

        Returns:
            BibleReader instance with assigned record_id and any
            server-generated fields

        Raises:
            RepositoryError: If creation fails
            ValidationError: If bible_reader data is invalid
        """
        pass

    @abstractmethod
    async def get_by_id(self, record_id: str) -> Optional[BibleReader]:
        """
        Retrieve a BibleReader by their record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            BibleReader instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_where(self, where: str) -> Optional[BibleReader]:
        """
        Retrieve a BibleReader by their primary field (where).

        Args:
            where: Location/session description

        Returns:
            BibleReader instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def update(self, bible_reader: BibleReader) -> BibleReader:
        """
        Update an existing BibleReader record.

        Args:
            bible_reader: BibleReader instance with record_id and updated fields

        Returns:
            Updated BibleReader instance

        Raises:
            RepositoryError: If update fails
            ValidationError: If bible_reader data is invalid
            NotFoundError: If record_id doesn't exist
        """
        pass

    @abstractmethod
    async def delete(self, record_id: str) -> bool:
        """
        Delete a BibleReader record.

        Args:
            record_id: Unique record identifier

        Returns:
            True if deletion was successful, False if record not found

        Raises:
            RepositoryError: If deletion fails
        """
        pass

    @abstractmethod
    async def list_all(self) -> List[BibleReader]:
        """
        Retrieve all BibleReader records.

        Returns:
            List of BibleReader instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass

    @abstractmethod
    async def get_by_participant_id(self, participant_id: str) -> List[BibleReader]:
        """
        Retrieve all BibleReader records where a participant is involved.

        Args:
            participant_id: Participant record identifier

        Returns:
            List of BibleReader instances

        Raises:
            RepositoryError: If retrieval fails
        """
        pass
