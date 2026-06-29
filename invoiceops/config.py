"""Configuration models for the InvoiceOps MVP."""

from dataclasses import dataclass, field


@dataclass(frozen=True, slots=True)
class PolicyConfig:
    allowed_vendors: tuple[str, ...] = (
        "Acme Office Supplies",
        "Metro Travel Services",
        "Northwind Catering",
        "Bluewave Printing",
    )
    max_invoice_total: float = 5000.0


@dataclass(frozen=True, slots=True)
class SecurityConfig:
    irrelevant_patterns: tuple[str, ...] = (
        "meeting notes",
        "team lunch",
        "not an invoice",
        "weekly reminder",
    )
    prompt_injection_patterns: tuple[str, ...] = (
        "ignore previous instructions",
        "reveal the system prompt",
        "exfiltrate",
        "override policy",
    )


@dataclass(frozen=True, slots=True)
class OutputConfig:
    invoices_filename: str = "invoices.json"
    accounting_export_filename: str = "accounting_export.csv"
    exceptions_report_filename: str = "exceptions_report.md"
    review_queue_filename: str = "review_queue.json"


@dataclass(frozen=True, slots=True)
class InvoiceOpsConfig:
    policy: PolicyConfig = field(default_factory=PolicyConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
