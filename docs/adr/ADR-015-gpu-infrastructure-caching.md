# ADR-015: GPU Infrastructure Provisioning via Kubernetes Node Pools and Local PVC Model Caching

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) uses an out-of-process model serving strategy (vLLM/SGLang sidecar, see [ADR-009](ADR-009-out-of-process-model-serving.md)) to run heavy deep learning tasks, including Whisper audio transcriptions, Vision-Language Model (VLM) image descriptions, and DroPE document embeddings. 

To run this serving layer cost-effectively and reliably in production:
1. **Developer Parity**: The infrastructure topology in production (GKE/Kubernetes) must mirror local development (a Docker Compose sidecar mapping to our RTX 2060 GPU), avoiding codebase fork or custom logic branches.
2. **Cold Start Protection**: Loading multi-gigabyte model checkpoints (Whisper, DroPE, VLMs) from scratch can take over 10 minutes when pulling from raw repository endpoints, violating our time-to-first-token (TTFT) and real-time ingestion SLOs.
3. **Elastic Scaling**: Ingestion workloads are bursty (e.g. users uploading bulk media or importing massive document folder sets). The GPU infrastructure must scale out dynamically when backlogs build, and scale back down to zero or low-replica baselines to optimize cloud spend.
4. **Predictable Latency**: Network round-trip times between the application monolith and the inference server must remain in the single-digit millisecond range.

## Decision

We will deploy our production inference servers in dedicated, GPU-backed Kubernetes Node Pools (e.g. GKE nodes equipped with NVIDIA L4 or H200 GPUs) using local Persistent Volume Claims (PVC) for model caching and autoscaling managed via custom metrics.

Specific implementation details:
1. **Model Cache (Local PVC)**:
   - We will deploy a read-only shared Persistent Volume Claim (PVC) backed by high-speed cloud SSDs.
   - All required model checkpoints (Whisper, VLM, DroPE embeddings) will be pre-downloaded and cached on this volume.
   - When new model serving pods scale up, they will mount the PVC directly to bypass internet model downloads, reducing container initialization time (from download to entrypoint execution) to under 15 seconds.
2. **Sidecar / Pod Deployment**:
   - In production, the vLLM/SGLang server runs either as a sidecar container inside the worker pod or as a closely routed service in the same local network node pool.
   - This ensures sub-millisecond network latency between our application logic and the CUDA execution layer.
3. **Autoscaling (HPA)**:
   - We will configure Kubernetes Horizontal Pod Autoscaler (HPA) using custom Prometheus metrics (specifically `vllm:num_requests_waiting` and GPU VRAM memory saturation).
   - This prevents scaling thrashing by using queue-depth indicators instead of lagging CPU/GPU averages.
4. **Developer Environment Alignment**:
   - The local workstation environment will use a docker-compose volume mapping (`./models_cache:/models`) to mimic the PVC, targeting the local NVIDIA RTX 2060 CUDA workstation identically.

## Consequences

### Positive
* **Zero Internet Latency on Boot**: Mount-on-boot from local SSD PVCs bypasses HuggingFace/external endpoint downloads, safeguarding developer and pipeline velocity.
* **Turnkey Deployment Parity**: The code interacts with the `ModelInferencePort` identically whether it is hitting `localhost:8000` (RTX 2060 dev) or `http://sglang-service:8000` (production L4 pool).
* **Cost Efficiency**: GPU-backed pools autoscale based on active queue length, scaling down to baseline minimums during inactive periods to prevent idle GPU bills.
* **Network Speed**: Multi-container pods or single-node network routing keeps data transfer times between the application worker and the model serving GPU negligible.

### Negative
* **Storage Cost**: Maintaining high-speed SSD PVCs with cached models incurs a modest, predictable monthly storage cost.
* **Autoscaling Delay**: Setting up a physical GPU node in the cloud pool can take 1–3 minutes when scaling out from a zero-node pool. We will mitigate this by keeping a baseline pool minimum of 1 active cost-effective GPU node (e.g. NVIDIA L4).

### Neutral
* **Model Cache Update Frequency**: Checkpoints cached on the PVC are updated out-of-band only when new model versions are released, requiring no runtime application logic updates.

## Alternatives Considered

### Option B: Fully Managed Serverless GPU Inference Endpoints (Vertex AI / Runpod Serverless)
* **Pros:** Complete abstraction of infrastructure; scales to zero automatically.
* **Cons:** High network latency variance (cold start penalty of minutes when scaling from zero, due to downloading 12GB+ container images and model weights over the internet). It also breaks local workstation offline parity.
* **Why rejected:** Violates local self-containment, introduces unpredictable latency jitter, and breaks developer environment parity.

### Option C: Dedicated High-Density GPU Colocation / Bare-Metal Clusters
* **Pros:** Staggering compute capacity; full control over hardware (e.g. DGX Blackwell/Hopper systems).
* **Cons:** Massive capital expenditure (CapEx), high operational footprint, and complex orchestration overhead.
* **Why rejected:** Complete overkill for an inference-centric Intelligent Second Brain monolith, violating the KISS principle.

## Domain Model Impact

This decision affects only the deployment platform infrastructure. No Domain Entities or Value Objects are modified.

- **Port**: N/A (Kubernetes node pools and volumes operate entirely at the platform infrastructure level)
- **Adapter**: Kubernetes PVC templates, GKE node pool configuration manifests
- **Bounded Context**: Platform (Infrastructure)

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] Local/Production hardware parity achieved
- [x] GPU resource consumption optimized
- [x] Cold-start mitigation implemented via local SSD caching
- [x] Prometheus-driven autoscaling thresholds defined

## References

- Related ADRs: [ADR-006: Secure Non-Root Container](ADR-006-secure-non-root-container.md), [ADR-009: Out-of-Process Model Serving](ADR-009-out-of-process-model-serving.md), [ADR-014: Unified Observability Architecture](ADR-014-observability-architecture.md)
- Domain reference: `references/32-13 Cloud and Hardware for AI 1.md`, `references/34-13 Cloud and Hardware for AI 3.md`, `references/35-13 Cloud and Hardware for AI 4.md`

