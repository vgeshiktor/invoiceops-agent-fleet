"""Artifact writers for the InvoiceOps MVP."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from invoiceops.schemas import InvoiceRecord


FORMULA_PREFIXES = ("=", "+", "-", "@")


def write_json(path: Path, invoices: list[InvoiceRecord]) -> None:
    path.write_text(
        json.dumps([invoice.model_dump(mode="json") for invoice in invoices], indent=2),
        encoding="utf-8",
    )


def write_review_queue(path: Path, invoices: list[InvoiceRecord]) -> None:
    review_queue = [invoice for invoice in invoices if invoice.status in {"needs_review", "rejected"}]
    path.write_text(
        json.dumps([invoice.model_dump(mode="json") for invoice in review_queue], indent=2),
        encoding="utf-8",
    )


def write_csv(path: Path, invoices: list[InvoiceRecord]) -> None:
    approved = [invoice for invoice in invoices if invoice.status == "approved"]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_file",
                "document_type",
                "vendor_name",
                "vendor_tax_id",
                "invoice_number",
                "invoice_date",
                "currency",
                "subtotal",
                "vat",
                "total",
            ],
        )
        writer.writeheader()
        for invoice in approved:
            writer.writerow(
                {
                    "source_file": _sanitize_csv_value(invoice.source_file),
                    "document_type": _sanitize_csv_value(invoice.document_type),
                    "vendor_name": _sanitize_csv_value(invoice.vendor_name),
                    "vendor_tax_id": _sanitize_csv_value(invoice.vendor_tax_id),
                    "invoice_number": _sanitize_csv_value(invoice.invoice_number),
                    "invoice_date": _sanitize_csv_value(invoice.invoice_date),
                    "currency": _sanitize_csv_value(invoice.currency),
                    "subtotal": invoice.subtotal,
                    "vat": invoice.vat,
                    "total": invoice.total,
                }
            )


def write_markdown_report(
    path: Path,
    invoices: list[InvoiceRecord],
    total_documents_scanned: int,
    accounting_export_filename: str = "accounting_export.csv",
) -> None:
    approved = [invoice for invoice in invoices if invoice.status == "approved"]
    needs_review = [invoice for invoice in invoices if invoice.status == "needs_review"]
    rejected = [invoice for invoice in invoices if invoice.status == "rejected"]
    security_flags = [invoice for invoice in invoices if invoice.risk_flags]

    lines = [
        "# InvoiceOps Exceptions Report",
        "",
        "## Summary",
        f"- Total documents scanned: {total_documents_scanned}",
        f"- Invoices approved: {len(approved)}",
        f"- Needs review: {len(needs_review)}",
        f"- Rejected: {len(rejected)}",
        "",
        "## Needs Review",
    ]

    if needs_review:
        for invoice in needs_review:
            lines.append(f"- {invoice.source_file}: {', '.join(invoice.issues)}")
    else:
        lines.append("- None")

    lines.extend(["", "## Rejected"])
    if rejected:
        for invoice in rejected:
            detail = ", ".join(invoice.risk_flags or invoice.issues or ["rejected"])
            lines.append(f"- {invoice.source_file}: {detail}")
    else:
        lines.append("- None")

    lines.extend(["", "## Security Flags"])
    if security_flags:
        for invoice in security_flags:
            lines.append(f"- {invoice.source_file}: {', '.join(invoice.risk_flags)}")
    else:
        lines.append("- None")

    lines.extend(
        [
            "",
            "## Accounting Export Created",
            f"- {accounting_export_filename} with {len(approved)} approved records",
            "",
        ]
    )

    path.write_text("\n".join(lines), encoding="utf-8")


def _sanitize_csv_value(value: str | None) -> str | None:
    if value is None:
        return None
    if value and (value[0] in FORMULA_PREFIXES or ord(value[0]) < 32):
        return "'" + value
    return value
