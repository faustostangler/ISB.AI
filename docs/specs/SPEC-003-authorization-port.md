# SPEC-003: Access Control and Purge Authorization Specification

**Linked ADR:** [ADR-003](../adr/ADR-003-authorization-port.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Shared Kernel / Ingress / Application Security

## 1. Overview & Objectives

This specification defines the validation scenarios and interfaces for the `AuthorizationPort`. It guarantees that all resource-level operations are validated against the requester's identity, specifically protecting destructive tasks such as LGPD data purges.

## 2. Bounded Context & Domain Invariants

Authorization is handled through a port interface in the application layer.
- **Value Object**: `Subject`
  - Validation: Must contain a valid user ID (non-empty string) and a dictionary of claims.
- **Value Object**: `Resource`
  - Validation: Must contain a valid resource ID (non-empty string) and resource type.
- **Value Object**: `Action`
  - Validation: Must match one of the predefined CRUD/purge action types (read, write, delete, purge).

## 3. Test Strategy Classification

- **Unit Tests (Domain & Ports)**:
  - Scope: Test Use Cases (e.g. `PurgeUserDataUseCase`) injecting a mocked `AuthorizationPort`.
  - Assertions: Verify that if the mock returns `false` (unauthorized), the use case raises a `PermissionDeniedError` and halts database execution.
- **Integration Tests (Adapters & Infra)**:
  - Scope: Test the `LocalRuleAuthorizationAdapter` against various configurations of Subject, Action, and Resource.
  - Verification: Ensure ownership mismatch triggers immediate denial.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Owner Authorized to Purge Data
- **Given**: A user with ID `user-123` (Subject).
- **And**: An ingestion resource with owner ID `user-123` (Resource).
- **When**: The user requests a `purge` action.
- **Then**: The `AuthorizationPort` must return `true`.

### Scenario 2: Non-Owner Denied Deletion (IDOR Prevention)
- **Given**: A user with ID `user-456` (Subject).
- **And**: A note resource with owner ID `user-123` (Resource).
- **When**: The user requests a `delete` action.
- **Then**: The `AuthorizationPort` must return `false`.
- **And**: The calling use case must raise `PermissionDeniedError`.

### Scenario 3: Platform Administrator Authorized for Maintenance
- **Given**: A user with role `administrator` and ID `user-admin` (Subject).
- **And**: Any user's note resource with owner ID `user-123` (Resource).
- **When**: The admin requests a `delete` action.
- **Then**: The `AuthorizationPort` must return `true` (if admin delegation is enabled).

## 5. Boundary Conditions & Exception Mapping

| Requester ID | Resource Owner ID | Action | Expected Outcome / Exception |
|--------------|-------------------|--------|------------------------------|
| `user-123`   | `user-123`        | `purge`| `true` (Allowed)             |
| `user-456`   | `user-123`        | `purge`| `PermissionDeniedError`      |
| `None`       | `user-123`        | `read` | `PermissionDeniedError`      |

## 6. Regression Anchors (For Bug Fixes Only)

*None at present (greenfield configuration).*

## 7. Observability & Telemetry Assertions

- **Audit Logging**:
  - Every denied authorization check must emit a security warning log containing the requester ID, resource ID, action, and timestamp.
  - **IMPORTANT**: To maintain LGPD/security compliance, logs must never contain PII or unredacted credentials.
- **Prometheus Metrics**:
  - Access failures: `isb_auth_denials_total` counter labeled by resource type and action.

