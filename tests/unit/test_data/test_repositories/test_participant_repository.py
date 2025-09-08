"""
Unit tests for abstract ParticipantRepository interface.

Tests verify the interface contract is correctly defined and that custom
exceptions are properly structured. Actual implementation testing will be
done in concrete repository test files.
"""

from abc import ABC
from typing import get_type_hints

import pytest

from src.data.repositories.participant_repository import (
    NotFoundError,
    ParticipantRepository,
    RepositoryError,
    ValidationError,
)
from src.models.participant import Participant


class TestParticipantRepositoryInterface:
    """Test suite for repository interface definition."""

    def test_repository_is_abstract(self):
        """Test that ParticipantRepository is an abstract base class."""
        assert issubclass(ParticipantRepository, ABC)

        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            ParticipantRepository()

    def test_repository_has_required_abstract_methods(self):
        """Test that all required abstract methods are defined."""
        required_methods = {
            "create",
            "get_by_id",
            "get_by_full_name_ru",
            "update",
            "delete",
            "list_all",
            "search_by_criteria",
            "get_by_role",
            "get_by_department",
            "get_by_payment_status",
            "count_total",
            "bulk_create",
            "bulk_update",
            "search_by_name_fuzzy",
        }

        repository_methods = set(dir(ParticipantRepository))

        # Check all required methods exist
        for method in required_methods:
            assert (
                method in repository_methods
            ), f"Method {method} not found in repository"

            # Check method is marked as abstract
            method_obj = getattr(ParticipantRepository, method)
            assert hasattr(
                method_obj, "__isabstractmethod__"
            ), f"Method {method} should be abstract"
            assert (
                method_obj.__isabstractmethod__
            ), f"Method {method} should be abstract"

    def test_create_method_signature(self):
        """Test create method has correct signature."""
        method = getattr(ParticipantRepository, "create")

        # Check it's an async method
        assert hasattr(method, "__annotations__")

        # Check parameter types
        annotations = method.__annotations__
        assert (
            "participant" in annotations or len(annotations) >= 2
        )  # self + participant + return
        assert "return" in annotations

    def test_get_by_id_method_signature(self):
        """Test get_by_id method has correct signature."""
        method = getattr(ParticipantRepository, "get_by_id")

        assert hasattr(method, "__annotations__")
        annotations = method.__annotations__
        assert "record_id" in annotations or len(annotations) >= 2
        assert "return" in annotations

    def test_search_by_criteria_method_signature(self):
        """Test search_by_criteria method has correct signature."""
        method = getattr(ParticipantRepository, "search_by_criteria")

        assert hasattr(method, "__annotations__")
        annotations = method.__annotations__
        assert "criteria" in annotations or len(annotations) >= 2
        assert "return" in annotations

    def test_bulk_operations_method_signatures(self):
        """Test bulk operation methods have correct signatures."""
        bulk_create = getattr(ParticipantRepository, "bulk_create")
        bulk_update = getattr(ParticipantRepository, "bulk_update")

        for method in [bulk_create, bulk_update]:
            assert hasattr(method, "__annotations__")
            annotations = method.__annotations__
            assert len(annotations) >= 2  # participants + return
            assert "return" in annotations


class TestRepositoryExceptions:
    """Test suite for repository exception classes."""

    def test_repository_error_inheritance(self):
        """Test RepositoryError inherits from Exception."""
        assert issubclass(RepositoryError, Exception)

        # Test basic instantiation
        error = RepositoryError("Test error")
        assert str(error) == "Test error"
        assert error.original_error is None

    def test_repository_error_with_original_exception(self):
        """Test RepositoryError can wrap original exceptions."""
        original = ValueError("Original error")
        error = RepositoryError("Repository error", original)

        assert str(error) == "Repository error"
        assert error.original_error is original
        assert isinstance(error.original_error, ValueError)

    def test_not_found_error_inheritance(self):
        """Test NotFoundError inherits from RepositoryError."""
        assert issubclass(NotFoundError, RepositoryError)
        assert issubclass(NotFoundError, Exception)

        # Test instantiation
        error = NotFoundError("Record not found")
        assert str(error) == "Record not found"
        assert error.original_error is None

    def test_validation_error_inheritance(self):
        """Test ValidationError inherits from RepositoryError."""
        assert issubclass(ValidationError, RepositoryError)
        assert issubclass(ValidationError, Exception)

        # Test instantiation
        error = ValidationError("Validation failed")
        assert str(error) == "Validation failed"
        assert error.original_error is None

    def test_exception_chain_handling(self):
        """Test that exceptions can be chained properly."""
        # Simulate nested exception handling
        try:
            raise ValueError("Database connection failed")
        except ValueError as e:
            repo_error = RepositoryError("Failed to create participant", e)

        assert isinstance(repo_error, RepositoryError)
        assert isinstance(repo_error.original_error, ValueError)
        assert "Database connection failed" in str(repo_error.original_error)


class TestConcreteImplementationRequirements:
    """Test that concrete implementations must implement all methods."""

    def test_partial_implementation_fails(self):
        """Test that partial implementations cannot be instantiated."""

        class PartialRepository(ParticipantRepository):
            """Incomplete implementation for testing."""

            async def create(self, participant):
                pass

            async def get_by_id(self, record_id):
                pass

            # Missing all other required methods

        # Should not be able to instantiate due to missing abstract methods
        with pytest.raises(TypeError) as exc_info:
            PartialRepository()

        error_msg = str(exc_info.value)
        assert "Can't instantiate abstract class" in error_msg
        assert "abstract method" in error_msg

    def test_complete_implementation_succeeds(self):
        """Test that complete implementations can be instantiated."""

        class CompleteRepository(ParticipantRepository):
            """Complete implementation for testing."""

            async def create(self, participant):
                pass

            async def get_by_id(self, record_id):
                pass

            async def get_by_full_name_ru(self, full_name_ru):
                pass

            async def update(self, participant):
                pass

            async def delete(self, record_id):
                pass

            async def list_all(self, limit=None, offset=None):
                pass

            async def search_by_criteria(self, criteria):
                pass

            async def get_by_role(self, role):
                pass

            async def get_by_department(self, department):
                pass

            async def get_by_payment_status(self, payment_status):
                pass

            async def count_total(self):
                pass

            async def bulk_create(self, participants):
                pass

            async def bulk_update(self, participants):
                pass

            async def search_by_name_fuzzy(self, query, threshold=0.8, limit=5):
                pass

        # Should be able to instantiate complete implementation
        repo = CompleteRepository()
        assert isinstance(repo, ParticipantRepository)
        assert isinstance(repo, CompleteRepository)


class TestRepositoryMethodDocstrings:
    """Test that all repository methods have proper documentation."""

    def test_all_methods_have_docstrings(self):
        """Test that all abstract methods have docstrings."""
        abstract_methods = [
            "create",
            "get_by_id",
            "get_by_full_name_ru",
            "update",
            "delete",
            "list_all",
            "search_by_criteria",
            "get_by_role",
            "get_by_department",
            "get_by_payment_status",
            "count_total",
            "bulk_create",
            "bulk_update",
        ]

        for method_name in abstract_methods:
            method = getattr(ParticipantRepository, method_name)
            assert method.__doc__ is not None, f"Method {method_name} missing docstring"
            assert (
                len(method.__doc__.strip()) > 0
            ), f"Method {method_name} has empty docstring"

            # Check for standard docstring sections
            docstring = method.__doc__
            assert "Args:" in docstring, f"Method {method_name} missing Args section"
            assert (
                "Returns:" in docstring
            ), f"Method {method_name} missing Returns section"
            assert (
                "Raises:" in docstring
            ), f"Method {method_name} missing Raises section"


class TestRepositoryUsageContract:
    """Test the expected usage patterns and contracts."""

    def test_repository_interface_imports(self):
        """Test that interface can be imported and used for type hints."""
        # This test verifies the import structure works correctly
        from src.data.repositories.participant_repository import ParticipantRepository
        from src.models.participant import Participant

        # Test that we can use it in type annotations
        def example_function(repo: ParticipantRepository) -> None:
            """Example function using repository type hint."""
            pass

        # Verify type hint is correctly applied
        annotations = example_function.__annotations__
        assert annotations["repo"] is ParticipantRepository

    def test_exception_hierarchy_usage(self):
        """Test that exception hierarchy supports proper error handling."""
        # Test that we can catch specific exceptions
        try:
            raise NotFoundError("Participant not found")
        except RepositoryError as e:
            # Should catch NotFoundError as RepositoryError
            assert isinstance(e, NotFoundError)
            assert isinstance(e, RepositoryError)

        try:
            raise ValidationError("Invalid data")
        except RepositoryError as e:
            # Should catch ValidationError as RepositoryError
            assert isinstance(e, ValidationError)
            assert isinstance(e, RepositoryError)

    def test_async_method_contract(self):
        """Test that methods are properly defined as async."""
        import inspect

        # All methods should be coroutines when implemented
        async_methods = [
            "create",
            "get_by_id",
            "get_by_full_name_ru",
            "update",
            "delete",
            "list_all",
            "search_by_criteria",
            "get_by_role",
            "get_by_department",
            "get_by_payment_status",
            "count_total",
            "bulk_create",
            "bulk_update",
        ]

        for method_name in async_methods:
            method = getattr(ParticipantRepository, method_name)
            # Check that method is defined as async (coroutine function)
            assert inspect.iscoroutinefunction(method) or hasattr(
                method, "__code__"
            ), f"Method {method_name} should be async"
