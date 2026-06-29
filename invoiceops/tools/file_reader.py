"""Input loading utilities."""

from __future__ import annotations

from pathlib import Path

from invoiceops.schemas import InputDocument


def load_input_documents(input_dir: str | Path) -> list[InputDocument]:
    root = Path(input_dir)
    documents: list[InputDocument] = []

    for path in sorted(root.glob("*.txt")):
        documents.append(
            InputDocument(
                source_file=path.name,
                path=path,
                raw_text=path.read_text(encoding="utf-8").strip(),
            )
        )

    return documents
