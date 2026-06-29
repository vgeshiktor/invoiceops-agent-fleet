"""Extraction agent for normalized invoice data."""

from __future__ import annotations

from invoiceops.schemas import DocumentCandidate, InvoiceRecord
from invoiceops.tools.invoice_parser import parse_invoice_text


class ExtractionAgent:
    def run(self, documents: list[DocumentCandidate]) -> list[InvoiceRecord]:
        return [
            parse_invoice_text(document.raw_text, document.source_file, document.document_type)
            for document in documents
            if document.is_invoice_like
        ]
