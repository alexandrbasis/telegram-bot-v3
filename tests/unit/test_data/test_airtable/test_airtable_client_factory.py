"""
Unit tests for Airtable client factory.

Tests cover factory pattern for creating table-specific clients
while maintaining single-table client behavior.
"""

import pytest
from unittest.mock import patch

from src.data.airtable.airtable_client_factory import AirtableClientFactory
from src.data.airtable.airtable_client import AirtableClient
from src.config.settings import DatabaseSettings


class TestAirtableClientFactory:
    """Test suite for AirtableClientFactory."""

    @pytest.fixture
    def factory(self):
        """Create a factory instance for testing."""
        return AirtableClientFactory()

    def test_create_participants_client(self, factory):
        """Test creating client for participants table."""
        with patch.dict("os.environ", {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base"
        }):
            client = factory.create_client("participants")

            assert isinstance(client, AirtableClient)
            assert client.config.table_id == "tbl8ivwOdAUvMi3Jy"
            assert client.config.table_name == "Participants"

    def test_create_bible_readers_client(self, factory):
        """Test creating client for bible_readers table."""
        with patch.dict("os.environ", {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base"
        }):
            client = factory.create_client("bible_readers")

            assert isinstance(client, AirtableClient)
            assert client.config.table_id == "tblGEnSfpPOuPLXcm"
            assert client.config.table_name == "BibleReaders"

    def test_create_roe_client(self, factory):
        """Test creating client for roe table."""
        with patch.dict("os.environ", {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base"
        }):
            client = factory.create_client("roe")

            assert isinstance(client, AirtableClient)
            assert client.config.table_id == "tbl0j8bcgkV3lVAdc"
            assert client.config.table_name == "ROE"

    def test_invalid_table_type_raises_error(self, factory):
        """Test that invalid table type raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            factory.create_client("invalid_table")

        assert "invalid_table" in str(exc_info.value)

    def test_factory_uses_database_settings(self):
        """Test that factory properly uses DatabaseSettings."""
        with patch.dict("os.environ", {
            "AIRTABLE_API_KEY": "custom_key",
            "AIRTABLE_BASE_ID": "custom_base"
        }, clear=True):
            # Create factory after environment is patched
            factory = AirtableClientFactory()
            client = factory.create_client("participants")

            assert client.config.api_key == "custom_key"
            assert client.config.base_id == "custom_base"

    def test_all_supported_table_types(self, factory):
        """Test that factory supports all expected table types."""
        supported_types = ["participants", "bible_readers", "roe"]

        with patch.dict("os.environ", {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base"
        }):
            for table_type in supported_types:
                client = factory.create_client(table_type)
                assert isinstance(client, AirtableClient)