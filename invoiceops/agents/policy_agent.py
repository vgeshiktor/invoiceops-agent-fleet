"""Policy agent for rule checks."""

from __future__ import annotations

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.policy_rules import apply_policy


class PolicyAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def run(self, invoices: list[InvoiceRecord]) -> list[InvoiceRecord]:
        return [apply_policy(invoice, self._config.policy) for invoice in invoices]
