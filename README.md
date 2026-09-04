# File Organizer

A command-line Python script that scans a folder and automatically sorts
its files into subfolders — either by file type (Images, Documents,
Videos, etc.) or by the file's last-modified month (YYYY-MM). Includes a
dry-run preview mode and a one-command undo.

## Features

- **Sort by type** — groups files into folders like `Images/`, `Documents/`,
  `Spreadsheets/`, `Code/`, `Archives/`, etc., based on file extension
- **Sort by date** — groups files into `YYYY-MM/` folders based on when
  they were last modified
- **Dry run** — preview exactly what would move before touching anything
- **Undo** — reverses the most recent run using a small JSON log, and
  cleans up any now-empty folders it created
- **Safe by default** — never overwrites a file; if a name collision
  occurs, it appends `(1)`, `(2)`, etc.
- No external dependencies — standard library only

## Getting Started

```bash
git clone <your-repo-url>
cd file_organizer
python organizer.py /path/to/folder --by type
```

## Usage

```bash
# Preview what would happen (recommended first run)
python organizer.py ~/Downloads --by type --dry-run

# Actually organize by file type
python organizer.py ~/Downloads --by type

# Organize by last-modified month instead
python organizer.py ~/Downloads --by date

# Undo the most recent run in that folder
python organizer.py ~/Downloads --undo
```

## How It Works

- Files are matched to a category by extension, using a dictionary that's
  easy to edit (`CATEGORY_MAP` in `organizer.py`). Anything unmatched goes
  into an `Other/` folder.
- Every real run writes a `.organizer_log.json` file recording each
  file's original and new location, which `--undo` reads to move
  everything back and remove the log.
- `--dry-run` never writes the log or touches the filesystem — it only
  prints what would happen.

## Project Structure

```
file_organizer/
├── organizer.py   # CLI, sorting logic, undo logic
└── README.md
```

## Possible Extensions

- Sort by file size (e.g., "Large files" bucket)
- Recursive mode to organize subfolders too
- A config file (JSON/YAML) for custom category rules instead of editing
  the script directly
- A `--watch` mode that auto-organizes a folder (e.g., Downloads) as new
  files arrive

## Author

Adebowale Ogungbesan
