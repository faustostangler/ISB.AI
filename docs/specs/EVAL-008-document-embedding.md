# EVAL-008: Document Embedding DroPE Rubric

**Linked SPEC:** [SPEC-008](./SPEC-008-document-embedding-drope.md)  
**Blocking Policy:** BLOCK (fails the pipeline on threshold breach)

## Dimensions

### 1. Retrieval Reciprocal Rank Relevance (MTEB equivalent)
- **ADR Consequence**: ADR-008 Consequence 1 (Global Context Preservation & Fact Retrieval)
- **Method**: Cosine similarity retrieval against a golden "needle-in-a-haystack" long-context dataset.
- **Pass Threshold**: `Mean Reciprocal Rank (MRR) >= 0.85` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-008-retrieval.jsonl`

### 2. Semantic Drift Stability
- **ADR Consequence**: ADR-008 Consequence 2 (Zero-shot length generalization)
- **Method**: Cosine similarity comparison of short document segment embeddings against full long-document embeddings.
- **Pass Threshold**: `Similarity Score >= 0.70` (WARN)
- **Dataset**: `tests/evals/datasets/EVAL-008-drift.jsonl`
