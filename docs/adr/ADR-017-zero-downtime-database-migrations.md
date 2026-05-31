# ADR-017: Zero-Downtime Database Migrations and Schema Evolution

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is structured as a Modular Monolith. In production (GKE/Kubernetes), we will run multiple instances of the application container behind our Ingress Proxy, serving live traffic. 

Evolving the database schema (adding columns, constraints, or indexes, renaming columns, or deleting tables) using standard single-phase database migration tools (e.g. Alembic auto-generated upgrade scripts run synchronously on deployment boot) presents severe operational risks:
1. **Blocking Locks**: Commands like `ALTER TABLE ADD COLUMN NOT NULL` or standard index creation acquire exclusive table locks (`ACCESS EXCLUSIVE`), blocking active inserts/updates/deletes. In high-concurrency systems, this leads to connection pool starvation and application timeouts.
2. **Backward Incompatibility**: Running new database structures (such as renamed columns) before the previous version of application container nodes is completely terminated breaks the active deployment, causing failures during rolling updates.
3. **Rollback Friction**: If a migration fails mid-deployment, rolling back structural tables containing live production data can cause corruption or loss of transactions.

We need a structured protocol that guarantees database schema transitions can be executed with zero downtime, full backward compatibility, and robust rollback options.

## Decision

We will adopt the **Expand-Contract (Parallel Run)** database schema migration pattern for all schema modifications. Every database change must be split into distinct, backward-compatible stages, separating structural modifications from data transformations.

Specifically:
1. **Multi-Phase Pipeline**:
   - **Phase 1: Expand**: All structural elements are added as optional, nullable, or concurrently-built. For example, new columns are added as nullable; indexes are built using `CONCURRENTLY`.
   - **Phase 2: Migrate (Parallel Writes & Backfill)**: The application code is deployed to write to both the old and new structures. A throttled background worker (Backfill Job) updates existing rows in batches.
   - **Phase 3: Contract**: The application code is updated to read and write exclusively using the new schema. The old structural columns, tables, or obsolete constraints are dropped in a separate database migration.
2. **Constraint Validation**: Non-nullable columns must be added as nullable first, populated, and then protected using a check constraint added `NOT VALID` and validated asynchronously (`VALIDATE CONSTRAINT`) to prevent long-running table locks.
3. **Lock Protections**: Every migration transaction must set a strict `lock_timeout` (maximum 2 seconds) to prevent blocked migration queries from queuing transactions.

## Consequences

### Positive
- **Zero-Downtime Releases**: Rolling updates can occur continuously without locking transaction tables.
- **Safe Rollbacks**: If a bug is detected in new code, the application can safely be rolled back because the database remains backward-compatible with the previous container version during the parallel run.
- **Connection Health**: Prevents PostgreSQL connection pool starvation by avoiding table lock escalation.

### Negative
- **PR Overhead**: Simple changes (like renaming a column) now require multiple releases, separate pull requests, and additional developer planning.
- **Temporarily Nullable Schema**: Core fields might temporarily be declared nullable at the database level during the expansion phase, relying on application use cases to enforce logic rules.

### Neutral
- **Increased Tracking**: Database migration scripts must be named and ordered to clearly identify which phase (Expand/Contract) they correspond to.

## Alternatives Considered

### Alternative A: Single-Phase Migrations (Standard Alembic)
- **Pros:** Fast implementation; single PR; simple code.
- **Cons:** Triggers exclusive locks on high-write tables, causing application downtime during deployments.
- **Why rejected:** Violates our strict MTTR and high-performance system availability requirements.

### Alternative B: Online Schema Migration Tools (e.g. pg-osc)
- **Pros:** Automates shadow table copying and write mirroring.
- **Cons:** Adds operational tool complexity; triggers degrade database write throughput.
- **Why rejected:** Exceeds the complexity threshold needed for our Modular Monolith layout (violates the KISS principle).

## Domain Model Impact

This decision affects only the persistence schema evolution. No Domain Entities or Value Objects are modified.

- **Port**: N/A (database migrations are executed out-of-process via CLI during the deployment bootstrap)
- **Adapter**: Alembic migration scripts (`alembic.ini`, `env.py`), PostgreSQL database schema
- **Bounded Context**: Platform / Shared Kernel (cross-cutting persistence layer)

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (migration script testing and backfill verification)
- [x] Observability plan included (track backfill progress and database lock query times)
- [x] LGPD/Security implications assessed (ensures audit fields exist during parallel writes)

## References

- Related ADRs: [ADR-005 Distributed Locking](ADR-005-distributed-locking-abstraction.md)
- Domain reference: `references/zero_downtime_migrations.md`, `references/6-03 Databases, Queues, and Cache 1.md`
