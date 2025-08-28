"""
Unit tests for SearchService with fuzzy matching capabilities.

Tests the search service that provides fuzzy name matching using rapidfuzz
library with Russian/English name normalization and similarity scoring.
"""

import pytest
from unittest.mock import Mock, patch
from typing import List, Tuple

from src.services.search_service import (
    SearchService,
    normalize_russian,
    SearchResult
)
from src.models.participant import Participant


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
            Participant(full_name_ru="Александр Иванов", full_name_en="Alexander Ivanov"),
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
        service = SearchService(similarity_threshold=0.7)  # Lower threshold for partial matches
        results = service.search_participants("Александр", sample_participants)
        
        assert len(results) >= 1
        assert results[0].similarity_score >= 0.7
        assert "Александр" in results[0].participant.full_name_ru
        
    def test_search_below_threshold_filtered(self, sample_participants):
        """Test that results below similarity threshold are filtered out."""
        service = SearchService(similarity_threshold=0.9)
        results = service.search_participants("Completely Different Name", sample_participants)
        
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
        
        results_lower = service.search_participants("александр иванов", sample_participants)
        results_upper = service.search_participants("АЛЕКСАНДР ИВАНОВ", sample_participants)
        results_mixed = service.search_participants("Александр ИВАНОВ", sample_participants)
        
        # All should find the same participant
        assert len(results_lower) >= 1
        assert len(results_upper) >= 1
        assert len(results_mixed) >= 1
        
        # Should have similar scores
        assert abs(results_lower[0].similarity_score - results_upper[0].similarity_score) < 0.1


class TestSearchServiceIntegration:
    """Integration tests for SearchService."""
    
    def test_search_with_rapidfuzz_integration(self):
        """Test that rapidfuzz library is properly integrated."""
        service = SearchService()
        participants = [
            Participant(full_name_ru="Тест Участник")
        ]
        
        # This should work without import errors
        results = service.search_participants("Тест", participants)
        assert isinstance(results, list)