"""Shared runtime models for the InvoiceOps MVP."""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


DocumentType = Literal["invoice", "receipt", "irrelevant", "unknown"]
InvoiceStatus = Literal["approved", "needs_review", "rejected"]


class DocumentCandidate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    path: Path
    raw_text: str
    document_type: DocumentType = "unknown"
    risk_flags: list[str] = Field(default_factory=list)

    @property
    def is_invoice_like(self) -> bool:
        return self.document_type in {"invoice", "receipt"}


class InvoiceRecord(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_file: str
    document_type: DocumentType
    vendor_name: str | None = None
    vendor_tax_id: str | None = None
    invoice_number: str | None = None
    invoice_date: str | None = None
    currency: str | None = None
    subtotal: float | None = None
    vat: float | None = None
    total: float | None = None
    status: InvoiceStatus = "approved"
    issues: list[str] = Field(default_factory=list)
    risk_flags: list[str] = Field(default_factory=list)

    def add_issue(self, issue: str) -> None:
        if issue not in self.issues:
            self.issues.append(issue)

    def add_risk_flag(self, flag: str) -> None:
        if flag not in self.risk_flags:
            self.risk_flags.append(flag)

    def finalize_status(self) -> None:
        if self.risk_flags:
            self.status = "rejected"
        elif self.issues:
            self.status = "needs_review"
        else:
            self.status = "approved"


class ExportBundle(BaseModel):
    model_config = ConfigDict(extra="forbid")

    invoices: list[InvoiceRecord]
    review_queue: list[InvoiceRecord]
    output_dir: Path
    invoices_path: Path
    accounting_export_path: Path
    exceptions_report_path: Path
    review_queue_path: Path
    orchestration_backend: str
    total_documents_scanned: int
