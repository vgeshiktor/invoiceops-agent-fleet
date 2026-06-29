import json
from pathlib import Path

from invoiceops.agents import adk_available
from invoiceops.config import InputConfig, InvoiceOpsConfig
from invoiceops.pipeline import run_pipeline
from invoiceops.tools.invoice_parser import parse_invoice_text


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"
EXPECTED_DIR = PROJECT_ROOT / "samples" / "expected"


def test_run_pipeline_extracts_invoice_valid_fixture_fields(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")

    valid_invoice = next(
        invoice for invoice in bundle.invoices if invoice.source_file == "invoice_valid_001.txt"
    )

    assert valid_invoice.document_type == "invoice"
    assert valid_invoice.vendor_name == "Acme Office Supplies Ltd"
    assert valid_invoice.vendor_tax_id == "514123456"
    assert valid_invoice.invoice_number == "INV-2026-001"
    assert valid_invoice.invoice_date == "2026-06-20"
    assert valid_invoice.currency == "ILS"
    assert valid_invoice.subtotal == 1000.0
    assert valid_invoice.vat == 180.0
    assert valid_invoice.total == 1180.0
    assert valid_invoice.status == "approved"
    assert valid_invoice.issues == []
    assert valid_invoice.risk_flags == []


def test_run_pipeline_matches_expected_invoice_snapshot(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    expected_invoices = json.loads((EXPECTED_DIR / "expected_invoices.json").read_text())

    assert [invoice.model_dump(mode="json") for invoice in bundle.invoices] == expected_invoices


def test_parse_invoice_text_tolerates_formatted_amounts() -> None:
    invoice = parse_invoice_text(
        "\n".join(
            [
                "Invoice",
                "Vendor: Amount Vendor",
                "Tax ID: 514123456",
                "Invoice Number: INV-AMT-1",
                "Date: 2026-06-20",
                "Currency: ILS",
                "Subtotal: 1,000.00",
                "VAT: ILS 180.00",
                "Total: not-a-number",
            ]
        ),
        source_file="formatted_amounts.txt",
        document_type="invoice",
    )

    assert invoice.subtotal == 1000.0
    assert invoice.vat == 180.0
    assert invoice.total is None


def test_run_pipeline_honors_custom_supported_extensions(tmp_path: Path) -> None:
    input_dir = tmp_path / "inbox"
    input_dir.mkdir()
    (input_dir / "invoice.custom").write_text(
        "\n".join(
            [
                "Invoice",
                "Vendor: Custom Extension Vendor",
                "Tax ID: 511111111",
                "Invoice Number: CUST-1",
                "Date: 2026-06-20",
                "Currency: ILS",
                "Subtotal: 100.00",
                "VAT: 18.00",
                "Total: 118.00",
            ]
        ),
        encoding="utf-8",
    )

    bundle = run_pipeline(
        input_dir=input_dir,
        output_dir=tmp_path / "outputs",
        config=InvoiceOpsConfig(input=InputConfig(supported_extensions=(".custom",))),
    )

    assert [invoice.source_file for invoice in bundle.invoices] == ["invoice.custom"]


def test_adk_available_returns_false_when_parent_package_is_missing(monkeypatch) -> None:
    def raising_find_spec(name: str):
        raise ModuleNotFoundError("No module named 'google'")

    monkeypatch.setattr("invoiceops.agents.find_spec", raising_find_spec)

    assert adk_available() is False


def test_run_pipeline_reports_actual_backend_when_adk_is_available(
    monkeypatch,
    tmp_path: Path,
) -> None:
    monkeypatch.setattr("invoiceops.pipeline.adk_available", lambda: True)

    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")

    assert bundle.orchestration_backend == "local-sequential"
