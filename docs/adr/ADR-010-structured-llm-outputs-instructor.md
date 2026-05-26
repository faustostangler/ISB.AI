# ADR-010: Structured LLM Outputs via Instructor with Multi-Provider Failover

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) extracts structured metadata (e.g. key entities, parent topics, summaries, and action items) from ingested documents. Raw text outputs from Large Language Models (LLMs) are unreliable and often contain markdown formatting, missing fields, or incorrect data types, which break database serialization.

We need a structured output mechanism that:
1. Enforces strict schema validation matching our database models.
2. Isolates domain-level schemas from LLM client libraries and prompt structures.
3. Operates efficiently on our local GPU (NVIDIA RTX 2060 with 6 GB VRAM) but remains flexible enough to fallback to cloud APIs (such as OpenAI or Anthropic) in the event of local hardware failures or OOM errors.

## Decision

We will implement structured metadata extraction by wrapping our async HTTP model clients with the **Instructor** library. Target schemas will be defined as standard Pydantic V2 classes within the Domain layer.

Specific details of this architecture:
1. **Domain Isolation**:
   The domain use cases define the metadata contract via plain Pydantic models (e.g., `DocumentMetadata`). They call the application ports without knowing anything about prompt engineering or the underlying LLM client.
2. **Adapter Implementation (`InstructorMetadataExtractorAdapter`)**:
   The infrastructure adapter wraps the client using Instructor (`instructor.apatch()`). It submits requests to our local vLLM/SGLang sidecar, passing the target Pydantic class as the `response_model`.
3. **Resilient Multiprovider Failover**:
   If the local sidecar fails, throws connection errors, or times out due to local workstation resource contention, the adapter will catch `ModelServerUnavailableException` and dynamically redirect the request to a cloud client (e.g., Anthropic Claude or OpenAI API) using the same Pydantic schema validation.
4. **Self-Correction Retry Loop**:
   When the model returns output that violates the Pydantic schema constraints (such as missing fields or wrong literal types), Instructor automatically catches the validation error and submits it back to the LLM along with the validation message, prompting the model to self-correct (configured up to 3 retries).

## Consequences

### Positive
* **Hexagonal Isolation**: The domain only handles clean Pydantic schemas, completely isolated from vendor-specific prompt wrappers.
* **Failover Resilience**: Gracefully handles local hardware constraints (VRAM OOMs on the RTX 2060) by routing extraction tasks to external APIs without application downtime.
* **Automatic Error Recovery**: Transparently repairs schema violations without manual exception handling in use cases.

### Negative
* **Latent Retry Cost**: Schema failures incur a network retry round-trip, which we will mitigate by writing clean, explicit instructions in our system prompt templates.

## Alternatives Considered

### Alternative B: Token-Level Constraints (Outlines)
* **Pros:** $100\%$ schema compliance on the first token pass.
* **Cons:** Hard-couples the architecture to local token-guided backends, breaking cloud failover compatibility since proprietary APIs do not expose token logits overrides.
* **Why rejected:** Prevents multi-provider resilience.

### Alternative C: Agent-Based Extraction (PydanticAI)
* **Pros:** Rich agent and dependency injection patterns.
* **Cons:** High code complexity for simple deterministic metadata extraction.
* **Why rejected:** Violates the KISS principle.

### Alternative D: Raw Prompting + Manual Regex Parsing
* **Pros:** Zero external dependencies.
* **Cons:** Extremely fragile; fails on simple formatting errors.
* **Why rejected:** High rate of database insertion failures.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No Instructor or LLM library imports in Domain layer
- [x] Async-first execution context enforced
- [x] Local/Cloud failover path implemented in adapters

## References

- Domain reference: `references/21-08 MLOps and LLMOps 1.md`
- Layout reference: `references/project_layout.md`
