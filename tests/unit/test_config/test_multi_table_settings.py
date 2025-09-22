"""
Unit tests for multi-table configuration settings.

Tests cover:
- BibleReaders table configuration
- ROE table configuration
- Multi-table environment variable loading
- Configuration validation for multiple tables
"""

import os
from unittest.mock import patch

import pytest

from src.config.settings import DatabaseSettings


class TestMultiTableConfiguration:
    """Test suite for multi-table Airtable configuration."""

    def test_default_bible_readers_table_config(self):
        """Test that default BibleReaders table configuration is set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = DatabaseSettings()

            # Should have BibleReaders table configuration
            assert hasattr(settings, "bible_readers_table_id")
            assert settings.bible_readers_table_id == "tblGEnSfpPOuPLXcm"  # Actual table ID from database
            assert hasattr(settings, "bible_readers_table_name")
            assert settings.bible_readers_table_name == "BibleReaders"

    def test_environment_bible_readers_override(self):
        """Test that BibleReaders table can be configured via environment variables."""
        env_vars = {
            "AIRTABLE_BIBLE_READERS_TABLE_ID": "tblCustomBibleReaders123",
            "AIRTABLE_BIBLE_READERS_TABLE_NAME": "CustomBibleReaders"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.bible_readers_table_id == "tblCustomBibleReaders123"
            assert settings.bible_readers_table_name == "CustomBibleReaders"

    def test_default_roe_table_config(self):
        """Test that default ROE table configuration is set correctly."""
        with patch.dict(os.environ, {}, clear=True):
            settings = DatabaseSettings()

            # Should have ROE table configuration
            assert hasattr(settings, "roe_table_id")
            assert settings.roe_table_id == "tbl0j8bcgkV3lVAdc"  # Actual table ID from database
            assert hasattr(settings, "roe_table_name")
            assert settings.roe_table_name == "ROE"

    def test_environment_roe_override(self):
        """Test that ROE table can be configured via environment variables."""
        env_vars = {
            "AIRTABLE_ROE_TABLE_ID": "tblCustomROE456",
            "AIRTABLE_ROE_TABLE_NAME": "CustomROE"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            assert settings.roe_table_id == "tblCustomROE456"
            assert settings.roe_table_name == "CustomROE"

    def test_multi_table_validation_empty_ids(self):
        """Test that validation fails when table IDs are empty."""
        env_vars = {
            "AIRTABLE_API_KEY": "valid_key",
            "AIRTABLE_BASE_ID": "valid_base",
            "AIRTABLE_BIBLE_READERS_TABLE_ID": "",  # Empty should fail
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            with pytest.raises(ValueError) as exc_info:
                settings.validate()

            assert "AIRTABLE_BIBLE_READERS_TABLE_ID" in str(exc_info.value)

    def test_get_table_config_method(self):
        """Test that we can get table-specific configurations."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "AIRTABLE_TABLE_ID": "tbl8ivwOdAUvMi3Jy",
            "AIRTABLE_BIBLE_READERS_TABLE_ID": "tblBibleReaders123",
            "AIRTABLE_ROE_TABLE_ID": "tblROE456",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            # Should have method to get table-specific config
            assert hasattr(settings, "get_table_config")

            # Get Participants table config
            participants_config = settings.get_table_config("participants")
            assert participants_config["table_id"] == "tbl8ivwOdAUvMi3Jy"
            assert participants_config["table_name"] == "Participants"

            # Get BibleReaders table config
            bible_readers_config = settings.get_table_config("bible_readers")
            assert bible_readers_config["table_id"] == "tblBibleReaders123"
            assert bible_readers_config["table_name"] == "BibleReaders"

            # Get ROE table config
            roe_config = settings.get_table_config("roe")
            assert roe_config["table_id"] == "tblROE456"
            assert roe_config["table_name"] == "ROE"

    def test_backward_compatibility(self):
        """Test that existing Participants configuration still works."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "AIRTABLE_TABLE_ID": "tbl8ivwOdAUvMi3Jy",
            "AIRTABLE_TABLE_NAME": "Participants"
        }

        with patch.dict(os.environ, env_vars, clear=True):
            settings = DatabaseSettings()

            # Original fields should still work
            assert settings.airtable_table_id == "tbl8ivwOdAUvMi3Jy"
            assert settings.airtable_table_name == "Participants"

            # Should be able to create AirtableConfig as before
            config = settings.to_airtable_config()
            assert config.table_id == "tbl8ivwOdAUvMi3Jy"