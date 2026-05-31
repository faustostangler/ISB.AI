# ADR-019: Kubernetes Deployment, Self-Healing, and Resource Rightsizing

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is deployed to production clusters running Kubernetes. We need a standardized deployment topology that ensures our components (the API Presentation and the Background Worker) are robust, self-healing, and operate within clear capacity guardrails.

Without explicit resource requests and limits, Kubernetes workloads can lead to noisy neighbor scenarios, memory exhaustion (`OOMKilled`) of adjacent workloads, and inefficient node utilization (FinOps waste). Furthermore, if a process encounters a deadlock, connection pool exhaustion, or fails during startup due to database availability delays, we must have automated recovery loops to maintain service availability.

We require a configuration policy that guarantees self-healing and resource rightsizing while keeping the operational overhead to a minimum, aligning with our Modular Monolith topology.

## Decision

We will configure our Kubernetes deployment manifests and Helm values with:
1. **Resource Rightsizing**: Every container will explicitly declare `requests` and `limits` for CPU and Memory, ensuring the Quality of Service (QoS) class is set to `Burstable` or `Guaranteed` depending on environment priority.
2. **Three-Tiered Probing**: The API Presentation component will expose dedicated endpoints and be monitored using:
   - **Startup Probe**: A HTTP-get check targeting `/health/startup` with a high failure threshold to allow slow application bootstrap andComposition Root dependency injection wiring.
   - **Readiness Probe**: A HTTP-get check targeting `/health/ready` that verifies downstream adapter connectivity (Postgres and Redis).
   - **Liveness Probe**: A HTTP-get check targeting `/health/live` confirming process responsiveness.
3. **Horizontal Pod Autoscaling (HPA)**: The API tier will scale dynamically based on a target CPU utilization of 75%.
4. **Single-Image Execution**: Both the API and Worker roles will execute using the same container image, invoking their respective roles via container start arguments, matching the Single Source of Truth image pattern.

## Consequences

### Positive
- **Deterministic Reliability**: Probes automate container restarts during deadlock scenarios without operator intervention.
- **FinOps Optimization**: Rightsized boundaries prevent budget overrun and ensure cluster nodes are efficiently bin-packed.
- **Startup Protection**: The startup probe prevents the liveness probe from prematurely killing the pod during heavy framework initializations.

### Negative
- **Manifest Overhead**: Requires writing and maintaining more detailed YAML configurations (probes, limits, HPA rules) in our Helm/K8s setup.
- **Probe Load**: The readiness probe places regular check queries on database and caching adapters, which must be lightweight to prevent self-denial-of-service.

### Neutral
- The health check logic will be embedded within the `Presentation` layer, keeping the domain clean of HTTP route and connection check concerns.

## Alternatives Considered

### Alternative A: Minimal Static Deployment
- **Pros**: Simplest possible manifests; no resource tuning.
- **Cons**: High risk of silent lockups and cluster node instability.
- **Why rejected**: Violates basic operational standards for high-availability production workloads.

### Alternative C: Microservices Split and Kyverno Policy-as-Code
- **Pros**: Complete cryptographic isolation, fine-grained access control, automated policy validation.
- **Cons**: High engineering friction, service mesh complexity, sidecar overhead, and violates the KISS principle for modular monolithic deployments.
- **Why rejected**: Introduces excessive cognitive load and infrastructure cost before the business scale demands it.

## Domain Model Impact

This decision affects only the deployment environment configuration. No Domain Entities or Value Objects are modified.

- **Port**: N/A (Kubernetes health checks and scheduling operate at the orchestration/container tier)
- **Adapter**: `Deployment` resources, `StartupProbe`/`LivenessProbe`/`ReadinessProbe` configurations
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected (health checks implemented in Presentation layer)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined
- [x] Observability plan included
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-006: Secure Non-Root Container](./ADR-006-secure-non-root-container.md)
- Domain reference: `references/8-04 Containers, Docker, and Orchestration 1.md`
- Domain reference: `references/9-04 Containers, Docker, and Orchestration 2.md`
