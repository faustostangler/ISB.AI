# SPEC-027: Telemetry Exporting and Collector Specification

**Linked ADR:** [ADR-027](../adr/ADR-027-telemetry-collector.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure / Observability  

## 1. Overview & Objectives

This specification defines the integration and validation criteria for exporting OpenTelemetry traces and metrics through the local OpenTelemetry Collector. It guarantees that context propagation, batching, and backend routing function correctly under simulated network outages.

## 2. Invariants & Observability Rules

*   **Invariant 1**: The application SDK must only export metrics and traces to the local collector endpoints (`localhost:4317` for gRPC or `localhost:4318` for HTTP).
*   **Invariant 2**: Distributed tracing must propagate the `traceparent` context header across Redis queues and network requests.
*   **Invariant 3**: Application logging handlers must capture the active trace ID and span ID and append them to structured JSON logs.
*   **Invariant 4**: In the event of a backend tracing destination failure (e.g. Tempo container offline), the OTel collector must queue spans locally, and the application must continue processing requests normally.

## 3. Test Strategy Classification

*   **Unit Tests (OTel Context Propagation)**:
    *   Scope: Test request header parsing and queue task serialization.
    *   Assertions: Verify that executing a background task extracts the `trace_id` sent by the API presentation server.
*   **Integration Tests (Telemetry Export Flow)**:
    *   Scope: Mock the OTel collector OTLP receiver endpoint.
    *   Assertions:
        *   Sending an HTTP request to the API server generates spans that successfully land on the mock collector port `4317`.
        *   Uncaught exceptions successfully trigger Sentry capture blocks and write corresponding trace correlation tags in stdout logs.
*   **Resilience & Offline Tests**:
    *   Scope: Stop the trace backend (e.g., Jaeger/Tempo) and run request workloads.
    *   Assertions:
        *   The OTel collector successfully batches and stores the spans in memory/disk queue files.
        *   The API server does not block or return timeouts.
        *   Once the backend is restarted, the collector flushes the queued spans successfully.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Trace ID Correlation across monolithic layers
*   **Given**: An incoming HTTP request with no tracing headers.
*   **When**: The FastAPI middleware processes the request and queues an ingestion task.
*   **Then**: It must generate a new `trace_id`.
*   **And**: Append this `trace_id` to the JSON logs.
*   **And**: Inject the trace context into the Dramatiq task payload.
*   **And**: The worker process must resume the same `trace_id` for downstream Whisper tasks.

### Scenario 2: OTel Collector Buffers under Target Outage
*   **Given**: The backend tracing storage container is offline.
*   **When**: Telemetry signals are pushed to the OTel Collector.
*   **Then**: The collector must log a warning but buffer data.
*   **And**: The API server responds immediately to user actions without latency.

### Scenario 3: Prometheus Scrapes Collector Metrics
*   **Given**: The Prometheus scraper queries the OTel collector on port `8889` (or `/metrics`).
*   **When**: A query is executed.
*   **Then**: It must expose standard metrics including API counts and queue durations.

## 5. Boundary Conditions & Exception Mapping

| Parameter / Port | Condition | Expected Outcome |
|------------------|-----------|------------------|
| OTel Collector Socket | Port `4317` blocked | SDK drops span payloads asynchronously, does not crash process, logs warn. |
| Memory Limits | Collector memory exceeds 100MB | `memory_limiter` processor drops oldest spans, keeps collector active. |
| Context Injection | None / Malformed header | Generate a new root span context, execute normally. |
