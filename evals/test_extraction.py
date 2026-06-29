from pathlib import Path

from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_run_pipeline_extracts_valid_invoice_fields(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="approve-all",
    )

    valid_invoice = next(
        invoice for invoice in bundle.invoices if invoice.source_file == "invoice_valid_001.txt"
    )

    assert valid_invoice.document_type == "invoice"
    assert valid_invoice.vendor == "Acme Office Supplies"
    assert valid_invoice.invoice_number == "INV-1001"
    assert valid_invoice.invoice_date == "2026-06-15"
    assert valid_invoice.currency == "USD"
    assert valid_invoice.total_amount == 1200.50
    assert valid_invoice.vat_number == "IL123456789"


def test_run_pipeline_extracts_valid_receipt_without_vat(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="approve-all",
    )

    receipt = next(
        invoice for invoice in bundle.invoices if invoice.source_file == "receipt_valid_001.txt"
    )

    assert receipt.document_type == "receipt"
    assert receipt.vendor == "Metro Travel Services"
    assert receipt.invoice_number == "RECEIPT-9001"
    assert receipt.vat_number is None
