"""
Integration tests for multi-table repository coordination.

This module tests that BibleReaders and ROE repositories work together
without connection conflicts using the factory pattern.
"""

from unittest.mock import AsyncMock

import pytest

from src.data.airtable.airtable_bible_readers_repo import AirtableBibleReadersRepository
from src.data.airtable.airtable_client_factory import AirtableClientFactory
from src.data.airtable.airtable_roe_repo import AirtableROERepository


class TestMultiTableRepositories:
    """Integration tests for multi-table repository coordination."""

    @pytest.fixture
    def mock_factory(self):
        """Create a mock client factory."""
        factory = AsyncMock(spec=AirtableClientFactory)

        # Create separate mock clients for each table
        bible_readers_client = AsyncMock()
        roe_client = AsyncMock()

        # Configure factory to return appropriate clients
        def create_client_side_effect(table_type):
            if table_type == "bible_readers":
                return bible_readers_client
            elif table_type == "roe":
                return roe_client
            else:
                raise ValueError(f"Unknown table type: {table_type}")

        factory.create_client.side_effect = create_client_side_effect

        return factory, bible_readers_client, roe_client

    async def test_repositories_use_separate_clients(self, mock_factory):
        """Test that repositories use separate clients from factory."""
        factory, bible_readers_client, roe_client = mock_factory

        # Create repositories using factory
        bible_readers_repo = AirtableBibleReadersRepository(
            factory.create_client("bible_readers")
        )
        roe_repo = AirtableROERepository(factory.create_client("roe"))

        # Verify each repository has its own client
        assert bible_readers_repo.client is bible_readers_client
        assert roe_repo.client is roe_client
        assert bible_readers_repo.client is not roe_repo.client

        # Verify factory was called for each table type
        factory.create_client.assert_any_call("bible_readers")
        factory.create_client.assert_any_call("roe")

    async def test_repositories_have_correct_field_mappings(self, mock_factory):
        """Test that repositories use correct field mappings."""
        factory, bible_readers_client, roe_client = mock_factory

        # Create repositories
        bible_readers_repo = AirtableBibleReadersRepository(bible_readers_client)
        roe_repo = AirtableROERepository(roe_client)

        # Verify field mappings are different and correct
        assert bible_readers_repo.field_mapping is not roe_repo.field_mapping

        # Test key field mappings
        assert (
            bible_readers_repo.field_mapping.python_to_airtable_field("where")
            == "Where"
        )
        assert (
            roe_repo.field_mapping.python_to_airtable_field("roe_topic") == "RoeTopic"
        )

    async def test_concurrent_repository_operations(self, mock_factory):
        """Test that repositories can operate concurrently without conflicts."""
        factory, bible_readers_client, roe_client = mock_factory

        # Setup mock responses
        bible_readers_client.list_records.return_value = {"records": [], "offset": None}
        roe_client.list_records.return_value = {"records": [], "offset": None}

        # Create repositories
        bible_readers_repo = AirtableBibleReadersRepository(bible_readers_client)
        roe_repo = AirtableROERepository(roe_client)

        # Perform concurrent operations
        import asyncio

        bible_readers_task = asyncio.create_task(bible_readers_repo.list_all())
        roe_task = asyncio.create_task(roe_repo.list_all())

        # Wait for both to complete
        bible_readers_result, roe_result = await asyncio.gather(
            bible_readers_task, roe_task
        )

        # Verify both operations completed successfully
        assert bible_readers_result == []
        assert roe_result == []

        # Verify each client was called independently
        bible_readers_client.list_records.assert_called_once()
        roe_client.list_records.assert_called_once()

    async def test_repository_client_isolation(self, mock_factory):
        """Test that client operations are isolated between repositories."""
        factory, bible_readers_client, roe_client = mock_factory

        # Create repositories
        bible_readers_repo = AirtableBibleReadersRepository(bible_readers_client)
        roe_repo = AirtableROERepository(roe_client)

        # Setup different responses for each client
        bible_readers_client.get_record.return_value = None
        roe_client.get_record.return_value = None

        # Call operations on different repositories
        bible_result = await bible_readers_repo.get_by_id("bible123")
        roe_result = await roe_repo.get_by_id("roe456")

        # Verify each client was called with its specific record ID
        bible_readers_client.get_record.assert_called_once_with("bible123")
        roe_client.get_record.assert_called_once_with("roe456")

        # Verify results
        assert bible_result is None
        assert roe_result is None
