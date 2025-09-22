"""
Unit tests for ROE repository interface.

Tests ensure the abstract base class defines proper contracts
for data operations following the repository pattern.
"""

import pytest
from abc import ABC

from src.data.repositories.roe_repository import ROERepository
from src.models.roe import ROE


class TestROERepositoryInterface:
    """Test suite for ROERepository abstract interface."""

    def test_is_abstract_base_class(self):
        """Test that ROERepository is an abstract base class."""
        assert issubclass(ROERepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            ROERepository()

    def test_has_required_crud_methods(self):
        """Test that all required CRUD methods are defined."""
        required_methods = [
            "create",
            "get_by_id",
            "get_by_topic",
            "update",
            "delete",
            "list_all",
            "get_by_roista_id",
            "get_by_assistant_id"
        ]

        for method_name in required_methods:
            assert hasattr(ROERepository, method_name)
            method = getattr(ROERepository, method_name)
            assert callable(method)

    def test_abstract_methods_are_properly_marked(self):
        """Test that abstract methods raise TypeError when not implemented."""
        # Create a concrete class that doesn't implement required methods
        class IncompleteRepository(ROERepository):
            pass

        with pytest.raises(TypeError):
            IncompleteRepository()


class MockROERepository(ROERepository):
    """Mock implementation for testing the interface contract."""

    async def create(self, roe):
        return roe

    async def get_by_id(self, record_id):
        return None

    async def get_by_topic(self, topic):
        return None

    async def update(self, roe):
        return roe

    async def delete(self, record_id):
        return True

    async def list_all(self):
        return []

    async def get_by_roista_id(self, roista_id):
        return []

    async def get_by_assistant_id(self, assistant_id):
        return []


class TestROERepositoryContract:
    """Test the repository contract with a mock implementation."""

    @pytest.fixture
    def repository(self):
        return MockROERepository()

    @pytest.mark.asyncio
    async def test_can_implement_interface(self, repository):
        """Test that the interface can be properly implemented."""
        # Should be able to call all methods without error
        roe = ROE(id="rec123", roe_topic="Test Topic")

        result = await repository.create(roe)
        assert result == roe

        result = await repository.get_by_id("rec123")
        assert result is None  # Mock returns None

        result = await repository.list_all()
        assert result == []

        result = await repository.get_by_roista_id("recRoista")
        assert result == []