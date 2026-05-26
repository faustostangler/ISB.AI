# SPEC-004: API Contract and CLI Exporter Specification

**Linked ADR:** [ADR-004](../adr/ADR-004-api-contract-and-client-generation.md)
**Status:** Approved
**Date:** 2026-05-26
**Bounded Context:** Presentation / API Ingress

## 1. Overview & Objectives

This specification defines the validation criteria and functional rules for generating the API schema and compiling client-side types. It enforces the contract-first consistency between SvelteKit and the FastAPI backend.

## 2. Bounded Context & Domain Invariants

The OpenAPI contract is generated dynamically from the presentation layer schemas and routes.
- **Invariant 1**: All endpoint paths, parameters, request body schemas, and response schemas must be fully documented in the generated OpenAPI schema.
- **Invariant 2**: The generated schema must adhere strictly to the OpenAPI 3.0 or 3.1 specification standard.

## 3. Test Strategy Classification

- **Static Validation**:
  - Scope: Test the CLI schema exporter.
  - Command: `python -m presentation.api export-schema --output openapi.json`
  - Assertions: Verify the output file `openapi.json` is generated, is valid JSON, and contains the expected router path keys.
- **Integration Validation**:
  - Scope: Verify the compiled frontend types match the backend schemas.
  - Execution: Run `orval` client generator on the exported schema and verify it compiles without TypeScript errors.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: CLI Schema Exporter Execution
- **Given**: A configured FastAPI app instance in the presentation layer.
- **When**: The schema exporter CLI command is executed with `export-schema` flag.
- **Then**: It must generate a file named `openapi.json` at the target output path.
- **And**: The file must contain standard OpenAPI root keys (`openapi`, `info`, `paths`, `components`).

### Scenario 2: Synchronized Schema Validation (CI Gate)
- **Given**: A pull request modified a Pydantic V2 schema in the backend.
- **When**: Running the schema validation step in the CI pipeline.
- **Then**: It must verify that the committed `openapi.json` matches the freshly exported schema.
- **And**: If they differ, it must fail the pipeline, prompting the developer to update and run the exporter locally.

## 5. Boundary Conditions & Exception Mapping

| Exporter Arguments | Input Value | Expected Exception / Error Code |
|--------------------|-------------|---------------------------------|
| `--output`         | `/invalid/path/openapi.json` | `FileNotFoundError` or exit code > 0 |

## 6. Observability & Telemetry Assertions

- **CI Telemetry**:
  - The build pipeline logs the size and path of the generated `openapi.json` file.
  - Contract schema hash changes are tracked to identify breaking API changes.
