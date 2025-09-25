"""
Unit tests for authorization configuration settings.

Tests cover:
- Viewer and coordinator user ID parsing from environment variables
- Role hierarchy validation
- Backward compatibility with existing admin settings
- Configuration validation and error handling
"""

import os
from unittest.mock import patch

import pytest

from src.config.settings import Settings, TelegramSettings


class TestViewerCoordinatorConfiguration:
    """Test suite for viewer and coordinator role configuration."""

    def test_default_viewer_coordinator_empty_lists(self):
        """Test that viewer and coordinator lists default to empty when not set."""
        # RED phase - this test will fail until we implement viewer_user_ids and coordinator_user_ids

        with patch.dict(os.environ, {}, clear=True):
            settings = TelegramSettings()

            # Should have viewer and coordinator user ID lists
            assert hasattr(settings, "viewer_user_ids")
            assert hasattr(settings, "coordinator_user_ids")

            # Default to empty lists
            assert settings.viewer_user_ids == []
            assert settings.coordinator_user_ids == []

    def test_viewer_ids_parsing_comma_separated(self):
        """Test parsing viewer IDs from comma-separated environment variable."""
        # RED phase - this test will fail until we implement TELEGRAM_VIEWER_IDS parsing

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_VIEWER_IDS": "111111111,222222222,333333333",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.viewer_user_ids == [111111111, 222222222, 333333333]

    def test_coordinator_ids_parsing_comma_separated(self):
        """Test parsing coordinator IDs from comma-separated environment variable."""
        # RED phase - this test will fail until we implement TELEGRAM_COORDINATOR_IDS parsing

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_COORDINATOR_IDS": "444444444,555555555",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.coordinator_user_ids == [444444444, 555555555]

    def test_viewer_ids_parsing_json_array(self):
        """Test parsing viewer IDs from JSON array format."""
        # RED phase - this test will fail until we implement JSON parsing for viewer IDs

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_VIEWER_IDS": "[111111111, 222222222, 333333333]",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.viewer_user_ids == [111111111, 222222222, 333333333]

    def test_coordinator_ids_parsing_json_array(self):
        """Test parsing coordinator IDs from JSON array format."""
        # RED phase - this test will fail until we implement JSON parsing for coordinator IDs

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_COORDINATOR_IDS": "[444444444, 555555555]",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.coordinator_user_ids == [444444444, 555555555]

    def test_viewer_ids_parsing_with_spaces(self):
        """Test parsing viewer IDs with whitespace handling."""
        # RED phase - this test will fail until we implement whitespace handling

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_VIEWER_IDS": " 111111111 , 222222222 , 333333333 ",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.viewer_user_ids == [111111111, 222222222, 333333333]

    def test_coordinator_ids_parsing_with_spaces(self):
        """Test parsing coordinator IDs with whitespace handling."""
        # RED phase - this test will fail until we implement whitespace handling

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_COORDINATOR_IDS": " 444444444 , 555555555 ",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            assert settings.coordinator_user_ids == [444444444, 555555555]

    def test_viewer_ids_invalid_format_graceful_handling(self):
        """Test graceful handling of invalid viewer ID formats."""
        # RED phase - this test will fail until we implement error handling

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_VIEWER_IDS": "not_a_number,222222222,another_invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            # Should parse only valid numbers
            assert settings.viewer_user_ids == [222222222]

    def test_coordinator_ids_invalid_format_graceful_handling(self):
        """Test graceful handling of invalid coordinator ID formats."""
        # RED phase - this test will fail until we implement error handling

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_COORDINATOR_IDS": "invalid,555555555,also_invalid",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            # Should parse only valid numbers
            assert settings.coordinator_user_ids == [555555555]

    def test_backward_compatibility_admin_ids_still_work(self):
        """Test that existing admin ID functionality remains unchanged."""
        # RED phase - this test should pass since admin functionality already exists

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_ADMIN_IDS": "123456789,987654321",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            # Admin functionality should remain unchanged
            assert settings.admin_user_ids == [123456789, 987654321]

    def test_all_role_types_can_be_configured_simultaneously(self):
        """Test that all three role types can be configured at the same time."""
        # RED phase - this test will fail until we implement viewer/coordinator parsing

        env_vars = {
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_ADMIN_IDS": "123456789",
            "TELEGRAM_COORDINATOR_IDS": "444444444,555555555",
            "TELEGRAM_VIEWER_IDS": "111111111,222222222,333333333",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = TelegramSettings()

            # All role types should be populated
            assert settings.admin_user_ids == [123456789]
            assert settings.coordinator_user_ids == [444444444, 555555555]
            assert settings.viewer_user_ids == [111111111, 222222222, 333333333]


class TestIntegrationWithSettings:
    """Test integration of role configuration with main Settings container."""

    def test_settings_initialization_with_roles(self):
        """Test that Settings properly initializes with role configuration."""
        # RED phase - this test will fail until we implement role parsing

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_ADMIN_IDS": "123456789",
            "TELEGRAM_COORDINATOR_IDS": "444444444",
            "TELEGRAM_VIEWER_IDS": "111111111,222222222",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()

            # Should initialize without errors
            assert settings.telegram.admin_user_ids == [123456789]
            assert settings.telegram.coordinator_user_ids == [444444444]
            assert settings.telegram.viewer_user_ids == [111111111, 222222222]

    def test_settings_to_dict_includes_role_counts(self):
        """Test that to_dict includes counts for all role types."""
        # RED phase - this test will fail until we update to_dict method

        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "TELEGRAM_BOT_TOKEN": "test_token",
            "TELEGRAM_ADMIN_IDS": "123456789",
            "TELEGRAM_COORDINATOR_IDS": "444444444,555555555",
            "TELEGRAM_VIEWER_IDS": "111111111,222222222,333333333",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = Settings()
            settings_dict = settings.to_dict()

            # Should include counts for all role types
            assert settings_dict["telegram"]["admin_count"] == 1
            assert settings_dict["telegram"]["coordinator_count"] == 2
            assert settings_dict["telegram"]["viewer_count"] == 3
