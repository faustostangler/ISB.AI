# ADR-016: Dependency Injection and Component Wiring via Composition Root

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) is developed as a Modular Monolith following clean hexagonal architecture principles. As the system scales to include multiple Bounded Contexts (e.g. Ingestion, Knowledge, Platform), dependencies between use cases, ports, and external adapters must be wired securely.

FastAPI is our primary web framework. It provides a native dependency injection tool via `Depends()`. However:
1. **Coupling**: Utilizing inline `Depends()` forces routing files to import infrastructure adapters (such as database sessions, file repositories, and model clients) directly in route signatures to construct use cases. This couples presentation routes to outer implementation adapters and violates Hexagonal isolation boundaries.
2. **Scattered Wiring**: Spreading initialization logic across router files makes it difficult to trace which adapters are bound to which ports, complicating dependency audits and static typing analysis.
3. **DX and Test Parity**: Using external complex dependency injection libraries (such as `dependency-injector`) introduces heavy boilerplate, proprietary DSL decorators, and framework magic, violating the KISS principle.

We need a clean, framework-agnostic dependency injection strategy that preserves a single Composition Root, allows simple unit-test overrides, and enforces compile-time type checking.

## Decision

We will implement manual dependency injection at a single **Composition Root** located in `src/main.py` (and test setup entry points). 

Specifically:
1. **Single-Instantiation Bootstrapping**: During application startup (in `src/main.py`), we will load settings, instantiate all concrete infrastructure adapters, wire them to their target use cases, and attach these fully constructed use cases as singletons to the FastAPI `app.state` object.
2. **Zero-Wiring Presentation Routes**: FastAPI route definitions will remain clean "Humble Objects" and will never import infrastructure adapters or use case constructors. Instead, they will retrieve the wired use cases directly from the running request's application state (e.g., `request.app.state.ingest_use_case`).
3. **Test-Time Overrides**: In unit and integration test configurations, we will override the registered singletons directly on the test application instance `app.state` to swap production adapters for test stubs (such as `InMemLockAdapter` or memory-based repositories) without changing router definitions or using complex mocking libraries.

## Consequences

### Positive
- **Hexagonal Isolation**: Route controllers are completely decoupled from adapter constructors, preserving a clean boundary between the presentation layer and infrastructure.
- **Single Source of Truth**: The wiring of the entire monolith is declared in one file (`src/main.py`), making it straightforward to inspect, document, and debug component lifetimes.
- **Low Overhead**: Instantiating objects once on startup avoids request-time instantiation latency.
- **Zero Framework Lock-in**: The DI strategy relies entirely on standard Python object constructor passing, keeping the core domain and use cases free of external decorators.

### Negative
- **Manual Wiring Overhead**: Adding new ports or use cases requires manually editing `src/main.py` to wire the new components.
- **Implicit Route Typing**: Fetching use cases from `app.state` requires either adding type hints inside the route function or using type-asserting properties/helpers to satisfy static checkers like mypy.

### Neutral
- **Process Scope**: All wired use cases are singletons within the process workspace, requiring stateless design patterns inside application use cases.

## Alternatives Considered

### Alternative A: Native FastAPI `Depends()` resolving
- **Pros:** Native framework support; automatic request context handling.
- **Cons:** Router files are forced to import concrete adapter classes, breaking the decoupling goals of Hexagonal Architecture.
- **Why rejected:** Tightly couples presentation routers to infrastructure implementation.

### Alternative B: Third-Party DI Frameworks (e.g. `dependency-injector`)
- **Pros:** Automated container declarations; dynamic lifetime scopes.
- **Cons:** Unnecessary complexity and runtime magic for a modular monolith.
- **Why rejected:** Violates the KISS principle.

## Compliance

- [x] Hexagonal Architecture layers respected (Composition Root lives at the outermost entry boundary)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (override `app.state` properties in tests)
- [x] Observability plan included
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-004: API Contract and Client Generation](ADR-004-api-contract-and-client-generation.md)
- Domain reference: `references/project_layout.md`, `references/37-DevOps, DDD, TDD, ADRs, Code.md`
