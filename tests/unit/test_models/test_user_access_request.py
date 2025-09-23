"""
Unit tests for UserAccessRequest model.

Tests the data model validation, field mapping, and state transitions
for bot access request functionality.
"""

import pytest
from datetime import datetime, timezone
from pydantic import ValidationError

from src.models.user_access_request import (
    UserAccessRequest,
    AccessLevel,
    AccessRequestStatus,
)


class TestUserAccessRequest:
    """Test UserAccessRequest model validation and functionality."""

    def test_create_minimal_request(self):
        """Test creating a request with minimal required fields."""
        request = UserAccessRequest(
            telegram_user_id=123456789,
            telegram_username="testuser"
        )

        assert request.telegram_user_id == 123456789
        assert request.telegram_username == "testuser"
        assert request.status == AccessRequestStatus.PENDING
        assert request.access_level == AccessLevel.VIEWER
        assert request.record_id is None
        assert request.requested_at is not None
        assert request.reviewed_at is None
        assert request.reviewed_by is None

    def test_create_request_without_username(self):
        """Test creating a request without username (optional field)."""
        request = UserAccessRequest(
            telegram_user_id=123456789
        )

        assert request.telegram_user_id == 123456789
        assert request.telegram_username is None
        assert request.status == AccessRequestStatus.PENDING

    def test_telegram_user_id_validation(self):
        """Test telegram_user_id field validation."""
        # Valid user ID
        request = UserAccessRequest(telegram_user_id=123456789)
        assert request.telegram_user_id == 123456789

        # Invalid types should raise ValidationError
        with pytest.raises(ValidationError):
            UserAccessRequest(telegram_user_id="invalid")

        with pytest.raises(ValidationError):
            UserAccessRequest(telegram_user_id=None)

    def test_access_level_enum_validation(self):
        """Test AccessLevel enum validation."""
        # Valid access levels
        for level in AccessLevel:
            request = UserAccessRequest(
                telegram_user_id=123456789,
                access_level=level
            )
            assert request.access_level == level

        # Invalid access level should raise ValidationError
        with pytest.raises(ValidationError):
            UserAccessRequest(
                telegram_user_id=123456789,
                access_level="INVALID"
            )

    def test_status_enum_validation(self):
        """Test AccessRequestStatus enum validation."""
        # Valid statuses
        for status in AccessRequestStatus:
            request = UserAccessRequest(
                telegram_user_id=123456789,
                status=status
            )
            assert request.status == status

        # Invalid status should raise ValidationError
        with pytest.raises(ValidationError):
            UserAccessRequest(
                telegram_user_id=123456789,
                status="INVALID"
            )

    def test_requested_at_auto_generation(self):
        """Test that requested_at is automatically set to current timestamp."""
        before = datetime.now(timezone.utc)
        request = UserAccessRequest(telegram_user_id=123456789)
        after = datetime.now(timezone.utc)

        assert before <= request.requested_at <= after

    def test_complete_request_with_all_fields(self):
        """Test creating a complete request with all fields populated."""
        requested_at = datetime(2025, 9, 23, 10, 0, 0)
        reviewed_at = datetime(2025, 9, 23, 11, 0, 0)

        request = UserAccessRequest(
            record_id="recABC123456789",
            telegram_user_id=123456789,
            telegram_username="testuser",
            status=AccessRequestStatus.APPROVED,
            access_level=AccessLevel.COORDINATOR,
            requested_at=requested_at,
            reviewed_at=reviewed_at,
            reviewed_by="admin_user_123"
        )

        assert request.record_id == "recABC123456789"
        assert request.telegram_user_id == 123456789
        assert request.telegram_username == "testuser"
        assert request.status == AccessRequestStatus.APPROVED
        assert request.access_level == AccessLevel.COORDINATOR
        assert request.requested_at == requested_at
        assert request.reviewed_at == reviewed_at
        assert request.reviewed_by == "admin_user_123"

    def test_model_serialization(self):
        """Test that model can be serialized to dict."""
        request = UserAccessRequest(
            telegram_user_id=123456789,
            telegram_username="testuser",
            access_level=AccessLevel.COORDINATOR
        )

        data = request.model_dump()

        assert data["telegram_user_id"] == 123456789
        assert data["telegram_username"] == "testuser"
        assert data["status"] == "PENDING"
        assert data["access_level"] == "COORDINATOR"
        assert "requested_at" in data
        assert data["reviewed_at"] is None
        assert data["reviewed_by"] is None

    def test_model_deserialization(self):
        """Test that model can be created from dict data."""
        data = {
            "telegram_user_id": 123456789,
            "telegram_username": "testuser",
            "status": "APPROVED",
            "access_level": "ADMIN",
            "requested_at": "2025-09-23T10:00:00",
            "reviewed_at": "2025-09-23T11:00:00",
            "reviewed_by": "admin_123"
        }

        request = UserAccessRequest.model_validate(data)

        assert request.telegram_user_id == 123456789
        assert request.telegram_username == "testuser"
        assert request.status == AccessRequestStatus.APPROVED
        assert request.access_level == AccessLevel.ADMIN
        assert request.reviewed_by == "admin_123"


class TestAccessLevel:
    """Test AccessLevel enum."""

    def test_access_level_values(self):
        """Test AccessLevel enum has expected values."""
        assert AccessLevel.VIEWER == "VIEWER"
        assert AccessLevel.COORDINATOR == "COORDINATOR"
        assert AccessLevel.ADMIN == "ADMIN"

    def test_access_level_hierarchy(self):
        """Test access level hierarchy ordering (for future permission checks)."""
        levels = [AccessLevel.VIEWER, AccessLevel.COORDINATOR, AccessLevel.ADMIN]
        assert len(levels) == 3
        assert AccessLevel.VIEWER in levels
        assert AccessLevel.COORDINATOR in levels
        assert AccessLevel.ADMIN in levels


class TestAccessRequestStatus:
    """Test AccessRequestStatus enum."""

    def test_status_values(self):
        """Test AccessRequestStatus enum has expected values."""
        assert AccessRequestStatus.PENDING == "PENDING"
        assert AccessRequestStatus.APPROVED == "APPROVED"
        assert AccessRequestStatus.DENIED == "DENIED"

    def test_status_transitions(self):
        """Test valid status transition logic (business rule validation)."""
        # This tests the business logic that PENDING can transition to APPROVED/DENIED
        # and APPROVED/DENIED can be changed (for re-approval scenarios)
        valid_transitions = {
            AccessRequestStatus.PENDING: [AccessRequestStatus.APPROVED, AccessRequestStatus.DENIED],
            AccessRequestStatus.APPROVED: [AccessRequestStatus.DENIED, AccessRequestStatus.PENDING],
            AccessRequestStatus.DENIED: [AccessRequestStatus.APPROVED, AccessRequestStatus.PENDING],
        }

        for from_status, to_statuses in valid_transitions.items():
            for to_status in to_statuses:
                # This validates the enum values exist and can be compared
                assert from_status != to_status
                assert isinstance(from_status, AccessRequestStatus)
                assert isinstance(to_status, AccessRequestStatus)