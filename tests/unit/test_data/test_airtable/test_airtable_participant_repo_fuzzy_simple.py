"""
Simplified unit tests for AirtableParticipantRepository fuzzy search functionality.

Tests the fuzzy search method implementation with focus on actual functionality
rather than detailed mocking.
"""

from typing import List, Tuple
from unittest.mock import AsyncMock, Mock

import pytest

from src.data.airtable.airtable_participant_repo import (
    AirtableParticipantRepository,
    _PARTICIPANT_CACHE,
)
from src.data.repositories.participant_repository import RepositoryError
from src.models.participant import Participant


@pytest.fixture(autouse=True)
def reset_cache():
    _PARTICIPANT_CACHE.clear()
    yield
    _PARTICIPANT_CACHE.clear()


@pytest.fixture
def mock_airtable_client():
    """Fixture providing a mock AirtableClient."""
    client = Mock()
    client.config = Mock()
    client.config.base_id = "appSimpleBase"
    client.config.table_id = "tblSimple"
    client.config.table_name = "Participants"
    return client


@pytest.fixture
def repository(mock_airtable_client):
    """Fixture providing AirtableParticipantRepository with mock client."""
    return AirtableParticipantRepository(mock_airtable_client)


@pytest.fixture
def sample_participants():
    """Sample participants for fuzzy search testing."""
    return [
        Participant(
            record_id="rec1",
            full_name_ru="Александр Иванов",
            full_name_en="Alexander Ivanov",
        ),
        Participant(
            record_id="rec2",
            full_name_ru="Алёксей Петров",
            full_name_en="Alexey Petrov",
        ),
        Participant(
            record_id="rec3",
            full_name_ru="Мария Сидорова",
            full_name_en="Maria Sidorova",
        ),
    ]


class TestFuzzySearchBasicFunctionality:
    """Test basic fuzzy search functionality."""

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_method_exists(self, repository):
        """Test that search_by_name_fuzzy method exists."""
        assert hasattr(repository, "search_by_name_fuzzy")
        assert callable(repository.search_by_name_fuzzy)

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_empty_query(self, repository):
        """Test fuzzy search with empty query returns empty list."""
        repository.list_all = AsyncMock(return_value=[])

        result = await repository.search_by_name_fuzzy("")
        assert result == []

        result = await repository.search_by_name_fuzzy("  ")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_no_participants(self, repository):
        """Test fuzzy search with no participants in database."""
        repository.list_all = AsyncMock(return_value=[])

        result = await repository.search_by_name_fuzzy("test")
        assert result == []

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_returns_correct_type(
        self, repository, sample_participants
    ):
        """Test fuzzy search returns list of (Participant, float) tuples."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        # Search for exact match
        result = await repository.search_by_name_fuzzy("Александр Иванов")

        assert isinstance(result, list)

        # If there are results, check the tuple structure
        if result:
            participant, score = result[0]
            assert isinstance(participant, Participant)
            assert isinstance(score, float)
            assert 0.0 <= score <= 1.0

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_exact_match(
        self, repository, sample_participants
    ):
        """Test fuzzy search finds exact matches."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        result = await repository.search_by_name_fuzzy("Александр Иванов")

        # Should find at least one match
        assert len(result) >= 1

        # First result should have high score
        participant, score = result[0]
        assert score >= 0.9  # Very high similarity for exact match
        assert participant.full_name_ru == "Александр Иванов"

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_english_match(
        self, repository, sample_participants
    ):
        """Test fuzzy search finds English name matches."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        result = await repository.search_by_name_fuzzy("Alexander Ivanov")

        # Should find at least one match
        assert len(result) >= 1

        # First result should have high score
        participant, score = result[0]
        assert score >= 0.9
        assert participant.full_name_en == "Alexander Ivanov"

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_partial_match(
        self, repository, sample_participants
    ):
        """Test fuzzy search finds partial matches."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        # Search for just first name - should match but with lower score
        result = await repository.search_by_name_fuzzy("Александр", threshold=0.5)

        # Should find at least one match with relaxed threshold
        assert len(result) >= 1

        # Should find the participant with "Александр" in name
        found_alexander = any("Александр" in p.full_name_ru for p, _ in result)
        assert found_alexander

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_russian_normalization(
        self, repository, sample_participants
    ):
        """Test fuzzy search handles Russian character normalization."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        # Search for "Алексей" (normalized) should match "Алёксей" (with ё)
        result = await repository.search_by_name_fuzzy("Алексей Петров", threshold=0.8)

        # Should find the match due to normalization
        if result:
            participant, score = result[0]
            assert score >= 0.8
            assert participant.full_name_ru == "Алёксей Петров"

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_custom_threshold(
        self, repository, sample_participants
    ):
        """Test fuzzy search respects custom similarity threshold."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        # Search with very high threshold
        high_threshold_results = await repository.search_by_name_fuzzy(
            "Alex", threshold=0.95
        )

        # Search with lower threshold
        low_threshold_results = await repository.search_by_name_fuzzy(
            "Alex", threshold=0.3
        )

        # Lower threshold should return same or more results
        assert len(low_threshold_results) >= len(high_threshold_results)

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_result_limit(self, repository):
        """Test fuzzy search respects result limit."""
        # Create many similar participants
        many_participants = [
            Participant(record_id=f"rec{i}", full_name_ru=f"Александр {i}")
            for i in range(10)
        ]
        repository.list_all = AsyncMock(return_value=many_participants)

        # Search with limit of 3
        result = await repository.search_by_name_fuzzy(
            "Александр", threshold=0.5, limit=3
        )

        # Should return at most 3 results
        assert len(result) <= 3

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_results_sorted(
        self, repository, sample_participants
    ):
        """Test fuzzy search results are sorted by similarity score."""
        repository.list_all = AsyncMock(return_value=sample_participants)

        # Search that should return multiple results
        result = await repository.search_by_name_fuzzy("Alex", threshold=0.3)

        if len(result) > 1:
            # Verify results are sorted by score (descending)
            scores = [score for _, score in result]
            assert scores == sorted(scores, reverse=True)


class TestFuzzySearchErrorHandling:
    """Test error handling in fuzzy search."""

    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_repository_error(self, repository):
        """Test fuzzy search handles repository errors."""
        # Mock list_all to raise an exception
        repository.list_all = AsyncMock(side_effect=Exception("Database error"))

        with pytest.raises(RepositoryError):
            await repository.search_by_name_fuzzy("test")
