# ADR-022: Model Validation Partitioning and Accuracy Metrics

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) classifies ingested notes and web scraps into distinct domains. To guarantee the reliability of these classifications, we must periodically train and deploy new revisions of our classifier. 

However, evaluating these models presents several statistical risks:
1. **Class Imbalance**: Certain categories (e.g. *Work*) may contain 90% of the documents, while others (e.g. *Personal*) represent only 5%. Raw accuracy metrics will hide a model that completely fails on rare categories.
2. **Chronological Leakage**: If document vocabularies or topics drift over time, randomly shuffling the training and test sets leaks information from the "future" into the "past", artificially inflating offline validation scores and leading to poor generalization in production.
3. **Probability Calibration**: To support our Conformal Prediction calibration step ([ADR-007](./ADR-007-prediction-calibration-port.md)), we require models that output well-calibrated probabilities rather than raw overconfident softmax scores.

We need a standardized validation pipeline that prevents leakage, handles class imbalance, and penalizes poorly calibrated models.

## Decision

We will implement a unified model validation pipeline characterized by:
1. **Stratified K-Fold Partitioning**: For historical documents where time is not a major signal, we will partition training using Stratified K-Fold Cross-Validation to guarantee that rare classes are represented equally in each fold.
2. **Temporal Splitting**: For datasets or features that carry chronological metadata, we will enforce a strict Temporal Split (training on documents before time $T$, validating on documents after time $T$).
3. **Multi-Dimensional Metrics**: Models will be promoted to production only if they meet predefined thresholds on:
   - **Macro F1-Score**: To evaluate classification precision and recall evenly across all classes, regardless of their occurrence frequency.
   - **Log Loss / Cross-Entropy**: To measure and penalize overconfident incorrect predictions, forcing the model to produce well-calibrated probabilities.

## Consequences

### Positive
- **Leakage-Free Validation**: Temporal splits ensure validation results mirror actual production inference behavior.
- **Fair Representation**: Macro F1-Score prevents rare categories from being ignored during model selection.
- **Calibrated Scores**: Prioritizing Log Loss ensures the classifier output probabilities are fit for conformal prediction mapping, reducing manual triage volumes.

### Negative
- **Computational Overhead**: Running Stratified Cross-Validation on large training sets takes longer and requires more compute resources.
- **Pipeline Complexity**: Developers must write custom temporal ordering queries when preparing training data.

### Neutral
- Training datasets and metrics are managed as versioned artifacts in our MLOps pipelines.

## Alternatives Considered

### Alternative A: Random Train/Test Split with Raw Accuracy
- **Pros**: Easy to implement; fast execution time.
- **Cons**: Severe data leakage; completely blind to class imbalance.
- **Why rejected**: Fails to provide realistic performance guarantees, leading to silent classification failures in production.

### Alternative C: Online-Shadow Routing & A/B Validation
- **Pros**: Directly tests real-world data distributions.
- **Cons**: High operational cost; cannot catch regressions before deployment.
- **Why rejected**: Highly unsafe; increases MTTR (Mean Time To Recovery) and DORA Change Failure Rates.

## Domain Model Impact

This decision affects only the validation scripts and MLOps metrics collection pipelines. No Domain Entities or Value Objects are modified.

- **Port**: N/A (validation and evaluation processes are executed as part of training pipelines, outside the runtime application)
- **Adapter**: `TrainingPipelineAdapter` (infrastructure — handles the training execution flow)
- **Bounded Context**: MLOps Context (Supporting Domain)

## Compliance

- [x] Hexagonal Architecture layers respected (validation logic isolated in MLOps/training scripts)
- [x] No framework dependencies in Domain layer
- [x] Tests strategy defined
- [x] Observability plan included
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-007: Prediction Calibration Port via Conformal Prediction](./ADR-007-prediction-calibration-port.md)
- Domain reference: `references/11-05 IA and Machine Learning Fundamentals 2.md` (Accuracy metrics and classification guidelines)
- Domain reference: `references/10-05 IA and Machine Learning Fundamentals 1.md`
