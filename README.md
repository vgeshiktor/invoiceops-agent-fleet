# invoiceops-agent-fleet

InvoiceOps Agent Fleet is a text-first multi-agent MVP that turns local invoice fixtures into reviewed accounting artifacts.

## MVP Behavior
- `invoiceops run --input-dir <dir> --output-dir <dir>` processes a local folder of text fixtures.
- The pipeline classifies documents, extracts invoice fields, applies policy checks, flags duplicates, and writes review/export artifacts.
- Human approval is supported through `interactive`, `approve-all`, and `reject-all` modes.

## Artifacts
- `review_queue.json`
- `exceptions_report.md`
- `invoices.json`
- `accounting_export.csv`

## Notes
- The repo keeps Google ADK integration optional and falls back to a deterministic local orchestrator when ADK is unavailable.
- PDFs, OCR, Gmail, Drive, and external accounting integrations are intentionally out of scope for this MVP.
