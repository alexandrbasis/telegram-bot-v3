"""
Airtable-specific implementation of ParticipantRepository.

This implementation uses the AirtableClient to perform all CRUD operations
on participant data, mapping between Participant domain objects and Airtable
record format.
"""

from typing import List, Optional, Dict, Any, Tuple, Union
import logging

from src.data.repositories.participant_repository import (
    ParticipantRepository,
    RepositoryError,
    ValidationError,
    NotFoundError,
    DuplicateError,
)
from src.data.airtable.airtable_client import AirtableClient, AirtableAPIError
from src.models.participant import Participant
from src.services.search_service import (
    SearchService,
    detect_language,
    format_participant_result,
)

logger = logging.getLogger(__name__)


class AirtableParticipantRepository(ParticipantRepository):
    """
    Airtable-specific implementation of ParticipantRepository.

    Maps between Participant domain objects and Airtable records, handling
    all CRUD operations and search functionality through the AirtableClient.
    """

    def __init__(self, client: AirtableClient):
        """
        Initialize the repository with an AirtableClient.

        Args:
            client: Configured AirtableClient instance
        """
        self.client = client
        logger.info("Initialized AirtableParticipantRepository")

    async def create(self, participant: Participant) -> Participant:
        """
        Create a new participant record in Airtable.

        Args:
            participant: Participant domain object to create

        Returns:
            Created participant with Airtable record ID

        Raises:
            ValidationError: If participant data is invalid
            DuplicateError: If participant already exists
            RepositoryError: If creation fails
        """
        try:
            # Convert Participant to Airtable fields format
            airtable_fields = participant.to_airtable_fields()

            # Check for duplicates by contact information if provided
            if participant.contact_information:
                existing = await self.find_by_contact_information(
                    participant.contact_information
                )
                if existing:
                    raise DuplicateError(
                        f"Participant with contact info '{participant.contact_information}' already exists"
                    )

            logger.info(f"Creating participant: {participant.full_name_ru}")

            # Create record in Airtable
            record = await self.client.create_record(airtable_fields)

            # Convert back to Participant with record ID
            created_participant = Participant.from_airtable_record(record)

            logger.info(f"Created participant with ID: {record['id']}")
            return created_participant

        except AirtableAPIError as e:
            # Check if it's a validation error from Airtable
            if e.status_code == 422:
                raise ValidationError(
                    f"Invalid participant data: {e}", e.original_error
                )
            else:
                raise RepositoryError(
                    f"Failed to create participant: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, (ValidationError, DuplicateError)):
                raise
            raise RepositoryError(f"Unexpected error creating participant: {e}", e)

    async def get_by_id(self, participant_id: str) -> Optional[Participant]:
        """
        Get a participant by their Airtable record ID.

        Args:
            participant_id: Airtable record ID

        Returns:
            Participant if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            logger.debug(f"Getting participant by ID: {participant_id}")

            record = await self.client.get_record(participant_id)
            if not record:
                return None

            return Participant.from_airtable_record(record)

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to get participant {participant_id}: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(f"Unexpected error getting participant: {e}", e)

    async def update(self, participant: Participant) -> Participant:
        """
        Update an existing participant record.

        Args:
            participant: Participant with updated data (must have record_id)

        Returns:
            Updated participant

        Raises:
            ValidationError: If participant data is invalid
            NotFoundError: If participant doesn't exist
            RepositoryError: If update fails
        """
        if not participant.record_id:
            raise ValidationError("Cannot update participant without record_id")

        try:
            logger.info(f"Updating participant: {participant.record_id}")

            # Convert to Airtable fields format
            airtable_fields = participant.to_airtable_fields()

            # Update record in Airtable
            updated_record = await self.client.update_record(
                participant.record_id, airtable_fields
            )

            # Convert back to Participant
            updated_participant = Participant.from_airtable_record(updated_record)

            logger.info(f"Updated participant: {participant.record_id}")
            return updated_participant

        except AirtableAPIError as e:
            if e.status_code == 404:
                raise NotFoundError(f"Participant {participant.record_id} not found")
            elif e.status_code == 422:
                raise ValidationError(
                    f"Invalid participant data: {e}", e.original_error
                )
            else:
                raise RepositoryError(
                    f"Failed to update participant: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError)):
                raise
            raise RepositoryError(f"Unexpected error updating participant: {e}", e)

    async def update_by_id(self, record_id: str, field_updates: Dict[str, Any]) -> bool:
        """
        Update specific fields of a participant by record ID.

        Updates only the specified fields, leaving other fields unchanged.
        Uses Airtable's partial update functionality.

        Args:
            record_id: Airtable record ID
            field_updates: Dictionary of field names and new values

        Returns:
            True if update was successful, False otherwise

        Raises:
            RepositoryError: If update operation fails
            NotFoundError: If record_id doesn't exist
            ValidationError: If field_updates contains invalid data
        """
        if not record_id:
            raise ValidationError("Record ID cannot be empty")

        if not field_updates:
            logger.info(f"No field updates provided for record {record_id}")
            return True

        try:
            logger.info(
                f"Updating fields for participant {record_id}: {list(field_updates.keys())}"
            )

            # Convert field updates to Airtable format
            # We need to handle the field name mapping between model fields and Airtable fields
            airtable_fields = self._convert_field_updates_to_airtable(field_updates)

            # Update record in Airtable
            updated_record = await self.client.update_record(record_id, airtable_fields)

            if updated_record:
                logger.info(f"Successfully updated participant {record_id}")
                return True
            else:
                logger.warning(f"No record returned from update for {record_id}")
                return False

        except AirtableAPIError as e:
            if e.status_code == 404:
                raise NotFoundError(f"Participant {record_id} not found")
            elif e.status_code == 422:
                raise ValidationError(f"Invalid field updates: {e}", e.original_error)
            else:
                raise RepositoryError(
                    f"Failed to update participant fields: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, (ValidationError, NotFoundError)):
                raise
            raise RepositoryError(
                f"Unexpected error updating participant fields: {e}", e
            )

    def _convert_field_updates_to_airtable(
        self, field_updates: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Convert model field names and values to Airtable field format.

        Maps between participant model field names and Airtable API field names.

        Args:
            field_updates: Dictionary with model field names as keys

        Returns:
            Dictionary with Airtable field names as keys
        """
        # Field name mapping from model to Airtable
        field_mapping = {
            "full_name_ru": "FullNameRU",
            "full_name_en": "FullNameEN",
            "church": "Church",
            "country_and_city": "CountryAndCity",
            "contact_information": "ContactInformation",
            "submitted_by": "SubmittedBy",
            "gender": "Gender",
            "size": "Size",
            "role": "Role",
            "department": "Department",
            "payment_status": "PaymentStatus",
            "payment_amount": "PaymentAmount",
            "payment_date": "PaymentDate",
            # Exact field names from live Airtable schema
            "floor": "Floor",
            "room_number": "RoomNumber",
        }

        airtable_fields = {}

        for field_name, value in field_updates.items():
            airtable_field_name = field_mapping.get(field_name)
            if not airtable_field_name:
                raise ValidationError(f"Unknown field name: {field_name}")

            # Convert value to appropriate format for Airtable
            if field_name == "payment_date" and value is not None:
                # Convert date to ISO format string
                airtable_fields[airtable_field_name] = (
                    value.isoformat() if hasattr(value, "isoformat") else str(value)
                )
            elif hasattr(value, "value"):
                # Handle enum values (Gender, Size, Role, Department, PaymentStatus)
                airtable_fields[airtable_field_name] = value.value
            else:
                airtable_fields[airtable_field_name] = value

        return airtable_fields

    async def delete(self, participant_id: str) -> bool:
        """
        Delete a participant record.

        Args:
            participant_id: Airtable record ID

        Returns:
            True if deletion was successful

        Raises:
            NotFoundError: If participant doesn't exist
            RepositoryError: If deletion fails
        """
        try:
            logger.info(f"Deleting participant: {participant_id}")

            # Check if participant exists first
            existing = await self.get_by_id(participant_id)
            if not existing:
                raise NotFoundError(f"Participant {participant_id} not found")

            # Delete from Airtable
            success = await self.client.delete_record(participant_id)

            if success:
                logger.info(f"Deleted participant: {participant_id}")

            return success

        except AirtableAPIError as e:
            if e.status_code == 404:
                raise NotFoundError(f"Participant {participant_id} not found")
            else:
                raise RepositoryError(
                    f"Failed to delete participant: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, NotFoundError):
                raise
            raise RepositoryError(f"Unexpected error deleting participant: {e}", e)

    async def get_by_full_name_ru(self, full_name_ru: str) -> Optional[Participant]:
        """
        Retrieve a participant by their Russian full name (primary field).

        Args:
            full_name_ru: Full name in Russian

        Returns:
            Participant instance if found, None otherwise

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            logger.debug(f"Finding participant by full name (RU): {full_name_ru}")

            # Search by FullNameRU field in Airtable (exact name)
            records = await self.client.search_by_field("FullNameRU", full_name_ru)

            if not records:
                return None

            # Return the first matching participant
            return Participant.from_airtable_record(records[0])

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participant by full name: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participant by full name: {e}", e
            )

    async def list_all(
        self, limit: Optional[int] = None, offset: Optional[int] = None
    ) -> List[Participant]:
        """
        List all participants with optional limit and offset.

        Args:
            limit: Maximum number of participants to return
            offset: Number of participants to skip (not supported by Airtable API)

        Returns:
            List of participants

        Raises:
            RepositoryError: If listing fails
        """
        try:
            logger.debug(f"Listing all participants (limit: {limit}, offset: {offset})")

            if offset is not None and offset > 0:
                logger.warning(
                    "Offset pagination not directly supported by Airtable API, offset will be ignored"
                )

            # Get records from Airtable
            records = await self.client.list_records(max_records=limit)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(f"Listed {len(participants)} participants")
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(f"Failed to list participants: {e}", e.original_error)
        except Exception as e:
            raise RepositoryError(f"Unexpected error listing participants: {e}", e)

    async def search_by_criteria(self, criteria: Dict[str, Any]) -> List[Participant]:
        """
        Search participants by multiple criteria.

        Args:
            criteria: Dictionary of search criteria where keys are field names
                     and values are the search values.

        Returns:
            List of participants matching the criteria

        Raises:
            RepositoryError: If search fails
            ValueError: If criteria contains unsupported fields or values
        """

        try:
            logger.debug(f"Searching participants by criteria: {criteria}")

            if not criteria:
                return await self.list_all()

            # Build Airtable formula from criteria
            conditions = []

            for field, value in criteria.items():
                if field == "full_name_ru":
                    conditions.append(f"SEARCH('{value}', {{FullNameRU}})")
                elif field == "full_name_en":
                    conditions.append(f"SEARCH('{value}', {{FullNameEN}})")
                elif field == "church":
                    conditions.append(f"{{Church}} = '{value}'")
                elif field == "role":
                    conditions.append(f"{{Role}} = '{value}'")
                elif field == "department":
                    conditions.append(f"{{Department}} = '{value}'")
                elif field == "payment_status":
                    conditions.append(f"{{PaymentStatus}} = '{value}'")
                elif field == "gender":
                    conditions.append(f"{{Gender}} = '{value}'")
                else:
                    raise ValueError(f"Unsupported search criteria field: {field}")

            # Combine conditions with AND
            if len(conditions) == 1:
                formula = conditions[0]
            else:
                formula = f"AND({', '.join(conditions)})"

            records = await self.client.search_by_formula(formula)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(f"Found {len(participants)} participants matching criteria")
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to search participants by criteria: {e}", e.original_error
            )
        except ValueError:
            raise
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error searching participants by criteria: {e}", e
            )

    async def get_by_role(self, role: str) -> List[Participant]:
        """
        Retrieve all participants with a specific role.

        Args:
            role: Role value (Role enum value)

        Returns:
            List of participants with the specified role

        Raises:
            RepositoryError: If retrieval fails
        """
        return await self.find_by_role(role)

    async def get_by_department(self, department: str) -> List[Participant]:
        """
        Retrieve all participants in a specific department.

        Args:
            department: Department value (Department enum value)

        Returns:
            List of participants in the specified department

        Raises:
            RepositoryError: If retrieval fails
        """
        return await self.find_by_department(department)

    async def get_by_payment_status(self, payment_status: str) -> List[Participant]:
        """
        Retrieve all participants with a specific payment status.

        Args:
            payment_status: Payment status value (PaymentStatus enum value)

        Returns:
            List of participants with the specified payment status

        Raises:
            RepositoryError: If retrieval fails
        """
        try:
            logger.debug(f"Finding participants by payment status: {payment_status}")

            # Search by PaymentStatus field in Airtable
            records = await self.client.search_by_field("PaymentStatus", payment_status)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(
                f"Found {len(participants)} participants with payment status: {payment_status}"
            )
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participants by payment status: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participants by payment status: {e}", e
            )

    async def count_total(self) -> int:
        """
        Get the total number of participant records.

        Returns:
            Total count of participant records

        Raises:
            RepositoryError: If count operation fails
        """
        return await self.count_all()

    async def find_by_contact_information(
        self, contact_info: str
    ) -> Optional[Participant]:
        """
        Find a participant by contact information.

        Args:
            contact_info: Contact information to search for

        Returns:
            Participant if found, None otherwise

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participant by contact information: {contact_info}")

            # Use display label as used in tests/schema: "Contact Information"
            records = await self.client.search_by_field(
                "Contact Information", contact_info
            )

            if not records:
                return None

            # Return the first matching participant
            return Participant.from_airtable_record(records[0])

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participant by contact info: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participant by contact info: {e}", e
            )

    async def find_by_telegram_id(self, telegram_id: int) -> Optional[Participant]:
        """
        Find a participant by Telegram user ID.

        Args:
            telegram_id: Telegram user ID to search for

        Returns:
            Participant if found, None otherwise

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participant by Telegram ID: {telegram_id}")

            # Use display label used in tests/schema: "Telegram ID"
            records = await self.client.search_by_field("Telegram ID", telegram_id)

            if not records:
                return None

            # Return the first matching participant
            return Participant.from_airtable_record(records[0])

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participant by Telegram ID: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participant by Telegram ID: {e}", e
            )

    async def search_by_name(self, name_pattern: str) -> List[Participant]:
        """
        Search participants by name pattern.

        Args:
            name_pattern: Pattern to search for in names

        Returns:
            List of matching participants

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Searching participants by name pattern: {name_pattern}")

            # Build Airtable formula for partial name matching using display labels
            formula = (
                f"OR(SEARCH('{name_pattern}', {{Full Name (RU)}}), "
                f"SEARCH('{name_pattern}', {{Full Name (EN)}}))"
            )

            records = await self.client.search_by_formula(formula)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(
                f"Found {len(participants)} participants matching name pattern"
            )
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to search participants by name: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error searching participants by name: {e}", e
            )

    async def find_by_role(self, role: str) -> List[Participant]:
        """
        Find participants by their role.

        Args:
            role: Role to search for (e.g., "Pilgrim", "Team")

        Returns:
            List of participants with the specified role

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participants by role: {role}")

            # Search by Role field in Airtable
            records = await self.client.search_by_field("Role", role)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(f"Found {len(participants)} participants with role: {role}")
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participants by role: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participants by role: {e}", e
            )

    async def find_by_department(self, department: str) -> List[Participant]:
        """
        Find participants by their department.

        Args:
            department: Department to search for

        Returns:
            List of participants in the specified department

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participants by department: {department}")

            # Search by Department field in Airtable
            records = await self.client.search_by_field("Department", department)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(
                f"Found {len(participants)} participants in department: {department}"
            )
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participants by department: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participants by department: {e}", e
            )

    async def bulk_create(self, participants: List[Participant]) -> List[Participant]:
        """
        Create multiple participants in batch.

        Args:
            participants: List of participants to create

        Returns:
            List of created participants with record IDs

        Raises:
            ValidationError: If any participant data is invalid
            RepositoryError: If bulk creation fails
        """
        if not participants:
            return []

        try:
            logger.info(f"Bulk creating {len(participants)} participants")

            # Convert all participants to Airtable fields format
            airtable_records = []
            for participant in participants:
                airtable_fields = participant.to_airtable_fields()
                airtable_records.append(airtable_fields)

            # Create records in Airtable using bulk operation
            created_records = await self.client.bulk_create(airtable_records)

            # Convert back to Participant objects
            created_participants = []
            for record in created_records:
                participant = Participant.from_airtable_record(record)
                created_participants.append(participant)

            logger.info(f"Bulk created {len(created_participants)} participants")
            return created_participants

        except AirtableAPIError as e:
            if e.status_code == 422:
                raise ValidationError(
                    f"Invalid participant data in bulk create: {e}", e.original_error
                )
            else:
                raise RepositoryError(
                    f"Failed to bulk create participants: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise RepositoryError(f"Unexpected error in bulk create: {e}", e)

    async def bulk_update(self, participants: List[Participant]) -> List[Participant]:
        """
        Update multiple participants in batch.

        Args:
            participants: List of participants to update (must have record_id)

        Returns:
            List of updated participants

        Raises:
            ValidationError: If any participant data is invalid or missing record_id
            RepositoryError: If bulk update fails
        """
        if not participants:
            return []

        # Validate all participants have record_id
        for participant in participants:
            if not participant.record_id:
                raise ValidationError(
                    "Cannot bulk update participants without record_id"
                )

        try:
            logger.info(f"Bulk updating {len(participants)} participants")

            # Convert to Airtable update format: {"id": record_id, "fields": {...}}
            airtable_updates = []
            for participant in participants:
                update_record = {
                    "id": participant.record_id,
                    "fields": participant.to_airtable_fields(),
                }
                airtable_updates.append(update_record)

            # Update records in Airtable using bulk operation
            updated_records = await self.client.bulk_update(airtable_updates)

            # Convert back to Participant objects
            updated_participants = []
            for record in updated_records:
                participant = Participant.from_airtable_record(record)
                updated_participants.append(participant)

            logger.info(f"Bulk updated {len(updated_participants)} participants")
            return updated_participants

        except AirtableAPIError as e:
            if e.status_code == 422:
                raise ValidationError(
                    f"Invalid participant data in bulk update: {e}", e.original_error
                )
            else:
                raise RepositoryError(
                    f"Failed to bulk update participants: {e}", e.original_error
                )
        except Exception as e:
            if isinstance(e, ValidationError):
                raise
            raise RepositoryError(f"Unexpected error in bulk update: {e}", e)

    async def count_all(self) -> int:
        """
        Count total number of participants.

        Returns:
            Total count of participants

        Raises:
            RepositoryError: If counting fails
        """
        try:
            logger.debug("Counting all participants")

            # Get all records and count them
            # Note: For very large datasets, this could be optimized with a dedicated count API
            records = await self.client.list_records()
            count = len(records)

            logger.debug(f"Total participant count: {count}")
            return count

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to count participants: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(f"Unexpected error counting participants: {e}", e)

    async def health_check(self) -> bool:
        """
        Check if the repository is healthy and accessible.

        Returns:
            True if repository is healthy

        Raises:
            RepositoryError: If health check fails
        """
        try:
            logger.debug("Performing repository health check")

            # Test connection to Airtable
            is_healthy = await self.client.test_connection()

            if is_healthy:
                logger.debug("Repository health check passed")
            else:
                logger.warning("Repository health check failed")

            return is_healthy

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Repository health check failed: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(f"Unexpected error in health check: {e}", e)

    async def search_by_name_fuzzy(
        self, query: str, threshold: float = 0.8, limit: int = 5
    ) -> List[Tuple[Participant, float]]:
        """
        Search participants by name with fuzzy matching.

        Uses SearchService to perform fuzzy matching on both Russian and English names
        with configurable similarity threshold and result limit.

        Args:
            query: Name or partial name to search for
            threshold: Minimum similarity score (0.0-1.0) to include in results
            limit: Maximum number of results to return

        Returns:
            List of tuples containing (Participant, similarity_score) sorted by
            similarity score in descending order

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(
                f"Fuzzy search for '{query}' (threshold={threshold}, limit={limit})"
            )

            if not query or not query.strip():
                logger.debug("Empty query, returning no results")
                return []

            # Get all participants from Airtable
            all_participants = await self.list_all()

            if not all_participants:
                logger.debug("No participants in database")
                return []

            # Use SearchService for fuzzy matching (maintaining backward compatibility)
            search_service = SearchService(
                similarity_threshold=threshold, max_results=limit
            )
            search_results = search_service.search_participants(query, all_participants)

            # Convert SearchResult objects to (Participant, float) tuples (backward compatible)
            fuzzy_results = [
                (result.participant, result.similarity_score)
                for result in search_results
            ]

            logger.debug(f"Fuzzy search found {len(fuzzy_results)} matches")
            return fuzzy_results

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Failed to perform fuzzy name search: {e}", e)

    async def search_by_name_enhanced(
        self, query: str, threshold: float = 0.8, limit: int = 5
    ) -> List[Tuple[Participant, float, str]]:
        """
        Enhanced search with language detection, multi-field search, and rich formatting.

        Uses the enhanced search service with language detection, first/last name search,
        and returns results with rich participant information formatting.

        Args:
            query: Name or partial name to search for
            threshold: Minimum similarity score (0.0-1.0) to include in results
            limit: Maximum number of results to return

        Returns:
            List of tuples containing (Participant, similarity_score, formatted_result)
            sorted by similarity score in descending order

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(
                f"Enhanced search for '{query}' (threshold={threshold}, limit={limit})"
            )

            if not query or not query.strip():
                logger.debug("Empty query, returning no results")
                return []

            # Get all participants from Airtable
            all_participants = await self.list_all()

            if not all_participants:
                logger.debug("No participants in database")
                return []

            # Detect query language for optimized formatting
            detected_lang = detect_language(query.strip())

            # Use enhanced SearchService for multi-field matching
            search_service = SearchService(
                similarity_threshold=threshold, max_results=limit
            )
            search_results = search_service.search_participants_enhanced(
                query, all_participants
            )

            # Convert SearchResult objects to (Participant, float, str) tuples with rich formatting
            enhanced_results = []
            for result in search_results:
                formatted_result = format_participant_result(
                    result.participant, detected_lang
                )
                enhanced_results.append(
                    (result.participant, result.similarity_score, formatted_result)
                )

            logger.debug(f"Enhanced search found {len(enhanced_results)} matches")
            return enhanced_results

        except Exception as e:
            if isinstance(e, RepositoryError):
                raise
            raise RepositoryError(f"Failed to perform enhanced name search: {e}", e)

    async def find_by_room_number(self, room_number: str) -> List[Participant]:
        """
        Find all participants assigned to a specific room number.

        Args:
            room_number: Room number to search for (as string to handle alphanumeric)

        Returns:
            List of participants in the specified room

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participants by room number: {room_number}")

            # Search by RoomNumber field in Airtable
            records = await self.client.search_by_field("RoomNumber", room_number)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(
                f"Found {len(participants)} participants in room: {room_number}"
            )
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participants by room: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participants by room: {e}", e
            )

    async def find_by_floor(self, floor: Union[int, str]) -> List[Participant]:
        """
        Find all participants assigned to a specific floor.

        Args:
            floor: Floor number or identifier (int or str to handle "Ground" etc.)

        Returns:
            List of participants on the specified floor

        Raises:
            RepositoryError: If search fails
        """
        try:
            logger.debug(f"Finding participants by floor: {floor}")

            # Search by Floor field in Airtable
            records = await self.client.search_by_field("Floor", floor)

            # Convert to Participant objects
            participants = []
            for record in records:
                try:
                    participant = Participant.from_airtable_record(record)
                    participants.append(participant)
                except Exception as e:
                    logger.warning(
                        f"Skipping invalid participant record {record.get('id', 'unknown')}: {e}"
                    )
                    continue

            logger.debug(f"Found {len(participants)} participants on floor: {floor}")
            return participants

        except AirtableAPIError as e:
            raise RepositoryError(
                f"Failed to find participants by floor: {e}", e.original_error
            )
        except Exception as e:
            raise RepositoryError(
                f"Unexpected error finding participants by floor: {e}", e
            )
