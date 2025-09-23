"""
User Access Request model for bot approval workflow.

This module defines the data model for tracking user access requests
through the approval process from submission to decision.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class AccessLevel(str, Enum):
    """User access levels for bot permissions."""

    VIEWER = "VIEWER"
    COORDINATOR = "COORDINATOR"
    ADMIN = "ADMIN"


class AccessRequestStatus(str, Enum):
    """Status of user access requests."""

    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"


class UserAccessRequest(BaseModel):
    """
    Model for user access requests in the bot approval workflow.

    Tracks requests from submission through admin review to final decision,
    including audit metadata for approval/denial actions.
    """

    record_id: Optional[str] = Field(None, description="Airtable record ID")
    telegram_user_id: int = Field(..., description="Telegram user ID (primary key)")
    telegram_username: Optional[str] = Field(
        None, description="Telegram username without @ prefix"
    )
    status: AccessRequestStatus = Field(
        default=AccessRequestStatus.PENDING, description="Current request status"
    )
    access_level: AccessLevel = Field(
        default=AccessLevel.VIEWER, description="Effective permissions after approval"
    )
    requested_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Timestamp when request was submitted",
    )
    reviewed_at: Optional[datetime] = Field(
        None, description="Timestamp when request was reviewed"
    )
    reviewed_by: Optional[str] = Field(
        None, description="Admin user who reviewed the request"
    )

    model_config = ConfigDict(
        use_enum_values=True,
    )
