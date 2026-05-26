# SPEC-002: Task Queue Abstraction Specification

**Linked ADR:** [ADR-002](../adr/ADR-002-task-queue-abstraction.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Shared Kernel / Infrastructure

## 1. Overview & Objectives

This specification defines the contract for background task execution in ISB.AI. It guarantees that tasks can be scheduled by use cases without knowledge of the underlying message broker, and validates the behavior of both synchronous (testing) and asynchronous (production) queue adapters.

## 2. Bounded Context & Domain Invariants

Background task scheduling is handled via the `TaskQueuePort` defined in the application layer.
- **Invariant 1**: All task inputs must be serializable to JSON (primitives, dictionaries, or Pydantic models).
- **Invariant 2**: Tasks must be idempotent to allow safe retries.

## 3. Test Strategy Classification

- **Unit Tests (Domain & Ports)**:
  - Scope: Test use case task dispatching using `ImmediateTaskQueueAdapter`.
  - Assertions: Verify the task is executed inline and the expected state modifications occur immediately.
- **Integration Tests (Adapters & Infra)**:
  - Scope: Verify `RedisDramatiqAdapter` puts jobs into Redis, and the Dramatiq worker successfully pulls and executes them.
  - Dependencies: Requires a running Redis test container.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Immediate/Synchronous Task Execution (Local & Test)
- **Given**: An `ImmediateTaskQueueAdapter` is registered as the task runner.
- **When**: A task is dispatched with arguments `{"url": "https://example.com"}`.
- **Then**: The task logic must run immediately on the same thread.
- **And**: The task execution result must be reflected in the database/state before the dispatch method returns.

### Scenario 2: Asynchronous Broker Enqueuing (Production & Staging)
- **Given**: A `RedisDramatiqAdapter` is registered with a running Redis connection.
- **When**: A task is dispatched.
- **Then**: A message representing the task and payload must be pushed into the Redis queue.
- **And**: The call must return a unique task ID immediately without waiting for the task to finish execution.

### Scenario 3: Task Payload Validation
- **Given**: The `TaskQueuePort` is invoked.
- **When**: A non-serializable object (e.g. an open file handle, database connection session) is passed as a parameter.
- **Then**: A `TaskSerializationError` must be raised immediately before queueing.

## 5. Boundary Conditions & Exception Mapping

| Input Parameters | Scenario | Expected Exception |
|------------------|----------|--------------------|
| Custom Class Obj | Non-serializable type | `TaskSerializationError` |
| `None`           | Empty task identifier | `ValueError` |

## 6. Observability & Telemetry Assertions

- **Prometheus Metrics**:
  - Worker execution time: `isb_worker_task_duration_seconds` histogram.
  - Tasks count: `isb_worker_tasks_total` counter labeled by task name and status (`success`, `failed`).
- **Sentry Logging**:
  - Task execution failures must be logged to Sentry with the task ID and payload metadata.
