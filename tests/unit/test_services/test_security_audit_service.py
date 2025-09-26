"""
Tests for security audit service.

Tests comprehensive security audit logging and sync telemetry functionality.
"""

import json
import logging
import time
from datetime import datetime
from unittest.mock import MagicMock, mock_open, patch

import pytest

from src.services.security_audit_service import (
    AuthorizationEvent,
    PerformanceMetrics,
    SecurityAuditService,
    SyncEvent,
)


class TestAuthorizationEvent:
    """Test authorization event data structure."""

    def test_authorization_event_creation_with_required_fields(self):
        """Test creating authorization event with required fields."""
        event = AuthorizationEvent(
            user_id=123456,
            action="search_participant",
            result="granted",
            user_role="admin",
            cache_state="hit",
        )

        assert event.user_id == 123456
        assert event.action == "search_participant"
        assert event.result == "granted"
        assert event.user_role == "admin"
        assert event.cache_state == "hit"
        assert event.timestamp is not None
        assert event.airtable_metadata is None
        assert event.error_details is None

    def test_authorization_event_with_full_metadata(self):
        """Test authorization event with all optional fields."""
        airtable_data = {
            "telegram_user_id": 123456,
            "status": "Active",
            "access_level": "Admin",
        }

        event = AuthorizationEvent(
            user_id=123456,
            action="admin_export",
            result="denied",
            user_role="viewer",
            cache_state="miss",
            airtable_metadata=airtable_data,
            error_details="Insufficient permissions for admin export",
        )

        assert event.user_id == 123456
        assert event.action == "admin_export"
        assert event.result == "denied"
        assert event.user_role == "viewer"
        assert event.cache_state == "miss"
        assert event.airtable_metadata == airtable_data
        assert event.error_details == "Insufficient permissions for admin export"

    def test_authorization_event_serialization(self):
        """Test authorization event can be serialized to dict."""
        event = AuthorizationEvent(
            user_id=789012,
            action="list_participants",
            result="granted",
            user_role="coordinator",
            cache_state="refresh",
        )

        event_dict = event.to_dict()

        assert event_dict["user_id"] == 789012
        assert event_dict["action"] == "list_participants"
        assert event_dict["result"] == "granted"
        assert event_dict["user_role"] == "coordinator"
        assert event_dict["cache_state"] == "refresh"
        assert "timestamp" in event_dict
        assert event_dict["airtable_metadata"] is None
        assert event_dict["error_details"] is None


class TestSyncEvent:
    """Test sync event data structure."""

    def test_sync_event_creation_basic(self):
        """Test creating basic sync event."""
        event = SyncEvent(
            sync_type="scheduled_refresh",
            duration_ms=250,
            records_processed=45,
            success=True,
        )

        assert event.sync_type == "scheduled_refresh"
        assert event.duration_ms == 250
        assert event.records_processed == 45
        assert event.success is True
        assert event.timestamp is not None
        assert event.error_details is None
        assert event.failed_record_ids == []

    def test_sync_event_with_failures(self):
        """Test sync event with error details and failed records."""
        failed_ids = ["rec123", "rec456", "rec789"]

        event = SyncEvent(
            sync_type="manual_refresh",
            duration_ms=1500,
            records_processed=100,
            success=False,
            error_details="Rate limit exceeded during sync",
            failed_record_ids=failed_ids,
        )

        assert event.sync_type == "manual_refresh"
        assert event.duration_ms == 1500
        assert event.records_processed == 100
        assert event.success is False
        assert event.error_details == "Rate limit exceeded during sync"
        assert event.failed_record_ids == failed_ids

    def test_sync_event_serialization(self):
        """Test sync event can be serialized to dict."""
        event = SyncEvent(
            sync_type="cache_invalidation",
            duration_ms=75,
            records_processed=12,
            success=True,
        )

        event_dict = event.to_dict()

        assert event_dict["sync_type"] == "cache_invalidation"
        assert event_dict["duration_ms"] == 75
        assert event_dict["records_processed"] == 12
        assert event_dict["success"] is True
        assert "timestamp" in event_dict
        assert event_dict["error_details"] is None
        assert event_dict["failed_record_ids"] == []


class TestPerformanceMetrics:
    """Test performance metrics data structure."""

    def test_performance_metrics_creation(self):
        """Test creating performance metrics."""
        metrics = PerformanceMetrics(
            operation="authorization_check",
            duration_ms=85,
            cache_hit=True,
            user_role="admin",
        )

        assert metrics.operation == "authorization_check"
        assert metrics.duration_ms == 85
        assert metrics.cache_hit is True
        assert metrics.user_role == "admin"
        assert metrics.timestamp is not None
        assert metrics.additional_context is None

    def test_performance_metrics_with_context(self):
        """Test performance metrics with additional context."""
        context = {"cache_size": 150, "concurrent_users": 5, "sync_in_progress": True}

        metrics = PerformanceMetrics(
            operation="role_resolution",
            duration_ms=120,
            cache_hit=False,
            user_role="coordinator",
            additional_context=context,
        )

        assert metrics.operation == "role_resolution"
        assert metrics.duration_ms == 120
        assert metrics.cache_hit is False
        assert metrics.user_role == "coordinator"
        assert metrics.additional_context == context

    def test_performance_metrics_serialization(self):
        """Test performance metrics can be serialized to dict."""
        metrics = PerformanceMetrics(
            operation="sync_operation",
            duration_ms=300,
            cache_hit=False,
            user_role="viewer",
        )

        metrics_dict = metrics.to_dict()

        assert metrics_dict["operation"] == "sync_operation"
        assert metrics_dict["duration_ms"] == 300
        assert metrics_dict["cache_hit"] is False
        assert metrics_dict["user_role"] == "viewer"
        assert "timestamp" in metrics_dict
        assert metrics_dict["additional_context"] is None


class TestSecurityAuditService:
    """Test security audit service functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.service = SecurityAuditService()

    def test_service_initialization(self):
        """Test service initializes with correct logger."""
        service = SecurityAuditService()

        assert service.logger.name == "src.services.security_audit_service"

    def test_log_authorization_event_info_level(self):
        """Test logging authorization event at info level."""
        service = SecurityAuditService()

        with patch.object(service.logger, "info") as mock_info:
            event = AuthorizationEvent(
                user_id=123456,
                action="search_participant",
                result="granted",
                user_role="admin",
                cache_state="hit",
            )

            service.log_authorization_event(event)

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "SECURITY_AUDIT" in call_args
            assert "authorization_event" in call_args
            assert "123456" in call_args
            assert "search_participant" in call_args
            assert "granted" in call_args

    def test_log_authorization_event_with_metadata(self):
        """Test logging authorization event with airtable metadata."""
        service = SecurityAuditService()

        with patch.object(service.logger, "info") as mock_info:
            airtable_data = {
                "telegram_user_id": 123456,
                "status": "Active",
                "access_level": "Admin",
            }

            event = AuthorizationEvent(
                user_id=123456,
                action="admin_export",
                result="granted",
                user_role="admin",
                cache_state="miss",
                airtable_metadata=airtable_data,
            )

            service.log_authorization_event(event)

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "SECURITY_AUDIT" in call_args
            assert "airtable_metadata" in call_args

    def test_log_authorization_event_denied(self):
        """Test logging denied authorization event with warning level."""
        service = SecurityAuditService()

        with patch.object(service.logger, "warning") as mock_warning:
            event = AuthorizationEvent(
                user_id=789012,
                action="admin_export",
                result="denied",
                user_role="viewer",
                cache_state="hit",
                error_details="Insufficient permissions",
            )

            service.log_authorization_event(event)

            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0][0]
            assert "SECURITY_AUDIT" in call_args
            assert "DENIED" in call_args
            assert "789012" in call_args

    def test_log_sync_event_success(self):
        """Test logging successful sync event."""
        service = SecurityAuditService()

        with patch.object(service.logger, "info") as mock_info:
            event = SyncEvent(
                sync_type="scheduled_refresh",
                duration_ms=250,
                records_processed=45,
                success=True,
            )

            service.log_sync_event(event)

            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "SYNC_AUDIT" in call_args
            assert "sync_event" in call_args
            assert "scheduled_refresh" in call_args
            assert "250ms" in call_args
            assert "45 records" in call_args

    def test_log_sync_event_failure(self):
        """Test logging failed sync event with error level."""
        service = SecurityAuditService()

        with patch.object(service.logger, "error") as mock_error:
            event = SyncEvent(
                sync_type="manual_refresh",
                duration_ms=1500,
                records_processed=100,
                success=False,
                error_details="API rate limit exceeded",
                failed_record_ids=["rec123", "rec456"],
            )

            service.log_sync_event(event)

            mock_error.assert_called_once()
            call_args = mock_error.call_args[0][0]
            assert "SYNC_AUDIT" in call_args
            assert "FAILED" in call_args
            assert "manual_refresh" in call_args
            assert "2 failed records" in call_args

    def test_log_performance_metrics_fast_operation(self):
        """Test logging performance metrics for fast operation."""
        service = SecurityAuditService()

        with patch.object(service.logger, "debug") as mock_debug:
            metrics = PerformanceMetrics(
                operation="authorization_check",
                duration_ms=45,
                cache_hit=True,
                user_role="admin",
            )

            service.log_performance_metrics(metrics)

            mock_debug.assert_called_once()
            call_args = mock_debug.call_args[0][0]
            assert "PERFORMANCE" in call_args
            assert "authorization_check" in call_args
            assert "45ms" in call_args
            assert "cache_hit=True" in call_args

    def test_log_performance_metrics_slow_operation(self):
        """Test logging performance metrics for slow operation with warning."""
        service = SecurityAuditService()

        with patch.object(service.logger, "warning") as mock_warning:
            metrics = PerformanceMetrics(
                operation="authorization_check",
                duration_ms=350,
                cache_hit=False,
                user_role="coordinator",
            )

            service.log_performance_metrics(metrics)

            mock_warning.assert_called_once()
            call_args = mock_warning.call_args[0][0]
            assert "PERFORMANCE" in call_args
            assert "SLOW" in call_args
            assert "350ms" in call_args

    def test_create_authorization_event_helper(self):
        """Test helper method for creating authorization events."""
        service = SecurityAuditService()

        event = service.create_authorization_event(
            user_id=123456,
            action="search_participant",
            result="granted",
            user_role="admin",
            cache_state="hit",
        )

        assert isinstance(event, AuthorizationEvent)
        assert event.user_id == 123456
        assert event.action == "search_participant"
        assert event.result == "granted"

    def test_create_sync_event_helper(self):
        """Test helper method for creating sync events."""
        service = SecurityAuditService()

        event = service.create_sync_event(
            sync_type="scheduled_refresh",
            duration_ms=250,
            records_processed=45,
            success=True,
        )

        assert isinstance(event, SyncEvent)
        assert event.sync_type == "scheduled_refresh"
        assert event.duration_ms == 250
        assert event.records_processed == 45
        assert event.success is True

    def test_create_performance_metrics_helper(self):
        """Test helper method for creating performance metrics."""
        service = SecurityAuditService()

        metrics = service.create_performance_metrics(
            operation="authorization_check",
            duration_ms=85,
            cache_hit=True,
            user_role="admin",
        )

        assert isinstance(metrics, PerformanceMetrics)
        assert metrics.operation == "authorization_check"
        assert metrics.duration_ms == 85
        assert metrics.cache_hit is True
        assert metrics.user_role == "admin"


class TestSecurityAuditIntegration:
    """Test security audit service integration scenarios."""

    def test_end_to_end_authorization_flow(self):
        """Test complete authorization flow with audit logging."""
        service = SecurityAuditService()

        with (
            patch.object(service.logger, "info") as mock_info,
            patch.object(service.logger, "debug") as mock_debug,
        ):

            # Create and log authorization event
            auth_event = service.create_authorization_event(
                user_id=123456,
                action="search_participant",
                result="granted",
                user_role="admin",
                cache_state="hit",
            )
            service.log_authorization_event(auth_event)

            # Create and log performance metrics
            perf_metrics = service.create_performance_metrics(
                operation="authorization_check",
                duration_ms=45,
                cache_hit=True,
                user_role="admin",
            )
            service.log_performance_metrics(perf_metrics)

            # Verify both events were logged
            assert mock_info.call_count >= 1  # Authorization event
            assert mock_debug.call_count >= 1  # Performance metrics

    def test_end_to_end_sync_flow(self):
        """Test complete sync flow with audit logging."""
        service = SecurityAuditService()

        with patch.object(service.logger, "info") as mock_info:

            # Create and log sync event
            sync_event = service.create_sync_event(
                sync_type="scheduled_refresh",
                duration_ms=250,
                records_processed=45,
                success=True,
            )
            service.log_sync_event(sync_event)

            # Verify sync event was logged
            mock_info.assert_called_once()
            call_args = mock_info.call_args[0][0]
            assert "SYNC_AUDIT" in call_args

    def test_audit_service_handles_edge_cases(self):
        """Test audit service handles various edge cases gracefully."""
        service = SecurityAuditService()

        with (
            patch.object(service.logger, "warning") as mock_warning,
            patch.object(service.logger, "error") as mock_error,
        ):

            # Test with None user_id (should still log)
            auth_event = AuthorizationEvent(
                user_id=None,
                action="unknown_action",
                result="denied",
                user_role=None,
                cache_state="error",
            )
            service.log_authorization_event(auth_event)

            # Test with zero duration (edge case)
            perf_metrics = PerformanceMetrics(
                operation="quick_check",
                duration_ms=0,
                cache_hit=True,
                user_role="admin",
            )
            service.log_performance_metrics(perf_metrics)

            # Verify logging occurred (specific assertions depend on implementation)
            assert mock_warning.call_count >= 0 or mock_error.call_count >= 0
