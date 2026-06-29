"""Restricted local-file server for the InvoiceOps MVP."""

from __future__ import annotations

from pathlib import Path

from invoiceops.tools.file_reader import DEFAULT_SUPPORTED_EXTENSIONS, read_document


class LocalFilesServer:
    def __init__(self, input_root: str | Path, output_root: str | Path) -> None:
        self.input_root = Path(input_root).resolve()
        self.output_root = Path(output_root).resolve()

    def list_documents(self) -> list[str]:
        allowed_extensions = {extension.lower() for extension in DEFAULT_SUPPORTED_EXTENSIONS}
        return sorted(
            path.name
            for path in self.input_root.iterdir()
            if path.is_file() and path.suffix.lower() in allowed_extensions
        )

    def read_document(self, relative_path: str) -> str:
        path = self._resolve_under(self.input_root, relative_path)
        return read_document(path)

    def write_output(self, relative_path: str, content: str) -> Path:
        path = self._resolve_under(self.output_root, relative_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return path

    @staticmethod
    def _resolve_under(root: Path, relative_path: str) -> Path:
        candidate = (root / relative_path).resolve()
        if candidate != root and root not in candidate.parents:
            raise ValueError(f"Path escapes sandbox root: {relative_path}")
        return candidate
