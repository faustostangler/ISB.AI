#!/usr/bin/env python3
"""Personalized Disk Cleanup Tool - Custom tailored based on diagnosis_report.md findings."""

import os
import sys
from pathlib import Path

REPORT_PATH = Path(__file__).parent / "diagnosis_report.md"
HOME = Path.home()

def print_header(title: str):
    print("\n" + "=" * 55)
    print(f" {title.center(53)} ")
    print("=" * 55)

def execute_command(cmd: str):
    """Safely run shell command and print outcome."""
    print(f"\nExecuting: {cmd}")
    res = os.system(cmd)
    if res == 0:
        print(">>> Success!")
    else:
        print(f">>> Failed (Exit code: {res})")

def run_cleanup():
    if not REPORT_PATH.exists():
        print("Error: diagnosis_report.md not found. Please run diagnose.py first.")
        sys.exit(1)

    print_header("STARTING NON-INTERACTIVE CLEANUP")

    # Action 1: Docker volumes (Safe & High Yield)
    print("\n--- Cleaning Docker Volumes ---")
    execute_command("docker volume prune -f")

    # Action 2: Whisper Cache
    whisper_dir = HOME / ".cache/whisper"
    if whisper_dir.exists():
        print("\n--- Cleaning Whisper Models Cache ---")
        execute_command(f"rm -f {whisper_dir}/large-v3.pt")
        execute_command(f"rm -f {whisper_dir}/medium.pt")
        execute_command(f"rm -f {whisper_dir}/small.pt")

    # Action 3: Hugging Face cache
    hf_dir = HOME / ".cache/huggingface"
    if hf_dir.exists():
        print("\n--- Cleaning Hugging Face Cache ---")
        execute_command(f"rm -rf {hf_dir}")

    # Action 4: NPM cache
    npm_dir = HOME / ".npm"
    if npm_dir.exists():
        print("\n--- Cleaning NPM Cache ---")
        execute_command("npm cache clean --force")

    # Action 5: Antigravity app logs and caches (Commented out to keep files)
    # print("\n--- Cleaning Antigravity logs (Skipped/Commented) ---")
    # gemini_dir = HOME / ".gemini"
    # if gemini_dir.exists():
    #     execute_command(f"find {gemini_dir} -name '*.log' -delete")

    # Action 6: Sudo journal logs vacuuming
    print("\n--- Vacuuming Journalctl Logs ---")
    execute_command("sudo journalctl --vacuum-time=2d")

    print_header("CLEANUP COMPLETE")
    print("Cleanup run finished. You can run python3 diagnose.py again to check your freed space.")
    print("Note: For the SQLite databases and model files in your Documents folder, please check them manually.")

if __name__ == "__main__":
    try:
        run_cleanup()
    except KeyboardInterrupt:
        print("\nCleanup aborted.")
        sys.exit(0)
