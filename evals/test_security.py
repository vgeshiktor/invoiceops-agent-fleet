import json
import subprocess
import sys
from pathlib import Path

import pytest

from invoiceops.config import InvoiceOpsConfig, OutputConfig, SecurityConfig
from invoiceops.mcp_server.local_files_server import LocalFilesServer
from invoiceops.pipeline import run_pipeline
from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.report_writer import write_csv
from invoiceops.tools.security_scanner import detect_document_type


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_security_finding_rejects_malicious_invoice(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}

    malicious = review_by_file["malicious_invoice.txt"]
    assert malicious.status == "rejected"
    assert malicious.risk_flags == ["suspicious_instruction_detected"]


def test_cli_command_writes_all_required_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    command = [
        sys.executable,
        "-m",
        "invoiceops",
        "run",
        "--input",
        str(SAMPLES_DIR),
        "--output",
        str(output_dir),
    ]

    completed = subprocess.run(
        command,
        capture_output=True,
        text=True,
        check=False,
        cwd=PROJECT_ROOT,
    )

    assert completed.returncode == 0, completed.stderr
    assert (output_dir / "invoices.json").exists()
    assert (output_dir / "accounting_export.csv").exists()
    assert (output_dir / "exceptions_report.md").exists()
    assert (output_dir / "review_queue.json").exists()

    invoices = json.loads((output_dir / "invoices.json").read_text())
    review_queue = json.loads((output_dir / "review_queue.json").read_text())

    assert any(invoice["status"] == "approved" for invoice in invoices)
    assert all(item["status"] in {"needs_review", "rejected"} for item in review_queue)


def test_local_files_server_blocks_path_escape(tmp_path: Path) -> None:
    server = LocalFilesServer(input_root=SAMPLES_DIR, output_root=tmp_path / "outputs")

    assert "invoice_valid_001.txt" in server.list_documents()
    assert "Acme Office Supplies Ltd" in server.read_document("invoice_valid_001.txt")

    server.write_output("probe.json", "{\"ok\": true}")
    assert (tmp_path / "outputs" / "probe.json").exists()

    with pytest.raises(ValueError):
        server.read_document("../secrets.txt")

    with pytest.raises(ValueError):
        server.write_output("../escape.txt", "bad")


def test_detect_document_type_prefers_structured_invoice_over_irrelevant_pattern() -> None:
    raw_payload = json.dumps(
        {
            "document_type": "invoice",
            "note": "payment reminder for this invoice",
        }
    )

    detected = detect_document_type(raw_payload, SecurityConfig())

    assert detected == "invoice"


def test_custom_accounting_export_name_is_reflected_in_report(tmp_path: Path) -> None:
    config = InvoiceOpsConfig(
        output=OutputConfig(accounting_export_filename="custom_export.csv"),
    )

    run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs", config=config)

    report_text = (tmp_path / "outputs" / "exceptions_report.md").read_text(encoding="utf-8")
    assert "custom_export.csv" in report_text


def test_write_csv_sanitizes_formula_like_text(tmp_path: Path) -> None:
    path = tmp_path / "accounting_export.csv"
    invoice = InvoiceRecord(
        source_file="=cmd|' /C calc'!A0",
        document_type="invoice",
        vendor_name="+Danger Vendor",
        vendor_tax_id="@123",
        invoice_number="-INV-1",
        invoice_date="2026-06-20",
        currency="=ILS",
        subtotal=100.0,
        vat=18.0,
        total=118.0,
        status="approved",
    )

    write_csv(path, [invoice])

    content = path.read_text(encoding="utf-8")
    assert "'=cmd|' /C calc'!A0" in content
    assert "'+Danger Vendor" in content
    assert "'@123" in content
    assert "'-INV-1" in content
    assert "'=ILS" in content
