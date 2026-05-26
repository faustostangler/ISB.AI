# SPEC-015: GPU Node Pool Autoscaling and Model Caching Specification

**Linked ADR:** [ADR-015](../adr/ADR-015-gpu-infrastructure-caching.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform / Infrastructure  

## 1. Overview & Objectives

This specification defines the validation criteria for production GPU node pool deployments, SSD-backed Persistent Volume Claim (PVC) model weight caching, hash-based checkpoint verification, and queue-depth-based Horizontal Pod Autoscaling (HPA) dynamics.

## 2. Invariants & Deployment Rules

* **Invariant 1**: Inference containers must boot and read model weights exclusively from the mounted cache directory path (`/models`), with no dynamic downloading from external endpoints permitted during runtime.
* **Invariant 2**: Prior to initiating model load execution, the bootstrap script must calculate and verify the cryptographic hash (SHA-256) of the local checkpoint files against a hardcoded registry, failing-fast on mismatch.
* **Invariant 3**: All inference pods must run under our non-privileged, non-root user profile (`USER isb`, UID/GID 10001, see [ADR-006](ADR-006-secure-non-root-container.md)) even when mounting system GPU drivers via container runtime interfaces (CRIs).
* **Invariant 4**: Horizontal Pod Autoscaling (HPA) must be driven by current request queue sizes (`vllm_num_requests_waiting` from the sidecar metrics exporter) rather than standard CPU/GPU utilization percentages.

## 3. Test Strategy Classification

* **Integration Tests (Platform Deployment)**:
  - Scope: Test deployment manifests and startup scripts against local Docker / Kubernetes configurations:
    - Test that the sidecar process exits with code `1` immediately when the `/models` cache directory is empty.
    - Test that the sidecar exits with code `1` when model weight files are modified or corrupted (hash verification failure).
    - Test that the container successfully boots and reaches readiness state in under 15 seconds when the cache directory contains valid model checkpoints.
    - Test that the HPA controller registers custom metrics and triggers a pod replica scale-out when mock metrics report `vllm_num_requests_waiting > 5`.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Accelerated Bootstrap from Local Cache
* **Given**: An SSD-backed cache volume containing a valid Whisper model checkpoint (verified SHA-256 hash).
* **When**: The container runtime launches the vLLM/SGLang server pod.
* **Then**: The startup script must skip external API handshakes.
* **And**: Mount the local checkpoint and transition to `READY` state within `15` seconds.

### Scenario 2: Fail-Fast on Empty Cache or Hash Mismatch
* **Given**: A newly provisioned container instance where the `/models` directory is unmounted or empty.
* **When**: The startup entrypoint is executed.
* **Then**: The hash-verifier script must fail-fast, write a CRITICAL alert log stating `CheckpointNotFoundException` or `SHA256HashMismatchException`, and exit with code `1`.

### Scenario 3: Queue-Based Pod Autoscaling Execution
* **Given**: An active deployment running with a minimum of `1` GPU replica pod.
* **When**: A burst of ingestion requests queue up, causing the Prometheus metric `vllm_num_requests_waiting` to average `6` over a 1-minute window.
* **Then**: The Kubernetes Horizontal Pod Autoscaler (HPA) must detect the threshold breach.
* **And**: Send a scale-out instruction to provision `1` additional replica pod.
* **And**: Scale back down to `1` replica after the metric returns to `0` and stays there for a 10-minute stabilization cooldown window.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Cache Volume | Write permission requested | Denied (volume must be mounted read-only `ro` to prevent corruption) |
| Checkpoint File | Corrupted/Altered bits | `SHA256HashMismatchException` / Exit Code `1` |
| Scale Down Limit | Active requests > 0 | Scale down blocked until queue is completely empty |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose gauge `isb_gpu_node_pool_replicas` tracking current active serving instances.
  - Expose gauge `isb_model_load_duration_seconds` tracking weight parsing speed at startup.
* **Audit Logs**:
  - Log model cache verification starts, file paths, and cryptographic hashes at `INFO` level.
  - Log any autoscaling scale-up and scale-down triggers at `INFO` level.
