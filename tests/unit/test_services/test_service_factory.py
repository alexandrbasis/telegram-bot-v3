"""Tests for service_factory helper functions."""

from unittest.mock import Mock, patch

import pytest

from src.data.airtable.airtable_client import AirtableConfig
from src.services import service_factory


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
    def test_reset_creates_new_client(
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
