# SPEC-011: Multimodal Ingestion Pipeline Specification

**Linked ADR:** [ADR-011](../adr/ADR-011-multimodal-ingestion-pipeline.md)  
**Status:** Approved  
**Date:** 2026-05-26  
**Bounded Context:** Ingestion / Automation  

## 1. Overview & Objectives

This specification defines the validation criteria for the `IngestionPort` composite architecture. It guarantees that files, web pages, audio, video streams, and tabular files are cleanly parsed into semantic text/markdown.

## 2. Invariants & Processing Rules

* **Invariant 1**: The final ingested output must be returned as a clean `IngestedContent` entity containing raw markdown text, title, and file metadata.
* **Invariant 2**: All media extraction (YouTube URLs or audio uploads) must output a transcoded, low-bitrate `.ogg` file before transcription is requested.
* **Invariant 3**: Tabular documents (Excel spreadsheets and CSV files) must be converted into valid Markdown table formatting.
* **Invariant 4**: Ingestion of image files must route the image to the out-of-process VLM endpoint and return a text description, never returning raw binary data.
* **Invariant 5**: Unsupported media formats must fail-fast with a mapped exception (`UnsupportedMediaTypeException`).

## 3. Test Strategy Classification

* **Unit Tests (Domain)**:
  - Scope: Test ingestion use cases using a mock `IngestionPort`.
* **Integration Tests (Adapter)**:
  - Scope: Test individual handlers in `InstructorMetadataExtractorAdapter` and `IngestionAdapter` against dummy test assets:
    - A dynamic React HTML mockup (checks static-to-dynamic fallback).
    - A dummy 3-row CSV file (checks Markdown table parsing).
    - A short wav file (checks ffmpeg command invocation and Whisper network integration).
    - A dummy PNG file (checks SGLang VLM API submission).

## 4. Acceptance Criteria (Scenarios)

### Scenario 1: Web Ingestion Fallback (Static -> Dynamic)
* **Given**: A URL pointing to a Javascript-only Single Page Application (SPA).
* **When**: Calling `ingest(url, "text/html")` on the port.
* **Then**: The static parser must execute first and return an empty or bootstrap-only string.
* **And**: The adapter must catch this and delegate execution to the dynamic Playwright adapter.
* **And**: Return the fully-rendered dynamic text content.

### Scenario 2: Audio Media Ingestion (Transcode and Transcribe)
* **Given**: A local path to an MP3 audio file.
* **When**: Calling `ingest(path, "audio/mp3")`.
* **Then**: The handler must execute a shell command invoking `ffmpeg` to transcode the file down to a temporary `.ogg` file.
* **And**: Post the `.ogg` file to the out-of-process Whisper server endpoint.
* **And**: Return the verified text transcription.
* **And**: Delete the temporary `.ogg` file.

### Scenario 3: Spreadsheets to Markdown Alignment
* **Given**: A spreadsheet containing two columns of text.
* **When**: Calling `ingest(path, "text/csv")`.
* **Then**: The handler must parse the columns and return the output aligned as:
  ```markdown
  | Header A | Header B |
  |----------|----------|
  | Cell 1A  | Cell 1B  |
  ```

### Scenario 4: Image Visual Ingestion (VLM Description)
* **Given**: A JPEG file containing a photo of a whiteboard diagram.
* **When**: Calling `ingest(path, "image/jpeg")`.
* **Then**: The image must be uploaded to the out-of-process model server VLM endpoint.
* **And**: Return a clean markdown description of the whiteboard diagram contents.

## 5. Boundary Conditions & Exception Mapping

| Parameter | Value | Expected Outcome |
|-----------|-------|------------------|
| Media Format | `video/wmv` | `UnsupportedMediaTypeException` |
| Binary File | Corrupted/Empty | `IngestionSourceCorruptException` |
| Ffmpeg Execution | Exit Code != 0 | `MediaProcessingException` |

## 6. Observability & Telemetry Assertions

* **Telemetry Metrics**:
  - Expose counter `isb_ingestion_attempts_total` labeled by format (`html`, `audio`, `table`, `image`).
  - Expose counter `isb_ingestion_failures_total` tracking ingestion processing errors.
* **Audit Logs**:
  - Log start of transcoding tasks with source format and file size.
  - Log any system subprocess command invocations (`ffmpeg`, `yt-dlp`) at `DEBUG` level.
