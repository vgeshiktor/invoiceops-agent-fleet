"""Intake agent for document loading, classification, and security scanning."""

from __future__ import annotations

from pathlib import Path

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import DocumentCandidate
from invoiceops.tools.file_reader import list_input_files, read_document
from invoiceops.tools.security_scanner import detect_document_type, scan_for_prompt_injection


class IntakeAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def run(self, input_dir: str | Path) -> list[DocumentCandidate]:
        documents: list[DocumentCandidate] = []

        for path in list_input_files(input_dir):
            raw_text = read_document(path)
            document_type = detect_document_type(raw_text, self._config.security)
            risk_flags = scan_for_prompt_injection(raw_text, self._config.security)
            documents.append(
                DocumentCandidate(
                    source_file=path.name,
                    path=path,
                    raw_text=raw_text,
                    document_type=document_type,
                    risk_flags=risk_flags,
                )
            )

        return documents
