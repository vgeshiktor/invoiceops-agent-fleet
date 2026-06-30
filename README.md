# invoiceops-agent-fleet

InvoiceOps Agent Fleet is a local multi-agent MVP that turns messy invoice inputs into structured, validated, human-reviewable accounting outputs.

## Problem

Small businesses receive invoices through emails, PDFs, scans, and messages. Manual review is slow and error-prone, and missing fields, duplicate invoices, suspicious instructions, and inconsistent totals can turn into accounting mistakes.

## Solution

InvoiceOps Agent Fleet uses a deterministic multi-agent workflow to classify documents, extract invoice data, validate business policy, detect anomalies, and produce accountant-ready outputs with a human review queue.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
python -m invoiceops run --input samples/inbox --output outputs
pytest evals/
```

## Core demo

Input:

```text
samples/inbox/
```

Output:

```text
outputs/invoices.json
outputs/accounting_export.csv
outputs/exceptions_report.md
outputs/review_queue.json
```

Core demo sentence:

> InvoiceOps Agent Fleet turns messy invoice inputs into structured, validated, human-reviewable accounting outputs using a safe multi-agent workflow.

## Demo flow

1. Put sample invoice files in `samples/inbox`.
2. Run `python -m invoiceops run --input samples/inbox --output outputs`.
3. Inspect `outputs/invoices.json`, `outputs/accounting_export.csv`, `outputs/exceptions_report.md`, and `outputs/review_queue.json`.
4. Run `pytest evals/`.
5. Confirm that valid, missing-field, duplicate, irrelevant, and suspicious invoices are handled correctly.

## Agent flow

- `IntakeAgent` reads local `.txt`, `.md`, and `.json` files, classifies documents, and flags suspicious instructions.
- `ExtractionAgent` deterministically extracts invoice and receipt fields into a shared `InvoiceRecord` schema.
- `PolicyAgent` enforces required-field, VAT, amount, and future-date rules.
- `AnomalyAgent` flags duplicate invoices and VAT math mismatches.
- `ReportAgent` writes the final JSON, CSV, Markdown, and review-queue artifacts.

## ADK note

This MVP uses deterministic local agent wrappers to keep the capstone demo reproducible. The architecture maps directly to ADK-style agent roles for `IntakeAgent`, `ExtractionAgent`, `PolicyAgent`, `AnomalyAgent`, and `ReportAgent`, and the runtime only surfaces ADK availability as metadata rather than switching orchestration behavior.

## Run the demo

```bash
python -m invoiceops run --input samples/inbox --output outputs
```

Generated artifacts:

- `invoices.json`: all extracted invoice-like records with final status, issues, and risk flags
- `accounting_export.csv`: approved records only
- `exceptions_report.md`: summary plus needs-review, rejected, and security sections
- `review_queue.json`: `needs_review` and `rejected` records only

## Run evals

```bash
pytest evals/
```

The eval suite covers extraction accuracy, policy routing, duplicate detection, security rejection, CLI artifact creation, and the restricted local-file MCP-style tool.

## Restricted local-file MCP-style tool

`invoiceops/mcp_server/local_files_server.py` provides a minimal MCP-style surface with:

- `list_documents`
- `read_document`
- `write_output`

It accepts configurable input and output roots and prevents path escapes outside those sandboxed directories. This is a sandboxed local interface, not a transport-backed MCP protocol server. There is no arbitrary filesystem access and no network access.

## Why it matters

The system does not blindly approve invoices. It creates structured outputs, highlights exceptions, blocks suspicious instructions, and keeps humans in control of final accounting handoff decisions.

## Scope boundaries

This MVP stays intentionally local and deterministic:

- No Gmail integration
- No Google Drive integration
- No OCR
- No database
- No login or auth
- No production deployment
- No UI dashboard

PDF ingestion is not implemented in the current MVP. The supported demo inputs are `.txt`, `.md`, and `.json`.

## Kaggle submission story

- Title: `InvoiceOps Agent Fleet: Safe Multi-Agent Invoice Review for Accounting Handoff`
- Track: `Agents for Business`

| Concept | How this repo demonstrates it |
| --- | --- |
| Multi-agent orchestration | Five specialized agents handle intake, extraction, policy checks, anomaly detection, and reporting in a fixed workflow. |
| Structured business outputs | The pipeline writes JSON, CSV, Markdown, and review-queue artifacts for downstream accounting handoff. |
| Restricted MCP-style tooling | The local-file tool exposes only sandboxed document listing, reading, and output writing within approved roots. |
| Security-aware document handling | Intake flags suspicious instructions and the pipeline rejects malicious-looking content instead of approving it. |
| Reproducible evaluation | `pytest evals/` verifies extraction, policy routing, duplicate detection, CLI behavior, and sandbox enforcement. |
