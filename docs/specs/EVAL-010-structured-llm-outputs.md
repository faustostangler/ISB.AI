# EVAL-010: Structured LLM Outputs Instructor Rubric

**Linked SPEC:** [SPEC-010](./SPEC-010-structured-llm-outputs-instructor.md)  
**Blocking Policy:** BLOCK (fails the pipeline on threshold breach)

## Dimensions

### 1. Schema Adherence
- **ADR Consequence**: ADR-010 Consequence 1 (Hexagonal schema-level consistency)
- **Method**: Strict validation against target Pydantic V2 schemas.
- **Pass Threshold**: `score == 1.0` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-010-schema.jsonl`

### 2. Entity Extraction Recall
- **ADR Consequence**: ADR-010 Consequence 3 (Automatic Error Recovery & Precision)
- **Method**: LLM-as-judge comparing extracted entities against a golden human-annotated dataset.
- **Pass Threshold**: `Recall >= 0.85` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-010-entities.jsonl`
