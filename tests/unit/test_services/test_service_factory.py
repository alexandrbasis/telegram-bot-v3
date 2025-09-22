"""Tests for service_factory helper functions."""

import os
from unittest.mock import Mock, patch

import pytest

from src.config.settings import Settings
from src.data.airtable.airtable_client import AirtableConfig
from src.services import service_factory
from src.services.bible_readers_export_service import BibleReadersExportService
from src.services.roe_export_service import ROEExportService


@pytest.fixture(autouse=True)
def reset_client_cache():
    """Ensure cached client is cleared between tests."""
    service_factory.reset_airtable_client_cache()
    yield
    service_factory.reset_airtable_client_cache()


def _build_settings(config: AirtableConfig) -> Mock:
    settings = Mock()
    settings.get_airtable_config.return_value = config
    return settings


class TestAirtableClientReuse:
    """Test reuse behaviour for shared Airtable client instances."""

    @patch("src.services.service_factory.AirtableClient")
    @patch("src.services.service_factory.get_settings")
    def test_get_participant_repository_reuses_client(
        self, mock_get_settings, mock_airtable_client
    ):
        config = AirtableConfig(
            api_key="key",
            base_id="base",
            table_name="Participants",
            table_id=None,
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )
        mock_get_settings.return_value = _build_settings(config)

        client_instance = Mock()
        mock_airtable_client.return_value = client_instance

        repo1 = service_factory.get_participant_repository()
        repo2 = service_factory.get_participant_repository()

        assert mock_airtable_client.call_count == 1
        assert repo1.client is client_instance
        assert repo2.client is client_instance

    @patch("src.services.service_factory.AirtableClient")
    @patch("src.services.service_factory.get_settings")
    def test_reset_creates_new_client(self, mock_get_settings, mock_airtable_client):
        config = AirtableConfig(
            api_key="key",
            base_id="base",
            table_name="Participants",
            table_id=None,
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )
        mock_get_settings.return_value = _build_settings(config)

        first_client = Mock()
        second_client = Mock()
        mock_airtable_client.side_effect = [first_client, second_client]

        repo1 = service_factory.get_participant_repository()

        service_factory.reset_airtable_client_cache()
        repo2 = service_factory.get_participant_repository()

        assert mock_airtable_client.call_count == 2
        assert repo1.client is first_client
        assert repo2.client is second_client

    @patch("src.services.service_factory.AirtableClient")
    @patch("src.services.service_factory.get_settings")
    def test_configuration_change_builds_new_client(
        self, mock_get_settings, mock_airtable_client
    ):
        config_a = AirtableConfig(
            api_key="keyA",
            base_id="baseA",
            table_name="Participants",
            table_id=None,
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )
        config_b = AirtableConfig(
            api_key="keyB",
            base_id="baseB",
            table_name="Participants",
            table_id=None,
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )

        mock_get_settings.side_effect = [
            _build_settings(config_a),
            _build_settings(config_b),
        ]

        first_client = Mock()
        second_client = Mock()
        mock_airtable_client.side_effect = [first_client, second_client]

        repo1 = service_factory.get_participant_repository()
        repo2 = service_factory.get_participant_repository()

        assert mock_airtable_client.call_count == 2
        assert repo1.client is first_client
        assert repo2.client is second_client


class TestTableSpecificClients:
    """Test table-specific client creation and caching."""

    @patch("src.services.service_factory.AirtableClient")
    @patch("src.services.service_factory.get_settings")
    def test_get_airtable_client_for_table_caches_by_type(
        self, mock_get_settings, mock_airtable_client
    ):
        """Test that table-specific clients are cached separately."""
        # Mock settings for different tables
        participants_config = AirtableConfig(
            api_key="key",
            base_id="base",
            table_name="Participants",
            table_id="tbl_participants",
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )
        bible_readers_config = AirtableConfig(
            api_key="key",
            base_id="base",
            table_name="BibleReaders",
            table_id="tbl_bible_readers",
            rate_limit_per_second=5,
            timeout_seconds=30,
            max_retries=3,
            retry_delay_seconds=1.0,
        )

        def get_config_side_effect(table_type=None):
            if table_type == "bible_readers":
                return bible_readers_config
            return participants_config

        mock_settings = Mock()
        mock_settings.get_airtable_config.side_effect = get_config_side_effect
        mock_get_settings.return_value = mock_settings

        participants_client = Mock()
        bible_readers_client = Mock()
        mock_airtable_client.side_effect = [participants_client, bible_readers_client]

        # Get clients for different tables
        client1 = service_factory.get_airtable_client_for_table("participants")
        client2 = service_factory.get_airtable_client_for_table("bible_readers")
        client3 = service_factory.get_airtable_client_for_table("participants")

        # Should create one client per table type
        assert mock_airtable_client.call_count == 2
        assert client1 is participants_client
        assert client2 is bible_readers_client
        assert client3 is participants_client  # Cached


class TestNewRepositoryFactories:
    """Test new repository factory methods."""

    @patch("src.services.service_factory.get_airtable_client_for_table")
    def test_get_bible_readers_repository(self, mock_get_client):
        """Test BibleReaders repository factory method."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        repo = service_factory.get_bible_readers_repository()

        mock_get_client.assert_called_once_with("bible_readers")
        assert repo.client is mock_client

    @patch("src.services.service_factory.get_airtable_client_for_table")
    def test_get_roe_repository(self, mock_get_client):
        """Test ROE repository factory method."""
        mock_client = Mock()
        mock_get_client.return_value = mock_client

        repo = service_factory.get_roe_repository()

        mock_get_client.assert_called_once_with("roe")
        assert repo.client is mock_client


class TestNewExportServiceFactories:
    """Test new export service factory methods."""

    @patch("src.services.service_factory.get_bible_readers_repository")
    @patch("src.services.service_factory.get_participant_repository")
    def test_get_bible_readers_export_service(
        self, mock_get_participant_repo, mock_get_bible_readers_repo
    ):
        """Test BibleReaders export service factory method."""
        mock_bible_readers_repo = Mock()
        mock_participant_repo = Mock()
        mock_get_bible_readers_repo.return_value = mock_bible_readers_repo
        mock_get_participant_repo.return_value = mock_participant_repo

        progress_callback = Mock()
        service = service_factory.get_bible_readers_export_service(progress_callback)

        assert isinstance(service, BibleReadersExportService)
        assert service.bible_readers_repository is mock_bible_readers_repo
        assert service.participant_repository is mock_participant_repo
        assert service.progress_callback is progress_callback

    @patch("src.services.service_factory.get_roe_repository")
    @patch("src.services.service_factory.get_participant_repository")
    def test_get_roe_export_service(
        self, mock_get_participant_repo, mock_get_roe_repo
    ):
        """Test ROE export service factory method."""
        mock_roe_repo = Mock()
        mock_participant_repo = Mock()
        mock_get_roe_repo.return_value = mock_roe_repo
        mock_get_participant_repo.return_value = mock_participant_repo

        progress_callback = Mock()
        service = service_factory.get_roe_export_service(progress_callback)

        assert isinstance(service, ROEExportService)
        assert service.roe_repository is mock_roe_repo
        assert service.participant_repository is mock_participant_repo
        assert service.progress_callback is progress_callback

    @patch("src.services.service_factory.get_bible_readers_repository")
    @patch("src.services.service_factory.get_participant_repository")
    def test_get_bible_readers_export_service_without_callback(
        self, mock_get_participant_repo, mock_get_bible_readers_repo
    ):
        """Test BibleReaders export service factory without progress callback."""
        mock_bible_readers_repo = Mock()
        mock_participant_repo = Mock()
        mock_get_bible_readers_repo.return_value = mock_bible_readers_repo
        mock_get_participant_repo.return_value = mock_participant_repo

        service = service_factory.get_bible_readers_export_service()

        assert isinstance(service, BibleReadersExportService)
        assert service.progress_callback is None

    @patch("src.services.service_factory.get_roe_repository")
    @patch("src.services.service_factory.get_participant_repository")
    def test_get_roe_export_service_without_callback(
        self, mock_get_participant_repo, mock_get_roe_repo
    ):
        """Test ROE export service factory without progress callback."""
        mock_roe_repo = Mock()
        mock_participant_repo = Mock()
        mock_get_roe_repo.return_value = mock_roe_repo
        mock_get_participant_repo.return_value = mock_participant_repo

        service = service_factory.get_roe_export_service()

        assert isinstance(service, ROEExportService)
        assert service.progress_callback is None


class TestSettingsIntegration:
    """Regression tests for real Settings object integration."""

    def test_get_airtable_client_for_table_with_real_settings(self):
        """Test that get_airtable_client_for_table works with real Settings object."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "TELEGRAM_BOT_TOKEN": "test_token",
            "AIRTABLE_BIBLE_READERS_TABLE_ID": "tblBibleReadersTest",
            "AIRTABLE_BIBLE_READERS_TABLE_NAME": "BibleReaders",
            "AIRTABLE_ROE_TABLE_ID": "tblROETest",
            "AIRTABLE_ROE_TABLE_NAME": "ROE",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("src.services.service_factory.get_settings") as mock_get_settings:
                # Use real Settings object instead of mock
                real_settings = Settings()
                mock_get_settings.return_value = real_settings

                # This should not raise TypeError anymore
                client_bible = service_factory.get_airtable_client_for_table("bible_readers")
                assert client_bible is not None

                client_roe = service_factory.get_airtable_client_for_table("roe")
                assert client_roe is not None

                client_participants = service_factory.get_airtable_client_for_table("participants")
                assert client_participants is not None

    def test_export_service_factories_with_real_settings(self):
        """Test that export service factories work with real Settings object."""
        env_vars = {
            "AIRTABLE_API_KEY": "test_key",
            "AIRTABLE_BASE_ID": "test_base",
            "TELEGRAM_BOT_TOKEN": "test_token",
            "AIRTABLE_BIBLE_READERS_TABLE_ID": "tblBibleReadersTest",
            "AIRTABLE_BIBLE_READERS_TABLE_NAME": "BibleReaders",
            "AIRTABLE_ROE_TABLE_ID": "tblROETest",
            "AIRTABLE_ROE_TABLE_NAME": "ROE",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            with patch("src.services.service_factory.get_settings") as mock_get_settings:
                # Use real Settings object
                real_settings = Settings()
                mock_get_settings.return_value = real_settings

                # These should not raise TypeError anymore
                bible_service = service_factory.get_bible_readers_export_service()
                assert isinstance(bible_service, BibleReadersExportService)

                roe_service = service_factory.get_roe_export_service()
                assert isinstance(roe_service, ROEExportService)
