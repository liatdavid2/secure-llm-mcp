from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

from .settings import settings


def write_audit_event(tool_name: str, payload: Dict[str, Any], result: Dict[str, Any]) -> None:
    """Write audit data to a JSONL file without printing to stdout."""
    log_path: Path = settings.audit_log_path
    log_path.parent.mkdir(parents=True, exist_ok=True)

    event = {
        "event_id": str(uuid.uuid4()),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "tool_name": tool_name,
        "payload_summary": _safe_summary(payload),
        "result_summary": _safe_summary(result),
    }

    with log_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, ensure_ascii=False) + "\n")


def _safe_summary(data: Dict[str, Any]) -> Dict[str, Any]:
    summary: Dict[str, Any] = {}
    for key, value in data.items():
        if key.lower() in {"prompt", "text", "response_text"} and isinstance(value, str):
            summary[key] = {
                "length": len(value),
                "preview": value[:160],
            }
        else:
            summary[key] = value
    return summary
