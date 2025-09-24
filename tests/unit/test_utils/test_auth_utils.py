"""
Unit tests for authentication utilities.

Tests cover:
- Admin user authorization functionality (existing)
- Role-based authorization functions (viewer, coordinator, admin)
- Role hierarchy validation (viewer < coordinator < admin)
- User role resolution and caching
- Performance requirements (<50ms per check)
"""

import time
from unittest.mock import MagicMock, patch

import pytest

from src.config.settings import Settings, TelegramSettings
from src.utils.auth_utils import (
    get_user_role,
    is_admin_user,
    is_coordinator_user,
    is_viewer_user,
)


class TestIsAdminUser:
    """Test is_admin_user function."""

    def test_admin_user_in_list(self):
        """Test that a user in the admin list is recognized as admin."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456, 789012, 345678]

        # Act & Assert
        assert is_admin_user(123456, settings) is True
        assert is_admin_user(789012, settings) is True

        assert is_admin_user(345678, settings) is True

    def test_non_admin_user(self):
        """Test that a user not in the admin list is not recognized as admin."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456, 789012]

        # Act & Assert
        assert is_admin_user(999999, settings) is False
        assert is_admin_user(111111, settings) is False

    def test_empty_admin_list(self):
        """Test behavior with empty admin list."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = []

        # Act & Assert
        assert is_admin_user(123456, settings) is False

    def test_single_admin(self):
        """Test with single admin user."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456]

        # Act & Assert
        assert is_admin_user(123456, settings) is True
        assert is_admin_user(789012, settings) is False

    def test_none_user_id(self):
        """Test handling of None user ID."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456]

        # Act & Assert
        assert is_admin_user(None, settings) is False

    def test_string_user_id_conversion(self):
        """Test that string user IDs are properly converted."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456, 789012]

        # Act - pass string that can be converted to int
        assert is_admin_user("123456", settings) is True
        assert is_admin_user("789012", settings) is True
        assert is_admin_user("999999", settings) is False

    def test_invalid_string_user_id(self):
        """Test handling of invalid string user IDs."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456]

        # Act & Assert
        assert is_admin_user("not_a_number", settings) is False
        assert is_admin_user("", settings) is False
        assert is_admin_user("12.34", settings) is False

    def test_negative_user_id(self):
        """Test handling of negative user IDs."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456, -789012]

        # Act & Assert
        assert is_admin_user(-789012, settings) is True
        assert is_admin_user(-999999, settings) is False

    def test_zero_user_id(self):
        """Test handling of zero as user ID."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [0, 123456]

        # Act & Assert
        assert is_admin_user(0, settings) is True
        assert is_admin_user(123456, settings) is True

    def test_large_admin_list(self):
        """Test performance with large admin list."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        # Create a large list of admin IDs
        settings.telegram.admin_user_ids = list(range(1000000, 1001000))

        # Act & Assert
        assert is_admin_user(1000500, settings) is True
        assert is_admin_user(999999, settings) is False
        assert is_admin_user(1001001, settings) is False

    def test_duplicate_admin_ids(self):
        """Test handling of duplicate admin IDs in the list."""
        # Arrange
        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.admin_user_ids = [123456, 123456, 789012]

        # Act & Assert
        assert is_admin_user(123456, settings) is True
        assert is_admin_user(789012, settings) is True


class TestRoleBasedAuthorizationFunctions:
    """Test suite for role-based authorization functions."""

    def test_is_viewer_user_with_valid_viewer_id(self):
        """Test that is_viewer_user correctly identifies viewer users."""
        # RED phase - this test will fail until we implement is_viewer_user function

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [111111111, 222222222]
        settings.telegram.coordinator_user_ids = []
        settings.telegram.admin_user_ids = []

        # Should return True for viewer IDs
        assert is_viewer_user(111111111, settings) is True
        assert is_viewer_user(222222222, settings) is True

        # Should return False for non-viewer IDs
        assert is_viewer_user(999999999, settings) is False

    def test_is_coordinator_user_with_valid_coordinator_id(self):
        """Test that is_coordinator_user correctly identifies coordinator users."""
        # RED phase - this test will fail until we implement is_coordinator_user function

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = []
        settings.telegram.coordinator_user_ids = [444444444, 555555555]
        settings.telegram.admin_user_ids = []

        # Should return True for coordinator IDs
        assert is_coordinator_user(444444444, settings) is True
        assert is_coordinator_user(555555555, settings) is True

        # Should return False for non-coordinator IDs
        assert is_coordinator_user(999999999, settings) is False

    def test_role_hierarchy_coordinator_has_viewer_access(self):
        """Test that coordinators have viewer-level access (role hierarchy)."""
        # RED phase - this test will fail until we implement role hierarchy

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = []
        settings.telegram.coordinator_user_ids = [444444444]
        settings.telegram.admin_user_ids = []

        # Coordinator should have viewer access
        assert is_viewer_user(444444444, settings) is True
        assert is_coordinator_user(444444444, settings) is True

    def test_role_hierarchy_admin_has_coordinator_and_viewer_access(self):
        """Test that admins have coordinator and viewer-level access (role hierarchy)."""
        # RED phase - this test will fail until we implement role hierarchy

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = []
        settings.telegram.coordinator_user_ids = []
        settings.telegram.admin_user_ids = [123456789]

        # Admin should have all access levels
        assert is_viewer_user(123456789, settings) is True
        assert is_coordinator_user(123456789, settings) is True
        assert is_admin_user(123456789, settings) is True

    def test_get_user_role_returns_correct_role(self):
        """Test that get_user_role returns the highest role for a user."""
        # RED phase - this test will fail until we implement get_user_role function

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [111111111]
        settings.telegram.coordinator_user_ids = [444444444]
        settings.telegram.admin_user_ids = [123456789]

        # Should return correct roles
        assert get_user_role(111111111, settings) == "viewer"
        assert get_user_role(444444444, settings) == "coordinator"
        assert get_user_role(123456789, settings) == "admin"
        assert get_user_role(999999999, settings) is None

    def test_get_user_role_with_multiple_roles_returns_highest(self):
        """Test that get_user_role returns the highest role when user has multiple."""
        # RED phase - this test will fail until we implement role priority logic

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [123456789]
        settings.telegram.coordinator_user_ids = [123456789]
        settings.telegram.admin_user_ids = [123456789]

        # Should return the highest role (admin)
        assert get_user_role(123456789, settings) == "admin"

    def test_role_functions_handle_none_user_id(self):
        """Test that role functions gracefully handle None user ID."""
        # RED phase - this test will fail until we implement None handling

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [111111111]
        settings.telegram.coordinator_user_ids = [444444444]
        settings.telegram.admin_user_ids = [123456789]

        # Should return False/None for None user ID
        assert is_viewer_user(None, settings) is False
        assert is_coordinator_user(None, settings) is False
        assert get_user_role(None, settings) is None

    def test_role_functions_handle_string_user_id(self):
        """Test that role functions handle string user IDs correctly."""
        # RED phase - this test will fail until we implement string conversion

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [111111111]
        settings.telegram.coordinator_user_ids = [444444444]
        settings.telegram.admin_user_ids = [123456789]

        # Should handle string IDs
        assert is_viewer_user("111111111", settings) is True
        assert is_coordinator_user("444444444", settings) is True
        assert get_user_role("123456789", settings) == "admin"

        # Should handle invalid string IDs
        assert is_viewer_user("not_a_number", settings) is False
        assert get_user_role("invalid", settings) is None

    def test_role_functions_handle_empty_lists(self):
        """Test that role functions handle empty user ID lists."""
        # RED phase - this test will fail until we implement empty list handling

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = []
        settings.telegram.coordinator_user_ids = []
        settings.telegram.admin_user_ids = []

        # Should return False/None for any user when lists are empty
        assert is_viewer_user(111111111, settings) is False
        assert is_coordinator_user(444444444, settings) is False
        assert get_user_role(123456789, settings) is None


class TestAuthorizationPerformance:
    """Test suite for authorization performance requirements."""

    def test_authorization_functions_performance_under_50ms(self):
        """Test that authorization functions complete in under 50ms as required."""
        # RED phase - this test will fail until we implement the functions

        settings = MagicMock(spec=Settings)
        settings.telegram = MagicMock(spec=TelegramSettings)
        settings.telegram.viewer_user_ids = [111111111]
        settings.telegram.coordinator_user_ids = [444444444]
        settings.telegram.admin_user_ids = [123456789]

        # Test performance for each function
        start_time = time.time()
        for _ in range(100):  # Run multiple iterations
            is_viewer_user(111111111, settings)
            is_coordinator_user(444444444, settings)
            get_user_role(123456789, settings)
        end_time = time.time()

        # Average should be well under 50ms (0.05 seconds)
        average_time = (end_time - start_time) / 300  # 300 total function calls
        assert average_time < 0.05, f"Authorization functions too slow: {average_time:.3f}s average"


class TestIntegrationWithRealSettings:
    """Test integration of authorization functions with real Settings objects."""

    def test_role_functions_with_real_settings_object(self):
        """Test that role functions work with real Settings object."""
        # RED phase - this test will fail until we implement the functions

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_VIEWER_IDS": "111111111,222222222",
            "TELEGRAM_COORDINATOR_IDS": "444444444",
            "TELEGRAM_ADMIN_IDS": "123456789",
        }

        with patch.dict("os.environ", env_vars, clear=True):
            settings = Settings()

            # Should work with real settings
            assert is_viewer_user(111111111, settings) is True
            assert is_coordinator_user(444444444, settings) is True
            assert is_admin_user(123456789, settings) is True

            # Should respect role hierarchy
            assert is_viewer_user(444444444, settings) is True  # Coordinator has viewer access
            assert is_viewer_user(123456789, settings) is True  # Admin has viewer access
            assert is_coordinator_user(123456789, settings) is True  # Admin has coordinator access

            # Should return correct roles
            assert get_user_role(111111111, settings) == "viewer"
            assert get_user_role(444444444, settings) == "coordinator"
            assert get_user_role(123456789, settings) == "admin"
            assert get_user_role(999999999, settings) is None
