"""
Airtable implementation of UserAccessRepository.

Provides Airtable-backed persistence for user access requests with
field mapping, status filtering, and audit metadata support.
"""

from datetime import datetime, timezone
from typing import List, Optional, Tuple

from src.config.field_mappings import BotAccessRequestsFieldMapping
from src.data.repositories.user_access_repository import UserAccessRepository
from src.models.user_access_request import (
    AccessLevel,
    AccessRequestStatus,
    UserAccessRequest,
)


class AirtableUserAccessRepository(UserAccessRepository):
    """
    Airtable implementation of user access request repository.

    Provides CRUD operations and status-based queries using the Airtable API
    with proper field mapping and option ID translation.
    """

    def __init__(
        self,
        airtable_client,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ):
        """
        Initialize repository with Airtable client and optional table configuration.

        Args:
            airtable_client: Configured Airtable client instance
            table_name: Name of the access requests table (defaults to field mapping)
            table_id: ID of the access requests table (defaults to field mapping)
        """
        self.client = airtable_client
        self.table_name = table_name or BotAccessRequestsFieldMapping.TABLE_NAME
        self.table_id = table_id or BotAccessRequestsFieldMapping.TABLE_ID

    async def create_request(self, request: UserAccessRequest) -> UserAccessRequest:
        """Create a new access request in Airtable."""
        # Convert model to Airtable field format
        airtable_data = self._model_to_airtable_data(request)

        # Translate field names to field IDs for API call
        field_id_data = BotAccessRequestsFieldMapping.translate_fields_to_ids(
            airtable_data
        )

        # Create record in Airtable
        response = await self.client.create_record(
            table_name=self.table_name, data=field_id_data
        )

        # Convert response back to model
        return self._airtable_record_to_model(response)

    async def get_request_by_user_id(
        self, telegram_user_id: int
    ) -> Optional[UserAccessRequest]:
        """Retrieve access request by Telegram user ID."""
        # Build filter formula for Telegram user ID lookup
        user_id_field_id = BotAccessRequestsFieldMapping.get_field_id("TelegramUserId")
        filter_formula = f"{{{user_id_field_id}}} = {telegram_user_id}"

        # Query Airtable
        records = await self.client.get_records(
            table_name=self.table_name, filter_formula=filter_formula, max_records=1
        )

        if not records:
            return None

        return self._airtable_record_to_model(records[0])

    async def list_requests_by_status(
        self,
        status: AccessRequestStatus,
        limit: Optional[int] = None,
        offset: Optional[str] = None,
    ) -> Tuple[List[UserAccessRequest], Optional[str]]:
        """List access requests filtered by status."""
        # Build filter formula for status
        status_field_id = BotAccessRequestsFieldMapping.get_field_id("Status")
        status_option_id = BotAccessRequestsFieldMapping.get_option_id(
            "Status", status.value
        )
        filter_formula = f"{{{status_field_id}}} = '{status_option_id}'"

        # Query Airtable with pagination
        kwargs = {
            "table_name": self.table_name,
            "filter_formula": filter_formula,
        }

        if limit is not None:
            kwargs["max_records"] = limit

        if offset is not None:
            kwargs["offset"] = offset

        response = await self.client.get_records(**kwargs)

        # Extract records from response and convert to models
        records = response.get("records", [])
        next_offset = response.get("offset")

        return (
            [self._airtable_record_to_model(record) for record in records],
            next_offset
        )

    async def approve_request(
        self, request: UserAccessRequest, access_level: AccessLevel, reviewed_by: str
    ) -> UserAccessRequest:
        """Approve an access request with specified access level."""
        if not request.record_id:
            raise ValueError("Cannot approve request without record_id")

        # Prepare update data
        update_data = {
            "Status": "Approved",
            "AccessLevel": access_level.value,
            "ReviewedAt": datetime.now(timezone.utc).isoformat(),
            "ReviewedBy": reviewed_by,
        }

        # Translate to field IDs
        field_id_data = BotAccessRequestsFieldMapping.translate_fields_to_ids(
            update_data
        )

        # Update record in Airtable
        response = await self.client.update_record(
            record_id=request.record_id, data=field_id_data
        )

        return self._airtable_record_to_model(response)

    async def deny_request(
        self, request: UserAccessRequest, reviewed_by: str
    ) -> UserAccessRequest:
        """Deny an access request."""
        if not request.record_id:
            raise ValueError("Cannot deny request without record_id")

        # Prepare update data
        update_data = {
            "Status": "Denied",
            "ReviewedAt": datetime.now(timezone.utc).isoformat(),
            "ReviewedBy": reviewed_by,
        }

        # Translate to field IDs
        field_id_data = BotAccessRequestsFieldMapping.translate_fields_to_ids(
            update_data
        )

        # Update record in Airtable
        response = await self.client.update_record(
            record_id=request.record_id, data=field_id_data
        )

        return self._airtable_record_to_model(response)

    async def update_request(self, request: UserAccessRequest) -> UserAccessRequest:
        """Update an existing access request."""
        if not request.record_id:
            raise ValueError("Cannot update request without record_id")

        # Convert model to Airtable field format
        airtable_data = self._model_to_airtable_data(request, exclude_record_id=True)

        # Translate field names to field IDs
        field_id_data = BotAccessRequestsFieldMapping.translate_fields_to_ids(
            airtable_data
        )

        # Update record in Airtable
        response = await self.client.update_record(
            record_id=request.record_id, data=field_id_data
        )

        return self._airtable_record_to_model(response)

    def _model_to_airtable_data(
        self, request: UserAccessRequest, exclude_record_id: bool = False
    ) -> dict:
        """Convert UserAccessRequest model to Airtable field format."""
        data = {}

        # Map all model fields to Airtable field names
        field_mappings = [
            ("telegram_user_id", "TelegramUserId"),
            ("telegram_username", "TelegramUsername"),
            ("status", "Status"),
            ("access_level", "AccessLevel"),
            ("requested_at", "RequestedAt"),
            ("reviewed_at", "ReviewedAt"),
            ("reviewed_by", "ReviewedBy"),
        ]

        for model_field, airtable_field in field_mappings:
            value = getattr(request, model_field)
            if value is not None:
                # Handle enum values with proper mapping
                if airtable_field == "Status" and isinstance(value, str):
                    # Map enum values to Airtable display values
                    status_mapping = {
                        "PENDING": "Pending",
                        "APPROVED": "Approved",
                        "DENIED": "Denied",
                    }
                    value = status_mapping.get(value, value)
                elif hasattr(value, "value"):
                    value = value.value
                # Handle datetime values
                elif isinstance(value, datetime):
                    value = value.isoformat()

                data[airtable_field] = value

        return data

    def _airtable_record_to_model(self, record: dict) -> UserAccessRequest:
        """Convert Airtable record to UserAccessRequest model."""
        fields = record.get("fields", {})

        # Extract record ID
        record_id = record.get("id")

        # Map Airtable field IDs back to values
        field_id_mappings = BotAccessRequestsFieldMapping.AIRTABLE_FIELD_IDS

        # Extract values using field IDs
        telegram_user_id = None
        telegram_username = None
        status = AccessRequestStatus.PENDING
        access_level = AccessLevel.VIEWER
        requested_at = None
        reviewed_at = None
        reviewed_by = None

        for airtable_field, field_id in field_id_mappings.items():
            if field_id in fields:
                value = fields[field_id]

                if airtable_field == "TelegramUserId":
                    telegram_user_id = int(value) if value is not None else None
                elif airtable_field == "TelegramUsername":
                    telegram_username = value
                elif airtable_field == "Status":
                    # Map from display value to enum
                    status_mapping = {
                        "Pending": AccessRequestStatus.PENDING,
                        "Approved": AccessRequestStatus.APPROVED,
                        "Denied": AccessRequestStatus.DENIED,
                    }
                    status = status_mapping.get(value, AccessRequestStatus.PENDING)
                elif airtable_field == "AccessLevel":
                    try:
                        access_level = AccessLevel(value)
                    except ValueError:
                        access_level = AccessLevel.VIEWER
                elif airtable_field == "RequestedAt":
                    if value:
                        requested_at = datetime.fromisoformat(
                            value.replace("Z", "+00:00")
                        )
                elif airtable_field == "ReviewedAt":
                    if value:
                        reviewed_at = datetime.fromisoformat(
                            value.replace("Z", "+00:00")
                        )
                elif airtable_field == "ReviewedBy":
                    reviewed_by = value

        # Create and return model instance
        return UserAccessRequest(
            record_id=record_id,
            telegram_user_id=telegram_user_id,
            telegram_username=telegram_username,
            status=status,
            access_level=access_level,
            requested_at=requested_at or datetime.now(timezone.utc),
            reviewed_at=reviewed_at,
            reviewed_by=reviewed_by,
        )
