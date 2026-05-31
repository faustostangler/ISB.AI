#!/usr/bin/env python3
"""Main orchestrator script to download a YouTube video as OGG and transcribe it using Whisper."""

import argparse
import os
import sys
import time
from pathlib import Path

# Add the current directory to sys.path to ensure local module imports work seamlessly
sys.path.append(str(Path(__file__).parent))

from downloader import get_youtube_audio_or_transcript
from transcriber import transcribe_audio_to_text

def run(url: str, output_dir: str, model_name: str, keep_audio: bool) -> None:
    """Run the complete pipeline: fetch subtitles directly or fallback to downloading OGG and transcribing via Whisper."""
    start_time = time.time()
    
    # 1. Try to fetch subtitles or download audio
    print("\n=== STEP 1: RETRIEVING SUBTITLES OR DOWNLOADING AUDIO ===")
    download_start = time.time()
    transcript_text, ogg_path, video_id = get_youtube_audio_or_transcript(url, output_dir=output_dir)
    download_duration = time.time() - download_start
    
    # Define text file path using the video ID
    txt_path = Path(output_dir) / f"{video_id}.txt"
    
    # xxxfsxxx my debug (uncomment to force Whisper fallback debugging)
    transcript_text = ''
    if transcript_text:
        # We got the subtitles directly!
        text = transcript_text.strip()
        print(f"Skipping Step 2: Subtitles fetched directly in {download_duration:.2f} seconds.")
    else:
        # We need to transcribe the downloaded OGG file
        if not ogg_path:
            # print("Transcript text is empty or skipped, but no audio file is downloaded. Downloading audio stream now...")
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
                # os.remove(ogg_path)
                print("Audio file deleted successfully.")
            except Exception as e:
                print(f"Warning: Failed to delete audio file: {e}")
                
    # Inline assertion to verify we have non-empty text before writing
    assert len(text) > 0, "Transcription/Subtitle text is empty."
    
    # 3. Output results
    print("\n================ FINAL TEXT RESULT ================")
    print(text)
    print("====================================================")
    
    # Save transcription text to a file
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved text to: {txt_path}")
    
    total_duration = time.time() - start_time
    print(f"\nPipeline finished in {total_duration:.2f} seconds.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download a YouTube video as OGG audio and transcribe it to text using Whisper."
    )
    parser.add_argument(
        "url",
        type=str,
        nargs="?",
        default=None,
        help="The URL of the YouTube video to process (optional; will prompt if omitted)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./downloads",
        help="Directory to save output files (default: './downloads')."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="base",
        help="Whisper model name to use: tiny, base, small, medium, large (default: 'tiny')."
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded OGG audio file after transcription (default: False/delete)."
    )
    
    args = parser.parse_args()
    
    url = args.url
    if not url:
        print("No YouTube URL specified via command line.")
        try:
            url = input("Enter YouTube URL (or press Enter to run test video): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
        if not url:
            url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
            print(f"Using default test URL: {url}")
            
    try:
        run(
            url=url,
            output_dir=args.output_dir,
            model_name=args.model,
            keep_audio=args.keep_audio
        )
    except KeyboardInterrupt:
        print("\nProcess interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
