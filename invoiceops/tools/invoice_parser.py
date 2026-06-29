"""Parsers for local invoice fixtures."""

from __future__ import annotations

import json
import re

from invoiceops.schemas import DocumentType, InvoiceRecord


FIELD_ALIASES = {
    "vendor": "vendor_name",
    "vendor name": "vendor_name",
    "tax id": "vendor_tax_id",
    "vendor tax id": "vendor_tax_id",
    "invoice number": "invoice_number",
    "receipt number": "invoice_number",
    "date": "invoice_date",
    "invoice date": "invoice_date",
    "receipt date": "invoice_date",
    "currency": "currency",
    "subtotal": "subtotal",
    "vat": "vat",
    "total": "total",
    "document type": "document_type",
}


def parse_invoice_text(
    text: str,
    source_file: str,
    document_type: DocumentType = "invoice",
) -> InvoiceRecord:
    values = _parse_values(text)
    parsed_document_type = values.get("document_type") or document_type

    return InvoiceRecord(
        source_file=source_file,
        document_type=parsed_document_type if parsed_document_type in {"invoice", "receipt"} else document_type,
        vendor_name=_as_string(values.get("vendor_name")),
        vendor_tax_id=_as_string(values.get("vendor_tax_id")),
        invoice_number=_as_string(values.get("invoice_number")),
        invoice_date=_as_string(values.get("invoice_date")),
        currency=_as_string(values.get("currency")),
        subtotal=_as_float(values.get("subtotal")),
        vat=_as_float(values.get("vat")),
        total=_as_float(values.get("total")),
    )


def _parse_values(text: str) -> dict[str, object]:
    payload = _parse_json_payload(text)
    if payload is not None:
        return payload

    values: dict[str, object] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, raw_value = line.split(":", 1)
        normalized_key = FIELD_ALIASES.get(key.strip().lower())
        if normalized_key:
            values[normalized_key] = raw_value.strip()
    return values


def _parse_json_payload(text: str) -> dict[str, object] | None:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return None

    if not isinstance(payload, dict):
        return None

    values: dict[str, object] = {}
    for key, value in payload.items():
        normalized = FIELD_ALIASES.get(key.strip().lower().replace("_", " "))
        if normalized:
            values[normalized] = value
    return values


def _as_string(value: object) -> str | None:
    if value is None:
        return None
    string_value = str(value).strip()
    return string_value or None


def _as_float(value: object) -> float | None:
    if value in (None, ""):
        return None
    if isinstance(value, (int, float)):
        return float(value)

    normalized = str(value).strip()
    normalized = normalized.replace(",", "")
    normalized = re.sub(r"^[A-Za-z]{3}\s+", "", normalized)
    normalized = re.sub(r"^[^\d+-]+", "", normalized)

    if not normalized or not re.fullmatch(r"[-+]?\d+(?:\.\d+)?", normalized):
        return None
    return float(normalized)
