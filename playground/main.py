#!/usr/bin/env python3
"""Main orchestrator script to download/transcribe single YouTube videos or sync entire channels."""

import argparse
import os
import sys
import time
from pathlib import Path

# Add the current directory to sys.path to ensure local module imports work seamlessly
sys.path.append(str(Path(__file__).parent))

import sync_channels
from sync_channels import sync_single_video
from downloader import get_youtube_audio_or_transcript
from transcriber import transcribe_audio_to_text
from llm_processor import process_transcript_to_obsidian


def run_single_video(
    url: str,
    output_dir: str,
    model_name: str,
    keep_audio: bool,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434"
) -> None:
    """Run the complete pipeline for a single video: fetch subtitles or fallback to Whisper."""
    start_time = time.time()

    print("\n=== STEP 1: RETRIEVING SUBTITLES OR DOWNLOADING AUDIO ===")
    res = sync_single_video(url, Path(output_dir), model_name, keep_audio)

    # 4. Compile to Obsidian Note via LLM
    print("\n=== STEP 2: COMPILING OBSIDIAN NOTE VIA OLLAMA LLM ===")
    notes_dir = Path(output_dir).parent / "wiki"
    process_transcript_to_obsidian(
        video_id=res["video_id"],
        title=res["title"],
        channel=res["channel"],
        channel_id=res["channel_id"],
        upload_date=res["upload_date"],
        transcript_text=res["text"],
        model=llm_model,
        ollama_url=ollama_url,
        output_dir=notes_dir
    )

    total_duration = time.time() - start_time
    print(f"\nPipeline finished in {total_duration:.2f} seconds.")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Download and transcribe YouTube videos or synchronize channels from playlist.txt."
    )
    parser.add_argument(
        "url",
        type=str,
        nargs="?",
        default=None,
        help="The URL of a specific YouTube video to process (optional; runs in Channel Syncer mode if omitted)."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days range of videos to sync in Channel Syncer mode (default: 7)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(sync_channels.DEFAULT_OUTPUT_DIR),
        help="Directory to save output files (default: './downloads')."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="Whisper model name to use: tiny, base, small, medium, large (default: 'tiny')."
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded OGG audio file after transcription (default: False/delete)."
    )
    parser.add_argument(
        "--playlist",
        type=str,
        default=str(sync_channels.PLAYLIST_FILE),
        help="Path to playlist seed URLs text file."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(sync_channels.CSV_FILE),
        help="Path to CSV persistence log."
    )
    parser.add_argument(
        "--ollama-model",
        type=str,
        default="gemma4:e2b",
        help="Ollama model to use for Obsidian note generation (default: 'gemma4:e2b')."
    )
    parser.add_argument(
        "--ollama-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API URL (default: 'http://localhost:11434')."
    )
    parser.add_argument(
        "--compile-only",
        action="store_true",
        help="Run bulk compilation on all historical synced transcripts without downloading new videos."
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    playlist_path = Path(args.playlist)
    csv_path = Path(args.csv)
    output_dir = Path(args.output_dir)

    if args.compile_only:
        print("Running in Compile Only Mode...")
        sync_channels.bulk_compile_historical_transcripts(
            csv_path=csv_path,
            output_dir=output_dir,
            llm_model=args.ollama_model,
            ollama_url=args.ollama_url
        )
        return

    url = args.url
    if not url:
        # Check if playlist.txt contains seed URLs
        playlist_urls = []
        if playlist_path.exists():
            playlist_urls = sync_channels.read_playlist_urls(playlist_path)

        if playlist_urls:
            print("Running in Sync Channels Mode...")
            sync_channels.sync_channels_and_seeds(
                days=args.days,
                output_dir=output_dir,
                model_name=args.model,
                keep_audio=args.keep_audio,
                playlist_path=playlist_path,
                csv_path=csv_path,
                llm_model=args.ollama_model,
                ollama_url=args.ollama_url
            )
            return
        else:
            print("No YouTube URL specified via command line, and playlist.txt is empty.")
            try:
                url = input("Enter YouTube URL (or press Enter to run default test video): ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting.")
                sys.exit(0)
            if not url:
                url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
                print(f"Using default test URL: {url}")

    # Run single video pipeline
    run_single_video(
        url=url,
        output_dir=str(output_dir),
        model_name=args.model,
        keep_audio=args.keep_audio,
        llm_model=args.ollama_model,
        ollama_url=args.ollama_url
    )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProcess aborted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
