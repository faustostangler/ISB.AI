# EVAL-011: Multimodal Ingestion Whisper & VLM Rubric

**Linked SPEC:** [SPEC-011](./SPEC-011-multimodal-ingestion-pipeline.md)  
**Blocking Policy:** BLOCK (fails the pipeline on threshold breach)

## Dimensions

### 1. Transcription Accuracy (Whisper)
- **ADR Consequence**: ADR-011 Consequence 1 (Audio Transcription Quality)
- **Method**: Word Error Rate (WER) against a golden human-transcribed audio dataset.
- **Pass Threshold**: `WER <= 0.15` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-011-whisper.jsonl`

### 2. Visual Description Faithfulness (VLM)
- **ADR Consequence**: ADR-011 Consequence 4 (VLM Image Content Description)
- **Method**: LLM-as-judge comparing generated description correctness against key features in a visual golden test set.
- **Pass Threshold**: `score >= 0.80` (BLOCK)
- **Dataset**: `tests/evals/datasets/EVAL-011-vlm.jsonl`
