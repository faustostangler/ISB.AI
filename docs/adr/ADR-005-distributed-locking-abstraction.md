# ADR-005: Distributed Locking Abstraction via Hexagonal Port

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) utilizes concurrent background workers to crawl web pages, ingest feeds, and extract document embeddings. 

If multiple workers attempt to process the same URL or document simultaneously, it results in:
1. Redundant network traffic and increased scraping costs.
2. Mismatch/conflicts in database updates.
3. Potential IP bans or rate-limiting from target websites.

To prevent this duplicate work, we require a concurrency-locking mechanism. However, implementing locking calls directly using a specific client library (e.g. `redis-py` or `redlock-py`) within our core use cases couples our domain to infrastructure details, violating Hexagonal guidelines and requiring a running Redis instance during simple unit tests. 

Additionally, utilizing database-level advisory locks (PostgreSQL) during slow network HTTP operations (like crawling a slow external site) is dangerous because it holds database connections open, leading to PostgreSQL connection pool starvation.

## Decision

We will define a `LockPort` interface in the application layer. Use cases requiring mutual exclusion (e.g., `ScrapeUrlUseCase`) will use this port via a context manager pattern.

We will write two adapters in the infrastructure layer:
1. **`InMemLockAdapter`**: Uses Python's standard `threading.Lock` (or an async lock equivalent) to perform local, broker-free locking for unit testing and local CLI tasks.
2. **`RedisLockAdapter`**: Uses Redis to manage distributed lock leases (via atomic `SET NX PX` operations and safe Lua-script releases) to coordinate locks across multiple containerized worker instances in production.

This ensures database connections are never held open during slow network crawls.

## Consequences

### Positive
- **Hexagonal Separation**: Domain logic is completely isolated from the locking mechanism.
- **Fast Testing**: Integration and unit tests can run locking scenarios in memory with no external dependencies.
- **DB Connection Protection**: Moving from database-level advisory locks to Redis distributed locks prevents connection pool starvation during slow, external I/O operations.
- **Graceful Fault Tolerance**: The Redis lock adapter will utilize TTLs (Time-To-Live) to automatically release locks if a worker container crashes or restarts.

### Negative
- **Lock Management Complexity**: Use cases must handle exceptions cleanly to ensure locks are always released (mitigated by using Python context managers).
- **Lease Timeout Tuning**: We must carefully tune lock TTLs depending on the type of ingestion job to ensure locks do not expire before a scrape completes.

### Neutral
- **Storage state**: Locking states (acquired, expired, released) are entirely ephemeral and are not persisted in the relational database.

## Alternatives Considered

### Alternative A: No Locking (Idempotency only)
- **Pros:** No extra complexity; fast database writes.
- **Cons:** High risk of duplicate scraping, redundant API bills, and target site rate-limiting.
- **Why rejected:** Violates resource efficiency and target site crawling ethics.

### Alternative B: PostgreSQL Advisory Locks
- **Pros:** Built into our primary database; auto-releases on transaction termination; very robust.
- **Cons:** Tying lock lifecycle to a database connection holds the connection open during slow network HTTP I/O, leading to connection starvation.
- **Why rejected:** Tying network wait time to database connection lifecycles violates database tuning guidelines.

## Domain Model Impact

- **Port**: `LockPort` (application layer — distributed locking interface)
- **Adapters**:
  - `InMemLockAdapter` (infrastructure — local threading-based lock)
  - `RedisLockAdapter` (infrastructure — Redis lease-based lock)
- **Bounded Context**: Shared Kernel
- **Value Objects**: `LockKey` (uniquely identifies the locked resource), `LockLeaseDuration` (specifies TTL)

## Compliance

- [x] Hexagonal Architecture layers respected (LockPort in application, concrete adapters in infrastructure)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (hermetic unit tests run using in-memory adapter)
- [x] Observability plan included (log lock acquisition failures and duration metrics)
- [x] LGPD/Security implications assessed

## References

- Domain reference: `references/7-03 Databases, Queues, and Cache 2.md`, `references/project_layout.md`

