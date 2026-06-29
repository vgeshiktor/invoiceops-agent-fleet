"""Anomaly agent for duplicate detection."""

from __future__ import annotations

from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.duplicate_detector import detect_duplicates


class AnomalyAgent:
    def run(self, invoices: list[InvoiceRecord]) -> list[InvoiceRecord]:
        return detect_duplicates(invoices)
