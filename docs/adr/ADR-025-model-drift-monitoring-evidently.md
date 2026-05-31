# ADR-025: Model Drift and Performance Monitoring via Evidently AI

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) depends on machine learning classifiers to structure user documents and web scraps. Once deployed, these models face two critical degradation patterns:
1. **Data Drift**: Shifts in vocabulary, semantic topics, or document length in user inputs over time, rendering training-set feature distributions obsolete.
2. **Concept Drift**: Underlying shifts in real-world semantic categories (e.g. new types of work projects or personal activities) causing classification precision to decline.

To ensure long-term reliability and compliance, we must run automated statistical checks on production input/output logs, compare them against training baselines, and save report metrics locally. 

However, we face several constraints:
* **Dependency Overhead**: Comprehensive ML monitoring libraries (e.g., pandas, numpy, Evidently AI, Great Expectations) are heavy. Importing them into our FastAPI presentation server container increases image size, bloats startup times, and consumes precious RAM needed for serving local 4-bit models.
* **Privacy and Data Sovereignty**: Document details and classification outputs are private user information. Shipping these features, embeddings, or logs to third-party cloud monitoring systems (e.g., Arize, WhyLabs) violates multi-tenant security agreements.
* **Offline-First Developer Autonomy**: Monitoring pipelines must run entirely on local developer workstations and self-hosted environments without relying on active internet access.

## Decision

We will implement data and concept drift detection by integrating **Evidently AI** within our out-of-process scheduled pipelines.

Specific implementation details:
1. **Dependency Isolation (Multi-Role Monolith)**:
   Evidently, pandas, and scikit-learn will *never* be imported or initialized in the FastAPI API presentation server process. Instead, they will be loaded exclusively within the out-of-process **Background Worker** (Dramatiq/Redis container role) where pipeline tasks are executed.
2. **Database Logging**:
   The prediction serving layer will asynchronously write a lightweight, anonymized sample of incoming features (e.g. classification output, confidence score, text length, and optionally text embeddings) to an inference log table in our monolithic PostgreSQL database.
3. **Scheduled Monitoring Job**:
   A scheduled background task (`ScheduledDriftAnalysisJob`) will run weekly or monthly. It will load a pandas DataFrame of recent production logs, load the baseline dataset (stored in S3/MinIO), execute Evidently AI’s drift reports (e.g., Text Drift, Target Drift, and Classification Performance metrics), and output a structured JSON report.
4. **Local Sovereignty**:
   Evidently HTML dashboards and JSON metric outputs will be saved to our local secure storage volumes (e.g., in a dedicated `/data/monitoring/` directory).
5. **Auto-Retraining Trigger**:
   If statistical tests indicate a critical drift threshold has been breached (e.g. Wasserstein distance or PSI exceeds preconfigured limits), the script will publish a `ModelDriftDetected` domain event to trigger our training pipeline adapter (`ADR-024`).

## Consequences

### Positive
* **SOTA Statistical Analysis**: Out-of-the-box, industry-standard drift algorithms specifically optimized for text datasets, avoiding buggy custom statistics implementations.
* **API Serving Performance**: Serving API containers remain lean, lightweight, and free of pandas/scikit-learn/evidently dependencies.
* **100% Data Sovereignty**: All telemetry, raw samples, embeddings, and drift reports remain stored inside our local secure borders, maintaining compliance with multi-tenant privacy policies.
* **Autonomous/Offline Ready**: The entire evaluation, reporting, and dashboard generation run locally without external cloud dependencies.

### Negative
* **Database Sample Management**: Requires setting up table archiving/retention policies on the PostgreSQL database to prevent inference log tables from growing unbounded.
* **Background RAM Allocation**: The Dramatiq worker container must be sized with sufficient RAM limits to handle loading pandas DataFrames during drift analysis.

### Neutral
* **Report Formats**: The monitoring adapter generates both machine-readable JSON metrics for pipeline alerts and human-readable HTML dashboards for manual administrator review.

## Alternatives Considered

### Alternative A: Custom Mathematical Scripts (Prometheus decile tracking)
* **Pros**: Zero new library dependencies.
* **Cons**: Extremely difficult to correctly write complex text distribution and vocabulary drift calculators from scratch in pure Python; fails to provide semantic-level text evaluation.
* **Why rejected**: Custom math code is highly prone to statistical errors and does not match state-of-the-art standards.

### Alternative C: SaaS-based ML Observability (Arize AI, WhyLabs)
* **Pros**: Zero infrastructure maintenance, pre-built dashboards.
* **Cons**: Transmits raw text metadata, confidence, and embeddings outside our secure network; requires internet connection.
* **Why rejected**: Violates strict tenant privacy constraints and fails offline-first requirements.

## Domain Model Impact

- **Port**: `ModelDriftMonitoringPort` (application layer — abstract model monitoring and drift check interface)
- **Adapters**:
  - `EvidentlyDriftMonitoringAdapter` (infrastructure — scheduled pandas-based Evidently drift analyzer)
- **Bounded Context**: MLOps Context (Supporting Domain)
- **Value Objects**: `DriftReport` (validated JSON object containing drift metrics), `DriftThreshold` (configuration parameters)

## Compliance

- [x] Hexagonal Architecture layers respected (Evidently imports isolated inside infrastructure pipelines adapter)
- [x] No monitoring framework dependencies in Domain layer
- [x] Tests strategy defined
- [x] Observability plan included
- [x] LGPD/Security implications assessed (inference logging anonymizes inputs)

## References

- Related ADRs: [ADR-002: Task Queue Abstraction via Hexagonal Port](./ADR-002-task-queue-abstraction.md), [ADR-006: Secure Non-Root Container](./ADR-006-secure-non-root-container.md), [ADR-024: Training Pipeline Orchestration via Pure Python and Task Queue Integration](./ADR-024-pipeline-orchestration-dramatiq.md)
- Domain reference: `references/22-08 MLOps and LLMOps 2.md`

