# EVAL-012: Vector Storage Hybrid Search Rubric

**Linked SPEC:** [SPEC-012](./SPEC-012-vector-storage-hybrid-search.md)  
**Blocking Policy:** BLOCK (fails the pipeline on threshold breach)

## Dimensions

### 1. Retrieval Relevance (NDCG@10)
- **ADR Consequence**: ADR-012 Consequence 1 (RRF Cosine & Sparse Fusion retrieval quality)
- **Method**: Normalized Discounted Cumulative Gain (NDCG) at K=10 against human-annotated search query benchmarks.
- **Pass Threshold**: `NDCG@10 >= 0.80` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-012-ndcg.jsonl`

### 2. Retrieval Precision (Precision@5)
- **ADR Consequence**: ADR-012 Consequence 3 (Semantic search query precision)
- **Method**: Percentage of relevant chunks in the top 5 retrieved items.
- **Pass Threshold**: `Precision@5 >= 0.75` (WARN)
- **Dataset**: `tests/evals/datasets/EVAL-012-precision.jsonl`
