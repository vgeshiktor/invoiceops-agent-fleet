# InvoiceOps Agent Fleet Design

## Goal

Create a public GitHub repository named `invoiceops-agent-fleet` with the exact user-requested directory structure and placeholder-only Python project scaffold.

## Scope

- Create the requested package, sample, eval, output, and MCP server directories.
- Add minimal repository metadata in `README.md`, `pyproject.toml`, and `.gitignore`.
- Keep implementation files intentionally skeletal.
- Initialize git, create a public GitHub repository, and push the initial commit.

## Architecture

The repository is a lightweight Python package scaffold centered on the `invoiceops` package. Files are created to establish clear future ownership boundaries across agents, tools, pipeline orchestration, schemas, configuration, and a local MCP server integration point.

The initial commit prioritizes structure over behavior. Python modules remain placeholders, sample input and expected-output fixtures exist as inert seed files, and evaluation files exist as empty anchors for later tests.

## File Responsibilities

- `invoiceops/`: root Python package for CLI, config, schemas, and pipeline orchestration.
- `invoiceops/agents/`: future agent modules for intake, extraction, policy, anomaly detection, and reporting.
- `invoiceops/tools/`: future helper utilities for parsing, validation, security, duplication checks, and reporting.
- `invoiceops/mcp_server/`: future local MCP server package.
- `samples/inbox/`: placeholder inbound document fixtures.
- `samples/expected/`: placeholder expected-result fixtures.
- `evals/`: placeholder evaluation test modules.
- `outputs/`: tracked output directory anchor via `.gitkeep`.

## Error Handling

There is no runtime behavior in this scaffold beyond repository metadata validity, so error handling is limited to ensuring files exist and git/GitHub publication succeeds.

## Testing

Verification is structural:

- confirm the created tree matches the requested layout
- confirm git repository initialization and clean commit state
- confirm GitHub repository creation and remote push

## Non-Goals

- no invoice-processing logic
- no runnable CLI workflow
- no implemented tests
- no dependency-heavy setup
