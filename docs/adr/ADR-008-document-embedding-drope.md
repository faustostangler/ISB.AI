# ADR-008: Document Embedding Port via DroPE (Dropped Positional Embeddings)

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is designed to organize, search, and synthesize user knowledge across notes, code files, and research papers of arbitrary lengths. To achieve this, the system must generate dense vector embeddings of entire documents.

Standard transformer-based embedding models are constrained by their pretraining context lengths (typically 2K or 4K tokens) due to the behavior of their Positional Embeddings (specifically RoPE). When inputs exceed this window:
1. Standard RoPE causes attention degradation and severe hallucinations because its rotational phases drift out of distribution.
2. Traditional RoPE-scaling tricks (such as NTK-aware scaling or YaRN) preserve perplexity but warp content-matching heads over long distances, causing "attention bleed" and failing to retrieve facts located deep in the context (the "lost in the middle" problem).
3. Splitting documents into static overlapping chunks (e.g., 512-token chunks) avoids sequence limits but fragments semantic structure, making global summarization and multi-hop reasoning across distant sections impossible.
4. State Space Models (SSMs/Mamba) offer linear complexity but lack mature, pre-trained retrieval-optimized weights and require specialized CUDA kernels that break local CPU-based development velocity.

## Decision

We will define a `DocumentEmbeddingPort` in the application layer. The production infrastructure adapter will implement a local transformer model optimized via the **DroPE (Dropped Positional Embeddings)** paradigm.

Specific details of this implementation:
1. **Application Interface**:
   ```python
   class DocumentEmbeddingPort(ABC):
       @abstractmethod
       async def embed_document(self, text: str) -> list[float]:
           """Generates a single dense embedding representing the full document context."""
           pass
   ```
2. **DroPE Adapter Implementation**:
   The adapter will load a local transformer model (e.g., SmolLM-DroPE or Llama2-DroPE) where positional embeddings have been removed and the model has been briefly recalibrated at the original context length. This allows the model to generalize zero-shot to sequence lengths up to 8x the original window without attention degradation or phase warping.
3. **Decoupled Architecture**:
   All checkpoint loading, tokenization, sequence padding, and attention-mask configurations remain encapsulated within the infrastructure adapter, keeping the domain layer simple and independent of deep learning frameworks (PyTorch, HuggingFace).
4. **Mocking for Testing**:
   Unit tests will inject a mock adapter returning deterministic float vectors, keeping test suites standalone and sub-second.

## Consequences

### Positive
* **Global Context Preservation**: Ingests long documents (16K+ tokens) as single units, preserving global semantics and enabling multi-hop retrieval.
* **High Attention Resolution**: Avoids the phase-warping and attention-bleed issues of NTK/YaRN scaling, maintaining strong recall for remote facts.
* **Developer Velocity**: Standard transformer architectures (without positional layers) run on CPU/PyTorch out of the box without requiring custom CUDA compilations like Mamba.

### Negative
* **Memory Scaling**: Attention cost remains quadratic $O(N^2)$. For extremely long files, we must enforce a safety limit (e.g., 32,768 tokens) or delegate processing to background worker queues to prevent out-of-memory errors on local dev machines.

### Neutral
* **Model Weight Deployment**: Embedding model weights are downloaded during container build/provisioning time, rather than dynamically on boot, to maintain fail-fast startup.

## Alternatives Considered

### Alternative A: Static Overlapping Chunking
* **Pros:** Low memory overhead; works with any external API model.
* **Cons:** Fragments document semantics; poor global representation.
* **Why rejected:** Restricts the AI's ability to relate distant ideas, which is a core requirement of a "second brain."

### Alternative C: State Space Models (Mamba)
* **Pros:** Linear complexity $O(N)$; infinite context length.
* **Cons:** Lack of mature, pre-trained retrieval checkpoints; high engineering overhead for custom CPU kernels.
* **Why rejected:** Violates the KISS principle by introducing unnecessary compiling and deployment friction.

### Alternative D: Dynamic RoPE Scaling (NTK-aware / YaRN)
* **Pros:** Simple runtime modification of standard weights.
* **Cons:** Content-matching heads degrade at large token distances.
* **Why rejected:** Fails "needle-in-a-haystack" and remote fact-retrieval benchmarks.

## Domain Model Impact

- **Port**: `DocumentEmbeddingPort` (application layer — document embedding generator interface)
- **Adapters**:
  - `DroPeEmbeddingAdapter` (infrastructure — local transformer model execution adapter)
- **Bounded Context**: Knowledge Context (Core Domain)
- **Value Objects**: `DenseVector` (validated list of floats), `DocumentContent` (validated text content)

## Langfuse Ingestion Strategy

- **Trace Taxonomy**:
  - `trace_id`: Maps to the parent document ingestion job ID.
  - Tags: `model_name` (e.g. `SmolLM-DroPE`), `sequence_length`.
- **Span Hierarchy**:
  - Parent trace: `ingest` or `query`
  - Child span: `generate_embeddings` (covers tokenization, forward pass, and mean pooling)
- **Prompt Version Tracking**: N/A (embedding execution does not use dynamic prompts).
- **Score Schema**:
  - Tracks embedding latency and token count.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] No PyTorch/HuggingFace imports in Domain layer
- [x] Mockable adapter defined for local unit testing
- [x] Memory safety limits established

## References

- Domain reference: `references/DroPE/Extending the Context of Pretrained LLMs by Dropping their Positional Embeddings`
- Code layout: `references/project_layout.md`

