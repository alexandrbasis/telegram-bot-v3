"""
Access Request Service - Business logic for user access management.

Handles the workflow for user access requests including submission,
approval, denial, and admin management operations.
"""

from datetime import datetime, timezone
from typing import List, Optional

from src.data.repositories.user_access_repository import UserAccessRepository
from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)


class AccessRequestService:
    """
    Service for managing user access requests.

    Provides business logic layer for access request workflow,
    including request submission, admin approval/denial, and status management.
    """

    def __init__(self, repository: UserAccessRepository):
        """
        Initialize service with repository dependency.

        Args:
            repository: UserAccessRepository implementation for data persistence
        """
        self.repository = repository

    async def submit_request(
        self, telegram_user_id: int, telegram_username: Optional[str] = None
    ) -> UserAccessRequest:
        """
        Submit a new access request or return existing one.

        Args:
            telegram_user_id: Telegram user ID
            telegram_username: Optional Telegram username

        Returns:
            UserAccessRequest (new or existing)

        Raises:
            Exception: If repository operation fails
        """
        # Check for existing request
        existing_request = await self.repository.get_request_by_user_id(
            telegram_user_id
        )
        if existing_request:
            return existing_request

        # Create new request
        new_request = UserAccessRequest(
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            status=AccessRequestStatus.PENDING,
            access_level=AccessLevel.VIEWER,
            requested_at=datetime.now(timezone.utc),
        )

        return await self.repository.create_request(new_request)

    async def get_request_by_user_id(
        self, telegram_user_id: int
    ) -> Optional[UserAccessRequest]:
        """
        Retrieve access request by user ID.

        Args:
            telegram_user_id: Telegram user ID to lookup

        Returns:
            UserAccessRequest if found, None otherwise

        Raises:
            Exception: If repository operation fails
        """
        return await self.repository.get_request_by_user_id(telegram_user_id)

    async def get_pending_requests(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[UserAccessRequest]:
        """
        Retrieve pending access requests with pagination.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of pending UserAccessRequest objects

        Raises:
            Exception: If repository operation fails
        """
        return await self.repository.list_requests_by_status(
            AccessRequestStatus.PENDING, limit=limit, offset=offset
        )

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
            Exception: If repository operation fails
        """
        return await self.repository.approve_request(request, access_level, reviewed_by)

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
            Exception: If repository operation fails
        """
        return await self.repository.deny_request(request, reviewed_by)

    def format_display_name(self, request: UserAccessRequest) -> str:
        """
        Format display name for admin notifications.

        Args:
            request: UserAccessRequest to format

        Returns:
            Formatted display name
        """
        return request.telegram_username or f"User {request.telegram_user_id}"

    def validate_admin_permissions(self, user_id: str) -> bool:
        """
        Validate if user has admin permissions.

        Args:
            user_id: User ID to validate

        Returns:
            True if user has admin permissions

        Note:
            This is a simplified implementation. In production,
            this would check against configured admin lists or roles.
        """
        # Simple validation based on username pattern
        # In production, this would check against actual admin configuration
        return user_id.startswith(("admin_", "coordinator_"))

    async def get_approved_requests(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[UserAccessRequest]:
        """
        Retrieve approved access requests.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of approved UserAccessRequest objects

        Raises:
            Exception: If repository operation fails
        """
        return await self.repository.list_requests_by_status(
            AccessRequestStatus.APPROVED, limit=limit, offset=offset
        )

    async def get_denied_requests(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[UserAccessRequest]:
        """
        Retrieve denied access requests.

        Args:
            limit: Maximum number of results to return
            offset: Number of results to skip

        Returns:
            List of denied UserAccessRequest objects

        Raises:
            Exception: If repository operation fails
        """
        return await self.repository.list_requests_by_status(
            AccessRequestStatus.DENIED, limit=limit, offset=offset
        )

    def check_user_access(self, request: Optional[UserAccessRequest]) -> bool:
        """
        Check if user has approved access.

        Args:
            request: User's access request (can be None)

        Returns:
            True if user has approved access
        """
        return request is not None and request.status == AccessRequestStatus.APPROVED

    def get_access_level(
        self, request: Optional[UserAccessRequest]
    ) -> Optional[AccessLevel]:
        """
        Get user's access level if approved.

        Args:
            request: User's access request (can be None)

        Returns:
            AccessLevel if user is approved, None otherwise
        """
        if self.check_user_access(request) and request is not None:
            return request.access_level
        return None
