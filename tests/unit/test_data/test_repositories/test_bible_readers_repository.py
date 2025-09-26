"""
Unit tests for BibleReaders repository interface.

Tests ensure the abstract base class defines proper contracts
for data operations following the repository pattern.
"""

from abc import ABC

import pytest

from src.data.repositories.bible_readers_repository import BibleReadersRepository
from src.models.bible_readers import BibleReader


class TestBibleReadersRepositoryInterface:
    """Test suite for BibleReadersRepository abstract interface."""

    def test_is_abstract_base_class(self):
        """Test that BibleReadersRepository is an abstract base class."""
        assert issubclass(BibleReadersRepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            BibleReadersRepository()

    def test_has_required_crud_methods(self):
        """Test that all required CRUD methods are defined."""
        required_methods = [
            "create",
            "get_by_id",
            "get_by_where",
            "update",
            "delete",
            "list_all",
            "get_by_participant_id",
            "list_view_records",
        ]

        for method_name in required_methods:
            assert hasattr(BibleReadersRepository, method_name)
            method = getattr(BibleReadersRepository, method_name)
            assert callable(method)

    def test_abstract_methods_are_properly_marked(self):
        """Test that abstract methods raise TypeError when not implemented."""

        # Create a concrete class that doesn't implement required methods
        class IncompleteRepository(BibleReadersRepository):
            pass

        with pytest.raises(TypeError):
            IncompleteRepository()

    def test_method_signatures_match_expected_patterns(self):
        """Test that method signatures follow expected repository patterns."""
        # This test verifies the interface defines methods properly
        # without testing actual implementation

        methods = BibleReadersRepository.__abstractmethods__
        expected_methods = {
            "create",
            "get_by_id",
            "get_by_where",
            "update",
            "delete",
            "list_all",
            "get_by_participant_id",
            "list_view_records",
        }

        assert methods == expected_methods


class MockBibleReadersRepository(BibleReadersRepository):
    """Mock implementation for testing the interface contract."""

    async def create(self, bible_reader):
        return bible_reader

    async def get_by_id(self, record_id):
        return None

    async def get_by_where(self, where):
        return None

    async def update(self, bible_reader):
        return bible_reader

    async def delete(self, record_id):
        return True

    async def list_all(self):
        return []

    async def get_by_participant_id(self, participant_id):
        return []

    async def list_view_records(self, view):
        return []


class TestBibleReadersRepositoryContract:
    """Test the repository contract with a mock implementation."""

    @pytest.fixture
    def repository(self):
        return MockBibleReadersRepository()

    @pytest.mark.asyncio
    async def test_can_implement_interface(self, repository):
        """Test that the interface can be properly implemented."""
        # Should be able to call all methods without error
        bible_reader = BibleReader(id="rec123", where="Test Session")

        result = await repository.create(bible_reader)
        assert result == bible_reader

        result = await repository.get_by_id("rec123")
        assert result is None  # Mock returns None

        result = await repository.list_all()
        assert result == []
