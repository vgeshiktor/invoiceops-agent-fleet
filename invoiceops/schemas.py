"""Shared runtime models for the InvoiceOps MVP."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Callable, Literal


DocumentType = Literal["invoice", "receipt", "irrelevant", "unknown"]
FindingSeverity = Literal["low", "medium", "high"]
ReviewStatus = Literal["approve", "reject", "needs_clarification"]
ApprovalMode = Literal["interactive", "approve-all", "reject-all"]


@dataclass(slots=True)
class SecurityFinding:
    code: str
    severity: FindingSeverity
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class PolicyFinding:
    code: str
    severity: FindingSeverity
    message: str

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


@dataclass(slots=True)
class AnomalyFinding:
    code: str
    severity: FindingSeverity
    message: str
    related_files: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class InputDocument:
    source_file: str
    path: Path
    raw_text: str
    document_type: DocumentType = "unknown"
    is_relevant: bool = True
    is_suspicious: bool = False
    security_findings: list[SecurityFinding] = field(default_factory=list)

    def safe_preview(self, limit: int = 80) -> str:
        sanitized = " ".join(self.raw_text.split())
        return sanitized[:limit] + ("..." if len(sanitized) > limit else "")


@dataclass(slots=True)
class ExtractedInvoice:
    source_file: str
    document_type: DocumentType
    vendor: str | None
    invoice_number: str | None
    invoice_date: str | None
    currency: str | None
    total_amount: float | None
    vat_number: str | None = None

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(slots=True)
class ReviewItem:
    source_file: str
    document_type: DocumentType
    status: ReviewStatus
    recommended_status: ReviewStatus
    reasons: list[str] = field(default_factory=list)
    security_findings: list[SecurityFinding] = field(default_factory=list)
    policy_findings: list[PolicyFinding] = field(default_factory=list)
    anomaly_findings: list[AnomalyFinding] = field(default_factory=list)
    invoice: ExtractedInvoice | None = None
    export_blocked: bool = False

    def to_dict(self) -> dict[str, object]:
        return {
            "source_file": self.source_file,
            "document_type": self.document_type,
            "status": self.status,
            "recommended_status": self.recommended_status,
            "reasons": list(self.reasons),
            "security_findings": [finding.to_dict() for finding in self.security_findings],
            "policy_findings": [finding.to_dict() for finding in self.policy_findings],
            "anomaly_findings": [finding.to_dict() for finding in self.anomaly_findings],
            "invoice": self.invoice.to_dict() if self.invoice else None,
            "export_blocked": self.export_blocked,
        }


@dataclass(slots=True)
class ExportBundle:
    invoices: list[ExtractedInvoice]
    review_queue: list[ReviewItem]
    output_dir: Path
    invoices_path: Path
    accounting_export_path: Path
    exceptions_report_path: Path
    review_queue_path: Path
    orchestration_backend: str


ApprovalPrompt = Callable[[ReviewItem], ReviewStatus]
