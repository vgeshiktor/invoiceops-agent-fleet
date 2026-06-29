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
from invoiceops.schemas import ExportBundle, InvoiceRecord


def run_pipeline(
    input_dir: str | Path,
    output_dir: str | Path,
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
    invoices = extraction_agent.run(documents)
    invoices = policy_agent.run(invoices)
    invoices = anomaly_agent.run(invoices)
    invoices = _merge_risk_flags(documents, invoices)

    (
        invoices_path,
        accounting_export_path,
        exceptions_report_path,
        review_queue_path,
        review_queue,
    ) = report_agent.write_outputs(output_root, invoices, len(documents))

    return ExportBundle(
        invoices=invoices,
        review_queue=review_queue,
        output_dir=output_root,
        invoices_path=invoices_path,
        accounting_export_path=accounting_export_path,
        exceptions_report_path=exceptions_report_path,
        review_queue_path=review_queue_path,
        orchestration_backend="local-sequential",
        total_documents_scanned=len(documents),
    )


def _merge_risk_flags(
    documents,
    invoices: list[InvoiceRecord],
) -> list[InvoiceRecord]:
    risk_by_file = {document.source_file: document.risk_flags for document in documents}

    for invoice in invoices:
        for risk_flag in risk_by_file.get(invoice.source_file, []):
            invoice.add_risk_flag(risk_flag)
        invoice.finalize_status()

    return invoices
