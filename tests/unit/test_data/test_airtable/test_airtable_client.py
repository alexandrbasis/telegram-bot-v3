"""
Unit tests for Airtable client wrapper.

Tests cover:
- Configuration and client initialization
- Rate limiting functionality
- API operation methods (CRUD)
- Error handling and exceptions
- Connection testing
- Bulk operations
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any

from src.data.airtable.airtable_client import (
    AirtableClient,
    AirtableConfig,
    AirtableAPIError,
    RateLimiter,
)


class TestAirtableFieldIDSupport:
    """Test suite for Field ID translation in AirtableClient."""

    @pytest.mark.asyncio
    async def test_translate_fields_to_ids_in_create_data(self):
        """Test that create operations translate field names to Field IDs."""
        # RED phase - this test will fail until we implement Field ID translation in AirtableClient

        config = AirtableConfig(
            api_key="test_api_key", base_id="test_base_id", table_name="TestTable"
        )

        with patch(
            "src.data.airtable.airtable_client.AirtableClient.table"
        ) as mock_table:
            client = AirtableClient(config)

            # Mock the create method
            mock_table.create.return_value = {"id": "rec123", "fields": {}}

            # Test data with field names
            test_data = {
                "FullNameRU": "Иван Иванов",
                "Gender": "M",
                "PaymentAmount": 500,
            }

            # This should internally translate to Field IDs
            await client.create_record(test_data)

            # Verify that the mock was called with Field IDs, not field names
            mock_table.create.assert_called_once()
            call_args = mock_table.create.call_args[0][0]

            # Should have Field IDs as keys
            assert "fldOcpA3JW5MRmR6R" in call_args  # FullNameRU Field ID
            assert "fldOAGXoU0DqqFRmB" in call_args  # Gender Field ID
            assert "fldyP24ZbeGD8nnaZ" in call_args  # PaymentAmount Field ID

            # Should not have field names as keys
            assert "FullNameRU" not in call_args
            assert "Gender" not in call_args
            assert "PaymentAmount" not in call_args

    @pytest.mark.asyncio
    async def test_translate_select_options_to_ids_in_create(self):
        """Test that create operations translate select option values to Option IDs."""
        # RED phase - this test will fail until we implement Option ID translation

        config = AirtableConfig(
            api_key="test_api_key", base_id="test_base_id", table_name="TestTable"
        )

        with patch(
            "src.data.airtable.airtable_client.AirtableClient.table"
        ) as mock_table:
            client = AirtableClient(config)

            mock_table.create.return_value = {"id": "rec123", "fields": {}}

            # Test data with select field values
            test_data = {"Gender": "M", "Size": "L", "Role": "CANDIDATE"}

            await client.create_record(test_data)

            # Verify that select values were translated to Option IDs
            call_args = mock_table.create.call_args[0][0]

            # Should have Option IDs as values for select fields
            assert (
                call_args["fldOAGXoU0DqqFRmB"] == "selZClW1ZQ0574g1o"
            )  # Gender M -> Option ID
            assert (
                call_args["fldZyNgaaa1snp6s7"] == "sel5Zd5JF5WD8Y5ab"
            )  # Size L -> Option ID
            assert (
                call_args["fldetbIGOkKFK0hYq"] == "seleMsONuukNzmB2M"
            )  # Role CANDIDATE -> Option ID

    @pytest.mark.asyncio
    async def test_translate_fields_to_ids_in_update_data(self):
        """Test that update operations translate field names to Field IDs."""
        # RED phase - this test will fail until we implement Field ID translation in update

        config = AirtableConfig(
            api_key="test_api_key", base_id="test_base_id", table_name="TestTable"
        )

        with patch(
            "src.data.airtable.airtable_client.AirtableClient.table"
        ) as mock_table:
            client = AirtableClient(config)

            mock_table.update.return_value = {"id": "rec123", "fields": {}}

            # Test data with field names
            test_data = {"FullNameRU": "Updated Name", "PaymentStatus": "Paid"}

            await client.update_record("rec123", test_data)

            # Verify that the mock was called with Field IDs
            mock_table.update.assert_called_once()
            call_args = mock_table.update.call_args[0]  # (record_id, fields_dict)
            fields_dict = call_args[1]

            # Should have Field IDs as keys and Option IDs for select values
            assert "fldOcpA3JW5MRmR6R" in fields_dict  # FullNameRU Field ID
            assert "fldQzc7m7eO0JzRZf" in fields_dict  # PaymentStatus Field ID
            assert (
                fields_dict["fldQzc7m7eO0JzRZf"] == "sel4ZcXLVs973Gizi"
            )  # Paid Option ID

    @pytest.mark.asyncio
    async def test_field_id_translation_preserves_unknown_fields(self):
        """Test that Field ID translation preserves unknown/custom fields."""
        # RED phase - this test will fail until we implement fallback behavior

        config = AirtableConfig(
            api_key="test_api_key", base_id="test_base_id", table_name="TestTable"
        )

        with patch(
            "src.data.airtable.airtable_client.AirtableClient.table"
        ) as mock_table:
            client = AirtableClient(config)

            mock_table.create.return_value = {"id": "rec123", "fields": {}}

            # Test data with known and unknown fields
            test_data = {
                "FullNameRU": "Test Name",  # Known field -> should be translated
                "CustomField": "Custom Value",  # Unknown field -> should be preserved
                "fldDirectID": "Direct Value",  # Already Field ID -> should be preserved
            }

            await client.create_record(test_data)

            call_args = mock_table.create.call_args[0][0]

            # Known field should be translated
            assert "fldOcpA3JW5MRmR6R" in call_args
            assert call_args["fldOcpA3JW5MRmR6R"] == "Test Name"

            # Unknown fields should be preserved
            assert "CustomField" in call_args
            assert call_args["CustomField"] == "Custom Value"
            assert "fldDirectID" in call_args
            assert call_args["fldDirectID"] == "Direct Value"


class TestAirtableConfig:
    """Test suite for AirtableConfig dataclass."""

    def test_config_creation_minimal(self):
        """Test creating config with minimal required parameters."""
        config = AirtableConfig(api_key="test_api_key", base_id="test_base_id")

        assert config.api_key == "test_api_key"
        assert config.base_id == "test_base_id"
        assert config.table_name == "Participants"  # default
        assert config.rate_limit_per_second == 5  # default
        assert config.timeout_seconds == 30  # default
        assert config.max_retries == 3  # default
        assert config.retry_delay_seconds == 1.0  # default

    def test_config_creation_full(self):
        """Test creating config with all parameters specified."""
        config = AirtableConfig(
            api_key="custom_api_key",
            base_id="custom_base_id",
            table_name="CustomTable",
            rate_limit_per_second=10,
            timeout_seconds=60,
            max_retries=5,
            retry_delay_seconds=2.0,
        )

        assert config.api_key == "custom_api_key"
        assert config.base_id == "custom_base_id"
        assert config.table_name == "CustomTable"
        assert config.rate_limit_per_second == 10
        assert config.timeout_seconds == 60
        assert config.max_retries == 5
        assert config.retry_delay_seconds == 2.0


class TestRateLimiter:
    """Test suite for rate limiting functionality."""

    @pytest.mark.asyncio
    async def test_rate_limiter_creation(self):
        """Test rate limiter initialization."""
        limiter = RateLimiter(requests_per_second=5)

        assert limiter.requests_per_second == 5
        assert limiter.min_interval == 0.2  # 1/5
        assert limiter.last_request_time == 0.0

    @pytest.mark.asyncio
    async def test_rate_limiter_allows_immediate_first_request(self):
        """Test that first request is allowed immediately."""
        limiter = RateLimiter(requests_per_second=5)

        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time

        # First request should be immediate (very small delay acceptable)
        assert elapsed < 0.01

    @pytest.mark.asyncio
    async def test_rate_limiter_enforces_delay(self):
        """Test that rate limiter enforces proper delay between requests."""
        limiter = RateLimiter(requests_per_second=5)  # 0.2 second intervals

        # First request
        await limiter.acquire()

        # Second request should be delayed
        start_time = time.time()
        await limiter.acquire()
        elapsed = time.time() - start_time

        # Should wait approximately 0.2 seconds
        assert 0.18 <= elapsed <= 0.25  # Allow some timing tolerance

    @pytest.mark.asyncio
    async def test_rate_limiter_concurrent_requests(self):
        """Test rate limiter with concurrent requests."""
        limiter = RateLimiter(requests_per_second=10)  # 0.1 second intervals

        async def make_request(request_id):
            start_time = time.time()
            await limiter.acquire()
            return request_id, time.time() - start_time

        # Start multiple concurrent requests
        tasks = [make_request(i) for i in range(3)]
        results = await asyncio.gather(*tasks)

        # Results should be ordered by completion time due to rate limiting
        times = [result[1] for result in results]

        # First request immediate, subsequent requests delayed
        assert times[0] < 0.01  # First request immediate
        assert 0.08 <= times[1] <= 0.15  # Second request ~0.1s delay
        assert 0.18 <= times[2] <= 0.25  # Third request ~0.2s delay


class TestAirtableAPIError:
    """Test suite for AirtableAPIError exception."""

    def test_api_error_basic(self):
        """Test basic API error creation."""
        error = AirtableAPIError("Test error message")

        assert str(error) == "Test error message"
        assert error.status_code is None
        assert error.original_error is None

    def test_api_error_with_status_code(self):
        """Test API error with status code."""
        error = AirtableAPIError("API error", status_code=422)

        assert str(error) == "API error"
        assert error.status_code == 422
        assert error.original_error is None

    def test_api_error_with_original_exception(self):
        """Test API error wrapping original exception."""
        original = ValueError("Original error")
        error = AirtableAPIError("Wrapper error", original_error=original)

        assert str(error) == "Wrapper error"
        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)

    def test_api_error_inheritance(self):
        """Test that AirtableAPIError inherits from RepositoryError."""
        from src.data.repositories.participant_repository import RepositoryError

        error = AirtableAPIError("Test")

        assert isinstance(error, RepositoryError)
        assert isinstance(error, Exception)


@pytest.fixture
def mock_config():
    """Fixture providing a test configuration."""
    return AirtableConfig(
        api_key="test_api_key",
        base_id="test_base_id",
        table_name="TestTable",
        rate_limit_per_second=100,  # Fast for testing
    )


@pytest.fixture
def mock_table():
    """Fixture providing a mock Airtable table."""
    table = Mock()
    table.schema.return_value = {
        "fields": [{"name": "TestField", "type": "singleLineText"}]
    }
    table.create.return_value = {"id": "rec123", "fields": {"TestField": "Test Value"}}
    table.get.return_value = {"id": "rec123", "fields": {"TestField": "Test Value"}}
    table.update.return_value = {
        "id": "rec123",
        "fields": {"TestField": "Updated Value"},
    }
    table.delete.return_value = True
    table.all.return_value = [
        {"id": "rec123", "fields": {"TestField": "Value 1"}},
        {"id": "rec456", "fields": {"TestField": "Value 2"}},
    ]
    table.batch_create.return_value = [
        {"id": "rec123", "fields": {"TestField": "Batch 1"}},
        {"id": "rec456", "fields": {"TestField": "Batch 2"}},
    ]
    table.batch_update.return_value = [
        {"id": "rec123", "fields": {"TestField": "Updated 1"}},
        {"id": "rec456", "fields": {"TestField": "Updated 2"}},
    ]
    return table


class TestAirtableClient:
    """Test suite for AirtableClient functionality."""

    def test_client_initialization(self, mock_config):
        """Test client initialization with configuration."""
        client = AirtableClient(mock_config)

        assert client.config == mock_config
        assert isinstance(client.rate_limiter, RateLimiter)
        assert client.rate_limiter.requests_per_second == 100
        assert client._api is None
        assert client._table is None

    @patch("src.data.airtable.airtable_client.Api")
    def test_api_property_lazy_initialization(self, mock_api_class, mock_config):
        """Test that API is initialized lazily on first access."""
        mock_api_instance = Mock()
        mock_api_class.return_value = mock_api_instance

        client = AirtableClient(mock_config)
        assert client._api is None

        # First access should initialize
        api = client.api
        assert api is mock_api_instance
        assert client._api is mock_api_instance
        mock_api_class.assert_called_once_with("test_api_key")

        # Second access should return cached instance
        api2 = client.api
        assert api2 is mock_api_instance
        assert mock_api_class.call_count == 1

    @patch("src.data.airtable.airtable_client.Api")
    def test_table_property_lazy_initialization(
        self, mock_api_class, mock_config, mock_table
    ):
        """Test that table is initialized lazily on first access."""
        mock_api_instance = Mock()
        mock_api_instance.table.return_value = mock_table
        mock_api_class.return_value = mock_api_instance

        client = AirtableClient(mock_config)
        assert client._table is None

        # First access should initialize
        table = client.table
        assert table is mock_table
        assert client._table is mock_table
        mock_api_instance.table.assert_called_once_with("test_base_id", "TestTable")

        # Second access should return cached instance
        table2 = client.table
        assert table2 is mock_table
        assert mock_api_instance.table.call_count == 1


class TestAirtableClientOperations:
    """Test suite for Airtable client CRUD operations."""

    @pytest.fixture
    def client_with_mock_table(self, mock_config, mock_table):
        """Fixture providing client with mocked table."""
        with patch("src.data.airtable.airtable_client.Api") as mock_api_class:
            mock_api_instance = Mock()
            mock_api_instance.table.return_value = mock_table
            mock_api_class.return_value = mock_api_instance

            client = AirtableClient(mock_config)
            # Pre-initialize the cached properties to use our mocks
            client._api = mock_api_instance
            client._table = mock_table
            return client, mock_table

    @pytest.mark.asyncio
    async def test_test_connection_success(self, client_with_mock_table):
        """Test successful connection test."""
        client, mock_table = client_with_mock_table

        result = await client.test_connection()

        assert result is True
        mock_table.schema.assert_called_once()

    @pytest.mark.asyncio
    async def test_test_connection_failure(self, client_with_mock_table):
        """Test connection test failure."""
        client, mock_table = client_with_mock_table
        mock_table.schema.side_effect = Exception("Connection failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.test_connection()

        assert "connection test failed" in str(exc_info.value).lower()
        assert isinstance(exc_info.value.original_error, Exception)

    @pytest.mark.asyncio
    async def test_create_record_success(self, client_with_mock_table):
        """Test successful record creation."""
        client, mock_table = client_with_mock_table
        fields = {"TestField": "Test Value"}

        result = await client.create_record(fields)

        assert result == {"id": "rec123", "fields": {"TestField": "Test Value"}}
        mock_table.create.assert_called_once_with(fields)

    @pytest.mark.asyncio
    async def test_create_record_failure(self, client_with_mock_table):
        """Test record creation failure."""
        client, mock_table = client_with_mock_table
        mock_table.create.side_effect = Exception("Creation failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.create_record({"TestField": "Value"})

        assert "failed to create record" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_get_record_success(self, client_with_mock_table):
        """Test successful record retrieval."""
        client, mock_table = client_with_mock_table

        result = await client.get_record("rec123")

        assert result == {"id": "rec123", "fields": {"TestField": "Test Value"}}
        mock_table.get.assert_called_once_with("rec123")

    @pytest.mark.asyncio
    async def test_get_record_not_found(self, client_with_mock_table):
        """Test record not found scenario."""
        client, mock_table = client_with_mock_table
        mock_table.get.side_effect = Exception("Record not found")

        result = await client.get_record("nonexistent")

        assert result is None
        mock_table.get.assert_called_once_with("nonexistent")

    @pytest.mark.asyncio
    async def test_get_record_other_error(self, client_with_mock_table):
        """Test record retrieval with non-404 error."""
        client, mock_table = client_with_mock_table
        mock_table.get.side_effect = Exception("Server error")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.get_record("rec123")

        assert "failed to get record" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_update_record_success(self, client_with_mock_table):
        """Test successful record update."""
        client, mock_table = client_with_mock_table
        fields = {"TestField": "Updated Value"}

        result = await client.update_record("rec123", fields)

        assert result == {"id": "rec123", "fields": {"TestField": "Updated Value"}}
        mock_table.update.assert_called_once_with("rec123", fields)

    @pytest.mark.asyncio
    async def test_update_record_failure(self, client_with_mock_table):
        """Test record update failure."""
        client, mock_table = client_with_mock_table
        mock_table.update.side_effect = Exception("Update failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.update_record("rec123", {"TestField": "Value"})

        assert "failed to update record" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_delete_record_success(self, client_with_mock_table):
        """Test successful record deletion."""
        client, mock_table = client_with_mock_table

        result = await client.delete_record("rec123")

        assert result is True
        mock_table.delete.assert_called_once_with("rec123")

    @pytest.mark.asyncio
    async def test_delete_record_failure(self, client_with_mock_table):
        """Test record deletion failure."""
        client, mock_table = client_with_mock_table
        mock_table.delete.side_effect = Exception("Deletion failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.delete_record("rec123")

        assert "failed to delete record" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_list_records_success(self, client_with_mock_table):
        """Test successful record listing."""
        client, mock_table = client_with_mock_table

        result = await client.list_records()

        expected = [
            {"id": "rec123", "fields": {"TestField": "Value 1"}},
            {"id": "rec456", "fields": {"TestField": "Value 2"}},
        ]
        assert result == expected
        mock_table.all.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_list_records_with_parameters(self, client_with_mock_table):
        """Test record listing with various parameters."""
        client, mock_table = client_with_mock_table

        await client.list_records(
            formula="TestField = 'Value'",
            sort=["-CreatedAt"],
            fields=["TestField"],
            max_records=10,
            view="MyView",
        )

        mock_table.all.assert_called_once_with(
            formula="TestField = 'Value'",
            sort=["-CreatedAt"],
            fields=["TestField"],
            max_records=10,
            view="MyView",
        )

    @pytest.mark.asyncio
    async def test_list_records_failure(self, client_with_mock_table):
        """Test record listing failure."""
        client, mock_table = client_with_mock_table
        mock_table.all.side_effect = Exception("Listing failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.list_records()

        assert "failed to list records" in str(exc_info.value).lower()


class TestAirtableClientBulkOperations:
    """Test suite for bulk operations."""

    @pytest.fixture
    def client_with_mock_table(self, mock_config, mock_table):
        """Fixture providing client with mocked table."""
        with patch("src.data.airtable.airtable_client.Api") as mock_api_class:
            mock_api_instance = Mock()
            mock_api_instance.table.return_value = mock_table
            mock_api_class.return_value = mock_api_instance

            client = AirtableClient(mock_config)
            # Pre-initialize the cached properties to use our mocks
            client._api = mock_api_instance
            client._table = mock_table
            return client, mock_table

    @pytest.mark.asyncio
    async def test_bulk_create_empty_list(self, client_with_mock_table):
        """Test bulk create with empty list."""
        client, mock_table = client_with_mock_table

        result = await client.bulk_create([])

        assert result == []
        mock_table.batch_create.assert_not_called()

    @pytest.mark.asyncio
    async def test_bulk_create_single_batch(self, client_with_mock_table):
        """Test bulk create with single batch."""
        client, mock_table = client_with_mock_table
        records = [{"TestField": "Value 1"}, {"TestField": "Value 2"}]

        result = await client.bulk_create(records)

        expected = [
            {"id": "rec123", "fields": {"TestField": "Batch 1"}},
            {"id": "rec456", "fields": {"TestField": "Batch 2"}},
        ]
        assert result == expected
        mock_table.batch_create.assert_called_once_with(records)

    @pytest.mark.asyncio
    async def test_bulk_create_multiple_batches(self, client_with_mock_table):
        """Test bulk create with multiple batches."""
        client, mock_table = client_with_mock_table

        # Create 15 records (should be split into 2 batches of 10 and 5)
        records = [{"TestField": f"Value {i}"} for i in range(15)]

        result = await client.bulk_create(records)

        # Should result in 4 created records (2 batches × 2 records per batch)
        assert len(result) == 4
        assert mock_table.batch_create.call_count == 2

        # Check batch sizes
        first_call = mock_table.batch_create.call_args_list[0][0][0]
        second_call = mock_table.batch_create.call_args_list[1][0][0]
        assert len(first_call) == 10
        assert len(second_call) == 5

    @pytest.mark.asyncio
    async def test_bulk_create_failure(self, client_with_mock_table):
        """Test bulk create failure."""
        client, mock_table = client_with_mock_table
        mock_table.batch_create.side_effect = Exception("Batch creation failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.bulk_create([{"TestField": "Value"}])

        assert "failed to create batch" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_bulk_update_success(self, client_with_mock_table):
        """Test successful bulk update."""
        client, mock_table = client_with_mock_table
        updates = [
            {"id": "rec123", "fields": {"TestField": "Updated 1"}},
            {"id": "rec456", "fields": {"TestField": "Updated 2"}},
        ]

        result = await client.bulk_update(updates)

        expected = [
            {"id": "rec123", "fields": {"TestField": "Updated 1"}},
            {"id": "rec456", "fields": {"TestField": "Updated 2"}},
        ]
        assert result == expected
        mock_table.batch_update.assert_called_once_with(updates)

    @pytest.mark.asyncio
    async def test_bulk_update_empty_list(self, client_with_mock_table):
        """Test bulk update with empty list."""
        client, mock_table = client_with_mock_table

        result = await client.bulk_update([])

        assert result == []
        mock_table.batch_update.assert_not_called()


class TestAirtableClientSearchOperations:
    """Test suite for search operations."""

    @pytest.fixture
    def client_with_mock_table(self, mock_config, mock_table):
        """Fixture providing client with mocked table."""
        with patch("src.data.airtable.airtable_client.Api") as mock_api_class:
            mock_api_instance = Mock()
            mock_api_instance.table.return_value = mock_table
            mock_api_class.return_value = mock_api_instance

            client = AirtableClient(mock_config)
            # Pre-initialize the cached properties to use our mocks
            client._api = mock_api_instance
            client._table = mock_table
            return client, mock_table

    @pytest.mark.asyncio
    async def test_search_by_field_string(self, client_with_mock_table):
        """Test search by field with string value."""
        client, mock_table = client_with_mock_table

        await client.search_by_field("TestField", "Test Value")

        # String values should be quoted in formula
        expected_formula = "{TestField} = 'Test Value'"
        mock_table.all.assert_called_once_with(formula=expected_formula)

    @pytest.mark.asyncio
    async def test_search_by_field_number(self, client_with_mock_table):
        """Test search by field with numeric value."""
        client, mock_table = client_with_mock_table

        await client.search_by_field("NumberField", 42)

        # Numeric values should not be quoted
        expected_formula = "{NumberField} = 42"
        mock_table.all.assert_called_once_with(formula=expected_formula)

    @pytest.mark.asyncio
    async def test_search_by_field_string_with_quotes(self, client_with_mock_table):
        """Test search by field with string value containing single quotes."""
        client, mock_table = client_with_mock_table

        await client.search_by_field("NameField", "O'Connor")

        # Single quotes should be escaped by doubling them
        expected_formula = "{NameField} = 'O''Connor'"
        mock_table.all.assert_called_once_with(formula=expected_formula)

    @pytest.mark.asyncio
    async def test_search_by_field_string_with_multiple_quotes(
        self, client_with_mock_table
    ):
        """Test search by field with string value containing multiple single quotes."""
        client, mock_table = client_with_mock_table

        await client.search_by_field("CommentField", "Can't find John's file")

        # All single quotes should be escaped by doubling them
        expected_formula = "{CommentField} = 'Can''t find John''s file'"
        mock_table.all.assert_called_once_with(formula=expected_formula)

    @pytest.mark.asyncio
    async def test_search_by_formula(self, client_with_mock_table):
        """Test search by custom formula."""
        client, mock_table = client_with_mock_table
        custom_formula = "AND({Field1} = 'Value', {Field2} > 10)"

        await client.search_by_formula(custom_formula)

        mock_table.all.assert_called_once_with(formula=custom_formula)

    @pytest.mark.asyncio
    async def test_get_schema_success(self, client_with_mock_table):
        """Test successful schema retrieval."""
        client, mock_table = client_with_mock_table

        result = await client.get_schema()

        expected = {"fields": [{"name": "TestField", "type": "singleLineText"}]}
        assert result == expected
        mock_table.schema.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_schema_failure(self, client_with_mock_table):
        """Test schema retrieval failure."""
        client, mock_table = client_with_mock_table
        mock_table.schema.side_effect = Exception("Schema retrieval failed")

        with pytest.raises(AirtableAPIError) as exc_info:
            await client.get_schema()

        assert "failed to get schema" in str(exc_info.value).lower()
