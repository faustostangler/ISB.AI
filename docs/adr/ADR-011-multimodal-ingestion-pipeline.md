# ADR-011: Multimodal Hexagonal Ingestion Pipeline with Local CUDA Acceleration

**Status:** Accepted  
**Date:** 2026-05-26  
**Decision Makers:** Lead Architect, High-Performance Implementer  

## Context

The Intelligent Second Brain (ISB.AI) is designed to process, index, and query a wide variety of information sources. In addition to standard static and dynamic web pages, users submit:
1. **YouTube URLs / Audio Streams**: Requiring video audio extraction, transcoding, and transcription.
2. **Tabular Data (CSV, Excel)**: Requiring structural mapping to ensure relational content is readable by semantic search models.
3. **Documents (PDF, Office files)**: Requiring layout extraction and text clean-up.
4. **Images**: Requiring visual content analysis.

Executing heavy processing pipelines natively within our core Python application process introduces major bottlenecks:
- Native execution of transcription models (Whisper) or visual models (VLMs) freezes the event loops and blocks the GIL, stalling the whole application.
- Processing files natively couples the business domain to unstable third-party binaries, rendering tools, and GPU drivers.

We need a flexible, unified architecture that handles multimodal formats, isolates execution dependencies, preserves local developer parity, and utilizes our workstation's NVIDIA RTX 2060 CUDA accelerator to execute heavy ML inference out-of-process.

## Decision

We will implement a unified `IngestionPort` in the application layer. The infrastructure layer will implement a composite adapter that dynamically routes ingestion tasks to specialized file and network adapters.

Specific implementation details:
1. **Application Interface**:
   ```python
   class IngestionPort(ABC):
       @abstractmethod
       async def ingest(self, source_url_or_path: str, mime_type: str) -> IngestedContent:
           pass
   ```
2. **Infrastructure Adapters Composite Pattern**:
   The adapter will dynamically inspect the mime-type and scheme, routing tasks to specialized handlers:
   - **`WebPageHandler`**: Attempts fast static scraping (`BeautifulSoup4`). If the DOM content is empty or requires dynamic rendering, it falls back to dynamic headless execution (`Playwright`).
   - **`YoutubeAndAudioHandler`**: Uses local `yt-dlp` and system `ffmpeg` (installed inside our non-root container stage) to extract and transcode media files down to low-bitrate `.ogg` formats. Transcoded audio is submitted asynchronously to our out-of-process CUDA-accelerated inference sidecar running Whisper.
   - **`DocumentHandler`**: Converts text documents (PDFs, Word files) to clean text. Tabular files (CSV, Excel) are rendered directly into Markdown tables to preserve structural alignments for our long-context DroPE embedding layer.
   - **`VisualHandler`**: Routes image files to the out-of-process CUDA sidecar for descriptive analysis using Vision-Language Models (VLMs).
3. **GIL & VRAM Isolation**:
   All heavy GPU workloads (Whisper transcription, VLM description, DroPE embedding) are executed asynchronously against our sidecar service running on the host's GPU (RTX 2060), protecting developer velocity and system stability.

## Consequences

### Positive
* **Rich Multimodal Processing**: Ingests, transcribes, and indexes files, audios, videos, and tables cleanly.
* **Format-Agnostic Domain**: The core domain use cases simply process clean markdown/text content, completely shielded from extraction libraries.
* **Preserves Structural Semantics**: Markdown representation of Excel/CSV files maintains structural associations, avoiding embedding fragmentation.
* **Isolates GPU Tasks**: Offloading Whisper and VLM processes to the external container preserves the stability of the main worker.

### Negative
* **Resource Demand**: Running local Playwright browsers, media transcoder sub-processes, and local inference models concurrently can strain system limits (managed by strict worker concurrency controls and local INT4 model quantization).

## Alternatives Considered

### Option A: Web Scraping Only
* **Pros:** Simpler container image and minimal codebase complexity.
* **Cons:** Fails to address the comprehensive multimodal requirements of ISB.AI (which includes YouTube downloads, PDFs, Office documents, Images, and raw audio files).
* **Why rejected:** It is an excellent starting point for basic web pages, but completely fails to support our core second brain capabilities (indexing media, documents, and spreadsheets).

### Option B: Web and Standard Document Parsing (No Media Integration)
* **Pros:** Avoids native system dependencies like `ffmpeg` and `yt-dlp`.
* **Cons:** Cannot extract text or transcribe audio and video streams (e.g. YouTube).
* **Why rejected:** YouTube and raw audio notes are critical components of the ingestion roadmap.

### Option C: In-Process Deep Learning Execution (Whisper / VLM)
* **Pros:** Avoids network communication overhead between container pods.
* **Cons:** Introduces severe domain pollution by bringing PyTorch, Whisper, and other heavy ML/GPU libraries into our core monolithic process context. It also risks event-loop blockages, GIL freezes, and worker process OOMs.
* **Why rejected:** Violates our strict domain isolation boundaries and threatens application server stability.

### Option D: Cloud-Only Multimodal Extraction (External API Dependencies)
* **Pros:** Zero local GPU resource usage or system binary requirements (`ffmpeg`).
* **Cons:** Violates our local self-containment invariants. It requires a permanent internet connection, exposes sensitive user documents to third-party endpoints, and has high operating latency.
* **Why rejected:** Fails our offline-first local workstation invariant.

### Option E: Multimodal Hexagonal Ingestion Pipeline with Local CUDA Acceleration
* **Pros:** Hardened multi-media capabilities via `ffmpeg`/`yt-dlp` encapsulated in our secure non-root image. Out-of-process CUDA acceleration via our inference sidecar protects the event loop and GIL while exploiting the local NVIDIA RTX 2060 GPU. Tabular documents are mapped to Markdown tables to preserve structural relations for DroPE embedding.
* **Cons:** Higher local resource demand (mitigated by strict concurrency controls and INT4 model quantization).
* **Why selected:** It combines local self-containment, domain cleanliness, high performance, and full multimodal capability.

## Compliance

- [x] Hexagonal Architecture layers respected
- [x] System binaries (`ffmpeg`) run under secure non-root profile
- [x] CUDA offloading abstracted behind application ports
- [x] Structured file representation (Markdown tables) enforced

## References

- Domain reference: `references/25-10 Automation, and Integration 1.md`, `references/26-10 Automation, and Integration 2.md`
- Layout reference: `references/project_layout.md`
