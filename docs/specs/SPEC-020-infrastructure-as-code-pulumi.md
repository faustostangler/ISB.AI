# SPEC-020: Infrastructure as Code (IaC) Tooling via Pulumi and Python Specification

**Linked ADR:** [ADR-020](../adr/ADR-020-infrastructure-as-code-pulumi.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Operations / Infrastructure  

## 1. Overview & Objectives

This specification details the testing guidelines for validating cloud resources declared inside our Pulumi Python application. By utilizing Pulumi's mock engine, we can assert security, tagging, and structure invariants using standard `pytest` tools, preventing invalid deployments before they reach the cloud provider.

## 2. Bounded Context & Domain Invariants

- **Component**: Pulumi Resource Declarations
  - Invariant 1: Cloud storage buckets (AWS S3, GCP GCS) must have public read/write access blocked.
  - Invariant 2: Network Security Groups must not expose SSH port 22 or Database ports (e.g., 5432) to `0.0.0.0/0` (public internet).
  - Invariant 3: All resources must possess a mandatory tag dictionary containing keys `Environment`, `Owner`, and `Project`.

## 3. Test Strategy Classification

- **Unit Tests (Pulumi Mocks)**:
  - Scope: Test class definitions and stack resource graphs.
  - Mock Boundary: Mock the Pulumi engine calls (`pulumi.runtime.set_mocks`) to simulate cloud provider returns, verifying resource structures in memory.
  - Command: `[ENV_EXEC] [TEST_EXEC] tests/infra/`

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Storage Bucket Security Invariant Verification
- **Given**: A Pulumi program declaring a storage bucket.
- **When**: Running the mock tests via `pytest`.
- **Then**: The test asserts that the bucket property `acl` is not set to `public-read` or `public-read-write`.
- **And**: The block public access settings are explicitly enabled (`block_public_acls=True`, `block_public_policy=True`).

### Scenario 2: Security Group Firewall Invariant Verification
- **Given**: A network configuration declaring database security groups.
- **When**: Mocking the stack resource evaluations.
- **Then**: No ingress rules permit traffic on port `5432` from CIDR range `0.0.0.0/0`.
- **And**: Ingress rules for port `22` are restricted to administrative CIDRs only.

### Scenario 3: Resource Tag Integrity Verification
- **Given**: Any declared cloud resource in the Pulumi graph.
- **When**: The resource configuration is parsed by the test runner.
- **Then**: The resource metadata must contain the tag keys `Environment`, `Owner`, and `Project` with non-empty string values.

## 5. Boundary Conditions & Exception Mapping

| Resource Checked | Configured Property | Expected Test Outcome |
|------------------|----------------------|-----------------------|
| S3 Bucket        | Public ACL           | AssertionError        |
| Security Group   | Port 22 open to all  | AssertionError        |
| EC2 Instance     | Missing 'Owner' tag  | AssertionError        |
| VPC              | Correct CIDR blocks  | Pass                  |

## 6. Observability & Telemetry Assertions

- **Pulumi Engine Policy**:
  - Assert that all warnings generated during resource compilation (e.g., deprecation warnings from cloud providers) are treated as errors in the CI/CD environment.
- **Audit Trails**:
  - Assert that Pulumi state updates log stack deployment metadata (such as the initiating Github Action run ID or user context) to the state lock manager.
