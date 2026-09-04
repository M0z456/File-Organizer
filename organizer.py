"""
File Organizer
--------------
Scans a folder and sorts files into subfolders, either by file type
(Images, Documents, Videos, etc.) or by the date the file was last
modified (YYYY-MM). Supports a dry-run preview and an undo command
that reverses the most recent run using a JSON log.

Usage:
    python organizer.py <folder> --by type
    python organizer.py <folder> --by date
    python organizer.py <folder> --by type --dry-run
    python organizer.py <folder> --undo
"""

import argparse
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

LOG_FILENAME = ".organizer_log.json"

# Extension -> category mapping. Extend this dict to fit your needs.
CATEGORY_MAP = {
    "Images": {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".heic"},
    "Documents": {".pdf", ".doc", ".docx", ".txt", ".md", ".rtf", ".odt"},
    "Spreadsheets": {".xls", ".xlsx", ".csv", ".ods"},
    "Presentations": {".ppt", ".pptx", ".key", ".odp"},
    "Videos": {".mp4", ".mov", ".avi", ".mkv", ".webm"},
    "Audio": {".mp3", ".wav", ".flac", ".aac", ".m4a"},
    "Archives": {".zip", ".rar", ".7z", ".tar", ".gz"},
    "Code": {".py", ".js", ".html", ".css", ".java", ".c", ".cpp", ".json", ".sh"},
    "Installers": {".exe", ".msi", ".dmg", ".pkg", ".deb"},
}


def category_for_extension(ext):
    """Return the category folder name for a given file extension."""
    ext = ext.lower()
    for category, extensions in CATEGORY_MAP.items():
        if ext in extensions:
            return category
    return "Other"


def month_folder_for_file(path):
    """Return a YYYY-MM string based on the file's last-modified time."""
    timestamp = path.stat().st_mtime
    return datetime.fromtimestamp(timestamp).strftime("%Y-%m")


def unique_destination(dest_folder, filename):
    """
    Avoid overwriting files with the same name: if 'photo.jpg' already
    exists, try 'photo (1).jpg', 'photo (2).jpg', etc.
    """
    dest = dest_folder / filename
    if not dest.exists():
        return dest

    stem, suffix = Path(filename).stem, Path(filename).suffix
    counter = 1
    while True:
        candidate = dest_folder / f"{stem} ({counter}){suffix}"
        if not candidate.exists():
            return candidate
        counter += 1


def scan_files(folder):
    """Return top-level files in folder, skipping the log file and hidden files."""
    return [
        f for f in folder.iterdir()
        if f.is_file() and f.name != LOG_FILENAME and not f.name.startswith(".")
    ]


def organize(folder, mode="type", dry_run=False):
    folder = Path(folder).expanduser().resolve()
    if not folder.is_dir():
        print(f"Error: '{folder}' is not a valid directory.")
        sys.exit(1)

    files = scan_files(folder)
    if not files:
        print("No files to organize — folder is empty or already sorted.")
        return

    moves = []  # list of (original_path, new_path) for the undo log

    for file_path in files:
        if mode == "type":
            subfolder_name = category_for_extension(file_path.suffix)
        elif mode == "date":
            subfolder_name = month_folder_for_file(file_path)
        else:
            raise ValueError(f"Unknown mode: {mode}")

        dest_folder = folder / subfolder_name
        dest_path = unique_destination(dest_folder, file_path.name)

        if dry_run:
            print(f"[dry run] {file_path.name}  ->  {subfolder_name}/{dest_path.name}")
            continue

        dest_folder.mkdir(exist_ok=True)
        shutil.move(str(file_path), str(dest_path))
        moves.append({"from": str(file_path), "to": str(dest_path)})
        print(f"Moved: {file_path.name}  ->  {subfolder_name}/{dest_path.name}")

    if dry_run:
        print(f"\nDry run complete. {len(files)} file(s) would be moved. "
              f"Re-run without --dry-run to apply.")
        return

    if moves:
        log_path = folder / LOG_FILENAME
        with open(log_path, "w") as f:
            json.dump(moves, f, indent=2)
        print(f"\nOrganized {len(moves)} file(s). Run with --undo to reverse this.")


def undo(folder):
    folder = Path(folder).expanduser().resolve()
    log_path = folder / LOG_FILENAME

    if not log_path.exists():
        print("No previous run found to undo (no log file in this folder).")
        return

    with open(log_path) as f:
        moves = json.load(f)

    restored = 0
    for move in reversed(moves):
        src, dest = Path(move["to"]), Path(move["from"])
        if src.exists():
            dest.parent.mkdir(exist_ok=True)
            shutil.move(str(src), str(dest))
            restored += 1
            print(f"Restored: {src.name} -> {dest}")
        else:
            print(f"Skipped (already moved or missing): {src}")

    # Clean up empty category folders created by the last run
    for move in moves:
        parent = Path(move["to"]).parent
        if parent.exists() and not any(parent.iterdir()):
            parent.rmdir()

    log_path.unlink()
    print(f"\nUndo complete. Restored {restored} file(s).")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Organize files in a folder by type or by modified date."
    )
    parser.add_argument("folder", help="Path to the folder you want to organize")
    parser.add_argument(
        "--by", choices=["type", "date"], default="type",
        help="Sort by file type (default) or by modified-date (YYYY-MM)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Preview the moves without actually moving any files"
    )
    parser.add_argument(
        "--undo", action="store_true",
        help="Reverse the most recent organize run in this folder"
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if args.undo:
        undo(args.folder)
    else:
        organize(args.folder, mode=args.by, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
