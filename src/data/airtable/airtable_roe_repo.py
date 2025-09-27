"""
Airtable-specific implementation of ROERepository.

This implementation uses the AirtableClient to perform all CRUD operations
on ROE data, mapping between ROE domain objects and Airtable record format.
"""

import logging
from typing import Any, Dict, List, Optional

from src.config.field_mappings.roe import ROEFieldMapping
from src.data.airtable.airtable_client import AirtableAPIError, AirtableClient
from src.data.airtable.formula_utils import escape_formula_value
from src.data.repositories.participant_repository import (
    NotFoundError,
    RepositoryError,
    ValidationError,
)
from src.data.repositories.roe_repository import ROERepository
from src.models.roe import ROE

logger = logging.getLogger(__name__)


class AirtableROERepository(ROERepository):
    """
    Airtable-specific implementation of ROERepository.

    Maps between ROE domain objects and Airtable records, handling
    all CRUD operations through the AirtableClient for table tbl0j8bcgkV3lVAdc.
    """

    def __init__(self, client: AirtableClient):
        """
        Initialize the repository with an Airtable client.

        Args:
            client: Configured AirtableClient instance for ROE table
        """
        self.client = client
        self.field_mapping = ROEFieldMapping

    async def create(self, roe: ROE) -> ROE:
        """
        Create a new ROE record in Airtable.

        Args:
            roe: ROE instance to create (record_id should be None)

        Returns:
            ROE instance with assigned record_id

        Raises:
            RepositoryError: If creation fails
            ValidationError: If roe data is invalid
        """
        if roe.record_id is not None:
            raise ValidationError("Cannot create roe with existing record_id")

        # Validate that ROE has at least one presenter
        if not self.field_mapping.validate_presenter_relationships(roe.model_dump()):
            raise ValidationError(
                "ROE must have at least one presenter (roista or assistant)"
            )

        try:
            # Convert to Airtable fields format
            airtable_fields = roe.to_airtable_fields()

            # Create record via client
            record = await self.client.create_record(airtable_fields)

            # Convert back to domain object
            return ROE.from_airtable_record(record)

        except AirtableAPIError as e:
            logger.error(f"Airtable API error creating ROE: {e}")
            raise RepositoryError(f"Failed to create ROE: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error creating ROE: {e}")
            raise RepositoryError(f"Failed to create ROE: {e}") from e

    async def get_by_id(self, record_id: str) -> Optional[ROE]:
        """
        Retrieve a ROE by record ID.

        Args:
            record_id: Unique record identifier

        Returns:
            ROE instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            record = await self.client.get_record(record_id)
            if not record:
                return None

            return ROE.from_airtable_record(record)

        except AirtableAPIError as e:
            if "NOT_FOUND" in str(e):
                return None
            logger.error(f"Airtable API error retrieving ROE {record_id}: {e}")
            raise RepositoryError(f"Failed to get ROE {record_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error retrieving ROE {record_id}: {e}")
            raise RepositoryError(f"Failed to get ROE {record_id}: {e}") from e

    async def get_by_topic(self, topic: str) -> Optional[ROE]:
        """
        Retrieve a ROE by topic (primary field).

        Args:
            topic: ROE topic

        Returns:
            ROE instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Build Airtable formula to search by RoeTopic field
            topic_field = self.field_mapping.python_to_airtable_field("roe_topic")
            escaped_topic = escape_formula_value(topic)
            formula = f"{{{topic_field}}} = '{escaped_topic}'"

            records = await self.client.list_records(formula=formula, max_records=1)

            if not records:
                return None

            return ROE.from_airtable_record(records[0])

        except AirtableAPIError as e:
            logger.error(f"Airtable API error searching ROE by topic '{topic}': {e}")
            raise RepositoryError(
                f"Failed to search ROE by topic '{topic}': {e}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error searching ROE by topic '{topic}': {e}")
            raise RepositoryError(
                f"Failed to search ROE by topic '{topic}': {e}"
            ) from e

    async def update(self, roe: ROE) -> ROE:
        """
        Update an existing ROE record.

        Args:
            roe: ROE instance with record_id and updated fields

        Returns:
            Updated ROE instance

        Raises:
            RepositoryError: If update fails
            ValidationError: If roe data is invalid
            NotFoundError: If record_id doesn't exist
        """
        if not roe.record_id:
            raise ValidationError("Cannot update roe without record_id")

        # Validate that ROE has at least one presenter
        if not self.field_mapping.validate_presenter_relationships(roe.model_dump()):
            raise ValidationError(
                "ROE must have at least one presenter (roista or assistant)"
            )

        try:
            # Convert to Airtable fields format (only writable fields)
            airtable_fields = roe.to_airtable_fields()

            # Update record via client
            record = await self.client.update_record(roe.record_id, airtable_fields)

            # Convert back to domain object
            return ROE.from_airtable_record(record)

        except AirtableAPIError as e:
            if "NOT_FOUND" in str(e):
                raise NotFoundError(f"ROE with id {roe.record_id} not found") from e
            logger.error(f"Airtable API error updating ROE {roe.record_id}: {e}")
            raise RepositoryError(f"Failed to update ROE {roe.record_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error updating ROE {roe.record_id}: {e}")
            raise RepositoryError(f"Failed to update ROE {roe.record_id}: {e}") from e

    async def delete(self, record_id: str) -> bool:
        """
        Delete a ROE record.

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
            logger.error(f"Airtable API error deleting ROE {record_id}: {e}")
            raise RepositoryError(f"Failed to delete ROE {record_id}: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error deleting ROE {record_id}: {e}")
            raise RepositoryError(f"Failed to delete ROE {record_id}: {e}") from e

    async def list_all(self) -> List[ROE]:
        """
        Retrieve all ROE records.

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            records = await self.client.list_records()

            roes = []
            for record in records:
                try:
                    roe = ROE.from_airtable_record(record)
                    roes.append(roe)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid ROE record "
                        f"{record.get('id', 'unknown')}: {e}"
                    )

            return roes

        except AirtableAPIError as e:
            logger.error(f"Airtable API error listing ROEs: {e}")
            raise RepositoryError(f"Failed to list ROEs: {e}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing ROEs: {e}")
            raise RepositoryError(f"Failed to list ROEs: {e}") from e

    async def get_by_roista_id(self, roista_id: str) -> List[ROE]:
        """
        Retrieve all ROE records where a participant is the main roista.

        Args:
            roista_id: Participant record identifier

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Build Airtable formula to search for participant in Roista field
            roista_field = self.field_mapping.python_to_airtable_field("roista")
            escaped_roista_id = escape_formula_value(roista_id)
            formula = f"FIND('{escaped_roista_id}', ARRAYJOIN({{{roista_field}}})) > 0"

            records = await self.client.list_records(formula=formula)

            roes = []
            for record in records:
                try:
                    roe = ROE.from_airtable_record(record)
                    roes.append(roe)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid ROE record "
                        f"{record.get('id', 'unknown')}: {e}"
                    )

            return roes

        except AirtableAPIError as e:
            logger.error(
                f"Airtable API error searching ROEs by roista {roista_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to search ROEs by roista {roista_id}: {e}"
            ) from e
        except Exception as e:
            logger.error(f"Unexpected error searching ROEs by roista {roista_id}: {e}")
            raise RepositoryError(
                f"Failed to search ROEs by roista {roista_id}: {e}"
            ) from e

    async def get_by_assistant_id(self, assistant_id: str) -> List[ROE]:
        """
        Retrieve all ROE records where a participant is an assistant.

        Args:
            assistant_id: Participant record identifier

        Returns:
            List of ROE instances

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            # Build Airtable formula to search for participant in Assistant field
            assistant_field = self.field_mapping.python_to_airtable_field("assistant")
            escaped_assistant_id = escape_formula_value(assistant_id)
            formula = (
                f"FIND('{escaped_assistant_id}', ARRAYJOIN({{{assistant_field}}})) > 0"
            )

            records = await self.client.list_records(formula=formula)

            roes = []
            for record in records:
                try:
                    roe = ROE.from_airtable_record(record)
                    roes.append(roe)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid ROE record "
                        f"{record.get('id', 'unknown')}: {e}"
                    )

            return roes

        except AirtableAPIError as e:
            logger.error(
                f"Airtable API error searching ROEs by assistant {assistant_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to search ROEs by assistant {assistant_id}: {e}"
            ) from e
        except Exception as e:
            logger.error(
                f"Unexpected error searching ROEs by assistant {assistant_id}: {e}"
            )
            raise RepositoryError(
                f"Failed to search ROEs by assistant {assistant_id}: {e}"
            ) from e

    async def list_view_records(self, view: str) -> List[Dict[str, Any]]:
        """
        Retrieve raw Airtable records for a specific view.

        Args:
            view: Airtable view name to pull records from

        Returns:
            List of Airtable record dictionaries returned by the view

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            logger.debug(f"Listing ROE records using view '{view}'")
            records = await self.client.list_records(view=view)
            logger.debug("Retrieved %s ROE records from view '%s'", len(records), view)
            return records  # type: ignore
        except AirtableAPIError as e:
            logger.error(
                f"Airtable API error listing ROE records for view '{view}': {e}"
            )
            raise RepositoryError(
                f"Failed to list ROE records for view '{view}': {e}", e.original_error
            )
