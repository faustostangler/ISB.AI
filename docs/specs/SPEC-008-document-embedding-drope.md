# SPEC-008: Document Embedding Port Specification

**Linked ADR:** [ADR-008](../adr/ADR-008-document-embedding-drope.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Knowledge Organization / Search  

## 1. Overview & Objectives

This specification defines the validation criteria for document representation using the `DocumentEmbeddingPort` with DroPE-calibrated model adapters. It ensures that embeddings are generated reliably, handle long contexts without memory overflows, and prevent NaN/Infinity calculations.

## 2. Bounded Context & Domain Invariants

- **Value Object**: `DenseVector`
  - Validation: Float array matching model dimensions (e.g. 768 or 1536). All values must be finite (no NaN or Inf).
- **Value Object**: `DocumentContent`
  - Validation: String, must be non-empty, clamped to 32,768 tokens.

## 3. Test Strategy Classification

* **Unit Tests (Domain)**:
  - Scope: Test indexing use cases using a mock `DocumentEmbeddingPort` returning a pre-defined float array.
* **Integration Tests (Adapter)**:
  - Scope: Test the `DroPEEmbeddingAdapter` with a live local model checkpoint.
  - Assertions: Verify output dimensions, zero-shot length execution (e.g., with 8,192 tokens), execution latency, and truncation logic.
- **LLM Evals (Non-Deterministic Gates)**:
  - Scope: Verification of embedding representation quality against reference datasets.
  - Rubric: Linked to [EVAL-008-document-embedding.md](./EVAL-008-document-embedding.md)

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Standard Document Ingestion
* **Given**: A text document of 200 words.
* **When**: Calling `embed_document(text)` on the port.
* **Then**: The return value must be a list of floats.
* **And**: The length of the list must match the model's output dimension exactly.
* **And**: All values in the list must be finite (no `NaN` or `Inf`).

### Scenario 2: Zero-Shot Length Generalization (Long Context)
* **Given**: A long research paper containing 8,192 tokens.
* **When**: Calling `embed_document(text)` on the DroPE adapter.
* **Then**: The model must execute without raising out-of-memory or out-of-index exceptions.
* **And**: It must return a valid, unfragmented dense float vector.

### Scenario 3: Safety Truncation Enforcer
* **Given**: A huge log file containing 50,000 tokens.
* **When**: Calling `embed_document(text)` on the adapter.
* **Then**: The adapter must truncate the text to the maximum safety limit (e.g., 32,768 tokens) before tokenization.
* **And**: The generated embedding must represent the truncated text cleanly.

### Scenario 4: Empty Content Exception
* **Given**: An empty string `""` or whitespace `"   "`.
* **When**: Calling `embed_document(text)`.
* **Then**: The system must raise a `ValueError` indicating that empty content cannot be embedded.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Text size | 0 chars | `ValueError` |
| Text size | > 32,768 tokens | Truncated to 32,768 tokens |
| Model Weight Load | Missing checkpoint | `RuntimeError` on startup initialization |

## 6. Regression Anchors (For Bug Fixes Only)

*None at present (greenfield configuration).*

## 7. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose histogram `isb_embedding_latency_seconds` representing model forward pass times.
  - Expose histogram `isb_embedding_input_tokens` representing the distribution of token lengths processed.
* **Audit Logs**:
  - Log any truncation events at `INFO` level, capturing the document ID and original word count.

