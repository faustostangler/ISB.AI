# SPEC-022: Model Validation Partitioning and Accuracy Metrics Specification

**Linked ADR:** [ADR-022](../adr/ADR-022-model-validation-and-evaluation.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Knowledge Organization / Ingestion  

## 1. Overview & Objectives

This specification defines the validation checks for our machine learning model training and evaluation pipelines. It ensures that data splits are statistically sound, free from temporal leakage, and that model promotion gates enforce quality thresholds for F1-Score and Log Loss.

## 2. Bounded Context & Domain Invariants

- **Component**: Dataset Partitioning
  - Invariant 1: For any Temporal Split at time $T$, every sample in the training partition must have a timestamp $t_i < T$, and every sample in the validation partition must have a timestamp $t_j \ge T$.
  - Invariant 2: For any Stratified K-Fold partition, the class ratio $p_c$ in each fold $k$ must be within $\pm 2\%$ of the global class ratio $P_c$ for all classes $c$.
- **Component**: Promotion Gate
  - Invariant 3: A model revision can only be promoted to production if it satisfies:
    - $\text{Macro F1-Score} \ge 0.85$
    - $\text{Log Loss} \le 0.35$

## 3. Test Strategy Classification

- **Unit Tests (Data Splitters)**:
  - Scope: Test dataset split utilities using synthetic document data.
  - Assertions: Verify chronological order enforcement and class distribution balance.
- **Integration Tests (Promotion Gate)**:
  - Scope: Test the model registration workflow with mock evaluations.
  - Assertions: Verify that registration fails and rolls back if metric thresholds are not met.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Temporal Split Leakage Prevention
- **Given**: A list of documents with mixed timestamps:
  - Doc A: `2026-01-01`
  - Doc B: `2026-02-01`
  - Doc C: `2026-03-01`
- **When**: Partitioning the dataset temporally at $T = \text{2026-02-15}$.
- **Then**: Doc A and Doc B must reside in the training partition.
- **And**: Doc C must reside in the validation partition.
- **And**: Any attempt to shuffle that places Doc C in training must be blocked.

### Scenario 2: Stratified Fold Balance Validation
- **Given**: A raw dataset containing 900 "Work" documents and 100 "Personal" documents (9:1 ratio).
- **When**: Splitting the dataset into 5 stratified folds.
- **Then**: Every fold must contain exactly 180 "Work" documents and 20 "Personal" documents.

### Scenario 3: Model Gate Promotion Enforcement
- **Given**: A newly trained model candidate.
- **When**: Evaluated on the validation set, yielding:
  - Macro F1: `0.81`
  - Log Loss: `0.28`
- **Then**: The promotion pipeline rejects the model registry request.
- **And**: Raises a `ModelPromotionBlocked` exception stating `Macro F1 score (0.81) is below target threshold (0.85)`.

## 5. Boundary Conditions & Exception Mapping

| Partition / Metric Input | Scenario Condition | Expected Exception / Code |
|--------------------------|---------------------|---------------------------|
| Timestamp values         | Unsorted / Null     | `ValueError`              |
| Macro F1                 | `< 0.85`            | `ModelPromotionBlocked`   |
| Log Loss                 | `> 0.35`            | `ModelPromotionBlocked`   |
| Folds count $K$          | `< 2`               | `ValueError`              |

## 6. Observability & Telemetry Assertions

- **MLflow / Model Registry Metrics**:
  - Assert that every evaluation run logs metrics `validation_macro_f1` and `validation_log_loss` as floating-point properties.
- **Audit Logs**:
  - Log model rejection events at `ERROR` level containing the specific metrics that failed.
  - Log successful promotions at `INFO` level with version hash and score values.
