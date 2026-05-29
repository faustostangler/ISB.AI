# ADR-007: Prediction Calibration Port via Conformal Prediction

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) ingests web scraps, notes, and documents, and classifies them into domains (e.g. *Finance*, *Research*, *Personal*, *Work*). 

Traditional deep learning classifiers (such as transformers or custom ML classifiers) produce raw confidence scores (e.g., softmax outputs). However, these scores are notoriously poorly calibrated and overconfident, particularly when encountering out-of-domain data or inputs subject to feature drift. Relying on a static threshold (e.g., probability > 0.8) leads to silent misclassification failures.

Additionally, importing machine learning frameworks (like `torch` or `scikit-learn`) directly into our core domain layer violates hexagonal boundary isolation and slows down our unit test suite.

We need a way to:
1. Guarantee classification accuracy rates under statistical uncertainty.
2. Gracefully intercept out-of-domain or highly ambiguous inputs.
3. Completely isolate our domain logic from ML libraries and model types.

## Decision

We will define a `PredictionCalibratorPort` in the application layer. This port will consume raw model output scores and translate them into a statistically calibrated `CalibratedPredictionSet` at a target confidence level ($1 - \alpha$, default $90\%$).

Specific details of this design:
1. **Application Interface**:
   The `PredictionCalibratorPort` will provide an interface:
   ```python
   def calibrate(self, raw_scores: dict[str, float], confidence_level: float = 0.90) -> set[str]:
       ...
   ```
2. **Infrastructure Adapter (`ConformalCalibratorAdapter`)**:
   This adapter will implement Split Conformal Prediction. It retrieves a pre-computed list of nonconformity scores (absolute prediction errors on a validation/calibration dataset) from the cache (Redis) or database. It calculates the adjusted quantile threshold $\hat{q}$ and returns the set of all classes whose raw score is within the threshold boundary.
3. **Domain Routing Pattern**:
   The domain use case will evaluate the returned set:
   - **Single Category** (set size = 1): Auto-assigns the category.
   - **Ambiguous Categories** (set size > 1) or **Out-of-Domain** (empty set): Routes the document to a manual triage queue or flags it for active learning.
4. **Mockability**:
   For domain unit tests, we inject a mock `PredictionCalibratorPort` returning hardcoded prediction sets, keeping tests broker-free and sub-second.

## Consequences

### Positive
* **Mathematical Guarantees**: Under the assumption of exchangeability, the true category is guaranteed to be contained within the prediction set at least $90\%$ of the time.
* **Isolates ML Frameworks**: The core domain is entirely decoupled from PyTorch, Scikit-learn, or external LLM API clients.
* **Proactive Defensiveness**: Eliminates silent classification errors by mapping statistical uncertainty directly to deterministic business logic (routing to a review queue).

### Negative
* **Calibration Set Management**: We must store and periodically refresh the validation/calibration nonconformity scores in the database (refreshed asynchronously when the model is retrained).
* **Storage Lookups**: Calibrating a prediction requires fetching the nonconformity quantile, which we will mitigate by caching the pre-computed $\hat{q}$ quantile threshold in Redis.

### Neutral
* **Quantile Caching**: The computed calibration quantile is stored ephemerally in Redis cache, falling back to database retrieval if the cache is cold.

## Alternatives Considered

### Alternative A: RawSoftmax Thresholding
* **Pros:** Zero database lookups; trivial to implement.
- **Cons:** Softmax scores do not correlate to actual confidence; highly susceptible to out-of-domain failures.
* **Why rejected:** Underestimates uncertainty and leads to silent database pollution.

### Alternative C: Quantile Regression Neural Network
* **Pros:** Real-time sample-specific calibration.
* **Cons:** Heavy implementation coupling to neural network layers; makes unit testing very complex.
* **Why rejected:** Violates the KISS principle.

## Domain Model Impact

- **Port**: `PredictionCalibratorPort` (application layer — classification calibration interface)
- **Adapters**:
  - `ConformalCalibratorAdapter` (infrastructure — conformal prediction calculator using cached quantiles)
- **Bounded Context**: Classification Context (Supporting Domain)
- **Entities/Value Objects**: `CalibratedPredictionSet` (holds categories meeting the confidence threshold), `ConfidenceLevel` (float in range `(0.0, 1.0)`)

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No ML library imports in domain layer
- [x] Test strategy defined (mock adapters in unit tests)
- [x] Out-of-domain boundary handling defined

## References

- Domain reference: `references/10-05 IA and Machine Learning Fundamentals 1.md`
- Code layout: `references/project_layout.md`

