import json
from datetime import date, timedelta
from pathlib import Path

from invoiceops.pipeline import run_pipeline
from invoiceops.schemas import InvoiceRecord
from invoiceops.tools.policy_rules import apply_policy


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"
EXPECTED_DIR = PROJECT_ROOT / "samples" / "expected"


def test_policy_statuses_match_mvp_cases(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}
    invoices_by_file = {invoice.source_file: invoice for invoice in bundle.invoices}

    assert invoices_by_file["invoice_valid_001.txt"].status == "approved"
    assert review_by_file["invoice_missing_vat.txt"].status == "needs_review"
    assert "missing_vat" in review_by_file["invoice_missing_vat.txt"].issues
    assert "irrelevant_note.txt" not in invoices_by_file
    assert "irrelevant_note.txt" not in review_by_file
    assert review_by_file["malicious_invoice.txt"].status == "rejected"
    assert "suspicious_instruction_detected" in review_by_file["malicious_invoice.txt"].risk_flags


def test_run_pipeline_matches_expected_review_queue_snapshot(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    expected_review_queue = json.loads((EXPECTED_DIR / "expected_review_queue.json").read_text())

    assert [item.model_dump(mode="json") for item in bundle.review_queue] == expected_review_queue


def test_apply_policy_marks_invalid_invoice_date_without_raising() -> None:
    invoice = InvoiceRecord(
        source_file="broken-date.txt",
        document_type="invoice",
        vendor_name="Acme Office Supplies Ltd",
        vendor_tax_id="514123456",
        invoice_number="INV-ERR-1",
        invoice_date="2026-99-99",
        currency="ILS",
        subtotal=100.0,
        vat=18.0,
        total=118.0,
    )

    reviewed = apply_policy(invoice)

    assert reviewed.status == "needs_review"
    assert "invalid_invoice_date" in reviewed.issues


def test_policy_flags_future_dates_and_amount_cap(tmp_path: Path) -> None:
    future_date = (date.today() + timedelta(days=30)).isoformat()
    input_dir = tmp_path / "inbox"
    input_dir.mkdir()
    (input_dir / "future_invoice.txt").write_text(
        "\n".join(
            [
                "Invoice",
                "Vendor: Future Vendor Ltd",
                "Tax ID: 500000001",
                "Invoice Number: FUT-1",
                f"Date: {future_date}",
                "Currency: ILS",
                "Subtotal: 100.00",
                "VAT: 18.00",
                "Total: 118.00",
            ]
        ),
        encoding="utf-8",
    )
    (input_dir / "over_cap_invoice.txt").write_text(
        "\n".join(
            [
                "Invoice",
                "Vendor: Big Vendor Ltd",
                "Tax ID: 500000002",
                "Invoice Number: CAP-1",
                "Date: 2026-06-20",
                "Currency: ILS",
                "Subtotal: 10050.00",
                "VAT: 1809.00",
                "Total: 11859.00",
            ]
        ),
        encoding="utf-8",
    )

    bundle = run_pipeline(input_dir=input_dir, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}

    assert "date_in_future" in review_by_file["future_invoice.txt"].issues
    assert "amount_exceeds_limit" in review_by_file["over_cap_invoice.txt"].issues
