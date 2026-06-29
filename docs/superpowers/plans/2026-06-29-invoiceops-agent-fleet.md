# InvoiceOps Agent Fleet Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish a placeholder-only Python repository scaffold that exactly matches the requested `invoiceops-agent-fleet` structure.

**Architecture:** The repository will be created as a minimal Python package with skeletal modules and fixture/test placeholders. Metadata will be intentionally small so the first commit establishes structure without prematurely defining implementation details.

**Tech Stack:** Python, setuptools, git, GitHub CLI

---

### Task 1: Repository Metadata And Folder Skeleton

**Files:**
- Create: `README.md`
- Create: `pyproject.toml`
- Create: `.gitignore`
- Create: `invoiceops/__init__.py`
- Create: `invoiceops/cli.py`
- Create: `invoiceops/config.py`
- Create: `invoiceops/schemas.py`
- Create: `invoiceops/pipeline.py`
- Create: `invoiceops/agents/__init__.py`
- Create: `invoiceops/agents/intake_agent.py`
- Create: `invoiceops/agents/extraction_agent.py`
- Create: `invoiceops/agents/policy_agent.py`
- Create: `invoiceops/agents/anomaly_agent.py`
- Create: `invoiceops/agents/report_agent.py`
- Create: `invoiceops/tools/__init__.py`
- Create: `invoiceops/tools/file_reader.py`
- Create: `invoiceops/tools/invoice_parser.py`
- Create: `invoiceops/tools/policy_rules.py`
- Create: `invoiceops/tools/duplicate_detector.py`
- Create: `invoiceops/tools/security_scanner.py`
- Create: `invoiceops/tools/report_writer.py`
- Create: `invoiceops/mcp_server/__init__.py`
- Create: `invoiceops/mcp_server/local_files_server.py`
- Create: `samples/inbox/invoice_valid_001.txt`
- Create: `samples/inbox/invoice_missing_vat.txt`
- Create: `samples/inbox/invoice_duplicate_a.txt`
- Create: `samples/inbox/invoice_duplicate_b.txt`
- Create: `samples/inbox/receipt_valid_001.txt`
- Create: `samples/inbox/irrelevant_note.txt`
- Create: `samples/inbox/malicious_invoice.txt`
- Create: `samples/expected/expected_invoices.json`
- Create: `samples/expected/expected_review_queue.json`
- Create: `evals/test_extraction.py`
- Create: `evals/test_policy.py`
- Create: `evals/test_duplicates.py`
- Create: `evals/test_security.py`
- Create: `outputs/.gitkeep`

- [ ] **Step 1: Add minimal repository metadata**

```toml
[build-system]
requires = ["setuptools>=68"]
build-backend = "setuptools.build_meta"

[project]
name = "invoiceops-agent-fleet"
version = "0.1.0"
description = "Placeholder scaffold for an invoice operations agent fleet."
readme = "README.md"
requires-python = ">=3.11"

[tool.setuptools.packages.find]
include = ["invoiceops*"]
```

- [ ] **Step 2: Create skeletal Python modules and placeholder fixture files**

```python
"""Placeholder module for future implementation."""
```

- [ ] **Step 3: Create output tracking anchor**

```text
# empty tracked file
```

- [ ] **Step 4: Verify the tree matches the requested structure**

Run: `find . -maxdepth 4 | sort`
Expected: output includes the requested directories and files

- [ ] **Step 5: Commit**

```bash
git add .
git commit -m "chore: scaffold invoiceops agent fleet"
```

### Task 2: Git Initialization And GitHub Publication

**Files:**
- Modify: `.git/config`

- [ ] **Step 1: Initialize git and stage the scaffold**

```bash
git init
git add .
```

- [ ] **Step 2: Create the initial commit**

```bash
git commit -m "chore: scaffold invoiceops agent fleet"
```

- [ ] **Step 3: Create the public GitHub repository**

```bash
gh repo create invoiceops-agent-fleet --public --source=. --remote=origin --push
```

- [ ] **Step 4: Verify publication**

Run: `git remote -v && git status --short && gh repo view --json name,url,visibility`
Expected: `origin` exists, working tree is clean, and the repository is public
