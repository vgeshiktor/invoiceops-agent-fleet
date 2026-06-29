"""Parsers for the text-first invoice fixtures."""

from __future__ import annotations

from invoiceops.schemas import ExtractedInvoice, InputDocument


FIELD_ALIASES = {
    "document-type": "document_type",
    "vendor": "vendor",
    "invoice-number": "invoice_number",
    "receipt-number": "invoice_number",
    "invoice-date": "invoice_date",
    "receipt-date": "invoice_date",
    "currency": "currency",
    "total-amount": "total_amount",
    "vat-number": "vat_number",
}


def parse_structured_document(document: InputDocument) -> ExtractedInvoice | None:
    if document.document_type not in {"invoice", "receipt"}:
        return None

    values: dict[str, str] = {}

    for line in document.raw_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        alias = FIELD_ALIASES.get(key.strip().lower())
        if alias:
            values[alias] = value.strip()

    total_amount = values.get("total_amount")

    return ExtractedInvoice(
        source_file=document.source_file,
        document_type=document.document_type,
        vendor=values.get("vendor"),
        invoice_number=values.get("invoice_number"),
        invoice_date=values.get("invoice_date"),
        currency=values.get("currency"),
        total_amount=float(total_amount) if total_amount else None,
        vat_number=values.get("vat_number"),
    )
