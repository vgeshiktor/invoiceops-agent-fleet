import json
import subprocess
import sys
from pathlib import Path

import pytest

from invoiceops.mcp_server.local_files_server import LocalFilesServer
from invoiceops.pipeline import run_pipeline


PROJECT_ROOT = Path(__file__).resolve().parents[1]
SAMPLES_DIR = PROJECT_ROOT / "samples" / "inbox"


def test_security_finding_rejects_malicious_invoice(tmp_path: Path) -> None:
    bundle = run_pipeline(input_dir=SAMPLES_DIR, output_dir=tmp_path / "outputs")
    review_by_file = {item.source_file: item for item in bundle.review_queue}

    malicious = review_by_file["malicious_invoice.txt"]
    assert malicious.status == "rejected"
    assert malicious.risk_flags == ["suspicious_instruction_detected"]


def test_cli_command_writes_all_required_artifacts(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    command = [
        sys.executable,
        "-m",
        "invoiceops",
        "run",
        "--input",
        str(SAMPLES_DIR),
        "--output",
        str(output_dir),
    ]

    completed = subprocess.run(command, capture_output=True, text=True, check=False)

    assert completed.returncode == 0, completed.stderr
    assert (output_dir / "invoices.json").exists()
    assert (output_dir / "accounting_export.csv").exists()
    assert (output_dir / "exceptions_report.md").exists()
    assert (output_dir / "review_queue.json").exists()

    invoices = json.loads((output_dir / "invoices.json").read_text())
    review_queue = json.loads((output_dir / "review_queue.json").read_text())

    assert any(invoice["status"] == "approved" for invoice in invoices)
    assert all(item["status"] in {"needs_review", "rejected"} for item in review_queue)


def test_local_files_server_blocks_path_escape(tmp_path: Path) -> None:
    server = LocalFilesServer(input_root=SAMPLES_DIR, output_root=tmp_path / "outputs")

    assert "invoice_valid_001.txt" in server.list_documents()
    assert "Acme Office Supplies Ltd" in server.read_document("invoice_valid_001.txt")

    server.write_output("probe.json", "{\"ok\": true}")
    assert (tmp_path / "outputs" / "probe.json").exists()

    with pytest.raises(ValueError):
        server.read_document("../secrets.txt")

    with pytest.raises(ValueError):
        server.write_output("../escape.txt", "bad")
