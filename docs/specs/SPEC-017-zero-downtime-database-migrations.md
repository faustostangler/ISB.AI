# SPEC-017: Zero-Downtime Database Migrations Specification

**Linked ADR:** [ADR-017](../adr/ADR-017-zero-downtime-database-migrations.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform / Persistence  

## 1. Overview & Objectives

This specification defines the validation criteria for database schema migrations, lock timeout enforcement, parallel-writing logic verification, and background data backfill job reliability. It guarantees that database changes can be deployed concurrently with live application traffic without causing outages.

## 2. Bounded Context & Domain Invariants

* **Invariant 1**: Every migration transaction block must invoke `SET lock_timeout = '2s';` immediately upon acquiring a connection session.
* **Invariant 2**: Index creation on tables containing active customer records must use the `CONCURRENTLY` SQL flag and execute outside standard transaction blocks.
* **Invariant 3**: New columns containing `NOT NULL` logic must be added as nullable in the Expand phase, backfilled, and enforced via check constraints with the `NOT VALID` flag before conversion.
* **Invariant 4**: Data backfill jobs must execute in parameterized batches (e.g. limit of 1000 records per loop) and include configurable sleep delays (throttling) to allow database replication lag to settle.

## 3. Test Strategy Classification

* **Unit Tests (Migration Isolation & Config)**:
  - Scope: Test migration setup configuration blocks in python (Alembic configuration):
    - Assert that the migration scripts have lock timeouts defined.
    - Assert that concurrent index operations are set to run with transactional blocks disabled (`with_op` or autocommit settings in Alembic).
* **Integration Tests (Parallel Runs & Backfills)**:
  - Scope: Assert schema state changes against a real test database container:
    - Verify that old database queries continue to function successfully when the "Expand" migration phase is applied.
    - Verify that backfill scripts update precisely the target records and stop when 0 rows are affected.
    - Verify that check constraints defined as `NOT VALID` are verified asynchronously without lock timeouts.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Safe Concurrent Index Creation
* **Given**: An active PostgreSQL database containing a high-throughput table.
* **When**: A migration containing a new index definition is executed.
* **Then**: The migration script must disable standard transaction pooling and issue `CREATE INDEX CONCURRENTLY`.
* **And**: Inserting new records during the index build must execute without blocking or timing out.

### Scenario 2: Throttled Batch Backfill Processing
* **Given**: A table with 5,000 records where a new column `new_field` is initialized to `NULL`.
* **When**: The backfill job is launched with a batch size of `1000` and sleep of `0.1` seconds.
* **Then**: The job must execute exactly 5 database updates.
* **And**: The backfill job must exit with code `0` once all matching rows have been set.

### Scenario 3: NOT VALID Constraint Validation
* **Given**: A table with backfilled values in `new_field`.
* **When**: The constraint validation migration is applied.
* **Then**: The constraint must first be added as `NOT VALID` to avoid lock escalation.
* **And**: The validation command `VALIDATE CONSTRAINT` must verify all rows successfully.

## 5. BDD Test Case Matrix

| Parameter | Input | Expected Output |
| :--- | :--- | :--- |
| `migration_timeout` | No setting configured | MIGRATION_TIMEOUT_ERROR / Fail validation |
| `lock_timeout` | `SET lock_timeout = '2s'` | Connection sessions close if lock not acquired within 2000ms |
| `backfill_batch` | batch_size = `-10` | Raises `ValueError: batch size must be positive` |
| `backfill_run` | 0 matching rows left | Exits immediately (returns `0` records modified) |

## 6. Observability & Telemetry Assertions

- **Prometheus Metrics**:
  - Assert that `database_migration_duration_seconds` is recorded for each phase.
  - Assert that `database_backfill_processed_rows` records the throughput of data migration.
- **Sentry Integration**:
  - Assert that migration transaction timeouts (`LockNotAvailable` exceptions) are caught and reported with critical severity.
