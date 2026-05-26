# SPEC-006: Secure Non-Root Container and Multi-Role Runtime Specification

**Linked ADR:** [ADR-006](../adr/ADR-006-secure-non-root-container.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Operations / Infrastructure  

## 1. Overview & Objectives

This specification details the automated validation and verification tests required to ensure the containerized environment complies with security restrictions while retaining its multi-role execution capability (API, background worker, CLI ingestion tools).

## 2. Invariants & Security Guarantees

* **Invariant 1**: The container process must not execute as `root`.
* **Invariant 2**: The container must execute with user ID `10001` and group ID `10001`.
* **Invariant 3**: The `/app` directory must be owned and writable by user `isb` (`10001:10001`) to support temporary application runtime caches.
* **Invariant 4**: Necessary third-party system libraries (specifically `ffmpeg`) must be installed and executable under the `isb` user context.

## 3. Test Strategy Classification

* **Static Analysis**:
  - Run `hadolint` on the `Dockerfile` to detect security misconfigurations (e.g., lack of pinned versions, missing `USER` directive).
* **Integration Verification**:
  - Spawn the built image locally using a secure runtime profile and verify identity constraints, package availability, and directory write permissions.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Identity Constraint Verification
* **Given**: A successfully built `isb:latest` Docker image.
* **When**: Running the container with command `id -u` and `id -g`.
* **Then**: The output for user ID must be `10001`.
* **And**: The output for group ID must be `10001`.

### Scenario 2: System Library Validation
* **Given**: A successfully built `isb:latest` Docker image.
* **When**: Executing the command `ffmpeg -version` inside the container.
* **Then**: The exit code must be `0` and print valid executable version metadata.

### Scenario 3: Writable Application Directory
* **Given**: A successfully built `isb:latest` Docker image.
* **When**: Creating a dummy file under `/app/src/test_write.tmp` or inside `/app` cache paths as user `isb`.
* **Then**: The file must be created successfully without permission denied errors.
* **And**: Cleaning up the test file must succeed.

### Scenario 4: Hadolint Security Validation
* **Given**: The codebase [Dockerfile](../../Dockerfile).
* **When**: Running `hadolint Dockerfile`.
* **Then**: There should be no severity warning or error violations.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| User Name | `root` | Execution rejected in production |
| Directory | `/root` | Writable check fails (no-access) |
| System binaries | `apt-get` | Execution disabled for non-root users post-build |

## 6. Observability & Telemetry Assertions

* **Startup Identity Ingress**:
  - On startup, the main entry point `isb.main` must log the current running UID and role:
    `"Starting ISB.AI system component [role=...] under UID 10001"` at `INFO` level.
