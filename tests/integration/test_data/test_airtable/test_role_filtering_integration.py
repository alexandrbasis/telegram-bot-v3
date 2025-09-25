"""
Integration tests for role-based filtering in Airtable repository search methods.

These tests verify that the critical security issue has been fixed - search methods
now properly filter sensitive data based on user roles, preventing unauthorized
access to coordinator/admin-only information.
"""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest

from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.models.participant import Gender, Participant, PaymentStatus, Role


@pytest.fixture
def mock_airtable_client():
    """Create a mock AirtableClient for testing."""
    client = AsyncMock()
    client.config.base_id = "test_base"
    client.config.table_id = "test_table"
    return client


@pytest.fixture
def participant_repo(mock_airtable_client):
    """Create AirtableParticipantRepository with mocked client."""
    return AirtableParticipantRepository(mock_airtable_client)


@pytest.fixture
def sample_airtable_records():
    """Sample Airtable records with sensitive data for testing."""
    return [
        {
            "id": "rec123",
            "fields": {
                "FullNameRU": "Иван Иванов",
                "FullNameEN": "Ivan Ivanov",
                "Church": "Test Church",
                "ContactInformation": "ivan@secret.com, +7-123-456-7890",
                "PaymentAmount": 5000,
                "PaymentDate": "2025-09-20",
                "PaymentStatus": "Paid",
                "DateOfBirth": "1990-05-15",
                "Age": 35,
                "Notes": "Confidential medical notes",
                "SubmittedBy": "Admin User",
                "ChurchLeader": "Father Confidential",
                "Gender": "M",
                "Role": "CANDIDATE",
            },
        },
        {
            "id": "rec456",
            "fields": {
                "FullNameRU": "Мария Петрова",
                "ContactInformation": "maria@private.org",
                "PaymentAmount": 3000,
                "PaymentStatus": "Partial",
                "Notes": "Special dietary requirements - confidential",
                "Gender": "F",
                "Role": "TEAM",
            },
        },
    ]


class TestSearchByNameRoleFiltering:
    """Test role filtering in search_by_name method."""

    @pytest.mark.asyncio
    async def test_admin_sees_all_sensitive_data(
        self, participant_repo, sample_airtable_records
    ):
        """Admin users should see all sensitive data in search results."""
        # Mock the Airtable search response
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("Иван", user_role="admin")

        assert len(results) == 2
        admin_participant = results[0]

        # Admin should see all sensitive fields
        assert (
            admin_participant.contact_information == "ivan@secret.com, +7-123-456-7890"
        )
        assert admin_participant.payment_amount == 5000
        assert admin_participant.payment_status == PaymentStatus.PAID
        assert admin_participant.notes == "Confidential medical notes"
        assert admin_participant.submitted_by == "Admin User"
        assert admin_participant.church_leader == "Father Confidential"
        assert admin_participant.date_of_birth == date(1990, 5, 15)

    @pytest.mark.asyncio
    async def test_coordinator_filtered_sensitive_data(
        self, participant_repo, sample_airtable_records
    ):
        """Coordinator users should see most data but not highly sensitive PII."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("Иван", user_role="coordinator")

        assert len(results) == 2
        coord_participant = results[0]

        # Coordinator should see operational data
        assert (
            coord_participant.contact_information == "ivan@secret.com, +7-123-456-7890"
        )
        assert coord_participant.payment_amount == 5000
        assert coord_participant.payment_status == PaymentStatus.PAID
        assert coord_participant.notes == "Confidential medical notes"
        assert coord_participant.submitted_by == "Admin User"
        assert coord_participant.church_leader == "Father Confidential"
        assert coord_participant.age == 35

        # But not highly sensitive PII
        assert coord_participant.date_of_birth is None

    @pytest.mark.asyncio
    async def test_viewer_only_basic_organizational_data(
        self, participant_repo, sample_airtable_records
    ):
        """Viewer users should only see basic organizational information - CRITICAL SECURITY TEST."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("Иван", user_role="viewer")

        assert len(results) == 2
        viewer_participant = results[0]

        # Viewer should see basic organizational fields
        assert viewer_participant.full_name_ru == "Иван Иванов"
        assert viewer_participant.full_name_en == "Ivan Ivanov"
        assert viewer_participant.church == "Test Church"
        assert viewer_participant.gender == Gender.MALE
        assert viewer_participant.role == Role.CANDIDATE

        # But NO sensitive data - this is the critical security fix
        assert viewer_participant.contact_information is None
        assert viewer_participant.payment_amount is None
        assert viewer_participant.payment_status is None
        assert viewer_participant.date_of_birth is None
        assert viewer_participant.age is None
        assert viewer_participant.notes is None
        assert viewer_participant.submitted_by is None
        assert viewer_participant.church_leader is None

    @pytest.mark.asyncio
    async def test_no_role_treated_as_viewer(
        self, participant_repo, sample_airtable_records
    ):
        """Users with no role should be treated as viewers."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("Иван", user_role=None)

        viewer_participant = results[0]

        # Should have same filtering as viewer role
        assert viewer_participant.contact_information is None
        assert viewer_participant.payment_amount is None
        assert viewer_participant.notes is None


class TestSearchByNameEnhancedRoleFiltering:
    """Test role filtering in search_by_name_enhanced method."""

    @pytest.mark.asyncio
    async def test_enhanced_search_applies_role_filtering(
        self, participant_repo, sample_airtable_records
    ):
        """Enhanced search should apply role filtering before formatting results."""
        # Mock the cached participants method
        with patch.object(
            participant_repo, "_get_all_participants_cached"
        ) as mock_cached:
            # Create participant objects from records
            participants = []
            for record in sample_airtable_records:
                participant = Participant.from_airtable_record(record)
                participants.append(participant)

            mock_cached.return_value = participants

            results = await participant_repo.search_by_name_enhanced(
                "Иван", user_role="viewer"
            )

            # Should return tuples of (participant, score, formatted_result)
            assert len(results) > 0
            filtered_participant, score, formatted_result = results[0]

            # Verify role filtering was applied
            assert filtered_participant.contact_information is None
            assert filtered_participant.payment_amount is None
            assert filtered_participant.notes is None

            # Verify basic info still available
            assert filtered_participant.full_name_ru == "Иван Иванов"

    @pytest.mark.asyncio
    async def test_enhanced_search_admin_sees_sensitive_in_formatting(
        self, participant_repo, sample_airtable_records
    ):
        """Enhanced search formatting should reflect admin's access to sensitive data."""
        with patch.object(
            participant_repo, "_get_all_participants_cached"
        ) as mock_cached:
            participants = []
            for record in sample_airtable_records:
                participant = Participant.from_airtable_record(record)
                participants.append(participant)

            mock_cached.return_value = participants

            results = await participant_repo.search_by_name_enhanced(
                "Иван", user_role="admin"
            )

            if results:
                admin_participant, score, formatted_result = results[0]

                # Admin should see all sensitive data
                assert admin_participant.contact_information is not None
                assert admin_participant.payment_amount is not None
                # Formatted result should potentially include sensitive info for admins


class TestSearchByNameFuzzyRoleFiltering:
    """Test role filtering in search_by_name_fuzzy method."""

    @pytest.mark.asyncio
    async def test_fuzzy_search_applies_role_filtering(
        self, participant_repo, sample_airtable_records
    ):
        """Fuzzy search should apply role filtering to results."""
        with patch.object(
            participant_repo, "_get_all_participants_cached"
        ) as mock_cached:
            participants = []
            for record in sample_airtable_records:
                participant = Participant.from_airtable_record(record)
                participants.append(participant)

            mock_cached.return_value = participants

            results = await participant_repo.search_by_name_fuzzy(
                "Иван", user_role="coordinator"
            )

            if results:
                # Results are tuples of (participant, similarity_score)
                coord_participant, score = results[0]

                # Coordinator should see operational data
                assert coord_participant.payment_amount is not None
                assert coord_participant.contact_information is not None

                # But not highly sensitive PII
                assert coord_participant.date_of_birth is None


class TestRoleFilteringSecurityRegression:
    """Critical security regression tests to ensure the vulnerability is fixed."""

    @pytest.mark.asyncio
    async def test_viewer_cannot_access_financial_data(
        self, participant_repo, sample_airtable_records
    ):
        """CRITICAL: Viewers must not be able to access any financial information."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("test", user_role="viewer")

        for participant in results:
            # Financial data must be completely hidden
            assert (
                participant.payment_amount is None
            ), f"Payment amount leaked: {participant.payment_amount}"
            assert (
                participant.payment_date is None
            ), f"Payment date leaked: {participant.payment_date}"
            assert (
                participant.payment_status is None
            ), f"Payment status leaked: {participant.payment_status}"

    @pytest.mark.asyncio
    async def test_viewer_cannot_access_pii(
        self, participant_repo, sample_airtable_records
    ):
        """CRITICAL: Viewers must not be able to access personal identifiable information."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name("test", user_role="viewer")

        for participant in results:
            # PII must be completely hidden
            assert (
                participant.contact_information is None
            ), f"Contact info leaked: {participant.contact_information}"
            assert (
                participant.date_of_birth is None
            ), f"Date of birth leaked: {participant.date_of_birth}"
            assert participant.age is None, f"Age leaked: {participant.age}"
            assert participant.notes is None, f"Notes leaked: {participant.notes}"
            assert (
                participant.submitted_by is None
            ), f"Submitted by leaked: {participant.submitted_by}"

    @pytest.mark.asyncio
    async def test_role_hierarchy_enforcement(
        self, participant_repo, sample_airtable_records
    ):
        """Verify role hierarchy: admin > coordinator > viewer is properly enforced."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        admin_results = await participant_repo.search_by_name("test", user_role="admin")
        coord_results = await participant_repo.search_by_name(
            "test", user_role="coordinator"
        )
        viewer_results = await participant_repo.search_by_name(
            "test", user_role="viewer"
        )

        if admin_results and coord_results and viewer_results:
            admin_p, coord_p, viewer_p = (
                admin_results[0],
                coord_results[0],
                viewer_results[0],
            )

            # Admin should have the most access
            admin_sensitive_count = sum(
                1
                for field in [
                    admin_p.contact_information,
                    admin_p.payment_amount,
                    admin_p.date_of_birth,
                    admin_p.notes,
                    admin_p.submitted_by,
                ]
                if field is not None
            )

            # Coordinator should have less access than admin
            coord_sensitive_count = sum(
                1
                for field in [
                    coord_p.contact_information,
                    coord_p.payment_amount,
                    coord_p.date_of_birth,
                    coord_p.notes,
                    coord_p.submitted_by,
                ]
                if field is not None
            )

            # Viewer should have minimal access
            viewer_sensitive_count = sum(
                1
                for field in [
                    viewer_p.contact_information,
                    viewer_p.payment_amount,
                    viewer_p.date_of_birth,
                    viewer_p.notes,
                    viewer_p.submitted_by,
                ]
                if field is not None
            )

            # Verify hierarchy: admin >= coordinator >= viewer
            assert (
                admin_sensitive_count >= coord_sensitive_count
            ), "Admin should have >= access than coordinator"
            assert (
                coord_sensitive_count >= viewer_sensitive_count
            ), "Coordinator should have >= access than viewer"
            assert (
                viewer_sensitive_count == 0
            ), "Viewer should have no access to sensitive fields"

    @pytest.mark.asyncio
    async def test_unknown_role_secure_default(
        self, participant_repo, sample_airtable_records
    ):
        """Unknown/invalid roles should default to secure (viewer-level) access."""
        participant_repo.client.search_by_formula.return_value = sample_airtable_records

        results = await participant_repo.search_by_name(
            "test", user_role="invalid_role"
        )

        if results:
            participant = results[0]

            # Should default to viewer-level security (no sensitive data)
            assert participant.contact_information is None
            assert participant.payment_amount is None
            assert participant.date_of_birth is None
            assert participant.notes is None
