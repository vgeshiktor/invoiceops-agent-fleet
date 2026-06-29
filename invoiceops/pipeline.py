"""End-to-end pipeline for the InvoiceOps MVP."""

from __future__ import annotations

from pathlib import Path

from invoiceops.agents import adk_available
from invoiceops.agents.anomaly_agent import AnomalyAgent
from invoiceops.agents.extraction_agent import ExtractionAgent
from invoiceops.agents.intake_agent import IntakeAgent
from invoiceops.agents.policy_agent import PolicyAgent
from invoiceops.agents.report_agent import ReportAgent
from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import ApprovalMode, ApprovalPrompt, ExportBundle


def run_pipeline(
    input_dir: str | Path,
    output_dir: str | Path,
    approval_mode: ApprovalMode = "interactive",
    prompt_fn: ApprovalPrompt | None = None,
    config: InvoiceOpsConfig | None = None,
) -> ExportBundle:
    runtime_config = config or InvoiceOpsConfig()
    output_root = Path(output_dir)

    intake_agent = IntakeAgent(runtime_config)
    extraction_agent = ExtractionAgent()
    policy_agent = PolicyAgent(runtime_config)
    anomaly_agent = AnomalyAgent()
    report_agent = ReportAgent(runtime_config)

    documents = intake_agent.run(input_dir)
    invoices_by_file = extraction_agent.run(documents)
    policy_findings = policy_agent.run(invoices_by_file)
    anomaly_findings = anomaly_agent.run(invoices_by_file)

    review_queue = report_agent.build_review_queue(
        documents=documents,
        invoices=invoices_by_file,
        policy_findings=policy_findings,
        anomaly_findings=anomaly_findings,
    )

    exceptions_report_path = report_agent.write_provisional_artifacts(output_root, review_queue)
    final_review_queue = report_agent.resolve_approvals(review_queue, approval_mode, prompt_fn)
    invoices_path, accounting_export_path, review_queue_path = report_agent.write_final_artifacts(
        output_root,
        final_review_queue,
    )

    approved_invoices = [
        item.invoice
        for item in final_review_queue
        if item.status == "approve" and not item.export_blocked and item.invoice is not None
    ]

    return ExportBundle(
        invoices=approved_invoices,
        review_queue=final_review_queue,
        output_dir=output_root,
        invoices_path=invoices_path,
        accounting_export_path=accounting_export_path,
        exceptions_report_path=exceptions_report_path,
        review_queue_path=review_queue_path,
        orchestration_backend="google-adk" if adk_available() else "local-sequential",
    )
