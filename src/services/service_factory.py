"""Service factory for dependency injection and shared client reuse."""

from dataclasses import asdict
from typing import Callable, Optional

from src.config.settings import get_settings
from src.data.airtable.airtable_client import AirtableClient
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.services.participant_export_service import ParticipantExportService
from src.services.participant_list_service import ParticipantListService
from src.services.search_service import SearchService


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


def reset_airtable_client_cache() -> None:
    """Reset cached Airtable client (useful for testing or config reloads)."""
    global _AIRTABLE_CLIENT, _AIRTABLE_CLIENT_SIGNATURE
    _AIRTABLE_CLIENT = None
    _AIRTABLE_CLIENT_SIGNATURE = None


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
