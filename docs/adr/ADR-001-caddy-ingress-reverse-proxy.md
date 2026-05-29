# ADR-001: Adopt Caddy as Ingress and Reverse Proxy

**Status:** Accepted
**Date:** 2026-05-26
**Decision Makers:** Lead Architect, High-Performance Implementer

## Context

The Intelligent Second Brain (ISB.AI) application is structured as a Modular Monolith with an API presentation layer (FastAPI) and background workers (Scraper). We require an ingress controller and reverse proxy to handle external HTTP/HTTPS traffic, manage TLS/SSL certificate lifecycle (Let's Encrypt), enforce secure headers, and route traffic to the presentation layer. 

The proxy tier must be robust, secure by default, and simple to configure, minimizing operational overhead while remaining flexible enough for potential dynamic routing requirements (e.g., routing custom ingestion endpoints).

## Decision

We will adopt Caddy as the edge ingress, reverse proxy, and API gateway because it provides automatic HTTPS certificate management out-of-the-box, has a highly readable and concise configuration syntax (Caddyfile), is built on a memory-safe language (Go), and exposes a REST API for dynamic JSON-based configuration updates without process reloads.

Additionally, our core Python FastAPI presentation container will execute using native multi-worker Uvicorn (`uvicorn --workers N` where `N = (2 * CPU_cores) + 1` in production) behind the Caddy proxy. This allows the application container to leverage multi-core host CPU resources under Python 3.13 without the operational footprint of Gunicorn, while Caddy load-balances external traffic to the Uvicorn socket.

## Consequences

### Positive
- **Automatic TLS**: Automated certificate acquisition and renewal (via Let's Encrypt / ZeroSSL) with zero custom scripts or Certbot cron jobs.
- **Developer Experience**: The `Caddyfile` syntax is incredibly clean, reducing setup and maintenance effort.
- **Dynamic Configuration**: Caddy exposes an administrative REST API (`localhost:2019`) to dynamically add or modify routes at runtime if needed.
- **Default Security**: Highly secure defaults, including TLS 1.3, secure cipher suites, and HTTP-to-HTTPS redirection.

### Negative
- **Throughput Overhead**: Written in Go, which is slightly slower and utilizes more memory than C-based Nginx under extreme concurrent workloads, though this is negligible for the expected load of ISB.AI.
- **Smaller Ecosystem**: A smaller library of third-party plugins and modules compared to Nginx's extensive module library.

### Neutral
- **Service Orchestration**: Local development uses a dedicated Caddy container in the `docker-compose.yml` to mimic production network routing.

## Alternatives Considered

### Alternative A: Bare FastAPI / Uvicorn Exposure
- **Pros:** Zero configuration; fewer containers.
- **Cons:** No automatic SSL management; vulnerable to denial-of-service/slow-loris attacks; poor static file handling.
- **Why rejected:** Exposing an application server directly to the internet violates web application security and reliability best practices.

### Alternative B: Nginx
- **Pros:** Industry standard; maximum throughput; very low resource footprint.
- **Cons:** Complex configuration syntax; requires Certbot/external tooling for Let's Encrypt; reloading config can drop/disturb active connections and requires shell access.
- **Why rejected:** Nginx introduces extra complexity for SSL certificate lifecycle management and lacks a native, easy-to-use JSON API for dynamic routing.

## Domain Model Impact

This ADR affects **infrastructure-only** components. No Domain Entities or Value Objects are modified.

- **Port**: N/A (Caddy operates outside the application boundary)
- **Adapter**: Caddy Ingress container configuration (`Caddyfile`, `docker-compose.yml`)
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected (ingress is kept strictly in the outer infrastructure tier)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined (validate Caddy configurations with `caddy validate`)
- [x] Observability plan included (caddy logging configured to forward logs to Grafana Loki)
- [x] LGPD/Security implications assessed (enforces modern TLS configurations and secure headers)

## References

- Related ADRs: [ADR-006: Secure Non-Root Container](ADR-006-secure-non-root-container.md), [ADR-014: Observability Architecture](ADR-014-observability-architecture.md)
- Domain reference: `references/2-01 Computing Fundamentals and Servers 2.md`
