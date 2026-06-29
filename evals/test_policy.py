from pathlib import Path

from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_missing_vat_invoice_is_flagged_for_review(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="reject-all",
    )

    review_item = next(
        item for item in bundle.review_queue if item.source_file == "invoice_missing_vat.txt"
    )

    assert review_item.status == "reject"
    assert any(finding.code == "missing_vat_number" for finding in review_item.policy_findings)
    assert review_item.export_blocked is False


def test_approve_all_mode_exports_reviewable_policy_exceptions(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="approve-all",
    )

    approved_files = {invoice.source_file for invoice in bundle.invoices}

    assert "invoice_missing_vat.txt" in approved_files
