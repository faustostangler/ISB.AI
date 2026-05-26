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

### Experiment Tracking & Model Registry

**Model Registry**:
The centralized repository service inside MLflow responsible for version control, promotion stages, tag management, and lineage tracking of candidate machine learning model weights.
_Avoid_: Weight store, model bucket, release list

**Experiment Tracking**:
The practice of logging parameters, code versions, metrics, and artifact outputs associated with each individual machine learning model training or validation run to ensure repeatability.
_Avoid_: Metric logging, execution logging, training stats

### Pipeline Orchestration

**Training Pipeline**:
The modular execution sequence (implemented as pure Python modules and executed via CLI or the asynchronous Task Queue) responsible for data loading, preprocessing, model cross-validation, evaluation, and registry promotion.
_Avoid_: DAG pipeline, workflow graph, Prefect flow, ZenML pipeline

### Model Monitoring & Drift

**Data Drift**:
The statistical divergence in the distribution of model input features (such as user notes, web scraps, or their embeddings) compared to the baseline training dataset.
_Avoid_: Feature shift, distribution skew, input drift

**Concept Drift**:
The degradation in model prediction accuracy and calibration over time, caused by changes in the underlying business domain relationship between inputs and targets.
_Avoid_: Model decay, performance drop, class shift

### Security & Vulnerability Scanning

**Dependency Auditing**:
The automated process of checking third-party application package lock manifests (such as `uv.lock`) for known security vulnerabilities prior to container image compilation.
_Avoid_: Library checking, package auditing, dependency verification

**Image Scanning**:
The static analysis process of inspecting container filesystem layers to identify security vulnerabilities, misconfigurations, and compliance violations in system packages.
_Avoid_: Docker check, container auditing, image testing

### Observability & Telemetry

**Telemetry Agent**:
The high-performance proxy service (running as a sidecar/gateway container) that receives, batches, filters, and routes metrics, logs, and traces from the application to backend monitoring platforms.
_Avoid_: Monitoring server, logging proxy, collector hub

**Context Propagation**:
The practice of injecting and extracting unique tracing identifiers (e.g. trace and span IDs) across process, network, and queue boundaries to correlate distributed transactions.
_Avoid_: ID passing, trace header routing, span linking

### Cloud & Hardware Allocation

**GPU Lock**:
A distributed concurrency lock (acquired via the `DistributedLockingPort`) that coordinates access to a physical GPU device, ensuring exclusive execution between model training pipelines and online inference sidecars to prevent memory starvation.
_Avoid_: Device key, GPU flag, VRAM blocker













