# SPEC-014: Observability, Distributed Tracing, and Alerting Specification

**Linked ADR:** [ADR-014](../adr/ADR-014-observability-architecture.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform / Observability  

## 1. Overview & Objectives

This specification defines the validation criteria for structured JSON logging, distributed OpenTelemetry trace context propagation, Prometheus metrics exports, and Sentry crash interception.

## 2. Invariants & Telemetry Rules

* **Invariant 1**: All logs emitted to standard output must be valid, single-line JSON strings with mandatory fields: `timestamp` (ISO-8601), `level`, `logger`, and `message`.
* **Invariant 2**: If a log statement is executed within an active OpenTelemetry tracer scope, the resulting JSON output must include fields `trace_id` and `span_id`.
* **Invariant 3**: Asynchronous task enqueue operations must inject the active trace context metadata (`traceparent`) into the task broker message envelope.
* **Invariant 4**: The `/metrics` presentation endpoint must respond in standard OpenMetrics plaintext format, exposing the Prometheus Golden Signals.
* **Invariant 5**: Any unhandled application exception must be captured by the Sentry SDK integration before the process exits or returns a generic HTTP 500 error.

## 3. Test Strategy Classification

* **Unit Tests (Telemetry)**:
  - Scope: Test context propagation, custom JSON logging formatters, and metrics endpoints:
    - Assert that custom Python logging formatters produce valid JSON output under all scenarios.
    - Assert that the logging formatter injects dummy `trace_id` and `span_id` when OTel context mock fields are present.
    - Assert that `TaskQueuePort` adapters correctly extract OTel headers from active environments and inject them into the task payloads.
    - Assert that receiving workers extract the OTel context payload and instantiate the correct active parent span.
* **Integration Tests (Platform)**:
  - Scope: Assert endpoint functionality and error capturing:
    - Assert that fetching the `/metrics` endpoint yields standard Prometheus metrics containing HTTP request metrics.
    - Test that throwing a division-by-zero error on a test API router triggers the Sentry client mock call containing the exception payload.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Structured JSON Logging with Trace Correlation
* **Given**: An active HTTP request trace with `trace_id = "0af7651916cd43dd8448eb211c80319c"`.
* **When**: The application writes a log statement using `logger.info("Executing database query")`.
* **Then**: The resulting stdout string must be a single-line JSON:
  ```json
  {"timestamp": "2026-05-26T12:15:00.000Z", "level": "INFO", "logger": "src.db", "message": "Executing database query", "trace_id": "0af7651916cd43dd8448eb211c80319c", "span_id": "b7ad6b7169203331"}
  ```
* **And**: The JSON must be valid and parsable.

### Scenario 2: Trace Context Propagation Across Task Queue
* **Given**: An active API request context with trace ID `T_001`.
* **When**: The user triggers an upload task that calls `task_queue.submit("ingest_media", file_path)`.
* **Then**: The task enqueue message payload in Redis must contain the envelope key `"traceparent": "00-T_001-..."`.
* **When**: The background worker picks up the task from Redis.
* **Then**: The worker must extract `"traceparent"`, start a child span under trace ID `T_001`, and emit logs with `trace_id = "T_001"`.

### Scenario 3: Prometheus Golden Signals Export
* **Given**: The application has processed 50 API requests with varying latency.
* **When**: Fetching the `/metrics` endpoint.
* **Then**: The payload must return standard OpenMetrics format.
* **And**: Contain the following time-series:
  - `isb_http_requests_total` (counter, labeled by method, path, status)
  - `isb_http_request_duration_seconds` (histogram, labeled by method, path)
  - `isb_process_cpu_usage` (gauge)
  - `isb_process_memory_bytes` (gauge)

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Trace Context | Corrupted/Invalid `traceparent` | Ignores context, starts new trace; does not crash |
| Prometheus Registry | Duplicate metric names | Raises `ValueError` at startup (fail-fast) |
| Sentry Network | Target connection offline | Caches/drops error internally; does not block request thread |

## 6. Observability & Telemetry Assertions (Alerting Thresholds)

* **SRE Golden Signal Alert Rules**:
  - **Latency Alert**: Trigger high-priority alert if `isb_http_request_duration_seconds{quantile="0.95"}` exceeds `2.0` seconds over a 5-minute sliding window.
  - **Errors Alert**: Trigger critical alert if `isb_http_requests_total{status=~"5.."}` / `isb_http_requests_total` exceeds `5%` of total traffic.
  - **CUDA Saturation Alert**: Trigger warning alert if NVIDIA GPU memory utilization exceeds `90%` for more than 2 minutes.
