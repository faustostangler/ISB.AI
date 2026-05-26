# SPEC-018: Event-Driven Caching and Invalidation Specification

**Linked ADR:** [ADR-018](../adr/ADR-018-cache-strategy-and-invalidation.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform / Caching  

## 1. Overview & Objectives

This specification defines the validation criteria for the `CachePort` interface, its concrete adapters (`InMemCacheAdapter` and `RedisCacheAdapter`), event bus subscription invalidation triggers, and lock-guarded cache reconstruction routines.

## 2. Bounded Context & Domain Invariants

* **Invariant 1**: Published Domain Events indicating structural state changes (e.g. `DocumentUpdatedEvent`, `DocumentDeletedEvent`) must cause the immediate deletion (`DEL`) of the associated cached key paths.
* **Invariant 2**: Cached keys must be prefixed with a unique, configured application prefix and salt (e.g. `isb:v1:`) to isolate keys on shared Redis nodes.
* **Invariant 3**: Cache reconstruction logic must acquire a lock via `LockPort` on a cache miss for any protected key. Concurrent queries for the same key must wait for the lock to release, then read the reconstructed value from the cache, preventing thundering herd hits to PostgreSQL.
* **Invariant 4**: In test environments, the in-memory cache adapter must allow isolated key manipulation without requiring a running Redis server instance.

## 3. Test Strategy Classification

* **Unit Tests (Cache Port & In-Memory)**:
  - Scope: Test use case caching patterns using the mock/in-memory adapter:
    - Verify cache-aside behaviour (miss -> DB fetch -> set cache).
    - Verify write-through caching updates the cache immediately.
    - Verify that publishing `DocumentUpdatedEvent` trigger deletes the specific cached document key.
* **Integration Tests (Redis & Concurrency)**:
  - Scope: Assert real Redis client interactions:
    - Test active connection pooling, timeouts, and fallback degradation if Redis is down.
    - Test concurrent execution of 10 threads missing the same key; assert that only 1 thread fetches from the mock database, while the remaining 9 read from cache after waiting.
    - Verify that Redis is operating with the `maxmemory` threshold and `allkeys-lfu`/`allkeys-lru` eviction parameters.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Event Bus Cache Invalidation
* **Given**: A document record with ID `doc_123` is cached in Redis under key `isb:v1:document:doc_123`.
* **When**: A user updates the document, causing the application to publish a `DocumentUpdatedEvent(document_id="doc_123")` to the local Event Bus.
* **Then**: The invalidation listener must receive the event and issue a deletion command.
* **And**: Subsequent queries for `isb:v1:document:doc_123` must return a cache miss.

### Scenario 2: Lock-Guarded Cache Stampede Prevention
* **Given**: A key `isb:v1:stats` is not present in the cache.
* **When**: 5 concurrent worker processes query the cache for `isb:v1:stats` simultaneously.
* **Then**: Exactly one worker must acquire the lock, execute the database read, and write the value back to the cache.
* **And**: The other 4 workers must block, wait for the lock release, and read the populated value directly from the cache without hitting the database.

### Scenario 3: Graceful Degradation on Cache Failure
* **Given**: The Redis server becomes unreachable or crashes during operation.
* **When**: A read/write operation is requested via the `CachePort`.
* **Then**: The adapter must catch the connection exception, log a warning, and fall back to querying/updating the database directly (graceful degradation).

## 5. BDD Test Case Matrix

| Parameter | Input | Expected Output |
| :--- | :--- | :--- |
| `key_salt` | `None` / empty string | Raises `ValueError: cache key salt must be configured` |
| `cache_miss_lock` | Lock timeout of 1s reached | Falls back to direct PostgreSQL query |
| `redis_down` | Connection refused | Logs warning, returns cache miss, calls DB adapter |

## 6. Observability & Telemetry Assertions

- **Prometheus Metrics**:
  - Assert that `cache_hits_total` and `cache_misses_total` counters are incremented on reads.
  - Assert that `cache_stampede_locks_acquired` is incremented when a reconstruction lock is held.
- **Sentry Integration**:
  - Assert that Redis connection drops are logged as warnings, not crash alerts.
