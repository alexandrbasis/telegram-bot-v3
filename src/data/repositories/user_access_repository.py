"""
Abstract repository interface for user access requests.

Defines the contract for persisting and retrieving user access requests
in the bot approval workflow system.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple

from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)


class UserAccessRepository(ABC):
    """
    Abstract repository for user access request persistence.

    Defines the interface for CRUD operations and status-based queries
    on user access requests throughout the approval workflow.
    """

    @abstractmethod
    async def create_request(self, request: UserAccessRequest) -> UserAccessRequest:
        """
        Create a new access request.

        Args:
            request: UserAccessRequest to create

        Returns:
            Created request with populated record_id

        Raises:
            Exception: If creation fails
        """
        pass

    @abstractmethod
    async def get_request_by_user_id(
        self, telegram_user_id: int
    ) -> Optional[UserAccessRequest]:
        """
        Retrieve access request by Telegram user ID.

        Args:
            telegram_user_id: Telegram user ID to lookup

        Returns:
            UserAccessRequest if found, None otherwise

        Raises:
            Exception: If lookup fails
        """
        pass

    @abstractmethod
    async def list_requests_by_status(
        self,
        status: AccessRequestStatus,
        limit: Optional[int] = None,
        offset: Optional[str] = None,
    ) -> Tuple[List[UserAccessRequest], Optional[str]]:
        """
        List access requests filtered by status.

        Args:
            status: Status to filter by
            limit: Maximum number of results to return
            offset: Offset token for pagination (string)

        Returns:
            Tuple of (requests list, next_offset_token) where next_offset_token
            is None if no more records are available

        Raises:
            Exception: If query fails
        """
        pass

    @abstractmethod
    async def approve_request(
        self, request: UserAccessRequest, access_level: AccessLevel, reviewed_by: str
    ) -> UserAccessRequest:
        """
        Approve an access request with specified access level.

        Args:
            request: Request to approve
            access_level: Access level to grant
            reviewed_by: Admin user ID performing the approval

        Returns:
            Updated request with APPROVED status

        Raises:
            Exception: If approval fails
        """
        pass

    @abstractmethod
    async def deny_request(
        self, request: UserAccessRequest, reviewed_by: str
    ) -> UserAccessRequest:
        """
        Deny an access request.

        Args:
            request: Request to deny
            reviewed_by: Admin user ID performing the denial

        Returns:
            Updated request with DENIED status

        Raises:
            Exception: If denial fails
        """
        pass

    @abstractmethod
    async def update_request(self, request: UserAccessRequest) -> UserAccessRequest:
        """
        Update an existing access request.

        Args:
            request: Request with updated fields

        Returns:
            Updated UserAccessRequest

        Raises:
            Exception: If update fails
        """
        pass
