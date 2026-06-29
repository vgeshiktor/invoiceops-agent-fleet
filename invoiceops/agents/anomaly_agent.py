"""Anomaly agent for duplicate detection."""

from __future__ import annotations

from invoiceops.schemas import AnomalyFinding, ExtractedInvoice
from invoiceops.tools.duplicate_detector import detect_duplicates


class AnomalyAgent:
    def run(self, invoices: dict[str, ExtractedInvoice]) -> dict[str, list[AnomalyFinding]]:
        return detect_duplicates(list(invoices.values()))
