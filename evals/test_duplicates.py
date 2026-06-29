from pathlib import Path

from invoiceops.pipeline import run_pipeline
from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.duplicate_detector import detect_duplicates


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_duplicate_invoices_are_routed_to_review(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}

    for source_file in ("invoice_duplicate_a.txt", "invoice_duplicate_b.txt"):
        assert review_by_file[source_file].status == "needs_review"
        assert "duplicate_invoice" in review_by_file[source_file].issues


def test_same_invoice_number_for_different_vendors_is_not_flagged() -> None:
    invoices = [
        InvoiceRecord(
            source_file="vendor_a.txt",
            document_type="invoice",
            vendor_name="Vendor A",
            vendor_tax_id="100",
            invoice_number="INV-123",
            invoice_date="2026-06-20",
            currency="ILS",
            subtotal=100.0,
            vat=18.0,
            total=118.0,
        ),
        InvoiceRecord(
            source_file="vendor_b.txt",
            document_type="invoice",
            vendor_name="Vendor B",
            vendor_tax_id="200",
            invoice_number="INV-123",
            invoice_date="2026-06-20",
            currency="ILS",
            subtotal=100.0,
            vat=18.0,
            total=118.0,
        ),
    ]

    reviewed = detect_duplicates(invoices)

    assert all("duplicate_invoice" not in invoice.issues for invoice in reviewed)
