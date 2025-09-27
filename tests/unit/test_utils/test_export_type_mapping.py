"""
Tests for export type to Russian description mapping.

Tests the translation functionality for export types used in
success messages and user interface elements.
"""

import pytest

from src.utils.export_type_mapping import get_russian_export_description


class TestExportTypeMapping:
    """Test export type to Russian description mapping functionality."""

    def test_candidates_export_description(self):
        """Test Russian description for candidates export."""
        result = get_russian_export_description("candidates")
        assert result == "Кандидаты"

    def test_team_export_description(self):
        """Test Russian description for team members export."""
        result = get_russian_export_description("team")
        assert result == "Тим Мемберы"

    def test_departments_export_description(self):
        """Test Russian description for departments export."""
        result = get_russian_export_description("departments")
        assert result == "Департаменты"

    def test_roe_export_description(self):
        """Test Russian description for ROE export."""
        result = get_russian_export_description("roe")
        assert result == "РОЭ"

    def test_bible_readers_export_description(self):
        """Test Russian description for Bible readers export."""
        result = get_russian_export_description("bible_readers")
        assert result == "Чтецы"

    def test_unknown_export_type_fallback(self):
        """Test fallback behavior for unknown export types."""
        result = get_russian_export_description("unknown_type")
        assert result == "unknown_type"

    def test_none_export_type_fallback(self):
        """Test fallback behavior for None export type."""
        result = get_russian_export_description(None)
        assert result == "Экспорт"

    def test_empty_string_export_type_fallback(self):
        """Test fallback behavior for empty string export type."""
        result = get_russian_export_description("")
        assert result == "Экспорт"

    def test_case_insensitive_mapping(self):
        """Test that export type mapping is case insensitive."""
        assert get_russian_export_description("CANDIDATES") == "Кандидаты"
        assert get_russian_export_description("Team") == "Тим Мемберы"
        assert get_russian_export_description("ROE") == "РОЭ"

    def test_all_defined_export_types_have_translations(self):
        """Test that all expected export types have Russian translations."""
        expected_types = ["candidates", "team", "departments", "roe", "bible_readers"]

        for export_type in expected_types:
            result = get_russian_export_description(export_type)
            # Should not return the fallback value
            assert result != export_type
            assert result != "Экспорт"
            assert len(result) > 0
