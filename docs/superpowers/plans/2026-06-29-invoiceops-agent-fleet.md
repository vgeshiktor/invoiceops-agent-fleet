# InvoiceOps Agent Fleet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a strict MVP-aligned InvoiceOps demo that turns local invoice fixtures into validated accounting outputs.

**Architecture:** A five-stage pipeline keeps the agent handoff model while moving the public contract to exact MVP behavior: Pydantic schemas, deterministic parsing, strict status routing, and restricted local-file server access.

**Tech Stack:** Python 3.11+, argparse CLI, Pydantic, pytest, optional FastAPI, JSON/CSV/Markdown artifact writers

---

### Delivered scope

- CLI command: `python -m invoiceops run --input samples/inbox --output outputs`
- Shared Pydantic models: `DocumentCandidate`, `InvoiceRecord`, and `ExportBundle`
- Deterministic helpers for file reading, parsing, policy validation, anomaly detection, security scanning, and report writing
- Restricted local-file server with `list_documents`, `read_document`, and `write_output`
- Sample fixtures and snapshots aligned to the exact MVP scenarios
- Evals for extraction, policy, duplicates, security, CLI outputs, and MCP path restrictions

### Hard boundaries

- Local-only input and output
- No OCR or PDF implementation in the current MVP
- No Gmail, Drive, database, auth, UI, or deployment scope
