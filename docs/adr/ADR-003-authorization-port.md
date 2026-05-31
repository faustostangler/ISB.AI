# ADR-003: Access Control and LGPD Purge Authorization via Hexagonal Port

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) is a multi-tenant personal knowledge assistant. Users store highly personal data, including web scrapings, private notes, and chat histories. Protecting data privacy and ensuring compliance with data protection laws such as LGPD (Lei Geral de Proteção de Dados) is a critical requirement. 

Specifically, LGPD grants users the right to request the complete deletion (purge) of their personal data. We must guarantee that:
1. Access control checks are applied systematically to all resource interactions.
2. Destructive operations, such as a permanent data purge, can only be initiated and executed by the resource owner.
3. Access decisions are decoupled from routing/presentation code (FastAPI) and storage code (SQLAlchemy/PostgreSQL).

Hardcoding user-resource checks in endpoint handlers or directly in SQL queries is error-prone, hard to audit, and susceptible to Insecure Direct Object Reference (IDOR) vulnerabilities.

## Decision

We will define an `AuthorizationPort` in the application layer. This interface exposes a generic method to authorize a subject (the user) executing an action (e.g., read, write, delete, purge) on a resource (e.g., note, ingestion feed, entire user profile).

For security-critical use cases, particularly the **LGPD Data Purge Use Case**, the orchestrator will fetch the target resource and invoke the `AuthorizationPort` to verify ownership before proceeding with the database deletion.

We will write a lightweight infrastructure adapter `LocalRuleAuthorizationAdapter` that validates attributes locally (e.g., matching the user ID with the resource owner ID). This adapter can be upgraded to an external policy engine (like Open Policy Agent or Keycloak) without modifying domain entities or application use cases.

## Consequences

### Positive
- **LGPD Compliance**: Ensures a strict, auditable boundary for destructive and read operations, preventing unauthorized data purges.
- **Hexagonal Segregation**: Access control logic is isolated in the infrastructure adapter, keeping application use cases clean.
- **Protection Against IDOR**: Centralizing authorization checks ensures developers do not forget to validate resource ownership on new endpoints.
- **Clean Upgrade Path**: We can swap the rule-based local adapter for a sidecar-based OPA or Zanzibar-style ReBAC adapter if horizontal scale or complex sharing permissions are needed later.

### Negative
- **Fetch Before Write**: Verifying resource ownership requires fetching the resource metadata from the database before performing the action, adding a minor query overhead.
- **Context Translation**: Requires mapping request context (HTTP headers/JWT claims) and domain entities into generic Subject and Resource DTOs.

### Neutral
- **Role resolution**: User role metadata and permission policies are managed and decoded outside the domain model boundary (e.g., within Presentation API middleware).

## Alternatives Considered

### Alternative A: Role-Based Ingress (FastAPI Router dependencies)
- **Pros:** Extremely simple to implement; native to FastAPI.
- **Cons:** Only validates if a user has a role (e.g., "User" or "Admin"), but cannot evaluate resource-level ownership (e.g., "User A cannot delete User B's notes").
- **Why rejected:** Insufficient for LGPD requirements which mandate resource-level relationship evaluation.

### Alternative B: Direct OPA Integration
- **Pros:** Declarative policies (Rego); highly scalable.
- **Cons:** Adds infrastructure complexity; requires running and managing an OPA container.
- **Why rejected:** Overengineered for early monolith stages; our hexagonal abstraction allows us to defer this cost.

## Domain Model Impact

- **Port**: `AuthorizationPort` (application layer — user authentication/authorization checker)
- **Adapters**:
  - `LocalRuleAuthorizationAdapter` (infrastructure — in-process attribute check)
  - `OpaAuthorizationAdapter` (infrastructure — remote Open Policy Agent sidecar)
- **Bounded Context**: User Identity Context (Supporting Domain)
- **Value Objects**: `Subject` (User ID/claims), `Resource` (Resource ID/type), `Action` (CRUD/purge enum)

## Compliance

- [x] Hexagonal Architecture layers respected (AuthorizationPort in application, Rule evaluator in infrastructure)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (stub/mock the AuthorizationPort in use-case tests)
- [x] Observability plan included (audit logs emitted for denied authorization requests)
- [x] LGPD/Security implications assessed (explicitly designed to prevent IDOR and unauthorized purges)

## References

- Domain reference: `references/3-02 Programming and Backend Development 1.md`, `references/37-DevOps, DDD, TDD, ADRs, Code.md`

