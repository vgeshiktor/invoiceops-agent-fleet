"""Policy evaluation helpers."""

from __future__ import annotations

from datetime import date

from invoiceops.config import PolicyConfig
from invoiceops.schemas import InvoiceRecord


def apply_policy(
    invoice: InvoiceRecord,
    config: PolicyConfig | None = None,
) -> InvoiceRecord:
    runtime_config = config or PolicyConfig()
    updated = invoice.model_copy(deep=True)

    if not updated.invoice_number:
        updated.add_issue("missing_invoice_number")
    if not updated.vendor_name:
        updated.add_issue("missing_vendor_name")
    if not updated.invoice_date:
        updated.add_issue("missing_invoice_date")
    if updated.total is None:
        updated.add_issue("missing_total")

    if (
        updated.document_type == "invoice"
        and updated.currency == "ILS"
        and updated.vat is None
    ):
        updated.add_issue("missing_vat")

    if updated.total is not None and updated.total <= 0:
        updated.add_issue("invalid_total")

    if (
        updated.currency == "ILS"
        and updated.total is not None
        and updated.total > runtime_config.max_total_ils
    ):
        updated.add_issue("amount_exceeds_limit")

    if updated.invoice_date:
        try:
            parsed_date = date.fromisoformat(updated.invoice_date)
        except ValueError:
            updated.add_issue("invalid_invoice_date")
        else:
            if parsed_date > date.today():
                updated.add_issue("date_in_future")

    updated.finalize_status()
    return updated
