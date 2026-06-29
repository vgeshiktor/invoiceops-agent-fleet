"""Security and classification helpers."""

from __future__ import annotations

from invoiceops.config import SecurityConfig
from invoiceops.schemas import DocumentType, SecurityFinding


def detect_document_type(raw_text: str) -> DocumentType:
    for line in raw_text.splitlines():
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        if key.strip().lower() == "document-type":
            normalized = value.strip().lower()
            if normalized in {"invoice", "receipt"}:
                return normalized

    lowered = raw_text.lower()
    if "receipt" in lowered:
        return "receipt"
    if "invoice" in lowered:
        return "invoice"
    return "unknown"


def scan_security_findings(raw_text: str, config: SecurityConfig) -> list[SecurityFinding]:
    lowered = raw_text.lower()
    findings: list[SecurityFinding] = []

    if any(pattern in lowered for pattern in config.irrelevant_patterns):
        findings.append(
            SecurityFinding(
                code="irrelevant_content",
                severity="high",
                message="The document does not appear to be invoice-related business input.",
            )
        )

    if any(pattern in lowered for pattern in config.prompt_injection_patterns):
        findings.append(
            SecurityFinding(
                code="prompt_injection",
                severity="high",
                message="The document contains prompt-injection style instructions.",
            )
        )

    return findings
