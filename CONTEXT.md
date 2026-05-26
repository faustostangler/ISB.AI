# Intelligent Second Brain (ISB.AI) Context

Centralized glossary and Ubiquitous Language definitions for the ISB.AI Modular Monolith. This context defines the business domain terminology and eliminates translation ambiguity across technical adapters and core services.

## Language

### Infrastructure & Ingress

**Ingress Proxy**:
The edge web server that terminates external SSL/TLS transport security, injects mandatory security headers, and routes incoming traffic.
_Avoid_: Web server, load balancer, API gateway, reverse proxy

**API Presentation**:
The HTTP interface routing layer (FastAPI) responsible for mapping incoming web requests into core application use cases.
_Avoid_: Backend, API routes, controller tier

**Infrastructure as Code**:
The practice of managing and provisioning computing infrastructure using machine-readable configuration files or programming code rather than manual processes.
_Avoid_: Provisioning scripts, manual setup, cloud scripts

**Pulumi Program**:
A Python application that uses the Pulumi SDK to declare the desired state of cloud resources, executing unit tests on configuration layouts before deployment.
_Avoid_: Deploy script, Terraform config, yaml files

### Task Orchestration

**Task Queue**:
The application boundary abstraction that accepts asynchronous jobs from use cases and schedules them for out-of-process completion.
_Avoid_: Celery, message broker, Dramatiq runner

**Background Worker**:
The dedicated host process thread context configured to consume and execute asynchronous tasks offloaded by the task queue.
_Avoid_: Worker node, thread executor, runner daemon

### Data & Persistence

**Parallel Run**:
The schema migration transition window where both the old and new structural data layouts are concurrently supported by the database and application nodes.
_Avoid_: Dual schema, live sync, double migration

**Backfill Job**:
A batched, throttled background database update task responsible for migrating historical records to new schema representations without locking tables.
_Avoid_: Migration script, SQL update, data copy

**Cache-Aside**:
The caching pattern where the application queries the cache first, loads from the database on a miss, and updates the cache dynamically.
_Avoid_: Lazy loading, read caching, inline caching

**Event-Driven Invalidation**:
The policy of clearing cached objects from memory immediately when state-modifying domain events are published on the application's local event bus.
_Avoid_: Cache clearing, TTL purge, manual delete

### Container Orchestration & Health

**Liveness Probe**:
The health check mechanism that allows the orchestration controller to determine if a container must be restarted.
_Avoid_: Heartbeat, crash detection, alive check

**Readiness Probe**:
The health check mechanism that determines if a container is ready to accept incoming network connections and process requests.
_Avoid_: Available check, service ping, routing test

**Resource Rightsizing**:
The engineering practice of declaring specific CPU and memory requests and limits based on observed utilization patterns to optimize node capacity and prevent starvation.
_Avoid_: Memory limits, CPU specs, instance sizing

### Software Release & Versioning

**Semantic Versioning**:
The release numbering practice that exposes a three-part version (MAJOR.MINOR.PATCH) to enforce API stability constraints and automate compatibility checks.
_Avoid_: Build counter, date stamp, release number

**Conventional Commits**:
A standardized commit message syntax that communicates the type of code change (e.g., fix, feat, chore) to enable programmatic version upgrades and automated changelog updates.
_Avoid_: Commit messages, git log, tag descriptions

### Model Validation & Evaluation

**Temporal Split**:
The data partitioning strategy that splits training and validation sets chronologically to prevent future information from leaking into the training phase.
_Avoid_: Random split, shuffle split, cross-fold split

**Macro F1-Score**:
An evaluation metric that calculates the F1-score for each class independently and then takes the unweighted average, treating all classes equally regardless of frequency.
_Avoid_: Accuracy score, micro-F1, overall precision

### Model Compression & Precision

**Weight Quantization**:
The process of compressing a model's floating-point weights (typically 16-bit) into lower-precision representations (such as 4-bit integers) to reduce memory usage and accelerate inference.
_Avoid_: Model compression, precision scaling, weight reduction

**FP8 Precision**:
An 8-bit floating-point format supported by modern GPU hardware that accelerates deep learning tensor computing while maintaining high model performance.
_Avoid_: Float8, byte float, low accuracy format

### Model Inference & Serving

**RadixAttention**:
The KV cache management algorithm that organizes cached token sequences in a Radix Tree structure, enabling automatic sharing and retrieval of prompt prefixes (system instructions, retrieved documents) across multiple requests.
_Avoid_: Prompt caching, prefix storage, context buffer

**KV Cache Hit Rate**:
The metric measuring the proportion of token prompt sequences resolved from previously cached key-value states in the Radix Tree without requiring GPU computation.
_Avoid_: Cache match, retrieval score, memory hit







