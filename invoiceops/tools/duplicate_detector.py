"""Duplicate and anomaly detection helpers."""

from __future__ import annotations

from collections import defaultdict

from invoiceops.schemas import InvoiceRecord


def detect_duplicates(invoices: list[InvoiceRecord]) -> list[InvoiceRecord]:
    updated = [invoice.model_copy(deep=True) for invoice in invoices]
    by_invoice_number: dict[str, list[InvoiceRecord]] = defaultdict(list)
    by_vendor_amount_date: dict[tuple[str, float, str], list[InvoiceRecord]] = defaultdict(list)

    for invoice in updated:
        if invoice.invoice_number:
            by_invoice_number[invoice.invoice_number.casefold()].append(invoice)
        if invoice.vendor_name and invoice.total is not None and invoice.invoice_date:
            key = (invoice.vendor_name.casefold(), invoice.total, invoice.invoice_date)
            by_vendor_amount_date[key].append(invoice)

        if (
            invoice.subtotal is not None
            and invoice.vat is not None
            and invoice.total is not None
            and round(invoice.subtotal + invoice.vat, 2) != round(invoice.total, 2)
        ):
            invoice.add_issue("vat_math_mismatch")

    for group in list(by_invoice_number.values()) + list(by_vendor_amount_date.values()):
        if len(group) < 2:
            continue
        for invoice in group:
            invoice.add_issue("duplicate_invoice")

    for invoice in updated:
        invoice.finalize_status()

    return updated
