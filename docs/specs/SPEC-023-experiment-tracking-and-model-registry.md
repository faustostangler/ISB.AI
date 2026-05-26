# SPEC-023: Experiment Tracking and Model Registry Specification

**Linked ADR:** [ADR-023](../adr/ADR-023-self-hosted-mlflow-model-registry.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure / MLOps  

## 1. Overview & Objectives

This specification defines the validation criteria for logging training runs and retrieving versioned checkpoints from our self-hosted MLflow Server. It ensures that metadata logging, model registry queries, and failover behaviors operate correctly under test constraints.

## 2. Invariants & Registry Rules

*   **Invariant 1**: Every model training, evaluation, or fine-tuning run must initialize an active MLflow run and log the execution environment's `git_commit_sha`.
*   **Invariant 2**: Model validation runs must log the primary evaluation metrics (`validation_macro_f1` and `validation_log_loss`) before initiating a registry request.
*   **Invariant 3**: The application adapter querying the model server must fetch checkpoints dynamically using tag-based lookups (e.g., `champion`, `production`) from the MLflow Model Registry.
*   **Invariant 4**: Configuration parameters (`MLFLOW_TRACKING_URI`, `MLFLOW_ARTIFACT_URI`) must be validated on startup using Pydantic Settings and reject invalid schema configurations immediately.

## 3. Test Strategy Classification

*   **Unit Tests (Training Pipelines)**:
    *   Scope: Mock the MLflow client library in training routines.
    *   Assertions: Verify that metrics and parameters are logged correctly and that runs are safely closed on failures.
*   **Integration Tests (Adapter)**:
    *   Scope: Test the `MlflowModelRegistryAdapter` against a mocked HTTP layer (or local test instance).
    *   Assertions:
        *   Successful retrieval of a model URI for a given registered name and active tag (e.g., `"champion"`).
        *   Graceful mapping of network connection failures to `ModelRegistryUnavailableException`.
        *   Correct handling of missing tags or unpromoted models, raising `ModelVersionNotFoundException`.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Clean Metric Logging and Run Capture
*   **Given**: An active model training pipeline with access to the MLflow client.
*   **When**: The training script completes cross-validation.
*   **Then**: It must invoke `log_metric()` for `validation_macro_f1` and `validation_log_loss`.
*   **And**: It must record the active `git_commit_sha` as a run tag.
*   **And**: The active run must be marked as `FINISHED` in the backend database.

### Scenario 2: Active Tag Model Query
*   **Given**: A registered model name `"NoteClassifier"` and active tag `"production"`.
*   **When**: The sidecar initialization service requests the model path.
*   **Then**: The adapter must call the MLflow registry API to fetch the active version marked with `"production"`.
*   **And**: Return the exact S3 or local path to the checkpoint directory.

### Scenario 3: Promotion with Missing / Invalid Target
*   **Given**: A model registry request for a model version that failed validation thresholds.
*   **When**: Attempting to tag that model run as `"champion"`.
*   **Then**: The system must block the update and raise `ModelPromotionBlocked`.

### Scenario 4: Registry Connection Offline (Graceful Degradation)
*   **Given**: The self-hosted MLflow server is offline.
*   **When**: The model serving sidecar starts up.
*   **Then**: The sidecar must fall back to loading the last cached local model directory if present.
*   **And**: Emit a high-priority warning log `MLflow registry unreachable, loading fallback model from local cache`.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Condition | Expected Outcome |
|-----------|-----------|------------------|
| `MLFLOW_TRACKING_URI` | Empty / Invalid Scheme | `ConfigurationError` (Pydantic abort) |
| Registry connection | Socket Timeout / 503 | `ModelRegistryUnavailableException` |
| Model Tag | Not found in registry | `ModelVersionNotFoundException` |
| Promotion metric | Macro F1 `< 0.85` | `ModelPromotionBlocked` |

## 6. Observability & Telemetry Assertions

*   **Telemetry Metrics**:
    *   Expose histogram `isb_mlflow_api_request_duration_seconds` labeled by API operation (e.g., `get_model`, `log_run`).
    *   Expose counter `isb_mlflow_api_errors_total` tracking network failures.
*   **Audit Logs**:
    *   Log all successful model promotions at `INFO` level.
    *   Log fallback local cache loadings at `WARN` level.
