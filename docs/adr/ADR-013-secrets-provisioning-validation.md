# ADR-013: GitOps-First Encrypted Secrets with SOPS/SealedSecrets and Pydantic-Settings Validation

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) requires access to sensitive credentials, including database connection strings, local model endpoint paths, API keys for cloud fallback LLM providers (Anthropic, OpenAI), and Sentry/observability endpoints. 

To maintain security, operational efficiency, and GitOps compliance:
1. **No Raw Secrets in Git**: No credentials can ever be committed in plaintext to version control.
2. **GitOps Declarative Deployment**: Infrastructure deployment manifests (managed via ArgoCD) must contain all configuration parameters, including secrets, to enable reproducible cluster states.
3. **Application Decoupling (KISS)**: The application code must not be coupled to vendor-specific secrets manager SDKs (such as HashiCorp Vault or AWS Secrets Manager APIs) which require complex network error handling, caching logic, and local development mocks.
4. **Fail-Fast Startup**: The application must validate all configuration properties immediately upon launch to prevent running in an unhealthy state (e.g. missing connection credentials).

## Decision

We will implement a GitOps-First secrets provisioning architecture where secrets are encrypted at rest in our git repository and injected into the container runtime as environment variables, with schema-level validation performed by Pydantic.

Specifically:
1. **Secret Encryption**: Production secrets will be encrypted using public-key cryptography via **Bitnami SealedSecrets** (or **Mozilla SOPS**). Encrypted files (`SealedSecret` resources) can be safely committed to our git repository.
2. **Infrastructure-Layer Decryption**: The Kubernetes cluster Sealed Secrets controller (or SOPS decryption process in GitOps pipelines) will decrypt the configurations and mount them as standard Kubernetes `Secret` resources.
3. **Environment Injection**: The secrets will be injected into the application container as environment variables at the pod declaration level.
4. **Local Development**: Developers will use a git-ignored `.env` file at the project root for local credential overrides.
5. **Fail-Fast Configuration Validation**: The application will load and validate all settings through a unified `Settings` class using `pydantic-settings` inside `src/config.py`. The bootstrapper will fail-fast and crash the container if any required configuration is missing or malformed.

## Consequences

### Positive
* **100% Declarative GitOps**: Every component required to restore the application state is version-controlled and auditable in Git.
* **KISS Codebase**: The Python backend requires zero knowledge of the encryption/decryption mechanisms. It simply reads standard environment variables, keeping the codebase free of complex secret manager APIs.
* **Fail-Fast Safety**: Invalid or missing configurations trigger validation failures at startup, preventing corrupt pods from entering the routing mesh.
* **Developer Parity**: Running the system locally via `docker-compose` or natively uses the exact same interface (environment variables via `.env`) as production.

### Negative
* **Encryption Key Management**: The private key to decrypt the secrets resides inside the Kubernetes cluster. If this key is lost, committed secrets must be re-encrypted. We will manage private keys securely via standard backup procedures.

### Neutral
* **Configuration Source**: All credentials are dynamically loaded from environment variables and can be overridden by a standard `.env` file during local development.

## Alternatives Considered

### Option A: Standard Kubernetes Secrets (Manual Provisioning)
* **Pros:** Standard, simple, no extra tooling required.
* **Cons:** Hard to manage declaratively. Secrets cannot be checked into Git, requiring manual setup in each cluster, which is error-prone and violates GitOps best practices.
* **Why rejected:** Breaks the automated, declarative GitOps flow.

### Option C: Runtime Secrets Manager API Integration (HashiCorp Vault / AWS Secrets Manager SDK)
* **Pros:** Highly secure; supports dynamic short-lived credentials and rotate-on-read mechanisms.
* **Cons:** Adds network calls during container startup. Requires importing SDK libraries, managing access tokens, handling network timeouts, and creating complex mocks for local development.
* **Why rejected:** Violates the KISS principle and introduces unnecessary runtime dependencies.

## Domain Model Impact

This decision affects only the startup configuration process. No Domain Entities or Value Objects are modified.

- **Port**: N/A (configuration loading runs at startup in the Composition Root, not in the core domain)
- **Adapter**: `PydanticBaseSettingsAdapter` (infrastructure — parses environment variables into typed configuration classes)
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No cloud SDK dependencies in Domain or Application layers
- [x] Fail-fast configuration validation enforced
- [x] 100% GitOps and version-control compatibility achieved
- [x] LGPD compliance: credentials and audit tokens secured

## References

- Related ADRs: [ADR-004: API Contract and Client Generation](ADR-004-api-contract-and-client-generation.md), [ADR-006: Secure Non-Root Container](ADR-006-secure-non-root-container.md)
- Domain reference: `references/27-11 Container-Infra Security 1.md`, `references/28-11 Container-Infra Security 2.md`
