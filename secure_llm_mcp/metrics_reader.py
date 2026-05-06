from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, Optional

from .gateway_client import get_json
from .settings import settings


def get_metrics() -> Dict[str, Any]:
    if settings.gateway_metrics_path:
        gateway_result = get_json(settings.gateway_metrics_path)
        if "error" not in gateway_result:
            return {
                "source": "gateway_endpoint",
                "path": settings.gateway_metrics_path,
                "metrics": gateway_result,
            }

    if settings.artifacts_dir:
        return read_latest_artifacts(settings.artifacts_dir)

    return {
        "error": "metrics_source_not_configured",
        "details": "Set GATEWAY_METRICS_PATH or ARTIFACTS_DIR in .env or in Claude Desktop config env.",
    }


def read_latest_artifacts(artifacts_dir: Path) -> Dict[str, Any]:
    if not artifacts_dir.exists():
        return {
            "error": "artifacts_dir_not_found",
            "path": str(artifacts_dir),
        }

    results: Dict[str, Any] = {}

    for guard_dir in sorted(artifacts_dir.iterdir()):
        if not guard_dir.is_dir():
            continue

        latest_run = _find_latest_run(guard_dir)
        if not latest_run:
            continue

        metrics_path = latest_run / "metrics.json"
        if not metrics_path.exists():
            continue

        try:
            with metrics_path.open("r", encoding="utf-8") as f:
                metrics = json.load(f)
            results[guard_dir.name] = {
                "latest_run": latest_run.name,
                "metrics_path": str(metrics_path),
                "metrics": metrics,
            }
        except Exception as exc:
            results[guard_dir.name] = {
                "latest_run": latest_run.name,
                "metrics_path": str(metrics_path),
                "error": str(exc),
            }

    return {
        "source": "local_artifacts",
        "artifacts_dir": str(artifacts_dir),
        "guards": results,
    }


def _find_latest_run(guard_dir: Path) -> Optional[Path]:
    runs_dir = guard_dir / "runs"
    if not runs_dir.exists():
        return None

    run_dirs = [p for p in runs_dir.iterdir() if p.is_dir()]
    if not run_dirs:
        return None

    return sorted(run_dirs, key=lambda p: p.name, reverse=True)[0]
