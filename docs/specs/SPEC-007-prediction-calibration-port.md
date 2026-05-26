# SPEC-007: Prediction Calibration Port Specification

**Linked ADR:** [ADR-007](../adr/ADR-007-prediction-calibration-port.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Knowledge Organization / Ingestion  

## 1. Overview & Objectives

This specification defines the validation criteria for prediction calibration. It guarantees that our ingestion pipeline handles statistical uncertainty predictably and routes ambiguous or out-of-domain inputs to manual triage.

## 2. Invariants & Domain Rules

* **Invariant 1**: A classification prediction set must be generated at the target confidence level ($1 - \alpha$, default $90\%$).
* **Invariant 2**: Documents yielding an empty prediction set must be flagged as *Out-of-Domain* and routed to the manual triage queue.
* **Invariant 3**: Documents yielding a prediction set with more than one element (size > 1) must be flagged as *Ambiguous* and routed to the manual triage queue.
* **Invariant 4**: Only prediction sets with exactly one element (size = 1) can be auto-assigned to that single category.

## 3. Test Strategy Classification

* **Unit Tests (Domain Routing)**:
  - Scope: Test the `CategorizeDocumentUseCase` using a mock `PredictionCalibratorPort`.
  - Assertions: Verify correct routing to database categories vs. triage queue based on set size.
* **Integration Tests (Calibration Adapter)**:
  - Scope: Test the `ConformalCalibratorAdapter` against synthetic calibration lists.
  - Assertions: Verify that $\hat{q}$ calculation matches Split Conformal Prediction mathematical formulas.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Clear Classification (Auto-Assignment)
* **Given**: A document with raw classification probabilities.
* **When**: The `PredictionCalibratorPort` is called with $1 - \alpha = 0.90$.
* **And**: The returned prediction set is `{"Work"}`.
* **Then**: The document category must be saved as `"Work"`.
* **And**: The status of the ingestion must be marked as `Completed`.

### Scenario 2: Ambiguous Classification (Triage Routing)
* **Given**: A document with overlapping semantic scores.
* **When**: The `PredictionCalibratorPort` returns `{"Research", "Work"}`.
* **Then**: The document must NOT be auto-assigned to either category.
* **And**: The document status must be marked as `NeedsReview`.
* **And**: It must be pushed to the `review_triage` repository.

### Scenario 3: Out-of-Domain Document (Triage Routing)
* **Given**: An out-of-domain document (e.g., gibberish or non-text note).
* **When**: The `PredictionCalibratorPort` returns an empty set `set()`.
* **Then**: The document must NOT be auto-assigned.
* **And**: The document status must be marked as `NeedsReview` with isolation metadata flag `OutOfDomain`.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| `confidence_level` | `1.5` or `-0.1` | `ValueError` |
| `raw_scores` | Empty dict | `ValueError` |
| Calibration size | `< 10` samples | `RuntimeError` (insufficient data for statistical bounds) |

## 6. Observability & Telemetry Assertions

* **Metrics**:
  - Expose counter `isb_classification_triage_total` labeled by trigger (`ambiguous` vs `out_of_domain`).
  - Expose histogram `isb_prediction_set_size` recording the cardinality distribution of prediction sets.
* **Audit Logs**:
  - Log all routed-to-triage events at `WARN` level with the document ID and returned prediction set.
