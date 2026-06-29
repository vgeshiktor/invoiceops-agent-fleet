"""Extraction agent for normalized invoice data."""

from __future__ import annotations

from invoiceops.schemas import ExtractedInvoice, InputDocument
from invoiceops.tools.invoice_parser import parse_structured_document


class ExtractionAgent:
    def run(self, documents: list[InputDocument]) -> dict[str, ExtractedInvoice]:
        extracted: dict[str, ExtractedInvoice] = {}

        for document in documents:
            invoice = parse_structured_document(document)
            if invoice is not None:
                extracted[document.source_file] = invoice

        return extracted
