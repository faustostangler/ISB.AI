# ADR-002: Task Queue Abstraction via Hexagonal Port

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) requires asynchronous background task execution for web scraping, PDF extraction, vector indexing, and embedding/LLM processing. 

Directly coupling use cases or application services to a concrete background task runner (e.g., Celery, Dramatiq, or RQ) violates Hexagonal Architecture boundaries and introduces strong dependency lock-in. Moreover, it forces tests and local development to run a live message broker (like Redis or RabbitMQ) even for simple unit tests, degrading developer experience (DX).

We need an abstraction that allows us to run tasks synchronously/in-memory for local testing, yet scale to a high-performance out-of-process worker pool in staging and production.

## Decision

We will introduce a `TaskQueuePort` in the application layer of Bounded Contexts that require background processing. We will use dynamic dependency injection at the Composition Root (`main.py`) to switch adapters:
1. **Local/Testing Adapter (`ImmediateTaskQueueAdapter`)**: Runs tasks synchronously and immediately on the calling thread (or via a standard `ThreadPoolExecutor`), eliminating broker requirements.
2. **Production/Staging Adapter (`RedisDramatiqAdapter`)**: Enqueues tasks into a Redis broker using **Dramatiq** for out-of-process execution on worker containers.

Use cases will invoke background tasks by interacting solely with the `TaskQueuePort` interface.

## Consequences

### Positive
- **Domain Purity**: Application and Domain layers remain 100% decoupled from queuing frameworks and network brokers.
- **Fast, Hermetic Testing**: Unit and integration tests can execute worker flows synchronously without Docker containers or brokers by using the `ImmediateTaskQueueAdapter`.
- **Flexible Scaling**: We can swap Dramatiq for Celery, Amazon SQS, or any other broker-based system by changing only the Infrastructure layer Adapter.
- **Improved DX**: Local developers can run the system without spinning up Redis unless they are testing queue-specific infrastructure behavior.

### Negative
- **Abstraction Overhead**: Requires defining explicit `TaskQueuePort` interfaces and payload structures (DTOs/Value Objects) for every background task, adding minor boilerplate code.
- **Task Orchestration**: Complex workflows (like canvas/chains) must be handled by translating them through the adapter layer rather than using native library DSLs (like Celery's `.signature()`).

### Neutral
- **Payload Restrictions**: Task parameters must be serializable (e.g., standard Python primitives or Pydantic schemas) to ensure they can pass network boundaries when using the Redis adapter.

## Alternatives Considered

### Alternative A: Celery coupled directly to Use Cases
- **Pros:** Mature, feature-rich, supports complex chaining.
- **Cons:** Heavy dependency; pollutes use cases with `@app.task` decorators; notoriously complex configuration; hard to test hermetically.
- **Why rejected:** Direct coupling violates our architectural rules, and Celery is overengineered for our KISS monolith requirements.

### Alternative B: FastAPI `BackgroundTasks`
- **Pros:** Built-in, extremely simple.
- **Cons:** Runs in-process; cannot scale horizontally; CPU-heavy tasks (like local embeddings) will block the API server's event loop.
- **Why rejected:** Not suitable for CPU-bound or heavy ML inference workloads.

## Compliance

- [x] Hexagonal Architecture layers respected (Ports in application, concrete queue adapters in infrastructure)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (hermetic unit tests run synchronously via immediate adapter)
- [x] Observability plan included (telemetry tracked via Dramatiq middleware sending execution metrics to Prometheus)
- [x] LGPD/Security implications assessed (task payloads are stripped of raw PII/unencrypted credentials before serialization)

## References

- Domain reference: `references/project_layout.md`, `references/37-DevOps, DDD, TDD, ADRs, Code.md`
