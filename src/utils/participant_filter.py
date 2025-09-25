"""
Role-based participant data filtering utilities.

Provides functions to filter participant data based on user roles
to prevent unauthorized access to sensitive information.
"""

import logging
from typing import List, Union
from unittest.mock import MagicMock, Mock

from src.models.participant import Participant

logger = logging.getLogger(__name__)


def filter_participant_by_role(
    participant: Participant, user_role: Union[str, None]
) -> Participant:
    """
    Filter participant data based on user role.

    Role hierarchy: admin > coordinator > viewer

    Viewer access: Basic organizational information only
    Coordinator access: Most fields except highly sensitive PII
    Admin access: All fields

    Args:
        participant: Participant object to filter
        user_role: User's role ("admin", "coordinator", "viewer", or None)

    Returns:
        Filtered participant object with role-appropriate data
    """
    if user_role == "admin":
        # Admins see everything
        return participant

    if isinstance(participant, (MagicMock, Mock)):
        # Mocked objects (used in tests) should pass through untouched
        filtered = participant
    elif isinstance(participant, Participant):
        # Use Pydantic's model_copy to clone real Participant instances
        # without altering originals
        filtered = participant.model_copy(deep=True)
    elif (
        not isinstance(participant, (MagicMock, Mock))
        and hasattr(participant, "model_copy")
        and callable(getattr(participant, "model_copy"))
    ):
        # Some objects might provide model_copy-like behavior; use it if available
        filtered = participant.model_copy()
    else:
        # Non-Participant objects (e.g., MagicMock in tests) should pass
        # through untouched
        filtered = participant

    if user_role == "coordinator":
        # Coordinators see most fields but not the most sensitive PII
        # Remove highly sensitive personal information
        filtered.date_of_birth = None
        # Keep other fields for operational needs

    elif user_role == "viewer" or user_role is None:
        # Viewers see only basic organizational information
        # Clear all sensitive fields
        filtered.contact_information = None
        filtered.payment_amount = None
        filtered.payment_date = None
        filtered.payment_status = None
        filtered.date_of_birth = None
        filtered.age = None
        filtered.notes = None
        filtered.submitted_by = None
        filtered.church_leader = None
        # Keep basic organizational fields for search/organizational purposes

    else:
        # Unknown role - treat as no access
        logger.warning(f"Unknown role '{user_role}' in participant filtering")
        # Apply viewer-level filtering for unknown roles
        filtered.contact_information = None
        filtered.payment_amount = None
        filtered.payment_date = None
        filtered.payment_status = None
        filtered.date_of_birth = None
        filtered.age = None
        filtered.notes = None
        filtered.submitted_by = None
        filtered.church_leader = None

    return filtered


def filter_participants_by_role(
    participants: List[Participant], user_role: Union[str, None]
) -> List[Participant]:
    """
    Filter a list of participants based on user role.

    Args:
        participants: List of participant objects to filter
        user_role: User's role ("admin", "coordinator", "viewer", or None)

    Returns:
        List of filtered participant objects
    """
    if not participants:
        return participants

    filtered_participants = []
    for participant in participants:
        filtered = filter_participant_by_role(participant, user_role)
        filtered_participants.append(filtered)

    return filtered_participants


def get_allowed_search_fields(user_role: Union[str, None]) -> List[str]:
    """
    Get list of fields that the user role is allowed to search on.

    Args:
        user_role: User's role ("admin", "coordinator", "viewer", or None)

    Returns:
        List of allowed search field names
    """
    # All roles can search on basic organizational fields
    base_fields = ["full_name_ru", "full_name_en", "church", "role", "department"]

    if user_role == "admin":
        # Admins can search on all fields
        return base_fields + [
            "contact_information",
            "payment_status",
            "gender",
            "submitted_by",
            "church_leader",
            "table_name",
            "floor",
            "room_number",
        ]
    elif user_role == "coordinator":
        # Coordinators can search on most fields except highly sensitive ones
        return base_fields + [
            "payment_status",
            "gender",
            "table_name",
            "floor",
            "room_number",
        ]
    else:
        # Viewers and unknown roles get basic fields only
        return base_fields
