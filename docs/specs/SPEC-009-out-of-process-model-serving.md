# SPEC-009: Out-of-Process Model Serving Specification

**Linked ADR:** [ADR-009](../adr/ADR-009-out-of-process-model-serving.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure  

## 1. Overview & Objectives

This specification details the validation criteria for out-of-process model execution using the `ModelInferencePort`. It ensures correct networking abstraction, connection failure recovery, timeout policies, and telemetry monitoring.

## 2. Invariants & Networking Rules

* **Invariant 1**: All inference calls must execute asynchronously (`async`/`await`) to prevent event-loop freezing.
* **Invariant 2**: Connection failures, bad gateway responses, or timeouts from the model server must be caught and raised as a clean domain-specific exception (`ModelServerUnavailableException`).
* **Invariant 3**: Network request timeouts must be strictly enforced (default: 30 seconds for generation, 5 seconds for embeddings) to prevent socket leaks.
* **Invariant 4**: Host configuration (`MODEL_INFERENCE_URL`) must be validated on system startup using Pydantic Settings, utilizing a fail-fast approach if invalid.

## 3. Test Strategy Classification

* **Unit Tests (Domain)**:
  - Scope: Test domain use cases with a mock `ModelInferencePort` to ensure correct response extraction and exception handling.
* **Integration Tests (Adapter)**:
  - Scope: Test the HTTP-based sidecar adapter (`vLLMAdapter` or `SGLangAdapter`).
  - Assertions: Mock server endpoints (using `pytest-httpx` or similar) to verify handling of:
    - Success (200 OK with valid OpenAI-format JSON).
    - Client timeouts.
    - Quantization headers.
    - Server crashes (500 Internal Server Error, 502 Bad Gateway).

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Standard Generation (Success)
* **Given**: A running vLLM/SGLang model sidecar.
* **When**: Calling `generate_completion(prompt, system_prompt)` on the port.
* **Then**: The return value must be a non-empty string.
* **And**: The call must complete asynchronously without blocking other task executions.

### Scenario 2: Inference Sidecar Offline (Exception Mapping)
* **Given**: The model sidecar container is stopped or unavailable.
* **When**: Calling the inference port.
* **Then**: The adapter must timeout within 5 seconds.
* **And**: Raise `ModelServerUnavailableException`.

### Scenario 3: Quantized Profile Verification
* **Given**: The application is running in local `development` mode.
* **When**: The model server configuration is loaded.
* **Then**: The loaded model file parameter must resolve to an INT4/AWQ quantized checkpoint (e.g. `SmolLM-360M-Instruct-AWQ`) to stay within the 6 GB VRAM envelope.

### Scenario 4: Fast Fail on Startup
* **Given**: The environment variable `MODEL_INFERENCE_URL` is empty or invalid (e.g., missing host scheme).
* **When**: Initializing the application settings.
* **Then**: Pydantic must raise a validation error and abort process startup.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Server Response | `502 Bad Gateway` | `ModelServerUnavailableException` |
| Server Response | `422 Unprocessable` | `ValueError` (invalid request payload) |
| Timeout Limit | Exceeded | `ModelServerUnavailableException` (Request timeout) |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose histogram `isb_inference_request_duration_seconds` labeled by role/model.
  - Expose counter `isb_inference_tokens_total` representing input and output tokens consumed.
* **Audit Logs**:
  - Log inference start and completion details at `DEBUG` level.
  - Log connection timeouts and retries at `ERROR` level, including retry count.
