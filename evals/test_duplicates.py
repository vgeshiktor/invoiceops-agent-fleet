from pathlib import Path

from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_duplicate_finding_is_attached_to_both_duplicate_invoices(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="reject-all",
    )

    duplicate_items = [
        item
        for item in bundle.review_queue
        if any(finding.code == "duplicate_invoice" for finding in item.anomaly_findings)
    ]

    assert {item.source_file for item in duplicate_items} == {
        "invoice_duplicate_a.txt",
        "invoice_duplicate_b.txt",
    }
