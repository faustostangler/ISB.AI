# ADR-006: Secure Non-Root Container and Multi-Role Runtime

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is deployed across multiple environments (local development, staging, production Kubernetes). Our services run different roles using the same container image (the API server, dramatiq background workers, and CLI/migration scripts). 

The initial container configuration ran as the `root` user by default. Under modern security baselines (such as the NSA/CISA Kubernetes Hardening Guide and K8s Pod Security Standards), running containers as `root` is highly discouraged because it enables potential container escapes, host system compromise, and privilege escalations.

Furthermore, we require system packages like `ffmpeg` to support media ingestion and transcribing pipelines (such as running audio transcription through OpenAI Whisper or utilizing `yt-dlp`). While a Distroless container image (`gcr.io/distroless/python3`) reduces attack surface, installing and maintaining complex system utilities like `ffmpeg` inside it introduces excessive engineering friction and is incompatible with our fast-iteration goals.

## Decision

We will modify the multi-stage `Dockerfile` to create a dedicated, non-privileged system user and group named `isb` (UID/GID `10001`). All application processes inside the container will run under this user.

Specific configurations to be implemented:
1. **System User Creation**:
   ```dockerfile
   RUN groupadd -g 10001 isb && \
       useradd -u 10001 -g isb -s /sbin/nologin -m isb
   ```
2. **Directory Permissions**:
   The `/app` directory and its children will have ownership transferred to user `isb` (`chown -R isb:isb /app`).
3. **Execution Context**:
   The `USER isb` directive will be declared at the end of the runtime stage to enforce non-root execution.
4. **Development Parity**:
   To address local file permission friction during development (where files created inside the container might be owned by UID `10001` on the host machine), developers can pass the current host UID/GID or leverage group options inside `docker-compose.yml` if editing local volume-mounted folders.

## Consequences

### Positive
* **Least Privilege Compliance**: Satisfies Kubernetes security posture guidelines (`runAsNonRoot: true`, `allowPrivilegeEscalation: false`).
* **Maintained Operational Ease**: Keeping a Debian-slim base stage allows simple installation of `ffmpeg` and debugging utilities (when executing shell commands during staging diagnostics).
* **Single Image Multi-Role (SSOT)**: The same secure image is used for API, worker, and CLI tasks.

### Negative
* **Local Permissions Management**: Host files mounted into the container might require group write permissions (`chmod -R g+w`) or user mapping depending on the developer's Linux host configuration.

## Alternatives Considered

### Alternative A: Keep default `root` user execution
* **Pros:** Simplest option; no permission conflicts with local mounts.
* **Cons:** Security vulnerability; fails K8s security compliance.
* **Why rejected:** Violates core DevSecOps principles and enterprise readiness guidelines.

### Alternative C: Distroless container deployment (`gcr.io/distroless/python3`)
* **Pros:** Smallest possible attack surface; no shell binaries.
* **Cons:** Extremely high friction to compile and run utilities like `ffmpeg`. Lack of shell impairs developer diagnostics and troubleshooting.
* **Why rejected:** The complexity overhead of compiling custom system binaries overrides the marginal security benefit, violating the KISS principle.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] Pod Security Standard compliance validated (`runAsNonRoot: true`)
- [x] Dependency management uses `uv` in builder stage
- [x] Multi-role single image configuration supported

## References

- Domain reference: `references/8-04 Containers, Docker, and Orchestration 1.md`
- Code link: [Dockerfile](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/ISB.AI/Dockerfile)
- Code link: [docker-compose.yml](file:///home/stangler/gamer_d/Fausto%20Stangler/Documentos/Python/ISB.AI/docker-compose.yml)
