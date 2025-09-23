"""
Airtable API client wrapper with authentication, rate limiting, and error handling.

This client provides a low-level interface to the Airtable API with proper
error handling, rate limiting, and connection management.
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import httpx
from pyairtable import Api, Table
from pyairtable.api.types import RecordDict

from src.config.field_mappings import (  # Original participant mapping
    AirtableFieldMapping,
)
from src.data.repositories.participant_repository import RepositoryError

logger = logging.getLogger(__name__)


@dataclass
class AirtableConfig:
    """Configuration for Airtable API connection."""

    api_key: str
    base_id: str
    table_name: str = "Participants"
    table_id: Optional[str] = None
    rate_limit_per_second: int = 5
    timeout_seconds: int = 30
    max_retries: int = 3
    retry_delay_seconds: float = 1.0


class RateLimiter:
    """Rate limiter for Airtable API requests."""

    def __init__(self, requests_per_second: int = 5):
        self.requests_per_second = requests_per_second
        self.min_interval = 1.0 / requests_per_second
        self.last_request_time = 0.0
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Wait until next request is allowed per rate limit."""
        async with self._lock:
            current_time = time.time()
            time_since_last = current_time - self.last_request_time

            if time_since_last < self.min_interval:
                sleep_time = self.min_interval - time_since_last
                await asyncio.sleep(sleep_time)

            self.last_request_time = time.time()


class AirtableAPIError(RepositoryError):
    """Exception for Airtable API specific errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        original_error: Optional[Exception] = None,
    ):
        super().__init__(message, original_error)
        self.status_code = status_code


class AirtableClient:
    """
    Airtable API client with authentication, rate limiting, and error handling.

    Provides low-level access to Airtable API operations with proper error
    handling and rate limiting according to Airtable's API constraints.
    """

    def __init__(self, config: AirtableConfig):
        self.config = config
        self.rate_limiter = RateLimiter(config.rate_limit_per_second)
        self._api: Optional[Api] = None
        self._table: Optional[Table] = None
        self._table_cache: Dict[str, Table] = {}

        # Connection validation will be done on first request
        logger.info(
            f"Initialized Airtable client for base {config.base_id}, table {config.table_name}"
        )

    @property
    def api(self) -> Api:
        """Get or create Airtable API instance."""
        if self._api is None:
            self._api = Api(self.config.api_key)
        return self._api

    @property
    def table(self) -> Table:
        """Get or create Airtable table instance."""
        if self._table is None:
            # Use table_id if available, otherwise fall back to table_name
            table_identifier = (
                self.config.table_id if self.config.table_id else self.config.table_name
            )
            self._table = self.api.table(self.config.base_id, table_identifier)
            self._table_cache[table_identifier] = self._table
        return self._table

    def _get_table(
        self,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> Table:
        """Return the appropriate Airtable table instance, caching by identifier."""

        if not table_name and not table_id:
            return self.table

        identifier = table_id if table_id else table_name
        if identifier is None:
            identifier = (
                self.config.table_id if self.config.table_id else self.config.table_name
            )

        cached = self._table_cache.get(identifier)
        if cached is not None:
            return cached

        table_instance = self.api.table(self.config.base_id, identifier)
        self._table_cache[identifier] = table_instance
        return table_instance

    def _translate_fields_for_api(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """
        Translate field names to Field IDs and option values to Option IDs for API calls.

        Args:
            fields: Dictionary with field names and values

        Returns:
            Dictionary with Field IDs as keys and Option IDs for select values
        """
        # First translate field names to Field IDs
        translated_fields = AirtableFieldMapping.translate_fields_to_ids(fields)

        # Then translate select option values to Option IDs
        for field_name, value in fields.items():
            field_id = AirtableFieldMapping.get_field_id(field_name)
            key = field_id if field_id else field_name

            if isinstance(value, str):
                # Try to translate as select option
                option_id = AirtableFieldMapping.translate_option_to_id(
                    field_name, value
                )
                translated_fields[key] = option_id

        return translated_fields

    async def test_connection(self) -> bool:
        """
        Test the connection to Airtable API.

        Returns:
            True if connection is successful

        Raises:
            AirtableAPIError: If connection fails
        """
        try:
            await self.rate_limiter.acquire()

            # Try to get schema information (lightweight operation)
            await asyncio.to_thread(self.table.schema)

            logger.info("Airtable connection test successful")
            return True

        except Exception as e:
            error_msg = f"Airtable connection test failed: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def create_record(
        self,
        fields: Optional[Dict[str, Any]] = None,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> RecordDict:
        """
        Create a single record in Airtable.

        Args:
            fields: Dictionary of field names and values

        Returns:
            Created record with ID and fields

        Raises:
            AirtableAPIError: If creation fails
        """
        payload = data if data is not None else fields
        if payload is None:
            raise ValueError(
                "Either 'fields' positional argument or 'data' keyword argument must be provided"
            )

        await self.rate_limiter.acquire()

        try:
            logger.debug(
                "Creating record with fields: %s%s",
                list(payload.keys()),
                (
                    f" on table {table_id or table_name}"
                    if (table_name or table_id)
                    else ""
                ),
            )

            # Translate field names to Field IDs and option values to Option IDs
            translated_fields = self._translate_fields_for_api(payload)

            table = self._get_table(table_name=table_name, table_id=table_id)
            record = await asyncio.to_thread(table.create, translated_fields)

            logger.debug(f"Created record with ID: {record['id']}")
            return record

        except Exception as e:
            error_msg = f"Failed to create record: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def get_record(
        self,
        record_id: str,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> Optional[RecordDict]:
        """
        Get a single record by ID.

        Args:
            record_id: Airtable record ID

        Returns:
            Record if found, None otherwise

        Raises:
            AirtableAPIError: If retrieval fails
        """
        await self.rate_limiter.acquire()

        try:
            logger.debug(
                "Getting record %s%s",
                record_id,
                (
                    f" from table {table_id or table_name}"
                    if (table_name or table_id)
                    else ""
                ),
            )

            table = self._get_table(table_name=table_name, table_id=table_id)
            record = await asyncio.to_thread(table.get, record_id)

            return record

        except Exception as e:
            # Check if it's a "not found" error
            error_str = str(e).lower()
            if "not found" in error_str or "404" in error_str:
                logger.debug(f"Record {record_id} not found")
                return None

            error_msg = f"Failed to get record {record_id}: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def update_record(
        self,
        record_id: str,
        fields: Optional[Dict[str, Any]] = None,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
        data: Optional[Dict[str, Any]] = None,
    ) -> RecordDict:
        """
        Update a single record.

        Args:
            record_id: Airtable record ID
            fields: Dictionary of field names and updated values

        Returns:
            Updated record

        Raises:
            AirtableAPIError: If update fails
        """
        payload = data if data is not None else fields
        if payload is None:
            raise ValueError(
                "Either 'fields' positional argument or 'data' keyword argument must be provided"
            )

        await self.rate_limiter.acquire()

        try:
            logger.debug(
                "Updating record %s with fields: %s%s",
                record_id,
                list(payload.keys()),
                (
                    f" on table {table_id or table_name}"
                    if (table_name or table_id)
                    else ""
                ),
            )

            # Translate field names to Field IDs and option values to Option IDs
            translated_fields = self._translate_fields_for_api(payload)

            table = self._get_table(table_name=table_name, table_id=table_id)
            record = await asyncio.to_thread(table.update, record_id, translated_fields)

            logger.debug(f"Updated record with ID: {record['id']}")
            return record

        except Exception as e:
            error_msg = f"Failed to update record {record_id}: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def delete_record(
        self,
        record_id: str,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> bool:
        """
        Delete a single record.

        Args:
            record_id: Airtable record ID

        Returns:
            True if deletion was successful

        Raises:
            AirtableAPIError: If deletion fails
        """
        await self.rate_limiter.acquire()

        try:
            logger.debug(
                "Deleting record %s%s",
                record_id,
                (
                    f" from table {table_id or table_name}"
                    if (table_name or table_id)
                    else ""
                ),
            )

            table = self._get_table(table_name=table_name, table_id=table_id)
            await asyncio.to_thread(table.delete, record_id)

            logger.debug(f"Deleted record with ID: {record_id}")
            return True

        except Exception as e:
            error_msg = f"Failed to delete record {record_id}: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def list_records(
        self,
        formula: Optional[str] = None,
        sort: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        max_records: Optional[int] = None,
        view: Optional[str] = None,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
        offset: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        List records with optional filtering and pagination.

        Args:
            formula: Airtable formula for filtering
            sort: List of field names to sort by (prefix with '-' for descending)
            fields: List of field names to include in response
            max_records: Maximum number of records to return
            view: Name of view to use
            offset: Airtable offset token for pagination (string)

        Returns:
            Dict containing 'records' list and 'offset' token if more records available

        Raises:
            AirtableAPIError: If listing fails
        """
        await self.rate_limiter.acquire()

        try:
            logger.debug(
                "Listing records with formula: %s, max: %s, offset: %s%s",
                formula,
                max_records,
                offset,
                (
                    f", table: {table_id or table_name}"
                    if (table_name or table_id)
                    else ""
                ),
            )

            # Build parameters for direct Airtable API call
            params: Dict[str, Any] = {}
            if formula:
                params["filterByFormula"] = formula
            if sort:
                params["sort"] = sort
            if fields:
                params["fields"] = fields
            if max_records:
                params["maxRecords"] = max_records
            if view:
                params["view"] = view
            if page_size:
                params["pageSize"] = page_size
            if offset:
                params["offset"] = offset

            # Get table identifier for URL construction
            table_identifier = table_id if table_id else table_name
            if not table_identifier:
                table_identifier = (
                    self.config.table_id if self.config.table_id else self.config.table_name
                )

            # Make direct API call to get paginated response with offset token
            url = f"/v0/{self.config.base_id}/{table_identifier}"
            
            response = await asyncio.to_thread(
                self.api.request, "GET", url, params=params
            )

            # Extract records and offset from response
            records = response.get("records", [])
            next_offset = response.get("offset")

            result = {
                "records": records,
                "offset": next_offset
            }

            logger.debug(f"Retrieved {len(records)} records, next_offset: {bool(next_offset)}")
            return result

        except Exception as e:
            error_msg = f"Failed to list records: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)

    async def get_records(
        self,
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
        filter_formula: Optional[str] = None,
        max_records: Optional[int] = None,
        sort: Optional[List[str]] = None,
        fields: Optional[List[str]] = None,
        view: Optional[str] = None,
        offset: Optional[str] = None,
        page_size: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Alias for list_records with repository-friendly parameter names."""

        return await self.list_records(
            formula=filter_formula,
            sort=sort,
            fields=fields,
            max_records=max_records,
            view=view,
            table_name=table_name,
            table_id=table_id,
            offset=offset,
            page_size=page_size,
        )

    async def bulk_create(
        self,
        records: List[Dict[str, Any]],
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> List[RecordDict]:
        """
        Create multiple records in batch.

        Args:
            records: List of field dictionaries to create

        Returns:
            List of created records

        Raises:
            AirtableAPIError: If bulk creation fails
        """
        if not records:
            return []

        # Airtable batch operations are limited to 10 records per request
        batch_size = 10
        results = []

        for i in range(0, len(records), batch_size):
            batch = records[i : i + batch_size]
            await self.rate_limiter.acquire()

            try:
                logger.debug(f"Creating batch of {len(batch)} records")

                translated_batch = [
                    self._translate_fields_for_api(record) for record in batch
                ]

                table = self._get_table(table_name=table_name, table_id=table_id)
                batch_results = await asyncio.to_thread(
                    table.batch_create, translated_batch
                )

                results.extend(batch_results)
                logger.debug(f"Created batch with {len(batch_results)} records")

            except Exception as e:
                error_msg = f"Failed to create batch: {str(e)}"
                logger.error(error_msg)
                raise AirtableAPIError(error_msg, original_error=e)

        return results

    async def bulk_update(
        self,
        updates: List[Dict[str, Any]],
        *,
        table_name: Optional[str] = None,
        table_id: Optional[str] = None,
    ) -> List[RecordDict]:
        """
        Update multiple records in batch.

        Args:
            updates: List of dictionaries with 'id' and 'fields' keys

        Returns:
            List of updated records

        Raises:
            AirtableAPIError: If bulk update fails
        """
        if not updates:
            return []

        # Airtable batch operations are limited to 10 records per request
        batch_size = 10
        results = []

        for i in range(0, len(updates), batch_size):
            batch = updates[i : i + batch_size]
            await self.rate_limiter.acquire()

            try:
                logger.debug(f"Updating batch of {len(batch)} records")

                translated_batch = [
                    {
                        "id": update["id"],
                        "fields": self._translate_fields_for_api(update["fields"]),
                    }
                    for update in batch
                ]

                table = self._get_table(table_name=table_name, table_id=table_id)
                batch_results = await asyncio.to_thread(
                    table.batch_update, translated_batch  # type: ignore[arg-type]
                )

                results.extend(batch_results)
                logger.debug(f"Updated batch with {len(batch_results)} records")

            except Exception as e:
                error_msg = f"Failed to update batch: {str(e)}"
                logger.error(error_msg)
                raise AirtableAPIError(error_msg, original_error=e)

        return results

    async def search_by_field(self, field_name: str, value: Any) -> List[RecordDict]:
        """
        Search records by exact field match.

        Args:
            field_name: Name of field to search
            value: Value to match exactly

        Returns:
            List of matching records

        Raises:
            AirtableAPIError: If search fails
        """
        # Build Airtable formula for exact match
        if isinstance(value, str):
            # String values need to be quoted and single quotes escaped
            escaped_value = value.replace("'", "''")
            formula = f"{{{field_name}}} = '{escaped_value}'"
        else:
            # Numbers and other values don't need quotes
            formula = f"{{{field_name}}} = {value}"

        response = await self.list_records(formula=formula)
        return response["records"]

    async def search_by_formula(self, formula: str) -> List[RecordDict]:
        """
        Search records using custom Airtable formula.

        Args:
            formula: Airtable formula string

        Returns:
            List of matching records

        Raises:
            AirtableAPIError: If search fails
        """
        response = await self.list_records(formula=formula)
        return response["records"]

    async def get_schema(self) -> Any:
        """
        Get table schema information.

        Returns:
            Schema information including fields and their types

        Raises:
            AirtableAPIError: If schema retrieval fails
        """
        await self.rate_limiter.acquire()

        try:
            logger.debug("Getting table schema")

            schema = await asyncio.to_thread(self.table.schema)

            return schema

        except Exception as e:
            error_msg = f"Failed to get schema: {str(e)}"
            logger.error(error_msg)
            raise AirtableAPIError(error_msg, original_error=e)
