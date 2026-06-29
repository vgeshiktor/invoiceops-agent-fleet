"""Input loading utilities."""

from __future__ import annotations

from pathlib import Path


DEFAULT_SUPPORTED_EXTENSIONS = (".txt", ".md", ".json")


def list_input_files(
    input_dir: str | Path,
    supported_extensions: tuple[str, ...] = DEFAULT_SUPPORTED_EXTENSIONS,
) -> list[Path]:
    root = Path(input_dir)
    allowed_extensions = {extension.lower() for extension in supported_extensions}
    return sorted(
        path
        for path in root.iterdir()
        if path.is_file() and path.suffix.lower() in allowed_extensions
    )


def read_document(path: str | Path) -> str:
    return Path(path).read_text(encoding="utf-8").strip()
