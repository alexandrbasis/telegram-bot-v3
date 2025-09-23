"""
Integration tests for Airtable pagination functionality.

Tests the complete pagination flow from client through repository to service layer,
ensuring offset tokens are properly handled and backward navigation works.
"""

from unittest.mock import AsyncMock, Mock

import pytest

from src.data.airtable.airtable_client import AirtableClient, AirtableConfig
from src.data.airtable.airtable_user_access_repo import AirtableUserAccessRepository
from src.models.user_access_request import AccessRequestStatus, UserAccessRequest
from src.services.access_request_service import AccessRequestService


class TestPaginationIntegration:
    """Integration tests for pagination across all layers."""

    @pytest.fixture
    def mock_api(self):
        """Create mock API with pagination responses."""
        mock_api = Mock()
        mock_api.request = Mock()  # Use regular Mock, not AsyncMock
        return mock_api

    @pytest.fixture
    def client_with_pagination(self, mock_api):
        """Create client with mocked pagination responses."""
        config = AirtableConfig(
            api_key="test_key",
            base_id="test_base",
            table_name="AccessRequests",
        )
        client = AirtableClient(config)
        client._api = mock_api
        return client, mock_api

    @pytest.fixture
    def sample_page_responses(self):
        """Sample paginated responses."""
        return {
            "page_1": {
                "records": [
                    {
                        "id": "rec1",
                        "fields": {
                            "fldeiF3gxg4fZMirc": 111111111,
                            "fld1RzNGWTGl8fSE4": "user1",
                            "fldcuRa8qeUDKY3hN": "Pending",
                            "fldRBCoHwrJ87hdjr": "VIEWER",
                        },
                    },
                    {
                        "id": "rec2",
                        "fields": {
                            "fldeiF3gxg4fZMirc": 222222222,
                            "fld1RzNGWTGl8fSE4": "user2",
                            "fldcuRa8qeUDKY3hN": "Pending",
                            "fldRBCoHwrJ87hdjr": "VIEWER",
                        },
                    },
                ],
                "offset": "page2_token",
            },
            "page_2": {
                "records": [
                    {
                        "id": "rec3",
                        "fields": {
                            "fldeiF3gxg4fZMirc": 333333333,
                            "fld1RzNGWTGl8fSE4": "user3",
                            "fldcuRa8qeUDKY3hN": "Pending",
                            "fldRBCoHwrJ87hdjr": "VIEWER",
                        },
                    },
                ],
                "offset": None,  # No more pages
            },
        }

    async def test_pagination_flow_forward_and_backward(
        self, client_with_pagination, sample_page_responses
    ):
        """Test complete pagination flow: forward to page 2, then back to page 1."""
        client, mock_api = client_with_pagination

        # Setup repository and service
        repository = AirtableUserAccessRepository(client, "AccessRequests")
        service = AccessRequestService(repository)

        # Mock API responses for different pages
        def mock_request(method, url, params=None):
            if params and params.get("offset") == "page2_token":
                return sample_page_responses["page_2"]
            else:
                return sample_page_responses["page_1"]

        mock_api.request.side_effect = mock_request

        # Test Page 1 (no offset)
        requests_page1, offset_token = (
            await service.get_pending_requests_with_pagination(limit=2, offset=None)
        )

        assert len(requests_page1) == 2
        assert requests_page1[0].telegram_user_id == 111111111
        assert requests_page1[1].telegram_user_id == 222222222
        assert offset_token == "page2_token"

        # Test Page 2 (with offset token)
        requests_page2, next_offset = (
            await service.get_pending_requests_with_pagination(
                limit=2, offset=offset_token
            )
        )

        assert len(requests_page2) == 1
        assert requests_page2[0].telegram_user_id == 333333333
        assert next_offset is None  # No more pages

        # Test backward navigation - should get page 1 again
        requests_back_page1, back_offset = (
            await service.get_pending_requests_with_pagination(limit=2, offset=None)
        )

        assert len(requests_back_page1) == 2
        assert requests_back_page1[0].telegram_user_id == 111111111
        assert requests_back_page1[1].telegram_user_id == 222222222
        assert back_offset == "page2_token"

        # Verify API calls were made with correct parameters
        assert mock_api.request.call_count == 3

        # Verify first call (page 1)
        first_call = mock_api.request.call_args_list[0]
        assert first_call[0][0] == "GET"  # Check method
        assert first_call[1]["params"]["maxRecords"] == 2
        assert "offset" not in first_call[1]["params"]

        # Verify second call (page 2)
        second_call = mock_api.request.call_args_list[1]
        assert second_call[0][0] == "GET"  # Check method
        assert second_call[1]["params"]["offset"] == "page2_token"

        # Verify third call (back to page 1)
        third_call = mock_api.request.call_args_list[2]
        assert third_call[0][0] == "GET"  # Check method
        assert "offset" not in third_call[1]["params"]

    async def test_pagination_with_filtering(
        self, client_with_pagination, sample_page_responses
    ):
        """Test pagination works correctly with filtering."""
        client, mock_api = client_with_pagination
        repository = AirtableUserAccessRepository(client, "AccessRequests")

        mock_api.request.return_value = sample_page_responses["page_1"]

        # Test with status filtering
        requests, offset = await repository.list_requests_by_status(
            AccessRequestStatus.PENDING, limit=2, offset=None
        )

        assert len(requests) == 2
        assert offset == "page2_token"

        # Verify filter was applied in API call
        call_args = mock_api.request.call_args
        assert "filterByFormula" in call_args[1]["params"]
        assert "Pending" in call_args[1]["params"]["filterByFormula"]

    async def test_pagination_edge_cases(self, client_with_pagination):
        """Test edge cases in pagination."""
        client, mock_api = client_with_pagination
        repository = AirtableUserAccessRepository(client, "AccessRequests")

        # Test empty results
        mock_api.request.return_value = {"records": [], "offset": None}

        requests, offset = await repository.list_requests_by_status(
            AccessRequestStatus.PENDING, limit=5, offset=None
        )

        assert len(requests) == 0
        assert offset is None

        # Test single page with no next offset
        mock_api.request.return_value = {
            "records": [
                {
                    "id": "rec1",
                    "fields": {
                        "fldeiF3gxg4fZMirc": 111111111,
                        "fld1RzNGWTGl8fSE4": "user1",
                        "fldcuRa8qeUDKY3hN": "Pending",
                        "fldRBCoHwrJ87hdjr": "VIEWER",
                    },
                }
            ],
            "offset": None,
        }

        requests, offset = await repository.list_requests_by_status(
            AccessRequestStatus.PENDING, limit=5, offset=None
        )

        assert len(requests) == 1
        assert offset is None

    async def test_api_parameter_mapping(self, client_with_pagination):
        """Test that parameters are correctly mapped to Airtable API format."""
        client, mock_api = client_with_pagination
        mock_api.request.return_value = {"records": [], "offset": None}

        await client.list_records(
            formula="test_formula",
            sort=["-CreatedTime"],
            fields=["Name", "Status"],
            max_records=10,
            view="MyView",
            page_size=5,
            offset="test_offset",
        )

        call_args = mock_api.request.call_args
        params = call_args[1]["params"]

        # Verify parameter mapping
        assert params["filterByFormula"] == "test_formula"
        assert params["sort"] == ["-CreatedTime"]
        assert params["fields"] == ["Name", "Status"]
        assert params["maxRecords"] == 10
        assert params["view"] == "MyView"
        assert params["pageSize"] == 5
        assert params["offset"] == "test_offset"
