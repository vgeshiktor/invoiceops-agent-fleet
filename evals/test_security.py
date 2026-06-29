import json
from pathlib import Path

from invoiceops.cli import main as cli_main
from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_pipeline_quarantines_irrelevant_and_malicious_documents(tmp_path: Path) -> None:
    bundle = run_pipeline(
        input_dir=SAMPLES_DIR,
        output_dir=tmp_path / "outputs",
        approval_mode="reject-all",
    )

    irrelevant = next(item for item in bundle.review_queue if item.source_file == "irrelevant_note.txt")
    malicious = next(item for item in bundle.review_queue if item.source_file == "malicious_invoice.txt")

    assert irrelevant.document_type == "irrelevant"
    assert irrelevant.export_blocked is True
    assert any(finding.code == "irrelevant_content" for finding in irrelevant.security_findings)

    assert malicious.document_type == "invoice"
    assert malicious.export_blocked is True
    assert any(finding.code == "prompt_injection" for finding in malicious.security_findings)


def test_cli_run_writes_all_artifacts_and_uses_interactive_decisions(tmp_path: Path) -> None:
    decisions = {
        "invoice_valid_001.txt": "approve",
        "invoice_missing_vat.txt": "reject",
        "invoice_duplicate_a.txt": "needs_clarification",
        "invoice_duplicate_b.txt": "reject",
        "receipt_valid_001.txt": "approve",
        "irrelevant_note.txt": "reject",
        "malicious_invoice.txt": "reject",
    }

    exit_code = cli_main(
        [
            "run",
            "--input-dir",
            str(SAMPLES_DIR),
            "--output-dir",
            str(tmp_path / "outputs"),
            "--approval-mode",
            "interactive",
        ],
        prompt_fn=lambda item: decisions[item.source_file],
    )

    assert exit_code == 0

    output_dir = tmp_path / "outputs"
    assert (output_dir / "invoices.json").exists()
    assert (output_dir / "accounting_export.csv").exists()
    assert (output_dir / "exceptions_report.md").exists()
    assert (output_dir / "review_queue.json").exists()

    invoices = json.loads((output_dir / "invoices.json").read_text())
    review_queue = json.loads((output_dir / "review_queue.json").read_text())

    assert {invoice["source_file"] for invoice in invoices} == {
        "invoice_valid_001.txt",
        "receipt_valid_001.txt",
    }
    assert {item["status"] for item in review_queue} >= {"approve", "reject", "needs_clarification"}
