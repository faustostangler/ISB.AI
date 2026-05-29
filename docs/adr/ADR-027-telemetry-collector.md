# ADR-027: Telemetry Exporting Architecture via OpenTelemetry Collector

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) generates extensive telemetry signals: metrics (e.g. inference latencies, conformal prediction sizes), logs (structured JSON), and traces (across web endpoints, background workers, and model servers). 

If the application exports this data directly from its execution thread, we face critical constraints:
1. **CPU/Event Loop Blocking**: Batching, compressing, and sending spans over HTTP/gRPC runs inside the Python application processes, risking latency spikes and event-loop blocks.
2. **Vendor Lock-in**: Directly importing and configuring backend-specific exporters in Python couples our codebase configuration to our current observability vendors (Tempo/Prometheus/Jaeger). Changing providers in the future would require code modification.
3. **No Network Buffer**: If our trace visualization server goes down under high load, directly exporting SDKs will lose traces or block request processing threads.

We need a resilient, decoupled architecture that offloads telemetry processing, abstracts backend endpoints, and preserves developer workstation resources.

## Decision

We will implement telemetry exporting by routing all application and worker metrics and traces through a local **OpenTelemetry Collector** running as a containerized proxy agent.

Specific implementation details:
1. **Application Instrumenting**:
   The Python OpenTelemetry SDK will be configured with a standard OTLP/gRPC exporter pointing to `http://localhost:4317` (using default non-blocking OTLP configurations).
2. **OTel Collector Deployment**:
   We will add the `otel/opentelemetry-collector-contrib` container to our `docker-compose.yml` and Kubernetes manifests.
3. **Collector Pipelines (`otel-collector-config.yaml`)**:
   The collector configuration will define:
   - **Receivers**: OTLP (gRPC on port `4317` and HTTP on port `4318`).
   - **Processors**: `batch` (to combine spans/metrics and optimize network payloads) and `memory_limiter` (to prevent resource starvation).
   - **Exporters**: `prometheus` (exposing metrics for scraping) and `otlp` (routing traces to Tempo/Jaeger).
4. **Resilience & Buffering**:
   The OTel collector will manage local memory/disk retry buffers to cache spans in the event of backend network hiccups.

## Consequences

### Positive
* **Decoupled Architecture**: The Python application is 100% vendor-agnostic, using only default OpenTelemetry OTLP protocols. Swapping backends is done strictly by updating `otel-collector-config.yaml`.
* **Zero Main-Thread Latency**: Span serialization, compression, and exporting tasks are offloaded out-of-process to the highly optimized Go-based collector.
* **Telemetry Buffer & Resilience**: Prevents data loss during backend hiccups or transient network partition failures.
* **Environment Parity**: The same collector architecture runs locally and in Kubernetes.

### Negative
* **Minor Resource Footprint**: Running the collector container consumes a small amount of memory (~30-50MB RAM) on our development workstation.
* **Configuration Overhead**: Requires maintaining the `otel-collector-config.yaml` file.

### Neutral
* **Network Protocol**: The collector supports both gRPC (port 4317) and HTTP (port 4318) protocols, allowing clients to connect using either transport format.

## Alternatives Considered

### Alternative B: Direct SDK-to-Backend Exporting
* **Pros**: Avoids deploying the extra collector container.
* **Cons**: Introduces event-loop blocking risks; hard-couples Python package imports and configurations to specific vendor APIs.
* **Why rejected**: Violates hexagonal architectural separation and degrades python event-loop performance.

## Domain Model Impact

This decision affects only the container collection and routing topology. No Domain Entities or Value Objects are modified.

- **Port**: N/A (telemetry exporting runs out-of-band and is configured strictly at the container orchestration tier)
- **Adapter**: OTel Collector configuration files (`otel-collector-config.yaml`)
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected (observability configurations isolated in infrastructure config)
- [x] No monitoring vendor dependencies in Domain layer
- [x] Telemetry buffering and retries configured
- [x] Prometheus Golden Signals exposed via collector

## References

- Related ADRs: [ADR-014: Unified Observability Architecture via OpenTelemetry, Prometheus, Grafana Loki, and Sentry](./ADR-014-observability-architecture.md)
- Domain reference: `references/31-12 Observability and Operation 3.md` (OpenTelemetry Traces Concept)

