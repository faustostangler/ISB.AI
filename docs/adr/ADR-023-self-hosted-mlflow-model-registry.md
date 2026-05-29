# ADR-023: Self-Hosted MLflow Server for Experiment Tracking and Model Registry

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) evaluates and promotes machine learning models (such as document classifiers, key phrase extractors, and custom representations). Managing this model lifecycle requires structured tracking of training metrics (e.g., Stratified K-Fold cross-validation results like `validation_macro_f1` and `validation_log_loss`), hyperparameter configurations, and model checkpoints.

We need a tracking and registry system that satisfies:
1. **Data Sovereignty and Privacy (KISS)**: The application processes sensitive personal and workplace documents. Shipping raw metadata hooks, extraction statistics, or document examples to external third-party cloud servers violates strict privacy limits.
2. **Offline-First Developer Autonomy**: Developers must be able to train and run experiments locally without requiring an internet connection.
3. **Operational Simplicity**: The tooling must integrate cleanly into our modular monolith deployment model without introducing heavy external orchestration dependencies or complex deployment topologies.
4. **Seamless Model Lifecycle (SOTA)**: The system must support promoting validated model versions dynamically to our model serving sidecars (SGLang/vLLM) in both development (NVIDIA RTX 2060 GPU with 4-bit AWQ compression) and cloud production (FP8 precision).

## Decision

We will deploy and utilize a **Self-Hosted MLflow Server** as our centralized experiment tracking and model registry platform.

Specific implementation details:
1. **Infrastructure & Deployment**:
   - The MLflow tracking server will run as a lightweight container co-located with our application services.
   - **Backend Metadata Database**: Supported by SQLite in local development and the monolithic PostgreSQL database cluster (running in a dedicated schemaspace/database `mlflow`) in production environments.
   - **Artifact Storage**: Supported by local volume directories in development and an S3-compatible cloud storage bucket (e.g., AWS S3 or MinIO) in production.
2. **API Tracking Integration**:
   - Training and validation scripts will log experiment metadata using the standard `mlflow` Python SDK.
   - Standard logged attributes must include the `GIT_SHA` for repeatability, dataset partition hashes, and target evaluation scores (`validation_macro_f1`, `validation_log_loss`).
3. **Registry Lifecycle Management**:
   - The MLflow Model Registry will act as the single source of truth for model weights.
   - Our deployment automation and model serving sidecar adapters will query the MLflow registry API to fetch approved checkpoints dynamically (by tags like `production` or `champion`), enabling zero-downtime model hot-swapping.

## Consequences

### Positive
* **Complete Data Sovereignty**: 100% of model statistics, run parameters, and metadata remain within our secure network boundaries.
* **Offline Autonomy**: Full tracking, comparison, and local registry capabilities are available offline.
* **Low Orchestration Overhead**: Avoids complex external pipeline orchestration wrappers, adhering to a lightweight monolithic deployment strategy.
* **SOTA Portability**: Easily promotes models from local INT4 configurations to production FP8 endpoints using tags and version promotion stages via the registry API.

### Negative
* **Service Maintenance**: The team must manage the MLflow container, PostgreSQL schema allocations, and S3 bucket IAM/access permissions.
* **No Built-in Pipeline Lineage**: MLflow tracks experiments but does not enforce DAG execution steps. We will structure our training pipelines using clean, modular, and unit-tested Python scripts.

### Neutral
* **Registry Storage**: SQLite is used for local registry metadata and PostgreSQL is used in staging/production, requiring no adapter code changes due to MLflow's abstraction.

## Alternatives Considered

### Alternative B: ZenML Pipelines with MLflow Adapter
* **Pros**: Enforces strict pipeline DAG orchestration and data lineage.
* **Cons**: Introduces high orchestration complexity and operational friction for a single-deployable modular monolith.
* **Why rejected**: Violates the KISS principle by adding unnecessary layers of abstraction.

### Alternative C: SaaS-hosted Weights & Biases (W&B)
* **Pros**: Superior out-of-the-box visualizations; zero operational maintenance.
* **Cons**: Shakes developer autonomy during offline work; requires sending metadata statistics to third-party endpoints.
* **Why rejected**: Violates security guidelines and network isolation requirements.

## Domain Model Impact

- **Port**: `ModelRegistryPort` (application layer — model registry query and promotion interface)
- **Adapters**:
  - `MlflowRegistryAdapter` (infrastructure — remote/local MLflow server API client)
- **Bounded Context**: MLOps Context (Supporting Domain)
- **Value Objects**: `ModelVersion` (validated version string), `ArtifactPath` (validated storage path)

## Compliance

- [x] Hexagonal layers respected (MLflow SDK calls isolated inside infrastructure/training scripts)
- [x] No MLflow references or imports in the core Domain layer
- [x] Database configuration validation centralized via Pydantic settings
- [x] Parquet/artifact storage matches PyArrow/Feather guidelines

## References

- Related ADRs: [ADR-009: Out-of-Process Model Serving](./ADR-009-out-of-process-model-serving.md), [ADR-022: Model Validation Partitioning and Accuracy Metrics](./ADR-022-model-validation-and-evaluation.md)
- Domain reference: `references/21-08 MLOps and LLMOps 1.md` (Structured LLM outputs and MLOps tools)
- Domain reference: `references/22-08 MLOps and LLMOps 2.md` (LLMOps monitoring and registry)

