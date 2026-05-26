# SPEC-019: Kubernetes Deployment, Self-Healing, and Resource Rightsizing Specification

**Linked ADR:** [ADR-019](../adr/ADR-019-kubernetes-deployment-and-self-healing.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Operations / Infrastructure  

## 1. Overview & Objectives

This specification defines the validation criteria for container self-healing behaviors, health probe routes, resource limits, and auto-scaling rules. It guarantees that our applications start safely, report connectivity status, and are bounded by resource rules under Kubernetes.

## 2. Bounded Context & Domain Invariants

- **Component**: API Health Endpoints
  - Invariant 1: `/health/startup` must return `200 OK` only after Composition Root wiring is completed.
  - Invariant 2: `/health/ready` must return `200 OK` if database and cache ports are accessible, and `503 Service Unavailable` if any vital dependency fails.
  - Invariant 3: `/health/live` must return `200 OK` as long as the HTTP event loop is responsive.
- **Component**: Resource Definition
  - Invariant 4: Resource requests must be strictly less than or equal to resource limits (`requests.cpu <= limits.cpu` and `requests.memory <= limits.memory`).

## 3. Test Strategy Classification

- **Integration Tests (Health Check Adapters)**:
  - Scope: Execute health check routes using FastAPI TestClient. Mock downstream adapters (DB, Cache) to simulate connection timeouts and disconnects.
- **Static Analysis (Kubernetes Manifests)**:
  - Scope: Run validation scripts (e.g., `kube-score` or structured schema checkers) on our deployment YAML files to verify CPU/memory request allocations and probe configurations.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: API Startup Check Success
- **Given**: The FastAPI application is starting up.
- **When**: Composition root wiring finishes successfully.
- **Then**: An HTTP `GET` request to `/health/startup` returns status `200 OK` with payload `{"status": "started"}`.

### Scenario 2: API Readiness Check with Database Outage
- **Given**: The database adapter is unreachable (connection timeout).
- **When**: An HTTP `GET` request to `/health/ready` is received.
- **Then**: The route returns status `503 Service Unavailable` with payload indicating the failed database dependency: `{"status": "unhealthy", "checks": {"database": "disconnected", "cache": "connected"}}`.

### Scenario 3: API Liveness Check During Event Loop Responsiveness
- **Given**: The FastAPI process is running normally.
- **When**: An HTTP `GET` request to `/health/live` is received.
- **Then**: The route returns status `200 OK` with payload `{"status": "alive"}`.

### Scenario 4: Manifest Validation via Static Checks
- **Given**: A Kubernetes deployment manifest file.
- **When**: Audited by the validation scanner or static tests.
- **Then**: It must define `resources.requests`, `resources.limits`, `livenessProbe`, `readinessProbe`, and `startupProbe` for all containers.

## 5. Boundary Conditions & Exception Mapping

| Target Probe Endpoint | Adapter State | Expected HTTP Status Code |
|-----------------------|---------------|---------------------------|
| `/health/startup`     | Bootstrapping | `503 Service Unavailable` |
| `/health/startup`     | Active        | `200 OK`                  |
| `/health/ready`       | Database Down | `503 Service Unavailable` |
| `/health/ready`       | Cache Down    | `503 Service Unavailable` |
| `/health/ready`       | All Ports Up  | `200 OK`                  |
| `/health/live`        | Deadlocked    | Timeout (No response)     |

## 6. Observability & Telemetry Assertions

- **Prometheus Metrics**:
  - Assert that an health check failure increments the counter `isb_health_check_failures_total{check="database"}` or `isb_health_check_failures_total{check="cache"}`.
- **Sentry Integration**:
  - Assert that a sustained health check failure (e.g., database down for more than 3 consecutive checks) logs a `critical` event to Sentry.
