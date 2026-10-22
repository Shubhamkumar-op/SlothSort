
from pathlib import Path
from datetime import datetime
import hashlib


IGNORED_FOLDERS = {
    ".venv",
    ".venv_broken",
    ".pytest_cache",
    "__pycache__",
    ".git",
    "Code",
    "Documents",
    "Images",
    "Archives",
    "Videos",
    "Audio",
    "Other",
}

IGNORED_FILES = {
    "slothsort_audit.jsonl",
}


def calculate_file_hash(file_path: Path) -> str:
    """Calculate SHA-256 hash without loading the entire file into memory."""
    sha256 = hashlib.sha256()

    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            sha256.update(chunk)

    return sha256.hexdigest()


def scan_folder(folder_path: str) -> list[dict]:
    """Scan eligible files without following symlinks or internal folders."""
    root = Path(folder_path).expanduser().resolve(strict=True)

    if not root.is_dir():
        raise NotADirectoryError(f"Not a directory: {root}")

    results = []

    for current_folder, folder_names, file_names in __import__("os").walk(root):
        current_path = Path(current_folder)

        folder_names[:] = [
            name
            for name in folder_names
            if name not in IGNORED_FOLDERS
            and not (current_path / name).is_symlink()
        ]

        for name in file_names:
            path = current_path / name

            try:
                if name in IGNORED_FILES:
                    continue

                if path.is_symlink() or not path.is_file():
                    continue

                stat = path.stat()

                results.append({
                    "name": path.name,
                    "extension": path.suffix.lower() or "[no extension]",
                    "relative_path": str(path.relative_to(root)),
                    "size_bytes": stat.st_size,
                    "modified_time": datetime.fromtimestamp(
                        stat.st_mtime
                    ).isoformat(timespec="seconds"),
                })

            except (OSError, ValueError) as error:
                results.append({
                    "name": path.name,
                    "relative_path": str(path),
                    "error": str(error),
                })

    return results
