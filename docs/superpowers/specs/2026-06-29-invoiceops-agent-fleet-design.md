# InvoiceOps Agent Fleet Design

## Goal

Implement a runnable MVP that processes local text-based invoices and receipts into reviewed accounting artifacts through a small multi-agent pipeline.

## Scope

- One CLI entrypoint with `interactive`, `approve-all`, and `reject-all` approval modes.
- Five agent stages: intake, extraction, policy, anomaly, and report.
- Four final artifacts: `review_queue.json`, `exceptions_report.md`, `invoices.json`, and `accounting_export.csv`.
- Deterministic local parsing and rule enforcement with optional Google ADK orchestration when available.

## Architecture

The pipeline remains centered on the `invoiceops` package. Each agent owns one stage of the workflow and delegates deterministic work to small helper modules in `invoiceops/tools/`.

The Google ADK layer stays thin and optional. If ADK is installed, the project can advertise that orchestration backend; if it is not installed, the runtime falls back to the same agent sequence through a local deterministic coordinator so tests and demos remain stable.

## Runtime Behavior

- Intake loads local `.txt` fixtures, classifies document type, and quarantines irrelevant or prompt-injection content.
- Extraction normalizes invoice and receipt fields into a shared schema.
- Policy validates required fields, vendor allowlist rules, and amount thresholds.
- Anomaly detection flags duplicate invoices by vendor and invoice number.
- Reporting writes a provisional review queue and exceptions report, resolves approval decisions, then writes approved invoice exports.

## Testing

- Evals cover extraction, policy exceptions, duplicate detection, security quarantine behavior, and CLI artifact generation.
- The MVP is intentionally text-first and fully local so the tests can stay deterministic.

## Non-Goals

- No OCR or PDF/image ingestion.
- No Gmail, Drive, or accounting API integrations.
- No external model dependency required for local tests.
