"""Report agent for review item assembly and approval handling."""

from __future__ import annotations

from pathlib import Path

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import (
    ApprovalMode,
    ApprovalPrompt,
    ExtractedInvoice,
    InputDocument,
    ReviewItem,
    ReviewStatus,
)
from invoiceops.tools.report_writer import (
    write_accounting_export,
    write_exceptions_report,
    write_invoices_json,
    write_review_queue,
)


class ReportAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def build_review_queue(
        self,
        documents: list[InputDocument],
        invoices: dict[str, ExtractedInvoice],
        policy_findings: dict[str, list],
        anomaly_findings: dict[str, list],
    ) -> list[ReviewItem]:
        review_queue: list[ReviewItem] = []

        for document in documents:
            security_findings = list(document.security_findings)
            policy = list(policy_findings.get(document.source_file, []))
            anomalies = list(anomaly_findings.get(document.source_file, []))
            export_blocked = document.document_type == "irrelevant" or any(
                finding.severity == "high" for finding in security_findings
            )

            if export_blocked:
                recommended_status: ReviewStatus = "reject"
            elif security_findings or policy or anomalies or document.document_type == "unknown":
                recommended_status = "needs_clarification"
            else:
                recommended_status = "approve"

            reasons = [finding.code for finding in security_findings + policy + anomalies] or ["no_exceptions"]

            review_queue.append(
                ReviewItem(
                    source_file=document.source_file,
                    document_type=document.document_type,
                    status=recommended_status,
                    recommended_status=recommended_status,
                    reasons=reasons,
                    security_findings=security_findings,
                    policy_findings=policy,
                    anomaly_findings=anomalies,
                    invoice=invoices.get(document.source_file),
                    export_blocked=export_blocked or invoices.get(document.source_file) is None,
                )
            )

        return review_queue

    def write_provisional_artifacts(self, output_dir: Path, review_queue: list[ReviewItem]) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        review_queue_path = output_dir / self._config.output.review_queue_filename
        exceptions_report_path = output_dir / self._config.output.exceptions_report_filename
        write_review_queue(review_queue_path, review_queue)
        write_exceptions_report(exceptions_report_path, review_queue)
        return exceptions_report_path

    def resolve_approvals(
        self,
        review_queue: list[ReviewItem],
        approval_mode: ApprovalMode,
        prompt_fn: ApprovalPrompt | None,
    ) -> list[ReviewItem]:
        resolved: list[ReviewItem] = []

        for item in review_queue:
            if approval_mode == "approve-all":
                item.status = "approve" if not item.export_blocked else "reject"
            elif approval_mode == "reject-all":
                item.status = "reject"
            else:
                decision = prompt_fn(item) if prompt_fn else "reject"
                item.status = decision if decision in {"approve", "reject", "needs_clarification"} else "reject"
                if item.export_blocked and item.status == "approve":
                    item.status = "reject"

            resolved.append(item)

        return resolved

    def write_final_artifacts(self, output_dir: Path, review_queue: list[ReviewItem]) -> tuple[Path, Path, Path]:
        invoices = [
            item.invoice
            for item in review_queue
            if item.status == "approve" and not item.export_blocked and item.invoice is not None
        ]
        invoices_path = output_dir / self._config.output.invoices_filename
        accounting_export_path = output_dir / self._config.output.accounting_export_filename
        review_queue_path = output_dir / self._config.output.review_queue_filename

        write_review_queue(review_queue_path, review_queue)
        write_invoices_json(invoices_path, invoices)
        write_accounting_export(accounting_export_path, invoices)

        return invoices_path, accounting_export_path, review_queue_path
