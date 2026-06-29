"""Intake agent for document loading, classification, and security scanning."""

from __future__ import annotations

from pathlib import Path

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import InputDocument
from invoiceops.tools.file_reader import load_input_documents
from invoiceops.tools.security_scanner import detect_document_type, scan_security_findings


class IntakeAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def run(self, input_dir: str | Path) -> list[InputDocument]:
        documents = load_input_documents(input_dir)

        for document in documents:
            document.document_type = detect_document_type(document.raw_text)
            document.security_findings = scan_security_findings(
                document.raw_text,
                self._config.security,
            )
            document.is_suspicious = any(
                finding.code == "prompt_injection" for finding in document.security_findings
            )
            document.is_relevant = document.document_type in {"invoice", "receipt"}

            if any(finding.code == "irrelevant_content" for finding in document.security_findings):
                document.document_type = "irrelevant"
                document.is_relevant = False

        return documents
