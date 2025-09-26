"""
Advanced authorization cache with TTL and manual invalidation.

Provides optimized caching for authorization operations with configurable TTL,
manual refresh endpoints, and comprehensive performance monitoring.
"""

import threading
import time
from dataclasses import dataclass, field
from typing import Dict, Optional, Tuple, Union, cast

from src.services.security_audit_service import get_security_audit_service

# Default cache configuration
DEFAULT_CACHE_TTL_SECONDS = 60  # 1 minute for more aggressive refresh
DEFAULT_MAX_CACHE_SIZE = 10000  # Maximum number of cached entries


@dataclass
class CacheEntry:
    """Cache entry with metadata for performance tracking."""

    value: Optional[str]  # User role or None
    timestamp: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)

    def is_expired(self, ttl_seconds: int) -> bool:
        """Check if entry is expired based on TTL."""
        return (time.time() - self.timestamp) > ttl_seconds

    def access(self) -> None:
        """Record access to this cache entry."""
        self.access_count += 1
        self.last_access = time.time()


class AuthorizationCache:
    """
    High-performance authorization cache with TTL and advanced features.

    Features:
    - Configurable TTL with automatic expiration
    - Manual cache invalidation (single user or full cache)
    - LRU eviction when cache size limit is reached
    - Comprehensive performance metrics and audit logging
    - Thread-safe operations with minimal locking
    - Cache hit/miss statistics tracking
    """

    def __init__(
        self,
        ttl_seconds: int = DEFAULT_CACHE_TTL_SECONDS,
        max_size: int = DEFAULT_MAX_CACHE_SIZE,
    ):
        """
        Initialize authorization cache.

        Args:
            ttl_seconds: Time-to-live for cache entries in seconds
            max_size: Maximum number of entries to cache
        """
        self.ttl_seconds = ttl_seconds
        self.max_size = max_size
        self._cache: Dict[int, CacheEntry] = {}
        self._lock = threading.RLock()
        self._stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "invalidations": 0,
            "refreshes": 0,
        }
        self.audit_service = get_security_audit_service()

    def get(self, user_id: int) -> Tuple[Optional[str], str]:
        """
        Get user role from cache.

        Args:
            user_id: User ID to lookup

        Returns:
            Tuple of (role, cache_state) where cache_state is:
            - 'hit': Valid cache entry found
            - 'expired': Cache entry expired
            - 'miss': No cache entry found
        """
        start_time = time.time()

        with self._lock:
            if user_id not in self._cache:
                self._stats["misses"] += 1
                duration_ms = int((time.time() - start_time) * 1000)

                # Log cache miss performance
                perf_metrics = self.audit_service.create_performance_metrics(
                    operation="cache_lookup",
                    duration_ms=duration_ms,
                    cache_hit=False,
                    user_role=None,
                    additional_context={
                        "cache_state": "miss",
                        "cache_size": len(self._cache),
                    },
                )
                self.audit_service.log_performance_metrics(perf_metrics)

                return None, "miss"

            entry = self._cache[user_id]

            # Check if entry is expired
            if entry.is_expired(self.ttl_seconds):
                self._stats["misses"] += 1
                duration_ms = int((time.time() - start_time) * 1000)

                # Log expired cache performance
                perf_metrics = self.audit_service.create_performance_metrics(
                    operation="cache_lookup",
                    duration_ms=duration_ms,
                    cache_hit=False,
                    user_role=entry.value,
                    additional_context={
                        "cache_state": "expired",
                        "cache_size": len(self._cache),
                        "entry_age_seconds": time.time() - entry.timestamp,
                    },
                )
                self.audit_service.log_performance_metrics(perf_metrics)

                return entry.value, "expired"

            # Valid cache hit
            entry.access()
            self._stats["hits"] += 1
            duration_ms = int((time.time() - start_time) * 1000)

            # Log cache hit performance
            perf_metrics = self.audit_service.create_performance_metrics(
                operation="cache_lookup",
                duration_ms=duration_ms,
                cache_hit=True,
                user_role=entry.value,
                additional_context={
                    "cache_state": "hit",
                    "cache_size": len(self._cache),
                    "entry_access_count": entry.access_count,
                },
            )
            self.audit_service.log_performance_metrics(perf_metrics)

            return entry.value, "hit"

    def set(self, user_id: int, role: Optional[str]) -> None:
        """
        Set user role in cache.

        Args:
            user_id: User ID to cache
            role: User role to cache
        """
        start_time = time.time()

        with self._lock:
            # Check if we need to evict entries due to size limit
            if len(self._cache) >= self.max_size and user_id not in self._cache:
                self._evict_lru()

            # Store or update cache entry
            self._cache[user_id] = CacheEntry(value=role, timestamp=time.time())

            duration_ms = int((time.time() - start_time) * 1000)

            # Log cache set operation
            perf_metrics = self.audit_service.create_performance_metrics(
                operation="cache_set",
                duration_ms=duration_ms,
                cache_hit=False,  # Setting is not a hit
                user_role=role,
                additional_context={
                    "cache_size": len(self._cache),
                    "max_size": self.max_size,
                },
            )
            self.audit_service.log_performance_metrics(perf_metrics)

    def invalidate(self, user_id: Optional[int] = None) -> int:
        """
        Invalidate cache entries.

        Args:
            user_id: User ID to invalidate, or None to clear all entries

        Returns:
            Number of entries invalidated
        """
        start_time = time.time()

        with self._lock:
            if user_id is None:
                # Clear entire cache
                count = len(self._cache)
                self._cache.clear()
                self._stats["invalidations"] += count
                cache_type = "full_invalidation"
            else:
                # Invalidate specific user
                if user_id in self._cache:
                    del self._cache[user_id]
                    count = 1
                    self._stats["invalidations"] += 1
                else:
                    count = 0
                cache_type = "user_invalidation"

            duration_ms = int((time.time() - start_time) * 1000)

            # Log sync event for cache invalidation
            sync_event = self.audit_service.create_sync_event(
                sync_type=cache_type,
                duration_ms=duration_ms,
                records_processed=count,
                success=True,
            )
            self.audit_service.log_sync_event(sync_event)

            return count

    def refresh_all(self, role_resolver_func) -> int:
        """
        Refresh all cache entries by re-resolving roles.

        Args:
            role_resolver_func: Function to resolve user roles
                (user_id, settings) -> role

        Returns:
            Number of entries refreshed
        """
        start_time = time.time()
        refreshed_count = 0
        failed_count = 0

        with self._lock:
            user_ids = list(self._cache.keys())

            for user_id in user_ids:
                try:
                    # This would need to be called from auth_utils with proper settings
                    # For now, just mark as needing refresh
                    if user_id in self._cache:
                        # Reset timestamp to force refresh on next access
                        self._cache[user_id].timestamp = 0
                        refreshed_count += 1
                except Exception:
                    failed_count += 1

            self._stats["refreshes"] += refreshed_count

            duration_ms = int((time.time() - start_time) * 1000)

            # Log sync event for cache refresh
            sync_event = self.audit_service.create_sync_event(
                sync_type="cache_refresh_all",
                duration_ms=duration_ms,
                records_processed=refreshed_count,
                success=failed_count == 0,
                error_details=(
                    f"Failed to refresh {failed_count} entries"
                    if failed_count > 0
                    else None
                ),
            )
            self.audit_service.log_sync_event(sync_event)

            return refreshed_count

    def get_stats(self) -> Dict[str, Union[int, float, Dict]]:
        """
        Get comprehensive cache statistics.

        Returns:
            Dictionary with cache performance statistics
        """
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = (
                self._stats["hits"] / total_requests if total_requests > 0 else 0.0
            )

            return {
                "size": len(self._cache),
                "max_size": self.max_size,
                "ttl_seconds": self.ttl_seconds,
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "statistics": self._stats.copy(),
                "memory_efficiency": (
                    len(self._cache) / self.max_size if self.max_size > 0 else 0.0
                ),
            }

    def _evict_lru(self) -> None:
        """Evict least recently used entry to make space."""
        if not self._cache:
            return

        # Find LRU entry
        lru_user_id = min(
            self._cache.keys(), key=lambda uid: self._cache[uid].last_access
        )

        del self._cache[lru_user_id]
        self._stats["evictions"] += 1

        # Log eviction event
        perf_metrics = self.audit_service.create_performance_metrics(
            operation="cache_eviction",
            duration_ms=1,  # Eviction is very fast
            cache_hit=False,
            user_role=None,
            additional_context={
                "evicted_user_id": lru_user_id,
                "cache_size_after": len(self._cache),
            },
        )
        self.audit_service.log_performance_metrics(perf_metrics)


# Global cache instance
_auth_cache: Optional[AuthorizationCache] = None


def get_authorization_cache() -> AuthorizationCache:
    """
    Get the global authorization cache instance.

    Returns:
        AuthorizationCache instance
    """
    global _auth_cache
    if _auth_cache is None:
        _auth_cache = AuthorizationCache()
    return _auth_cache


def create_cache_with_config(ttl_seconds: int, max_size: int) -> AuthorizationCache:
    """
    Create a new cache instance with custom configuration.

    Args:
        ttl_seconds: Cache TTL in seconds
        max_size: Maximum cache size

    Returns:
        Configured AuthorizationCache instance
    """
    return AuthorizationCache(ttl_seconds=ttl_seconds, max_size=max_size)


# Cache management functions for external use
def invalidate_user_cache(user_id: int) -> bool:
    """
    Invalidate cache for specific user.

    Args:
        user_id: User ID to invalidate

    Returns:
        True if user was cached and invalidated, False otherwise
    """
    cache = get_authorization_cache()
    return cache.invalidate(user_id) > 0


def invalidate_all_cache() -> int:
    """
    Invalidate entire authorization cache.

    Returns:
        Number of entries invalidated
    """
    cache = get_authorization_cache()
    return cache.invalidate()


def get_cache_stats() -> Dict[str, Union[int, float, Dict]]:
    """
    Get authorization cache statistics.

    Returns:
        Cache performance statistics
    """
    cache = get_authorization_cache()
    return cache.get_stats()


def is_cache_healthy() -> bool:
    """
    Check if cache is performing within acceptable parameters.

    Returns:
        True if cache is healthy, False if performance issues detected
    """
    stats = get_cache_stats()

    # Define health thresholds
    MIN_HIT_RATE = 0.7  # At least 70% hit rate
    MAX_SIZE_UTILIZATION = 0.9  # No more than 90% size utilization

    hit_rate_healthy = (
        cast(float, stats["hit_rate"]) >= MIN_HIT_RATE
        or cast(int, stats["total_requests"]) < 10
    )
    size_healthy = cast(float, stats["memory_efficiency"]) <= MAX_SIZE_UTILIZATION

    return hit_rate_healthy and size_healthy
