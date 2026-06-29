"""CLI entrypoint for the InvoiceOps MVP."""

from __future__ import annotations

import argparse
from pathlib import Path

from invoiceops.pipeline import run_pipeline
from invoiceops.schemas import ReviewItem, ReviewStatus


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="invoiceops")
    subparsers = parser.add_subparsers(dest="command", required=True)

    run_parser = subparsers.add_parser("run", help="Process a folder of invoice fixtures.")
    run_parser.add_argument("--input-dir", required=True)
    run_parser.add_argument("--output-dir", required=True)
    run_parser.add_argument(
        "--approval-mode",
        choices=["interactive", "approve-all", "reject-all"],
        default="interactive",
    )

    return parser


def _interactive_prompt(review_item: ReviewItem) -> ReviewStatus:
    prompt = (
        f"{review_item.source_file} [{review_item.document_type}] "
        f"recommended={review_item.recommended_status} "
        "-> approve/reject/needs_clarification: "
    )
    decision = input(prompt).strip().lower()
    if decision not in {"approve", "reject", "needs_clarification"}:
        return "reject"
    return decision


def main(argv: list[str] | None = None, prompt_fn=None) -> int:
    args = build_parser().parse_args(argv)

    if args.command != "run":
        return 1

    bundle = run_pipeline(
        input_dir=Path(args.input_dir),
        output_dir=Path(args.output_dir),
        approval_mode=args.approval_mode,
        prompt_fn=prompt_fn or _interactive_prompt,
    )

    print(
        f"Processed {len(bundle.review_queue)} documents and exported "
        f"{len(bundle.invoices)} approved records to {bundle.output_dir}."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
