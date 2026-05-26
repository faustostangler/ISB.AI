# SPEC-025: Model Drift and Performance Monitoring Specification

**Linked ADR:** [ADR-025](../adr/ADR-025-model-drift-monitoring-evidently.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure / MLOps  

## 1. Overview & Objectives

This specification defines the validation criteria for calculating data and concept drift metrics using Evidently AI. It ensures that inference logging, drift metrics calculations, local report storage, and auto-retraining triggers operate correctly under simulated drift scenarios.

## 2. Invariants & Monitoring Rules

*   **Invariant 1**: The API presentation server (`FastAPI`) must never import or invoke `evidently`, `pandas`, or `sklearn` modules.
*   **Invariant 2**: All inference data written to the database logs must be anonymized (e.g. text inputs are hashed or represented by character/token counts and classification embeddings) to protect user privacy.
*   **Invariant 3**: The drift analysis job must compare a sliding window of production data (e.g., last 30 days) against the reference baseline training dataset.
*   **Invariant 4**: Breaching pre-configured statistical drift thresholds (e.g., Text Drift $p\text{-value} < 0.05$ or classification accuracy drop $> 10\%$) must raise a `ModelDriftAlertException` and dispatch a retraining trigger task.

## 3. Test Strategy Classification

*   **Unit Tests (Drift Detector Adapter)**:
    *   Scope: Mock the Evidently AI `Report` and database query interface.
    *   Assertions: Verify that query inputs are mapped to DataFrames correctly and that drift checks return the correct boolean flags depending on mock test results.
*   **Integration Tests (Drift Calculation Pipeline)**:
    *   Scope: Run the drift detection task using controlled test data partitions:
        *   **Control group**: A sample drawn from the baseline distribution. (Assert: Drift check passes, no alert).
        *   **Drifted group**: A sample representing drifted vocabularies and class predictions. (Assert: Drift check fails, `ModelDriftAlertException` is raised, auto-retraining task is queued).
*   **Performance / Isolation Validation**:
    *   Scope: Run static import analysis on the API serving package.
    *   Assertions: Verify that executing `import src.api` does not load `evidently` or `pandas` into the sys modules registry.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Inference Logging without VRAM Overhead
*   **Given**: An active API prediction endpoint receiving requests.
*   **When**: A user receives a note classification prediction.
*   **Then**: The serving code must write prediction stats (predicted class, confidence score, text length) to the local database asynchronously.
*   **And**: The VRAM consumption of the model sidecar remains unaffected.

### Scenario 2: Standard Weekly Drift Check (No Drift)
*   **Given**: A production data sample matching the reference training distribution.
*   **When**: The scheduled `DriftMonitoringJob` runs.
*   **Then**: Evidently AI must compute text and target drift metrics.
*   **And**: Verify all $p$-values are above the $0.05$ threshold.
*   **And**: Store the JSON metric summary in the local secure directory.
*   **And**: No retraining tasks are enqueued.

### Scenario 3: Drift Detected and Auto-Retraining Triggered
*   **Given**: A production dataset containing significant topic and classification distribution shift.
*   **When**: The scheduled `DriftMonitoringJob` runs.
*   **Then**: Evidently AI's Text Drift or Class Performance tests must fail.
*   **And**: Raise a drift alert warning log.
*   **And**: Dispatch a retraining task via `TaskQueuePort.enqueue("train_model_pipeline")`.
*   **And**: Save the generated HTML visualization report to the `/data/monitoring/` path.

## 5. Boundary Conditions & Exception Mapping

| Parameter / Metric | Condition | Expected Outcome |
|--------------------|-----------|------------------|
| Production Sample Size | $< 50$ records | Log warning "insufficient sample size for statistical tests" and abort calculation. |
| Missing Baseline Dataset | File not found in S3 | Raise `BaselineDatasetUnavailableException`, tag alert in Prometheus. |
| Database Connection | DB server timed out | Raise `MonitoringDatabaseException`, retry task up to 3 times. |

## 6. Observability & Telemetry Assertions

*   **Telemetry Metrics**:
    *   Expose gauge `isb_monitoring_drift_p_value` labeled by metric type (e.g., `text_drift`, `target_drift`).
    *   Expose counter `isb_monitoring_alerts_total` tracking triggered drift alerts.
*   **Audit Logs**:
    *   Log all successful drift calculations and their outcomes at `INFO` level.
    *   Log drift alert exceptions and retraining trigger failures at `ERROR` level.
