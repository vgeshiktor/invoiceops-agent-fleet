"""Duplicate and anomaly detection helpers."""

from __future__ import annotations

from collections import defaultdict

from invoiceops.schemas import AnomalyFinding, ExtractedInvoice


def detect_duplicates(invoices: list[ExtractedInvoice]) -> dict[str, list[AnomalyFinding]]:
    groups: dict[tuple[str, str], list[ExtractedInvoice]] = defaultdict(list)

    for invoice in invoices:
        if not invoice.vendor or not invoice.invoice_number:
            continue
        groups[(invoice.vendor.casefold(), invoice.invoice_number.casefold())].append(invoice)

    findings: dict[str, list[AnomalyFinding]] = {}

    for duplicate_group in groups.values():
        if len(duplicate_group) < 2:
            continue

        related_files = sorted(invoice.source_file for invoice in duplicate_group)
        message = (
            "Duplicate invoice number detected for vendor "
            f"{duplicate_group[0].vendor}: {duplicate_group[0].invoice_number}."
        )

        for invoice in duplicate_group:
            findings.setdefault(invoice.source_file, []).append(
                AnomalyFinding(
                    code="duplicate_invoice",
                    severity="medium",
                    message=message,
                    related_files=related_files,
                )
            )

    return findings
