# ADR-018: Event-Driven Caching and Invalidation Strategy via Redis and Event Bus

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) requires low-latency read access to frequently queried domain aggregates, including parsed document metadata, segment transcriptions, and user authorization bounds. 

Querying PostgreSQL directly on every API request or background scraping task execution can create database bottlenecks. However, introducing caching introduces the risk of cache-drift (stale data), where updates to the primary PostgreSQL data are not reflected in the Redis cache.

Key forces at play:
1. **Consistency**: Cached reads must reflect database modifications as close to real-time as possible.
2. **Hexagonal Cleanliness**: The caching logic must be decoupled from application use cases to keep core business logic clean and easily testable.
3. **Thundering Herd (Stampede)**: If a highly popular cache key expires or is deleted, multiple concurrent requests must not hit the database simultaneously to rebuild it.
4. **Memory Hygiene**: Redis memory must be bounded safely to prevent out-of-memory (OOM) crashes of the container runtime.

## Decision

We will implement an **Event-Driven Write-Through / Cache-Aside** caching architecture utilizing Redis for volatile object storage, with invalidation driven by domain events published to our local Event Bus.

Specifically:
1. **CachePort & Adapters**:
   - We will define a `CachePort` interface in the application layer.
   - We will write an **`InMemCacheAdapter`** (using a simple local dictionary) for broker-free unit testing.
   - We will write a **`RedisCacheAdapter`** for production, utilizing the `phpredis` equivalent for Python (`redis-py` client) with persistent connections.
2. **Event-Driven Invalidation**:
   - When a state-changing use case modifies database structures, it will publish a corresponding domain event (e.g. `DocumentUpdatedEvent`, `DocumentDeletedEvent`) to the local Event Bus.
   - A dedicated cache invalidation subscriber will listen for these events and issue atomic delete (`DEL`) commands to Redis for all keys mapping to the modified entity ID.
3. **Cache Reconstruction with Locking**:
   - To prevent cache stampedes on misses, the reconstruction logic will acquire a short-lived lock via `LockPort` (ADR-005). The first thread/instance to acquire the lock will fetch from PostgreSQL and repopulate Redis, while concurrent requests wait and re-read the cache.
4. **Redis Cache-Only Tuning**:
   - Production Redis servers will be configured strictly as ephemeral caches: persistence disabled (`save ""`, `appendonly no`), `maxmemory` limit explicitly defined, `maxmemory-policy` set to `allkeys-lfu` (Least Frequently Used) or `allkeys-lru`, and `activedefrag yes` enabled.

## Consequences

### Positive
- **High Consistency**: Cached entities are invalidated instantly when updates happen, eliminating stale reads.
- **No Domain Pollution**: Caching details, connection strings, and invalidation subscribers are isolated in the infrastructure layer.
- **Stability**: Bounded memory limits and eviction policies protect Redis and host nodes from crash loops.
- **Stampede Protection**: Lock-guarded cache reconstruction protects PostgreSQL from concurrency spikes.

### Negative
- **Event Bus Coupling**: The reliability of cache consistency relies on the successful generation and publication of domain events by all modifying use cases.

## Alternatives Considered

### Alternative A: Cache-Aside with Pure TTL Invalidation (Lazy Expiry)
- **Pros:** Extremely simple; no event handlers needed.
- **Cons:** Stale data persists until the TTL expires; prone to thundering herds when hot keys expire.
- **Why rejected:** Data consistency requirements for user document metadata are too strict to wait for time-based expiry.

### Alternative B: Database Triggers / CDC (Change Data Capture) Invalidation
- **Pros:** Fully decoupled from application use cases.
- **Cons:** Relies on database-layer triggers or external pipeline workers, which are difficult to test and maintain.
- **Why rejected:** Overengineered and couples infrastructure keys directly to DB table columns instead of domain entities.

## Compliance

- [x] Hexagonal Architecture layers respected (CachePort in application, RedisCacheAdapter in infrastructure)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (unit tests verify event bus triggers cache invalidation)
- [x] Observability plan included (track cache hit/miss ratio, connection pools, and evictions)
- [x] LGPD/Security implications assessed (ensure cached items do not contain decrypted PII keys)

## References

- Related ADRs: [ADR-005 Distributed Locking](ADR-005-distributed-locking-abstraction.md), [ADR-017 Database Migrations](ADR-017-zero-downtime-database-migrations.md)
- Domain reference: `references/7-03 Databases, Queues, and Cache 2.md`
