"""
Security audit service for comprehensive authorization and sync logging.

Provides structured audit logging for all security events, authorization attempts,
Airtable sync operations, and performance metrics to ensure complete observability
and compliance with security monitoring requirements.
"""

import json
import logging
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

# Configuration imported where needed

logger = logging.getLogger(__name__)

# Performance thresholds for authorization operations
AUTHORIZATION_FAST_THRESHOLD_MS = 100  # < 100ms is considered fast
AUTHORIZATION_SLOW_THRESHOLD_MS = 300  # > 300ms is considered slow


@dataclass
class AuthorizationEvent:
    """
    Data structure for authorization events.

    Captures all relevant information about user authorization attempts
    including cache state and Airtable metadata for complete audit trail.
    """

    user_id: Optional[int]
    action: str
    result: str  # "granted", "denied"
    user_role: Optional[str]
    cache_state: str  # "hit", "miss", "refresh", "error"
    timestamp: Optional[datetime] = None
    airtable_metadata: Optional[Dict[str, Any]] = None
    error_details: Optional[str] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class SyncEvent:
    """
    Data structure for Airtable sync events.

    Captures sync operation details including performance metrics,
    success/failure status, and failed record details for monitoring.
    """

    sync_type: str  # "scheduled_refresh", "manual_refresh", "cache_invalidation"
    duration_ms: int
    records_processed: int
    success: bool
    timestamp: Optional[datetime] = None
    error_details: Optional[str] = None
    failed_record_ids: Optional[List[str]] = None

    def __post_init__(self):
        """Set defaults if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)
        if self.failed_record_ids is None:
            self.failed_record_ids = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


@dataclass
class PerformanceMetrics:
    """
    Data structure for performance metrics.

    Captures timing and performance data for authorization operations
    to ensure performance requirements are met and monitored.
    """

    operation: str
    duration_ms: int
    cache_hit: bool
    user_role: Optional[str]
    timestamp: Optional[datetime] = None
    additional_context: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        """Set timestamp if not provided."""
        if self.timestamp is None:
            self.timestamp = datetime.now(timezone.utc)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class SecurityAuditService:
    """
    Security audit service for comprehensive logging and monitoring.

    Provides structured logging for authorization events, sync operations,
    and performance metrics to ensure complete security observability.
    """

    def __init__(self):
        """Initialize security audit service."""
        self.logger = logging.getLogger(__name__)

    def log_authorization_event(self, event: AuthorizationEvent) -> None:
        """
        Log authorization event with appropriate severity level.

        Denied access attempts are logged as warnings for security monitoring.
        Granted access is logged as info for audit trail.

        Args:
            event: Authorization event to log
        """
        # Create structured log message
        log_data: Dict[str, Any] = {
            "event_type": "authorization_event",
            "user_id": event.user_id,
            "action": event.action,
            "result": event.result,
            "user_role": event.user_role,
            "cache_state": event.cache_state,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

        # Add optional fields if present
        if event.airtable_metadata:
            log_data["airtable_metadata"] = event.airtable_metadata

        if event.error_details:
            log_data["error_details"] = event.error_details

        # Format log message
        log_message = f"SECURITY_AUDIT: {json.dumps(log_data)}"

        # Log at appropriate level based on result
        if event.result == "denied":
            denied_message = (
                "SECURITY_AUDIT: DENIED access attempt - "
                f"User {event.user_id} (role: {event.user_role}) "
                f"attempted '{event.action}'"
            )
            self.logger.warning(f"{denied_message} - {log_message}")
        else:
            self.logger.info(log_message)

    def log_sync_event(self, event: SyncEvent) -> None:
        """
        Log Airtable sync event with performance and error details.

        Failed syncs are logged as errors, successful syncs as info.

        Args:
            event: Sync event to log
        """
        # Create structured log message
        log_data = {
            "event_type": "sync_event",
            "sync_type": event.sync_type,
            "duration_ms": event.duration_ms,
            "records_processed": event.records_processed,
            "success": event.success,
            "timestamp": event.timestamp.isoformat() if event.timestamp else None,
        }

        # Add failure details if present
        if not event.success:
            if event.error_details:
                log_data["error_details"] = event.error_details
            if event.failed_record_ids:
                log_data["failed_record_count"] = len(event.failed_record_ids)
                # Don't log full record IDs for privacy, just count

        # Format log message
        base_message = (
            f"SYNC_AUDIT: {event.sync_type} - {event.duration_ms}ms - "
            f"{event.records_processed} records"
        )

        if event.success:
            self.logger.info(f"{base_message} - SUCCESS: {json.dumps(log_data)}")
        else:
            failed_count = (
                len(event.failed_record_ids) if event.failed_record_ids else 0
            )
            self.logger.error(
                f"{base_message} - FAILED: {failed_count} failed records - "
                f"{json.dumps(log_data)}"
            )

    def log_performance_metrics(self, metrics: PerformanceMetrics) -> None:
        """
        Log performance metrics with appropriate severity based on thresholds.

        Slow operations (>300ms) are logged as warnings for monitoring.
        Fast operations (<100ms) are logged as debug for detailed tracking.
        Medium operations are logged as info.

        Args:
            metrics: Performance metrics to log
        """
        # Create structured log message
        log_data = {
            "event_type": "performance_metrics",
            "operation": metrics.operation,
            "duration_ms": metrics.duration_ms,
            "cache_hit": metrics.cache_hit,
            "user_role": metrics.user_role,
            "timestamp": metrics.timestamp.isoformat() if metrics.timestamp else None,
        }

        if metrics.additional_context:
            log_data["additional_context"] = metrics.additional_context

        # Format log message
        base_message = (
            f"PERFORMANCE: {metrics.operation} - {metrics.duration_ms}ms - "
            f"cache_hit={metrics.cache_hit} - role={metrics.user_role}"
        )

        # Log at appropriate level based on performance thresholds
        if metrics.duration_ms > AUTHORIZATION_SLOW_THRESHOLD_MS:
            self.logger.warning(
                f"{base_message} - SLOW operation: {json.dumps(log_data)}"
            )
        elif metrics.duration_ms < AUTHORIZATION_FAST_THRESHOLD_MS:
            self.logger.debug(f"{base_message} - {json.dumps(log_data)}")
        else:
            self.logger.info(f"{base_message} - {json.dumps(log_data)}")

    def create_authorization_event(
        self,
        user_id: Optional[int],
        action: str,
        result: str,
        user_role: Optional[str],
        cache_state: str,
        airtable_metadata: Optional[Dict[str, Any]] = None,
        error_details: Optional[str] = None,
    ) -> AuthorizationEvent:
        """
        Helper method to create authorization event.

        Args:
            user_id: User ID from Telegram
            action: Action being attempted
            result: "granted" or "denied"
            user_role: User's role ("admin", "coordinator", "viewer", None)
            cache_state: Cache state ("hit", "miss", "refresh", "error")
            airtable_metadata: Optional Airtable record metadata
            error_details: Optional error details for denied access

        Returns:
            AuthorizationEvent instance
        """
        return AuthorizationEvent(
            user_id=user_id,
            action=action,
            result=result,
            user_role=user_role,
            cache_state=cache_state,
            airtable_metadata=airtable_metadata,
            error_details=error_details,
        )

    def create_sync_event(
        self,
        sync_type: str,
        duration_ms: int,
        records_processed: int,
        success: bool,
        error_details: Optional[str] = None,
        failed_record_ids: Optional[List[str]] = None,
    ) -> SyncEvent:
        """
        Helper method to create sync event.

        Args:
            sync_type: Type of sync operation
            duration_ms: Duration in milliseconds
            records_processed: Number of records processed
            success: Whether sync was successful
            error_details: Optional error details
            failed_record_ids: Optional list of failed record IDs

        Returns:
            SyncEvent instance
        """
        return SyncEvent(
            sync_type=sync_type,
            duration_ms=duration_ms,
            records_processed=records_processed,
            success=success,
            error_details=error_details,
            failed_record_ids=failed_record_ids or [],
        )

    def create_performance_metrics(
        self,
        operation: str,
        duration_ms: int,
        cache_hit: bool,
        user_role: Optional[str],
        additional_context: Optional[Dict[str, Any]] = None,
    ) -> PerformanceMetrics:
        """
        Helper method to create performance metrics.

        Args:
            operation: Operation being measured
            duration_ms: Duration in milliseconds
            cache_hit: Whether operation used cache
            user_role: User's role for the operation
            additional_context: Optional additional context data

        Returns:
            PerformanceMetrics instance
        """
        return PerformanceMetrics(
            operation=operation,
            duration_ms=duration_ms,
            cache_hit=cache_hit,
            user_role=user_role,
            additional_context=additional_context,
        )


# Global service instance for easy access
_audit_service: Optional[SecurityAuditService] = None


def get_security_audit_service() -> SecurityAuditService:
    """
    Get the global security audit service instance.

    Returns:
        SecurityAuditService instance
    """
    global _audit_service
    if _audit_service is None:
        _audit_service = SecurityAuditService()
    return _audit_service
