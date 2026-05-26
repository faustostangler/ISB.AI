# SPEC-012: Unified Hybrid Search and Vector Storage Specification

**Linked ADR:** [ADR-012](../adr/ADR-012-vector-storage-hybrid-search.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Knowledge Organization / Semantic Search  

## 1. Overview & Objectives

This specification defines the validation criteria for the `VectorStoragePort` implementation. It guarantees that document chunk storage, dense vector HNSW indexing, full-text sparse retrieval, Reciprocal Rank Fusion (RRF) ranking, and ACID transactional purge cascade behaviors function reliably and securely.

## 2. Invariants & Storage Rules

* **Invariant 1**: Document text chunks, parent document metadata, and high-dimensional vector embeddings must live in the same relational database row, guaranteeing single-transaction write integrity.
* **Invariant 2**: Any delete instruction triggered on a document record must instantly cascade to remove its associated text chunks and vector embeddings (LGPD owner-only compliance).
* **Invariant 3**: Hybrid search execution must return a unified list of results ranked by Reciprocal Rank Fusion (RRF) calculated over dense (cosine similarity) and sparse (TSVector match) rankings.
* **Invariant 4**: All search queries must be dynamically constrained by owner identifiers passed from the presentation boundary, rejecting any out-of-bounds cross-tenant access.
* **Invariant 5**: The dimensionality of ingested embeddings must match the configuration of the active DroPE embedding model (e.g. 1536 or 768 dimensions), failing-fast on dimension mismatch.

## 3. Test Strategy Classification

* **Unit Tests (Domain)**:
  - Scope: Test domain search orchestration workflows using a mock `VectorStoragePort`.
* **Integration Tests (Adapter)**:
  - Scope: Test the `PostgresVectorAdapter` using `pytest` against an active Postgres test container (initialized with `pgvector` enabled):
    - Verify `vector` extension installation and table schemas.
    - Test HNSW index creation and verify index builds are successful.
    - Test hybrid SQL execution: assert that RRF calculations merge sparse text search ranks and dense cosine distance ranks correctly.
    - Test ACID transactional safety: assert that database rollback occurs on aborted write transactions, avoiding partially written chunks/embeddings.
    - Test cascading delete constraints.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Transactional Insertion and Deletion Cascade
* **Given**: A document containing three text chunks and three corresponding 768-dimension embeddings.
* **When**: Storing the document via `save_document_chunks()` in a single transaction.
* **Then**: The database must commit all relational metadata and vector coordinates successfully.
* **When**: Executing a delete command on the parent document.
* **Then**: The database must automatically cascade delete all three chunks and vector coordinates.
* **And**: Subsequent vector similarity queries must return zero matching chunks for that document.

### Scenario 2: Hybrid Search Retrieval and RRF Merging
* **Given**: A database populated with documents containing specific technical terms (e.g., "GIL lock contention") and semantic equivalents.
* **When**: Executing a hybrid query for "Python GIL contention".
* **Then**: The adapter must execute a sparse query (TSVector) and a dense query (HNSW cosine similarity).
* **And**: Compute the RRF score for each unique chunk using the formula:
  $$RRF\_Score(d) = \sum_{m \in \{dense, sparse\}} \frac{1}{60 + r_m(d)}$$
  *(where $r_m(d)$ is the rank of document $d$ in the retrieved list from retriever $m$)*.
* **And**: Return results sorted in descending order of their computed RRF scores.

### Scenario 3: Owner-Only Query Isolation (Multi-Tenancy)
* **Given**: Document A owned by `User_1` and Document B owned by `User_2`.
* **When**: `User_2` executes a hybrid search query matching terms present in both documents.
* **Then**: The adapter must restrict the database query using the owner constraint `owner_id = 'User_2'`.
* **And**: Return only chunks from Document B, completely isolating Document A from retrieval.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Embedding Dimension | 1024 (expected: 768) | `VectorDimensionMismatchException` |
| Empty Embedding | Null vector | `InvalidVectorDataException` |
| Delete Query | Invalid/Non-existent ID | Returns `0` records affected; no exception raised |
| Query Filter | Unauthenticated/Missing Owner ID | `UnauthorizedSearchQueryException` |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose histogram `isb_vector_search_duration_seconds` tracking search latency, bucketed for sub-10ms monitoring.
  - Expose counter `isb_vector_queries_total` labeled by query type (`hybrid`, `dense`, `sparse`).
* **Audit Logs**:
  - Log search execution query parameters (excluding sensitive PII data) at `DEBUG` level.
  - Log any database lock contention or HNSW index build warning events at `WARN` level.
