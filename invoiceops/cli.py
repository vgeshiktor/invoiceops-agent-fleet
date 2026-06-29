"""CLI entrypoint for the InvoiceOps MVP."""

from __future__ import annotations

import argparse
from pathlib import Path

from invoiceops.pipeline import run_pipeline


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="invoiceops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Process a folder of invoice fixtures.")
    run_parser.add_argument("--input", required=True)
    run_parser.add_argument("--output", required=True)

    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)

    if args.command != "run":
        return 1

    bundle = run_pipeline(input_dir=Path(args.input), output_dir=Path(args.output))
    print(
        f"Processed {bundle.total_documents_scanned} documents and wrote "
        f"{len(bundle.invoices)} invoice records to {bundle.output_dir}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
