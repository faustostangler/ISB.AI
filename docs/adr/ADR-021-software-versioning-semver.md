# ADR-021: Software Versioning and Automated Release Strategy via SemVer

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is developed as a Modular Monolith with separate logical subdomains that may eventually evolve into independent microservices. We also generate client SDKs and OpenAPI specs for downstream consumption.

We need a consistent software versioning scheme to:
1. Communicate API compatibility guarantees clearly to developers and client integrations.
2. Automate release management, avoiding manual tagging errors or forgotten version increments.
3. Manage software updates and rollbacks in our environments (development, staging, production) predictably.

Without a structured versioning standard, updating packages or APIs can result in unexpected breaking changes (dependency hell), leading to high regression rates and deployment downtime.

## Decision

We will adopt **Semantic Versioning (SemVer) 2.0.0** coupled with **Conventional Commits** to automate our codebase release cycles.

Key implementation rules include:
1. **Three-Tier Version Scheme**: Versions will be formatted as `MAJOR.MINOR.PATCH`:
   - `MAJOR` increments on incompatible API updates (breaking changes).
   - `MINOR` increments on backward-compatible feature additions.
   - `PATCH` increments on backward-compatible bug fixes or security patches.
2. **Conventional Commits Enforcement**: Developers and agents must write commit messages adhering to the Angular commit format:
   - `feat(...)`: maps to a `MINOR` bump.
   - `fix(...)`: maps to a `PATCH` bump.
   - Breaking changes must contain the `BREAKING CHANGE:` footer or `!` suffix to trigger a `MAJOR` bump.
3. **Automated Pipeline Releases**: The CI/CD pipeline (GitHub Actions) will scan commit logs using automation tools (e.g., `semantic-release`), automatically tag the repository on successful builds of the main branch, update `pyproject.toml` version metadata, and compile the `CHANGELOG.md`.
4. **Pre-Releases**: Alpha and Beta releases for staging environments will use suffix metadata (e.g., `1.0.0-alpha.1` or `1.0.0-rc.1`).

## Consequences

### Positive
- **Predictable API Stability**: Consumer systems know immediately if an upgrade contains breaking changes based on the version changes.
- **Automated Operations**: Removes manual release overhead. The changelog and git tags are kept perfectly in sync with the codebase state.
- **Microservices Readiness**: Facilitates clean boundary management when splitting contexts into independent deployments in the future.

### Negative
- **Developer Discipline Required**: Developers must strictly follow Conventional Commit conventions. Commits that are poorly structured can cause incorrect version increments.
- **Pipeline Complexity**: Adds commit linting and version bump stages to our CI/CD workflows.

### Neutral
- Container images built by the pipeline will be tagged matching the exact SemVer tag (e.g., `isb:1.2.3`), with floating tags (`isb:1`, `isb:1.2`) created automatically to support rolling updates of minor/patch changes.

## Alternatives Considered

### Alternative B: Calendar Versioning (CalVer)
- **Pros**: Direct correlation between version name and release date; simple for continuous-delivery SaaS applications.
- **Cons**: Conveys zero information about breaking API changes or compatibility limits, which is dangerous for generated clients and modular APIs.
- **Why rejected**: Lacks the required contract enforcement necessary to support our microservices-ready modular monolith.

### Alternative C: Incremental Build Numbering
- **Pros**: Zero-config execution; simple sequence numbering.
- **Cons**: No structural info, no dates, no version semantics.
- **Why rejected**: Completely insufficient for managing distributed dependency layers and contract validation.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined
- [x] Observability plan included
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-004: API Contract and Client Generation](ADR-004-api-contract-and-client-generation.md)
- Domain reference: `references/37-DevOps, DDD, TDD, ADRs, Code.md` (Release governance rules)
