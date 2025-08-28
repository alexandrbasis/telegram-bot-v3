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
        if '\u0400' <= char <= '\u04FF':  # Cyrillic block
            cyrillic_count += 1
        # Check if character is in Basic Latin range (letters only)
        elif 'A' <= char <= 'Z' or 'a' <= char <= 'z':
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
        role_value = participant.role.value if hasattr(participant.role, 'value') else str(participant.role)
        info_parts.append(role_value)
    
    if participant.department:
        # Handle both enum objects and string values (pydantic with use_enum_values=True) 
        dept_value = participant.department.value if hasattr(participant.department, 'value') else str(participant.department)
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
    
    return "".join(result_parts)


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
    
    def search_participants_enhanced(self, query: str, participants: List[Participant]) -> List[SearchResult]:
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
        
        logger.debug(f"Enhanced search for '{query}' (lang: {detected_lang}, normalized: '{query_normalized}') among {len(participants)} participants")
        
        for participant in participants:
            max_score = 0.0
            
            # Get fields to search based on detected language
            if detected_lang == "ru":
                primary_field = participant.full_name_ru
                secondary_field = participant.full_name_en
            else:
                primary_field = participant.full_name_en
                secondary_field = participant.full_name_ru
            
            # Search in primary field (full name and individual parts)
            if primary_field:
                # Full name search
                primary_normalized = normalize_russian(primary_field)
                full_score = fuzz.token_sort_ratio(query_normalized, primary_normalized) / 100.0
                max_score = max(max_score, full_score)
                
                # Individual name parts search
                name_parts = parse_name_parts(primary_field)
                for part in name_parts:
                    part_normalized = normalize_russian(part)
                    part_score = fuzz.token_sort_ratio(query_normalized, part_normalized) / 100.0
                    max_score = max(max_score, part_score)
            
            # Search in secondary field (lower priority)
            if secondary_field and max_score < 0.9:  # Only if no excellent match in primary
                # Full name search
                secondary_normalized = normalize_russian(secondary_field)
                secondary_full_score = fuzz.token_sort_ratio(query_normalized, secondary_normalized) / 100.0
                max_score = max(max_score, secondary_full_score * 0.9)  # Slight penalty for secondary field
                
                # Individual name parts search
                secondary_parts = parse_name_parts(secondary_field)
                for part in secondary_parts:
                    part_normalized = normalize_russian(part)
                    part_score = fuzz.token_sort_ratio(query_normalized, part_normalized) / 100.0
                    max_score = max(max_score, part_score * 0.9)  # Slight penalty for secondary field
            
            # Add to results if meets threshold
            if max_score >= self.similarity_threshold:
                results.append(SearchResult(
                    participant=participant,
                    similarity_score=max_score
                ))
        
        # Sort by similarity score descending and limit results
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        limited_results = results[:self.max_results]
        
        logger.debug(f"Enhanced search found {len(limited_results)} matches above threshold {self.similarity_threshold}")
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