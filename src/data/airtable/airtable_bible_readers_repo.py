"""
Airtable-specific implementation of BibleReadersRepository.

This implementation uses the AirtableClient to perform all CRUD operations
on BibleReaders data, mapping between BibleReader domain objects and Airtable
record format.
"""

import logging
from typing import List, Optional

from src.config.field_mappings.bible_readers import BibleReadersFieldMapping
from src.data.airtable.airtable_client import AirtableAPIError, AirtableClient
from src.data.airtable.formula_utils import escape_formula_value
from src.data.repositories.bible_readers_repository import BibleReadersRepository
from src.data.repositories.participant_repository import (
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from src.models.bible_readers import BibleReader

logger = logging.getLogger(__name__)


class AirtableBibleReadersRepository(BibleReadersRepository):
    """
    Airtable-specific implementation of BibleReadersRepository.

    Maps between BibleReader domain objects and Airtable records, handling
    all CRUD operations through the AirtableClient for table tblGEnSfpPOuPLXcm.
    """

    def __init__(self, client: AirtableClient):
        """
        Initialize the repository with an Airtable client.

        Args:
            client: Configured AirtableClient instance for BibleReaders table
        """
        self.client = client
        self.field_mapping = BibleReadersFieldMapping

    async def create(self, bible_reader: BibleReader) -> BibleReader:
        """
        Create a new BibleReader record in Airtable.

        Args:
            bible_reader: BibleReader instance to create (record_id should be None)

        Returns:
            BibleReader instance with assigned record_id

        Raises:
            RepositoryError: If creation fails
            ValidationError: If bible_reader data is invalid
        """
        if bible_reader.record_id is not None:
            raise ValidationError("Cannot create bible_reader with existing record_id")

        try:
            # Convert to Airtable fields format
            airtable_fields = bible_reader.to_airtable_fields()

            # Create record via client
            record = await self.client.create_record(airtable_fields)

            # Convert back to domain object
            return BibleReader.from_airtable_record(record)

        except AirtableAPIError as e:
            logger.error(f"Airtable API error creating BibleReader: {e}")
            raise RepositoryError(f"Failed to create BibleReader: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating BibleReader: {e}")
            raise RepositoryError(f"Failed to create BibleReader: {e}") from e

    async def get_by_id(self, record_id: str) -> Optional[BibleReader]:
        """
        Retrieve a BibleReader by record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            BibleReader instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            record = await self.client.get_record(record_id)
            if not record:
                return None

            return BibleReader.from_airtable_record(record)

        except AirtableAPIError as e:
            if "NOT_FOUND" in str(e):
                return None
            logger.error(f"Airtable API error retrieving BibleReader {record_id}: {e}")
            raise RepositoryError(f"Failed to get BibleReader {record_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error retrieving BibleReader {record_id}: {e}")
            raise RepositoryError(f"Failed to get BibleReader {record_id}: {e}") from e

    async def get_by_where(self, where: str) -> Optional[BibleReader]:
        """
        Retrieve a BibleReader by their primary field (where).

        Args:
            where: Location/session description

        Returns:
            BibleReader instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Build Airtable formula to search by Where field
            where_field = self.field_mapping.python_to_airtable_field("where")
            escaped_where = escape_formula_value(where)
            formula = f"{{{where_field}}} = '{escaped_where}'"

            records = await self.client.list_records(formula=formula, max_records=1)

            if not records:
                return None

            return BibleReader.from_airtable_record(records[0])

        except AirtableAPIError as e:
            logger.error(
                f"Airtable API error searching BibleReader by where '{where}': {e}"
            )
            raise RepositoryError(
                f"Failed to search BibleReader by where '{where}': {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error searching BibleReader by where '{where}': {e}"
            )
            raise RepositoryError(
                f"Failed to search BibleReader by where '{where}': {e}"
            ) from e

    async def update(self, bible_reader: BibleReader) -> BibleReader:
        """
        Update an existing BibleReader record.

        Args:
            bible_reader: BibleReader instance with record_id and updated fields

        Returns:
            Updated BibleReader instance

        Raises:
            RepositoryError: If update fails
            ValidationError: If bible_reader data is invalid
            NotFoundError: If record_id doesn't exist
        """
        if not bible_reader.record_id:
            raise ValidationError("Cannot update bible_reader without record_id")

        try:
            # Convert to Airtable fields format (only writable fields)
            airtable_fields = bible_reader.to_airtable_fields()

            # Update record via client
            record = await self.client.update_record(
                bible_reader.record_id, airtable_fields
            )

            # Convert back to domain object
            return BibleReader.from_airtable_record(record)

        except AirtableAPIError as e:
            if "NOT_FOUND" in str(e):
                raise NotFoundError(
                    f"BibleReader with id {bible_reader.record_id} not found"
                ) from e
            logger.error(
                f"Airtable API error updating BibleReader {bible_reader.record_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to update BibleReader {bible_reader.record_id}: {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error updating BibleReader {bible_reader.record_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to update BibleReader {bible_reader.record_id}: {e}"
            ) from e

    async def delete(self, record_id: str) -> bool:
        """
        Delete a BibleReader record.

        Args:
            record_id: Unique record identifier

        Returns:
            True if deletion was successful, False if record not found

        Raises:
            RepositoryError: If deletion fails
        """
        try:
            success = await self.client.delete_record(record_id)
            return success

        except AirtableAPIError as e:
            if "NOT_FOUND" in str(e):
                return False
            logger.error(f"Airtable API error deleting BibleReader {record_id}: {e}")
            raise RepositoryError(
                f"Failed to delete BibleReader {record_id}: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error deleting BibleReader {record_id}: {e}")
            raise RepositoryError(
                f"Failed to delete BibleReader {record_id}: {e}"
            ) from e

    async def list_all(self) -> List[BibleReader]:
        """
        Retrieve all BibleReader records.

        Returns:
            List of BibleReader instances

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            records = await self.client.list_records()

            bible_readers = []
            for record in records:
                try:
                    bible_reader = BibleReader.from_airtable_record(record)
                    bible_readers.append(bible_reader)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid BibleReader record {record.get('id', 'unknown')}: {e}"
                    )

            return bible_readers

        except AirtableAPIError as e:
            logger.error(f"Airtable API error listing BibleReaders: {e}")
            raise RepositoryError(f"Failed to list BibleReaders: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing BibleReaders: {e}")
            raise RepositoryError(f"Failed to list BibleReaders: {e}") from e

    async def get_by_participant_id(self, participant_id: str) -> List[BibleReader]:
        """
        Retrieve all BibleReader records where a participant is involved.

        Args:
            participant_id: Participant record identifier

        Returns:
            List of BibleReader instances

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Build Airtable formula to search for participant in Participants field
            participants_field = self.field_mapping.python_to_airtable_field(
                "participants"
            )
            # Use FIND function to search within the array field
            escaped_participant_id = escape_formula_value(participant_id)
            formula = f"FIND('{escaped_participant_id}', ARRAYJOIN({{{participants_field}}})) > 0"

            records = await self.client.list_records(formula=formula)

            bible_readers = []
            for record in records:
                try:
                    bible_reader = BibleReader.from_airtable_record(record)
                    bible_readers.append(bible_reader)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid BibleReader record {record.get('id', 'unknown')}: {e}"
                    )

            return bible_readers

        except AirtableAPIError as e:
            logger.error(
                f"Airtable API error searching BibleReaders by participant {participant_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to search BibleReaders by participant {participant_id}: {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error searching BibleReaders by participant {participant_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to search BibleReaders by participant {participant_id}: {e}"
            ) from e
