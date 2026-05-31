# ADR-024: Training Pipeline Orchestration via Pure Python and Task Queue Integration

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) periodically retrains and validates its machine learning classifiers (e.g. document categorization and metadata extraction). Managing these model training and evaluation runs requires executing structured steps: data loading, preprocessing, model cross-validation (Stratified K-Fold), probability calibration (Conformal Prediction), evaluation metrics collection, and model registry promotion.

We need a training pipeline orchestration strategy that satisfies:
1. **Zero Infrastructure Bloat (KISS)**: Developers run training locally on the RTX 2060 GPU without the overhead of heavy workflow servers (Prefect/Dagster).
2. **Unified Deployment**: Avoids separate task execution layers or server dependencies, keeping the application as a single deployable modular monolith.
3. **Execution Parity**: Local training is executed using lightweight CLI commands, while production triggers these tasks asynchronously using our existing out-of-process worker pool (`TaskQueuePort` via Dramatiq/Redis).
4. **Lineage Tracking**: Experiment metadata, hyperparameter logs, evaluation metrics (`validation_macro_f1`), and weight artifact paths must be tracked and versioned inside the self-hosted MLflow Server.

## Decision

We will orchestrate training workflows by structuring them as pure Python modules within the infrastructure layer (`src/mlops/pipelines/`). For execution and scheduling, we will:
1. **Local Dev/CLI**: Expose CLI scripts (e.g. `python -m src.mlops.pipelines.train`) to run and debug pipelines directly on the developer workspace.
2. **Production/Async Scheduling**: Wrap pipeline invocations inside background tasks scheduled via the existing `TaskQueuePort` (Dramatiq/Redis adapter).
3. **Experiment Tracking**: Enforce that pipeline steps register metadata, metrics, and artifact paths to the self-hosted MLflow server.

## Consequences

### Positive
* **Zero Infrastructure Overhead**: Reuses the existing Dramatiq/Redis background workers, eliminating the memory and CPU footprints of separate orchestration servers (Prefect/Dagster) on local and cloud instances.
* **Hermetic Unit Testing**: Pipeline modules are standard Python code that can be mocked, run, and unit-tested locally without running a global orchestrator database.
* **No Framework Lock-in**: Decouples pipeline logic from workflow orchestrator APIs (like Prefect flows or ZenML steps), keeping code standard and portable.

### Negative
* **No Pipeline DAG UI**: We do not get a graphical execution graph or specialized task-retry scheduler UI, although MLflow provides run metadata visualization.
* **Manual Step Caching**: Any step-level caching (e.g., bypassing data loading if already done) must be handled programmatically using local caching abstractions rather than native orchestrator caching.

### Neutral
* **Telemetry Platform**: Pipeline runs are tracked in MLflow for machine learning metrics/artifacts, and Prometheus/Grafana for execution metrics.

## Alternatives Considered

### Alternative B: ZenML Pipelines
* **Pros**: Enforces standardized pipeline structures; provides portability across cloud backends.
* **Cons**: Introduces high dependency weight; hard-couples code to ZenML step and pipeline decorators; raises testing friction.
* **Why rejected**: Violates the KISS principle for a monolithic codebase.

### Alternative C: Dedicated Self-Hosted Orchestrator (Prefect / Dagster)
* **Pros**: Superior DAG visualization, pipeline-level scheduling, and run metrics.
* **Cons**: Consumes substantial CPU and RAM; requires separate databases, ingress configurations, and maintenance.
* **Why rejected**: Premature optimization that wastes system resources on our local RTX 2060 workstation.

## Domain Model Impact

- **Port**: `TaskQueuePort` (application layer — async pipeline trigger), `ModelRegistryPort` (application layer — model catalog interface)
- **Adapters**:
  - `RedisDramatiqAdapter` (infrastructure — queue adapter)
  - `MlflowRegistryAdapter` (infrastructure — remote MLflow model registry)
- **Bounded Context**: MLOps Context (Supporting Domain)
- **Value Objects**: `ModelHyperparameters`, `PipelineRunId`, `ValidationMetrics`

## Cross-Context State Strategy

### 7a. Boundary Violations Check
No pipeline execution block will read or write directly to another bounded context's database. Data inputs are retrieved via application ports, and outputs are published as events.

### 7b. Consistency Model
- **Eventual Consistency (Async Events)**: Used to propagate pipeline status events (e.g., `ModelTrainedEvent`) across context boundaries.
- **Broker**: Redis/Dramatiq (in-process or Redis broker)
- **Delivery Guarantee**: At-least-once delivery.
- **Idempotency Strategy**: The receiving domain checks the registry and ignores duplicate events if the model version already exists.

### 7c. Failure Modes & Compensation (Saga Pattern)
- **Failure Mode**: Training succeeds but validation fails, or validation succeeds but registration fails.
- **Compensation**: The Saga Orchestrator catches the error, registers a failure in Sentry, flags the run status as `Failed` in the metadata database, and triggers cleanup of temporary artifacts.
- **Saga Style**: Orchestration (coordinated by a pipeline execution service).
- **Max Delay (SLA)**: 5 minutes.

## Compliance

- [x] Hexagonal Architecture layers respected (Pipelines live in infrastructure/mlops layer)
- [x] No pipeline orchestrator library imports in Domain layer
- [x] Tests strategy defined (hermetic unit tests run pipeline functions synchronously)
- [x] Observability plan included (pipeline executions emit telemetry through MLflow and Prometheus metrics)
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-002: Task Queue Abstraction via Hexagonal Port](./ADR-002-task-queue-abstraction.md), [ADR-023: Self-Hosted MLflow Server for Experiment Tracking and Model Registry](./ADR-023-self-hosted-mlflow-model-registry.md)
- Domain reference: `references/22-08 MLOps and LLMOps 2.md` (Orchestration comparisons)

