"""Artifact writers for the InvoiceOps MVP."""

from __future__ import annotations

import csv
import json
from pathlib import Path

from invoiceops.schemas import ExtractedInvoice, ReviewItem


def write_review_queue(path: Path, review_items: list[ReviewItem]) -> None:
    path.write_text(
        json.dumps([item.to_dict() for item in review_items], indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_invoices_json(path: Path, invoices: list[ExtractedInvoice]) -> None:
    path.write_text(
        json.dumps([invoice.to_dict() for invoice in invoices], indent=2, sort_keys=True),
        encoding="utf-8",
    )


def write_accounting_export(path: Path, invoices: list[ExtractedInvoice]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle,
            fieldnames=[
                "source_file",
                "document_type",
                "vendor",
                "invoice_number",
                "invoice_date",
                "currency",
                "total_amount",
                "vat_number",
            ],
        )
        writer.writeheader()
        for invoice in invoices:
            writer.writerow(invoice.to_dict())


def write_exceptions_report(path: Path, review_items: list[ReviewItem]) -> None:
    lines = ["# Exceptions Report", ""]

    for item in review_items:
        if item.recommended_status == "approve" and not item.export_blocked:
            continue

        lines.append(f"## {item.source_file}")
        lines.append(f"- Recommended status: {item.recommended_status}")
        lines.append(f"- Export blocked: {'yes' if item.export_blocked else 'no'}")

        for finding in item.security_findings:
            lines.append(f"- Security: {finding.code} ({finding.severity}) - {finding.message}")
        for finding in item.policy_findings:
            lines.append(f"- Policy: {finding.code} ({finding.severity}) - {finding.message}")
        for finding in item.anomaly_findings:
            lines.append(f"- Anomaly: {finding.code} ({finding.severity}) - {finding.message}")

        if item.invoice:
            lines.append(
                f"- Parsed invoice: {item.invoice.vendor or 'unknown vendor'} / "
                f"{item.invoice.invoice_number or 'no invoice number'}"
            )

        lines.append("")

    if len(lines) == 2:
        lines.extend(["No exceptions detected.", ""])

    path.write_text("\n".join(lines), encoding="utf-8")
