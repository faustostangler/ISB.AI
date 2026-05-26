# ADR-014: Unified Observability Architecture via OpenTelemetry, Prometheus, Grafana Loki, and Sentry

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is built as a modular monolith but executes tasks using an asynchronous, decoupled layout. A single ingestion request flows from our Caddy ingress, through the FastAPI web server, into a Redis task broker, out to an asynchronous ingestion worker executing system binaries (`ffmpeg`), and finally submits payloads to an out-of-process CUDA model server (Whisper/VLM sidecar). 

In this multi-process, heterogeneous hardware environment:
1. **Silent Failures**: Failures in background tasks or model servers are hard to trace and debug without correlated context.
2. **Resource Saturation**: The local workstation's NVIDIA RTX 2060 GPU (6 GB VRAM) is a highly constrained resource. We need real-time alerting on VRAM and CPU memory saturation before it triggers OOM crashes.
3. **12-Factor Compliance**: The application must treat logs as event streams, outputting structured logs directly to `stdout`/`stderr` rather than writing to mutable files or local databases.
4. **Fast Incident Loop**: Unhandled application errors must be instantly captured, aggregated, and mapped to source code lines to maintain a low Change Failure Rate.

## Decision

We will implement a unified observability stack combining OpenTelemetry (OTel) for distributed tracing, Prometheus for metrics collection, Grafana Loki for log aggregation, and Sentry for error reporting.

Specific implementation details:
1. **Distributed Tracing (OpenTelemetry)**:
   - We will instrument the FastAPI presentation layer, HTTP client adapters, and the Redis-based task worker layer using OpenTelemetry SDKs.
   - Context propagation will be enforced across process and network boundaries (e.g., passing `trace_id` headers through Redis message payloads and sidecar HTTP headers).
2. **Structured Logging (Grafana Loki)**:
   - All application logs will be written to standard output (`stdout`) in structured JSON format (using `python-json-logger`).
   - Log statements will automatically inject the current OpenTelemetry `trace_id` and `span_id` when executing within an active trace context, enabling instant correlation.
3. **Metrics Collection (Prometheus)**:
   - We will expose a `/metrics` endpoint on the presentation API server and use Prometheus client libraries to publish system metrics (Prometheus Golden Signals: Latency, Traffic, Errors, Saturation).
   - We will expose domain-specific metrics (e.g., embedding latency, prediction conformal set cardinality, prefix cache hit rate).
   - In production and local development, we will deploy a Prometheus node-exporter and NVIDIA GPU exporter to track system memory and CUDA VRAM saturation.
4. **Crash Reporting (Sentry)**:
   - We will integrate Sentry natively into the application and worker bootstrap configurations. Sentry will capture unhandled exceptions, including context details (environment configurations, metadata properties, and user IDs).

## Consequences

### Positive
* **End-to-End Tracing Visibility**: Developers can trace a single document ingestion request through its entire path (ingress -> API -> queue -> worker -> ffmpeg -> Whisper sidecar), localizing latency bottlenecks or crash vectors instantly.
* **Correlated Telemetry**: Clicking a trace in Grafana allows viewing the exact matching JSON logs in Loki and the associated CPU/GPU metrics in Prometheus, cutting Mean Time to Resolution (MTTR).
* **Fault Isolation**: Sentry alerts immediately pinpoint code regressions, linking them to version commits and environments.
* **12-Factor App Compliance**: The container stdout stream remains clean and structured, leaving log routing, persistence, and rotation to the container platform.

### Negative
* **Instrumenting Overhead**: Requires configuring OTel telemetry propagation in our task queues and client wrappers.
* **Telemetry Data Footprint**: Traces and metrics generate extra network traffic and disk storage. We will configure sensible sampling rates (e.g. 100% in development, 10% in production for successful traces, 100% for error traces) to manage costs.

## Alternatives Considered

### Option B: Structured JSON Logs and Prometheus Metrics (No Distributed Tracing)
* **Pros:** Simpler configuration; zero context propagation overhead in Celery/Redis.
* **Cons:** Blind spots in asynchronous task execution. Finding out why a specific Whisper transcription task timed out requires manual cross-referencing of timestamp strings across different logs, significantly increasing debugging overhead.
* **Why rejected:** Distributed context is crucial for diagnosing multi-stage async pipelines.

### Option C: Local File-Based Logs and Custom Database Log Tables
* **Pros:** Self-contained, does not require deploying Prometheus or Loki sidecars.
* **Cons:** Completely violates 12-Factor App design. Writing logs to database tables creates write contention, database disk bloat, and resource starvation on our primary storage engine.
* **Why rejected:** Poor scalability and violates container state isolation.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] Telemetry configuration isolated in infrastructure/presentation layers
- [x] Prometheus Golden Signals monitored
- [x] OTel context propagation across Redis queue boundaries enforced
- [x] Trace-to-Log correlation implemented

## References

- Related ADRs: [ADR-002: Task Queue Abstraction](ADR-002-task-queue-abstraction.md), [ADR-006: Secure Non-Root Container](ADR-006-secure-non-root-container.md), [ADR-009: Out-of-Process Model Serving](ADR-009-out-of-process-model-serving.md)
- Domain reference: `references/29-12 Observability and Operation 1.md`, `references/30-12 Observability and Operation 2.md`, `references/31-12 Observability and Operation 3.md`
