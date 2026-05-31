#!/usr/bin/env python3
"""YouTube Channel Video Syncer script.

Downloads new videos uploaded within the last X days from channels listed in playlist.txt.
Maintains idempotency via a CSV log file.
"""

import argparse
import csv
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import yt_dlp

# Ensure we can import downloader and transcriber modules from the current directory
sys.path.append(str(Path(__file__).parent))

from downloader import get_youtube_audio_or_transcript
from transcriber import transcribe_audio_to_text

# --- Configs ---
PLAYLIST_FILE = Path(__file__).parent / "playlist.txt"
CSV_FILE = Path(__file__).parent / "videos.csv"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "downloads"

def load_synced_video_ids(csv_path: Path) -> set[str]:
    """Load previously synced video IDs from the CSV file.
    
    Expects columns: channel_id, video_id, upload_date, synced_at
    """
    synced_ids = set()
    if csv_path.exists():
        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    pass
                for row in reader:
                    if len(row) > 1:
                        # video_id is the second column (index 1)
                        synced_ids.add(row[1])
        except Exception as e:
            print(f"Warning: Failed to load {csv_path}: {e}")
    return synced_ids

def load_historical_channels(csv_path: Path) -> set[str]:
    """Load previously synced channel IDs from the CSV file.
    
    Expects columns: channel_id, video_id, upload_date, synced_at
    """
    channel_ids = set()
    if csv_path.exists():
        try:
            with open(csv_path, encoding="utf-8") as f:
                reader = csv.reader(f)
                try:
                    next(reader)  # Skip header
                except StopIteration:
                    pass
                for row in reader:
                    if len(row) > 0 and row[0].strip():
                        # channel_id is the first column (index 0)
                        channel_ids.add(row[0].strip())
        except Exception as e:
            print(f"Warning: Failed to load channels from {csv_path}: {e}")
    return channel_ids

def record_synced_video(csv_path: Path, channel_id: str, video_id: str, upload_date: str) -> None:
    """Record a successfully synced video ID in the CSV file using standard columns.
    
    Columns: channel_id, video_id, upload_date, synced_at
    """
    file_exists = csv_path.exists()
    try:
        with open(csv_path, "a", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["channel_id", "video_id", "upload_date", "synced_at"])
            writer.writerow([
                channel_id,
                video_id,
                upload_date,
                datetime.now(UTC).isoformat()
            ])
        print(f"Recorded video {video_id} in {csv_path.name}")
    except Exception as e:
        print(f"Error saving to CSV: {e}")

def read_playlist_urls(file_path: Path) -> list[str]:
    """Read seed video URLs from a text file, skipping comments and blank lines."""
    urls = []
    if file_path.exists():
        with open(file_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    urls.append(line)
    return urls

def fetch_channel_recent_videos(channel_id: str, limit: int = 50) -> list[dict]:
    """Query recent videos from a channel using its uploads playlist ID."""
    if not channel_id.startswith("UC"):
        print(f"Warning: Channel ID '{channel_id}' does not match standard UC prefix. Fetching videos page directly.")
        url = f"https://www.youtube.com/channel/{channel_id}/videos"
    else:
        # Swap UC to UU to target the channel's uploads playlist directly
        uploads_playlist_id = "UU" + channel_id[2:]
        url = f"https://www.youtube.com/playlist?list={uploads_playlist_id}"

    print(f"Querying channel uploads for ID: {channel_id}")
    print(f"Fetching recent channel videos from uploads list: {url}")

    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "playlistend": limit,
        "extract_flat": True,
        "extractor_args": {"youtubetab": {"approximate_date": [""]}},
        "ignoreerrors": True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            playlist_info = ydl.extract_info(url, download=False)
            if playlist_info:
                # Filter out None values from failed extractions
                entries = [e for e in playlist_info.get("entries", []) if e]
                return entries
        except Exception as e:
            print(f"Error fetching channel playlist: {e}")
    return []

def get_full_upload_date(info: dict) -> str:
    """Retrieve full upload date if available (ISO timestamp), falling back to YYYYMMDD."""
    timestamp = info.get("timestamp")
    if timestamp:
        try:
            return datetime.fromtimestamp(timestamp, tz=UTC).isoformat()
        except Exception:
            pass
    return info.get("upload_date", "")

def sync_single_video(url: str, output_dir: Path, model_name: str, keep_audio: bool) -> tuple[str | None, str | None, str, str]:
    """Process a single video using the 3-tier fallback model (JSON3 -> SRV1 -> Whisper OGG).
    
    Returns:
        A tuple of (transcript_text, title, video_id, upload_date).
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch metadata first
    ydl_opts = {
        "quiet": True,
        "no_warnings": True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        video_id = info.get("id", "unknown_video")
        title = info.get("title", "Unknown Title")
        upload_date = get_full_upload_date(info)

    print(f"\nProcessing video: {title} ({video_id})")
    txt_path = output_dir / f"{video_id}.txt"

    # Check 3-tier downloader
    transcript_text, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(output_dir))

    if transcript_text:
        text = transcript_text.strip()
        print("Transcript retrieved directly from subtitles.")
    else:
        # Fallback to Whisper
        if not ogg_path:
            # Re-fetch forcing download
            _, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(output_dir), force_audio=True)

        assert ogg_path and os.path.exists(ogg_path), f"Audio file not found: {ogg_path}"
        print(f"Transcribing audio file with Whisper (model: {model_name})...")
        result = transcribe_audio_to_text(ogg_path, model_name=model_name)
        text = result.get("text", "").strip()

        # Clean up
        if not keep_audio:
            try:
                os.remove(ogg_path)
                print("Cleaned up OGG file.")
            except Exception as e:
                print(f"Warning: Failed to delete OGG file: {e}")

    # Save the text
    assert len(text) > 0, "No text extracted."
    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(text)
    print(f"Saved text to: {txt_path}")

    return text, title, video_id, upload_date

def is_within_range(upload_date_str: str, days_limit: int) -> bool:
    """Check if the upload date string falls within the last X days.
    
    Supports both ISO format (YYYY-MM-DD...) and standard YYYYMMDD.
    """
    if not upload_date_str:
        return False
    try:
        if "-" in upload_date_str:
            clean_str = upload_date_str.split("T")[0]
            upload_date = datetime.strptime(clean_str, "%Y-%m-%d").replace(tzinfo=UTC)
        else:
            upload_date = datetime.strptime(upload_date_str, "%Y%m%d").replace(tzinfo=UTC)

        threshold_date = datetime.now(UTC) - timedelta(days=days_limit)
        return upload_date >= threshold_date
    except Exception:
        return False

def sync_channels_and_seeds(
    days: int,
    output_dir: Path,
    model_name: str,
    keep_audio: bool,
    playlist_path: Path,
    csv_path: Path
) -> None:
    """Core synchronization execution flow."""
    # 1. Load synced video IDs and historical channels
    synced_ids = load_synced_video_ids(csv_path)
    historical_channels = load_historical_channels(csv_path)
    print(f"Loaded {len(synced_ids)} synced video IDs and {len(historical_channels)} historical channels.")

    # 2. Read seed URLs from playlist.txt
    urls = read_playlist_urls(playlist_path)
    print(f"Found {len(urls)} seed URLs in {playlist_path.name}.")

    channels_to_scan = set(historical_channels)

    # 3. Process seed URLs and add their channels to our list
    for url in urls:
        print(f"\nAnalyzing seed URL: {url}")
        ydl_opts = {
            "quiet": True,
            "no_warnings": True,
            "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
            "remote_components": ["ejs:github"],
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=False)
            except Exception as e:
                print(f"Error fetching metadata for seed URL {url}: {e}")
                continue

            video_id = info.get("id")
            title = info.get("title")
            channel_id = info.get("channel_id")
            channel = info.get("channel", "Unknown Channel")
            upload_date = get_full_upload_date(info)

        print(f"Seed Video ID: {video_id}")
        print(f"Title: {title}")
        print(f"Channel: {channel} ({channel_id})")
        print(f"Upload Date: {upload_date}")

        if channel_id:
            channels_to_scan.add(channel_id)

        # Process the seed video itself if it is within range and not yet synced
        if is_within_range(upload_date, days):
            if video_id not in synced_ids:
                print("-> Seed video is within range and not synced. Syncing now...")
                try:
                    _, _, vid, udate = sync_single_video(url, output_dir, model_name, keep_audio)
                    record_synced_video(csv_path, channel_id, vid, udate)
                    synced_ids.add(vid)
                except Exception as e:
                    print(f"Error syncing seed video {video_id}: {e}")
            else:
                print("-> Seed video is already synced.")
        else:
            print("-> Seed video falls outside the date range.")

    # 4. Scan all unique channels (both seed channels and historical ones)
    print(f"\nScanning total of {len(channels_to_scan)} channels for new uploads...")
    safe_limit = max(50, days * 10)
    for chan_id in channels_to_scan:
        recent_entries = fetch_channel_recent_videos(chan_id, limit=safe_limit)
        print(f"Found {len(recent_entries)} recent uploads on the channel.")

        for entry in recent_entries:
            entry_id = entry.get("id")
            entry_title = entry.get("title", "Unknown Title")
            entry_date = get_full_upload_date(entry)

            if is_within_range(entry_date, days):
                if entry_id not in synced_ids:
                    print(f"  + New video found: {entry_title} ({entry_id}) - Date: {entry_date}")
                    video_url = f"https://www.youtube.com/watch?v={entry_id}"
                    try:
                        _, _, vid, udate = sync_single_video(video_url, output_dir, model_name, keep_audio)
                        record_synced_video(csv_path, chan_id, vid, udate)
                        synced_ids.add(vid)
                    except Exception as e:
                        print(f"  Error syncing video {entry_id}: {e}")
                else:
                    print(f"  - Video already synced: {entry_title} ({entry_id})")

def main() -> None:
    parser = argparse.ArgumentParser(
        description="YouTube Channel Video Syncer - Sync videos in a date range."
    )
    parser.add_argument(
        "--days",
        type=int,
        default=7,
        help="Number of days range of videos to sync (default: 7)."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(DEFAULT_OUTPUT_DIR),
        help="Directory to save output files (default: './downloads')."
    )
    parser.add_argument(
        "--model",
        type=str,
        default="tiny",
        help="Whisper model name to use for fallback: tiny, base, etc. (default: 'tiny')."
    )
    parser.add_argument(
        "--keep-audio",
        action="store_true",
        help="Keep the downloaded OGG audio file if Whisper runs."
    )
    parser.add_argument(
        "--playlist",
        type=str,
        default=str(PLAYLIST_FILE),
        help="Path to playlist seed URLs text file."
    )
    parser.add_argument(
        "--csv",
        type=str,
        default=str(CSV_FILE),
        help="Path to CSV persistence log."
    )

    args = parser.parse_args()

    sync_channels_and_seeds(
        days=args.days,
        output_dir=Path(args.output_dir),
        model_name=args.model,
        keep_audio=args.keep_audio,
        playlist_path=Path(args.playlist),
        csv_path=Path(args.csv)
    )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSync process aborted by user.")
        sys.exit(1)
