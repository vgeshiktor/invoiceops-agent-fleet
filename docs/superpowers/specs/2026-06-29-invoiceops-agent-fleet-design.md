# InvoiceOps Agent Fleet Design

## Goal

Build a runnable local MVP that processes messy invoice and receipt fixtures into accountant-ready outputs through a deterministic multi-agent workflow.

## Scope

- One CLI entrypoint: `python -m invoiceops run --input samples/inbox --output outputs`
- Five stages: intake, extraction, policy, anomaly, and reporting
- Four artifacts: `invoices.json`, `accounting_export.csv`, `exceptions_report.md`, and `review_queue.json`
- Shared Pydantic schemas for document intake and final invoice records
- A minimal local-file MCP-style server restricted to `samples/inbox` and `outputs`

## Architecture

The pipeline stays centered on the `invoiceops` package. Agents orchestrate the workflow, while deterministic helpers in `invoiceops/tools/` own file access, parsing, policy checks, anomaly checks, security scanning, and artifact writing.

The Google ADK dependency remains optional and descriptive only. If it is installed, the runtime can report that orchestration backend; otherwise the MVP runs locally with the same deterministic logic.

## Runtime behavior

- Intake reads `.txt`, `.md`, and `.json` inputs, classifies `invoice`, `receipt`, `irrelevant`, or `unknown`, and flags prompt-injection-like text.
- Extraction parses exact fixture fields such as `Vendor`, `Tax ID`, `Invoice Number`, `Date`, `Subtotal`, `VAT`, and `Total`.
- Policy enforces required fields, VAT for Israeli invoices, positive totals, a `10,000 ILS` max total, and no future-dated invoices.
- Anomaly detection flags duplicate invoices by invoice number or by vendor plus amount plus date, and flags VAT math mismatches.
- Reporting writes all invoice-like records to `invoices.json`, approved records to `accounting_export.csv`, actionable exceptions to `review_queue.json`, and a Markdown summary report.

## Testing

- Extraction evals verify exact field extraction on the valid sample invoice.
- Policy evals verify approved, needs-review, skipped, and rejected routing.
- Duplicate evals verify both duplicate fixtures become `needs_review`.
- Security evals verify suspicious instructions produce `rejected` plus `suspicious_instruction_detected`.
- CLI and MCP evals verify artifact creation and path-sandbox enforcement.

## Non-goals

- No Gmail, Drive, database, auth, UI, or cloud deployment
- No OCR
- No PDF processing in the current MVP implementation
