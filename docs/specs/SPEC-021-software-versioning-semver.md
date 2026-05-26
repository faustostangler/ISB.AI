# SPEC-021: Software Versioning and Automated Release Strategy via SemVer Specification

**Linked ADR:** [ADR-021](../adr/ADR-021-software-versioning-semver.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Platform & Operations / Release Engineering  

## 1. Overview & Objectives

This specification details the validation checks required to enforce Semantic Versioning (SemVer 2.0.0) constraints and Conventional Commit message rules across local developer workstations and CI/CD verification stages.

## 2. Bounded Context & Domain Invariants

- **Component**: SemVer Version Strings
  - Invariant 1: Any release version string must match the official SemVer regular expression pattern:
    `^(?P<major>0|[1-9]\d*)\.(?P<minor>0|[1-9]\d*)\.(?P<patch>0|[1-9]\d*)(?:-(?P<prerelease>(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+(?P<buildmetadata>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$`
- **Component**: Conventional Commit Message
  - Invariant 2: The git commit header must follow the structure: `<type>(<scope>): <description>` where `<type>` is restricted to `feat`, `fix`, `docs`, `style`, `refactor`, `perf`, `test`, `build`, `ci`, `chore`, or `revert`.
  - Invariant 3: Breaking changes must declare `BREAKING CHANGE:` in the commit body/footer or append `!` after the type/scope prefix.

## 3. Test Strategy Classification

- **Static Analysis (Commit Hooks & Linting)**:
  - Scope: Run commit message validation scripts (e.g., `commitlint` or equivalent python pre-commit script) locally and on Pull Request validations.
- **Unit Tests (Version Increment Logic)**:
  - Scope: Verify custom parser logic that reads Git tags and commit histories to calculate the next version bump target.

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Commit Header Conformance
- **Given**: A developer executes `git commit -m "<message>"`.
- **When**: The message starts with a valid type (e.g., `feat(api): add health route`).
- **Then**: The commit hook succeeds and accepts the commit.

### Scenario 2: Commit Header Violation
- **Given**: A developer executes `git commit -m "<message>"`.
- **When**: The message violates the type or syntax (e.g., `git commit -m "added a cool database query"` or `git commit -m "feat: missing colon"`).
- **Then**: The commit hook fails, rejects the commit, and displays a format instruction message.

### Scenario 3: Automated Version Bump Calculation
- **Given**: The current release tag is `1.2.3`.
- **When**: Analyzing the commit range since the last tag:
  - Commit list contains `fix(worker): handle connection failure`
  - Commit list contains `feat(api): expose new ready check`
- **Then**: The computed next version must be `1.3.0` (minor bump due to the presence of `feat`).
- **And**: If any commit contains `BREAKING CHANGE: config file changed`, the next version must be `2.0.0` (major bump).

## 5. Boundary Conditions & Exception Mapping

| Commit Message Input | Evaluated Release Type | Next Version Result (from `1.2.3`) |
|----------------------|------------------------|-------------------------------------|
| `fix: fix typo`      | `PATCH`                | `1.2.4`                             |
| `feat(api): query`   | `MINOR`                | `1.3.0`                             |
| `feat!: drop python` | `MAJOR`                | `2.0.0`                             |
| `chore: update deps` | `NONE`                 | No release triggered                |

## 6. Observability & Telemetry Assertions

- **CI/CD Build Invariants**:
  - Assert that tag extraction returns a valid SemVer string before publishing Docker images.
  - Assert that all published artifacts (e.g., wheel packages, OpenAPI specs) carry the identical SemVer version tag corresponding to the Git release tag.
