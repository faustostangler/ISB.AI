#!/usr/bin/env python3
"""Audio transcriber script using OpenAI Whisper."""

import os
from pathlib import Path

import whisper


def transcribe_audio_to_text(audio_path: str, model_name: str = "base") -> dict:
    """Transcribe an audio file to text using Whisper.

    Args:
        audio_path: Path to the audio file (e.g. .ogg).
        model_name: The Whisper model size/name to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').

    Returns:
        A dictionary containing the transcription text and other metadata segments.
    """
    path = Path(audio_path)
    if not path.exists():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")

    print(f"Loading Whisper model: {model_name}...")
    model = whisper.load_model(model_name)

    print(f"Transcribing audio file: {audio_path}...")
    result = model.transcribe(str(path), fp16=False)

    return result

if __name__ == "__main__":
    # Quick CLI invocation test if run directly
    import glob
    import sys

    audio_path = sys.argv[1] if len(sys.argv) > 1 else None
    if not audio_path:
        print("No audio file path provided via command line.")

        # Scan for existing audio files to make selection easy
        downloads_dir = Path(__file__).parent / "downloads"
        if not downloads_dir.exists():
            downloads_dir = Path("./downloads")

        files = []
        if downloads_dir.exists():
            for ext in ("*.ogg", "*.mp3", "*.wav", "*.m4a"):
                files.extend(glob.glob(str(downloads_dir / ext)))

        if files:
            print(f"Available audio files in {downloads_dir}:")
            for i, f in enumerate(files):
                print(f"  [{i}] {Path(f).name}")
            try:
                choice = input(f"Select file index (0-{len(files)-1}) or enter custom path: ").strip()
                if choice.isdigit() and 0 <= int(choice) < len(files):
                    audio_path = files[int(choice)]
                elif choice:
                    audio_path = choice
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)
        else:
            try:
                audio_path = input("Enter path to audio file: ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)

    if not audio_path or not os.path.exists(audio_path):
        print(f"Error: Invalid or non-existent audio file: {audio_path}")
        sys.exit(1)

    res = transcribe_audio_to_text(audio_path)
    print("\nTranscription Result:")
    print(res.get("text", ""))
