from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(PROJECT_ROOT / ".env")


def _get_env(name: str, default: str = "") -> str:
    return os.getenv(name, default).strip()


def _get_float(name: str, default: float) -> float:
    value = _get_env(name)
    if not value:
        return default
    try:
        return float(value)
    except ValueError:
        return default


def _get_int(name: str, default: int) -> int:
    value = _get_env(name)
    if not value:
        return default
    try:
        return int(value)
    except ValueError:
        return default


class Settings:
    gateway_base_url: str = _get_env("SECURE_LLM_GATEWAY_BASE_URL", "http://localhost:8000").rstrip("/")
    chat_path: str = _get_env("SECURE_LLM_CHAT_PATH", "/chat") or "/chat"
    prompt_scan_path: str = _get_env("PROMPT_SCAN_PATH", "")
    pii_scan_path: str = _get_env("PII_SCAN_PATH", "")
    gateway_metrics_path: str = _get_env("GATEWAY_METRICS_PATH", "")

    artifacts_dir_value: str = _get_env("ARTIFACTS_DIR", "")
    artifacts_dir: Optional[Path] = Path(artifacts_dir_value) if artifacts_dir_value else None

    audit_log_path: Path = Path(_get_env("AUDIT_LOG_PATH", "logs/audit.jsonl"))
    if not audit_log_path.is_absolute():
        audit_log_path = PROJECT_ROOT / audit_log_path

    default_model_name: str = _get_env("DEFAULT_MODEL_NAME", "qwen2.5:0.5b")
    default_temperature: float = _get_float("DEFAULT_TEMPERATURE", 0.2)
    default_max_tokens: int = _get_int("DEFAULT_MAX_TOKENS", 256)


settings = Settings()
