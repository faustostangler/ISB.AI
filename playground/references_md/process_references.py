#!/usr/bin/env python3
"""Script to process, rename, and move reference markdown files grouped by set name."""

import re
from collections import defaultdict
from pathlib import Path

# --- Config ---
REFERENCES_DIR = Path("/home/stangler/gamer_d/Fausto Stangler/Documentos/Python/ISB.AI/docs/references")
SEPARATOR = "--------------------------------------------------------------------------------"

def main():
    print(f"Scanning directory: {REFERENCES_DIR}")

    # 1. Find all matching files at the top level of the references folder
    groups = defaultdict(list)
    for p in REFERENCES_DIR.glob("*.md"):
        match = re.match(r"^(\d+)-", p.name)
        if match:
            num = int(match.group(1))
            # Get renamed name without the leading 'x-'
            renamed_filename = re.sub(r"^\d+-", "", p.name)
            # Set name without the ' xx.md' ending
            set_name = re.sub(r"\s+\d{2}\.md$", "", renamed_filename)

            groups[set_name].append({
                "num": num,
                "path": p,
                "renamed_filename": renamed_filename,
                "set_name": set_name
            })

    if not groups:
        print("No files found to process at the top level of references directory!")
        return

    print(f"Found {len(groups)} distinct sets to process:")
    for set_name, files in groups.items():
        print(f"  Set: '{set_name}' ({len(files)} files)")

    # 2. Process each set independently
    for set_name, files_in_group in groups.items():
        print(f"\n--- Processing Set: {set_name} ---")

        # Sort files in group by their starting number
        files_in_group.sort(key=lambda x: x["num"])

        # Load files and split by separator
        files_articles = []
        original_total_articles = 0
        for item in files_in_group:
            p = item["path"]
            content = p.read_text(encoding="utf-8")
            articles = content.split(SEPARATOR)
            original_total_articles += len(articles)
            print(f"  File {p.name}: {len(articles)} articles found.")
            files_articles.append({
                "item": item,
                "articles": articles
            })

        # Re-organize (shift last article to the start of the next file)
        for i in range(len(files_articles) - 1):
            last_article = files_articles[i]["articles"].pop()
            files_articles[i+1]["articles"][0] = last_article + files_articles[i+1]["articles"][0]

        # Verify article counts
        new_total_articles = sum(len(f["articles"]) for f in files_articles)
        expected_articles = original_total_articles - (len(files_in_group) - 1)
        assert new_total_articles == expected_articles, (
            f"Set '{set_name}': Expected {expected_articles} articles, but got {new_total_articles}"
        )

        # Write new files
        original_paths_to_delete = []
        for f_art in files_articles:
            item = f_art["item"]
            old_path = item["path"]

            # Create target folder
            target_dir = REFERENCES_DIR / item["set_name"]
            target_dir.mkdir(parents=True, exist_ok=True)
            new_path = target_dir / item["renamed_filename"]

            # Join articles and write
            new_content = SEPARATOR.join(f_art["articles"])
            new_path.write_text(new_content, encoding="utf-8")
            print(f"    Saved: {new_path.relative_to(REFERENCES_DIR.parent.parent)}")

            assert new_path.exists(), f"Target file {new_path} does not exist after writing!"
            original_paths_to_delete.append(old_path)

        # Clean up original files for this set
        print("  Cleaning up original files for this set...")
        for old_path in original_paths_to_delete:
            old_path.unlink()
            print(f"    Deleted original: {old_path.name}")

    print("\nAll sets processed successfully!")

if __name__ == "__main__":
    main()
