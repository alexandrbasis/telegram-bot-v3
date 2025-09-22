"""Service factory for dependency injection and shared client reuse."""

from dataclasses import asdict
from typing import Callable, Dict, Optional, Tuple

from src.config.settings import get_settings
from src.data.airtable.airtable_bible_readers_repo import AirtableBibleReadersRepository
from src.data.airtable.airtable_client import AirtableClient
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.data.airtable.airtable_roe_repo import AirtableROERepository
from src.services.bible_readers_export_service import BibleReadersExportService
from src.services.participant_export_service import ParticipantExportService
from src.services.participant_list_service import ParticipantListService
from src.services.roe_export_service import ROEExportService
from src.services.search_service import SearchService

# Cache for table-specific clients
_AIRTABLE_CLIENTS: Dict[str, AirtableClient] = {}
_AIRTABLE_CLIENT_SIGNATURES: Dict[str, Tuple] = {}

# Legacy cache for backward compatibility
_AIRTABLE_CLIENT: Optional[AirtableClient] = None
_AIRTABLE_CLIENT_SIGNATURE: Optional[tuple] = None


def get_airtable_client() -> AirtableClient:
    """Return a shared AirtableClient instance based on current settings."""
    global _AIRTABLE_CLIENT, _AIRTABLE_CLIENT_SIGNATURE

    settings = get_settings()
    config = settings.get_airtable_config()
    signature = tuple(sorted(asdict(config).items()))

    if _AIRTABLE_CLIENT is not None and _AIRTABLE_CLIENT_SIGNATURE == signature:
        return _AIRTABLE_CLIENT

    _AIRTABLE_CLIENT = AirtableClient(config)
    _AIRTABLE_CLIENT_SIGNATURE = signature
    return _AIRTABLE_CLIENT


def get_airtable_client_for_table(table_type: str) -> AirtableClient:
    """
    Return a shared AirtableClient instance for a specific table type.

    Args:
        table_type: The table type ('participants', 'bible_readers', 'roe')

    Returns:
        Cached AirtableClient instance for the specified table
    """
    settings = get_settings()
    config = settings.get_airtable_config(table_type)
    signature = tuple(sorted(asdict(config).items()))

    if (
        table_type in _AIRTABLE_CLIENTS
        and _AIRTABLE_CLIENT_SIGNATURES.get(table_type) == signature
    ):
        return _AIRTABLE_CLIENTS[table_type]

    _AIRTABLE_CLIENTS[table_type] = AirtableClient(config)
    _AIRTABLE_CLIENT_SIGNATURES[table_type] = signature
    return _AIRTABLE_CLIENTS[table_type]


def reset_airtable_client_cache() -> None:
    """Reset cached Airtable clients (useful for testing or config reloads)."""
    global _AIRTABLE_CLIENT, _AIRTABLE_CLIENT_SIGNATURE

    # Reset legacy cache
    _AIRTABLE_CLIENT = None
    _AIRTABLE_CLIENT_SIGNATURE = None

    # Reset table-specific caches
    _AIRTABLE_CLIENTS.clear()
    _AIRTABLE_CLIENT_SIGNATURES.clear()


def get_participant_repository() -> AirtableParticipantRepository:
    """
    Get participant repository instance.

    Centralized factory method for participant repository creation.

    Returns:
        AirtableParticipantRepository: Configured repository instance
    """
    client = get_airtable_client()
    return AirtableParticipantRepository(client)


def get_search_service() -> SearchService:
    """
    Get search service instance.

    Centralized factory method for search service creation with repository.

    Returns:
        SearchService: Configured search service instance
    """
    repository = get_participant_repository()
    # Pass repository via keyword to match SearchService signature
    return SearchService(repository=repository)


def get_participant_list_service() -> ParticipantListService:
    """
    Get participant list service instance.

    Centralized factory method for participant list service creation with repository.

    Returns:
        ParticipantListService: Configured participant list service instance
    """
    repository = get_participant_repository()
    return ParticipantListService(repository)


def get_export_service(
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> ParticipantExportService:
    """
    Get export service instance.

    Centralized factory method for export service creation with repository.

    Args:
        progress_callback: Optional callback for progress updates

    Returns:
        ParticipantExportService: Configured export service instance
    """
    repository = get_participant_repository()
    return ParticipantExportService(repository, progress_callback)


def get_bible_readers_repository() -> AirtableBibleReadersRepository:
    """
    Get BibleReaders repository instance.

    Centralized factory method for BibleReaders repository creation.

    Returns:
        AirtableBibleReadersRepository: Configured repository instance
    """
    client = get_airtable_client_for_table("bible_readers")
    return AirtableBibleReadersRepository(client)


def get_roe_repository() -> AirtableROERepository:
    """
    Get ROE repository instance.

    Centralized factory method for ROE repository creation.

    Returns:
        AirtableROERepository: Configured repository instance
    """
    client = get_airtable_client_for_table("roe")
    return AirtableROERepository(client)


def get_bible_readers_export_service(
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> BibleReadersExportService:
    """
    Get BibleReaders export service instance.

    Centralized factory method for BibleReaders export service creation with
    repositories.

    Args:
        progress_callback: Optional callback for progress updates

    Returns:
        BibleReadersExportService: Configured export service instance
    """
    bible_readers_repository = get_bible_readers_repository()
    participant_repository = get_participant_repository()
    return BibleReadersExportService(
        bible_readers_repository=bible_readers_repository,
        participant_repository=participant_repository,
        progress_callback=progress_callback,
    )


def get_roe_export_service(
    progress_callback: Optional[Callable[[int, int], None]] = None,
) -> ROEExportService:
    """
    Get ROE export service instance.

    Centralized factory method for ROE export service creation with repositories.

    Args:
        progress_callback: Optional callback for progress updates

    Returns:
        ROEExportService: Configured export service instance
    """
    roe_repository = get_roe_repository()
    participant_repository = get_participant_repository()
    return ROEExportService(
        roe_repository=roe_repository,
        participant_repository=participant_repository,
        progress_callback=progress_callback,
    )
