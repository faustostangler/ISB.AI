# ADR-020: Infrastructure as Code (IaC) Tooling via Pulumi and Python

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is deployed to public cloud infrastructure (AWS/GCP) and local test environments. We require a robust mechanism to provision clusters (EKS/GKE), database instances (PostgreSQL/CloudNativePG), caches (Valkey/Redis), and virtual networking topologies.

To support continuous delivery, we must define this infrastructure declaratively. We face a choice between standard declarative template engines (like Terraform HCL) and general-purpose programming frameworks (like Pulumi).

Our team consists primarily of Python software developers. Requiring the team to learn and maintain HCL configurations for complex multi-tier setups increases cognitive load and complicates our local testing and validation pipelines. We need a unified toolchain where infrastructure can be declared, validated, and tested using the same language and testing framework as our core application code (Python and `pytest`).

## Decision

We will adopt **Pulumi with Python** as our primary Infrastructure as Code (IaC) tool. All environments (staging, production, multi-cloud clusters) will be defined and provisioned using the Pulumi Python SDK.

Key details of this implementation include:
1. **Language Parity**: Infrastructure manifests will be written as clean Python code. Dependency management for IaC will be managed by `uv` and tracked in `pyproject.toml`.
2. **Infrastructure Unit Testing**: We will leverage Pulumi's mock testing framework to write automated unit tests in `pytest`. These tests will assert configuration correctness (e.g., verifying that S3/GCS buckets have public access blocked, security groups restrict SSH port 22, and tags are correctly populated) before provisioning runs in CI/CD.
3. **Environment Stacks**: We will use Pulumi Stacks to isolate environments (`isb-dev`, `isb-staging`, `isb-prod`).
4. **State Management**: State files will be stored in a centralized, secure cloud storage bucket (e.g., Amazon S3 or Google Cloud Storage) with locking enabled, or optionally via the hosted Pulumi Service for collaboration and audit trails.

## Consequences

### Positive
- **Unified Toolchain**: Developers use the same environment manager (`uv`), language (Python), and testing framework (`pytest`) for both infrastructure and backend logic.
- **Testability**: Enabling standard unit tests in pipelines before deployment reduces configuration errors (Change Failure Rate).
- **Expressiveness**: Creating dynamic setups, loops, and custom resource abstractions is straightforward and readable compared to verbose HCL blocks.

### Negative
- **Abstraction Danger**: Programming languages make it easy to write overly complex code. We must keep our infrastructure code clean, flat, and declarative (KISS principle), avoiding deep inheritance hierarchies or dynamic logic where simple parameterization suffices.
- **Smaller Module Registry**: Compared to Terraform's massive repository of pre-built HCL modules, Pulumi has fewer community-contributed high-level packages, though it supports importing Terraform providers natively.

### Neutral
- Secret management within Pulumi programs will leverage the encrypted secrets provider (integrated with KMS/vault or Pulumi's default cryptography) rather than storing plain text keys in state.

## Alternatives Considered

### Alternative A: Terraform with HCL
- **Pros**: Largest registry of modules, mature state model, industry default.
- **Cons**: Requires learning a proprietary language (HCL); writing unit tests for configuration invariants requires custom Go code (`terratest`) or third-party CLI tooling, breaking language parity.
- **Why rejected**: The benefits of developer experience (DX) and automated testing using Python/pytest outweigh the ecosystem advantage of HCL.

### Alternative C: Native Cloud Provider Manifests
- **Pros**: Direct provider support, no third-party state managers.
- **Cons**: High vendor lock-in; disjointed multi-cloud configuration files.
- **Why rejected**: Fails multi-cloud and portability requirements.

## Domain Model Impact

This decision affects only the provisioned cloud environment structure. No Domain Entities or Value Objects are modified.

- **Port**: N/A (infrastructure provisioning runs out-of-band relative to application execution)
- **Adapter**: Pulumi Python stacks (`__main__.py`, configuration schemas)
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected (IaC isolated in separate `infra/` or repository deployments)
- [x] No cloud SDK dependencies in Domain or Application layers
- [x] Tests strategy defined (pytest assertions for resource properties)
- [x] Observability plan included (telemetry resources mapped in stack)
- [x] LGPD/Security implications assessed (encryption-at-rest for state secrets)

## References

- Related ADRs: [ADR-013: Secrets Provisioning Validation](./ADR-013-secrets-provisioning-validation.md)
- Domain reference: `references/32-13 Cloud and Hardware for AI 1.md` (Pulumi best practices)
- Domain reference: `references/9-04 Containers, Docker, and Orchestration 2.md`
