"""
Unit tests for SearchService with fuzzy matching capabilities.

Tests the search service that provides fuzzy name matching using rapidfuzz
library with Russian/English name normalization and similarity scoring.
"""

from typing import List, Tuple
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.models.participant import Department, Participant, Role
from src.services.search_service import (
    SearchResult,
    SearchService,
    detect_language,
    format_participant_full,
    format_participant_result,
    normalize_russian,
    parse_name_parts,
)


class TestLanguageDetection:
    """Test automatic language detection for input strings."""

    def test_detect_russian_cyrillic(self):
        """Test detection of Russian/Cyrillic text."""
        assert detect_language("Александр") == "ru"
        assert detect_language("Басис") == "ru"
        assert detect_language("Лия Глеева") == "ru"
        assert detect_language("АЛЕКСАНДР БАСИС") == "ru"
        assert detect_language("алёксей петров") == "ru"

    def test_detect_english_latin(self):
        """Test detection of English/Latin text."""
        assert detect_language("Alexander") == "en"
        assert detect_language("Basis") == "en"
        assert detect_language("Liya Gleyeva") == "en"
        assert detect_language("ALEXANDER BASIS") == "en"
        assert detect_language("john smith") == "en"

    def test_detect_mixed_defaults_to_predominant(self):
        """Test mixed language input defaults to predominant language."""
        assert detect_language("Александр Smith") == "ru"  # 9 Cyrillic vs 5 Latin
        assert detect_language("John Иванов") == "ru"  # 6 Cyrillic vs 4 Latin
        assert detect_language("John Smith Б") == "en"  # 9 Latin vs 1 Cyrillic
        assert detect_language("A Б В Г Д") == "ru"  # 4 Cyrillic vs 1 Latin

    def test_detect_empty_and_special_chars(self):
        """Test detection with empty strings and special characters."""
        assert detect_language("") == "en"  # Default to English
        assert detect_language("   ") == "en"  # Whitespace defaults to English
        assert detect_language("123 456") == "en"  # Numbers default to English
        assert detect_language("@#$%") == "en"  # Special chars default to English

    def test_detect_numbers_with_text(self):
        """Test detection with numbers mixed with text."""
        assert detect_language("Александр 123") == "ru"
        assert detect_language("Alexander 456") == "en"


class TestNameParsing:
    """Test name parsing functionality for multi-field search."""

    def test_parse_russian_full_names(self):
        """Test parsing Russian full names into first/last parts."""
        assert parse_name_parts("Александр Иванов") == ["Александр", "Иванов"]
        assert parse_name_parts("Мария Петровна Сидорова") == [
            "Мария",
            "Петровна",
            "Сидорова",
        ]
        assert parse_name_parts("Иван") == ["Иван"]  # Single name

    def test_parse_english_full_names(self):
        """Test parsing English full names into first/last parts."""
        assert parse_name_parts("Alexander Ivanov") == ["Alexander", "Ivanov"]
        assert parse_name_parts("Mary Jane Smith") == ["Mary", "Jane", "Smith"]
        assert parse_name_parts("John") == ["John"]  # Single name

    def test_parse_with_extra_whitespace(self):
        """Test parsing with extra whitespace handling."""
        assert parse_name_parts("  Александр   Иванов  ") == ["Александр", "Иванов"]
        assert parse_name_parts("Alexander\t\tIvanov") == ["Alexander", "Ivanov"]

    def test_parse_empty_and_invalid(self):
        """Test parsing edge cases."""
        assert parse_name_parts("") == []
        assert parse_name_parts("   ") == []
        assert parse_name_parts("123") == ["123"]  # Numbers treated as name parts


class TestMultiFieldSearch:
    """Test multi-field search functionality."""

    def test_enhanced_search_russian_first_name(self):
        """Test searching by Russian first name matches both full names."""
        service = SearchService()
        participants = [
            Participant(
                full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
            ),
            Participant(full_name_ru="Мария Петрова", full_name_en="Maria Petrova"),
            Participant(
                full_name_ru="Александра Сидорова", full_name_en="Alexandra Sidorova"
            ),
        ]

        results = service.search_participants_enhanced("Александр", participants)

        # Should find both "Александр Иванов" and potentially "Александра" as fuzzy match
        assert len(results) >= 1
        assert any("Александр Иванов" in r.participant.full_name_ru for r in results)

    def test_enhanced_search_russian_last_name(self):
        """Test searching by Russian last name."""
        service = SearchService()
        participants = [
            Participant(
                full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
            ),
            Participant(full_name_ru="Петр Иванов", full_name_en="Peter Ivanov"),
            Participant(full_name_ru="Мария Петрова", full_name_en="Maria Petrova"),
        ]

        results = service.search_participants_enhanced("Иванов", participants)

        # Should find both participants with last name "Иванов"
        assert len(results) >= 2
        ivanov_results = [r for r in results if "Иванов" in r.participant.full_name_ru]
        assert len(ivanov_results) >= 2

    def test_enhanced_search_english_first_name(self):
        """Test searching by English first name."""
        service = SearchService()
        participants = [
            Participant(
                full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
            ),
            Participant(full_name_ru="Мария Петрова", full_name_en="Maria Petrova"),
            Participant(full_name_ru="Алекс Смирнов", full_name_en="Alex Smirnov"),
        ]

        results = service.search_participants_enhanced("Alexander", participants)

        # Should find "Alexander Ivanov" and potentially "Alex" as fuzzy match
        assert len(results) >= 1
        assert any(
            "Alexander Ivanov" in (r.participant.full_name_en or "") for r in results
        )

    def test_enhanced_search_language_detection_optimization(self):
        """Test that language detection optimizes search fields."""
        service = SearchService()
        participants = [
            Participant(
                full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
            ),
            Participant(full_name_ru="Мария Петрова", full_name_en="Maria Petrova"),
        ]

        # Russian input should focus on Russian fields
        ru_results = service.search_participants_enhanced("Александр", participants)
        # English input should focus on English fields
        en_results = service.search_participants_enhanced("Alexander", participants)

        # Both should find results, potentially with different scores
        assert len(ru_results) >= 1
        assert len(en_results) >= 1


class TestRichResultFormatting:
    """Test rich result formatting for participant information display."""

    def test_format_participant_basic_info(self):
        """Test basic participant formatting with name only."""
        participant = Participant(
            full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
        )

        result = format_participant_result(participant, "ru")

        assert "Александр Иванов" in result
        assert "Alexander Ivanov" in result

    def test_format_participant_with_role_and_department(self):
        """Test formatting with role and department information."""
        participant = Participant(
            full_name_ru="Мария Петрова",
            full_name_en="Maria Petrova",
            role=Role.TEAM,
            department=Department.KITCHEN,
        )

        result = format_participant_result(participant, "ru")

        assert "Мария Петрова" in result
        assert "TEAM" in result
        assert "Kitchen" in result

    def test_format_participant_english_priority(self):
        """Test formatting with English language priority."""
        participant = Participant(
            full_name_ru="Иван Смирнов",
            full_name_en="Ivan Smirnov",
            role=Role.CANDIDATE,
            department=Department.MEDIA,
        )

        result = format_participant_result(participant, "en")

        # Should prioritize English name first
        assert "Ivan Smirnov" in result
        assert "Иван Смирнов" in result  # But still include Russian
        assert "CANDIDATE" in result
        assert "Media" in result

    def test_format_participant_missing_fields(self):
        """Test formatting when some fields are missing."""
        participant = Participant(
            full_name_ru="Елена Козлова",
            role=Role.TEAM,
            # No full_name_en, no department
        )

        result = format_participant_result(participant, "ru")

        assert "Елена Козлова" in result
        assert "TEAM" in result
        # Should handle missing fields gracefully
        assert result is not None and len(result) > 0

    def test_format_participant_with_church_info(self):
        """Test formatting including church and location information."""
        participant = Participant(
            full_name_ru="Сергей Волков",
            full_name_en="Sergey Volkov",
            role=Role.CANDIDATE,
            department=Department.WORSHIP,
            church="St. Nicholas Cathedral",
            country_and_city="Moscow, Russia",
        )

        result = format_participant_result(participant, "ru")

        assert "Сергей Волков" in result
        assert "St. Nicholas Cathedral" in result or "Moscow, Russia" in result

    def test_format_participant_with_accommodation_fields(self):
        """Test Floor and Room Number fields display as 'Floor: X, Room: Y' when available."""
        participant = Participant(
            full_name_ru="Анна Морозова",
            full_name_en="Anna Morozova",
            floor=3,
            room_number="301A",
        )

        result = format_participant_result(participant, "ru")

        assert "Анна Морозова" in result
        assert "Anna Morozova" in result
        assert "Этаж: 3, Комната: 301A" in result

    def test_format_participant_accommodation_fields_with_na_fallbacks(self):
        """Test Floor and Room Number fields display as 'N/A' when not set in participant."""
        participant = Participant(
            full_name_ru="Михаил Кузнецов",
            full_name_en="Mikhail Kuznetsov",
            floor=None,
            room_number=None,
        )

        result = format_participant_result(participant, "ru")

        assert "Михаил Кузнецов" in result
        assert "Этаж: Не указано, Комната: Не указано" in result

    def test_format_participant_partial_accommodation_fields(self):
        """Test Floor and Room Number display with only one field set."""
        # Only floor set
        participant = Participant(
            full_name_ru="Ольга Белова", floor="Ground", room_number=None
        )

        result = format_participant_result(participant, "ru")
        assert "Этаж: Ground, Комната: Не указано" in result

        # Only room number set
        participant = Participant(
            full_name_ru="Дмитрий Орлов", floor=None, room_number="Suite 100"
        )

        result = format_participant_result(participant, "ru")
        assert "Этаж: Не указано, Комната: Suite 100" in result

    def test_format_participant_accommodation_with_empty_strings(self):
        """Test Floor and Room Number display handles empty strings as N/A."""
        participant = Participant(
            full_name_ru="Татьяна Жукова",
            floor="",  # Empty string should be N/A
            room_number="",  # Empty string should be N/A
        )

        result = format_participant_result(participant, "ru")
        assert "Этаж: Не указано, Комната: Не указано" in result

    def test_format_participant_accommodation_string_floor_alphanumeric_room(self):
        """Test Floor (string) and Room Number (alphanumeric) display correctly."""
        participant = Participant(
            full_name_ru="Максим Лебедев", floor="Basement", room_number="B12A"
        )

        result = format_participant_result(participant, "ru")
        assert "Этаж: Basement, Комната: B12A" in result

    def test_format_participant_complete_with_accommodation(self):
        """Test complete participant formatting including accommodation information."""
        participant = Participant(
            full_name_ru="Елена Николаева",
            full_name_en="Elena Nikolaeva",
            role=Role.TEAM,
            department=Department.ADMINISTRATION,
            church="Holy Trinity Church",
            floor=2,
            room_number="204",
        )

        result = format_participant_result(participant, "ru")

        # Verify all components are present
        assert "Елена Николаева" in result
        assert "Elena Nikolaeva" in result
        assert "TEAM" in result
        assert "Administration" in result
        assert "Holy Trinity Church" in result
        assert "Этаж: 2, Комната: 204" in result

    def test_format_participant_with_demographic_fields(self):
        """Test demographic fields display as 'Date of Birth: YYYY-MM-DD | Age: XX years' when available."""
        from datetime import date

        participant = Participant(
            full_name_ru="Петр Смирнов",
            full_name_en="Petr Smirnov",
            date_of_birth=date(1990, 5, 15),
            age=33,
        )

        result = format_participant_result(participant, "ru")

        assert "Петр Смирнов" in result
        assert "Petr Smirnov" in result
        assert "Дата рождения: 15.05.1990 | Возраст: 33 года" in result

    def test_format_participant_demographic_fields_with_na_fallbacks(self):
        """Test demographic fields display as 'N/A' when not set in participant."""
        participant = Participant(
            full_name_ru="Ольга Ковалева",
            full_name_en="Olga Kovaleva",
            # No demographic data
        )

        result = format_participant_result(participant, "ru")

        assert "Ольга Ковалева" in result
        assert "Дата рождения: Не указано | Возраст: Не указано" in result

    def test_format_participant_partial_demographic_fields(self):
        """Test demographic fields display with mixed availability (some N/A, some values)."""
        participant = Participant(
            full_name_ru="Игорь Кузнецов",
            full_name_en="Igor Kuznetsov",
            age=29,
            # date_of_birth not set
        )

        result = format_participant_result(participant, "ru")

        assert "Игорь Кузнецов" in result
        assert "Дата рождения: Не указано | Возраст: 29 лет" in result


class TestRussianNormalization:
    """Test Russian character normalization for fuzzy matching."""

    def test_normalize_russian_basic(self):
        """Test basic Russian character normalization."""
        # ё -> е, й -> и, case insensitive
        assert normalize_russian("Алёксей") == "алексеи"
        assert normalize_russian("АЛЁКСЕЙ") == "алексеи"
        assert normalize_russian("Александр Иванович") == "александр иванович"

    def test_normalize_russian_special_chars(self):
        """Test normalization with special Russian characters."""
        assert normalize_russian("Сергей") == "сергеи"
        assert normalize_russian("Андрей") == "андреи"
        assert normalize_russian("Николай") == "николаи"

    def test_normalize_russian_english_passthrough(self):
        """Test that English characters pass through unchanged."""
        assert normalize_russian("Alexander Smith") == "alexander smith"
        assert normalize_russian("JOHN DOE") == "john doe"

    def test_normalize_russian_mixed_text(self):
        """Test normalization of mixed Russian-English text."""
        assert normalize_russian("Алёксей Smith") == "алексеи smith"


class TestSearchResult:
    """Test SearchResult data class."""

    def test_search_result_creation(self):
        """Test SearchResult creation with participant and score."""
        participant = Participant(full_name_ru="Иван Иванов")
        result = SearchResult(participant=participant, similarity_score=0.85)

        assert result.participant == participant
        assert result.similarity_score == 0.85

    def test_search_result_ordering(self):
        """Test SearchResult comparison for sorting by score."""
        p1 = Participant(full_name_ru="Иван")
        p2 = Participant(full_name_ru="Петр")

        result1 = SearchResult(participant=p1, similarity_score=0.85)
        result2 = SearchResult(participant=p2, similarity_score=0.90)

        results = [result1, result2]
        sorted_results = sorted(results, key=lambda x: x.similarity_score, reverse=True)

        assert sorted_results[0].similarity_score == 0.90
        assert sorted_results[1].similarity_score == 0.85


class TestSearchService:
    """Test fuzzy search service functionality."""

    @pytest.fixture
    def sample_participants(self) -> List[Participant]:
        """Sample participants for testing."""
        return [
            Participant(
                full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"
            ),
            Participant(full_name_ru="Алёксей Петров", full_name_en="Alexey Petrov"),
            Participant(full_name_ru="Мария Сидорова", full_name_en="Maria Sidorova"),
            Participant(full_name_ru="Иван Смирнов", full_name_en="Ivan Smirnov"),
            Participant(full_name_ru="Елена Козлова", full_name_en="Elena Kozlova"),
        ]

    def test_search_service_initialization(self):
        """Test SearchService initialization with default threshold."""
        service = SearchService()
        assert service.similarity_threshold == 0.8
        assert service.max_results == 5

    def test_search_service_custom_params(self):
        """Test SearchService initialization with custom parameters."""
        service = SearchService(similarity_threshold=0.75, max_results=3)
        assert service.similarity_threshold == 0.75
        assert service.max_results == 3

    def test_search_exact_match_russian(self, sample_participants):
        """Test exact match in Russian name."""
        service = SearchService()
        results = service.search_participants("Александр Иванов", sample_participants)

        assert len(results) >= 1
        assert results[0].similarity_score >= 0.95
        assert "Александр Иванов" in results[0].participant.full_name_ru

    def test_search_exact_match_english(self, sample_participants):
        """Test exact match in English name."""
        service = SearchService()
        results = service.search_participants("Alexander Ivanov", sample_participants)

        assert len(results) >= 1
        assert results[0].similarity_score >= 0.95
        assert "Alexander Ivanov" in results[0].participant.full_name_en

    def test_search_fuzzy_match_russian(self, sample_participants):
        """Test fuzzy matching with Russian names."""
        service = SearchService()
        # Test with typo: "Алёксей" vs "Алексей" (ё->е normalization)
        results = service.search_participants("Алексей Петров", sample_participants)

        assert len(results) >= 1
        assert results[0].similarity_score >= 0.8
        assert "Алёксей Петров" in results[0].participant.full_name_ru

    def test_search_partial_name_match(self, sample_participants):
        """Test partial name matching."""
        service = SearchService(
            similarity_threshold=0.7
        )  # Lower threshold for partial matches
        results = service.search_participants("Александр", sample_participants)

        assert len(results) >= 1
        assert results[0].similarity_score >= 0.7
        assert "Александр" in results[0].participant.full_name_ru

    def test_search_below_threshold_filtered(self, sample_participants):
        """Test that results below similarity threshold are filtered out."""
        service = SearchService(similarity_threshold=0.9)
        results = service.search_participants(
            "Completely Different Name", sample_participants
        )

        # Should return empty results as no matches meet 0.9 threshold
        assert len(results) == 0

    def test_search_max_results_limit(self, sample_participants):
        """Test that results are limited by max_results parameter."""
        # Add more participants with similar names
        extended_participants = sample_participants + [
            Participant(full_name_ru="Александра Иванова"),
            Participant(full_name_ru="Александрия Иванович"),
            Participant(full_name_ru="Саша Иванов"),
        ]

        service = SearchService(similarity_threshold=0.5, max_results=3)
        results = service.search_participants("Александр", extended_participants)

        assert len(results) <= 3

    def test_search_results_sorted_by_score(self, sample_participants):
        """Test that results are sorted by similarity score descending."""
        service = SearchService()
        results = service.search_participants("Алекс", sample_participants)

        if len(results) > 1:
            # Verify descending order
            for i in range(len(results) - 1):
                assert results[i].similarity_score >= results[i + 1].similarity_score

    def test_search_empty_query(self, sample_participants):
        """Test search with empty query string."""
        service = SearchService()
        results = service.search_participants("", sample_participants)

        assert len(results) == 0

    def test_search_empty_participants_list(self):
        """Test search with empty participants list."""
        service = SearchService()
        results = service.search_participants("Александр", [])

        assert len(results) == 0

    def test_search_case_insensitive(self, sample_participants):
        """Test that search is case insensitive."""
        service = SearchService()

        results_lower = service.search_participants(
            "александр иванов", sample_participants
        )
        results_upper = service.search_participants(
            "АЛЕКСАНДР ИВАНОВ", sample_participants
        )
        results_mixed = service.search_participants(
            "Александр ИВАНОВ", sample_participants
        )

        # All should find the same participant
        assert len(results_lower) >= 1
        assert len(results_upper) >= 1
        assert len(results_mixed) >= 1

        # Should have similar scores
        assert (
            abs(results_lower[0].similarity_score - results_upper[0].similarity_score)
            < 0.1
        )


class TestMatchQualityFormatting:
    """Test match quality label formatting for enhanced search display."""

    def test_format_match_quality_exact_match(self):
        """Test formatting exact match (100%) to Russian label."""
        from src.services.search_service import format_match_quality

        # 100% should be "Точное совпадение"
        assert format_match_quality(1.0) == "Точное совпадение"
        assert format_match_quality(0.99) == "Точное совпадение"

    def test_format_match_quality_high_match(self):
        """Test formatting high quality match (85-98%) to Russian label."""
        from src.services.search_service import format_match_quality

        # 85-98% should be "Высокое совпадение"
        assert format_match_quality(0.98) == "Высокое совпадение"
        assert format_match_quality(0.90) == "Высокое совпадение"
        assert format_match_quality(0.85) == "Высокое совпадение"

    def test_format_match_quality_medium_match(self):
        """Test formatting medium quality match (70-84%) to Russian label."""
        from src.services.search_service import format_match_quality

        # 70-84% should be "Совпадение"
        assert format_match_quality(0.84) == "Совпадение"
        assert format_match_quality(0.80) == "Совпадение"
        assert format_match_quality(0.70) == "Совпадение"

    def test_format_match_quality_low_match(self):
        """Test formatting low quality match (<70%) to Russian label."""
        from src.services.search_service import format_match_quality

        # <70% should be "Слабое совпадение"
        assert format_match_quality(0.69) == "Слабое совпадение"
        assert format_match_quality(0.50) == "Слабое совпадение"
        assert format_match_quality(0.30) == "Слабое совпадение"

    def test_format_match_quality_edge_cases(self):
        """Test formatting edge cases for match quality labels."""
        from src.services.search_service import format_match_quality

        # Test boundaries
        assert format_match_quality(0.0) == "Слабое совпадение"
        assert format_match_quality(1.0) == "Точное совпадение"

    def test_format_match_quality_invalid_input(self):
        """Test handling of invalid input for match quality formatting."""
        from src.services.search_service import format_match_quality

        # Should handle negative values gracefully
        assert format_match_quality(-0.1) == "Слабое совпадение"
        # Should handle values > 1.0 gracefully
        assert format_match_quality(1.1) == "Точное совпадение"


class TestSearchServiceIntegration:
    """Integration tests for SearchService."""

    def test_search_with_rapidfuzz_integration(self):
        """Test that rapidfuzz library is properly integrated."""
        service = SearchService()
        participants = [Participant(full_name_ru="Тест Участник")]

        # This should work without import errors
        results = service.search_participants("Тест", participants)
        assert isinstance(results, list)
        assert len(results) >= 1
        assert results[0].similarity_score > 0.8
        assert "Тест Участник" in results[0].participant.full_name_ru

        # Дополнительная проверка интеграции с rapidfuzz
        assert hasattr(service, "similarity_threshold")
        assert service.similarity_threshold > 0


class TestRoomFloorSearchService:
    """Test class for room and floor search service methods."""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository for testing service layer."""
        repo = Mock()
        repo.find_by_room_number = AsyncMock()
        repo.find_by_floor = AsyncMock()
        return repo

    @pytest.fixture
    def search_service_with_repo(self, mock_repository):
        """SearchService instance with mocked repository."""
        service = SearchService()
        service.repository = (
            mock_repository  # This will FAIL - no repository attribute exists
        )
        return service

    @pytest.mark.asyncio
    async def test_search_by_room_success(
        self, search_service_with_repo, mock_repository
    ):
        """Test successful room search with validation and formatting."""
        room_number = "205"
        mock_participants = [
            Participant(full_name_ru="Участник 1", room_number="205", floor=2),
            Participant(full_name_ru="Участник 2", room_number="205", floor=2),
        ]
        mock_repository.find_by_room_number.return_value = mock_participants

        result = await search_service_with_repo.search_by_room(room_number)

        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        mock_repository.find_by_room_number.assert_called_once_with("205")

    @pytest.mark.asyncio
    async def test_search_by_room_invalid_input(self, search_service_with_repo):
        """Test room search with invalid input raises ValueError."""
        with pytest.raises(ValueError, match="Room number must be provided"):
            await search_service_with_repo.search_by_room("")

        with pytest.raises(ValueError, match="Room number must be provided"):
            await search_service_with_repo.search_by_room(None)

    @pytest.mark.asyncio
    async def test_search_by_floor_success(
        self, search_service_with_repo, mock_repository
    ):
        """Test successful floor search with validation and grouping."""
        floor = 2
        mock_participants = [
            Participant(full_name_ru="Участник 1", room_number="201", floor=2),
            Participant(full_name_ru="Участник 2", room_number="205", floor=2),
        ]
        mock_repository.find_by_floor.return_value = mock_participants

        result = await search_service_with_repo.search_by_floor(floor)

        assert len(result) == 2
        assert all(isinstance(p, Participant) for p in result)
        mock_repository.find_by_floor.assert_called_once_with(2)

    @pytest.mark.asyncio
    async def test_search_by_floor_string_input(
        self, search_service_with_repo, mock_repository
    ):
        """Test floor search with string input (e.g., 'Ground')."""
        floor = "Ground"
        mock_participants = [
            Participant(full_name_ru="Участник 1", room_number="G01", floor="Ground")
        ]
        mock_repository.find_by_floor.return_value = mock_participants

        result = await search_service_with_repo.search_by_floor(floor)

        assert len(result) == 1
        mock_repository.find_by_floor.assert_called_once_with("Ground")

    @pytest.mark.asyncio
    async def test_search_by_floor_invalid_input(self, search_service_with_repo):
        """Test floor search with invalid input raises ValueError."""
        with pytest.raises(ValueError, match="Floor must be provided"):
            await search_service_with_repo.search_by_floor("")

        with pytest.raises(ValueError, match="Floor must be provided"):
            await search_service_with_repo.search_by_floor(None)

    @pytest.mark.asyncio
    async def test_search_by_room_with_formatting(
        self, search_service_with_repo, mock_repository
    ):
        """Test room search results are properly formatted."""
        room_number = "205"
        mock_participants = [
            Participant(
                full_name_ru="Участник Тест",
                room_number="205",
                floor=2,
                role=Role.CANDIDATE,
                department=Department.CHAPEL,
            )
        ]
        mock_repository.find_by_room_number.return_value = mock_participants

        result = await search_service_with_repo.search_by_room_formatted(room_number)

        assert len(result) == 1
        assert "Участник Тест" in result[0]
        assert "Этаж: 2, Комната: 205" in result[0]


class TestFullParticipantFormatting:
    """Test format_participant_full function with demographic fields."""

    def test_format_participant_full_with_demographic_fields(self):
        """Test that format_participant_full includes demographic fields with Russian labels."""
        from datetime import date

        participant = Participant(
            full_name_ru="Анна Петрова",
            full_name_en="Anna Petrova",
            church="Храм Христа Спасителя",
            date_of_birth=date(1985, 3, 20),
            age=39,
        )

        result = format_participant_full(participant, "ru")

        # Verify demographic fields are present with Russian labels
        assert "👤 Имя (русское): Анна Петрова" in result
        assert "⛪ Церковь: Храм Христа Спасителя" in result
        # Demographic fields should be included
        assert "🎂 Дата рождения: 20/03/1985" in result
        assert "🔢 Возраст: 39" in result

    def test_format_participant_full_demographic_fields_with_na_fallbacks(self):
        """Test that format_participant_full shows 'Не указано' for missing demographic fields."""
        participant = Participant(
            full_name_ru="Борис Козлов",
            full_name_en="Boris Kozlov",
            # No demographic data
        )

        result = format_participant_full(participant, "ru")

        # Verify demographic fields show "Не указано" when missing
        assert "🎂 Дата рождения: Не указано" in result
        assert "🔢 Возраст: Не указано" in result


class TestSearchServiceFloorDiscovery:
    """Test service layer floor discovery functionality."""

    @pytest.fixture
    def mock_repository(self):
        """Mock repository with floor discovery capabilities."""
        repository = Mock()
        repository.get_available_floors = AsyncMock()
        return repository

    @pytest.fixture
    def search_service(self, mock_repository):
        """SearchService instance with mock repository."""
        return SearchService(repository=mock_repository)

    @pytest.mark.asyncio
    async def test_get_available_floors_success(self, search_service, mock_repository):
        """Test successful floor discovery returns floors from repository."""
        # Mock repository returning floors
        mock_repository.get_available_floors.return_value = [1, 2, 3, 5]

        # This test should FAIL - method doesn't exist yet
        result = await search_service.get_available_floors()

        # Should return floors from repository
        assert result == [1, 2, 3, 5]
        mock_repository.get_available_floors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_floors_empty_result(
        self, search_service, mock_repository
    ):
        """Test floor discovery with empty result."""
        # Mock repository returning empty list
        mock_repository.get_available_floors.return_value = []

        result = await search_service.get_available_floors()

        assert result == []
        mock_repository.get_available_floors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_floors_repository_error(
        self, search_service, mock_repository
    ):
        """Test floor discovery handles repository errors gracefully."""
        from src.data.repositories.participant_repository import RepositoryError

        # Mock repository raising error
        mock_repository.get_available_floors.side_effect = RepositoryError(
            "Database connection failed"
        )

        # Should return empty list and log error, not raise exception
        result = await search_service.get_available_floors()

        assert result == []
        mock_repository.get_available_floors.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_available_floors_unexpected_error(
        self, search_service, mock_repository
    ):
        """Test floor discovery handles unexpected errors gracefully."""
        # Mock repository raising unexpected error
        mock_repository.get_available_floors.side_effect = Exception("Unexpected error")

        # Should return empty list and log error, not raise exception
        result = await search_service.get_available_floors()

        assert result == []
        mock_repository.get_available_floors.assert_called_once()
