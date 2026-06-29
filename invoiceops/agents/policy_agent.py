"""Policy agent for rule checks."""

from __future__ import annotations

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import ExtractedInvoice, PolicyFinding
from invoiceops.tools.policy_rules import evaluate_policy


class PolicyAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def run(self, invoices: dict[str, ExtractedInvoice]) -> dict[str, list[PolicyFinding]]:
        return {
            source_file: evaluate_policy(invoice, self._config.policy)
            for source_file, invoice in invoices.items()
        }
