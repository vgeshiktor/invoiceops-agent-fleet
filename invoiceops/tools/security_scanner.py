"""Security and classification helpers."""

from __future__ import annotations

import json

from invoiceops.config import SecurityConfig
from invoiceops.schemas import DocumentType


def detect_document_type(
    raw_text: str,
    config: SecurityConfig | None = None,
) -> DocumentType:
    runtime_config = config or SecurityConfig()
    lowered = raw_text.lower()
    stripped_lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    first_line = stripped_lines[0].lower() if stripped_lines else ""

    if first_line == "invoice":
        return "invoice"
    if first_line == "receipt":
        return "receipt"
    if any(pattern in lowered for pattern in runtime_config.irrelevant_patterns):
        return "irrelevant"

    try:
        payload = json.loads(raw_text)
    except json.JSONDecodeError:
        payload = None

    if isinstance(payload, dict):
        doc_type = str(payload.get("document_type", "")).strip().lower()
        if doc_type in {"invoice", "receipt"}:
            return doc_type

    if "invoice number:" in lowered and "total:" in lowered:
        return "invoice"
    if "receipt number:" in lowered:
        return "receipt"
    return "unknown"


def scan_for_prompt_injection(
    raw_text: str,
    config: SecurityConfig | None = None,
) -> list[str]:
    runtime_config = config or SecurityConfig()
    lowered = raw_text.lower()

    return [
        "suspicious_instruction_detected"
        for pattern in runtime_config.prompt_injection_patterns
        if pattern in lowered
    ][:1]
