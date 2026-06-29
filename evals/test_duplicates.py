from pathlib import Path

from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_duplicate_invoices_are_routed_to_review(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}

    for source_file in ("invoice_duplicate_a.txt", "invoice_duplicate_b.txt"):
        assert review_by_file[source_file].status == "needs_review"
        assert "duplicate_invoice" in review_by_file[source_file].issues
