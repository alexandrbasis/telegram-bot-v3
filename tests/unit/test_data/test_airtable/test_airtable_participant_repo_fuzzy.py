"""
Unit tests for AirtableParticipantRepository fuzzy search functionality.

Tests the fuzzy search method implementation with various scenarios
including Russian/English name matching and similarity scoring.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import List, Tuple

from src.data.airtable.airtable_participant_repo import AirtableParticipantRepository
from src.data.airtable.airtable_client import AirtableClient, AirtableAPIError
from src.data.repositories.participant_repository import RepositoryError
from src.models.participant import Participant


@pytest.fixture
def mock_airtable_client():
    """Fixture providing a mock AirtableClient."""
    client = Mock(spec=AirtableClient)
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
            full_name_en="Alexander Ivanov"
        ),
        Participant(
            record_id="rec2", 
            full_name_ru="Алёксей Петров",
            full_name_en="Alexey Petrov"
        ),
        Participant(
            record_id="rec3",
            full_name_ru="Мария Сидорова", 
            full_name_en="Maria Sidorova"
        ),
        Participant(
            record_id="rec4",
            full_name_ru="Иван Смирнов",
            full_name_en="Ivan Smirnov"
        ),
    ]


class TestFuzzySearchMethodSignature:
    """Test fuzzy search method signature and basic behavior."""
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_method_exists(self, repository):
        """Test that search_by_name_fuzzy method exists with correct signature."""
        # Method should exist
        assert hasattr(repository, 'search_by_name_fuzzy')
        
        # Should be callable
        assert callable(repository.search_by_name_fuzzy)
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_default_parameters(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with default threshold and limit parameters."""
        # Mock list_all to return participants (not empty, so SearchService gets called)
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            # Should work with just query parameter
            results = await repository.search_by_name_fuzzy("test")
            
            assert isinstance(results, list)
            # Should use default threshold=0.8, limit=5
            mock_search_service.assert_called_once_with(similarity_threshold=0.8, max_results=5)


class TestFuzzySearchImplementation:
    """Test fuzzy search implementation with various scenarios."""
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_exact_match(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with exact name match."""
        # Mock repository methods
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            from src.services.search_service import SearchResult
            
            # Mock search service to return high-scoring result
            mock_service = Mock()
            mock_service.search_participants.return_value = [
                SearchResult(participant=sample_participants[0], similarity_score=0.95)
            ]
            mock_search_service.return_value = mock_service
            
            results = await repository.search_by_name_fuzzy("Александр Иванов", threshold=0.8, limit=5)
            
            # Should return list of tuples
            assert isinstance(results, list)
            assert len(results) == 1
            
            participant, score = results[0]
            assert isinstance(participant, Participant)
            assert isinstance(score, float)
            assert participant.full_name_ru == "Александр Иванов"
            assert score == 0.95
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_multiple_results(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search returning multiple results sorted by score."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            from src.services.search_service import SearchResult
            
            # Mock search service to return multiple results
            mock_service = Mock()
            mock_service.search_participants.return_value = [
                SearchResult(participant=sample_participants[0], similarity_score=0.95),
                SearchResult(participant=sample_participants[1], similarity_score=0.85),
            ]
            mock_search_service.return_value = mock_service
            
            results = await repository.search_by_name_fuzzy("Алекс", threshold=0.8, limit=5)
            
            assert len(results) == 2
            
            # Should be sorted by score descending
            participant1, score1 = results[0]
            participant2, score2 = results[1]
            assert score1 >= score2
            assert score1 == 0.95
            assert score2 == 0.85
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_no_results(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with no matching results."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            # Mock search service to return no results
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            results = await repository.search_by_name_fuzzy("NonExistentName", threshold=0.8, limit=5)
            
            assert isinstance(results, list)
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_custom_threshold(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with custom similarity threshold."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            # Test with custom threshold
            await repository.search_by_name_fuzzy("test", threshold=0.9, limit=3)
            
            # Should use custom parameters
            mock_search_service.assert_called_once_with(similarity_threshold=0.9, max_results=3)
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_repository_error(self, repository, mock_airtable_client):
        """Test fuzzy search handles repository errors gracefully."""
        # Mock list_all to raise an exception
        repository.list_all = AsyncMock(side_effect=Exception("Database error"))
        
        with pytest.raises(RepositoryError):
            await repository.search_by_name_fuzzy("test")
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_empty_query(self, repository, mock_airtable_client):
        """Test fuzzy search with empty query string."""
        repository.list_all = AsyncMock(return_value=[])
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            results = await repository.search_by_name_fuzzy("", threshold=0.8, limit=5)
            
            assert isinstance(results, list)
            assert len(results) == 0
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_integration_with_search_service(self, repository, mock_airtable_client, sample_participants):
        """Test that fuzzy search correctly integrates with SearchService."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            await repository.search_by_name_fuzzy("Александр", threshold=0.75, limit=10)
            
            # Should instantiate SearchService with correct parameters
            mock_search_service.assert_called_once_with(similarity_threshold=0.75, max_results=10)
            
            # Should call search_participants with query and all participants
            mock_service.search_participants.assert_called_once_with("Александр", sample_participants)


class TestFuzzySearchEdgeCases:
    """Test edge cases for fuzzy search functionality."""
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_threshold_bounds(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with threshold boundary values."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            # Test with threshold 0.0 (should accept all)
            await repository.search_by_name_fuzzy("test", threshold=0.0)
            mock_search_service.assert_called_with(similarity_threshold=0.0, max_results=5)
            
            # Reset mock for second call
            mock_search_service.reset_mock()
            
            # Test with threshold 1.0 (only perfect matches)
            await repository.search_by_name_fuzzy("test", threshold=1.0)
            mock_search_service.assert_called_with(similarity_threshold=1.0, max_results=5)
    
    @pytest.mark.asyncio
    async def test_search_by_name_fuzzy_limit_bounds(self, repository, mock_airtable_client, sample_participants):
        """Test fuzzy search with limit boundary values."""
        repository.list_all = AsyncMock(return_value=sample_participants)
        
        with patch('src.data.airtable.airtable_participant_repo.SearchService') as mock_search_service:
            mock_service = Mock()
            mock_service.search_participants.return_value = []
            mock_search_service.return_value = mock_service
            
            # Test with limit 1
            await repository.search_by_name_fuzzy("test", limit=1)
            mock_search_service.assert_called_with(similarity_threshold=0.8, max_results=1)
            
            # Reset mock for second call
            mock_search_service.reset_mock()
            
            # Test with large limit
            await repository.search_by_name_fuzzy("test", limit=100)
            mock_search_service.assert_called_with(similarity_threshold=0.8, max_results=100)