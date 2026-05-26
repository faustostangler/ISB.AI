# ADR-009: Out-of-Process Model Serving via vLLM / SGLang Sidecar

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) depends on executing deep learning models (such as DroPE embeddings, text classifiers, and LLM text generation) during document ingestion, indexing, and retrieval. 

Executing these models natively in-process (Alternative A) introduces critical bottlenecks:
1. **Global Interpreter Lock (GIL) Blocking**: Heavy tensor processing in PyTorch blocks the Python GIL, freezing the web/worker event loops and causing request timeouts.
2. **Memory Fragmentation and OOM**: Neural network weights and KV caches consume large amounts of memory. Without dynamic management, this leads to Out-of-Memory (OOM) crashes, especially on our local development GPU (NVIDIA RTX 2060 with 6 GB VRAM).
3. **Friction in Compilation**: Native compilation using TensorRT-LLM and Triton (Alternative C) delivers high throughput but is extremely complex to set up, violating developer-velocity and cross-platform execution goals.

We need a serving architecture that achieves optimal performance, provides hardware-isolated memory safety, handles KV caching efficiently (PagedAttention/RadixAttention), and maintains local/production environment parity.

## Decision

We will define a `ModelInferencePort` in the application layer. All model inference (embeddings, classification, chat generation) will be executed out-of-process by communicating with a dedicated sidecar container running **vLLM** or **SGLang**.

Specific details of this architecture:
1. **Application Interface**:
   The `ModelInferencePort` abstract class will decouple the domain from the networking protocol:
   ```python
   class ModelInferencePort(ABC):
       @abstractmethod
       async def generate_completion(self, prompt: str, system_prompt: str) -> str:
           pass
   ```
2. **Out-of-Process Sidecar**:
   In both local development and production, we run a dedicated container for the model server. The application communicates with it asynchronously over HTTP (OpenAI-compatible REST API) or gRPC.
3. **Local Dev VRAM Constraints**:
   To fit model executions inside our local RTX 2060 (6 GB VRAM), we will:
   - Configure the local sidecar to load highly compressed, quantized model weights (e.g. 4-bit AWQ or GPTQ configurations).
   - Reserve GPU access in `docker-compose.yml` via the `nvidia` driver reservations block.
   - Utilize vLLM's paged memory allocation to prevent cache fragmentation and OOM.
4. **Production Configuration**:
   The production deployment will target high-precision model checkpoints (FP16 or FP8) on cloud GPUs, managed simply by changing environment variables (`MODEL_INFERENCE_URL`, `MODEL_CHECKPOINT_NAME`) without modifying the application code.

## Consequences

### Positive
* **GIL and Event Loop Isolation**: Main application and background worker processes remain lightweight and non-blocking.
* **VRAM Safety (RTX 2060)**: PagedAttention blocks allocation prevents memory OOMs during concurrent local development indexing.
* **Zero Code Changes for Scaling**: Easily swap local AWQ/GPTQ models for larger production models or external APIs (such as HuggingFace TGI) by changing the network adapter config.

### Negative
* **Networking Overhead**: Negligible latency penalty for inter-container communication on the same bridge network (mitigated by asynchronous HTTP connections).
* **Docker Complexity**: Developers must have the NVIDIA Container Toolkit installed locally to bind GPU reservations to the container.

## Alternatives Considered

### Alternative A: Native In-Process PyTorch execution
* **Pros:** Single container, easy local debugging.
* **Cons:** Event loop starvation, GIL blocking, high risk of process crash on OOM.
* **Why rejected:** Prevents serving concurrent requests and violates Monolithic simplicity guidelines.

### Alternative C: Triton Inference Server + TensorRT-LLM Compilation
* **Pros:** Maximum performance.
* **Cons:** Hardware lock-in; long compilation pipelines; breaks developer velocity.
* **Why rejected:** Violates the KISS principle.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] GPU reservations enabled in `docker-compose.yml`
- [x] Local VRAM limit configurations documented (RTX 2060)
- [x] No PyTorch code imported inside Domain package

## References

- Domain reference: `references/20-07 Framework Ecosystem and Model Tools 2.md`
- Layout reference: `references/project_layout.md`
