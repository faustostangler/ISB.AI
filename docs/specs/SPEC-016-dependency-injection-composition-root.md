# SPEC-016: Dependency Injection and Composition Root Specification

**Linked ADR:** [ADR-016](../adr/ADR-016-dependency-injection-composition-root.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Platform / Bootstrapping

## 1. Overview & Objectives

This specification defines the validation criteria for manual dependency injection, initialization verification, routing controllers isolation, and state properties type-assertions. It guarantees that all components are wired correctly at boot time.

## 2. Invariants & Bootstrap Rules

* **Invariant 1**: No route handler inside any `presentation` layer context is permitted to import an infrastructure adapter or instantiate a core use case.
* **Invariant 2**: The application container configuration must execute the manual wiring sequence in `src/main.py` once during the startup phase.
* **Invariant 3**: If any required environment setting or resource dependency (e.g. database connectivity) fails validation during manual wiring, the bootstrap script must terminate the process with exit code `1` (fail-fast bootstrap).
* **Invariant 4**: In test mode, use case registry properties on `app.state` must be hot-swappable to override production adapters with test stubs.

## 3. Test Strategy Classification

* **Unit Tests (Compilation & Linting)**:
  - Scope: Assert that router files do not contain imports of database adapters or use case constructor objects (static import analysis).
* **Integration Tests (Bootstrap & State)**:
  - Scope: Test the wiring logic and state registration in `src/main.py`:
    - Test that launching the composition root setup registers all use case singletons on `app.state`.
    - Test that a `ValidationError` or failure in adapter configuration blocks app startup and returns exit code `1`.
    - Test that test-client overrides correctly mount an in-memory stub and execute the mock path.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Successful Composition Root Wiring
* **Given**: A fully configured environment (valid `.env` properties).
* **When**: The FastAPI application is instantiated via `src/main.py`.
* **Then**: The bootstrap logic must resolve all adapter dependencies.
* **And**: Instantiate all core application use cases.
* **And**: Register them as attributes of `app.state` (e.g., `app.state.ingest_use_case` is registered and is an instance of `IngestUseCase`).

### Scenario 2: Fail-Fast on Connection Failure during Wiring
* **Given**: A database configuration pointing to an offline server.
* **When**: The application attempts to boot and configure the database persistence adapter.
* **Then**: The connection check must fail, raise a mapped database connection exception, log a `CRITICAL` alert, and prevent the application from binding to HTTP ports.

### Scenario 3: Test Override on App State
* **Given**: A running FastAPI test client instance.
* **When**: Overriding a registered use case via `app.state.ingest_use_case = MockIngestUseCase()`.
* **Then**: HTTP calls to the ingestion endpoint must execute the mock use case instead of the production persistence adapter.
* **And**: Return the mock response successfully.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| `app.state` Lookup | Attribute not registered | `AttributeError` raised (fail-fast request execution) |
| System environment | Incomplete parameters | `pydantic.ValidationError` / Bootstrap Aborted |

## 6. Observability & Telemetry Assertions

* **Audit Logs**:
  - Log start of dependency resolution and wiring sequence at `INFO` level.
  - Log successful component wiring complete stating the counts of registered adapters and use cases at `INFO` level.
  - Log any bootstrapping error at `CRITICAL` level with full traceback.
