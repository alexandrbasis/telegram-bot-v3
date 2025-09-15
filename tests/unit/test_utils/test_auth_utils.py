"""
Unit tests for authentication utilities.

Tests admin user authorization functionality.
"""

from unittest.mock import MagicMock, patch

import pytest

from src.config.settings import Settings, TelegramSettings
from src.utils.auth_utils import is_admin_user


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