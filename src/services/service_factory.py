"""
Service factory for dependency injection.

Provides centralized service instantiation to avoid duplication across handlers.
This is a simple factory pattern that should eventually be replaced with a proper
DI container.
"""

from typing import Callable, Optional

from src.config.settings import get_settings
from src.data.airtable.airtable_client import AirtableClient
from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.services.participant_export_service import ParticipantExportService
from src.services.participant_list_service import ParticipantListService
from src.services.search_service import SearchService


def get_participant_repository() -> AirtableParticipantRepository:
    """
    Get participant repository instance.

    Centralized factory method for participant repository creation.

    Returns:
        AirtableParticipantRepository: Configured repository instance
    """
    settings = get_settings()
    client = AirtableClient(settings.get_airtable_config())
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
