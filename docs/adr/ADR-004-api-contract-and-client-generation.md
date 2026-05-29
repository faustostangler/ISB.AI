# ADR-004: API Contract and Client Generation via FastAPI and Orval

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) uses SvelteKit for the presentation frontend and FastAPI for the core backend services. They communicate over HTTP/JSON APIs. 

Manually writing client-side fetch functions and duplicating data schemas (Pydantic V2 classes in Python, Interfaces/Types in TypeScript) results in significant developer friction, duplication of effort, and a high risk of silent integration bugs when contracts drift. We need a way to ensure 100% compile-time type safety across the network boundary with minimal manual configuration.

## Decision

We will adopt a **Code-First API Contract** strategy. FastAPI routers and Pydantic V2 models will serve as the single source of truth for the API contract. 

To bridge the backend and frontend:
1. **Schema Exporter CLI**: We will implement a lightweight CLI utility inside our presentation entry point that exports the FastAPI application's generated OpenAPI schema directly to a JSON file (`openapi.json`) without spinning up the Uvicorn HTTP server.
2. **Orval Client Generation**: The SvelteKit frontend will use **Orval** to read the exported `openapi.json` and automatically generate strongly-typed TypeScript HTTP clients, query keys, and fetch functions.

The schema export command will be integrated into local format/lint loops (e.g., via `Makefile` commands) and CI/CD pipelines.

## Consequences

### Positive
- **Single Source of Truth**: Backend modifications in Pydantic models are immediately propagated to the frontend client interfaces.
- **Type Safety**: Full end-to-end compile-time type checking from the database (via Pydantic schemas) to Svelte components.
- **Improved DX**: Frontend developers can consume new endpoints immediately by running a single command to regenerate types.
- **No Server Requirement**: The schema exporter CLI eliminates the need to run an active development server just to generate client contracts.

### Negative
- **Build Sequence Dependency**: Frontend client regeneration depends on running the Python exporter command first. This requires the frontend build machine or developer workspace to have the Python virtual environment set up.

### Neutral
- **OpenAPI Schema Versioning**: The exported `openapi.json` will be tracked in git, providing a clear visual diff of API contract changes during Pull Request reviews.

## Alternatives Considered

### Alternative A: Design-First OpenAPI (YAML Spec First)
- **Pros:** Standard approach; decouples frontend and backend development timelines.
- **Cons:** Verbose YAML maintenance; high risk of implementation deviating from the written contract.
- **Why rejected:** Introduces unnecessary friction for a unified codebase and small team.

### Alternative B: gRPC / Protocol Buffers
- **Pros:** Extremely fast binary serialization; strict schema contract.
- **Cons:** Complex web browser integration (requires gRPC-web proxying or specialized client-side libraries).
- **Why rejected:** Overengineered for a web application BFF-to-Monolith layout.

## Domain Model Impact

This decision affects only the **Presentation layer** boundary. No Domain Entities or Value Objects are modified.

- **Port**: N/A (API serialization runs in the Presentation Layer, not inside the core Application or Domain)
- **Adapter**: FastAPI routing/validation handlers, Orval generated client
- **Bounded Context**: Platform / Presentation (Cross-cutting infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected (schemas and routers stay in presentation layer)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (schema validation and Orval compilation tests)
- [x] Observability plan included
- [x] LGPD/Security implications assessed (ensures strict validation schemas prevent payload injection)

## References

- Domain reference: `references/37-DevOps, DDD, TDD, ADRs, Code.md`

