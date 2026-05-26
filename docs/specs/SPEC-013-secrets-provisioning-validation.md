# SPEC-013: Secrets Provisioning and Configuration Validation Specification

**Linked ADR:** [ADR-013](../adr/ADR-013-secrets-provisioning-validation.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Configuration / Security  

## 1. Overview & Objectives

This specification defines the validation criteria for container configuration loading, Pydantic-Settings verification, fail-fast container boot dynamics, and credential leak prevention.

## 2. Invariants & Configuration Rules

* **Invariant 1**: All configuration variables must be centralized and validated via a single class (`Settings` in `src/config.py`) inheriting from Pydantic's `BaseSettings`.
* **Invariant 2**: The instantiation of `Settings` must be performed at application startup (in `src/main.py`), and any validation error must block startup and terminate the process with exit code `1`.
* **Invariant 3**: Secrets (such as DB passwords and API keys) must be typed as `pydantic.SecretStr` to prevent accidental logging or printing of plaintext values.
* **Invariant 4**: In production mode (`ENV = "production"`), default fallbacks for critical secrets (like fallback cloud API keys) must be disabled, forcing explicit provisioning.

## 3. Test Strategy Classification

* **Unit Tests (Configuration)**:
  - Scope: Test the `Settings` model validation using different environment dict states:
    - Test that `ValidationError` is raised when mandatory variables (e.g., `DATABASE_URL`) are missing.
    - Test that type constraints are validated (e.g., `PORT` must be an integer between 1 and 65535).
    - Test that `SecretStr` variables mask their values when represented as strings or logged.
    - Test that local development configurations fallback safely to default values when `ENV` is set to `"development"`.
    - Test that `ENV = "production"` raises errors when standard fallback values are relied upon.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Successful Bootstrap Validation
* **Given**: An environment populated with valid configuration properties:
  - `DATABASE_URL` = "postgresql://isb:pass@localhost:5432/isb"
  - `PORT` = "8000"
  - `ENV` = "development"
* **When**: The application instantiates the `Settings` class.
* **Then**: The settings object must be created successfully.
* **And**: The parsed values must match their corresponding environment types (e.g. `PORT` is mapped to type `int`).

### Scenario 2: Fail-Fast Startup on Missing Required Secret
* **Given**: An environment where `DATABASE_URL` is omitted.
* **When**: The application initialization script execution starts.
* **Then**: The settings loader must raise a `ValidationError`.
* **And**: The process must immediately catch the error, write a structured log indicating which field failed validation, and exit with code `1`.

### Scenario 3: Leak Protection for Secrets (Masking)
* **Given**: An environment where `OPENAI_API_KEY` is set to `"sk-123456789abcdef"`.
* **When**: Accessing the settings configuration or converting the Settings model to a JSON string.
* **Then**: The key must be displayed as `"**********"` (masked by Pydantic's `SecretStr`).
* **And**: Under no circumstances should the plaintext string `"sk-123456789abcdef"` be output to the console logs.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| `PORT` | `65536` | `ValidationError` (Port range violation) |
| `DATABASE_URL` | Invalid connection schema | `ValidationError` (Regex pattern match fail) |
| `ENV` | `invalid_mode` | `ValidationError` (Not in allowed literal set) |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose a simple metric `isb_application_startup_status` (gauge) indicating `1` for healthy launch and `0` for validation failure.
* **Audit Logs**:
  - Log successful boot events containing validation summaries (listing config properties, excluding raw values) at `INFO` level.
  - Log all startup validation errors with field names and validation rules at `CRITICAL` level. Plaintext values must be stripped from the log payload.
