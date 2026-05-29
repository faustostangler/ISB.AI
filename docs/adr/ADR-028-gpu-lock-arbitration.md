# ADR-028: GPU Hardware Lock Arbitration for Inference and Training Workloads

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) executes both online model serving (via SGLang/vLLM sidecars, see [ADR-009](./ADR-009-out-of-process-model-serving.md)) and training/evaluation pipelines (`ADR-024`) on the local developer workstation and production cloud environments. 

However, we face a major physical bottleneck:
* **Workstation VRAM Limit**: Our development workstation is equipped with a single NVIDIA RTX 2060 GPU with only 6 GB of VRAM.
* **Out-of-Memory (OOM) Danger**: Running both model inference serving and model training pipelines simultaneously on the same GPU will instantly exceed the 6 GB capacity, leading to CUDA Out-of-Memory crashes that take down the entire model serving tier.
* **Offline Autonomy**: Developers must be able to run and test training pipelines locally without internet access, preventing us from offloading all training workloads exclusively to cloud infrastructure during development.

We need a resource arbitration mechanism that dynamically prevents concurrent VRAM allocations between serving and training/calibration scripts, while maintaining high availability for online API requests.

## Decision

We will implement GPU hardware resource arbitration by coordinating access to the physical GPU device using our `DistributedLockingPort` (`ADR-005`) and our dynamic cloud provider failover adapter (`ADR-010`).

Specific implementation details:
1. **Hardware Resource Lock**:
   We will define a centralized resource lock named `gpu_hardware_lock`. 
2. **Training Pipeline Gate**:
   Before initiating any training, fine-tuning, or calibration pipelines on the GPU, the pipeline script must acquire the `gpu_hardware_lock` via our locking adapter. It holds this lock for the duration of the training execution.
3. **Serving Failover Logic**:
   The online inference adapter will query the status of the `gpu_hardware_lock` or catch connection timeouts from SGLang. If the GPU is locked (meaning SGLang is temporarily paused or starved of compute cores by the training run), the adapter will dynamically activate the cloud fallback route (`ADR-010`), routing user requests to OpenAI/Anthropic APIs.
4. **SGLang VRAM Headroom**:
   Local SGLang containers will run with a strict VRAM allocation limit (`--gpu-memory-utilization 0.6` capping SGLang VRAM at 3.6 GB), leaving 2.4 GB headroom for minor concurrent operations or background processes.

## Consequences

### Positive
* **Deterministic OOM Prevention**: Guarantees that heavy training tasks and serving engines never allocate GPU memory concurrently, protecting workstation stability.
* **High Availability**: Online API requests continue functioning seamlessly during training runs by dynamically failing over to cloud API providers.
* **Reuse of Existing Abstractions**: Leverages our existing Hexagonal ports (Distributed Locking and Multi-Provider Failover) rather than introducing new complex scheduling frameworks.
* **Preserved Developer Autonomy**: Developers can run and debug the entire training loop offline locally on their workstation.

### Negative
* **Cloud Costs During Training**: Runs that overlap with active user requests will temporarily incur cloud API costs while the GPU lock is active.

### Neutral
* **Lock Duration Variance**: The training pipeline complexity dictates how long the GPU lock is held, ranging from minutes (calibration) to hours (fine-tuning).

## Alternatives Considered

### Alternative B: NVIDIA Multi-Process Service (MPS)
* **Pros**: Splits GPU compute and memory dynamically among containers.
* **Cons**: No stable support on consumer GeForce cards; a 60/40 split on a 6 GB card yields too little memory for either task to succeed.
* **Why rejected**: Incompatible with consumer developer workstations and causes constant VRAM starvation.

### Alternative C: Direct Cloud Offloading for all Training
* **Pros**: Zero local VRAM contention.
* **Cons**: Breaks offline capabilities; introduces cost and boot delays for minor local tests.
* **Why rejected**: Violates offline-first local workstation self-containment.

## Domain Model Impact

This decision affects only the resource coordination layer. No Domain Entities or Value Objects are modified.

- **Port**: `LockPort` (application layer — locking interface, see [ADR-005](./ADR-005-distributed-locking-abstraction.md))
- **Adapters**:
  - `RedisLockAdapter` / `InMemLockAdapter` (infrastructure — manages the `gpu_hardware_lock` key)
- **Bounded Context**: Platform / Shared Kernel (cross-cutting hardware management)

## Compliance

- [x] Hexagonal Architecture layers respected (lock checks managed in infrastructure adapters)
- [x] No hardware or locking framework dependencies in Domain layer
- [x] Tests strategy defined
- [x] Observability plan included
- [x] LGPD/Security implications assessed

## References

- Related ADRs: [ADR-005: Distributed Locking Abstraction via Hexagonal Port](./ADR-005-distributed-locking-abstraction.md), [ADR-009: Out-of-Process Model Serving](./ADR-009-out-of-process-model-serving.md), [ADR-010: Structured LLM Outputs via Instructor with Multi-Provider Failover](./ADR-010-structured-llm-outputs-instructor.md), [ADR-024: Training Pipeline Orchestration via Pure Python and Task Queue Integration](./ADR-024-pipeline-orchestration-dramatiq.md)
- Domain reference: `references/34-13 Cloud and Hardware for AI 3.md` (GPU VRAM management)

