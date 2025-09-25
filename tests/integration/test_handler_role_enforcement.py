"""
Integration tests for handler-level role enforcement.

Verifies that bot handlers properly resolve user roles and enforce
authorization boundaries for viewer/coordinator/admin access.
"""

from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from telegram import Update, User
from telegram.ext import ContextTypes

from src.bot.handlers.search_handlers import process_name_search
from src.config.settings import Settings
from src.models.participant import Participant
from src.services.search_service import SearchResult


@pytest.fixture
def mock_settings():
    """Mock Settings instance with test user IDs."""
    settings = MagicMock(spec=Settings)

    # Create mock telegram settings
    mock_telegram = MagicMock()
    mock_telegram.admin_user_ids = [123]  # Admin user
    mock_telegram.coordinator_user_ids = [456]  # Coordinator user
    mock_telegram.viewer_user_ids = [789]  # Viewer user
    settings.telegram = mock_telegram

    return settings


@pytest.fixture
def mock_participants():
    """Mock participant data for testing filtering."""
    return [
        Participant(
            record_id="rec1",
            full_name_ru="Админ Тестов",
            full_name_en="Admin Test",
            role="TEAM",
            phone="+1234567890",
            email="admin@test.com",
        ),
        Participant(
            record_id="rec2",
            full_name_ru="Координатор Иванов",
            full_name_en="Coordinator Ivan",
            role="TEAM",
            phone="+1234567891",
            email="coord@test.com",
        ),
        Participant(
            record_id="rec3",
            full_name_ru="Зритель Петров",
            full_name_en="Viewer Peter",
            role="CANDIDATE",
            phone=None,  # Viewer shouldn't see this
            email=None,  # Viewer shouldn't see this
        ),
    ]


@pytest.fixture
def mock_update():
    """Create mock Update object."""
    update = MagicMock(spec=Update)
    update.message.text = "Тест"
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def mock_context():
    """Create mock Context object."""
    context = MagicMock(spec=ContextTypes.DEFAULT_TYPE)
    context.user_data = {}
    return context


class TestHandlerRoleEnforcement:
    """Test role enforcement in bot handlers."""

    @patch("src.bot.handlers.search_handlers.get_settings")
    @patch("src.bot.handlers.search_handlers.get_user_role")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    async def test_admin_gets_all_data(
        self,
        mock_get_repo,
        mock_get_user_role,
        mock_get_settings,
        mock_update,
        mock_context,
        mock_settings,
        mock_participants,
    ):
        """Test that admin users get full data access."""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "admin"
        mock_update.effective_user = User(id=123, first_name="Admin", is_bot=False)

        mock_repo = AsyncMock()
        mock_repo.search_by_name_enhanced.return_value = [
            (mock_participants[0], 0.9, "Admin Test - TEAM")
        ]
        mock_get_repo.return_value = mock_repo

        # Execute handler
        result = await process_name_search(mock_update, mock_context)

        # Verify admin role was resolved and passed to repository
        mock_get_user_role.assert_called_once_with(123, mock_settings)
        mock_repo.search_by_name_enhanced.assert_called_once_with(
            "Тест", threshold=0.8, limit=5, user_role="admin"
        )

        # Verify results stored correctly
        assert len(mock_context.user_data["search_results"]) == 1
        assert result is not None

    @patch("src.bot.handlers.search_handlers.get_settings")
    @patch("src.bot.handlers.search_handlers.get_user_role")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    async def test_coordinator_gets_filtered_data(
        self,
        mock_get_repo,
        mock_get_user_role,
        mock_get_settings,
        mock_update,
        mock_context,
        mock_settings,
        mock_participants,
    ):
        """Test that coordinator users get appropriately filtered data."""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "coordinator"
        mock_update.effective_user = User(
            id=456, first_name="Coordinator", is_bot=False
        )

        mock_repo = AsyncMock()
        mock_repo.search_by_name_enhanced.return_value = [
            (mock_participants[1], 0.85, "Coordinator Ivan - TEAM")
        ]
        mock_get_repo.return_value = mock_repo

        # Execute handler
        result = await process_name_search(mock_update, mock_context)

        # Verify coordinator role was resolved and passed
        mock_get_user_role.assert_called_once_with(456, mock_settings)
        mock_repo.search_by_name_enhanced.assert_called_once_with(
            "Тест", threshold=0.8, limit=5, user_role="coordinator"
        )

        assert len(mock_context.user_data["search_results"]) == 1
        assert result is not None

    @patch("src.bot.handlers.search_handlers.get_settings")
    @patch("src.bot.handlers.search_handlers.get_user_role")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    async def test_viewer_gets_restricted_data(
        self,
        mock_get_repo,
        mock_get_user_role,
        mock_get_settings,
        mock_update,
        mock_context,
        mock_settings,
        mock_participants,
    ):
        """Test that viewer users get most restricted data."""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "viewer"
        mock_update.effective_user = User(id=789, first_name="Viewer", is_bot=False)

        mock_repo = AsyncMock()
        mock_repo.search_by_name_enhanced.return_value = [
            (mock_participants[2], 0.8, "Viewer Peter - Участник")
        ]
        mock_get_repo.return_value = mock_repo

        # Execute handler
        result = await process_name_search(mock_update, mock_context)

        # Verify viewer role was resolved and passed
        mock_get_user_role.assert_called_once_with(789, mock_settings)
        mock_repo.search_by_name_enhanced.assert_called_once_with(
            "Тест", threshold=0.8, limit=5, user_role="viewer"
        )

        assert len(mock_context.user_data["search_results"]) == 1
        assert result is not None

    @patch("src.bot.handlers.search_handlers.get_settings")
    @patch("src.bot.handlers.search_handlers.get_user_role")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    @patch("src.bot.handlers.search_handlers.filter_participants_by_role")
    async def test_fallback_path_applies_filtering(
        self,
        mock_filter_participants,
        mock_get_repo,
        mock_get_user_role,
        mock_get_settings,
        mock_update,
        mock_context,
        mock_settings,
        mock_participants,
    ):
        """Test that fallback search path properly applies role-based filtering."""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "viewer"
        mock_update.effective_user = User(id=789, first_name="Viewer", is_bot=False)

        mock_repo = AsyncMock()
        # Make enhanced search fail to trigger fallback
        mock_repo.search_by_name_enhanced.side_effect = AttributeError(
            "Enhanced search not available"
        )
        mock_repo.list_all.return_value = mock_participants
        mock_get_repo.return_value = mock_repo

        # Mock filtered results
        mock_filter_participants.return_value = [
            mock_participants[2]
        ]  # Viewer only sees participant 3

        # Mock search service
        with patch(
            "src.bot.handlers.search_handlers.SearchService"
        ) as mock_search_service:
            mock_service_instance = MagicMock()
            mock_service_instance.search_participants.return_value = [
                SearchResult(participant=mock_participants[2], similarity_score=0.8)
            ]
            mock_search_service.return_value = mock_service_instance

            # Execute handler
            result = await process_name_search(mock_update, mock_context)

        # Verify fallback filtering was applied
        mock_filter_participants.assert_called_once_with(mock_participants, "viewer")
        mock_service_instance.search_participants.assert_called_once_with(
            "Тест", [mock_participants[2]]
        )

        assert len(mock_context.user_data["search_results"]) == 1
        assert result is not None

    @patch("src.bot.handlers.search_handlers.get_settings")
    @patch("src.bot.handlers.search_handlers.get_user_role")
    @patch("src.bot.handlers.search_handlers.get_participant_repository")
    async def test_unauthorized_user_gets_none_role(
        self,
        mock_get_repo,
        mock_get_user_role,
        mock_get_settings,
        mock_update,
        mock_context,
        mock_settings,
    ):
        """Test that unauthorized users get user_role=None passed to repository."""
        # Setup mocks
        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = None  # Unauthorized user
        mock_update.effective_user = User(
            id=999, first_name="Unauthorized", is_bot=False
        )

        mock_repo = AsyncMock()
        mock_repo.search_by_name_enhanced.return_value = []
        mock_get_repo.return_value = mock_repo

        # Execute handler
        result = await process_name_search(mock_update, mock_context)

        # Verify None role was passed to repository
        mock_get_user_role.assert_called_once_with(999, mock_settings)
        mock_repo.search_by_name_enhanced.assert_called_once_with(
            "Тест", threshold=0.8, limit=5, user_role=None
        )

        assert result is not None


class TestAccessControlDecorator:
    """Test the access control decorator middleware."""

    @patch("src.utils.access_control.get_settings")
    @patch("src.utils.access_control.get_user_role")
    async def test_require_admin_allows_admin(
        self, mock_get_user_role, mock_get_settings, mock_settings
    ):
        """Test that @require_admin allows admin users."""
        from src.utils.access_control import require_admin

        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "admin"

        @require_admin()
        async def test_handler(update, context):
            return "success"

        update = MagicMock()
        update.effective_user = User(id=123, first_name="Admin", is_bot=False)
        context = MagicMock()

        result = await test_handler(update, context)
        assert result == "success"

    @patch("src.utils.access_control.get_settings")
    @patch("src.utils.access_control.get_user_role")
    async def test_require_admin_denies_viewer(
        self, mock_get_user_role, mock_get_settings, mock_settings
    ):
        """Test that @require_admin denies viewer users."""
        from src.utils.access_control import require_admin

        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "viewer"

        @require_admin()
        async def test_handler(update, context):
            return "success"

        update = MagicMock()
        update.effective_user = User(id=789, first_name="Viewer", is_bot=False)
        update.message.reply_text = AsyncMock()
        context = MagicMock()

        result = await test_handler(update, context)

        # Should return None (access denied)
        assert result is None
        # Should send unauthorized message
        update.message.reply_text.assert_called_once()

    @patch("src.utils.access_control.get_settings")
    @patch("src.utils.access_control.get_user_role")
    async def test_require_coordinator_or_above_allows_coordinator(
        self, mock_get_user_role, mock_get_settings, mock_settings
    ):
        """Test that @require_coordinator_or_above allows coordinator users."""
        from src.utils.access_control import require_coordinator_or_above

        mock_get_settings.return_value = mock_settings
        mock_get_user_role.return_value = "coordinator"

        @require_coordinator_or_above()
        async def test_handler(update, context):
            return "success"

        update = MagicMock()
        update.effective_user = User(id=456, first_name="Coordinator", is_bot=False)
        context = MagicMock()

        result = await test_handler(update, context)
        assert result == "success"
