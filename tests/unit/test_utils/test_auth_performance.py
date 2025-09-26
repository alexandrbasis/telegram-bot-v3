"""
Performance benchmarking tests for authorization system.

Tests authorization performance requirements:
- Cache hits: <100ms at 95th percentile
- Cache misses with sync: <300ms at 99th percentile
- Comprehensive performance metrics collection
"""

import statistics
import time
from unittest.mock import MagicMock, patch

import pytest

from src.config.settings import TelegramSettings
from src.services.security_audit_service import get_security_audit_service
from src.utils.access_control import require_role
from src.utils.auth_utils import (
    _ROLE_CACHE,
    _ROLE_CACHE_TTL_SECONDS,
    get_user_role,
    invalidate_role_cache,
    is_admin_user,
    is_coordinator_user,
    is_viewer_user,
)


class TestAuthorizationPerformanceBenchmarks:
    """Test authorization performance against required thresholds."""

    def setup_method(self):
        """Set up test fixtures before each test."""
        # Clear cache before each test
        _ROLE_CACHE.clear()

        # Create mock test settings with just telegram config
        self.test_settings = MagicMock()
        self.test_settings.telegram = TelegramSettings(
            bot_token="test_token",
            admin_user_ids=[123456, 789012],
            coordinator_user_ids=[111111, 222222],
            viewer_user_ids=[333333, 444444],
        )

    def teardown_method(self):
        """Clean up after each test."""
        _ROLE_CACHE.clear()

    def test_cache_hit_performance_under_100ms_95th_percentile(self):
        """Test cache hit performance meets <100ms at 95th percentile requirement."""
        user_id = 123456  # Admin user

        # Warm up cache with initial call
        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()
            get_user_role(user_id, self.test_settings)

        # Performance test - measure cache hits
        execution_times = []
        num_iterations = 100

        for _ in range(num_iterations):
            start_time = time.perf_counter()

            with patch(
                "src.services.security_audit_service.get_security_audit_service"
            ) as mock_audit:
                mock_audit.return_value = MagicMock()
                result = get_user_role(user_id, self.test_settings)

            end_time = time.perf_counter()
            execution_times.append(
                (end_time - start_time) * 1000
            )  # Convert to milliseconds

            # Verify we got the expected result
            assert result == "admin"

        # Calculate performance statistics
        percentile_95 = statistics.quantiles(execution_times, n=20)[
            18
        ]  # 95th percentile
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)

        # Performance assertion - 95th percentile must be under 100ms
        assert percentile_95 < 100, (
            f"Cache hit performance failed: 95th percentile {percentile_95:.2f}ms "
            f"exceeds 100ms requirement (avg: {avg_time:.2f}ms, max: {max_time:.2f}ms)"
        )

        # Additional performance insights
        print(f"\nCache hit performance metrics:")
        print(f"95th percentile: {percentile_95:.2f}ms")
        print(f"Average: {avg_time:.2f}ms")
        print(f"Max: {max_time:.2f}ms")

    def test_cache_miss_performance_under_300ms_99th_percentile(self):
        """Test cache miss performance meets <300ms at 99th percentile requirement."""
        user_ids = [123456, 789012, 111111, 222222, 333333]  # Various roles

        execution_times = []
        num_iterations = 100

        for i in range(num_iterations):
            # Clear cache to force cache miss
            _ROLE_CACHE.clear()

            user_id = user_ids[i % len(user_ids)]
            start_time = time.perf_counter()

            with patch(
                "src.services.security_audit_service.get_security_audit_service"
            ) as mock_audit:
                mock_audit.return_value = MagicMock()
                result = get_user_role(user_id, self.test_settings)

            end_time = time.perf_counter()
            execution_times.append(
                (end_time - start_time) * 1000
            )  # Convert to milliseconds

            # Verify we got a valid result
            assert result in ["admin", "coordinator", "viewer", None]

        # Calculate performance statistics
        percentile_99 = statistics.quantiles(execution_times, n=100)[
            98
        ]  # 99th percentile
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)

        # Performance assertion - 99th percentile must be under 300ms
        assert percentile_99 < 300, (
            f"Cache miss performance failed: 99th percentile {percentile_99:.2f}ms "
            f"exceeds 300ms requirement (avg: {avg_time:.2f}ms, max: {max_time:.2f}ms)"
        )

        # Additional performance insights
        print(f"\nCache miss performance metrics:")
        print(f"99th percentile: {percentile_99:.2f}ms")
        print(f"Average: {avg_time:.2f}ms")
        print(f"Max: {max_time:.2f}ms")

    def test_admin_check_performance_benchmarks(self):
        """Test is_admin_user function performance."""
        user_id = 123456  # Admin user
        execution_times = []
        num_iterations = 50

        for _ in range(num_iterations):
            start_time = time.perf_counter()

            with patch(
                "src.services.security_audit_service.get_security_audit_service"
            ) as mock_audit:
                mock_audit.return_value = MagicMock()
                result = is_admin_user(user_id, self.test_settings)

            end_time = time.perf_counter()
            execution_times.append((end_time - start_time) * 1000)

            assert result is True

        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)

        # Admin check should be very fast since it's direct lookup
        assert avg_time < 50, f"Admin check too slow: avg {avg_time:.2f}ms"
        assert max_time < 100, f"Admin check max time too slow: {max_time:.2f}ms"

    def test_role_hierarchy_performance_benchmarks(self):
        """Test performance of role hierarchy functions."""
        test_cases = [
            (is_coordinator_user, 111111, "coordinator"),
            (is_viewer_user, 333333, "viewer"),
            (is_viewer_user, 111111, "coordinator_with_viewer_access"),  # Higher role
        ]

        for func, user_id, description in test_cases:
            execution_times = []
            num_iterations = 30

            for _ in range(num_iterations):
                start_time = time.perf_counter()

                with patch(
                    "src.services.security_audit_service.get_security_audit_service"
                ) as mock_audit:
                    mock_audit.return_value = MagicMock()
                    result = func(user_id, self.test_settings)

                end_time = time.perf_counter()
                execution_times.append((end_time - start_time) * 1000)

                assert result is True

            avg_time = statistics.mean(execution_times)
            assert avg_time < 50, f"{description} check too slow: avg {avg_time:.2f}ms"

    def test_cache_invalidation_performance(self):
        """Test cache invalidation performance."""
        # Populate cache with multiple users
        user_ids = [123456, 789012, 111111, 222222, 333333]

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            for user_id in user_ids:
                get_user_role(user_id, self.test_settings)

        assert len(_ROLE_CACHE) == len(user_ids)

        # Test individual user cache invalidation performance
        start_time = time.perf_counter()
        invalidate_role_cache(123456)
        individual_time = (time.perf_counter() - start_time) * 1000

        assert (
            individual_time < 10
        ), f"Individual cache invalidation too slow: {individual_time:.2f}ms"
        assert len(_ROLE_CACHE) == len(user_ids) - 1

        # Test full cache invalidation performance
        start_time = time.perf_counter()
        invalidate_role_cache()  # Clear all
        full_clear_time = (time.perf_counter() - start_time) * 1000

        assert (
            full_clear_time < 10
        ), f"Full cache invalidation too slow: {full_clear_time:.2f}ms"
        assert len(_ROLE_CACHE) == 0

    def test_concurrent_access_simulation(self):
        """Test performance under simulated concurrent access."""
        user_ids = [123456, 789012, 111111, 222222, 333333]
        num_operations = 200

        # Simulate concurrent access pattern
        execution_times = []

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            for i in range(num_operations):
                user_id = user_ids[i % len(user_ids)]

                start_time = time.perf_counter()
                result = get_user_role(user_id, self.test_settings)
                end_time = time.perf_counter()

                execution_times.append((end_time - start_time) * 1000)
                assert result is not None

        # Performance should remain consistent under load
        avg_time = statistics.mean(execution_times)
        percentile_95 = statistics.quantiles(execution_times, n=20)[18]

        assert avg_time < 25, f"Concurrent access avg too slow: {avg_time:.2f}ms"
        assert (
            percentile_95 < 75
        ), f"Concurrent access 95th percentile too slow: {percentile_95:.2f}ms"

    def test_cache_ttl_performance_impact(self):
        """Test performance impact of cache TTL expiration."""
        user_id = 123456

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            # Initial cache population
            start_time = time.perf_counter()
            result1 = get_user_role(user_id, self.test_settings)
            initial_time = (time.perf_counter() - start_time) * 1000

            # Cache hit
            start_time = time.perf_counter()
            result2 = get_user_role(user_id, self.test_settings)
            cache_hit_time = (time.perf_counter() - start_time) * 1000

            assert result1 == result2

            # Cache hit should be at least as fast as initial lookup and usually faster
            # With the optimized implementation, both execution paths remain fast
            assert (
                cache_hit_time <= initial_time + 0.1
            ), f"Cache hit slower than expected: {cache_hit_time:.2f}ms vs {initial_time:.2f}ms"

    @patch("src.utils.auth_utils._ROLE_CACHE_TTL_SECONDS", 1)  # Short TTL for testing
    def test_cache_expiration_performance(self):
        """Test performance when cache expires."""
        user_id = 123456

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            # Initial cache population
            result1 = get_user_role(user_id, self.test_settings)

            # Wait for cache expiration
            time.sleep(1.1)

            # This should trigger cache refresh
            start_time = time.perf_counter()
            result2 = get_user_role(user_id, self.test_settings)
            refresh_time = (time.perf_counter() - start_time) * 1000

            assert result1 == result2

            # Cache refresh should still be reasonably fast
            assert refresh_time < 100, f"Cache refresh too slow: {refresh_time:.2f}ms"


class TestPerformanceMetricsCollection:
    """Test that performance metrics are properly collected and structured."""

    def setup_method(self):
        """Set up test fixtures."""
        _ROLE_CACHE.clear()
        self.test_settings = MagicMock()
        self.test_settings.telegram = TelegramSettings(
            bot_token="test_token",
            admin_user_ids=[123456],
            coordinator_user_ids=[],
            viewer_user_ids=[],
        )

    def teardown_method(self):
        """Clean up after each test."""
        _ROLE_CACHE.clear()

    def test_performance_metrics_are_logged_with_thresholds(self):
        """Test that performance metrics are logged with correct threshold classifications."""
        user_id = 123456

        with patch("src.utils.auth_utils.get_security_audit_service") as mock_audit:
            mock_service = MagicMock()
            mock_audit.return_value = mock_service

            # Call authorization function
            get_user_role(user_id, self.test_settings)

            # Verify performance metrics were logged
            assert mock_service.create_performance_metrics.called
            assert mock_service.log_performance_metrics.called

            # Check the metrics call
            create_call = mock_service.create_performance_metrics.call_args
            assert create_call[1]["operation"] == "role_resolution"
            assert "duration_ms" in create_call[1]
            assert "cache_hit" in create_call[1]
            assert "user_role" in create_call[1]
            assert "additional_context" in create_call[1]

    def test_audit_events_capture_cache_state_correctly(self):
        """Test that audit events correctly capture cache state."""
        user_id = 123456

        with patch("src.utils.auth_utils.get_security_audit_service") as mock_audit:
            mock_service = MagicMock()
            mock_audit.return_value = mock_service

            # First call - cache miss
            get_user_role(user_id, self.test_settings)

            # Verify cache miss was logged
            create_calls = mock_service.create_authorization_event.call_args_list
            assert len(create_calls) >= 1

            # Check cache state in the authorization event
            auth_event_call = create_calls[0]
            assert auth_event_call[1]["action"] == "role_resolution"
            assert auth_event_call[1]["cache_state"] in ["miss", "expired"]

            # Reset mock for second call
            mock_service.reset_mock()

            # Second call - should be cache hit
            get_user_role(user_id, self.test_settings)

            # Verify cache hit was logged
            create_calls = mock_service.create_authorization_event.call_args_list
            assert len(create_calls) >= 1

            auth_event_call = create_calls[0]
            assert auth_event_call[1]["cache_state"] == "hit"


class TestAuthorizationScalabilityBenchmarks:
    """Test authorization system scalability under various conditions."""

    def setup_method(self):
        """Set up test fixtures."""
        _ROLE_CACHE.clear()
        self.test_settings = MagicMock()
        self.test_settings.telegram = TelegramSettings(
            bot_token="test_token",
            admin_user_ids=list(range(100000, 100010)),  # 10 admins
            coordinator_user_ids=list(range(200000, 200050)),  # 50 coordinators
            viewer_user_ids=list(range(300000, 300200)),  # 200 viewers
        )

    def teardown_method(self):
        """Clean up after each test."""
        _ROLE_CACHE.clear()

    def test_large_role_lists_performance(self):
        """Test performance with larger role lists."""
        # Test various users from different role lists
        test_users = [
            (100005, "admin"),  # Admin user for large list performance
            (200025, "coordinator"),  # Coordinator user performance case
            (300100, "viewer"),  # Viewer user performance case
            (999999, None),  # Unauthorized user performance case
        ]

        execution_times = []

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            for user_id, expected_role in test_users:
                start_time = time.perf_counter()
                result = get_user_role(user_id, self.test_settings)
                end_time = time.perf_counter()

                execution_times.append((end_time - start_time) * 1000)
                assert result == expected_role

        # Performance should remain good even with larger role lists
        avg_time = statistics.mean(execution_times)
        max_time = max(execution_times)

        assert (
            avg_time < 50
        ), f"Large role list performance degraded: avg {avg_time:.2f}ms"
        assert max_time < 100, f"Large role list max time too high: {max_time:.2f}ms"

    def test_cache_scalability_with_many_users(self):
        """Test cache performance with many cached users."""
        num_users = 100
        user_base = 400000

        with patch(
            "src.services.security_audit_service.get_security_audit_service"
        ) as mock_audit:
            mock_audit.return_value = MagicMock()

            # Populate cache with many users
            for i in range(num_users):
                user_id = user_base + i
                # Add some users to role lists
                if i % 10 == 0:
                    self.test_settings.telegram.admin_user_ids.append(user_id)
                elif i % 5 == 0:
                    self.test_settings.telegram.coordinator_user_ids.append(user_id)
                elif i % 3 == 0:
                    self.test_settings.telegram.viewer_user_ids.append(user_id)

                get_user_role(user_id, self.test_settings)

            # Verify cache is populated
            assert len(_ROLE_CACHE) == num_users

            # Test cache hit performance with large cache
            execution_times = []
            for i in range(20):  # Test 20 random cache hits
                user_id = user_base + (i * 3) % num_users

                start_time = time.perf_counter()
                get_user_role(user_id, self.test_settings)
                end_time = time.perf_counter()

                execution_times.append((end_time - start_time) * 1000)

            avg_time = statistics.mean(execution_times)
            assert (
                avg_time < 50
            ), f"Large cache performance degraded: avg {avg_time:.2f}ms"
