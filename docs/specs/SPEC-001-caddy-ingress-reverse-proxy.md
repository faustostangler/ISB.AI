# SPEC-001: Caddy Ingress and Reverse Proxy Specification

**Linked ADR:** [ADR-001](../adr/ADR-001-caddy-ingress-reverse-proxy.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Infrastructure / Ingress

## 1. Overview & Objectives

This specification defines the validation criteria and structural routing rules for the Caddy ingress tier of the Intelligent Second Brain (ISB.AI). It serves as a contract ensuring that traffic is correctly routed, secure headers are applied, and TLS is terminated.

## 2. Bounded Context & Domain Invariants

Ingress is handled as an infrastructure adapter. While it is outside the pure business domain, the following invariants apply:
- **Value Object**: `AllowedHost`
  - Validation: Must match the allowed host domain (e.g. `localhost` or configured domain name).
- **Value Object**: `HttpResponseHeader`
  - Validation: Must contain secure defaults (X-Frame-Options, X-Content-Type-Options, etc.).

## 3. Test Strategy Classification

- **Static Infrastructure Validation**:
  - Scope: Verification of `Caddyfile` syntax, TLS settings, and proxy targets.
  - Command: `caddy validate --config infrastructure/caddy/Caddyfile`
- **Integration/E2E Ingress Tests**:
  - Scope: Spin up Caddy and FastAPI containers in a test network, check routing, header injection, and SSL status.
  - Dependencies: Local Docker instance.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Validate Caddy Configuration Syntax
- **Given**: A Caddyfile defined in the repository.
- **When**: Running the Caddy syntax validation tool.
- **Then**: The command must exit with code 0 (valid configuration).

### Scenario 2: Traffic Redirection and Proxy Routing
- **Given**: Caddy is running in front of the FastAPI app container.
- **When**: An HTTP request is sent to `http://localhost/`
- **Then**: Caddy must respond with a `308 Permanent Redirect` to `https://localhost/`.
- **When**: An HTTPS request is sent to `https://localhost/health`
- **Then**: Caddy must forward the request to the FastAPI app at `http://api:8000/health` and return the response.

### Scenario 3: Secure Headers Injection
- **Given**: A request is made to any endpoint via Caddy.
- **When**: The response is returned.
- **Then**: The headers must contain security defaults:
  - `X-Frame-Options: DENY`
  - `X-Content-Type-Options: nosniff`
  - `Strict-Transport-Security: max-age=31536000; includeSubDomains; preload`

### Scenario 4: Multi-Worker Process Verification
- **Given**: The FastAPI application container is running.
- **When**: Inspecting running processes inside the container.
- **Then**: There must be `N` independent Python processes running Uvicorn workers, where `N > 1` (scaled to system CPU capacity).

## 5. Boundary Conditions & Exception Mapping

| Input Host / Header | Value | Expected Outcome |
|---------------------|-------|------------------|
| Request Host        | `localhost` | Allowed, routed to FastAPI |
| Host Header         | `malicious.domain` | Rejected / 403 or ignored if not in allowed hosts |

## 6. Regression Anchors (For Bug Fixes Only)

*None at present (greenfield configuration).*

## 7. Observability & Telemetry Assertions

- **Caddy Access Logs**:
  - Access logs must be emitted in JSON format to standard output.
  - Log format must contain fields: `request.method`, `request.uri`, `resp_status`, `duration`.

