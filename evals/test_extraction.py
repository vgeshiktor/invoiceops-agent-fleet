import json
from pathlib import Path

from invoiceops.pipeline import run_pipeline


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
