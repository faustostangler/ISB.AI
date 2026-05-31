#!/usr/bin/env python3
"""Disk Diagnosis Tool - Scans home directory for space-eating files and caches."""

import os
import sys
from pathlib import Path

# Paths to scan
HOME = Path.home()
EXCLUDE_DIR = HOME / "gamer_d"
REPORT_PATH = Path(__file__).parent / "diagnosis_report.md"

def get_dir_size(path: Path) -> int:
    """Recursively calculate directory size in bytes, skipping symlinks and gamer_d."""
    total = 0
    try:
        for entry in os.scandir(path):
            if entry.is_symlink():
                continue
            entry_path = Path(entry.path)
            if entry_path == EXCLUDE_DIR:
                continue
            if entry.is_dir(follow_symlinks=False):
                total += get_dir_size(entry_path)
            else:
                total += entry.stat().st_size
    except (PermissionError, FileNotFoundError):
        pass
    return total

def format_size(size_bytes: int) -> str:
    """Format bytes to human readable format."""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} PB"

def run_diagnosis():
    print("Starting disk diagnosis of home directory...")
    print(f"Scanning {HOME} (excluding {EXCLUDE_DIR})...")
    
    report = []
    report.append("# Disk Space Diagnosis Report")
    report.append(f"Generated on: {os.popen('date').read().strip()}")
    report.append(f"Target: `{HOME}` (Excluding: `{EXCLUDE_DIR}`)\n")
    
    # 1. Check partition usage
    df_output = os.popen('df -h /home').read().strip()
    report.append("## Partition Disk Usage (`df -h /home`)")
    report.append(f"```text\n{df_output}\n```\n")
    
    # 2. Scan standard cache directories
    report.append("## Known Cache Directory Sizes")
    caches = {
        "UV Cache": HOME / ".uv_cache",
        "NPM Cache": HOME / ".npm",
        "Pip Cache": HOME / ".cache/pip",
        "Hugging Face Cache": HOME / ".cache/huggingface",
        "Ollama Models (default local path)": HOME / ".ollama",
        "Cargo/Rust Registry": HOME / ".cargo",
        "Antigravity IDE app data (Antigravity logs/caches)": HOME / ".gemini",
        "Standard user cache folder (~/.cache)": HOME / ".cache"
    }
    
    for name, path in caches.items():
        if path.exists():
            size = get_dir_size(path)
            report.append(f"- **{name}** (`{path}`): **{format_size(size)}**")
        else:
            report.append(f"- **{name}** (`{path}`): _Not Found_")
    report.append("")

    # 3. Find top 15 largest directories in HOME (ignoring gamer_d)
    report.append("## Top 15 Largest Home Subdirectories (excluding gamer_d)")
    dir_sizes = []
    try:
        for entry in os.scandir(HOME):
            entry_path = Path(entry.path)
            if entry_path == EXCLUDE_DIR or entry_path.is_symlink():
                continue
            if entry.is_dir(follow_symlinks=False):
                print(f"Scanning subdirectory: {entry_path.name}...")
                size = get_dir_size(entry_path)
                dir_sizes.append((entry_path, size))
    except Exception as e:
        report.append(f"Error listing subdirectories: {e}")
        
    dir_sizes.sort(key=lambda x: x[1], reverse=True)
    for path, size in dir_sizes[:15]:
        report.append(f"- `{path.relative_to(HOME)}`: **{format_size(size)}**")
    report.append("")

    # 4. Find top 20 largest files in HOME (excluding gamer_d)
    report.append("## Top 20 Largest Files (excluding gamer_d)")
    large_files = []
    
    # Recursively find large files, skipping gamer_d
    def scan_for_large_files(path: Path):
        try:
            for entry in os.scandir(path):
                entry_path = Path(entry.path)
                if entry_path == EXCLUDE_DIR or entry.is_symlink():
                    continue
                if entry.is_dir(follow_symlinks=False):
                    scan_for_large_files(entry_path)
                else:
                    size = entry.stat().st_size
                    if size > 10 * 1024 * 1024:  # > 10MB
                        large_files.append((entry_path, size))
        except (PermissionError, FileNotFoundError):
            pass
            
    print("Scanning for large files...")
    scan_for_large_files(HOME)
    large_files.sort(key=lambda x: x[1], reverse=True)
    
    for file_path, size in large_files[:20]:
        report.append(f"- `{file_path.relative_to(HOME)}`: **{format_size(size)}**")
    report.append("")

    # 5. Check if Docker is taking space
    docker_check = os.popen('docker system df 2>/dev/null').read().strip()
    if docker_check:
        report.append("## Docker Disk Usage (`docker system df`)")
        report.append(f"```text\n{docker_check}\n```\n")
        
    # Write report file
    try:
        with open(REPORT_PATH, "w", encoding="utf-8") as f:
            f.write("\n".join(report))
        print(f"\nDiagnosis complete. Report saved to: {REPORT_PATH}")
    except Exception as e:
        print(f"Error saving report: {e}")

if __name__ == "__main__":
    run_diagnosis()
