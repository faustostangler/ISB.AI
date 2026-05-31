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
from downloader import get_youtube_audio_or_transcript
from transcriber import transcribe_audio_to_text


def run_single_video(url: str, output_dir: str, model_name: str, keep_audio: bool) -> None:
    """Run the complete pipeline for a single video: fetch subtitles or fallback to Whisper."""
    start_time = time.time()

    # 1. Try to fetch subtitles or download audio
    print("\n=== STEP 1: RETRIEVING SUBTITLES OR DOWNLOADING AUDIO ===")
    download_start = time.time()
    transcript_text, ogg_path, video_id = get_youtube_audio_or_transcript(url, output_dir=output_dir)
    download_duration = time.time() - download_start

    # Define text file path using the video ID
    txt_path = Path(output_dir) / f"{video_id}.txt"

    if transcript_text:
        # We got the subtitles directly!
        text = transcript_text.strip()
        print(f"Skipping Step 2: Subtitles fetched directly in {download_duration:.2f} seconds.")
    else:
        # We need to transcribe the downloaded OGG file
        if not ogg_path:
            print("Transcript text is empty or skipped, but no audio file is downloaded. Downloading audio stream now...")
            _, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=output_dir, force_audio=True)

        assert ogg_path and os.path.exists(ogg_path), f"Download verification failed. File not found: {ogg_path}"
        file_size_mb = os.path.getsize(ogg_path) / (1024 * 1024)
        print(f"Downloaded audio to {ogg_path} ({file_size_mb:.2f} MB) in {download_duration:.2f} seconds.")

        # 2. Transcribe
        print("\n=== STEP 2: TRANSCRIBING AUDIO TO TEXT VIA WHISPER ===")
        transcribe_start = time.time()
        result = transcribe_audio_to_text(ogg_path, model_name=model_name)
        transcribe_duration = time.time() - transcribe_start

        text = result.get("text", "").strip()
        print(f"Transcribed audio in {transcribe_duration:.2f} seconds.")

        # Clean up if requested
        if not keep_audio:
            print(f"\nCleaning up temporary audio file: {ogg_path}")
            try:
                os.remove(ogg_path)
                print("Audio file deleted successfully.")
            except Exception as e:
                print(f"Warning: Failed to delete audio file: {e}")

    # Inline assertion to verify we have non-empty text before writing
    assert len(text) > 0, "Transcription/Subtitle text is empty."

    # 3. Output results
    print("\n================ FINAL TEXT RESULT ================")
    print(text[:1000] + "\n...")
    print("====================================================")

    # Save transcription text to a file
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved text to: {txt_path}")

    total_duration = time.time() - start_time
    print(f"\nPipeline finished in {total_duration:.2f} seconds.")

def main() -> None:
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

    args = parser.parse_args()

    playlist_path = Path(args.playlist)
    csv_path = Path(args.csv)
    output_dir = Path(args.output_dir)

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
                csv_path=csv_path
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
        keep_audio=args.keep_audio
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
