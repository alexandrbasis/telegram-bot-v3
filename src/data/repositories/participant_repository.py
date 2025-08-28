"""
Abstract repository interface for participant data operations.

This interface defines the contract for participant data access, enabling
easy switching between different database implementations (Airtable, PostgreSQL, etc.)
without changing business logic.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
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
    async def list_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> List[Participant]:
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