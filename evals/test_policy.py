import json
from pathlib import Path

from invoiceops.pipeline import run_pipeline


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
