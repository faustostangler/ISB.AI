# SPEC-005: Concurrency and Distributed Locking Specification

**Linked ADR:** [ADR-005](../adr/ADR-005-distributed-locking-abstraction.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Shared Kernel / Infrastructure / Worker

## 1. Overview & Objectives

This specification defines the validation criteria for lock acquisition and release. It guarantees that parallel scraping workers do not execute duplicate fetches for the same URL, and verifies the context manager usage.

## 2. Bounded Context & Domain Invariants

Concurrency locking is handled via the `LockPort` in the application layer.
- **Invariant 1**: A lock is bound to a specific string identifier (e.g. `lock:scrape:url:<hashed_url>`).
- **Invariant 2**: Acquiring an already held lock must return immediately as `false` or block until a timeout occurs, depending on lock parameters.
- **Invariant 3**: Locks must always be released, even in the event of unhandled exceptions within the protected block.

## 3. Test Strategy Classification

- **Unit Tests (Domain & Ports)**:
  - Scope: Test Use Cases utilizing `InMemLockAdapter` to ensure concurrent attempts trigger expected lock-held exceptions.
- **Integration Tests (Adapters & Infra)**:
  - Scope: Test the `RedisLockAdapter` against a real Redis instance.
  - Assertions: Verify atomic acquisition, expiration behavior, and that a client can only release its own lock (using matching token signatures).

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Context Manager Releases Lock on Success
- **Given**: A lock identifier `lock:test`.
- **When**: Entering the `LockPort` context manager.
- **Then**: The lock must be successfully acquired.
- **And**: Upon exiting the context manager block successfully, the lock must be released.
- **And**: A subsequent attempt to acquire the lock must succeed.

### Scenario 2: Context Manager Releases Lock on Failure
- **Given**: A lock identifier `lock:test-fail`.
- **When**: Entering the `LockPort` context manager.
- **And**: An unhandled exception occurs inside the code block.
- **Then**: The exception must propagate out of the block.
- **And**: The lock must be successfully released in the teardown phase.

### Scenario 3: Mismatched Token Release Protection
- **Given**: Client A acquires the lock `lock:test-safe` with token `token-A`.
- **And**: The lock expires or is held past its deadline.
- **When**: Client B acquires the lock `lock:test-safe` with token `token-B`.
- **And**: Client A attempts to release the lock `lock:test-safe` with token `token-A`.
- **Then**: The release attempt must fail (or be ignored by the Lua script) to prevent Client A from releasing Client B's lock.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| lock key  | `None` or empty | `ValueError` |
| release token | mismatched | No-op (does not release) |

## 6. Observability & Telemetry Assertions

- **Audit Logs**:
  - Log lock acquisitions and releases at debug level.
  - Log lock collisions (attempts to acquire an already held lock) at warning level.
- **Prometheus Metrics**:
  - Lock latency: `isb_lock_acquire_duration_seconds`.
  - Lock collisions: `isb_lock_collisions_total` counter labeled by lock key prefix.
