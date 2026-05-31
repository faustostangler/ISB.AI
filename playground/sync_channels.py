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

from downloader import get_youtube_audio_or_transcript, extract_video_metadata
from transcriber import transcribe_audio_to_text
from llm_processor import process_transcript_to_obsidian

# --- Configs ---
PLAYLIST_FILE = Path(__file__).parent / "playlist.txt"
CSV_FILE = Path(__file__).parent / "brain" / "wiki" / "log.md"
DEFAULT_OUTPUT_DIR = Path(__file__).parent / "brain" / "raw"

def load_historical_metadata(log_path: Path) -> tuple[set[str], set[str]]:
    """Load previously synced video IDs and channel IDs from the Markdown log file table.

    Returns:
        tuple[set[str], set[str]]: A tuple containing (synced_ids, synced_channels)
    """
    synced_ids = set()
    synced_channels = set()
    if log_path.exists():
        try:
            with open(log_path, encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line.startswith("|") and not "---" in line and not "Channel ID" in line:
                        parts = [p.strip() for p in line.split("|") if p.strip()]
                        if len(parts) >= 2:
                            synced_channels.add(parts[0])
                            synced_ids.add(parts[1])
        except Exception as e:
            print(f"Warning: Failed to load historical metadata from {log_path.name}: {e}")
    return synced_ids, synced_channels

def record_synced_video(log_path: Path, channel_id: str, video_id: str, upload_date: str, title: str = "Unknown Title") -> None:
    """Record a successfully synced video in the Markdown log table."""
    file_exists = log_path.exists()
    log_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(log_path, "a", encoding="utf-8") as f:
            if not file_exists:
                f.write("# Ingestion Log\n\n")
                f.write("| Channel ID | Video ID | Upload Date | Synced At | Title |\n")
                f.write("| --- | --- | --- | --- | --- |\n")
            synced_at = datetime.now(UTC).isoformat()
            clean_title = title.replace("|", "\\|")
            f.write(f"| {channel_id} | {video_id} | {upload_date} | {synced_at} | {clean_title} |\n")
        print(f"Recorded video {video_id} in {log_path.name}")
    except Exception as e:
        print(f"Error saving to Markdown log: {e}")

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

def sync_single_video(url: str, output_dir: Path, model_name: str, keep_audio: bool, info: dict | None = None) -> dict:
    """Process a single video using the 3-tier fallback model (JSON3 -> SRV1 -> Whisper OGG).
    
    Returns a dict containing:
        - text: the transcript text
        - title: the video title
        - video_id: the video ID
        - upload_date: the upload date (ISO or YYYYMMDD)
        - channel: the channel name
        - channel_id: the channel ID
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Fetch metadata first
    if not info:
        info = extract_video_metadata(url)
    video_id = info.get("id", "unknown_video")
    video_url = info.get("webpage_url", "unknown_url")
    title = info.get("title", "Unknown Title")
    upload_date = get_full_upload_date(info)
    channel = info.get("channel", "Unknown Channel")
    channel_id = info.get("channel_id", "unknown_channel")

    # print(f"\nProcessing video: {upload_date} {channel_id} {video_url} {title} ({video_id})")
    txt_path = output_dir / f"{video_id}.txt"

    # Check 3-tier downloader
    transcript_text, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(output_dir), info=info)

    if transcript_text:
        text = transcript_text.strip()
        # print("Transcript retrieved directly from subtitles.")
    else:
        # Fallback to Whisper
        if not ogg_path:
            # Re-fetch forcing download
            _, ogg_path, _ = get_youtube_audio_or_transcript(url, output_dir=str(output_dir), force_audio=True, info=info)

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

    return {
        "text": text,
        "title": title,
        "video_id": video_id,
        "upload_date": upload_date,
        "channel": channel,
        "channel_id": channel_id,
    }

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

def process_and_compile_video(
    url: str,
    output_dir: Path,
    csv_path: Path,
    model_name: str,
    keep_audio: bool,
    llm_model: str,
    ollama_url: str,
    channel_id: str | None,
    synced_ids: set[str],
    info: dict | None = None
) -> dict:
    """Download, transcribe, log, and compile a YouTube video to Obsidian."""
    res = sync_single_video(url, output_dir, model_name, keep_audio, info=info)
    actual_channel_id = channel_id or res["channel_id"]

    # Record to ingestion log
    record_synced_video(csv_path, actual_channel_id, res["video_id"], res["upload_date"], title=res["title"])
    synced_ids.add(res["video_id"])

    # Compile to Obsidian Note inside wiki/
    process_transcript_to_obsidian(
        video_id=res["video_id"],
        title=res["title"],
        channel=res["channel"],
        channel_id=actual_channel_id,
        upload_date=res["upload_date"],
        transcript_text=res["text"],
        model=llm_model,
        ollama_url=ollama_url,
        output_dir=output_dir.parent / "wiki"
    )
    return res

def sync_channels_and_seeds(
    days: int,
    output_dir: Path,
    model_name: str,
    keep_audio: bool,
    playlist_path: Path,
    csv_path: Path,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434"
) -> None:
    """Core synchronization execution flow."""
    # 1. Load synced video IDs and historical channels
    synced_ids, synced_channels = load_historical_metadata(csv_path)
    print(f"Loaded {len(synced_ids)} synced video IDs and {len(synced_channels)} synced channel IDs.")

    # 2. Read seed URLs from playlist.txt
    urls = read_playlist_urls(playlist_path)
    print(f"Found {len(urls)} seed URLs in {playlist_path.name}.")

    channels_to_scan = set(synced_channels)

    # 3. Process seed URLs and add their channels to our list
    for url in urls:
        print(f"\nAnalyzing seed URL: {url}")
        try:
            info = extract_video_metadata(url)
            video_id = info.get("id")
            video_url = info.get("webpage_url")
            title = info.get("title")
            channel_id = info.get("channel_id")
            upload_date = get_full_upload_date(info)
        except Exception as e:
            print(f"Error fetching metadata for seed URL {url}: {e}")
            continue

        print(f"{upload_date} | {channel_id} {video_url} | {title}")

        if channel_id:
            channels_to_scan.add(channel_id)

        # Process the seed video itself if it is within range and not yet synced
        if is_within_range(upload_date, days):
            if video_id not in synced_ids:
                # print("-> Seed video is within range and not synced. Syncing now...")
                try:
                    process_and_compile_video(
                        url=url,
                        output_dir=output_dir,
                        csv_path=csv_path,
                        model_name=model_name,
                        keep_audio=keep_audio,
                        llm_model=llm_model,
                        ollama_url=ollama_url,
                        channel_id=channel_id,
                        synced_ids=synced_ids,
                        info=info
                    )
                except Exception as e:
                    print(f"Error syncing seed video {video_id}: {e}")
            else:
                pass
                # print("-> Seed video is already synced.")
        else:
            print("-> Seed video falls outside the date range.")

    # 4. Scan all unique channels (both seed channels and historical ones)
    print(f"\nScanning total of {len(channels_to_scan)} channels for new uploads...")
    safe_limit = max(50, days * 30)
    for chan_id in channels_to_scan:
        recent_entries = fetch_channel_recent_videos(chan_id, limit=safe_limit)
        print(f"Found {len(recent_entries)} recent uploads on the channel.")

        for entry in recent_entries:
            entry_id = entry.get("id")
            entry_url = entry.get("url")
            entry_title = entry.get("title", "Unknown Title")
            entry_date = get_full_upload_date(entry)

            if is_within_range(entry_date, days):
                if entry_id not in synced_ids:
                    print(f"  + {entry_date} | {entry_url} | {entry_title}")
                    try:
                        process_and_compile_video(
                            url=entry_url,
                            output_dir=output_dir,
                            csv_path=csv_path,
                            model_name=model_name,
                            keep_audio=keep_audio,
                            llm_model=llm_model,
                            ollama_url=ollama_url,
                            channel_id=chan_id,
                            synced_ids=synced_ids
                        )
                    except Exception as e:
                        print(f"  Error syncing video {entry_id}: {e}")
                else:
                    pass
                    # print(f"  - Video already synced: {entry_title} ({entry_id})")

def bulk_compile_historical_transcripts(
    csv_path: Path,
    output_dir: Path,
    llm_model: str = "gemma4:e2b",
    ollama_url: str = "http://localhost:11434"
) -> None:
    """Scan the Markdown log file and compile any unprocessed video transcripts into Obsidian notes."""
    if not csv_path.exists():
        print(f"No historical sync log found at {csv_path}. Nothing to compile.")
        return

    print(f"Scanning {csv_path.name} for transcripts to compile...")

    wiki_dir = output_dir.parent / "wiki"
    wiki_dir.mkdir(parents=True, exist_ok=True)
    sources_dir = wiki_dir / "sources"
    sources_dir.mkdir(parents=True, exist_ok=True)

    rows = []
    try:
        with open(csv_path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line.startswith("|") and not "---" in line and not "Channel ID" in line:
                    parts = [p.strip() for p in line.split("|") if p.strip()]
                    if len(parts) >= 4:
                        title = parts[4] if len(parts) >= 5 else "Unknown Title"
                        rows.append((parts[0], parts[1], parts[2], title))
    except Exception as e:
        print(f"Error reading log table: {e}")
        return

    print(f"Found {len(rows)} entries in sync log.")
    compiled_count = 0

    for channel_id, video_id, upload_date, title in rows:
        source_note_path = sources_dir / f"{video_id}.md"
        if source_note_path.exists():
            continue

        txt_path = output_dir / f"{video_id}.txt"
        if not txt_path.exists():
            # Alternative check old downloads
            txt_path_alt = output_dir.parent.parent / "downloads" / f"{video_id}.txt"
            if txt_path_alt.exists():
                txt_path = txt_path_alt
            else:
                print(f"Warning: Transcript text file {txt_path} not found. Skipping.")
                continue

        try:
            with open(txt_path, encoding="utf-8") as f:
                transcript_text = f.read().strip()
        except Exception as e:
            print(f"Error reading transcript file {txt_path}: {e}")
            continue

        if not transcript_text:
            print(f"Warning: Transcript {txt_path} is empty. Skipping.")
            continue

        if title == "Unknown Title" or not title:
            print(f"Fetching title for video {video_id} to compile note...")
            channel = "Unknown Channel"
            try:
                info = extract_video_metadata(f"https://www.youtube.com/watch?v={video_id}")
                title = info.get("title", "Unknown Title")
                channel = info.get("channel", "Unknown Channel")
            except Exception as e:
                print(f"Warning: Could not fetch metadata for {video_id}: {e}. Using placeholders.")
        else:
            channel = "Unknown Channel"

        success = process_transcript_to_obsidian(
            video_id=video_id,
            title=title,
            channel=channel,
            channel_id=channel_id,
            upload_date=upload_date,
            transcript_text=transcript_text,
            model=llm_model,
            ollama_url=ollama_url,
            output_dir=wiki_dir
        )
        if success:
            compiled_count += 1

    print(f"\nBulk compilation finished. Successfully compiled {compiled_count} new notes.")

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

    args = parser.parse_args()
    
    output_path = Path(args.output_dir)

    if args.compile_only:
        bulk_compile_historical_transcripts(
            csv_path=Path(args.csv),
            output_dir=output_path,
            llm_model=args.ollama_model,
            ollama_url=args.ollama_url
        )
    else:
        sync_channels_and_seeds(
            days=args.days,
            output_dir=output_path,
            model_name=args.model,
            keep_audio=args.keep_audio,
            playlist_path=Path(args.playlist),
            csv_path=Path(args.csv),
            llm_model=args.ollama_model,
            ollama_url=args.ollama_url
        )

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nSync process aborted by user.")
        sys.exit(1)
