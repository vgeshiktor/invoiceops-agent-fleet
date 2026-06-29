"""Input loading utilities."""

from __future__ import annotations

from pathlib import Path


SUPPORTED_EXTENSIONS = {".txt", ".md", ".json"}


def list_input_files(input_dir: str | Path) -> list[Path]:
    root = Path(input_dir)
    return sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def read_document(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8").strip()
