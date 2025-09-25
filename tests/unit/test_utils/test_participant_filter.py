"""
Tests for role-based participant data filtering utilities.

Verifies that sensitive data is properly filtered based on user roles
to prevent unauthorized access to PII and financial information.
"""

from copy import deepcopy
from datetime import date

import pytest

from src.models.participant import Department, Gender, Participant, PaymentStatus, Role
from src.utils.participant_filter import (
    filter_participant_by_role,
    filter_participants_by_role,
    get_allowed_search_fields,
)


@pytest.fixture
def sample_participant():
    """Create a sample participant with all fields populated for testing."""
    return Participant(
        full_name_ru="Иван Иванов",
        full_name_en="Ivan Ivanov",
        church="Test Church",
        country_and_city="Moscow, Russia",
        submitted_by="Admin User",
        contact_information="ivan@example.com, +7-123-456-7890",
        church_leader="Father John",
        table_name="Table 1",
        notes="Special dietary requirements",
        gender=Gender.MALE,
        role=Role.CANDIDATE,
        department=Department.ROE,
        payment_status=PaymentStatus.PAID,
        payment_amount=5000,
        payment_date=date(2025, 9, 20),
        date_of_birth=date(1990, 5, 15),
        age=35,
        floor=2,
        room_number=101,
        is_department_chief=False,
        record_id="recABC123DEF456",
    )


class TestFilterParticipantByRole:
    """Test individual participant filtering by role."""

    def test_admin_sees_all_fields(self, sample_participant):
        """Admin users should see all participant fields unchanged."""
        filtered = filter_participant_by_role(sample_participant, "admin")

        # Admin should see everything - compare all fields
        assert filtered.full_name_ru == sample_participant.full_name_ru
        assert filtered.contact_information == sample_participant.contact_information
        assert filtered.payment_amount == sample_participant.payment_amount
        assert filtered.payment_date == sample_participant.payment_date
        assert filtered.payment_status == sample_participant.payment_status
        assert filtered.date_of_birth == sample_participant.date_of_birth
        assert filtered.age == sample_participant.age
        assert filtered.notes == sample_participant.notes
        assert filtered.submitted_by == sample_participant.submitted_by
        assert filtered.church_leader == sample_participant.church_leader

    def test_coordinator_filtered_sensitive_fields(self, sample_participant):
        """Coordinator users should not see highly sensitive PII like date of birth."""
        filtered = filter_participant_by_role(sample_participant, "coordinator")

        # Coordinators see most fields but not the most sensitive PII
        assert filtered.full_name_ru == sample_participant.full_name_ru
        assert (
            filtered.contact_information == sample_participant.contact_information
        )  # Still visible
        assert (
            filtered.payment_amount == sample_participant.payment_amount
        )  # Still visible
        assert filtered.payment_date == sample_participant.payment_date  # Still visible
        assert (
            filtered.payment_status == sample_participant.payment_status
        )  # Still visible
        assert filtered.age == sample_participant.age  # Still visible
        assert filtered.notes == sample_participant.notes  # Still visible
        assert filtered.submitted_by == sample_participant.submitted_by  # Still visible
        assert (
            filtered.church_leader == sample_participant.church_leader
        )  # Still visible

        # But highly sensitive PII is filtered
        assert filtered.date_of_birth is None

    def test_viewer_only_basic_fields(self, sample_participant):
        """Viewer users should only see basic organizational information."""
        filtered = filter_participant_by_role(sample_participant, "viewer")

        # Viewers see basic organizational fields
        assert filtered.full_name_ru == sample_participant.full_name_ru
        assert filtered.full_name_en == sample_participant.full_name_en
        assert filtered.church == sample_participant.church
        assert filtered.country_and_city == sample_participant.country_and_city
        assert filtered.role == sample_participant.role
        assert filtered.department == sample_participant.department
        assert filtered.gender == sample_participant.gender
        assert filtered.size == sample_participant.size
        assert filtered.floor == sample_participant.floor
        assert filtered.room_number == sample_participant.room_number
        assert filtered.table_name == sample_participant.table_name
        assert filtered.is_department_chief == sample_participant.is_department_chief
        assert filtered.record_id == sample_participant.record_id

        # But sensitive fields are filtered out
        assert filtered.contact_information is None
        assert filtered.payment_amount is None
        assert filtered.payment_date is None
        assert filtered.payment_status is None
        assert filtered.date_of_birth is None
        assert filtered.age is None
        assert filtered.notes is None
        assert filtered.submitted_by is None
        assert filtered.church_leader is None

    def test_none_role_same_as_viewer(self, sample_participant):
        """Users with None role should be treated the same as viewers."""
        filtered_none = filter_participant_by_role(sample_participant, None)
        filtered_viewer = filter_participant_by_role(sample_participant, "viewer")

        # Both should have the same filtering applied
        assert filtered_none.contact_information == filtered_viewer.contact_information
        assert filtered_none.payment_amount == filtered_viewer.payment_amount
        assert filtered_none.payment_status == filtered_viewer.payment_status
        assert filtered_none.date_of_birth == filtered_viewer.date_of_birth
        assert filtered_none.notes == filtered_viewer.notes

    def test_unknown_role_treated_as_viewer(self, sample_participant):
        """Unknown roles should be treated with viewer-level access."""
        filtered = filter_participant_by_role(sample_participant, "unknown_role")

        # Should apply viewer-level filtering
        assert filtered.full_name_ru == sample_participant.full_name_ru
        assert filtered.contact_information is None
        assert filtered.payment_amount is None
        assert filtered.date_of_birth is None
        assert filtered.notes is None

    def test_filtering_preserves_original(self, sample_participant):
        """Filtering should not modify the original participant object."""
        original_contact = sample_participant.contact_information
        original_payment = sample_participant.payment_amount

        filter_participant_by_role(sample_participant, "viewer")

        # Original should be unchanged
        assert sample_participant.contact_information == original_contact
        assert sample_participant.payment_amount == original_payment


class TestFilterParticipantsByRole:
    """Test bulk participant filtering by role."""

    def test_empty_list_handling(self):
        """Empty participant lists should be returned unchanged."""
        result = filter_participants_by_role([], "admin")
        assert result == []

    def test_multiple_participants_filtered(self):
        """Multiple participants should all be filtered consistently."""
        participants = [
            Participant(full_name_ru="User 1", contact_information="user1@example.com"),
            Participant(full_name_ru="User 2", contact_information="user2@example.com"),
            Participant(full_name_ru="User 3", payment_amount=1000),
        ]

        filtered = filter_participants_by_role(participants, "viewer")

        # All should have sensitive fields removed
        for participant in filtered:
            assert participant.contact_information is None
            assert participant.payment_amount is None

        # But basic fields preserved
        assert filtered[0].full_name_ru == "User 1"
        assert filtered[1].full_name_ru == "User 2"
        assert filtered[2].full_name_ru == "User 3"

    def test_different_roles_different_filtering(self):
        """Different roles should result in different levels of filtering."""
        participants = [
            Participant(
                full_name_ru="Test User",
                contact_information="test@example.com",
                date_of_birth=date(1990, 1, 1),
                payment_amount=1000,
            )
        ]

        admin_filtered = filter_participants_by_role(participants, "admin")[0]
        coordinator_filtered = filter_participants_by_role(participants, "coordinator")[
            0
        ]
        viewer_filtered = filter_participants_by_role(participants, "viewer")[0]

        # Admin sees everything
        assert admin_filtered.contact_information == "test@example.com"
        assert admin_filtered.date_of_birth == date(1990, 1, 1)
        assert admin_filtered.payment_amount == 1000

        # Coordinator sees some sensitive fields but not highly sensitive PII
        assert coordinator_filtered.contact_information == "test@example.com"
        assert coordinator_filtered.date_of_birth is None  # Filtered
        assert coordinator_filtered.payment_amount == 1000

        # Viewer sees minimal information
        assert viewer_filtered.contact_information is None
        assert viewer_filtered.date_of_birth is None
        assert viewer_filtered.payment_amount is None


class TestGetAllowedSearchFields:
    """Test search field permissions by role."""

    def test_admin_all_fields(self):
        """Admin should have access to search all fields."""
        allowed = get_allowed_search_fields("admin")

        # Admin should have access to sensitive search fields
        assert "contact_information" in allowed
        assert "payment_status" in allowed
        assert "submitted_by" in allowed
        assert "church_leader" in allowed

        # Plus all basic fields
        assert "full_name_ru" in allowed
        assert "church" in allowed
        assert "role" in allowed

    def test_coordinator_limited_sensitive_fields(self):
        """Coordinator should have limited access to sensitive search fields."""
        allowed = get_allowed_search_fields("coordinator")

        # Coordinators should have some operational search capabilities
        assert "payment_status" in allowed
        assert "gender" in allowed
        assert "floor" in allowed
        assert "room_number" in allowed

        # But not highly sensitive fields
        assert "contact_information" not in allowed
        assert "submitted_by" not in allowed
        assert "church_leader" not in allowed

        # Basic fields should be available
        assert "full_name_ru" in allowed
        assert "church" in allowed
        assert "role" in allowed

    def test_viewer_basic_fields_only(self):
        """Viewer should only have access to basic organizational search fields."""
        allowed = get_allowed_search_fields("viewer")

        # Basic organizational fields
        assert "full_name_ru" in allowed
        assert "full_name_en" in allowed
        assert "church" in allowed
        assert "role" in allowed
        assert "department" in allowed

        # No sensitive fields
        assert "contact_information" not in allowed
        assert "payment_status" not in allowed
        assert "submitted_by" not in allowed
        assert "church_leader" not in allowed
        assert "floor" not in allowed
        assert "room_number" not in allowed

    def test_none_role_same_as_viewer_search(self):
        """None role should have same search permissions as viewer."""
        viewer_allowed = get_allowed_search_fields("viewer")
        none_allowed = get_allowed_search_fields(None)

        assert set(viewer_allowed) == set(none_allowed)

    def test_unknown_role_basic_fields_search(self):
        """Unknown roles should get basic search field access."""
        allowed = get_allowed_search_fields("unknown_role")

        # Should match viewer permissions
        viewer_allowed = get_allowed_search_fields("viewer")
        assert set(allowed) == set(viewer_allowed)


class TestRoleFilteringSecurityCompliance:
    """Test that role filtering meets security compliance requirements."""

    def test_no_pii_leak_to_viewer(self, sample_participant):
        """Ensure no PII fields leak to viewer role - critical security test."""
        filtered = filter_participant_by_role(sample_participant, "viewer")

        # Critical PII fields must be None for viewers
        pii_fields = [
            "contact_information",
            "date_of_birth",
            "payment_amount",
            "payment_date",
            "payment_status",
            "notes",
            "submitted_by",
        ]

        for field_name in pii_fields:
            field_value = getattr(filtered, field_name)
            assert (
                field_value is None
            ), f"PII field '{field_name}' leaked to viewer: {field_value}"

    def test_coordinator_financial_access(self, sample_participant):
        """Coordinators should have access to operational financial data."""
        filtered = filter_participant_by_role(sample_participant, "coordinator")

        # Financial fields needed for operations
        assert filtered.payment_amount == sample_participant.payment_amount
        assert filtered.payment_date == sample_participant.payment_date
        assert filtered.payment_status == sample_participant.payment_status

        # But not highly sensitive PII
        assert filtered.date_of_birth is None

    def test_admin_unrestricted_access(self, sample_participant):
        """Admins should have completely unrestricted access."""
        filtered = filter_participant_by_role(sample_participant, "admin")

        # Should be identical to original
        for field_name in Participant.model_fields:
            original_value = getattr(sample_participant, field_name)
            filtered_value = getattr(filtered, field_name)
            assert (
                original_value == filtered_value
            ), f"Admin access restricted for field: {field_name}"
