import logging

import pytest
from prometheus_client import REGISTRY

from isb.shared_kernel.adapters.authorization.local_rule import LocalRuleAuthorizationAdapter
from isb.shared_kernel.ports.authorization import (
    Action,
    PermissionDeniedError,
    Resource,
    Subject,
)

# --- Value Object Validation Tests ---

def test_subject_validation_raises_value_error_on_empty_user_id() -> None:
    """Verify that Subject raises ValueError on empty or whitespace user_id."""
    with pytest.raises(ValueError, match="User ID cannot be empty"):
        Subject(user_id="")

    with pytest.raises(ValueError, match="User ID cannot be empty"):
        Subject(user_id="   ")


def test_resource_validation_raises_value_error_on_empty_identifiers() -> None:
    """Verify that Resource raises ValueError on empty resource_id or resource_type."""
    with pytest.raises(ValueError, match="Identifier fields cannot be empty"):
        Resource(resource_id="", resource_type="note")

    with pytest.raises(ValueError, match="Identifier fields cannot be empty"):
        Resource(resource_id="note-123", resource_type="   ")


# --- LocalRuleAuthorizationAdapter Tests ---

def test_owner_authorized_to_purge_data() -> None:
    """Scenario 1: Owner of the resource must be authorized for purge actions."""
    adapter = LocalRuleAuthorizationAdapter()
    subject = Subject(user_id="user-123")
    resource = Resource(resource_id="doc-999", resource_type="ingestion", owner_id="user-123")

    # Should authorize and not raise
    assert adapter.authorize(subject, Action.PURGE, resource) is True
    adapter.enforce(subject, Action.PURGE, resource)


def test_non_owner_denied_deletion_raises_permission_denied() -> None:
    """Scenario 2: Non-owner must be denied and raise PermissionDeniedError (IDOR prevention)."""
    adapter = LocalRuleAuthorizationAdapter()
    subject = Subject(user_id="user-456")
    resource = Resource(resource_id="note-777", resource_type="note", owner_id="user-123")

    assert adapter.authorize(subject, Action.DELETE, resource) is False

    with pytest.raises(PermissionDeniedError, match="not authorized"):
        adapter.enforce(subject, Action.DELETE, resource)


def test_administrator_authorized_for_maintenance() -> None:
    """Scenario 3: Users with administrator role bypass ownership verification."""
    adapter = LocalRuleAuthorizationAdapter()
    subject = Subject(user_id="user-admin", claims={"role": "administrator"})
    resource = Resource(resource_id="note-777", resource_type="note", owner_id="user-123")

    assert adapter.authorize(subject, Action.DELETE, resource) is True
    adapter.enforce(subject, Action.DELETE, resource)


def test_observability_assertions_on_denial(caplog: pytest.LogCaptureFixture) -> None:
    """Observability: Access denials must trigger warnings and increment Prometheus metrics."""
    adapter = LocalRuleAuthorizationAdapter()
    subject = Subject(user_id="user-456")
    resource = Resource(resource_id="note-777", resource_type="note", owner_id="user-123")

    # Capture logs at WARNING level for security audit
    with caplog.at_level(logging.WARNING, logger="isb.security"):
        # Record Prometheus metric before denial
        metric_before = REGISTRY.get_sample_value(
            "isb_auth_denials_total",
            {"resource_type": "note", "action": "delete"}
        ) or 0.0

        # Execute unauthorized action
        assert adapter.authorize(subject, Action.DELETE, resource) is False

        # Verify Prometheus metric has incremented
        metric_after = REGISTRY.get_sample_value(
            "isb_auth_denials_total",
            {"resource_type": "note", "action": "delete"}
        ) or 0.0
        assert metric_after == metric_before + 1.0

        # Verify audit logs contain non-PII details
        assert len(caplog.records) == 1
        record = caplog.records[0]
        assert "Access Denied" in record.message
        assert "user-456" in record.message
        assert "note-777" in record.message
        assert "delete" in record.message
        # Invariant check: Ensure no PII like emails or secrets are accidentally logged
        assert "email" not in record.message
        assert "password" not in record.message


def test_empty_subject_user_id_denied() -> None:
    """Verify that an empty subject user ID (bypassing validation) is denied."""
    adapter = LocalRuleAuthorizationAdapter()
    # Bypass Pydantic validation via model_construct to reach the adapter check
    subject = Subject.model_construct(user_id="")
    resource = Resource(resource_id="note-777", resource_type="note", owner_id="user-123")

    assert adapter.authorize(subject, Action.DELETE, resource) is False
