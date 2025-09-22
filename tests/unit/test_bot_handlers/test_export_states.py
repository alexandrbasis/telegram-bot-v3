"""
Tests for export conversation states and callback data structure.

Validates enum-based states and callback data patterns for export selection workflow.
"""

import pytest

from src.bot.handlers.export_states import ExportCallbackData, ExportStates


class TestExportStates:
    """Test export conversation states enumeration."""

    def test_export_states_enum_values(self):
        """Test that all required export states are defined."""
        # Test that the enum has all required states for conversation flow
        assert hasattr(ExportStates, "SELECTING_EXPORT_TYPE")
        assert hasattr(ExportStates, "SELECTING_DEPARTMENT")
        assert hasattr(ExportStates, "PROCESSING_EXPORT")

        # Test that states have string values for telegram-python-bot compatibility
        assert isinstance(ExportStates.SELECTING_EXPORT_TYPE, str)
        assert isinstance(ExportStates.SELECTING_DEPARTMENT, str)
        assert isinstance(ExportStates.PROCESSING_EXPORT, str)

    def test_export_states_unique_values(self):
        """Test that all state values are unique."""
        states = [
            ExportStates.SELECTING_EXPORT_TYPE,
            ExportStates.SELECTING_DEPARTMENT,
            ExportStates.PROCESSING_EXPORT,
        ]
        assert len(states) == len(set(states)), "All state values must be unique"

    def test_export_states_naming_convention(self):
        """Test that state names follow expected naming convention."""
        assert ExportStates.SELECTING_EXPORT_TYPE == "selecting_export_type"
        assert ExportStates.SELECTING_DEPARTMENT == "selecting_department"
        assert ExportStates.PROCESSING_EXPORT == "processing_export"


class TestExportCallbackData:
    """Test export callback data patterns for inline keyboards."""

    def test_export_type_callback_patterns(self):
        """Test callback data patterns for export type selection."""
        # Test patterns for all 6 export options
        assert ExportCallbackData.EXPORT_ALL == "export:all"
        assert ExportCallbackData.EXPORT_TEAM == "export:team"
        assert ExportCallbackData.EXPORT_CANDIDATES == "export:candidates"
        assert ExportCallbackData.EXPORT_BY_DEPARTMENT == "export:by_department"
        assert ExportCallbackData.EXPORT_BIBLE_READERS == "export:bible_readers"
        assert ExportCallbackData.EXPORT_ROE == "export:roe"

    def test_department_callback_patterns(self):
        """Test callback data patterns for department selection."""
        # Test pattern for department selection (should include department name)
        assert hasattr(ExportCallbackData, "department_callback")

        # Test that department callback generates proper format
        department_callback = ExportCallbackData.department_callback("Kitchen")
        assert department_callback == "export:department:Kitchen"

        # Test with all 13 departments
        departments = [
            "ROE",
            "Chapel",
            "Setup",
            "Palanka",
            "Administration",
            "Kitchen",
            "Decoration",
            "Bell",
            "Refreshment",
            "Worship",
            "Media",
            "Clergy",
            "Rectorate",
        ]

        for dept in departments:
            callback = ExportCallbackData.department_callback(dept)
            assert callback.startswith("export:department:")
            assert callback.endswith(dept)

    def test_navigation_callback_patterns(self):
        """Test callback data patterns for navigation."""
        assert ExportCallbackData.CANCEL == "export:cancel"
        assert ExportCallbackData.BACK_TO_EXPORT_SELECTION == "export:back"

    def test_callback_pattern_uniqueness(self):
        """Test that all callback patterns are unique."""
        callbacks = [
            ExportCallbackData.EXPORT_ALL,
            ExportCallbackData.EXPORT_TEAM,
            ExportCallbackData.EXPORT_CANDIDATES,
            ExportCallbackData.EXPORT_BY_DEPARTMENT,
            ExportCallbackData.EXPORT_BIBLE_READERS,
            ExportCallbackData.EXPORT_ROE,
            ExportCallbackData.CANCEL,
            ExportCallbackData.BACK_TO_EXPORT_SELECTION,
        ]

        assert len(callbacks) == len(
            set(callbacks)
        ), "All callback patterns must be unique"

    def test_callback_pattern_parsing(self):
        """Test that callback patterns can be parsed correctly."""
        # Test export type parsing
        assert ExportCallbackData.parse_export_type("export:all") == "all"
        assert ExportCallbackData.parse_export_type("export:team") == "team"
        assert ExportCallbackData.parse_export_type("export:candidates") == "candidates"

        # Test department parsing
        assert (
            ExportCallbackData.parse_department("export:department:Kitchen")
            == "Kitchen"
        )
        assert ExportCallbackData.parse_department("export:department:ROE") == "ROE"

        # Test invalid patterns return None
        assert ExportCallbackData.parse_export_type("invalid:pattern") is None
        assert ExportCallbackData.parse_department("invalid:pattern") is None
