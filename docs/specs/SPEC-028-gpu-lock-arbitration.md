# SPEC-028: GPU Hardware Lock Arbitration Specification

**Linked ADR:** [ADR-028](../adr/ADR-028-gpu-lock-arbitration.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Infrastructure / Hardware Management  

## 1. Overview & Objectives

This specification defines the validation criteria for coordinating access to the physical GPU device using our distributed lock system. It ensures that local training pipelines and model serving containers do not allocate memory concurrently, preventing Out-of-Memory (OOM) errors and verifying proper cloud API failover.

## 2. Invariants & Arbitration Rules

*   **Invariant 1**: Any training, fine-tuning, or validation pipeline that targets the GPU must check and acquire the `gpu_hardware_lock` before executing deep learning memory allocation.
*   **Invariant 2**: If the `gpu_hardware_lock` is held by another process, the pipeline block must wait/block or abort execution with a `GPULockedException`.
*   **Invariant 3**: If the `gpu_hardware_lock` is active or if local SGLang serving is unreachable, the model inference adapter must fallback and route structured requests to the configured Cloud Provider Adapter.
*   **Invariant 4**: Upon completion or failure of a training run, the pipeline must release the `gpu_hardware_lock` to allow other tasks or local SGLang memory reclamation.

## 3. Test Strategy Classification

*   **Unit Tests (Inference Adapter Failover)**:
    *   Scope: Mock the `DistributedLockingPort` and SGLang HTTP client.
    *   Assertions:
        *   When `gpu_hardware_lock` is mock-active, calling the `ModelInferencePort.predict()` routes queries to the Cloud Provider Adapter.
        *   When `gpu_hardware_lock` is mock-inactive, calling the port routes queries to the local SGLang URL.
*   **Integration Tests (Lock Gating)**:
    *   Scope: Run two mock training pipelines concurrently using the `ImmediateTaskQueueAdapter`.
    *   Assertions:
        *   The first pipeline acquires the `gpu_hardware_lock` and runs successfully.
        *   The second pipeline fails to acquire the lock, raising a `GPULockedException` and aborting execution cleanly without causing CUDA allocation calls.
*   **VRAM Leakage Verification**:
    *   Scope: Run the local training script and verify host GPU allocation using `nvidia-smi` queries.
    *   Assertions: Verify that upon script termination, the GPU memory allocated by the training process returns to baseline levels.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Training Pipeline Respects Active Lock
*   **Given**: An active training task currently holding the `gpu_hardware_lock`.
*   **When**: A user or scheduler triggers a new training task.
*   **Then**: The second task must fail to acquire the lock and exit immediately.
*   **And**: Raise a warning log indicating the GPU is currently occupied.

### Scenario 2: Inference Routes to Cloud during Active Lock
*   **Given**: A training pipeline running and holding the `gpu_hardware_lock`.
*   **When**: An online user submits a document classification request.
*   **Then**: The local serving adapter detects the lock is active.
*   **And**: Bypasses the local SGLang sidecar container.
*   **And**: Submits the request to the Cloud Provider API.
*   **And**: Returns the valid structured prediction back to the user interface.

### Scenario 3: Training Completes and Releases Lock
*   **Given**: A training pipeline executing and holding the `gpu_hardware_lock`.
*   **When**: The training script completes successfully or crashes with an exception.
*   **Then**: The pipeline must execute the lock release cleanup block.
*   **And**: The `gpu_hardware_lock` status in Redis/distributed coordinator is set back to free.

## 5. Boundary Conditions & Exception Mapping

| Event / Parameter | Condition | Expected Outcome |
|-------------------|-----------|------------------|
| Lock Coordinator Offline | Redis Server timeout | Raise `LockCoordinatorUnavailableException`, fallback to CPU-only training and cloud inference, log critical warning. |
| Process Orphaned Lock | Process dies without releasing | Lock TTL (Time-To-Live) set to a maximum of 2 hours, automatically self-releasing. |
| VRAM Allocation Failure | PyTorch VRAM OOM | Release lock, tag MLflow run `FAILED`, raise `GPUOutOfMemoryException`. |
