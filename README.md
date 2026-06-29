# invoiceops-agent-fleet

InvoiceOps Agent Fleet is a local multi-agent MVP that turns messy invoice inputs into structured, validated, human-reviewable accounting outputs.

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

## Agent flow

- `IntakeAgent` reads local `.txt`, `.md`, and `.json` files, classifies documents, and flags suspicious instructions.
- `ExtractionAgent` deterministically extracts invoice and receipt fields into a shared `InvoiceRecord` schema.
- `PolicyAgent` enforces required-field, VAT, amount, and future-date rules.
- `AnomalyAgent` flags duplicate invoices and VAT math mismatches.
- `ReportAgent` writes the final JSON, CSV, Markdown, and review-queue artifacts.

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

The eval suite covers extraction accuracy, policy routing, duplicate detection, security rejection, CLI artifact creation, and the restricted local-file server.

## Restricted local-file MCP server

`invoiceops/mcp_server/local_files_server.py` provides a minimal MCP-style surface with:

- `list_documents`
- `read_document`
- `write_output`

It is intentionally restricted to reading from `samples/inbox` and writing to `outputs`. There is no arbitrary filesystem access and no network access.

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
- Concepts shown: multi-agent orchestration, restricted MCP-style tooling, security scanning, and pytest-based evals
