"""
Service for participant list functionality.

Provides role-based participant filtering, list formatting with pagination,
and Russian date formatting for list display.
"""

from typing import Dict, List, Any
from telegram.helpers import escape_markdown

from src.models.participant import Participant
from src.data.repositories.participant_repository import ParticipantRepository


class ParticipantListService:
    """Service for managing participant list display and formatting."""

    def __init__(self, repository: ParticipantRepository):
        """
        Initialize participant list service.

        Args:
            repository: Participant repository for data access
        """
        self.repository = repository

    async def get_team_members_list(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get formatted team members list with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of participants per page

        Returns:
            Dict with formatted_list, pagination info, and counts
        """
        participants = await self.repository.get_by_role("TEAM")
        return self._format_participant_list(participants, page, page_size)

    async def get_candidates_list(
        self, page: int = 1, page_size: int = 20
    ) -> Dict[str, Any]:
        """
        Get formatted candidates list with pagination.

        Args:
            page: Page number (1-indexed)
            page_size: Number of participants per page

        Returns:
            Dict with formatted_list, pagination info, and counts
        """
        participants = await self.repository.get_by_role("CANDIDATE")
        return self._format_participant_list(participants, page, page_size)

    def _format_participant_list(
        self, participants: List[Participant], page: int, page_size: int
    ) -> Dict[str, Any]:
        """
        Format participant list with pagination.

        Args:
            participants: List of participants to format
            page: Current page number (1-indexed)
            page_size: Number of participants per page

        Returns:
            Dict with formatted list and pagination information
        """
        total_count = len(participants)

        if total_count == 0:
            return {
                "formatted_list": "Участники не найдены.",
                "has_prev": False,
                "has_next": False,
                "total_count": 0,
                "page": page,
            }

        # Calculate pagination
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_count)
        page_participants = participants[start_idx:end_idx]

        # Format the list
        formatted_lines = []
        for i, participant in enumerate(page_participants, start=start_idx + 1):
            line = self._format_participant_line(i, participant)
            formatted_lines.append(line)

        formatted_list = "\n\n".join(formatted_lines)
        
        # Track actual displayed count for pagination continuity
        actual_displayed_count = len(formatted_lines)

        # Apply message length constraint
        while len(formatted_list) >= 4096 and len(formatted_lines) > 1:
            # Remove last item and add truncation notice
            formatted_lines.pop()
            actual_displayed_count = len(formatted_lines)
            remaining_count = len(page_participants) - actual_displayed_count
            formatted_list = "\n\n".join(formatted_lines)
            if remaining_count > 0:
                formatted_list += f"\n\n... и ещё {remaining_count} участников"
        
        # Adjust pagination logic to account for trimmed items
        # If we trimmed items, the effective end index is smaller
        effective_end_idx = start_idx + actual_displayed_count
        
        # Has next page if there are more participants beyond what we actually displayed
        has_next_page = effective_end_idx < total_count

        return {
            "formatted_list": formatted_list,
            "has_prev": page > 1,
            "has_next": has_next_page,
            "total_count": total_count,
            "page": page,
            "actual_displayed": actual_displayed_count,  # For debugging/testing
        }

    def _format_participant_line(self, number: int, participant: Participant) -> str:
        """
        Format single participant line for display.

        Args:
            number: Sequential number for the participant
            participant: Participant to format

        Returns:
            Formatted participant line
        """
        # Format date of birth
        if participant.date_of_birth:
            dob_str = participant.date_of_birth.strftime("%d.%m.%Y")
        else:
            dob_str = "Не указано"

        # Handle optional fields with Markdown escaping
        size_str = escape_markdown(participant.size, version=2) if participant.size else "—"
        church_str = escape_markdown(participant.church, version=2) if participant.church else "—"
        name_str = escape_markdown(participant.full_name_ru, version=2) if participant.full_name_ru else "Неизвестно"
        dob_escaped = escape_markdown(dob_str, version=2)

        # Format the line with proper Markdown V2 escaping
        line = (
            f"{number}\\. **{name_str}**\n"
            f"   👕 Размер: {size_str}\n"
            f"   ⛪ Церковь: {church_str}\n"
            f"   📅 Дата рождения: {dob_escaped}"
        )

        return line
