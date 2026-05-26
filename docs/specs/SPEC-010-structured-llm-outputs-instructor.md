# SPEC-010: Structured LLM Outputs and Failover Specification

**Linked ADR:** [ADR-010](../adr/ADR-010-structured-llm-outputs-instructor.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Knowledge Organization / Ingestion  

## 1. Overview & Objectives

This specification defines the validation criteria for structured metadata extraction using Instructor. It ensures that Pydantic schema validation, self-correction retry behaviors, and multi-provider network failover operate reliably under load.

## 2. Invariants & Extraction Rules

* **Invariant 1**: Extracted objects must strictly validate against the requested Pydantic V2 schema.
* **Invariant 2**: If the model output violates the schema, Instructor must catch the `ValidationError` and submit a self-correction request containing the error logs.
* **Invariant 3**: If the self-correction loop fails to produce a valid schema within the max retry limit (default: 3), the system must raise `SchemaExtractionFailedException`.
* **Invariant 4**: In the event of a local inference server crash or timeout, the adapter must transparently catch the error and execute the extraction using the configured cloud fallback provider.

## 3. Test Strategy Classification

* **Unit Tests (Domain)**:
  - Scope: Test domain ingestion flows utilizing a mock metadata extractor port.
* **Integration Tests (Adapter)**:
  - Scope: Test the `InstructorMetadataExtractorAdapter` using a mocked HTTP framework (such as `pytest-httpx`).
  - Assertions: Mock responses to verify:
    - First-pass success.
    - Recovery on second-pass after a validation failure (types/literals mismatches).
    - Local server connection timeouts triggering a call to the external cloud API.
    - Max retry exhaustion raising `SchemaExtractionFailedException`.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Clean First-Pass Extraction
* **Given**: A document and a Pydantic schema `DocumentSummary`.
* **When**: The extraction adapter receives a valid JSON response from the local server.
* **Then**: It must return a validated `DocumentSummary` instance.
* **And**: The total client request count to the server must equal `1`.

### Scenario 2: Recovery via Self-Correction (Retry Loop)
* **Given**: A document and a Pydantic schema with rating constraints (`Literal[1, 2, 3]`).
* **When**: The first model response yields a rating value of `"five"`.
* **And**: Instructor intercepts the `ValidationError`.
* **Then**: It must initiate a retry request containing the traceback error message.
* **And**: If the second response yields a valid rating value of `3`, the adapter must return the validated instance.

### Scenario 3: Local Server Failure and Cloud Failover
* **Given**: The local model sidecar is offline (raising `ModelServerUnavailableException`).
* **When**: The application calls `extract_metadata()`.
* **Then**: The adapter must catch `ModelServerUnavailableException`.
* **And**: Instantiate and execute the call against the configured cloud API (e.g. Claude via Anthropic API).
* **And**: Return the validated Pydantic schema successfully.
* **And**: Log a warning indicating that a failover occurred.

### Scenario 4: Extraction Exhaustion Failure
* **Given**: A complex schema.
* **When**: The model fails to return a valid JSON payload matching the schema across 3 consecutive retry attempts.
* **Then**: The adapter must raise `SchemaExtractionFailedException`.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Retry count | `> 3` | `SchemaExtractionFailedException` |
| Fallback Config | Missing API keys | `ConfigurationError` on failover attempt |
| Input Text | Empty | `ValueError` |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose counter `isb_extractor_retries_total` representing self-correction requests.
  - Expose counter `isb_extractor_failovers_total` representing the count of redirections to the cloud provider.
* **Audit Logs**:
  - Log all validation errors at `WARN` level.
  - Log failover actions at `ERROR` level, indicating the triggering exception and local server status.
