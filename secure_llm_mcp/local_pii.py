from __future__ import annotations

import re
from typing import Any, Dict, List


PATTERNS = {
    "email": re.compile(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b"),
    "phone_like": re.compile(r"(?<!\d)(?:\+?\d[\d\s().-]{7,}\d)(?!\d)"),
    "ipv4": re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    "credit_card_like": re.compile(r"(?<!\d)(?:\d[ -]*?){13,19}(?!\d)"),
    "israeli_id_like": re.compile(r"(?<!\d)\d{9}(?!\d)"),
}


def scan_text_for_pii(text: str) -> Dict[str, Any]:
    findings: List[Dict[str, Any]] = []

    for label, pattern in PATTERNS.items():
        for match in pattern.finditer(text):
            findings.append(
                {
                    "type": label,
                    "start": match.start(),
                    "end": match.end(),
                    "value_preview": _mask(match.group(0)),
                }
            )

    return {
        "method": "local_regex_fallback",
        "pii_found": bool(findings),
        "finding_count": len(findings),
        "findings": findings,
        "note": "This fallback is useful when the gateway has no dedicated PII endpoint. It is not a replacement for the trained PII guard.",
    }


def _mask(value: str) -> str:
    if len(value) <= 4:
        return "*" * len(value)
    return f"{value[:2]}{'*' * max(1, len(value) - 4)}{value[-2:]}"
