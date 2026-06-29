# InvoiceOps Agent Fleet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Deliver a runnable InvoiceOps MVP that processes local text fixtures into reviewed accounting artifacts.

**Architecture:** A CLI orchestrates five agent stages. Each agent delegates deterministic work to small helpers so the workflow stays testable, while the orchestration backend can advertise Google ADK when available and otherwise run locally without external dependencies.

**Tech Stack:** Python 3.11+, argparse CLI, pytest evals, dataclass-based schemas, optional Google ADK compatibility, JSON/CSV/Markdown artifact writers

---

### Delivered Scope

- CLI command: `run --input-dir --output-dir --approval-mode`
- Shared runtime types for documents, findings, review items, and export bundles
- Deterministic tools for file reading, text parsing, policy checks, duplicate detection, security scanning, and artifact writing
- Agent modules for intake, extraction, policy, anomaly, and reporting
- Updated sample fixtures that represent valid, duplicate, missing-VAT, irrelevant, and malicious scenarios
- Evals that cover the full MVP flow
