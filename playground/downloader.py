#!/usr/bin/env python3
"""YouTube downloader script using yt-dlp to extract audio as OGG or fetch structured subtitles directly."""

import html
import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

import yt_dlp


def find_subtitle_url(info: dict, preferred_ext: str) -> tuple[str, str] | None:
    """Search for a suitable subtitle or automatic caption URL matching the preferred extension.
    
    Prioritizes:
    1. pt-BR, pt-orig, pt, pt-PT, en, en-US in manual subtitles
    2. pt-BR, pt-orig, pt, pt-PT, en, en-US in automatic captions
    3. Any language code starting with 'pt' or 'en'
    4. Any language code at all that has the preferred format
    """
    subtitles = info.get("subtitles") or {}
    auto_caps = info.get("automatic_captions") or {}

    preferred_languages = ["pt-BR", "pt-orig", "pt", "pt-PT", "en", "en-US"]

    for source in (subtitles, auto_caps):
        # 1. Search in exact preference order
        for lang in preferred_languages:
            if lang in source:
                for fmt in source[lang]:
                    if fmt.get("ext") == preferred_ext:
                        return lang, fmt.get("url")

        # 2. Search for any key starting with 'pt' or 'en'
        for lang in source:
            if lang.startswith("pt") or lang.startswith("en"):
                for fmt in source[lang]:
                    if fmt.get("ext") == preferred_ext:
                        return lang, fmt.get("url")

        # 3. Search for any key at all that has the preferred format
        for lang in source:
            for fmt in source[lang]:
                if fmt.get("ext") == preferred_ext:
                    return lang, fmt.get("url")

    return None

def parse_json3_to_paragraphs(json3_url: str, silence_threshold_ms: int = 2000, punctuation_limit: int = 5) -> str:
    """Fetch JSON3 format subtitles and reconstruct them into clean paragraphs using time-gaps and punctuation counts."""
    req = urllib.request.Request(json3_url, headers={'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=10) as response:
        data = json.loads(response.read().decode('utf-8'))

    events = data.get("events", [])

    # Filter out layout/header events and append events
    text_events = []
    for event in events:
        if "segs" in event and not event.get("aAppend"):
            # Combine segment texts
            seg_text = "".join(seg.get("utf8", "") for seg in event["segs"]).strip()
            if seg_text:
                text_events.append({
                    "start": event["tStartMs"],
                    "duration": event["dDurationMs"],
                    "end": event["tStartMs"] + event["dDurationMs"],
                    "text": seg_text
                })

    if not text_events:
        return ""

    paragraphs = []
    current_paragraph_texts = []
    punc_count = 0

    max_end_so_far = text_events[0]["end"]
    current_paragraph_texts.append(text_events[0]["text"])

    # Count punctuation in the first chunk
    punc_count += len(re.findall(r'[.!?]', text_events[0]["text"]))

    for i in range(1, len(text_events)):
        curr = text_events[i]

        # Calculate silence gap
        gap = curr["start"] - max_end_so_far

        # Count punctuation in the current event text
        curr_punc = len(re.findall(r'[.!?]', curr["text"]))

        # Split paragraph if:
        # 1. Silence gap is >= silence_threshold_ms
        # 2. Accumulated punctuation in the current paragraph meets or exceeds the limit
        if gap >= silence_threshold_ms or punc_count >= punctuation_limit:
            paragraphs.append(" ".join(current_paragraph_texts))
            current_paragraph_texts = [curr["text"]]
            punc_count = curr_punc
        else:
            current_paragraph_texts.append(curr["text"])
            punc_count += curr_punc

        max_end_so_far = max(max_end_so_far, curr["end"])

    if current_paragraph_texts:
        paragraphs.append(" ".join(current_paragraph_texts))

    # Clean up multiple spaces and join paragraphs
    cleaned_paragraphs = []
    for p in paragraphs:
        p_clean = re.sub(r'\s+', ' ', p).strip()
        if p_clean:
            cleaned_paragraphs.append(p_clean)

    return "\n\n".join(cleaned_paragraphs)

def fetch_and_parse_srv1(url: str, punctuation_limit: int = 5) -> str:
    """Fetch the XML subtitle in srv1 format and extract text split into paragraphs based on punctuation count."""
    req = urllib.request.Request(
        url,
        headers={'User-Agent': 'Mozilla/5.0'}
    )
    with urllib.request.urlopen(req, timeout=10) as response:
        xml_data = response.read().decode('utf-8')

    root = ET.fromstring(xml_data)
    texts = []
    for child in root.findall('text'):
        t = child.text
        if t:
            # HTML entities like &quot; and &#39; need to be unescaped
            texts.append(html.unescape(t.strip()))

    raw_text = " ".join(texts)

    # Split raw_text into paragraphs of at most punctuation_limit punctuation marks
    words = raw_text.split()
    paragraphs = []
    current_paragraph = []
    punc_count = 0

    for word in words:
        current_paragraph.append(word)
        punc_count += len(re.findall(r'[.!?]', word))
        if punc_count >= punctuation_limit:
            paragraphs.append(" ".join(current_paragraph))
            current_paragraph = []
            punc_count = 0

    if current_paragraph:
        paragraphs.append(" ".join(current_paragraph))

    return "\n\n".join(p for p in paragraphs if p.strip())

def extract_video_metadata(url: str) -> dict:
    """Extract and return video metadata using yt-dlp."""
    ydl_opts_meta = {
        'quiet': True,
        'no_warnings': True,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }
    with yt_dlp.YoutubeDL(ydl_opts_meta) as ydl:
        return ydl.extract_info(url, download=False)

def get_youtube_audio_or_transcript(url: str, output_dir: str = ".", force_audio: bool = False, info: dict | None = None) -> tuple[str | None, str | None, str]:
    """Retrieve the transcript directly from YouTube subtitles if available (json3 paragraphs -> srv1 raw text).
    Otherwise, download the audio and convert it to OGG format for Whisper.

    Args:
        url: The YouTube video URL.
        output_dir: The directory where output files will be saved.
        force_audio: If True, skips subtitle checks and forces audio downloading.
        info: Optional pre-extracted yt-dlp metadata dictionary.

    Returns:
        A tuple of (transcript_text, ogg_file_path, video_id).
        One of transcript_text or ogg_file_path will be None.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    if not info:
        print(f"Extracting metadata for: {url}")
        info = extract_video_metadata(url)
    video_id = info.get("id", "unknown_video")
    title = info.get("title", "Unknown Title")

    # Try to get subtitles if not forced to download audio
    if not force_audio:
        # Tier 1: Try JSON3 for paragraphs
        sub_json3 = find_subtitle_url(info, "json3")
        if sub_json3:
            lang, sub_url = sub_json3
            print(f"JSON3 subtitles found ({lang}). Reconstructing paragraphs...")
            try:
                transcript = parse_json3_to_paragraphs(sub_url)
                if transcript.strip():
                    print(f"Successfully processed JSON3 paragraphs for '{title}'")
                    return transcript, None, video_id
                else:
                    print("Warning: Parsed JSON3 text was empty. Trying Tier 2 fallback.")
            except Exception as e:
                print(f"Warning: Failed to parse JSON3 subtitles ({e}). Trying Tier 2 fallback.")

        # Tier 2: Try SRV1 for raw text
        sub_srv1 = find_subtitle_url(info, "srv1")
        if sub_srv1:
            lang, sub_url = sub_srv1
            print(f"SRV1 subtitles found ({lang}). Extracting raw text...")
            try:
                transcript = fetch_and_parse_srv1(sub_url)
                if transcript.strip():
                    print(f"Successfully processed SRV1 text for '{title}'")
                    return transcript, None, video_id
                else:
                    print("Warning: Parsed SRV1 text was empty. Trying Tier 3 fallback.")
            except Exception as e:
                print(f"Warning: Failed to parse SRV1 subtitles ({e}). Trying Tier 3 fallback.")

    # Tier 3: Download audio and convert to OGG for Whisper
    print("No subtitles or captions could be retrieved. Downloading audio stream (Whisper fallback)...")

    ydl_opts_download = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'vorbis',
            'preferredquality': '192',
        }],
        'outtmpl': str(out_path / '%(id)s.%(ext)s'),
        'quiet': False,
        'no_warnings': False,
        "js_runtimes": {"node": {}, "deno": {}, "bun": {}},
        "remote_components": ["ejs:github"],
    }

    with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
        download_info = ydl.extract_info(url, download=True)
        video_id = download_info.get("id", video_id)
        ogg_file = out_path / f"{video_id}.ogg"

        print(f"Successfully downloaded and processed '{title}' as: {ogg_file}")
        return None, str(ogg_file.resolve()), video_id

if __name__ == "__main__":
    # Quick CLI invocation test if run directly
    url = sys.argv[1] if len(sys.argv) > 1 else None
    if not url:
        print("No YouTube URL provided via command line.")
        try:
            url = input("Enter YouTube URL (or press Enter to run test video): ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
            sys.exit(0)
        if not url:
            url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"
            print(f"Using default test URL: {url}")

    txt, ogg, vid = get_youtube_audio_or_transcript(url, output_dir="./downloads")
    if txt:
        print(f"\n--- SUBTITLES RETRIEVED (Video ID: {vid}) ---")
        print(txt[:500] + "\n...")
    else:
        print(f"\n--- AUDIO DOWNLOADED (Video ID: {vid}) ---")
        print(f"File path: {ogg}")
