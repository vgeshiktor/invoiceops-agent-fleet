"""Report agent for writing MVP outputs."""

from __future__ import annotations

from pathlib import Path

from invoiceops.config import InvoiceOpsConfig
from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.report_writer import (
    write_csv,
    write_json,
    write_markdown_report,
    write_review_queue,
)


class ReportAgent:
    def __init__(self, config: InvoiceOpsConfig) -> None:
        self._config = config

    def write_outputs(
        self,
        output_dir: Path,
        invoices: list[InvoiceRecord],
        total_documents_scanned: int,
    ) -> tuple[Path, Path, Path, Path, list[InvoiceRecord]]:
        output_dir.mkdir(parents=True, exist_ok=True)
        invoices_path = output_dir / self._config.output.invoices_filename
        accounting_export_path = output_dir / self._config.output.accounting_export_filename
        exceptions_report_path = output_dir / self._config.output.exceptions_report_filename
        review_queue_path = output_dir / self._config.output.review_queue_filename
        review_queue = [invoice for invoice in invoices if invoice.status in {"needs_review", "rejected"}]

        write_json(invoices_path, invoices)
        write_csv(accounting_export_path, invoices)
        write_markdown_report(
            exceptions_report_path,
            invoices,
            total_documents_scanned,
            accounting_export_path.name,
        )
        write_review_queue(review_queue_path, invoices)

        return (
            invoices_path,
            accounting_export_path,
            exceptions_report_path,
            review_queue_path,
            review_queue,
        )
