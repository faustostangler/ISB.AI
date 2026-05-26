# SPEC-024: Training Pipeline Orchestration Specification

**Linked ADR:** [ADR-024](../adr/ADR-024-pipeline-orchestration-dramatiq.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure / MLOps  

## 1. Overview & Objectives

This specification defines the validation criteria, components, and test requirements for our Python-based training pipeline orchestration. It ensures that data loading, preprocessing, model cross-validation, evaluation, and registry promotion execute reliably and log all operations correctly to our self-hosted MLflow Server.

## 2. Invariants & Execution Rules

*   **Invariant 1**: Pipelines must be structured as standard Python modules containing functions or classes that can be executed independently.
*   **Invariant 2**: When executing a training run, the pipeline must wrap execution inside an active MLflow run, capturing parameters, metrics (`validation_macro_f1`, `validation_log_loss`), and the `git_commit_sha`.
*   **Invariant 3**: Asynchronous execution via the `TaskQueuePort` must use serialization-safe data transfer objects (DTOs) for task payloads (e.g., model name, dataset reference path).
*   **Invariant 4**: In the event of a training failure (e.g. out of memory on the GPU), the pipeline must cleanly terminate the active MLflow run, marking its status as `FAILED`.

## 3. Component Architecture

The training pipeline consists of the following components living in `src/mlops/`:

```
src/mlops/
├── domain/                  # Bounded context models (Pydantic models, core logic)
├── ports/                   # Interfaces (TaskQueuePort)
├── infrastructure/
│   ├── adapters/            # RedisDramatiqAdapter, MLflowAdapter
│   └── pipelines/           # Pure Python pipeline execution scripts
│       ├── train.py         # Entry point for training & cross-validation
│       └── evaluate.py      # Entry point for offline validation and calibration
```

## 4. Test Strategy Classification

*   **Unit Tests (Pipeline Steps)**:
    *   Scope: Test individual step functions (e.g., `preprocess_features`, `split_dataset`) using mock data.
    *   Assertions: Verify correct transformation logic, shape validation, and split ratios.
*   **Integration Tests (End-to-End CLI Pipeline)**:
    *   Scope: Execute the `train.py` script with mock dataset partitions and a mock MLflow server client.
    *   Assertions:
        *   The pipeline completes training successfully without crashing.
        *   All training parameters (e.g. `learning_rate`, `batch_size`) are logged to MLflow.
        *   Metrics (`validation_macro_f1`) are verified as uploaded.
        *   If the pipeline raises a training exception, the MLflow run is marked as `FAILED`.
*   **Async Queue Verification**:
    *   Scope: Verify pipeline integration with `TaskQueuePort`.
    *   Assertions: Enqueueing a pipeline task to `ImmediateTaskQueueAdapter` triggers execution synchronously and behaves identically to the direct script invocation.

## 5. Acceptance Criteria (Scenarios)

### Scenario 1: Successful Pipeline Execution and Tracking
*   **Given**: A mock dataset is available on disk and the MLflow client is configured.
*   **When**: The `run_training_pipeline()` function is called.
*   **Then**: It must start an MLflow run.
*   **And**: Perform Stratified K-Fold validation.
*   **And**: Log hyperparameter values and training dataset hashes.
*   **And**: Log evaluation metrics for each fold and final averages.
*   **And**: Register the model candidate weights.
*   **And**: Mark the run status as `FINISHED` in the MLflow database.

### Scenario 2: Pipeline Handles Out-of-Memory / Runtime Crashes Gracefully
*   **Given**: The training pipeline encounters an out-of-memory (OOM) error or hardware exception during execution.
*   **When**: The exception is thrown.
*   **Then**: The pipeline must catch the exception, log the traceback, and close the active MLflow run with status `FAILED`.
*   **And**: Properly release GPU memory.
*   **And**: Propagate the error so the task queue worker can mark the queue job as failed.

### Scenario 3: Task Queue Pipeline Triggers
*   **Given**: An asynchronous request to trigger training.
*   **When**: `TaskQueuePort.enqueue("train_model_pipeline", payload={"model_name": "NoteClassifier"})` is invoked.
*   **Then**: The background worker picks up the job.
*   **And**: Executes `run_training_pipeline()` within the worker process.

## 6. Boundary Conditions & Exception Mapping

| Parameter / Event | Condition | Expected Outcome |
|-------------------|-----------|------------------|
| GPU out-of-memory | VRAM limit reached | Release cache, tag run `FAILED`, raise `TrainingPipelineException` |
| Dataset Empty | No data loaded | Raise `ValueError`, abort pipeline execution |
| MLflow Server offline | Network timeout | Fallback to writing metrics to local disk cache, emit warning, complete training. |

## 7. Observability & Telemetry Assertions

*   **Telemetry Metrics**:
    *   Expose histogram `isb_training_pipeline_duration_seconds` tracking total execution times.
    *   Expose counter `isb_training_pipeline_failures_total` incremented on aborted training tasks.
*   **Audit Logs**:
    *   Log step execution timings at `INFO` level.
    *   Log MLflow connection fallback alerts at `WARN` level.
