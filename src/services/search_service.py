"""
Search service for fuzzy participant name matching.

Provides fuzzy search functionality using rapidfuzz library with Russian/English
name normalization and configurable similarity thresholds.
"""

import logging
from dataclasses import dataclass
from datetime import date
from typing import List, Optional, Tuple, Union

from rapidfuzz import fuzz, process

from src.bot.messages import SearchResultLabels
from src.data.repositories.participant_repository import ParticipantRepository
from src.models.participant import Gender, Participant, PaymentStatus, Role

logger = logging.getLogger(__name__)


def detect_language(text: str) -> str:
    """
    Detect the primary language of input text.

    Uses Cyrillic vs Latin character detection to determine if the input
    is primarily Russian (Cyrillic) or English (Latin).

    Args:
        text: Input text to analyze

    Returns:
        'ru' for Russian/Cyrillic, 'en' for English/Latin (default)
    """
    if not text or not text.strip():
        return "en"  # Default to English for empty input

    text_clean = text.strip()
    cyrillic_count = 0
    latin_count = 0

    for char in text_clean:
        # Check if character is in Cyrillic Unicode range
        if "\u0400" <= char <= "\u04ff":  # Cyrillic block
            cyrillic_count += 1
        # Check if character is in Basic Latin range (letters only)
        elif "A" <= char <= "Z" or "a" <= char <= "z":
            latin_count += 1

    # Return 'ru' if more Cyrillic characters, otherwise 'en'
    return "ru" if cyrillic_count > latin_count else "en"


def parse_name_parts(full_name: str) -> List[str]:
    """
    Parse a full name into individual parts (first, middle, last names).

    Splits on whitespace and filters out empty parts.

    Args:
        full_name: Full name string to parse

    Returns:
        List of name parts (first, middle, last, etc.)
    """
    if not full_name or not full_name.strip():
        return []

    # Split on any whitespace and filter empty parts
    parts = [part.strip() for part in full_name.strip().split() if part.strip()]
    return parts


def format_participant_result(participant: Participant, language: str = "ru") -> str:
    """
    Format participant information for rich search result display.

    Creates a formatted string with participant's name, role, department,
    and other relevant information based on language preference.

    Args:
        participant: Participant instance to format
        language: Display language preference ("ru" or "en")

    Returns:
        Formatted string with participant information
    """
    # Choose primary name based on language preference
    if language == "ru":
        primary_name = participant.full_name_ru
        secondary_name = participant.full_name_en
    else:
        primary_name = participant.full_name_en or participant.full_name_ru
        secondary_name = participant.full_name_ru if participant.full_name_en else None

    # Start with primary name
    result_parts = [primary_name]

    # Add secondary name in parentheses if different
    if secondary_name and secondary_name != primary_name:
        result_parts.append(f"({secondary_name})")

    # Add role and department information
    info_parts = []
    if participant.role:
        # Handle both enum objects and string values (pydantic with use_enum_values=True)
        role_value = (
            participant.role.value
            if hasattr(participant.role, "value")
            else str(participant.role)
        )
        info_parts.append(role_value)

    if participant.department:
        # Handle both enum objects and string values (pydantic with use_enum_values=True)
        dept_value = (
            participant.department.value
            if hasattr(participant.department, "value")
            else str(participant.department)
        )
        info_parts.append(dept_value)

    if info_parts:
        result_parts.append(" - " + ", ".join(info_parts))

    # Add additional context if available (church or location)
    context_parts = []
    if participant.church:
        context_parts.append(participant.church)
    elif participant.country_and_city:
        context_parts.append(participant.country_and_city)

    if context_parts:
        result_parts.append(f" | {context_parts[0]}")

    labels = SearchResultLabels.for_language(language)
    not_available = labels["not_available"]

    # Append accommodation info: Floor and Room Number
    floor_raw = getattr(participant, "floor", None)
    floor_display = str(floor_raw) if floor_raw not in (None, "") else not_available
    room_raw = getattr(participant, "room_number", None)
    room_display = str(room_raw) if room_raw not in (None, "") else not_available
    result_parts.append(
        f" | {labels['floor']}: {floor_display}, {labels['room']}: {room_display}"
    )

    # Append demographic info: Date of Birth and Age
    date_of_birth_val = getattr(participant, "date_of_birth", None)
    if date_of_birth_val is not None:
        if language == "ru":
            date_of_birth_display = date_of_birth_val.strftime("%d.%m.%Y")
        else:
            date_of_birth_display = Participant._format_date_of_birth(date_of_birth_val)
    else:
        date_of_birth_display = not_available

    age_raw = getattr(participant, "age", None)
    if isinstance(age_raw, (int, str)) and age_raw != "":
        try:
            age_value = int(age_raw)
            age_display = SearchResultLabels.format_age(age_value, language)
        except (TypeError, ValueError):
            age_display = str(age_raw)
    else:
        age_display = not_available

    result_parts.append(
        f" | {labels['date_of_birth']}: {date_of_birth_display} | {labels['age']}: {age_display}"
    )

    # Add ChurchLeader if available
    if participant.church_leader:
        church_leader_escaped = (
            participant.church_leader.replace("[", r"\[")
            .replace("]", r"\]")
            .replace("*", r"\*")
            .replace("_", r"\_")
            .replace("`", r"\`")
        )
        result_parts.append(f" | {labels['leader']}: {church_leader_escaped}")

    # Add TableName only if role is CANDIDATE
    participant_role = (
        (
            participant.role.value
            if hasattr(participant.role, "value")
            else str(participant.role)
        )
        if participant.role
        else None
    )

    if participant_role == "CANDIDATE" and participant.table_name:
        table_name_escaped = (
            participant.table_name.replace("[", r"\[")
            .replace("]", r"\]")
            .replace("*", r"\*")
            .replace("_", r"\_")
            .replace("`", r"\`")
        )
        result_parts.append(f" | {labels['table']}: {table_name_escaped}")

    # Add truncated Notes if available
    if participant.notes:
        notes_truncated = participant.notes[:50].replace("\n", " ").replace("\r", "")
        notes_escaped = (
            notes_truncated.replace("[", r"\[")
            .replace("]", r"\]")
            .replace("*", r"\*")
            .replace("_", r"\_")
            .replace("`", r"\`")
        )
        if len(participant.notes) > 50:
            notes_escaped += "..."
        result_parts.append(f" | {labels['notes']}: {notes_escaped}")

    return "".join(result_parts)


def format_participant_full(participant: Participant, language: str = "ru") -> str:
    """
    Format full participant details for display during edit/save flows.

    Shows all relevant fields with Russian labels and friendly values
    (gender/role/payment status translated), keeping output plain text.

    Args:
        participant: Participant instance to format
        language: Display language preference (currently only 'ru' supported)

    Returns:
        Multi-line string with all participant details
    """
    # Russian labels and icons
    labels = {
        "full_name_ru": "👤 Имя (русское)",
        "full_name_en": "🌍 Имя (английское)",
        "church": "⛪ Церковь",
        "country_and_city": "📍 Местоположение",
        "contact_information": "📞 Контакты",
        "submitted_by": "👨‍💼 Кто подал",
        "gender": "👫 Пол",
        "size": "👕 Размер",
        "role": "👥 Роль",
        "department": "📋 Департамент",
        "payment_amount": "💵 Сумма платежа",
        "payment_status": "💳 Статус оплаты",
        "payment_date": "📅 Дата оплаты",
        "floor": "🏢 Этаж",
        "room_number": "🚪 Номер комнаты",
        "date_of_birth": "🎂 Дата рождения",
        "age": "🔢 Возраст",
        "church_leader": "🧑‍💼 Лидер церкви",
        "table_name": "🪑 Название стола",
        "notes": "📝 Заметки",
    }

    def value_or_na(val: object) -> str:
        return str(val) if val not in (None, "") else "Не указано"

    def rus_gender(val: object) -> str:
        if val is None:
            return "Не указано"
        v = val.value if hasattr(val, "value") else val
        return (
            "Мужской"
            if v == Gender.MALE.value
            else ("Женский" if v == Gender.FEMALE.value else value_or_na(v))
        )

    def rus_role(val: object) -> str:
        if val is None:
            return "Не указано"
        v = val.value if hasattr(val, "value") else val
        return (
            "Кандидат"
            if v == Role.CANDIDATE.value
            else ("Команда" if v == Role.TEAM.value else value_or_na(v))
        )

    def rus_payment_status(val: object) -> str:
        if val is None:
            return "Не указано"
        v = val.value if hasattr(val, "value") else val
        if v == PaymentStatus.PAID.value:
            return "Оплачено"
        if v == PaymentStatus.PARTIAL.value:
            return "Частично"
        if v == PaymentStatus.UNPAID.value:
            return "Не оплачено"
        return value_or_na(v)

    lines = []
    # Names and general info
    lines.append(f"{labels['full_name_ru']}: {value_or_na(participant.full_name_ru)}")
    lines.append(f"{labels['full_name_en']}: {value_or_na(participant.full_name_en)}")
    lines.append(f"{labels['church']}: {value_or_na(participant.church)}")
    lines.append(
        f"{labels['country_and_city']}: {value_or_na(participant.country_and_city)}"
    )
    lines.append(
        f"{labels['contact_information']}: {value_or_na(participant.contact_information)}"
    )
    lines.append(f"{labels['submitted_by']}: {value_or_na(participant.submitted_by)}")

    # Enums and selections
    lines.append(f"{labels['gender']}: {rus_gender(participant.gender)}")
    lines.append(
        f"{labels['size']}: {value_or_na(getattr(participant.size, 'value', participant.size))}"
    )
    lines.append(f"{labels['role']}: {rus_role(participant.role)}")
    lines.append(
        f"{labels['department']}: {value_or_na(getattr(participant.department, 'value', participant.department))}"
    )

    # Payment info
    lines.append(
        f"{labels['payment_amount']}: {value_or_na(participant.payment_amount)}"
    )
    lines.append(
        f"{labels['payment_status']}: {rus_payment_status(participant.payment_status)}"
    )
    # Format date to ISO if present
    pay_date_val: Optional[date] = getattr(participant, "payment_date", None)
    pay_date = pay_date_val.isoformat() if pay_date_val is not None else None
    lines.append(f"{labels['payment_date']}: {value_or_na(pay_date)}")

    # Accommodation info
    lines.append(
        f"{labels['floor']}: {value_or_na(getattr(participant, 'floor', None))}"
    )
    lines.append(
        f"{labels['room_number']}: {value_or_na(getattr(participant, 'room_number', None))}"
    )

    # Demographic info
    date_of_birth_val = getattr(participant, "date_of_birth", None)
    if date_of_birth_val is not None:
        # Use European format (DD/MM/YYYY) for Russian full displays
        date_of_birth_display = date_of_birth_val.strftime("%d/%m/%Y")
    else:
        date_of_birth_display = "Не указано"
    lines.append(f"{labels['date_of_birth']}: {date_of_birth_display}")

    lines.append(f"{labels['age']}: {value_or_na(getattr(participant, 'age', None))}")

    # New fields
    lines.append(f"{labels['church_leader']}: {value_or_na(participant.church_leader)}")

    # TableName only if role is CANDIDATE
    participant_role = (
        (
            participant.role.value
            if hasattr(participant.role, "value")
            else str(participant.role)
        )
        if participant.role
        else None
    )

    if participant_role == "CANDIDATE":
        lines.append(f"{labels['table_name']}: {value_or_na(participant.table_name)}")

    # Full multiline Notes (escaped)
    if participant.notes:
        notes_escaped = (
            participant.notes.replace("*", r"\*")
            .replace("_", r"\_")
            .replace("[", r"\[")
            .replace("]", r"\]")
            .replace("`", r"\`")
        )
        lines.append(f"{labels['notes']}: {notes_escaped}")
    else:
        lines.append(f"{labels['notes']}: Не указано")

    return "\n".join(lines)


def normalize_russian(text: str) -> str:
    """
    Normalize Russian text for better fuzzy matching.

    Applies character normalizations:
    - ё -> е (yo -> ye)
    - й -> и (short i -> i)
    - Converts to lowercase for case-insensitive matching

    Args:
        text: Input text to normalize

    Returns:
        Normalized text string
    """
    if not text:
        return ""

    # Normalize Russian characters and convert to lowercase
    normalized = text.lower()
    normalized = normalized.replace("ё", "е")
    normalized = normalized.replace("й", "и")

    return normalized


@dataclass
class SearchResult:
    """
    Result of a fuzzy search operation.

    Contains the matched participant and similarity score for ranking.
    """

    participant: Participant
    similarity_score: float

    def __lt__(self, other: "SearchResult") -> bool:
        """Enable sorting by similarity score (descending)."""
        return self.similarity_score > other.similarity_score


class SearchService:
    """
    Service for fuzzy participant name searching and room/floor searches.

    Uses rapidfuzz token_set_ratio algorithm for word-order independent matching
    with Russian character normalization. Also provides repository-based searches
    for room and floor functionality.
    """

    def __init__(
        self,
        similarity_threshold: float = 0.8,
        max_results: int = 5,
        repository: Optional[ParticipantRepository] = None,
    ):
        """
        Initialize search service with configuration.

        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0)
            max_results: Maximum number of results to return
            repository: Optional participant repository for room/floor searches
        """
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        self.repository = repository
        logger.info(
            f"Initialized SearchService (threshold={similarity_threshold}, max_results={max_results})"
        )

    def search_participants(
        self, query: str, participants: List[Participant]
    ) -> List[SearchResult]:
        """
        Search participants by name using fuzzy matching.

        Args:
            query: Search query (name or partial name)
            participants: List of participants to search through

        Returns:
            List of SearchResult objects sorted by similarity score (descending)
        """
        if not query or not query.strip():
            return []

        if not participants:
            return []

        query_normalized = normalize_russian(query.strip())
        results = []

        logger.debug(
            f"Searching for '{query}' (normalized: '{query_normalized}') among {len(participants)} participants"
        )

        for participant in participants:
            # Get the best similarity score from Russian and English names
            max_score = 0.0

            # Check Russian name
            if participant.full_name_ru:
                ru_normalized = normalize_russian(participant.full_name_ru)
                ru_score = fuzz.token_set_ratio(query_normalized, ru_normalized) / 100.0
                max_score = max(max_score, ru_score)

            # Check English name
            if participant.full_name_en:
                en_normalized = normalize_russian(participant.full_name_en)
                en_score = fuzz.token_set_ratio(query_normalized, en_normalized) / 100.0
                max_score = max(max_score, en_score)

            # Add to results if meets threshold
            if max_score >= self.similarity_threshold:
                results.append(
                    SearchResult(participant=participant, similarity_score=max_score)
                )

        # Sort by similarity score descending and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        limited_results = results[: self.max_results]

        logger.debug(
            f"Found {len(limited_results)} matches above threshold {self.similarity_threshold}"
        )
        return limited_results

    def search_participants_enhanced(
        self, query: str, participants: List[Participant]
    ) -> List[SearchResult]:
        """
        Enhanced search with language detection and multi-field matching.

        Uses language detection to optimize search strategy and searches individual
        name parts (first/last names) in addition to full names.

        Args:
            query: Search query (name or partial name)
            participants: List of participants to search through

        Returns:
            List of SearchResult objects sorted by similarity score (descending)
        """
        if not query or not query.strip():
            return []

        if not participants:
            return []

        query_normalized = normalize_russian(query.strip())
        detected_lang = detect_language(query.strip())
        results = []

        logger.debug(
            f"Enhanced search for '{query}' (lang: {detected_lang}, normalized: '{query_normalized}') among {len(participants)} participants"
        )

        for participant in participants:
            max_score = 0.0

            # Get fields to search based on detected language
            if detected_lang == "ru":
                primary_field: Optional[str] = participant.full_name_ru
                secondary_field: Optional[str] = participant.full_name_en
            else:
                primary_field = participant.full_name_en
                secondary_field = participant.full_name_ru

            # Search in primary field (full name and individual parts)
            if primary_field:
                # Full name search
                primary_normalized = normalize_russian(primary_field)
                full_score = (
                    fuzz.token_set_ratio(query_normalized, primary_normalized) / 100.0
                )
                max_score = max(max_score, full_score)

                # Individual name parts search
                name_parts = parse_name_parts(primary_field)
                for part in name_parts:
                    part_normalized = normalize_russian(part)
                    part_score = (
                        fuzz.token_set_ratio(query_normalized, part_normalized) / 100.0
                    )
                    max_score = max(max_score, part_score)

            # Search in secondary field (lower priority)
            if (
                secondary_field and max_score < 0.9
            ):  # Only if no excellent match in primary
                # Full name search
                secondary_normalized = normalize_russian(secondary_field)
                secondary_full_score = (
                    fuzz.token_set_ratio(query_normalized, secondary_normalized) / 100.0
                )
                max_score = max(
                    max_score, secondary_full_score * 0.9
                )  # Slight penalty for secondary field

                # Individual name parts search
                secondary_parts = parse_name_parts(secondary_field)
                for part in secondary_parts:
                    part_normalized = normalize_russian(part)
                    part_score = (
                        fuzz.token_set_ratio(query_normalized, part_normalized) / 100.0
                    )
                    max_score = max(
                        max_score, part_score * 0.9
                    )  # Slight penalty for secondary field

            # Add to results if meets threshold
            if max_score >= self.similarity_threshold:
                results.append(
                    SearchResult(participant=participant, similarity_score=max_score)
                )

        # Sort by similarity score descending and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        limited_results = results[: self.max_results]

        logger.debug(
            f"Enhanced search found {len(limited_results)} matches above threshold {self.similarity_threshold}"
        )
        return limited_results

    def get_similarity_score(self, query: str, target: str) -> float:
        """
        Get similarity score between two strings.

        Args:
            query: Query string
            target: Target string to compare against

        Returns:
            Similarity score (0.0-1.0)
        """
        if not query or not target:
            return 0.0

        query_norm = normalize_russian(query)
        target_norm = normalize_russian(target)

        return fuzz.token_set_ratio(query_norm, target_norm) / 100.0

    async def search_by_room(self, room_number: str) -> List[Participant]:
        """
        Search participants by room number using the repository.

        Args:
            room_number: Room number to search for

        Returns:
            List of participants in the specified room

        Raises:
            ValueError: If room_number is None or empty
            RuntimeError: If repository is not configured
        """
        if not room_number or not room_number.strip():
            raise ValueError("Room number must be provided")

        if not self.repository:
            raise RuntimeError("Repository must be configured for room searches")

        logger.debug(f"Searching participants by room: {room_number}")
        return await self.repository.find_by_room_number(room_number.strip())

    async def search_by_floor(self, floor: Union[int, str]) -> List[Participant]:
        """
        Search participants by floor using the repository.

        Args:
            floor: Floor number or identifier to search for

        Returns:
            List of participants on the specified floor

        Raises:
            ValueError: If floor is None or empty
            RuntimeError: If repository is not configured
        """
        if floor is None or (isinstance(floor, str) and not floor.strip()):
            raise ValueError("Floor must be provided")

        if not self.repository:
            raise RuntimeError("Repository must be configured for floor searches")

        logger.debug(f"Searching participants by floor: {floor}")
        return await self.repository.find_by_floor(floor)

    async def search_by_room_formatted(
        self, room_number: str, language: str = "ru"
    ) -> List[str]:
        """
        Search participants by room number and return formatted results.

        Args:
            room_number: Room number to search for
            language: Display language preference ("ru" or "en")

        Returns:
            List of formatted participant strings

        Raises:
            ValueError: If room_number is None or empty
            RuntimeError: If repository is not configured
        """
        participants = await self.search_by_room(room_number)

        formatted_results = []
        for participant in participants:
            formatted_result = format_participant_result(participant, language)
            formatted_results.append(formatted_result)

        return formatted_results

    async def get_available_floors(self) -> List[int]:
        """
        Get list of unique floors that contain participants.

        Retrieves all floors from the repository that have at least one participant,
        returning them sorted in ascending order. Handles all repository errors
        gracefully by logging and returning empty list.

        Returns:
            List of unique floor numbers (as integers) that contain participants,
            sorted in ascending order. Returns empty list if no floors found
            or if any error occurs.

        Raises:
            RuntimeError: If repository is not configured
        """
        if not self.repository:
            raise RuntimeError("Repository not configured for floor operations")

        try:
            floors = await self.repository.get_available_floors()
            logger.info(f"Retrieved {len(floors)} unique floors with participants")
            return floors
        except Exception as e:
            logger.warning(f"Failed to retrieve available floors: {e}")
            return []


def format_match_quality(similarity_score: float) -> str:
    """
    Convert similarity score to human-readable Russian match quality label.

    Transforms raw percentage scores into user-friendly Russian labels for
    better search result presentation.

    Args:
        similarity_score: Similarity score from 0.0 to 1.0

    Returns:
        Russian match quality label:
        - >= 0.99: "Точное совпадение" (Exact match)
        - 0.85-0.98: "Высокое совпадение" (High match)
        - 0.70-0.84: "Совпадение" (Match)
        - < 0.70: "Слабое совпадение" (Low match)
    """
    # Handle edge cases
    if similarity_score < 0:
        similarity_score = 0.0
    elif similarity_score > 1.0:
        similarity_score = 1.0

    # Convert to Russian match quality labels
    if similarity_score >= 0.99:
        return "Точное совпадение"
    elif similarity_score >= 0.85:
        return "Высокое совпадение"
    elif similarity_score >= 0.70:
        return "Совпадение"
    else:
        return "Слабое совпадение"
