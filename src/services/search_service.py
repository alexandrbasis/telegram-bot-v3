"""
Search service for fuzzy participant name matching.

Provides fuzzy search functionality using rapidfuzz library with Russian/English 
name normalization and configurable similarity thresholds.
"""

from typing import List, Tuple
from dataclasses import dataclass
import logging

from rapidfuzz import fuzz, process
from src.models.participant import Participant

logger = logging.getLogger(__name__)


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
    normalized = normalized.replace('ё', 'е')
    normalized = normalized.replace('й', 'и')
    
    return normalized


@dataclass
class SearchResult:
    """
    Result of a fuzzy search operation.
    
    Contains the matched participant and similarity score for ranking.
    """
    participant: Participant
    similarity_score: float
    
    def __lt__(self, other):
        """Enable sorting by similarity score (descending)."""
        return self.similarity_score > other.similarity_score


class SearchService:
    """
    Service for fuzzy participant name searching.
    
    Uses rapidfuzz token_sort_ratio algorithm for word-order independent matching
    with Russian character normalization.
    """
    
    def __init__(self, similarity_threshold: float = 0.8, max_results: int = 5):
        """
        Initialize search service with configuration.
        
        Args:
            similarity_threshold: Minimum similarity score (0.0-1.0)
            max_results: Maximum number of results to return
        """
        self.similarity_threshold = similarity_threshold
        self.max_results = max_results
        logger.info(f"Initialized SearchService (threshold={similarity_threshold}, max_results={max_results})")
    
    def search_participants(self, query: str, participants: List[Participant]) -> List[SearchResult]:
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
        
        logger.debug(f"Searching for '{query}' (normalized: '{query_normalized}') among {len(participants)} participants")
        
        for participant in participants:
            # Get the best similarity score from Russian and English names
            max_score = 0.0
            
            # Check Russian name
            if participant.full_name_ru:
                ru_normalized = normalize_russian(participant.full_name_ru)
                ru_score = fuzz.token_sort_ratio(query_normalized, ru_normalized) / 100.0
                max_score = max(max_score, ru_score)
            
            # Check English name
            if participant.full_name_en:
                en_normalized = normalize_russian(participant.full_name_en)
                en_score = fuzz.token_sort_ratio(query_normalized, en_normalized) / 100.0
                max_score = max(max_score, en_score)
            
            # Add to results if meets threshold
            if max_score >= self.similarity_threshold:
                results.append(SearchResult(
                    participant=participant,
                    similarity_score=max_score
                ))
        
        # Sort by similarity score descending and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        limited_results = results[:self.max_results]
        
        logger.debug(f"Found {len(limited_results)} matches above threshold {self.similarity_threshold}")
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
        
        return fuzz.token_sort_ratio(query_norm, target_norm) / 100.0