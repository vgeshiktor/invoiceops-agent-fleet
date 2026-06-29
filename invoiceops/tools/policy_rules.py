"""Policy evaluation helpers."""

from __future__ import annotations

from invoiceops.config import PolicyConfig
from invoiceops.schemas import ExtractedInvoice, PolicyFinding


def evaluate_policy(invoice: ExtractedInvoice, config: PolicyConfig) -> list[PolicyFinding]:
    findings: list[PolicyFinding] = []

    required_fields = ["vendor", "invoice_date", "currency", "total_amount"]
    if invoice.document_type == "invoice":
        required_fields.extend(["invoice_number", "vat_number"])

    for field_name in required_fields:
        if getattr(invoice, field_name) in {None, ""}:
            findings.append(
                PolicyFinding(
                    code=f"missing_{field_name}",
                    severity="medium",
                    message=f"Required field '{field_name}' is missing.",
                )
            )

    if invoice.vendor and invoice.vendor not in config.allowed_vendors:
        findings.append(
            PolicyFinding(
                code="vendor_not_allowlisted",
                severity="medium",
                message=f"Vendor '{invoice.vendor}' is not on the MVP allowlist.",
            )
        )

    if invoice.total_amount is not None and invoice.total_amount > config.max_invoice_total:
        findings.append(
            PolicyFinding(
                code="amount_threshold_exceeded",
                severity="medium",
                message=f"Invoice total {invoice.total_amount:.2f} exceeds the configured threshold.",
            )
        )

    return findings
